# Textbook Chapter Cross-Reference

This index maps every function in the library to its corresponding chapter in the Startup Valuation textbook.

## Chapter 2: Mathematical Foundations

### Probability Theory
| Function | Module | Description |
|----------|--------|-------------|
| `expected_value_discrete` | `probability` | E[X] = Σ xᵢ × P(X=xᵢ) |
| `expected_value_continuous` | `probability` | E[X] = ∫ x × f(x) dx |
| `joint_probability` | `probability` | P(total) = Π Pᵢ |
| `probability_weighted_value` | `probability` | E[V] = Σ pᵢ × Vᵢ |
| `portfolio_expected_return` | `probability` | E[R] = Σ pᵢ × Rᵢ |
| `poisson_probability` | `probability` | P(X=k) = e⁻λ·λᵏ/k! |

### Time Value of Money
| Function | Module | Description |
|----------|--------|-------------|
| `present_value` | `tv` | PV = C/(1+r)ᵗ |
| `net_present_value` | `tv` | NPV = Σ Cₜ/(1+r)ᵗ |
| `annuity_present_value` | `tv` | PV = C×[(1-(1+r)⁻ⁿ)/r] |

### Risk-Adjusted Discount Rates
| Function | Module | Description |
|----------|--------|-------------|
| `capm` | `capm` | E(Rᵢ) = Rf + βᵢ(E(Rm) - Rf) |
| `portfolio_beta` | `capm` | βp = Σ wᵢβᵢ |
| `startup_adjusted_capm` | `capm` | CAPM + size + startup premiums |
| `portfolio_variance` | `capm` | Var(Rp) = ΣΣ wᵢwⱼCov(Rᵢ,Rⱼ) |

## Chapter 3: Core Valuation Models

| Function | Module | Description |
|----------|--------|-------------|
| `scorecard_valuation` | `core` | V = V_avg × Σ(wᵢ × sᵢ) |
| `berkus_valuation` | `core` | V = Σ vᵢ (max $500K per factor) |
| `risk_factor_summation` | `core` | V = V_base + Σ(rᵢ × $250K) |
| `vc_method_post_money` | `core` | Post = Terminal/ROI |
| `vc_method_pre_money` | `core` | Pre = Post - Investment |
| `terminal_value_multiple` | `core` | TV = Revenue × Multiple |

## Chapter 4: Advanced Techniques

| Function | Module | Description |
|----------|--------|-------------|
| `black_scholes` | `advanced` | C = N(d₁)S - N(d₂)Ke⁻ʳᵀ |
| `binomial_tree` | `advanced` | u, d, p factors + tree valuation |
| `binomial_valuation` | `advanced` | High-resolution binomial (steps=50) |
| `monte_carlo_valuation` | `advanced` | Simulation with distributions |
| `scenario_analysis` | `advanced` | E[V] = Σ pᵢ × Vᵢ |
| `ltv_cac_valuation` | `advanced` | (LTV/CAC) × Market Size × 0.1 |

## Chapter 5: Market Comparables

| Function | Module | Description |
|----------|--------|-------------|
| `pe_ratio` | `comparables` | P/E = Market Cap / Net Income |
| `ps_ratio` | `comparables` | P/S = Market Cap / Revenue |
| `ev_ebitda` | `comparables` | EV/EBITDA |
| `ev_revenue` | `comparables` | EV/Revenue |
| `regression_adjusted_multiple` | `comparables` | Multiple = β₀ + β₁g + β₂M + ... |
| `target_valuation_multiple` | `comparables` | Valuation = Multiple × Metric |

## Chapter 11: Industry-Specific Frameworks

### SaaS
| Function | Module | Description |
|----------|--------|-------------|
| `arr` | `saas` | Annual Recurring Revenue |
| `mrr` | `saas` | Monthly Recurring Revenue |
| `cac` | `saas` | Customer Acquisition Cost |
| `ltv_saas` | `saas` | LTV = (ARPU × GM) / Churn |
| `net_revenue_retention` | `saas` | NRR = Revenue_end / Revenue_start |
| `cac_payback_period` | `saas` | CAC / (MRR × GM) |
| `magic_number` | `saas` | Net New ARR / S&M Expense |
| `rule_of_40` | `saas` | Growth + Profit ≥ 40% |
| `saas_revenue_multiple_valuation` | `saas` | ARR × Multiple |

### Biotech
| Function | Module | Description |
|----------|--------|-------------|
| `rnPV` | `biotech` | Risk-adjusted NPV |
| `decision_tree_ev` | `biotech` | EV = Π pᵢ × Terminal Value |
| `peak_sales` | `biotech` | Population × Penetration × Price |
| `pipeline_valuation` | `biotech` | Σ(Peak × Multiple × P_success)/(1+r)ⁿ |
| `overall_success_probability` | `biotech` | P_total = Π P_stage |

### Fintech
| Function | Module | Description |
|----------|--------|-------------|
| `payment_revenue` | `fintech` | Volume × Take Rate |
| `max_loan_portfolio` | `fintech` | Equity / Capital Ratio |
| `network_effects_value` | `fintech` | Value ∝ Users^α |
| `lending_fintech_valuation` | `fintech` | Loan Book × ROE × P/E |
| `payment_processor_valuation` | `fintech` | DCF of payment revenue |
| `neobank_valuation` | `fintech` | Customers × LTV × P/E |

### Marketplace
| Function | Module | Description |
|----------|--------|-------------|
| `gmv` | `marketplace` | Gross Merchandise Value |
| `take_rate` | `marketplace` | Revenue / GMV |
| `liquidity` | `marketplace` | Successful / Total Attempts |
| `gmv_multiple_valuation` | `marketplace` | GMV × Multiple |
| `network_value` | `marketplace` | k × Users^α |
| `buyer_retention` | `marketplace` | Repeat Buyers / Period 1 Buyers |
| `network_density` | `marketplace` | Actual / Potential Connections |

### Hardware
| Function | Module | Description |
|----------|--------|-------------|
| `trl_adjusted_valuation` | `hardware` | Market × Share × Margin × Multiple × (1-TRL) |
| `gross_margin_hardware` | `hardware` | (ASP - COGS) / ASP |
| `break_even_volume` | `hardware` | Fixed Costs / (ASP - Variable Cost) |
| `probability_weighted_dcf` | `hardware` | E[V] = Σ pᵢ × Vᵢ |

## Chapter 12: International Valuation

| Function | Module | Description |
|----------|--------|-------------|
| `purchasing_power_parity` | `international` | Eₜ = E₀ × (1+π_f)/(1+π_d) |
| `interest_rate_parity` | `international` | F = S × (1+r_f)/(1+r_d) |
| `currency_adjusted_dcf` | `international` | PV = Σ[CFₜ^local/Eₜ]/(1+r_USD)^t |
| `country_risk_premium` | `international` | Sovereign Spread |
| `country_risk_premium_damodaran` | `international` | Default Spread × (σ_equity/σ_bond) |
| `adjusted_capm_international` | `international` | r = Rf + β×MRP + CRP |
| `after_tax_cash_flow` | `international` | Pre-Tax × (1-T_local) × (1-T_withhold) |
| `sum_of_parts_valuation` | `international` | Σ V_market × P(success) |

## Chapter 13: Stakeholder Perspectives

| Function | Module | Description |
|----------|--------|-------------|
| `single_round_dilution` | `stakeholders` | Ownership × (1 - Investment/Post) |
| `multi_round_dilution` | `stakeholders` | Π(1 - Investmentᵢ/Postᵢ) |
| `acquisition_value` | `stakeholders` | Standalone + Synergies - Integration |
| `opm_common_stock` | `stakeholders` | Black-Scholes for common stock |
| `pwerm` | `stakeholders` | Σ pᵢ × CommonValueᵢ |
| `common_stock_discount` | `stakeholders` | (Preferred - Common) / Preferred |
| `liquidation_value` | `stakeholders` | Σ(Asset × Recovery Rate) |
| `venture_debt_dilution` | `stakeholders` | Warrant Coverage × Loan / Post |
| `risk_adjusted_synergy` | `stakeholders` | PV of risk-adjusted synergies |
| `intrinsic_option_value` | `stakeholders` | max(FMV - Strike, 0) × Shares |
| `probability_weighted_employee_value` | `stakeholders` | E[V] across exit scenarios |
| `vesting_adjusted_value` | `stakeholders` | Vested + Σ(unvested × vest × retention) |
| `cash_equity_breakeven` | `stakeholders` | Salary tradeoff analysis |
| `max_asset_based_loan` | `stakeholders` | Collateral-based loan calculation |

## Chapter 14: Emerging Topics

| Function | Module | Description |
|----------|--------|-------------|
| `safe_conversion_discount` | `emerging` | Series A × (1 - Discount) |
| `safe_conversion_cap` | `emerging` | SAFE conversion with valuation cap |
| `safe_expected_value` | `emerging` | Expected value across cap/discount |
| `equation_of_exchange` | `emerging` | MV = PQ → Token Value |
| `nvt_ratio` | `emerging` | Market Cap / Daily Volume |
| `protocol_value` | `emerging` | TVL × Multiple |
| `esg_adjusted_discount_rate` | `emerging` | r = base + risk - opportunity |
| `esg_premium_valuation` | `emerging` | Base × (1 + ESG × premium) |
| `esg_discount_valuation` | `emerging` | Base × (1 - risk × discount) |
| `metcalfes_law` | `emerging` | V = k × n² |
| `modified_metcalfes` | `emerging` | V = k × n^α |
| `network_density_valuation` | `emerging` | Users × Connections × Value |
| `remote_cost_savings_npv` | `emerging` | Savings / r (perpetuity) |
| `data_moat_value` | `emerging` | DCF of data advantage |
| `remote_first_premium` | `emerging` | Base × (1 + savings + talent + productivity) |
