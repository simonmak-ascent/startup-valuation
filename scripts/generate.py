#!/usr/bin/env python3
"""Codegen: emit TypeScript `lib/methods/*.ts` from the canonical registry.

Deterministic: running twice produces byte-identical output.
Also validates that no schema field name is a SurrealDB reserved word.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from method_registry.registry import METHODS, RESERVED_WORDS  # noqa: E402

TS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib", "methods")


def check_reserved_words(methods):
    """Reject any method/input/field name that is a SurrealDB reserved word."""
    for m in methods:
        names = [m["slug"], m["method_name"], m["function"]] + [i["name"] for i in m["inputs"]]
        for n in names:
            if n.lower() in RESERVED_WORDS:
                raise ValueError(f"Reserved word '{n}' used in method '{m['slug']}'")


def _quote(s):
    return json.dumps(s, ensure_ascii=False)


def _emit_input(i):
    parts = [
        (
            f"    {{ name: {_quote(i['name'])}, label: {_quote(i['label'])}, "
            f"type: {_quote(i['type'])}, defaultValue: {_num(i['default'])}"
        ),
    ]
    if "step" in i:
        parts.append(f", step: {_num(i['step'])}")
    if "min" in i:
        parts.append(f", min: {_num(i['min'])}")
    if "max" in i:
        parts.append(f", max: {_num(i['max'])}")
    if "description" in i:
        parts.append(f", description: {_quote(i['description'])}")
    parts.append(" }")
    return "".join(parts)


def _num(v):
    if isinstance(v, float):
        r = repr(v)
        if "e" in r:
            return format(v, ".10f").rstrip("0").rstrip(".")
        return r
    return repr(v)


def _emit_transform(m):
    """Emit the toParams transform for special-case methods."""
    t = m.get("transform")
    if t == "scorecard":
        return (
            "  toParams: (values) => ({\n"
            "    average_valuation: values.average_valuation,\n"
            "    weights: [0.3, 0.25, 0.15, 0.1, 0.1, 0.05, 0.05],\n"
            "    scores: [values.w0, values.w1, values.w2, values.w3, values.w4, values.w5, values.w6],\n"
            "  }),\n"
        )
    if t == "poisson":
        return "  toParams: (values) => ({ lambda_: values.rate, k: values.k }),\n"
    return ""


def _emit_config(m):
    lines = [
        f"export const {_config_name(m)}: MethodConfig = {{",
        f"  slug: {_quote(m['slug'])},",
        f"  name: {_quote(m['name'])},",
        f"  category: {_quote(m['category'])},",
        f"  description: {_quote(m['description'])},",
        f"  textbookChapter: {_quote(m['chapter'])},",
        f"  formulaNumber: {_quote(m['formula_number'])},",
        f"  methodName: {_quote(m['method_name'])},",
    ]
    t = _emit_transform(m)
    if t:
        lines.append(t.rstrip("\n"))
    lines.append("  inputs: [")
    for i in m["inputs"]:
        lines.append(_emit_input(i) + ",")
    lines.append("  ],")
    lines.append("};")
    return "\n".join(lines)


def _config_name(m):
    # explicit override for non-camelCase names
    if "config_name" in m:
        return m["config_name"]
    parts = m["slug"].split("-")
    return parts[0] + "".join(p.capitalize() for p in parts[1:]) + "Config"


def _group_by_module():
    groups = {}
    for m in METHODS:
        groups.setdefault(m["module"], []).append(m)
    return groups


def generate():
    check_reserved_words(METHODS)
    groups = _group_by_module()
    exports = []

    for module, methods in sorted(groups.items()):
        config_names = [_config_name(m) for m in methods]
        exports.extend(config_names)
        body = ['import type { MethodConfig } from "../valuation/types";', ""]
        for m in methods:
            body.append(_emit_config(m))
            body.append("")
        path = os.path.join(TS_DIR, f"{module}.ts")
        with open(path, "w") as f:
            f.write("\n".join(body).rstrip() + "\n")

    # index.ts
    index_lines = ['import type { MethodConfig } from "../valuation/types";']
    for module in sorted(groups.keys()):
        names = ", ".join(_config_name(m) for m in groups[module])
        index_lines.append(f'import {{ {names} }} from "./{module}";')
    index_lines.append("")
    index_lines.append("const methodConfigs: MethodConfig[] = [")
    for module in sorted(groups.keys()):
        for m in groups[module]:
            index_lines.append(f"  {_config_name(m)},")
    index_lines.append("];")
    index_lines.append("")
    index_lines.append("export function getAllMethods(): MethodConfig[] {")
    index_lines.append("  return methodConfigs;")
    index_lines.append("}")
    index_lines.append("")
    index_lines.append("export function getMethodBySlug(slug: string): MethodConfig | undefined {")
    index_lines.append("  return methodConfigs.find((m) => m.slug === slug);")
    index_lines.append("}")
    with open(os.path.join(TS_DIR, "index.ts"), "w") as f:
        f.write("\n".join(index_lines) + "\n")

    print(f"generated {len(METHODS)} methods across {len(groups)} modules")


if __name__ == "__main__":
    generate()
