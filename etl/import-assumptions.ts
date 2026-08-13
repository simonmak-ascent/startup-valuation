import { readFile } from "node:fs/promises";
import { getDb } from "@/lib/db/client";
import { validateProvenance } from "./validate-provenance";

interface AssumptionRow {
  name: string;
  value: number;
  unit?: string;
  valid_from: string;
  valid_until?: string | null;
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
}

/**
 * Import economic / market assumptions (risk-free rate, market risk premium,
 * sector growth, etc.) from a JSON data file. Every row MUST carry full
 * provenance from a recognized source; rows missing provenance are rejected
 * (AC-E5) — no synthetic values are permitted.
 *
 * Data file format (`etl/data/assumptions.json`):
 *   [
 *     {
 *       "name": "Risk-Free Rate (10Y Treasury)",
 *       "value": 0.042,
 *       "unit": "decimal",
 *       "valid_from": "2026-08-01T00:00:00Z",
 *       "source_url": "https://www.federalreserve.gov/releases/h15/",
 *       "source_name": "Federal Reserve H.15",
 *       "source_retrieved_at": "2026-08-12T00:00:00Z",
 *       "source_version": "2026-08-11 release"
 *     }
 *   ]
 */
export async function importAssumptions(
  filePath = "etl/data/assumptions.json",
): Promise<{ imported: number; rejected: number; errors: string[] }> {
  const db = await getDb();
  let imported = 0;
  let rejected = 0;
  const errors: string[] = [];

  let rows: AssumptionRow[];
  try {
    const raw = await readFile(filePath, "utf-8");
    rows = JSON.parse(raw) as AssumptionRow[];
  } catch (e) {
    throw new Error(`Failed to read assumptions data file (${filePath}): ${(e as Error).message}`);
  }

  for (const [idx, row] of rows.entries()) {
    try {
      validateProvenance(row);
      await db.query(
        `CREATE assumption CONTENT {
          name: $name,
          value: $value,
          unit: $unit,
          valid_from: time::from::iso8601($valid_from),
          valid_until: time::from::iso8601($valid_until),
          source_url: $source_url,
          source_name: $source_name,
          source_retrieved_at: $source_retrieved_at,
          source_version: $source_version,
          created_at: time::now()
        }`,
        {
          name: row.name,
          value: row.value,
          unit: row.unit ?? null,
          valid_from: row.valid_from,
          valid_until: row.valid_until ?? null,
          source_url: row.source_url,
          source_name: row.source_name,
          source_retrieved_at: row.source_retrieved_at,
          source_version: row.source_version,
        },
      );
      imported++;
    } catch (e) {
      rejected++;
      errors.push(`row ${idx}: ${(e as Error).message}`);
    }
  }

  return { imported, rejected, errors };
}
