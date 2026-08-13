import { getDb } from "@/lib/db/client";
import { readCsvObjects } from "./csv";
import { validateProvenance } from "../validate-provenance";

/**
 * Crunchbase source — startup funding rounds / valuation events.
 * Reads `etl/data/crunchbase.csv` with columns:
 *   company_name,industry,valuation_amount,valuation_date,event_type,stage,currency,
 *   source_url,source_name,source_retrieved_at,source_version
 */
export async function importCrunchbase(filePath = "etl/data/crunchbase.csv") {
  const db = await getDb();
  const rows = await readCsvObjects(filePath);

  let imported = 0;
  let rejected = 0;

  for (const row of rows) {
    try {
      validateProvenance(row);
      const slug = (row.company_name ?? "").toLowerCase().replace(/[^a-z0-9]+/g, "-");

      await db.query(
        `UPSERT type::thing("public_company", $id) MERGE {
          name: $name,
          source_url: $source_url,
          source_name: $source_name,
          source_retrieved_at: $source_retrieved_at,
          source_version: $source_version
        }`,
        {
          id: slug,
          name: row.company_name,
          source_url: row.source_url,
          source_name: row.source_name,
          source_retrieved_at: row.source_retrieved_at,
          source_version: row.source_version,
        },
      );

      await db.query(
        `CREATE valuation_event CONTENT {
          company: $company,
          valuation_amount: $amount,
          valuation_date: $date,
          event_type: $event_type,
          stage: $stage,
          currency: $currency,
          source_url: $source_url,
          source_name: $source_name,
          source_retrieved_at: $source_retrieved_at,
          source_version: $source_version,
          created_at: time::now()
        }`,
        {
          company: `public_company:${slug}`,
          amount: Number(row.valuation_amount),
          date: row.valuation_date,
          event_type: row.event_type || "funding_round",
          stage: row.stage || null,
          currency: row.currency || "USD",
          source_url: row.source_url,
          source_name: row.source_name,
          source_retrieved_at: row.source_retrieved_at,
          source_version: row.source_version,
        },
      );
      imported++;
    } catch {
      rejected++;
    }
  }

  return { imported, rejected };
}
