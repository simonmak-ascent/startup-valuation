import type { MethodConfig } from "../valuation/types";

export const berkusConfig: MethodConfig = {
  slug: "berkus",
  name: "Berkus Method",
  category: "Core",
  description:
    "Value a very early-stage (idea to prototype) startup by scoring 5 key risk factors, each worth up to $500K (max $2.5M).",
  textbookChapter: "Chapter 3: Berkus Method",
  formulaNumber: "3.2",
  methodName: "berkus",
  inputs: [
    {
      name: "sound_idea",
      label: "Sound Idea ($)",
      type: "number",
      defaultValue: 500000,
      description: "Max $500K",
    },
    {
      name: "prototype",
      label: "Prototype ($)",
      type: "number",
      defaultValue: 300000,
      description: "Max $500K",
    },
    {
      name: "quality_team",
      label: "Quality Team ($)",
      type: "number",
      defaultValue: 400000,
      description: "Max $500K",
    },
    {
      name: "strategic_relationships",
      label: "Strategic Relationships ($)",
      type: "number",
      defaultValue: 250000,
      description: "Max $500K",
    },
    {
      name: "product_rollout",
      label: "Product Rollout ($)",
      type: "number",
      defaultValue: 200000,
      description: "Max $500K",
    },
  ],
};

export const vcPreMoneyConfig: MethodConfig = {
  slug: "vc-pre-money",
  name: "VC Method — Pre-Money",
  category: "Core",
  description:
    "Determine pre-money valuation by subtracting the investment amount from the post-money valuation.",
  textbookChapter: "Chapter 3: Venture Capital Method",
  formulaNumber: "3.4",
  methodName: "vc_pre_money",
  inputs: [
    {
      name: "post_money",
      label: "Post-Money Valuation ($)",
      type: "number",
      defaultValue: 5000000,
    },
    { name: "investment", label: "Investment ($)", type: "number", defaultValue: 1000000 },
  ],
};

export const terminalValueConfig: MethodConfig = {
  slug: "terminal-value",
  name: "Terminal Value (Exit Multiple)",
  category: "Core",
  description:
    "Estimate terminal value by multiplying projected revenue by an industry exit multiple.",
  textbookChapter: "Chapter 3: Venture Capital Method",
  formulaNumber: "3.4",
  methodName: "terminal_value",
  inputs: [
    {
      name: "projected_revenue",
      label: "Projected Revenue ($)",
      type: "number",
      defaultValue: 10000000,
    },
    { name: "multiple", label: "Exit Multiple (x)", type: "number", defaultValue: 5, step: 0.5 },
  ],
};
