"""Core data types for valuation results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SensitivityResult:
    """Sensitivity analysis results."""

    input_name: str
    base_value: float
    sensitivity_10pct_up: float
    sensitivity_10pct_down: float
    pct_change_up: float
    pct_change_down: float


@dataclass
class ValuationResult:
    """Structured result from a valuation calculation.

    Attributes:
        value: The computed valuation.
        method: The valuation method name.
        inputs: All input parameters used.
        assumptions: Key assumptions made during calculation.
        sensitivity: Sensitivity analysis for key inputs.
        chapter: Textbook chapter reference.
        formula_number: Textbook formula number (e.g., '3.1').
        steps: Intermediate calculation steps for traceability.
    """

    value: float
    method: str
    inputs: dict[str, float | str | list[Any]] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    sensitivity: dict[str, SensitivityResult] = field(default_factory=dict)
    chapter: str = ""
    formula_number: str = ""
    steps: list[dict[str, str | float]] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.method}: ${self.value:,.2f}"

    def __repr__(self) -> str:
        return f"ValuationResult(value={self.value:.2f}, method='{self.method}')"


@dataclass
class Distribution:
    """Probability distribution for Monte Carlo simulation.

    Attributes:
        dist_type: Distribution type ('normal', 'uniform', 'triangular').
        params: Distribution parameters (mean/sd for normal, min/max for uniform,
                min/mode/max for triangular).
    """

    dist_type: str
    params: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        valid = {"normal", "uniform", "triangular"}
        if self.dist_type not in valid:
            raise ValueError(f"dist_type must be one of {valid}, got '{self.dist_type}'")


@dataclass
class Scenario:
    """A scenario for scenario analysis.

    Attributes:
        name: Scenario name (e.g., 'bull', 'base', 'bear').
        probability: Probability of this scenario (0-1).
        value: Valuation in this scenario.
    """

    name: str
    probability: float
    value: float

    def __post_init__(self) -> None:
        if not 0 <= self.probability <= 1:
            raise ValueError(f"probability must be between 0 and 1, got {self.probability}")
