import type { MethodConfig } from "../valuation/types";

export const saasLtvConfig: MethodConfig = {
  slug: "saas-ltv",
  name: "SaaS LTV (Lifetime Value)",
  category: "Industry",
  description:
    "Calculate the Lifetime Value of a SaaS customer based on Average Revenue Per User (ARPU), gross margin, and monthly churn rate.",
  textbookChapter: "Chapter 11: SaaS Valuation Metrics",
  formulaNumber: "11.2",
  methodName: "saas_ltv",
  inputs: [
    {
      name: "arpu",
      label: "ARPU — Average Revenue Per User ($/month)",
      type: "number",
      defaultValue: 100,
      description: "Monthly average revenue per user",
    },
    {
      name: "gross_margin",
      label: "Gross Margin (%)",
      type: "number",
      defaultValue: 0.8,
      step: 0.01,
      min: 0,
      max: 1,
      description: "Gross margin as decimal (0.80 = 80%)",
    },
    {
      name: "churn_rate",
      label: "Monthly Churn Rate (%)",
      type: "number",
      defaultValue: 0.05,
      step: 0.001,
      min: 0,
      max: 1,
      description: "Monthly customer churn as decimal (0.05 = 5%)",
    },
  ],
};
