"""Registry ↔ library consistency (the single-source-of-truth gate).

Guards the V-007 invariant: every valuation method is defined ONCE in
`method_registry/registry.py`, and the generated TypeScript configs /
`api/calculate.py` tool map are derived from it. If a method's inputs drift
from the library function signature, this test fails BEFORE deploy.
"""

import ast
import hashlib
import importlib.util
import inspect
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SHA-256 of the canonical (sorted, non-ASCII-preserved) registry. Pins every
# user-facing default value, chapter, formula number, and description. Changing
# the registry requires updating this golden hash after a conscious review.
GOLDEN_REGISTRY_SHA = "5a8e710c73345fc234f46f5f78b938ba9b66cfea2054cc08d2083579aa5a03fd"


def _load_registry():
    spec = importlib.util.spec_from_file_location("registry", os.path.join(REPO_ROOT, "method_registry", "registry.py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_library():
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))
    import startup_valuation  # noqa: F401

    return startup_valuation


def _load_named_tools():
    path = os.path.join(REPO_ROOT, "api", "calculate.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    named = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "_NAMED_TOOLS":
            value = node.value
            if not isinstance(value, ast.Dict):
                continue
            for k, v in zip(value.keys, value.values):
                if not isinstance(k, ast.Constant) or not isinstance(v, ast.Tuple):
                    continue
                param_list = v.elts[1]
                if not isinstance(param_list, ast.List):
                    continue
                params = [str(e.value) for e in param_list.elts if isinstance(e, ast.Constant)]
                named[str(k.value)] = params
    return named


# Expected params after the `transform` is applied (scorecard/poisson collapse
# their display inputs into library params).
TRANSFORM_PARAMS = {
    "scorecard": ["average_valuation", "weights", "scores"],
    "poisson": ["lambda_", "k"],
}


def test_registry_has_27_methods():
    reg = _load_registry()
    assert len(reg.METHODS) == 27


def test_registry_golden_hash_unchanged():
    reg = _load_registry()
    canonical = json.dumps(
        {"methods": reg.METHODS, "reserved_words": reg.RESERVED_WORDS},
        sort_keys=True,
        ensure_ascii=False,
    )
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    assert digest == GOLDEN_REGISTRY_SHA, "registry changed — review defaults/chapters, then update GOLDEN_REGISTRY_SHA"


def test_slugs_and_method_names_unique():
    reg = _load_registry()
    slugs = [m["slug"] for m in reg.METHODS]
    method_names = [m["method_name"] for m in reg.METHODS]
    assert len(slugs) == len(set(slugs)), "duplicate slugs"
    assert len(method_names) == len(set(method_names)), "duplicate method_names"


def test_no_reserved_words():
    reg = _load_registry()
    reserved = set(reg.RESERVED_WORDS)
    for m in reg.METHODS:
        names = [m["slug"], m["method_name"], m["function"]] + [i["name"] for i in m["inputs"]]
        for n in names:
            assert n.lower() not in reserved, f"reserved word '{n}' in {m['slug']}"


def test_registry_inputs_match_library_signatures():
    reg = _load_registry()
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))
    for m in reg.METHODS:
        module = importlib.import_module(f"startup_valuation.{m['module']}")
        func = getattr(module, m["function"])
        sig = inspect.signature(func)
        all_params = list(sig.parameters.keys())
        required = [p for p, v in sig.parameters.items() if v.default is inspect.Parameter.empty]
        expected = TRANSFORM_PARAMS.get(m.get("transform"), [i["name"] for i in m["inputs"]])
        assert set(expected) <= set(all_params), (
            f"{m['slug']}: registry inputs {expected} not all valid params of {all_params}"
        )
        assert set(required) <= set(expected), (
            f"{m['slug']}: required params {required} not covered by registry {expected}"
        )


def test_registry_maps_to_named_tools():
    reg = _load_registry()
    named = _load_named_tools()
    assert named, "_NAMED_TOOLS not found in api/calculate.py"
    for m in reg.METHODS:
        mn = m["method_name"]
        assert mn in named, f"{m['slug']}: method_name '{mn}' missing from api/calculate.py"
        expected = TRANSFORM_PARAMS.get(m.get("transform"), [i["name"] for i in m["inputs"]])
        assert named[mn] == expected, f"{m['slug']}: _NAMED_TOOLS params {named[mn]} != registry {expected}"
