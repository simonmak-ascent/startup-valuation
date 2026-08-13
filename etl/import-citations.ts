import { getDb } from "@/lib/db/client";
import { validateProvenance } from "./validate-provenance";

/**
 * Canonical citations — real sources only, each with full provenance.
 * Idempotent (upsert by deterministic id).
 */
const CITATIONS = [
  {
    id: "citation:textbook-mak-2025",
    title: "Startup Valuation: A Comprehensive Guide for Fast-Growing and Pre-Revenue Companies",
    authors: ["Simon Mak"],
    year: 2025,
    type: "textbook",
    url: "https://www.amazon.com/Startup-Valuation-Comprehensive-Fast-Growing-Pre-Revenue-ebook/dp/B0FYTGNVWS/",
    source_url:
      "https://www.amazon.com/Startup-Valuation-Comprehensive-Fast-Growing-Pre-Revenue-ebook/dp/B0FYTGNVWS/",
    source_name: "Startup Valuation (Mak, 2025)",
    source_retrieved_at: "2026-08-12T00:00:00Z",
    source_version: "1st edition",
  },
  {
    id: "citation:software-cff-2026",
    title: "Startup Valuation Engine (software)",
    authors: ["Simon Mak"],
    year: 2026,
    type: "other",
    url: "https://github.com/simonplmak-cloud/startup-valuation",
    source_url: "https://github.com/simonplmak-cloud/startup-valuation/blob/main/CITATION.cff",
    source_name: "Startup Valuation Engine CITATION.cff",
    source_retrieved_at: "2026-08-12T00:00:00Z",
    source_version: "1.0.2",
  },
] as const;

export async function importCitations(): Promise<{ imported: number; rejected: number }> {
  const db = await getDb();
  let imported = 0;
  let rejected = 0;

  for (const c of CITATIONS) {
    try {
      validateProvenance(c);
      await db.query(`UPSERT type::record("citation", $id) MERGE $data`, {
        id: c.id.replace("citation:", ""),
        data: {
          title: c.title,
          authors: c.authors,
          year: c.year,
          type: c.type,
          url: c.url,
          source_url: c.source_url,
          source_name: c.source_name,
          source_retrieved_at: c.source_retrieved_at,
          source_version: c.source_version,
        },
      });
      imported++;
    } catch {
      rejected++;
    }
  }

  return { imported, rejected };
}
