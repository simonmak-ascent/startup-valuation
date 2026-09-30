"""Tests for the verification module."""

from __future__ import annotations

from pathlib import Path

import pytest

from startup_valuation.verification import (
    Check,
    VerificationReport,
    VisionModel,
    check_artifacts,
    check_impact_coverage,
    check_placeholders,
    check_task_completion,
    check_test_presence,
    check_vision_concrete,
    extract_acceptance_criteria,
    extract_impacts,
    extract_metrics,
    extract_tasks,
    parse_vision,
    verify_public_claims,
    verify_vision,
)

_FEATURE = "feature-1"

_CHAIN_FILES: dict[str, str] = {
    "constitution.md": "# Constitution\n\n## Technology Stack\n\nPython 3.10.\n",
    "vdd/vision.md": (
        "# Vision\n\n"
        "## Vision Statement\n\n> build a verification module\n\n"
        "### Goal (the desired future state)\n\n"
        "A single command yields a 100% coverage report.\n\n"
        "### Actors (who must behave differently)\n\n"
        "| Actor | Current State | Desired State | Benefit |\n"
        "|-------|--------------|---------------|---------|\n"
        "| Agent | manual | automated | trust |\n\n"
        "### Impacts (the behavioral changes that produce the goal)\n\n"
        "| Impact ID | Description | Actor | Measurement |\n"
        "|-----------|-------------|-------|-------------|\n"
        "| I-001 | run verification | Agent | coverage |\n"
        "| I-002 | map impacts to ACs | Agent | coverage check |\n\n"
        "## Success Metrics\n\n"
        "### Lagging Indicators (the outcomes)\n\n"
        "| Metric | Target | Measurement Method |\n"
        "|--------|--------|-------------------|\n"
        "| Coverage score | 100% | report.coverage |\n\n"
        "## Target Domains\n\n- [x] WebApp\n"
    ),
    "vdd/strategy.md": "# Strategy\n\n## Strategic Pillars\n\n### Pillar 1: Deterministic gate\n",
    "vdd/tactics.md": "# Tactics\n\n## Prioritized Action Items\n",
    "vdd/specs/feature-1/spec.md": (
        "# Verification Module\n\n"
        "## Acceptance Criteria\n\n"
        "### AC-1: Structured report [MUST]\n"
        "Given a root\nWhen called\nThen returns a report\n\n"
        "### AC-2: Artifact completeness [MUST]\n"
        "Covers I-001 and I-002.\n"
    ),
    "vdd/specs/feature-1/plan.md": "# Plan\n\n## Component Breakdown\n",
    "vdd/specs/feature-1/data-model.md": "# Data Model\n\n## Entities\n",
    "vdd/specs/feature-1/contracts/primary-endpoint.md": "# Contract\n\n## verify_vision\n",
    "vdd/specs/feature-1/tasks.md": (
        "# Tasks\n\n## Tasks\n\n- [x] **TASK-001** [S] skeleton\n\n- [x] **TASK-002** [M] tests\n"
    ),
    "vdd/impact-report.md": "# Impact Report\n\n## Summary\n",
}


def _write(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_valid_chain(root: Path) -> None:
    for rel, content in _CHAIN_FILES.items():
        _write(root, rel, content)
    _write(root, "src/startup_valuation/core.py", "def f() -> int:\n    return 1\n")
    _write(root, "tests/test_core.py", "def test_f():\n    pass\n")


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


class _FakeVerifier:
    name = "fake-tool"

    def __init__(self, result: bool) -> None:
        self._result = result

    def verify(self, claim: str) -> bool:
        return self._result


def test_report_coverage_and_achieved() -> None:
    report = VerificationReport(
        checks=[
            Check("A", "one", "pass"),
            Check("B", "two", "pass"),
            Check("C", "three", "fail"),
            Check("D", "four", "warn"),
            Check("E", "five", "skip"),
        ]
    )
    assert report.total == 5
    assert report.passed == 2
    assert report.failed == 1
    assert report.warnings == 1
    assert report.skipped == 1
    assert report.coverage == pytest.approx(66.67)
    assert report.achieved is False


def test_verify_vision_full_chain_reports_100(tmp_path: Path) -> None:
    _write_valid_chain(tmp_path)
    report = verify_vision(tmp_path, feature=_FEATURE)
    assert report.coverage == pytest.approx(100.0)
    assert report.achieved is True
    assert report.failed == 0


def test_check_artifacts_missing(tmp_path: Path) -> None:
    check = check_artifacts(tmp_path, feature=_FEATURE)
    assert check.status == "fail"
    assert "constitution.md" in check.evidence


def test_check_placeholders_detects_marker(tmp_path: Path) -> None:
    _write(tmp_path, "vdd/strategy.md", "# Strategy\n\n[e.g., something unresolved]\n")
    check = check_placeholders(tmp_path, feature=_FEATURE)
    assert check.status == "fail"
    assert "[e.g." in check.evidence


def test_check_placeholders_passes_when_clean(tmp_path: Path) -> None:
    _write_valid_chain(tmp_path)
    check = check_placeholders(tmp_path, feature=_FEATURE)
    assert check.status == "pass"


def test_verify_vision_missing_chain_no_exception(tmp_path: Path) -> None:
    report = verify_vision(tmp_path, feature=_FEATURE)
    assert report.failed >= 1
    assert any(c.check_id == "VDD.ARTIFACTS" and c.status == "fail" for c in report.checks)


def test_check_vision_concrete(tmp_path: Path) -> None:
    _write_valid_chain(tmp_path)
    vision = parse_vision(tmp_path / "vdd" / "vision.md")
    assert vision.goal == "A single command yields a 100% coverage report."
    assert vision.impacts == ["I-001", "I-002"]
    assert check_vision_concrete(vision).status == "pass"


def test_check_impact_coverage_uncovered() -> None:
    vision = VisionModel(goal="g", impacts=["I-001", "I-002"])
    check = check_impact_coverage(vision, "this spec mentions I-001 only")
    assert check.status == "fail"
    assert "I-002" in check.evidence


def test_check_task_completion_incomplete() -> None:
    tasks = [{"id": "TASK-001", "done": True}, {"id": "TASK-002", "done": False}]
    check = check_task_completion(tasks)
    assert check.status == "fail"
    assert "TASK-002" in check.evidence


def test_check_test_presence_missing(tmp_path: Path) -> None:
    _write(tmp_path, "src/startup_valuation/core.py", "x = 1\n")
    check = check_test_presence(
        tmp_path / "src" / "startup_valuation",
        tmp_path / "tests",
    )
    assert check.status == "fail"
    assert "test_core.py" in check.evidence


def test_verify_public_claims() -> None:
    report = verify_public_claims(["formula is correct", "api exists"], _FakeVerifier(True))
    assert report.passed == 2
    assert report.achieved is True

    failing = verify_public_claims(["made up claim"], _FakeVerifier(False))
    assert failing.failed == 1
    assert failing.achieved is False


def test_extractors(tmp_path: Path) -> None:
    _write_valid_chain(tmp_path)
    spec = _read(tmp_path, "vdd/specs/feature-1/spec.md")
    tasks = _read(tmp_path, "vdd/specs/feature-1/tasks.md")
    vision = _read(tmp_path, "vdd/vision.md")

    assert extract_acceptance_criteria(spec) == ["AC-1", "AC-2"]
    assert [t["id"] for t in extract_tasks(tasks)] == ["TASK-001", "TASK-002"]
    assert all(t["done"] for t in extract_tasks(tasks))
    assert extract_impacts(vision) == ["I-001", "I-002"]
    metrics = extract_metrics(vision)
    assert len(metrics) == 1
    assert metrics[0]["name"] == "Coverage score"


def test_coverage_zero_when_no_decisive_checks() -> None:
    report = VerificationReport(checks=[Check("a", "warned", "warn"), Check("b", "skipped", "skip")])
    assert report.coverage == 0.0
    assert report.achieved is False


def test_parse_vision_without_goal(tmp_path: Path) -> None:
    path = _write(tmp_path, "vision.md", "# Vision\n\n## Success Metrics\n\n| Metric | Target | Method |\n")
    assert parse_vision(path).goal == ""


def test_check_artifacts_empty_file(tmp_path: Path) -> None:
    _write(tmp_path, "constitution.md", "")
    check = check_artifacts(tmp_path, feature=_FEATURE)
    assert check.status == "fail"
    assert "(empty)" in check.evidence


def test_check_vision_concrete_fails() -> None:
    vision = VisionModel(goal="> raw statement", impacts=[], metrics=[])
    check = check_vision_concrete(vision)
    assert check.status == "fail"
    assert "goal is empty or still the raw statement" in check.detail
    assert "no impact IDs" in check.detail
    assert "no success metrics" in check.detail


def test_check_impact_coverage_skip_without_impacts() -> None:
    vision = VisionModel(goal="g", impacts=[])
    assert check_impact_coverage(vision, "spec text").status == "skip"


def test_check_task_completion_skip_without_tasks() -> None:
    assert check_task_completion([]).status == "skip"


def test_check_test_presence_skips_and_ignores_special_files(tmp_path: Path) -> None:
    src = tmp_path / "src" / "startup_valuation"
    tests = tmp_path / "tests"
    src.mkdir(parents=True)
    tests.mkdir(parents=True)

    assert check_test_presence(src, tests).status == "skip"

    (src / "__init__.py").write_text("")
    (src / "types.py").write_text("")
    (src / "core.py").write_text("x = 1")
    (tests / "test_core.py").write_text("")

    assert check_test_presence(src, tests).status == "pass"
