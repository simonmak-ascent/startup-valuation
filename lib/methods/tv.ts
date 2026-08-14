import type { MethodConfig } from "../valuation/types";

export const presentValueConfig: MethodConfig = {
  slug: "present-value",
  name: "Present Value",
  category: "Foundation",
  description: "PV = FV ÷ (1 + r)^n — discount a future cash flow to today.",
  textbookChapter: "Chapter 2: Valuation Foundations",
  formulaNumber: "2.2",
  methodName: "present_value",
  inputs: [
    { name: "future_value", label: "Future Value ($)", type: "number", defaultValue: 1000000 },
    { name: "rate", label: "Discount Rate (decimal)", type: "number", defaultValue: 0.1, step: 0.01 },
    { name: "periods", label: "Periods (years)", type: "number", defaultValue: 5, min: 0 },
  ],
};

export const annuityConfig: MethodConfig = {
  slug: "annuity",
  name: "Annuity Present Value",
  category: "Foundation",
  description: "PV of a series of equal periodic payments.",
  textbookChapter: "Chapter 2: Valuation Foundations",
  formulaNumber: "2.4",
  methodName: "annuity",
  inputs: [
    { name: "payment", label: "Periodic Payment ($)", type: "number", defaultValue: 100000 },
    { name: "rate", label: "Discount Rate (decimal)", type: "number", defaultValue: 0.08, step: 0.01 },
    { name: "periods", label: "Number of Periods", type: "number", defaultValue: 10, min: 1 },
  ],
};
