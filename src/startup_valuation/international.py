"""International valuation methods.

Chapter 12: International Valuation Considerations
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def purchasing_power_parity(
    spot_rate: float,
    inflation_foreign: float,
    inflation_domestic: float,
) -> ValuationResult:
    """Calculate PPP-adjusted exchange rate.

    Formula: Eₜ = E₀ × (1 + π_foreign) / (1 + π_domestic)

    Example:
        >>> result = purchasing_power_parity(83, 0.05, 0.02)
        >>> round(result.value, 1)
        85.4
    """
    rate = spot_rate * (1 + inflation_foreign) / (1 + inflation_domestic)
    return ValuationResult(
        value=rate,
        method="Purchasing Power Parity",
        inputs={
            "spot_rate": spot_rate,
            "inflation_foreign": inflation_foreign,
            "inflation_domestic": inflation_domestic,
        },
        chapter="12",
    )


def interest_rate_parity(
    spot_rate: float,
    rate_foreign: float,
    rate_domestic: float,
) -> ValuationResult:
    """Calculate forward rate using interest rate parity.

    Formula: F = S × (1 + r_foreign) / (1 + r_domestic)
    """
    return ValuationResult(
        value=spot_rate * (1 + rate_foreign) / (1 + rate_domestic),
        method="Interest Rate Parity",
        inputs={
            "spot_rate": spot_rate,
            "rate_foreign": rate_foreign,
            "rate_domestic": rate_domestic,
        },
        chapter="12",
    )


def currency_adjusted_dcf(
    cash_flows_local: list[float],
    exchange_rates: list[float],
    discount_rate_usd: float,
) -> ValuationResult:
    """Calculate currency-adjusted DCF.

    Formula: PV = Σ[CFₜ^local / Eₜ] / (1 + r_USD)^t
    """
    if len(cash_flows_local) != len(exchange_rates):
        raise ValueError("cash_flows_local and exchange_rates must have same length")

    pv = sum(
        (cf / e) / ((1 + discount_rate_usd) ** t)
        for t, (cf, e) in enumerate(zip(cash_flows_local, exchange_rates))
    )

    return ValuationResult(
        value=pv,
        method="Currency-Adjusted DCF",
        inputs={
            "cash_flows_local": cash_flows_local,
            "exchange_rates": exchange_rates,
            "discount_rate_usd": discount_rate_usd,
        },
        chapter="12",
    )


def country_risk_premium(
    sovereign_yield: float,
    us_treasury_yield: float,
) -> ValuationResult:
    """Calculate country risk premium using sovereign spread.

    Formula: CRP = Sovereign Bond Yield_local - US Treasury Yield

    Example:
        >>> result = country_risk_premium(0.105, 0.045)
        >>> result.value
        0.06
    """
    return ValuationResult(
        value=sovereign_yield - us_treasury_yield,
        method="Country Risk Premium (Sovereign Spread)",
        inputs={"sovereign_yield": sovereign_yield, "us_treasury_yield": us_treasury_yield},
        chapter="12",
    )


def country_risk_premium_damodaran(
    default_spread: float,
    equity_volatility: float,
    bond_volatility: float,
) -> ValuationResult:
    """Calculate CRP using Damodaran's method.

    Formula: CRP = Default Spread × (σ_equity / σ_bond)
    """
    if bond_volatility <= 0:
        raise ValueError("bond_volatility must be positive")
    return ValuationResult(
        value=default_spread * (equity_volatility / bond_volatility),
        method="Country Risk Premium (Damodaran)",
        inputs={
            "default_spread": default_spread,
            "equity_volatility": equity_volatility,
            "bond_volatility": bond_volatility,
        },
        chapter="12",
    )


def adjusted_capm_international(
    risk_free_rate: float,
    beta: float,
    market_risk_premium: float,
    crp: float,
) -> ValuationResult:
    """Calculate international adjusted CAPM.

    Formula: r = Rf + β × MRP + CRP

    Example:
        >>> result = adjusted_capm_international(0.045, 1.2, 0.06, 0.03)
        >>> round(result.value, 4)
        0.147
    """
    return ValuationResult(
        value=risk_free_rate + beta * market_risk_premium + crp,
        method="Adjusted CAPM (International)",
        inputs={
            "risk_free_rate": risk_free_rate,
            "beta": beta,
            "market_risk_premium": market_risk_premium,
            "crp": crp,
        },
        chapter="12",
    )


def after_tax_cash_flow(
    pre_tax_cf: float,
    local_tax_rate: float,
    withholding_tax_rate: float = 0,
) -> ValuationResult:
    """Calculate after-tax cash flow for international operations.

    Formula: After-Tax CF = Pre-Tax CF × (1 - Local Tax Rate) × (1 - Withholding Tax Rate)
    """
    return ValuationResult(
        value=pre_tax_cf * (1 - local_tax_rate) * (1 - withholding_tax_rate),
        method="After-Tax Cash Flow",
        inputs={
            "pre_tax_cf": pre_tax_cf,
            "local_tax_rate": local_tax_rate,
            "withholding_tax_rate": withholding_tax_rate,
        },
        chapter="12",
    )


def sum_of_parts_valuation(
    market_values: list[float],
    market_probabilities: list[float],
) -> ValuationResult:
    """Calculate sum-of-parts valuation across markets.

    Formula: Total V = Σ V_market_i × P(success in market i)
    """
    if len(market_values) != len(market_probabilities):
        raise ValueError("market_values and market_probabilities must have same length")
    total = sum(v * p for v, p in zip(market_values, market_probabilities))
    return ValuationResult(
        value=total,
        method="Sum-of-Parts Valuation",
        inputs={"market_values": market_values, "market_probabilities": market_probabilities},
        chapter="12",
    )
