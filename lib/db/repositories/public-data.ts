import { getDb } from "../client";
import { TABLES } from "../schema";

export interface CompanyRow {
  id: string;
  name: string;
  ticker?: string;
  industry: string;
  sector?: string;
  country?: string;
  description?: string;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
}

export interface ValuationEventRow {
  id: string;
  company: string;
  valuation_amount: number;
  valuation_date: string;
  event_type: string;
  stage?: string;
  currency: string;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
}

export interface BenchmarkRow {
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
}

export async function getCompanies(
  filters: { industry?: string; country?: string; search?: string } = {},
  limit = 50,
): Promise<CompanyRow[]> {
  const db = await getDb();
  const clauses: string[] = [];
  const bindings: Record<string, unknown> = { limit };

  if (filters.industry) {
    clauses.push("industry = $industry");
    bindings.industry = filters.industry;
  }
  if (filters.country) {
    clauses.push("country = $country");
    bindings.country = filters.country;
  }
  if (filters.search) {
    clauses.push("string::lowercase(name) CONTAINS $search");
    bindings.search = filters.search.toLowerCase();
  }

  const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
  const [rows] = await db.query<[CompanyRow[]]>(
    `SELECT * FROM ${TABLES.PUBLIC_COMPANY} ${where} ORDER BY name LIMIT $limit`,
    bindings,
  );
  return rows;
}

export async function getValuationEventsForCompany(
  companyId: string,
): Promise<ValuationEventRow[]> {
  const db = await getDb();
  const [rows] = await db.query<[ValuationEventRow[]]>(
    `SELECT * FROM ${TABLES.VALUATION_EVENT} WHERE company = $company ORDER BY valuation_date DESC`,
    { company: companyId },
  );
  return rows;
}

export async function getIndustries(): Promise<{ id: string; name: string }[]> {
  const db = await getDb();
  const [rows] = await db.query<[{ id: string; name: string }[]]>(
    `SELECT * FROM ${TABLES.INDUSTRY} ORDER BY name`,
  );
  return rows;
}

export async function getBenchmarks(version: string, industry?: string): Promise<BenchmarkRow[]> {
  const db = await getDb();
  const [rows] = await db.query<[BenchmarkRow[]]>(
    `SELECT * FROM ${TABLES.BENCHMARK} WHERE version = $version ${
      industry ? "AND industry = $industry" : ""
    } ORDER BY metric, stage`,
    industry ? { version, industry } : { version },
  );
  return rows;
}
