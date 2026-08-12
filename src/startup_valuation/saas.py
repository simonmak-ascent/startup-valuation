"""SaaS-specific valuation metrics and methods.

Chapter 11: Industry-Specific Valuation Frameworks — SaaS
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def arr(subscription_values: list[float]) -> ValuationResult:
    """Calculate Annual Recurring Revenue.

    Formula: ARR = Σ Annual Subscription Valueᵢ

    Notes:
        $$ARR = \\sum \\text{Subscription Value}_i$$

        Foundation of all SaaS metrics. Normalizes revenue to annual
        terms independent of billing cycle.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.1.

    See Also:
        mrr : Monthly equivalent (ARR / 12).
    """
    return ValuationResult(
        value=sum(subscription_values),
        method="ARR",
        inputs={"subscription_count": len(subscription_values)},
        chapter="11",
        formula_number="11.1",
    )


def mrr(arr_value: float) -> ValuationResult:
    """Calculate Monthly Recurring Revenue.

    Formula: MRR = ARR / 12

    Notes:
        $$MRR = ARR / 12$$

        Standard SaaS revenue reporting unit. Used in CAC payback,
        Magic Number, and other KPIs.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.1.

    See Also:
        arr : Annual equivalent. cac_payback_period : Uses MRR.
    """
    return ValuationResult(
        value=arr_value / 12,
        method="MRR",
        inputs={"arr": arr_value},
        chapter="11",
        formula_number="11.1",
    )


def cac(sales_marketing_expense: float, new_customers: int) -> ValuationResult:
    """Calculate Customer Acquisition Cost.

    Formula: CAC = Sales & Marketing Expenses / New Customers

    Notes:
        $$CAC = \\frac{\\text{Sales \\& Marketing}}{\\text{New Customers}}$$

        Lower CAC relative to LTV indicates sustainable unit economics.
        Industry benchmark: LTV/CAC > 3.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.2.

    See Also:
        ltv_saas : Lifetime value for LTV/CAC ratio.
    """
    if new_customers <= 0:
        raise ValueError("new_customers must be positive")
    return ValuationResult(
        value=sales_marketing_expense / new_customers,
        method="CAC",
        inputs={"sales_marketing_expense": sales_marketing_expense, "new_customers": new_customers},
        chapter="11",
        formula_number="11.2",
    )


def ltv_saas(arpu: float, gross_margin: float, churn_rate: float) -> ValuationResult:
    """Calculate SaaS Lifetime Value.

    Formula: LTV = (ARPU × Gross Margin) / Churn Rate

    Notes:
        $$LTV = \\frac{ARPU \\times \\text{Gross Margin}}{\\text{Churn Rate}}$$

        ARPU = Average Revenue Per User. Accounts for COGS via gross margin.
        Industry benchmark: LTV/CAC > 3.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.2.

    See Also:
        cac : For LTV/CAC ratio. net_revenue_retention : Expansion metric.

    Example:
        >>> result = ltv_saas(100, 0.80, 0.05)
        >>> result.value
        1600.0
    """
    if churn_rate <= 0:
        raise ValueError("churn_rate must be positive")
    ltv = (arpu * gross_margin) / churn_rate
    return ValuationResult(
        value=ltv,
        method="SaaS LTV",
        inputs={"arpu": arpu, "gross_margin": gross_margin, "churn_rate": churn_rate},
        assumptions=["Churn rate is constant", "Gross margin is stable"],
        chapter="11",
        formula_number="11.2",
    )


def net_revenue_retention(
    starting_revenue: float,
    ending_revenue: float,
    expansion_revenue: float = 0,
) -> ValuationResult:
    """Calculate Net Revenue Retention.

    Formula: NRR = (Ending Revenue + Expansion Revenue) / Starting Revenue

    Notes:
        $$NRR = \\frac{\\text{Ending Revenue} + \\text{Expansion Revenue}}{\\text{Starting Revenue}}$$

        NRR > 100% means existing customers grow net revenue.
        Best-in-class SaaS: NRR > 120%.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.3.

    See Also:
        ltv_saas : Retention drives lifetime value.
    """
    if starting_revenue <= 0:
        raise ValueError("starting_revenue must be positive")
    nrr = (ending_revenue + expansion_revenue) / starting_revenue
    return ValuationResult(
        value=nrr,
        method="Net Revenue Retention",
        inputs={"starting_revenue": starting_revenue, "ending_revenue": ending_revenue},
        assumptions=["Cohort is consistent over the period"],
        chapter="11",
        formula_number="11.3",
    )


def cac_payback_period(cac: float, mrr_per_customer: float, gross_margin: float) -> ValuationResult:
    """Calculate CAC Payback Period.

    Formula: CAC Payback = CAC / (MRR per Customer × Gross Margin)

    Notes:
        $$\\text{CAC Payback} = \\frac{CAC}{MRR \\times \\text{Gross Margin}}$$

        Months to recover customer acquisition cost. Target: <12 months.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.2.

    See Also:
        cac : Acquisition cost. mrr : Monthly revenue.
    """
    denominator = mrr_per_customer * gross_margin
    if denominator <= 0:
        raise ValueError("MRR × gross margin must be positive")
    return ValuationResult(
        value=cac / denominator,
        method="CAC Payback Period",
        inputs={"cac": cac, "mrr_per_customer": mrr_per_customer, "gross_margin": gross_margin},
        assumptions=["MRR per customer is stable"],
        chapter="11",
        formula_number="11.2",
    )


def magic_number(net_new_arr: float, sm_expense_prior: float) -> ValuationResult:
    """Calculate SaaS Magic Number.

    Formula: Magic Number = Net New ARR_quarter / S&M Expense_prior_quarter

    Notes:
        $$\\text{Magic Number} = \\frac{\\text{Net New ARR}}{\\text{S\\&M Expense (prior quarter)}}$$

        SaaS efficiency metric: ARR growth per dollar of S&M spend.
        >1.0 efficient, 0.75-1.0 good, <0.5 needs improvement.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.4.

    See Also:
        rule_of_40 : Combined growth + efficiency metric.
    """
    if sm_expense_prior <= 0:
        raise ValueError("S&M expense must be positive")
    return ValuationResult(
        value=net_new_arr / sm_expense_prior,
        method="Magic Number",
        inputs={"net_new_arr": net_new_arr, "sm_expense_prior": sm_expense_prior},
        assumptions=["Quarterly data is normalized"],
        chapter="11",
        formula_number="11.4",
    )


def rule_of_40(growth_rate: float, profit_margin: float) -> ValuationResult:
    """Calculate Rule of 40 metric.

    Formula: Growth Rate + Profit Margin ≥ 40%

    Notes:
        $$\\text{Rule of 40} = \\text{Growth Rate}\\% + \\text{Profit Margin}\\%$$

        SaaS health check: combined growth and profitability should
        exceed 40%. Balances growth investment with profitability.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.4.

    See Also:
        magic_number : SaaS efficiency metric.

    Example:
        >>> result = rule_of_40(1.18, 0.01)
        >>> round(result.value, 2)
        1.19
    """
    score = growth_rate + profit_margin
    return ValuationResult(
        value=score,
        method="Rule of 40",
        inputs={"growth_rate": growth_rate, "profit_margin": profit_margin},
        assumptions=["Growth rate and profit margin are annualized"],
        chapter="11",
        formula_number="11.4",
    )


def saas_revenue_multiple_valuation(
    arr: float,
    multiple: float,
) -> ValuationResult:
    """Value a SaaS company using ARR multiple.

    Formula: Valuation = ARR × Multiple

    Notes:
        $$V = ARR \\times \\text{Revenue Multiple}$$

        Multiples vary by growth rate: 5-10x for 20-30% growth,
        10-20x for 50%+ growth. Public SaaS median: ~8x ARR.

    References:
        Startup Valuation textbook, Chapter 11, Section 11.5.

    See Also:
        arr : Revenue base. comparables : Alternative multiples.

    Example:
        >>> result = saas_revenue_multiple_valuation(400_000_000, 23)
        >>> result.value
        9200000000.0
    """
    return ValuationResult(
        value=arr * multiple,
        method="SaaS Revenue Multiple Valuation",
        inputs={"arr": arr, "multiple": multiple},
        assumptions=["Multiple is from comparable SaaS companies"],
        chapter="11",
        formula_number="11.5",
    )
