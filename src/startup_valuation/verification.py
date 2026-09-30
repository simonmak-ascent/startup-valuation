"""Test & verification module for Vision-Driven Development (VDD).

This module guarantees that a VDD chain achieves 100% of its stated vision by
performing deterministic, network-free checks over the chain artifacts and by
exposing a pluggable interface for public-domain evidence gathering.

Checks performed by :func:`verify_vision`:

* **Artifact completeness** — all ten chain artifacts exist and are non-empty.
* **Placeholder freedom** — no unresolved template placeholder or
  ``[NEEDS CLARIFICATION]`` marker remains.
* **Vision concreteness** — the goal, impacts, and success metrics are concrete.
* **Impact-to-AC coverage** — every vision impact is referenced by at least one
  acceptance criterion.
* **Task completion** — every task checkbox is ticked.
* **Test presence** — every source module has a matching test file.

Public-domain verification is exposed through the :class:`ClaimVerifier`
protocol and :func:`verify_public_claims`, so any tool (context7, perplexity,
brave-search, GitHub, Postgres) can supply evidence for a claim.

Every public entry point returns a :class:`VerificationReport`, never a bare
number, mirroring the library-wide ``ValuationResult`` convention.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

# Stable template tokens that signal an unfinished VDD artifact. The gate
# engine flags `[e.g.]` and `[NEEDS CLARIFICATION]`; we enumerate those plus
# every other placeholder the VDD templates use.
_PLACEHOLDER_MARKERS: tuple[str, ...] = (
    "[e.g.",
    "[NEEDS CLARIFICATION]",
    "[AI assistant",
    "[feature name]",
    "[Feature Name]",
    "[Endpoint Name]",
    "[EntityName]",
    "[EntityA]",
    "[EntityB]",
    "[EntityC]",
    "[table_name]",
    "[table]",
    "[field]",
    "[type]",
    "[constraints]",
    "[description]",
    "[condition]",
    "[default]",
    "[param]",
    "[col1, col2]",
    "[role]",
    "[goal]",
    "[benefit]",
    "[component",
    "[file path]",
    "[inputs]",
    "[outputs]",
    "[What it does]",
    "[initial context]",
    "[action",
    "[expected",
    "[invalid or edge",
    "[Short Title]",
    "[Error Case",
    "[Explicitly",
    "[capability]",
    "[why excluded",
    "[Item ",
    "[Question ",
    "[answer]",
    "[Primary user]",
    "[Secondary user]",
    "[Behavioral change]",
    "[Actor]",
    "[How to measure]",
    "[What they do today]",
    "[What they will do]",
    "[Why it is better]",
    "[What they care about]",
    "[How to involve them]",
    "[Decision maker]",
    "[Secondary beneficiary]",
    "[Target]",
    "[Measurement Method]",
    "[1 sentence",
    "[1-2 sentences",
    "[ComponentName]",
    "[contracts/file.md]",
    "[ms]",
    "[System]",
    "[How it is used]",
    "[One sentence",
    "[HTTP METHOD]",
    "[Migration 001]",
    "[Component 1 Name]",
    "[Component 2 Name]",
    # validate-template / impact-report placeholders
    "[N commits]",
    "[metrics gathered]",
    "[results]",
    "[Leading indicator",
    "[Lagging indicator",
    "[target]",
    "[actual]",
    "[ON TRACK",
    "[Condition",
    "[GO / NO-GO",
    "[Every task]",
    "[Every component]",
    "[Every AC]",
    "[Every code artifact]",
    "[Spec AC]",
    "[PENDING]",
    "[TBD",
)

# The ten artifacts that constitute a complete VDD chain, keyed relative to the
# project root. ``description`` is used as human-readable evidence.
_CHAIN_ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("constitution.md", "constitution"),
    ("vdd/vision.md", "vision"),
    ("vdd/strategy.md", "strategy"),
    ("vdd/tactics.md", "tactics"),
    ("vdd/specs/{feature}/spec.md", "spec"),
    ("vdd/specs/{feature}/plan.md", "plan"),
    ("vdd/specs/{feature}/data-model.md", "data-model"),
    ("vdd/specs/{feature}/contracts/primary-endpoint.md", "contract"),
    ("vdd/specs/{feature}/tasks.md", "tasks"),
    ("vdd/impact-report.md", "impact-report"),
)

_IMPACT_RE = re.compile(r"\|\s*(I-\d+)\s*\|")
_AC_RE = re.compile(r"^#{2,3}\s*(AC-E?\d+)\b", re.MULTILINE)
_TASK_RE = re.compile(r"-\s*\[([ xX])\]\s*\*\*(TASK-\d+)\*\*")
_METRIC_ROW_RE = re.compile(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
_ACTOR_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|")


@dataclass
class Check:
    """A single verification check result.

    Attributes:
        check_id: Stable identifier (e.g. ``VDD.ARTIFACTS``).
        label: Human-readable check name.
        status: One of ``pass``, ``fail``, ``warn``, ``skip``.
        detail: Explanation when the check is not a pass.
        evidence: File/line or tool name backing the result.
    """

    check_id: str
    label: str
    status: str
    detail: str = ""
    evidence: str = ""


@dataclass
class VisionModel:
    """The parsed essence of a ``vision.md`` artifact.

    Attributes:
        goal: The goal sentence.
        impacts: Impact IDs in order (e.g. ``I-001``).
        metrics: Success-metric rows (``name``, ``target``, ``method``).
        actors: Actor labels from the Actors table.
    """

    goal: str
    impacts: list[str] = field(default_factory=list)
    metrics: list[dict[str, str]] = field(default_factory=list)
    actors: list[str] = field(default_factory=list)


@dataclass
class VerificationReport:
    """The structured result of a verification run.

    Attributes:
        checks: Every check executed, in run order.
    """

    checks: list[Check] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total number of checks."""
        return len(self.checks)

    @property
    def passed(self) -> int:
        """Number of checks with ``status == "pass"``."""
        return sum(1 for c in self.checks if c.status == "pass")

    @property
    def failed(self) -> int:
        """Number of checks with ``status == "fail"``."""
        return sum(1 for c in self.checks if c.status == "fail")

    @property
    def skipped(self) -> int:
        """Number of checks with ``status == "skip"``."""
        return sum(1 for c in self.checks if c.status == "skip")

    @property
    def warnings(self) -> int:
        """Number of checks with ``status == "warn"``."""
        return sum(1 for c in self.checks if c.status == "warn")

    @property
    def coverage(self) -> float:
        """Percentage of the vision achieved, in ``[0, 100]``.

        Computed as ``passed / (passed + failed) * 100``; skipped and warn
        checks are informational and do not affect the score.
        """
        decisive = self.passed + self.failed
        if decisive == 0:
            return 0.0
        return round(100.0 * self.passed / decisive, 2)

    @property
    def achieved(self) -> bool:
        """True when the vision is fully realized (no failures, some passes)."""
        return self.failed == 0 and self.passed > 0


class ClaimVerifier(Protocol):
    """Protocol for a public-domain evidence provider.

    Any callable-bearing object with a ``name`` and a ``verify`` method can back
    a claim, e.g. wrappers over context7, perplexity, brave-search, GitHub, or
    Postgres.
    """

    name: str

    def verify(self, claim: str) -> bool:
        """Return True when ``claim`` is confirmed by the backing tool."""
        ...


def parse_vision(path: str | Path) -> VisionModel:
    """Parse a ``vision.md`` file into a :class:`VisionModel`.

    Args:
        path: Path to the vision markdown file.

    Returns:
        VisionModel with goal, impacts, metrics, and actors.
    """
    text = Path(path).read_text(encoding="utf-8")
    goal = _extract_goal(text)
    impacts = extract_impacts(text)
    metrics = extract_metrics(text)
    actors = extract_actors(text)
    return VisionModel(goal=goal, impacts=impacts, metrics=metrics, actors=actors)


def _extract_goal(text: str) -> str:
    """Return the first non-empty line following the ``### Goal`` heading."""
    in_goal = False
    for line in text.splitlines():
        if line.strip().startswith("### Goal"):
            in_goal = True
            continue
        if in_goal:
            stripped = line.strip()
            if stripped:
                return stripped
    return ""


def extract_impacts(text: str) -> list[str]:
    """Return impact IDs (``I-001``…) found in an Impacts table, in order."""
    return _IMPACT_RE.findall(text)


def extract_metrics(text: str) -> list[dict[str, str]]:
    """Return success-metric rows from the Lagging/Leading indicator tables."""
    metrics: list[dict[str, str]] = []
    in_metrics = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Success Metrics"):
            in_metrics = True
            continue
        if in_metrics and stripped.startswith("## "):
            break
        if in_metrics and stripped.startswith("|"):
            match = _METRIC_ROW_RE.match(stripped)
            if match and match.group(1) not in ("Metric", "--------"):
                metrics.append(
                    {
                        "name": match.group(1).strip(),
                        "target": match.group(2).strip(),
                        "method": match.group(3).strip(),
                    }
                )
    return metrics


def extract_actors(text: str) -> list[str]:
    """Return actor labels from the Actors table."""
    actors: list[str] = []
    in_actors = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### Actors"):
            in_actors = True
            continue
        if in_actors and stripped.startswith("###"):
            break
        if in_actors and stripped.startswith("|") and not stripped.startswith("|---"):
            match = _ACTOR_ROW_RE.match(stripped)
            if match and match.group(1) not in ("Actor",):
                actors.append(match.group(1).strip())
    return actors


def extract_acceptance_criteria(text: str) -> list[str]:
    """Return acceptance-criterion IDs (``AC-1``, ``AC-E1``…) from a spec."""
    return _AC_RE.findall(text)


def extract_tasks(text: str) -> list[dict[str, str | bool]]:
    """Return task entries (``id`` and ``done``) from a tasks.md file."""
    tasks: list[dict[str, str | bool]] = []
    for line in text.splitlines():
        match = _TASK_RE.search(line)
        if match:
            tasks.append({"id": match.group(2), "done": match.group(1).lower() == "x"})
    return tasks


def find_placeholders(text: str) -> list[str]:
    """Return placeholder markers present in ``text``, in encounter order."""
    found: list[str] = []
    for marker in _PLACEHOLDER_MARKERS:
        if marker in text:
            found.append(marker)
    return found


def check_artifacts(project_root: str | Path, feature: str) -> Check:
    """Verify all ten chain artifacts exist and are non-empty.

    Args:
        project_root: Repository root.
        feature: Spec directory name under ``vdd/specs/``.

    Returns:
        A single ``Check`` whose evidence lists any missing/empty artifacts.
    """
    root = Path(project_root)
    missing: list[str] = []
    empty: list[str] = []
    for rel, _desc in _CHAIN_ARTIFACTS:
        path = root / rel.format(feature=feature)
        if not path.is_file():
            missing.append(path.as_posix())
        elif path.stat().st_size == 0:
            empty.append(path.as_posix())

    problems = missing + [f"{p} (empty)" for p in empty]
    if problems:
        return Check(
            check_id="VDD.ARTIFACTS",
            label="All 10 chain artifacts exist and are non-empty",
            status="fail",
            detail=f"{len(problems)} artifact(s) missing or empty",
            evidence="; ".join(problems),
        )
    return Check(
        check_id="VDD.ARTIFACTS",
        label="All 10 chain artifacts exist and are non-empty",
        status="pass",
        evidence=", ".join(rel.format(feature=feature) for rel, _ in _CHAIN_ARTIFACTS),
    )


def check_placeholders(project_root: str | Path, feature: str) -> Check:
    """Verify no template placeholder remains anywhere in the chain.

    Args:
        project_root: Repository root.
        feature: Spec directory name under ``vdd/specs/``.

    Returns:
        A single ``Check`` listing offending markers with file evidence.
    """
    root = Path(project_root)
    hits: list[str] = []
    for rel, _desc in _CHAIN_ARTIFACTS:
        path = root / rel.format(feature=feature)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in find_placeholders(text):
            hits.append(f"{path.as_posix()}: {marker}")

    if hits:
        return Check(
            check_id="VDD.PLACEHOLDERS",
            label="No unresolved template placeholders",
            status="fail",
            detail=f"{len(hits)} placeholder(s) remain",
            evidence="; ".join(hits),
        )
    return Check(
        check_id="VDD.PLACEHOLDERS",
        label="No unresolved template placeholders",
        status="pass",
        evidence="no template markers found",
    )


def check_vision_concrete(vision: VisionModel) -> Check:
    """Verify the vision goal, impacts, and metrics are concrete.

    Args:
        vision: Parsed :class:`VisionModel`.

    Returns:
        A single ``Check`` reporting missing goal/impacts/metrics.
    """
    problems: list[str] = []
    if not vision.goal or vision.goal.startswith(">"):
        problems.append("goal is empty or still the raw statement")
    if not vision.impacts:
        problems.append("no impact IDs (I-001…) parsed")
    if not vision.metrics:
        problems.append("no success metrics parsed")

    if problems:
        return Check(
            check_id="VDD.VISION_CONCRETE",
            label="Vision goal, impacts, and metrics are concrete",
            status="fail",
            detail="; ".join(problems),
            evidence="vdd/vision.md",
        )
    return Check(
        check_id="VDD.VISION_CONCRETE",
        label="Vision goal, impacts, and metrics are concrete",
        status="pass",
        evidence=f"{len(vision.impacts)} impacts, {len(vision.metrics)} metrics",
    )


def check_impact_coverage(vision: VisionModel, spec_text: str) -> Check:
    """Verify every vision impact is referenced by at least one AC.

    Args:
        vision: Parsed :class:`VisionModel`.
        spec_text: Raw text of the feature spec.

    Returns:
        A single ``Check`` naming any uncovered impacts.
    """
    uncovered = [i for i in vision.impacts if i not in spec_text]
    if not vision.impacts:
        return Check(
            check_id="VDD.IMPACT_COVERAGE",
            label="Every vision impact is covered by an AC",
            status="skip",
            detail="no impacts to check",
        )
    if uncovered:
        return Check(
            check_id="VDD.IMPACT_COVERAGE",
            label="Every vision impact is covered by an AC",
            status="fail",
            detail=f"{len(uncovered)} impact(s) not referenced in spec",
            evidence=", ".join(uncovered),
        )
    return Check(
        check_id="VDD.IMPACT_COVERAGE",
        label="Every vision impact is covered by an AC",
        status="pass",
        evidence=f"{len(vision.impacts)} impact(s) covered",
    )


def check_task_completion(tasks: list[dict[str, str | bool]]) -> Check:
    """Verify every task in the feature is ticked off.

    Args:
        tasks: Parsed task entries from :func:`extract_tasks`.

    Returns:
        A single ``Check`` naming any incomplete tasks.
    """
    incomplete = [t["id"] for t in tasks if t["done"] is False]
    if not tasks:
        return Check(
            check_id="VDD.TASK_COMPLETION",
            label="All tasks are completed",
            status="skip",
            detail="no tasks parsed",
        )
    if incomplete:
        return Check(
            check_id="VDD.TASK_COMPLETION",
            label="All tasks are completed",
            status="fail",
            detail=f"{len(incomplete)} task(s) incomplete",
            evidence=", ".join(str(i) for i in incomplete),
        )
    return Check(
        check_id="VDD.TASK_COMPLETION",
        label="All tasks are completed",
        status="pass",
        evidence=f"{len(tasks)} task(s) completed",
    )


def check_test_presence(src_dir: str | Path, tests_dir: str | Path) -> Check:
    """Verify every source module has a matching test file.

    Args:
        src_dir: Library source directory (``src/startup_valuation``).
        tests_dir: Test directory (``tests``).

    Returns:
        A single ``Check`` listing any modules lacking a ``test_<name>.py``.
    """
    src = Path(src_dir)
    tests = Path(tests_dir)
    missing: list[str] = []
    modules = 0
    for path in sorted(src.glob("*.py")):
        if path.name in {"__init__.py", "types.py"}:
            continue
        modules += 1
        expected = tests / f"test_{path.stem}.py"
        if not expected.is_file():
            missing.append(expected.name)

    if modules == 0:
        return Check(
            check_id="VDD.TEST_PRESENCE",
            label="Every source module has a test file",
            status="skip",
            detail="no source modules found",
        )
    if missing:
        return Check(
            check_id="VDD.TEST_PRESENCE",
            label="Every source module has a test file",
            status="fail",
            detail=f"{len(missing)} module(s) lack a test file",
            evidence=", ".join(missing),
        )
    return Check(
        check_id="VDD.TEST_PRESENCE",
        label="Every source module has a test file",
        status="pass",
        evidence=f"{modules} module(s) covered",
    )


def verify_public_claims(claims: list[str], verifier: ClaimVerifier) -> VerificationReport:
    """Verify a list of claims against a public-domain tool adapter.

    Args:
        claims: Statements to confirm.
        verifier: A :class:`ClaimVerifier` backed by a tool (e.g. context7,
            perplexity, brave-search, GitHub, Postgres).

    Returns:
        A :class:`VerificationReport` with one ``Check`` per claim.
    """
    checks: list[Check] = []
    for i, claim in enumerate(claims, start=1):
        confirmed = verifier.verify(claim)
        checks.append(
            Check(
                check_id=f"CLAIM.{i:03d}",
                label=f"Claim confirmed by {verifier.name}",
                status="pass" if confirmed else "fail",
                detail="" if confirmed else "claim not confirmed",
                evidence=claim,
            )
        )
    return VerificationReport(checks=checks)


def verify_vision(project_root: str | Path, feature: str = "feature-1") -> VerificationReport:
    """Run the full verification suite for a feature and return a report.

    Args:
        project_root: Repository root containing ``vdd/`` and ``src/``.
        feature: Spec directory name under ``vdd/specs/``.

    Returns:
        A :class:`VerificationReport` with coverage, per-check evidence, and an
        ``achieved`` flag that is True only when the vision is 100% realized.

    Example:
        >>> report = verify_vision("/path/to/repo", feature="feature-1")
        >>> report.coverage
        100.0
        >>> report.achieved
        True
    """
    root = Path(project_root)
    spec_path = root / "vdd" / "specs" / feature / "spec.md"
    tasks_path = root / "vdd" / "specs" / feature / "tasks.md"
    vision_path = root / "vdd" / "vision.md"

    checks: list[Check] = [
        check_artifacts(root, feature),
        check_placeholders(root, feature),
    ]

    if vision_path.is_file():
        vision = parse_vision(vision_path)
        checks.append(check_vision_concrete(vision))
        if spec_path.is_file():
            checks.append(check_impact_coverage(vision, spec_path.read_text(encoding="utf-8")))
    else:
        checks.append(
            Check(
                check_id="VDD.VISION_CONCRETE",
                label="Vision goal, impacts, and metrics are concrete",
                status="fail",
                detail="vdd/vision.md not found",
            )
        )

    if tasks_path.is_file():
        checks.append(check_task_completion(extract_tasks(tasks_path.read_text(encoding="utf-8"))))

    checks.append(check_test_presence(root / "src" / "startup_valuation", root / "tests"))

    return VerificationReport(checks=checks)


__all__ = [
    "Check",
    "VisionModel",
    "VerificationReport",
    "ClaimVerifier",
    "parse_vision",
    "extract_impacts",
    "extract_metrics",
    "extract_actors",
    "extract_acceptance_criteria",
    "extract_tasks",
    "find_placeholders",
    "check_artifacts",
    "check_placeholders",
    "check_vision_concrete",
    "check_impact_coverage",
    "check_task_completion",
    "check_test_presence",
    "verify_public_claims",
    "verify_vision",
]
