import { z } from "zod";

export const StepSchema = z.object({
  label: z.string().min(1),
  value: z.number(),
  formula: z.string(),
});

export const ProvenanceSchema = z.object({
  source_url: z.string().url(),
  source_name: z.string().min(1),
  source_retrieved_at: z.string().datetime(),
  source_version: z.string().min(1),
});

export const ValuationRunSchema = z.object({
  id: z.string(),
  method: z.string(),
  user: z.string().optional(),
  inputs: z.record(z.unknown()),
  result: z.number(),
  steps: z.array(StepSchema),
  formula_number: z.string(),
  chapter: z.string(),
  library_version: z.string(),
  git_commit: z.string().optional(),
  audit_log: z.string().optional(),
  created_at: z.string().datetime(),
  ip_hash: z.string().optional(),
});

export const MethodSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  slug: z.string().min(1),
  module: z.string().min(1),
  function: z.string().min(1),
  category: z.string(),
  description: z.string(),
  inputs_schema: z.record(z.unknown()),
  textbook_chapter: z.string().optional(),
  formula_numbers: z.array(z.string()),
  citations: z.array(z.string()),
  assumptions: z.array(z.string()),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime().optional(),
});

export const AssumptionSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  value: z.number(),
  unit: z.string().optional(),
  valid_from: z.string().datetime(),
  valid_until: z.string().datetime().optional(),
  ...ProvenanceSchema.shape,
  created_at: z.string().datetime(),
});

export const UserSchema = z.object({
  id: z.string(),
  clerk_id: z.string().min(1),
  email: z.string().email(),
  name: z.string().optional(),
  avatar_url: z.string().url().optional(),
  tier: z.enum(["free", "pro", "auditor", "enterprise"]).default("free"),
  preferences: z.record(z.unknown()).default({}),
  saved_calculations: z.array(z.string()),
  created_at: z.string().datetime(),
  last_active_at: z.string().datetime().optional(),
});

export const AuditLogSchema = z.object({
  id: z.string(),
  valuation_run: z.string(),
  user: z.string().optional(),
  action: z.string(),
  method: z.string(),
  inputs: z.record(z.unknown()),
  result: z.number(),
  steps: z.array(StepSchema),
  formula_number: z.string(),
  chapter: z.string(),
  library_version: z.string(),
  git_commit: z.string().optional(),
  client_ip_hash: z.string().optional(),
  user_agent: z.string().optional(),
  created_at: z.string().datetime(),
});

export const DataSourceSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  url: z.string().url(),
  reputation: z.enum(["High", "Medium", "Low", "Unknown"]).default("Unknown"),
  description: z.string(),
  access_method: z.string(),
  refresh_frequency: z.string(),
  last_validated_at: z.string().datetime().optional(),
  created_at: z.string().datetime(),
});

export const IndustrySchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  parent: z.string().optional(),
  description: z.string().optional(),
  created_at: z.string().datetime(),
});

export const PublicCompanySchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  ticker: z.string().optional(),
  industry: z.string(),
  sector: z.string().optional(),
  country: z.string().optional(),
  description: z.string().optional(),
  employees: z.number().int().positive().optional(),
  founded_year: z.number().int().optional(),
  ...ProvenanceSchema.shape,
  created_at: z.string().datetime(),
});

export const ValuationEventSchema = z.object({
  id: z.string(),
  company: z.string(),
  valuation_amount: z.number().positive(),
  valuation_date: z.string().datetime(),
  event_type: z.enum([
    "funding_round",
    "acquisition",
    "ipo",
    "409a",
    "market_cap",
    "secondary",
    "other",
  ]),
  stage: z.string().optional(),
  method_used: z.string().optional(),
  currency: z.string().default("USD"),
  ...ProvenanceSchema.shape,
  created_at: z.string().datetime(),
});

export const FinancialMetricSchema = z.object({
  id: z.string(),
  company: z.string(),
  metric_name: z.string().min(1),
  metric_value: z.number(),
  unit: z.string(),
  period: z.string().min(1),
  filing_date: z.string().datetime().optional(),
  ...ProvenanceSchema.shape,
  created_at: z.string().datetime(),
});

export const BenchmarkSchema = z.object({
  id: z.string(),
  version: z.string().min(1),
  industry: z.string(),
  stage: z.string().optional(),
  metric: z.string().min(1),
  value: z.number(),
  p25: z.number().optional(),
  p75: z.number().optional(),
  count: z.number().int().nonnegative(),
  source_records: z.array(z.string()),
  computed_at: z.string().datetime(),
  created_at: z.string().datetime(),
});

export const CitationSchema = z.object({
  id: z.string(),
  title: z.string().min(1),
  authors: z.array(z.string()),
  year: z.number().int(),
  type: z.enum(["textbook", "journal_article", "working_paper", "industry_report", "other"]),
  doi: z.string().optional(),
  url: z.string().url().optional(),
  bibtex: z.string().optional(),
  ...ProvenanceSchema.shape,
  created_at: z.string().datetime(),
});

export const EtlRunSchema = z.object({
  id: z.string(),
  job_name: z.string().min(1),
  status: z.enum(["running", "completed", "failed", "partial"]),
  records_imported: z.number().int().nonnegative().default(0),
  records_rejected: z.number().int().nonnegative().default(0),
  errors: z.array(z.string()),
  started_at: z.string().datetime(),
  completed_at: z.string().datetime().optional(),
  created_at: z.string().datetime(),
});

export const CalculatorRequestSchema = z.object({
  method: z.string().min(1),
  params: z.record(z.unknown()),
});

export const CalculatorResponseSchema = z.object({
  value: z.number(),
  method: z.string(),
  formula_number: z.string(),
  chapter: z.string(),
  steps: z.array(StepSchema),
  inputs: z.record(z.unknown()),
  assumptions: z.record(z.unknown()),
  library_version: z.string(),
  timestamp: z.string(),
  git_commit: z.string(),
  audit_id: z.string().optional(),
  audit_status: z.enum(["logged", "failed", "skipped"]),
});

export const AuditRequestSchema = z.object({
  method: z.string().min(1),
  inputs: z.record(z.unknown()).default({}),
  result: z.number(),
  steps: z.array(StepSchema).default([]),
  formula_number: z.string().default(""),
  chapter: z.string().default(""),
  library_version: z.string().default(""),
  git_commit: z.string().default(""),
});

export type Step = z.infer<typeof StepSchema>;
export type ProvenanceFields = z.infer<typeof ProvenanceSchema>;
export type CalculatorRequest = z.infer<typeof CalculatorRequestSchema>;
export type AuditRequest = z.infer<typeof AuditRequestSchema>;
