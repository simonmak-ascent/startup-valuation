import { getDb } from "@/lib/db/client";
import { importMethods, seedDataSources } from "./import-textbook";
import { importCitations } from "./import-citations";
import { importAssumptions } from "./import-assumptions";

/**
 * ETL orchestrator. Runs each importer, aggregates results, and writes an
 * `etl_run` record (idempotent imports + provenance rejection accounting).
 *
 * Usage: `pnpm etl:import`
 */
export async function importAll(): Promise<void> {
  const db = await getDb();
  const jobName = "import-all";
  const startedAt = new Date().toISOString();

  const allErrors: string[] = [];
  let totalImported = 0;
  let totalRejected = 0;
  let status: "completed" | "failed" | "partial" = "completed";

  const step = (label: string, r: { imported: number; rejected: number; errors?: string[] }) => {
    totalImported += r.imported;
    totalRejected += r.rejected;
    if (r.errors?.length) {
      allErrors.push(...r.errors.map((e) => `[${label}] ${e}`));
      status = "partial";
    }
    console.log(`  ${label}: ${r.imported} imported, ${r.rejected} rejected`);
  };

  console.log(`ETL run "${jobName}" started at ${startedAt}`);

  try {
    step("data_sources", { imported: await seedDataSources(), rejected: 0 });
    step("methods", await importMethods());
    step("citations", await importCitations());

    try {
      step("assumptions", await importAssumptions());
    } catch (e) {
      console.log(`  assumptions: skipped (${(e as Error).message})`);
    }
  } catch (e) {
    status = "failed";
    allErrors.push((e as Error).message);
  }

  await db.query(
    `CREATE etl_run CONTENT {
      job_name: $job_name,
      status: $status,
      records_imported: $imported,
      records_rejected: $rejected,
      errors: $errors,
      started_at: time::from::iso8601($started_at),
      completed_at: time::now(),
      created_at: time::now()
    }`,
    {
      job_name: jobName,
      status,
      imported: totalImported,
      rejected: totalRejected,
      errors: allErrors,
      started_at: startedAt,
    },
  );

  console.log(`ETL run complete: ${totalImported} imported, ${totalRejected} rejected (${status})`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  importAll()
    .then(() => process.exit(0))
    .catch((e) => {
      console.error("ETL failed:", e);
      process.exit(1);
    });
}
