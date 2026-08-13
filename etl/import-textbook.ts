import { getDb } from "@/lib/db/client";
import { getAllMethods } from "@/lib/methods";
import { RECOGNIZED_SOURCES, validateProvenance } from "./validate-provenance";

/**
 * Import valuation method metadata into the `method` table.
 * Source of truth: the canonical method registry in `lib/methods` (which
 * traces each method to a textbook chapter + Python function). Idempotent.
 */
export async function importMethods(): Promise<{ imported: number; rejected: number }> {
  const db = await getDb();
  const methods = getAllMethods();

  let imported = 0;
  let rejected = 0;

  for (const m of methods) {
    const [moduleName, functionName] = m.formulaNumber.split(".");

    const inputsSchema = {
      type: "object",
      properties: Object.fromEntries(
        m.inputs.map((i) => [
          i.name,
          {
            type: i.type,
            description: i.description ?? i.label,
            ...(i.defaultValue !== undefined ? { default: i.defaultValue } : {}),
          },
        ]),
      ),
    };

    const record = {
      name: m.name,
      slug: m.slug,
      module: moduleName ?? "",
      function_name: functionName ?? m.methodName,
      category: m.category,
      description: m.description,
      inputs_schema: inputsSchema,
      textbook_chapter: m.textbookChapter,
      formula_numbers: [m.formulaNumber],
      citations: [],
      assumptions: [],
    };

    try {
      await db.query(`UPSERT type::record("method", $id) MERGE $data`, { id: m.slug, data: record });
      imported++;
    } catch {
      rejected++;
    }
  }

  return { imported, rejected };
}

/** Seed the `data_source` catalog with recognized public sources. */
export async function seedDataSources(): Promise<number> {
  const db = await getDb();

  for (const s of RECOGNIZED_SOURCES) {
    await db.query(`UPSERT type::record("data_source", $id) MERGE $data`, {
      id: s.slug,
      data: {
        name: s.name,
        url: s.url,
        reputation: s.reputation,
        description: s.description,
        access_method: s.access_method,
        refresh_frequency: s.refresh_frequency,
      },
    });
  }

  return RECOGNIZED_SOURCES.length;
}

/** Validate a raw record carries full provenance (AC-E5). */
export function assertProvenance(record: Record<string, unknown>): void {
  validateProvenance(record);
}
