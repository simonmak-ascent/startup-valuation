import { computeBenchmarks } from "@/lib/benchmarks/compute";

/**
 * Compute valuation benchmarks from provenance-tracked valuation events.
 * Usage: `pnpm etl:compute-benchmarks`
 */
async function main(): Promise<void> {
  const version = process.argv[2] ?? new Date().toISOString().slice(0, 10);
  console.log(`Computing benchmarks for version "${version}"…`);
  const created = await computeBenchmarks(version);
  console.log(`Done: ${created} benchmark records created.`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main()
    .then(() => process.exit(0))
    .catch((e) => {
      console.error("Benchmark computation failed:", e);
      process.exit(1);
    });
}
