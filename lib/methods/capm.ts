import type { MethodConfig } from "../valuation/types";

export const capmConfig: MethodConfig = {
  slug: "capm",
  name: "CAPM (Capital Asset Pricing Model)",
  category: "Foundation",
  description: "Cost of equity: E(R) = Rf + β × (Market Return − Rf). Returns a decimal rate.",
  textbookChapter: "Chapter 2: Valuation Foundations",
  formulaNumber: "2.5",
  methodName: "capm",
  inputs: [
    {
      name: "risk_free_rate",
      label: "Risk-Free Rate (decimal)",
      type: "number",
      defaultValue: 0.04,
      step: 0.001,
    },
    { name: "beta", label: "Beta (β)", type: "number", defaultValue: 1.5, step: 0.1 },
    {
      name: "market_return",
      label: "Market Return (decimal)",
      type: "number",
      defaultValue: 0.055,
      step: 0.001,
    },
  ],
};

export const startupCapmConfig: MethodConfig = {
  slug: "startup-capm",
  name: "Startup-Adjusted CAPM",
  category: "Foundation",
  description:
    "Adds size premium and illiquidity premium to the base CAPM for early-stage companies.",
  textbookChapter: "Chapter 2: Valuation Foundations",
  formulaNumber: "2.7",
  methodName: "startup_capm",
  inputs: [
    {
      name: "risk_free_rate",
      label: "Risk-Free Rate (decimal)",
      type: "number",
      defaultValue: 0.04,
      step: 0.001,
    },
    { name: "beta", label: "Beta (β)", type: "number", defaultValue: 1.5, step: 0.1 },
    {
      name: "market_risk_premium",
      label: "Market Risk Premium (decimal)",
      type: "number",
      defaultValue: 0.055,
      step: 0.001,
    },
    {
      name: "size_premium",
      label: "Size Premium (decimal)",
      type: "number",
      defaultValue: 0.04,
      step: 0.001,
    },
    {
      name: "illiquidity_premium",
      label: "Illiquidity Premium (decimal)",
      type: "number",
      defaultValue: 0.05,
      step: 0.001,
    },
  ],
};
