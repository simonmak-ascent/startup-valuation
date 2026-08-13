import type { MethodConfig } from "../valuation/types";

export const poissonConfig: MethodConfig = {
  slug: "poisson",
  name: "Poisson Probability",
  category: "Foundation",
  description:
    "Probability of exactly k events given a mean rate λ (e.g., k acquisitions per year).",
  textbookChapter: "Chapter 2: Valuation Foundations",
  formulaNumber: "2.5",
  methodName: "poisson",
  toParams: (values) => ({ lambda_: values.rate, k: values.k }),
  inputs: [
    { name: "rate", label: "Mean Rate (λ)", type: "number", defaultValue: 2 },
    { name: "k", label: "Event Count (k)", type: "number", defaultValue: 3, min: 0 },
  ],
};
