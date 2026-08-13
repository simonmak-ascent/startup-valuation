import type { MethodConfig } from "../valuation/types";

const WEIGHTS = [0.3, 0.25, 0.15, 0.1, 0.1, 0.05, 0.05];

export const scorecardConfig: MethodConfig = {
  slug: "scorecard",
  name: "Scorecard Method",
  category: "Core",
  description:
    "Adjust average valuation by weighted factor scores for pre-revenue startups. Uses 7 factors (Team, Product, Market, Competition, Marketing, Funding Need, Other) with standard weights from the textbook.",
  textbookChapter: "Chapter 3: Scorecard Valuation Method",
  formulaNumber: "3.1",
  methodName: "scorecard",
  toParams: (values) => ({
    average_valuation: values.average_valuation,
    weights: WEIGHTS,
    scores: [values.w0, values.w1, values.w2, values.w3, values.w4, values.w5, values.w6],
  }),
  inputs: [
    {
      name: "average_valuation",
      label: "Average Regional Valuation ($)",
      type: "number",
      defaultValue: 1500000,
    },
    {
      name: "w0",
      label: "Team Score",
      type: "number",
      defaultValue: 1.25,
      step: 0.01,
      description: "Weight: 0.30",
    },
    {
      name: "w1",
      label: "Product Score",
      type: "number",
      defaultValue: 1.5,
      step: 0.01,
      description: "Weight: 0.25",
    },
    {
      name: "w2",
      label: "Market Score",
      type: "number",
      defaultValue: 1.2,
      step: 0.01,
      description: "Weight: 0.15",
    },
    {
      name: "w3",
      label: "Competition Score",
      type: "number",
      defaultValue: 0.75,
      step: 0.01,
      description: "Weight: 0.10",
    },
    {
      name: "w4",
      label: "Marketing Score",
      type: "number",
      defaultValue: 1.0,
      step: 0.01,
      description: "Weight: 0.10",
    },
    {
      name: "w5",
      label: "Funding Need Score",
      type: "number",
      defaultValue: 0.9,
      step: 0.01,
      description: "Weight: 0.05",
    },
    {
      name: "w6",
      label: "Other Score",
      type: "number",
      defaultValue: 1.0,
      step: 0.01,
      description: "Weight: 0.05",
    },
  ],
};
