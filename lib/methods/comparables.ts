import type { MethodConfig } from "../valuation/types";

export const peRatioConfig: MethodConfig = {
  slug: "pe-ratio",
  name: "P/E Ratio",
  category: "Foundation",
  description: "Price-to-Earnings ratio: Market Capitalization ÷ Net Income.",
  textbookChapter: "Chapter 5: Market Comparables",
  formulaNumber: "5",
  methodName: "pe_ratio",
  inputs: [
    {
      name: "market_cap",
      label: "Market Capitalization ($)",
      type: "number",
      defaultValue: 500000000,
    },
    { name: "net_income", label: "Net Income ($)", type: "number", defaultValue: 25000000 },
  ],
};

export const psRatioConfig: MethodConfig = {
  slug: "ps-ratio",
  name: "P/S Ratio",
  category: "Foundation",
  description: "Price-to-Sales ratio: Market Capitalization ÷ Revenue.",
  textbookChapter: "Chapter 5: Market Comparables",
  formulaNumber: "5",
  methodName: "ps_ratio",
  inputs: [
    {
      name: "market_cap",
      label: "Market Capitalization ($)",
      type: "number",
      defaultValue: 1000000000,
    },
    { name: "revenue", label: "Revenue ($)", type: "number", defaultValue: 100000000 },
  ],
};

export const evEbitdaConfig: MethodConfig = {
  slug: "ev-ebitda",
  name: "EV/EBITDA",
  category: "Foundation",
  description: "Enterprise Value ÷ EBITDA — a capital-structure-neutral multiple.",
  textbookChapter: "Chapter 5: Market Comparables",
  formulaNumber: "5",
  methodName: "ev_ebitda",
  inputs: [
    {
      name: "enterprise_value",
      label: "Enterprise Value ($)",
      type: "number",
      defaultValue: 500000000,
    },
    { name: "ebitda", label: "EBITDA ($)", type: "number", defaultValue: 50000000 },
  ],
};

export const evRevenueConfig: MethodConfig = {
  slug: "ev-revenue",
  name: "EV/Revenue",
  category: "Foundation",
  description: "Enterprise Value ÷ Revenue — for growth-stage companies without profits.",
  textbookChapter: "Chapter 5: Market Comparables",
  formulaNumber: "5",
  methodName: "ev_revenue",
  inputs: [
    {
      name: "enterprise_value",
      label: "Enterprise Value ($)",
      type: "number",
      defaultValue: 500000000,
    },
    { name: "revenue", label: "Revenue ($)", type: "number", defaultValue: 100000000 },
  ],
};
