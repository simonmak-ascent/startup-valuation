import { getDb } from "@/lib/db/client";
import { readCsvObjects } from "./csv";
import { validateProvenance } from "../validate-provenance";

/**
 * SEC EDGAR source — public company profiles + financial metrics from 10-K/10-Q.
 * Reads `etl/data/sec-edgar.csv` with columns:
 *   name,ticker,sector,country,employees,founded_year,description,
 *   metric_name,metric_value,unit,period,filing_date,
 *   source_url,source_name,source_retrieved_at,source_version
 */
export async function importSecEdgar(filePath = "etl/data/sec-edgar.csv") {
  const db = await getDb();
  const rows = await readCsvObjects(filePath);

  let imported = 0;
  let rejected = 0;

  for (const row of rows) {
    try {
      validateProvenance(row);
      const ticker = row.ticker?.toUpperCase();

      await db.query(
        `UPSERT type::record("public_company", $id) MERGE {
          name: $name,
          ticker: $ticker,
          sector: $sector,
          country: $country,
          employees: $employees,
          founded_year: $founded_year,
          description: $description,
          source_url: $source_url,
          source_name: $source_name,
          source_retrieved_at: $source_retrieved_at,
          source_version: $source_version
        }`,
        {
          id: ticker,
          name: row.name,
          ticker: ticker ?? null,
          sector: row.sector || null,
          country: row.country || null,
          employees: row.employees ? Number(row.employees) : null,
          founded_year: row.founded_year ? Number(row.founded_year) : null,
          description: row.description || null,
          source_url: row.source_url,
          source_name: row.source_name,
          source_retrieved_at: row.source_retrieved_at,
          source_version: row.source_version,
        },
      );

      if (row.metric_name && row.metric_value) {
        await db.query(
          `CREATE financial_metric CONTENT {
            company: $company,
            metric_name: $metric_name,
            metric_value: $metric_value,
            unit: $unit,
            period: $period,
            filing_date: time::from::iso8601($filing_date),
            source_url: $source_url,
            source_name: $source_name,
            source_retrieved_at: $source_retrieved_at,
            source_version: $source_version,
            created_at: time::now()
          }`,
          {
            company: `public_company:${ticker}`,
            metric_name: row.metric_name,
            metric_value: Number(row.metric_value),
            unit: row.unit || "USD",
            period: row.period || "FY",
            filing_date: row.filing_date || null,
            source_url: row.source_url,
            source_name: row.source_name,
            source_retrieved_at: row.source_retrieved_at,
            source_version: row.source_version,
          },
        );
      }
      imported++;
    } catch {
      rejected++;
    }
  }

  return { imported, rejected };
}
