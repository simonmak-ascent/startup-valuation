"""Tests for the optional Sentry observability module."""

from __future__ import annotations

from pathlib import Path

import pytest

from startup_valuation import observability
from startup_valuation.observability import (
    capture_exception,
    capture_message,
    init_sentry,
    report_verification,
    verify_and_report,
)
from startup_valuation.verification import Check, VerificationReport


class _FakeSentry:
    def __init__(self) -> None:
        self.init_calls: list[tuple[str, dict[str, object]]] = []
        self.exceptions: list[BaseException] = []
        self.messages: list[tuple[str, str]] = []
        self.tags: dict[str, str] = {}
        self.extras: dict[str, object] = {}

    def init(self, dsn: str | None = None, **kwargs: object) -> None:
        self.init_calls.append((dsn or "", kwargs))

    def capture_exception(self, error: BaseException) -> None:
        self.exceptions.append(error)

    def capture_message(self, message: str, level: str = "info") -> None:
        self.messages.append((level, message))

    def set_tag(self, key: str, value: str) -> None:
        self.tags[key] = value

    def set_extra(self, key: str, value: object) -> None:
        self.extras[key] = value


@pytest.fixture
def fake_sentry(monkeypatch: pytest.MonkeyPatch) -> _FakeSentry:
    fake = _FakeSentry()
    monkeypatch.setattr(observability, "_sentry_sdk", fake)
    monkeypatch.setattr(observability, "_INITIALIZED", True)
    return fake


def test_init_sentry_no_op_when_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(observability, "_sentry_sdk", None)
    monkeypatch.setattr(observability, "_INITIALIZED", False)
    assert init_sentry(dsn="https://example.ingest.sentry.io/1") is False


def test_init_sentry_no_op_without_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    assert init_sentry() is False


def test_init_sentry_enabled(fake_sentry: _FakeSentry) -> None:
    assert init_sentry(dsn="https://example.ingest.sentry.io/1") is True
    assert fake_sentry.init_calls == [("https://example.ingest.sentry.io/1", {})]


def test_capture_exception_no_op_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(observability, "_sentry_sdk", None)
    monkeypatch.setattr(observability, "_INITIALIZED", False)
    capture_exception(ValueError("boom"))  # must not raise


def test_capture_exception_enabled(fake_sentry: _FakeSentry) -> None:
    err = ValueError("boom")
    capture_exception(err)
    assert fake_sentry.exceptions == [err]


def test_capture_message_enabled(fake_sentry: _FakeSentry) -> None:
    capture_message("hello", level="warning")
    assert fake_sentry.messages == [("warning", "hello")]


def _report(achieved: bool) -> VerificationReport:
    status = "pass" if achieved else "fail"
    return VerificationReport(checks=[Check("C", "one", status)])


def test_report_verification_enabled(fake_sentry: _FakeSentry) -> None:
    assert report_verification(_report(True)) is True
    assert fake_sentry.tags["verification.achieved"] == "True"
    assert fake_sentry.tags["verification.coverage"] == "100.0"
    assert fake_sentry.messages[0][0] == "info"


def test_report_verification_failure(fake_sentry: _FakeSentry) -> None:
    assert report_verification(_report(False)) is True
    assert fake_sentry.messages[0][0] == "error"


def test_report_verification_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(observability, "_sentry_sdk", None)
    monkeypatch.setattr(observability, "_INITIALIZED", False)
    assert report_verification(_report(True)) is False


def test_verify_and_report_returns_report(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    sent = []

    def _fake_report(report: VerificationReport) -> bool:
        sent.append(report)
        return True

    def _fake_verify(project_root: str | Path, feature: str = "feature-1") -> VerificationReport:
        return _report(True)

    monkeypatch.setattr(observability, "report_verification", _fake_report)
    monkeypatch.setattr(observability, "verify_vision", _fake_verify)

    report = verify_and_report(tmp_path)
    assert report.achieved is True
    assert sent == [report]
