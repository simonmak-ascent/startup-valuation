import type { MethodConfig } from "../valuation/types";

export const gmvMultipleConfig: MethodConfig = {
  slug: "gmv-multiple",
  name: "GMV Multiple Valuation",
  category: "Emerging",
  description: "Marketplace valuation = GMV × Market GMV Multiple (typically 0.3–0.5x GMV).",
  textbookChapter: "Chapter 14: Emerging Topics",
  formulaNumber: "Ch. 11",
  methodName: "gmv_multiple",
  inputs: [
    { name: "gmv", label: "GMV ($)", type: "number", defaultValue: 100000000 },
    { name: "multiple", label: "GMV Multiple (x)", type: "number", defaultValue: 0.4, step: 0.05 },
  ],
};

export const networkValueConfig: MethodConfig = {
  slug: "metcalfe",
  name: "Metcalfe's Law (Network Value)",
  category: "Emerging",
  description: "Network value = k × n^α. Theoretical α=2; empirical platforms use α≈1.2–1.5.",
  textbookChapter: "Chapter 14: Emerging Topics",
  formulaNumber: "Ch. 11",
  methodName: "network_value",
  inputs: [
    { name: "active_users", label: "Active Users (n)", type: "number", defaultValue: 1000000 },
    { name: "k", label: "Value per Connection (k)", type: "number", defaultValue: 0.0000001 },
    { name: "alpha", label: "Exponent (α)", type: "number", defaultValue: 1.5, step: 0.1 },
  ],
};
