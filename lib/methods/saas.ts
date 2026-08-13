import type { MethodConfig } from "../valuation/types";

export const saasCacConfig: MethodConfig = {
  slug: "saas-cac",
  name: "SaaS CAC (Customer Acquisition Cost)",
  category: "Industry",
  description: "Customer Acquisition Cost = Sales & Marketing Expense ÷ New Customers acquired.",
  textbookChapter: "Chapter 11: SaaS Valuation Metrics",
  formulaNumber: "11.2",
  methodName: "saas_cac",
  inputs: [
    {
      name: "sales_marketing_expense",
      label: "Sales & Marketing Expense ($)",
      type: "number",
      defaultValue: 500000,
    },
    { name: "new_customers", label: "New Customers", type: "number", defaultValue: 1000, min: 1 },
  ],
};
export const saasNrrConfig: MethodConfig = {
  slug: "saas-nrr",
  name: "SaaS NRR (Net Revenue Retention)",
  category: "Industry",
  description: "Net Revenue Retention accounts for expansion within the existing customer base.",
  textbookChapter: "Chapter 11: SaaS Valuation Metrics",
  formulaNumber: "11.3",
  methodName: "saas_nrr",
  inputs: [
    {
      name: "starting_revenue",
      label: "Starting Revenue ($)",
      type: "number",
      defaultValue: 1000000,
    },
    { name: "ending_revenue", label: "Ending Revenue ($)", type: "number", defaultValue: 1100000 },
    {
      name: "expansion_revenue",
      label: "Expansion Revenue ($)",
      type: "number",
      defaultValue: 50000,
    },
  ],
};

export const saasMagicNumberConfig: MethodConfig = {
  slug: "saas-magic-number",
  name: "SaaS Magic Number",
  category: "Industry",
  description:
    "Magic Number = Net New ARR ÷ Prior-Quarter Sales & Marketing expense. >0.75 is efficient growth.",
  textbookChapter: "Chapter 11: SaaS Valuation Metrics",
  formulaNumber: "11.4",
  methodName: "saas_magic_number",
  inputs: [
    { name: "net_new_arr", label: "Net New ARR ($)", type: "number", defaultValue: 400000 },
    {
      name: "sm_expense_prior",
      label: "Prior-Quarter S&M Expense ($)",
      type: "number",
      defaultValue: 500000,
    },
  ],
};

export const saasRuleOf40Config: MethodConfig = {
  slug: "saas-rule-of-40",
  name: "SaaS Rule of 40",
  category: "Industry",
  description:
    "Rule of 40 = Revenue Growth Rate + Profit Margin. ≥40% signals healthy balance of growth and profitability.",
  textbookChapter: "Chapter 11: SaaS Valuation Metrics",
  formulaNumber: "11.4",
  methodName: "saas_rule_of_40",
  inputs: [
    {
      name: "growth_rate",
      label: "Revenue Growth Rate (decimal)",
      type: "number",
      defaultValue: 0.35,
      step: 0.01,
    },
    {
      name: "profit_margin",
      label: "Profit Margin (decimal)",
      type: "number",
      defaultValue: 0.1,
      step: 0.01,
    },
  ],
};

export const saasCacPaybackConfig: MethodConfig = {
  slug: "saas-cac-payback",
  name: "SaaS CAC Payback Period",
  category: "Industry",
  description: "Months to recover CAC from a customer's monthly gross profit.",
  textbookChapter: "Chapter 11: SaaS Valuation Metrics",
  formulaNumber: "11.2",
  methodName: "saas_cac_payback",
  inputs: [
    { name: "cac", label: "CAC ($)", type: "number", defaultValue: 1000 },
    {
      name: "mrr_per_customer",
      label: "MRR per Customer ($/month)",
      type: "number",
      defaultValue: 100,
    },
    {
      name: "gross_margin",
      label: "Gross Margin (decimal)",
      type: "number",
      defaultValue: 0.8,
      step: 0.01,
      min: 0,
      max: 1,
    },
  ],
};

export const saasRevenueMultipleConfig: MethodConfig = {
  slug: "saas-revenue-multiple",
  name: "SaaS Revenue Multiple Valuation",
  category: "Industry",
  description: "Valuation = ARR × Market Revenue Multiple (SaaS typically 5–15x ARR).",
  textbookChapter: "Chapter 11: SaaS Valuation Metrics",
  formulaNumber: "11.5",
  methodName: "saas_revenue_multiple",
  inputs: [
    { name: "arr", label: "ARR ($)", type: "number", defaultValue: 5000000 },
    {
      name: "revenue_multiple",
      label: "Revenue Multiple (x)",
      type: "number",
      defaultValue: 8,
      step: 0.5,
    },
  ],
};
