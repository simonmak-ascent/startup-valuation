import type { z } from "zod";

export interface MethodConfig {
  slug: string;
  name: string;
  category: string;
  description: string;
  textbookChapter: string;
  formulaNumber: string;
  methodName: string;
  inputs: InputField[];
}

export interface InputField {
  name: string;
  label: string;
  type: "number";
  defaultValue: number;
  step?: number;
  min?: number;
  max?: number;
  description?: string;
}

export interface CalculatorResult {
  value: number;
  method: string;
  formulaNumber: string;
  chapter: string;
  steps: CalculationStep[];
  inputs: Record<string, unknown>;
  assumptions: Record<string, string>;
  libraryVersion: string;
  timestamp: string;
  gitCommit: string;
  auditId?: string;
  auditStatus: "logged" | "failed" | "skipped";
}

export interface CalculationStep {
  label: string;
  value: number;
  formula: string;
}
