import type { MethodConfig } from "../valuation/types";

export const scorecardConfig: MethodConfig = {
  slug: "scorecard",
  name: "Scorecard Method",
  category: "Core",
  description: "Adjust average valuation by weighted factor scores for pre-revenue startups. Uses 7 factors (Team, Product, Market, Competition, Marketing, Funding Need, Other) with standard weights from the textbook.",
  textbookChapter: "Chapter 3: Scorecard Valuation Method",
  formulaNumber: "3.1",
  methodName: "scorecard",
  toParams: (values) => ({
    average_valuation: values.average_valuation,
    weights: [0.3, 0.25, 0.15, 0.1, 0.1, 0.05, 0.05],
    scores: [values.w0, values.w1, values.w2, values.w3, values.w4, values.w5, values.w6],
  }),
  inputs: [
    { name: "average_valuation", label: "Average Regional Valuation ($)", type: "number", defaultValue: 1500000 },
    { name: "w0", label: "Team Score", type: "number", defaultValue: 1.25, step: 0.01, description: "Weight: 0.30" },
    { name: "w1", label: "Product Score", type: "number", defaultValue: 1.5, step: 0.01, description: "Weight: 0.25" },
    { name: "w2", label: "Market Score", type: "number", defaultValue: 1.2, step: 0.01, description: "Weight: 0.15" },
    { name: "w3", label: "Competition Score", type: "number", defaultValue: 0.75, step: 0.01, description: "Weight: 0.10" },
    { name: "w4", label: "Marketing Score", type: "number", defaultValue: 1.0, step: 0.01, description: "Weight: 0.10" },
    { name: "w5", label: "Funding Need Score", type: "number", defaultValue: 0.9, step: 0.01, description: "Weight: 0.05" },
    { name: "w6", label: "Other Score", type: "number", defaultValue: 1.0, step: 0.01, description: "Weight: 0.05" },
  ],
};

export const berkusConfig: MethodConfig = {
  slug: "berkus",
  name: "Berkus Method",
  category: "Core",
  description: "Value a very early-stage (idea to prototype) startup by scoring 5 key risk factors, each worth up to $500K (max $2.5M).",
  textbookChapter: "Chapter 3: Berkus Method",
  formulaNumber: "3.2",
  methodName: "berkus",
  inputs: [
    { name: "sound_idea", label: "Sound Idea ($)", type: "number", defaultValue: 500000, description: "Max $500K" },
    { name: "prototype", label: "Prototype ($)", type: "number", defaultValue: 300000, description: "Max $500K" },
    { name: "quality_team", label: "Quality Team ($)", type: "number", defaultValue: 400000, description: "Max $500K" },
    { name: "strategic_relationships", label: "Strategic Relationships ($)", type: "number", defaultValue: 250000, description: "Max $500K" },
    { name: "product_rollout", label: "Product Rollout ($)", type: "number", defaultValue: 200000, description: "Max $500K" },
  ],
};

export const vcMethodConfig: MethodConfig = {
  slug: "vc-method",
  name: "VC Method",
  category: "Core",
  description: "Work backward from expected exit value to determine current post-money and pre-money valuation. Uses target return multiple to discount terminal value.",
  textbookChapter: "Chapter 3: Venture Capital Method",
  formulaNumber: "3.4",
  methodName: "vc_post_money",
  inputs: [
    { name: "terminal_value", label: "Terminal Value ($)", type: "number", defaultValue: 50000000, description: "Expected exit value at time of liquidity event" },
    { name: "target_return", label: "Target Return Multiple", type: "number", defaultValue: 10, step: 0.5, description: "VC target return (e.g., 10x for early stage)" },
  ],
};

export const vcPreMoneyConfig: MethodConfig = {
  slug: "vc-pre-money",
  name: "VC Method — Pre-Money",
  category: "Core",
  description: "Determine pre-money valuation by subtracting the investment amount from the post-money valuation.",
  textbookChapter: "Chapter 3: Venture Capital Method",
  formulaNumber: "3.4",
  methodName: "vc_pre_money",
  inputs: [
    { name: "post_money", label: "Post-Money Valuation ($)", type: "number", defaultValue: 5000000 },
    { name: "investment", label: "Investment ($)", type: "number", defaultValue: 1000000 },
  ],
};

export const terminalValueConfig: MethodConfig = {
  slug: "terminal-value",
  name: "Terminal Value (Exit Multiple)",
  category: "Core",
  description: "Estimate terminal value by multiplying projected revenue by an industry exit multiple.",
  textbookChapter: "Chapter 3: Venture Capital Method",
  formulaNumber: "3.4",
  methodName: "terminal_value",
  inputs: [
    { name: "projected_revenue", label: "Projected Revenue ($)", type: "number", defaultValue: 10000000 },
    { name: "multiple", label: "Exit Multiple (x)", type: "number", defaultValue: 5, step: 0.5 },
  ],
};
