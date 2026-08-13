import { getDb } from "@/lib/db/client";
import { readCsvObjects } from "./csv";
import { validateProvenance } from "../validate-provenance";

/**
 * Damodaran Online source — industry betas, equity risk premia, multiples.
 * Reads `etl/data/damodaran.csv` with columns:
 *   name,value,unit,valid_from,
 *   source_url,source_name,source_retrieved_at,source_version
 */
export async function importDamodaran(filePath = "etl/data/damodaran.csv") {
  const db = await getDb();
  const rows = await readCsvObjects(filePath);

  let imported = 0;
  let rejected = 0;

  for (const row of rows) {
    try {
      validateProvenance(row);
      await db.query(
        `CREATE assumption CONTENT {
          name: $name,
          value: $value,
          unit: $unit,
          valid_from: time::from::iso8601($valid_from),
          source_url: $source_url,
          source_name: $source_name,
          source_retrieved_at: $source_retrieved_at,
          source_version: $source_version,
          created_at: time::now()
        }`,
        {
          name: row.name,
          value: Number(row.value),
          unit: row.unit || null,
          valid_from: row.valid_from || new Date().toISOString(),
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
