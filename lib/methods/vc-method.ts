import type { MethodConfig } from "../valuation/types";

export const vcMethodConfig: MethodConfig = {
  slug: "vc-method",
  name: "VC Method",
  category: "Core",
  description:
    "Work backward from expected exit value to determine current post-money and pre-money valuation. Uses target return multiple to discount terminal value.",
  textbookChapter: "Chapter 4: Venture Capital Method",
  formulaNumber: "4.1",
  methodName: "valuation_vc_post_money",
  inputs: [
    {
      name: "terminal_value",
      label: "Terminal Value ($)",
      type: "number",
      defaultValue: 50000000,
      description: "Expected exit value at time of liquidity event",
    },
    {
      name: "target_return",
      label: "Target Return Multiple",
      type: "number",
      defaultValue: 10,
      step: 0.5,
      description: "VC target return (e.g., 10x for early stage)",
    },
  ],
};
