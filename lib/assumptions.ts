import { getDb } from "./db/client";
import { TABLES } from "./db/schema";

export interface CurrentAssumption {
  name: string;
  value: number;
  unit?: string;
  source_name: string;
  source_url: string;
  source_retrieved_at: string;
}

/**
 * Fetch the *current* economic assumptions (beyond-textbook): risk-free rate,
 * equity risk premium, country premia, etc. Each is provenance-tracked.
 * Only the most recent (valid_until = NONE) value per name is returned.
 */
export async function getCurrentAssumptions(): Promise<CurrentAssumption[]> {
  const db = await getDb();
  const [rows] = await db.query<[CurrentAssumption[]]>(
    `SELECT name, value, unit, source_name, source_url, source_retrieved_at
     FROM ${TABLES.ASSUMPTION}
     WHERE valid_until IS NONE
     ORDER BY name`,
  );
  return rows;
}

/** Look up a single current assumption by name. */
export async function getAssumption(name: string): Promise<CurrentAssumption | null> {
  const db = await getDb();
  const [rows] = await db.query<[CurrentAssumption[]]>(
    `SELECT name, value, unit, source_name, source_url, source_retrieved_at
     FROM ${TABLES.ASSUMPTION}
     WHERE name = $name AND valid_until IS NONE
     LIMIT 1`,
    { name },
  );
  return rows[0] ?? null;
}
