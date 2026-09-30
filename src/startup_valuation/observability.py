"""Optional Sentry instrumentation for the verification module.

Sentry is opt-in and dependency-free by default: if ``sentry-sdk`` is not
installed or no DSN is configured, every function is a no-op. This keeps the
core package's dependency floor at ``numpy``/``scipy`` (see constitution.md)
while wiring verification runs into the workflow's observability stack.

Install the optional extra with ``pip install -e ".[sentry]"`` and set the
``SENTRY_DSN`` environment variable (or pass ``dsn`` explicitly) to enable
telemetry.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from startup_valuation.verification import VerificationReport, verify_vision

try:
    import sentry_sdk as _sentry_sdk  # isort: skip
except ImportError:  # pragma: no cover - exercised only without sentry-sdk
    _sentry_sdk = None

_INITIALIZED = False


def init_sentry(dsn: str | None = None, **kwargs: Any) -> bool:
    """Initialize Sentry from ``dsn`` or the ``SENTRY_DSN`` env var.

    Args:
        dsn: Sentry DSN. Falls back to the ``SENTRY_DSN`` environment variable.
        kwargs: Extra keyword arguments forwarded to ``sentry_sdk.init``.

    Returns:
        True when Sentry was initialized, False when the SDK is absent or no
        DSN is available (a safe no-op).
    """
    global _INITIALIZED
    resolved = dsn or os.environ.get("SENTRY_DSN")
    if _sentry_sdk is None or not resolved:
        return False
    _sentry_sdk.init(dsn=resolved, **kwargs)
    _INITIALIZED = True
    return True


def capture_exception(error: BaseException) -> None:
    """Report an exception to Sentry if enabled, otherwise a no-op."""
    if _sentry_sdk is not None and _INITIALIZED:
        _sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info") -> None:
    """Report a message to Sentry if enabled, otherwise a no-op."""
    if _sentry_sdk is not None and _INITIALIZED:
        _sentry_sdk.capture_message(message, level=level)


def report_verification(report: VerificationReport) -> bool:
    """Send a verification summary (coverage + outcome) to Sentry.

    Args:
        report: The :class:`VerificationReport` produced by ``verify_vision``.

    Returns:
        True when the summary was sent, False when Sentry is disabled.
    """
    if _sentry_sdk is None or not _INITIALIZED:
        return False
    _sentry_sdk.set_tag("verification.achieved", str(report.achieved))
    _sentry_sdk.set_tag("verification.coverage", str(report.coverage))
    _sentry_sdk.set_extra("verification.failed", report.failed)
    level = "info" if report.achieved else "error"
    _sentry_sdk.capture_message(f"Vision verification: {report.coverage}%", level=level)
    return True


def verify_and_report(project_root: str | Path, feature: str = "feature-1") -> VerificationReport:
    """Run verification and report the summary to Sentry (opt-in).

    Args:
        project_root: Repository root containing ``vdd/`` and ``src/``.
        feature: Spec directory name under ``vdd/specs/``.

    Returns:
        The :class:`VerificationReport`, regardless of Sentry availability.
    """
    report = verify_vision(project_root, feature=feature)
    report_verification(report)
    return report


__all__ = [
    "init_sentry",
    "capture_exception",
    "capture_message",
    "report_verification",
    "verify_and_report",
]
