"""SaaS-specific valuation metrics and methods.

Chapter 11: Industry-Specific Valuation Frameworks — SaaS
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def arr(subscription_values: list[float]) -> ValuationResult:
    """Calculate Annual Recurring Revenue.

    Formula: ARR = Σ Annual Subscription Valueᵢ
    """
    return ValuationResult(
        value=sum(subscription_values),
        method="ARR",
        inputs={"subscription_count": len(subscription_values)},
        chapter="11",
    )


def mrr(arr_value: float) -> ValuationResult:
    """Calculate Monthly Recurring Revenue.

    Formula: MRR = ARR / 12
    """
    return ValuationResult(
        value=arr_value / 12,
        method="MRR",
        inputs={"arr": arr_value},
        chapter="11",
    )


def cac(sales_marketing_expense: float, new_customers: int) -> ValuationResult:
    """Calculate Customer Acquisition Cost.

    Formula: CAC = Sales & Marketing Expenses / New Customers
    """
    if new_customers <= 0:
        raise ValueError("new_customers must be positive")
    return ValuationResult(
        value=sales_marketing_expense / new_customers,
        method="CAC",
        inputs={"sales_marketing_expense": sales_marketing_expense, "new_customers": new_customers},
        chapter="11",
    )


def ltv_saas(arpu: float, gross_margin: float, churn_rate: float) -> ValuationResult:
    """Calculate SaaS Lifetime Value.

    Formula: LTV = (ARPU × Gross Margin) / Churn Rate

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
    )


def net_revenue_retention(
    starting_revenue: float,
    ending_revenue: float,
    expansion_revenue: float = 0,
) -> ValuationResult:
    """Calculate Net Revenue Retention.

    Formula: NRR = (Ending Revenue + Expansion Revenue) / Starting Revenue
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
    )


def cac_payback_period(cac: float, mrr_per_customer: float, gross_margin: float) -> ValuationResult:
    """Calculate CAC Payback Period.

    Formula: CAC Payback = CAC / (MRR per Customer × Gross Margin)
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
    )


def magic_number(net_new_arr: float, sm_expense_prior: float) -> ValuationResult:
    """Calculate SaaS Magic Number.

    Formula: Magic Number = Net New ARR_quarter / S&M Expense_prior_quarter
    """
    if sm_expense_prior <= 0:
        raise ValueError("S&M expense must be positive")
    return ValuationResult(
        value=net_new_arr / sm_expense_prior,
        method="Magic Number",
        inputs={"net_new_arr": net_new_arr, "sm_expense_prior": sm_expense_prior},
        assumptions=["Quarterly data is normalized"],
        chapter="11",
    )


def rule_of_40(growth_rate: float, profit_margin: float) -> ValuationResult:
    """Calculate Rule of 40 metric.

    Formula: Growth Rate + Profit Margin ≥ 40%

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
    )


def saas_revenue_multiple_valuation(
    arr: float,
    multiple: float,
) -> ValuationResult:
    """Value a SaaS company using ARR multiple.

    Formula: Valuation = ARR × Multiple

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
    )
