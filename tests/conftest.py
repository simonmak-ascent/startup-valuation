"""Shared test configuration."""

import pytest


@pytest.fixture
def sample_scenarios():
    """Standard bull/base/bear scenarios."""
    from startup_valuation.types import Scenario
    return [
        Scenario("bull", 0.20, 10_000_000),
        Scenario("base", 0.60, 5_000_000),
        Scenario("bear", 0.20, 1_000_000),
    ]
