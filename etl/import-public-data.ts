import { getDb } from "@/lib/db/client";
import { importCrunchbase, importSecEdgar, importDamodaran, importFred } from "./sources";

/**
 * Public data ETL orchestrator. Each source module reads a local CSV data file,
 * enforces provenance, and upserts into SurrealDB. Missing data files are
 * skipped gracefully — no synthetic data is created.
 *
 * Usage: `pnpm etl:import`
 */
export async function importPublicData(): Promise<void> {
  const db = await getDb();
  const startedAt = new Date().toISOString();

  const allErrors: string[] = [];
  let imported = 0;
  let rejected = 0;
  let status: "completed" | "failed" | "partial" = "completed";

  const step = (label: string, r: { imported: number; rejected: number }) => {
    imported += r.imported;
    rejected += r.rejected;
    if (r.rejected > 0) status = "partial";
    console.log(`  ${label}: ${r.imported} imported, ${r.rejected} rejected`);
  };

  const sources: [string, () => Promise<{ imported: number; rejected: number }>][] = [
    ["crunchbase", importCrunchbase],
    ["sec-edgar", importSecEdgar],
    ["damodaran", importDamodaran],
    ["fred", importFred],
  ];

  console.log(`Public data ETL started at ${startedAt}`);

  for (const [name, fn] of sources) {
    try {
      step(name, await fn());
    } catch (e) {
      console.log(`  ${name}: skipped (${(e as Error).message})`);
    }
  }

  await db.query(
    `CREATE etl_run CONTENT {
      job_name: $job_name,
      status: $status,
      records_imported: $imported,
      records_rejected: $rejected,
      errors: $errors,
      started_at: $started_at,
      completed_at: time::now(),
      created_at: time::now()
    }`,
    {
      job_name: "import-public-data",
      status,
      imported,
      rejected,
      errors: allErrors,
      started_at: startedAt,
    },
  );

  console.log(`Public data ETL complete: ${imported} imported, ${rejected} rejected (${status})`);
}
