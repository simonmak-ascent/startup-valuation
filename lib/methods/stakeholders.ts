import type { MethodConfig } from "../valuation/types";

export const dilutionConfig: MethodConfig = {
  slug: "dilution",
  name: "Single-Round Dilution",
  category: "Stakeholder",
  description:
    "Calculate ownership dilution from a funding round: new ownership = investment ÷ post-money.",
  textbookChapter: "Chapter 13: Stakeholder Valuation",
  formulaNumber: "stakeholders.single_round_dilution",
  methodName: "dilution",
  inputs: [
    {
      name: "ownership_before",
      label: "Ownership Before (decimal)",
      type: "number",
      defaultValue: 1,
      step: 0.01,
      min: 0,
      max: 1,
    },
    { name: "investment", label: "Investment ($)", type: "number", defaultValue: 1000000 },
    {
      name: "post_money",
      label: "Post-Money Valuation ($)",
      type: "number",
      defaultValue: 5000000,
    },
  ],
};

export const commonDiscountConfig: MethodConfig = {
  slug: "common-stock-discount",
  name: "Common Stock Discount",
  category: "Stakeholder",
  description:
    "Discount between preferred and common share value (common stock typically 30–80% below preferred).",
  textbookChapter: "Chapter 13: Stakeholder Valuation",
  formulaNumber: "stakeholders.common_stock_discount",
  methodName: "common_discount",
  inputs: [
    { name: "preferred_value", label: "Preferred Value ($)", type: "number", defaultValue: 10 },
    { name: "common_value", label: "Common Value ($)", type: "number", defaultValue: 5 },
  ],
};

export const opmConfig: MethodConfig = {
  slug: "opm",
  name: "OPM Common Stock (Option Pricing Method)",
  category: "Stakeholder",
  description:
    "Option-pricing model for common stock valuation — treats common equity as a call option on enterprise value.",
  textbookChapter: "Chapter 13: Stakeholder Valuation",
  formulaNumber: "stakeholders.opm_common_stock",
  methodName: "opm",
  inputs: [
    {
      name: "enterprise_value",
      label: "Enterprise Value ($)",
      type: "number",
      defaultValue: 30000000,
    },
    {
      name: "liquidation_preference",
      label: "Liquidation Preference ($)",
      type: "number",
      defaultValue: 20000000,
    },
    { name: "time_to_exit", label: "Time to Exit (years)", type: "number", defaultValue: 3 },
    {
      name: "volatility",
      label: "Volatility (decimal)",
      type: "number",
      defaultValue: 0.5,
      step: 0.05,
    },
    {
      name: "risk_free_rate",
      label: "Risk-Free Rate (decimal)",
      type: "number",
      defaultValue: 0.04,
      step: 0.001,
    },
  ],
};

export const ventureDebtConfig: MethodConfig = {
  slug: "venture-debt",
  name: "Venture Debt Dilution",
  category: "Stakeholder",
  description: "Dilution impact of venture debt warrants on equity value.",
  textbookChapter: "Chapter 13: Stakeholder Valuation",
  formulaNumber: "stakeholders.venture_debt_dilution",
  methodName: "venture_debt",
  inputs: [
    {
      name: "warrant_coverage",
      label: "Warrant Coverage (decimal)",
      type: "number",
      defaultValue: 0.08,
      step: 0.01,
    },
    { name: "loan_amount", label: "Loan Amount ($)", type: "number", defaultValue: 2000000 },
    {
      name: "post_money",
      label: "Post-Money Valuation ($)",
      type: "number",
      defaultValue: 20000000,
    },
  ],
};
