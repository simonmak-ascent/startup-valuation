export const TABLES = {
  VALUATION_RUN: "valuation_run",
  METHOD: "method",
  ASSUMPTION: "assumption",
  USER: "user",
  AUDIT_LOG: "audit_log",
  DATA_SOURCE: "data_source",
  PUBLIC_COMPANY: "public_company",
  VALUATION_EVENT: "valuation_event",
  FINANCIAL_METRIC: "financial_metric",
  INDUSTRY: "industry",
  BENCHMARK: "benchmark",
  CITATION: "citation",
  ETL_RUN: "etl_run",
  SUBSCRIPTION: "subscription",
  PAYMENT_EVENT: "payment_event",
  LEGAL_DOCUMENT: "legal_document",
  SECRET: "secret",
} as const;

export interface ValuationRun {
  id: string;
  method: string;
  user?: string;
  inputs: Record<string, unknown>;
  result: number;
  steps: Step[];
  formula_number: string;
  chapter: string;
  library_version: string;
  git_commit?: string;
  audit_log?: string;
  created_at: string;
  ip_hash?: string;
}

export interface Step {
  label: string;
  value: number;
  formula: string;
}

export interface Method {
  id: string;
  name: string;
  slug: string;
  module: string;
  function_name: string;
  category: string;
  description: string;
  inputs_schema: Record<string, unknown>;
  textbook_chapter?: string;
  formula_numbers: string[];
  citations: string[];
  assumptions: string[];
  created_at: string;
  updated_at?: string;
}

export interface Assumption {
  id: string;
  name: string;
  value: number;
  unit?: string;
  valid_from: string;
  valid_until?: string;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
  created_at: string;
}

export interface User {
  id: string;
  clerk_id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  tier: string;
  preferences: Record<string, unknown>;
  saved_calculations: string[];
  created_at: string;
  last_active_at?: string;
}

export interface AuditLog {
  id: string;
  valuation_run: string;
  user?: string;
  action: string;
  method: string;
  inputs: Record<string, unknown>;
  result: number;
  steps: Step[];
  formula_number: string;
  chapter: string;
  library_version: string;
  git_commit?: string;
  client_ip_hash?: string;
  user_agent?: string;
  created_at: string;
}

export interface DataSource {
  id: string;
  name: string;
  url: string;
  reputation: "High" | "Medium" | "Low" | "Unknown";
  description: string;
  access_method: string;
  refresh_frequency: string;
  last_validated_at?: string;
  created_at: string;
}

export interface PublicCompany {
  id: string;
  name: string;
  ticker?: string;
  industry: string;
  sector?: string;
  country?: string;
  description?: string;
  employees?: number;
  founded_year?: number;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
  created_at: string;
}

export interface ValuationEvent {
  id: string;
  company: string;
  valuation_amount: number;
  valuation_date: string;
  event_type: string;
  stage?: string;
  method_used?: string;
  currency: string;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
  created_at: string;
}

export interface FinancialMetric {
  id: string;
  company: string;
  metric_name: string;
  metric_value: number;
  unit: string;
  period: string;
  filing_date?: string;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
  created_at: string;
}

export interface Industry {
  id: string;
  name: string;
  parent?: string;
  description?: string;
  created_at: string;
}

export interface Benchmark {
  id: string;
  version: string;
  industry: string;
  stage?: string;
  metric: string;
  value: number;
  p25?: number;
  p75?: number;
  count: number;
  source_records: string[];
  computed_at: string;
  created_at: string;
}

export interface Citation {
  id: string;
  title: string;
  authors: string[];
  year: number;
  type: string;
  doi?: string;
  url?: string;
  bibtex?: string;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
  created_at: string;
}

export interface EtlRun {
  id: string;
  job_name: string;
  status: "running" | "completed" | "failed" | "partial";
  records_imported: number;
  records_rejected: number;
  errors: string[];
  started_at: string;
  completed_at?: string;
  created_at: string;
}

export interface ProvenanceFields {
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
}

export function validateProvenance(record: Partial<ProvenanceFields>): ProvenanceFields {
  const missing: string[] = [];
  if (!record.source_url) missing.push("source_url");
  if (!record.source_name) missing.push("source_name");
  if (!record.source_retrieved_at) missing.push("source_retrieved_at");
  if (!record.source_version) missing.push("source_version");

  if (missing.length > 0) {
    throw new Error(`Missing provenance fields: ${missing.join(", ")}`);
  }

  return record as ProvenanceFields;
}

export interface CalculatorResponse {
  value: number;
  method: string;
  formula_number: string;
  chapter: string;
  steps: Step[];
  inputs: Record<string, unknown>;
  assumptions: Record<string, string>;
  library_version: string;
  timestamp: string;
  git_commit: string;
  audit_id?: string;
  audit_status: "logged" | "failed" | "skipped";
}

export interface Subscription {
  id: string;
  user_id: string;
  stripe_subscription_id: string;
  stripe_customer_id: string;
  tier: "free" | "pro" | "enterprise";
  status: string;
  current_period_end?: string;
  created_at: string;
  updated_at?: string;
}

export interface PaymentEvent {
  id: string;
  stripe_event_id: string;
  type: string;
  payload: string;
  processed_at: string;
}

export interface LegalDocument {
  id: string;
  slug: string;
  version: string;
  title: string;
  body: string;
  content_hash: string;
  published_at: string;
}

export interface Secret {
  id: string;
  service: string;
  key_name: string;
  secret_value: string;
  created_at: string;
}
