import { getDb } from "@/lib/db/client";
import { TABLES } from "@/lib/db/schema";

/**
 * Compute valuation benchmarks (median, 25th/75th percentile) from
 * provenance-tracked `valuation_event` records. Only records whose source has
 * reputation >= Medium are included. No hardcoded values — every benchmark
 * derives from source data (AC-15).
 */

interface EventRow {
  valuation_amount: number;
  stage?: string | null;
  source_reputation?: string | null;
}

function percentile(sorted: number[], p: number): number {
  if (sorted.length === 0) return 0;
  const idx = (sorted.length - 1) * p;
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sorted[lo]!;
  return sorted[lo]! + (sorted[hi]! - sorted[lo]!) * (idx - lo);
}

export async function computeBenchmarks(version: string): Promise<number> {
  const db = await getDb();

  const [events] = await db.query<[EventRow[]]>(
    `SELECT valuation_amount, stage, source.reputation AS source_reputation
     FROM ${TABLES.VALUATION_EVENT}
     FETCH source`,
  );

  const filtered = events.filter(
    (e) => e.source_reputation === "High" || e.source_reputation === "Medium",
  );

  const byStage = new Map<string, number[]>();
  for (const e of filtered) {
    const key = e.stage ?? "all";
    if (!byStage.has(key)) byStage.set(key, []);
    byStage.get(key)!.push(e.valuation_amount);
  }

  let created = 0;
  for (const [stage, values] of byStage.entries()) {
    const sorted = [...values].sort((a, b) => a - b);
    const median = percentile(sorted, 0.5);
    const p25 = percentile(sorted, 0.25);
    const p75 = percentile(sorted, 0.75);

    await db.query(
      `CREATE ${TABLES.BENCHMARK} CONTENT {
        version: $version,
        stage: $stage,
        metric: "valuation_median",
        value: $value,
        p25: $p25,
        p75: $p75,
        count: $count,
        source_records: [],
        computed_at: time::now(),
        created_at: time::now()
      }`,
      {
        version,
        stage: stage === "all" ? null : stage,
        value: median,
        p25,
        p75,
        count: sorted.length,
      },
    );
    created++;
  }

  return created;
}
