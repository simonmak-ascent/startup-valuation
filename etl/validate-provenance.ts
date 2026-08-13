import { ProvenanceSchema } from "@/lib/db/validation";

export type Provenance = {
  source_url: string;
  source_name: string;
  source_retrieved_at: string;
  source_version: string;
};

/**
 * Enforce the "no seed data" rule: every imported record MUST carry full
 * provenance. Throws with a clear message listing the missing fields (AC-E5).
 * Zod validation additionally enforces `source_url` is a valid URL and
 * `source_retrieved_at` is a valid ISO datetime.
 */
export function validateProvenance(record: unknown): Provenance {
  const r = (record ?? {}) as Record<string, unknown>;
  const result = ProvenanceSchema.safeParse({
    source_url: r.source_url,
    source_name: r.source_name,
    source_retrieved_at: r.source_retrieved_at,
    source_version: r.source_version,
  });

  if (!result.success) {
    const issues = result.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`);
    throw new Error(`Missing provenance fields: ${issues.join(", ")}`);
  }

  return result.data;
}

/** Recognized public data sources. Only these may feed the database. */
export const RECOGNIZED_SOURCES = [
  {
    slug: "startup-valuation-textbook",
    name: "Startup Valuation (Mak, 2025)",
    url: "https://www.amazon.com/Startup-Valuation-Comprehensive-Fast-Growing-Pre-Revenue-ebook/dp/B0FYTGNVWS/",
    reputation: "High",
    description:
      "Companion textbook — canonical source of all valuation formulas and worked examples.",
    access_method: "Manual Curation",
    refresh_frequency: "One-time",
  },
  {
    slug: "federal-reserve",
    name: "Federal Reserve (H.15 / Treasury)",
    url: "https://www.federalreserve.gov/releases/h15/",
    reputation: "High",
    description: "Risk-free rate and Treasury yield data.",
    access_method: "CSV Download",
    refresh_frequency: "Daily",
  },
  {
    slug: "sec-edgar",
    name: "SEC EDGAR",
    url: "https://www.sec.gov/edgar/",
    reputation: "High",
    description: "Public company 10-K/10-Q filings for comparable analysis.",
    access_method: "API",
    refresh_frequency: "Quarterly",
  },
  {
    slug: "damodaran-online",
    name: "Damodaran Online (NYU)",
    url: "https://pages.stern.nyu.edu/~adamodar/",
    reputation: "High",
    description: "Industry betas, equity risk premia, and country risk premia.",
    access_method: "CSV Download",
    refresh_frequency: "Annual",
  },
  {
    slug: "citation-cff",
    name: "Startup Valuation Engine CITATION.cff",
    url: "https://github.com/simonplmak-cloud/startup-valuation/blob/main/CITATION.cff",
    reputation: "High",
    description: "Canonical software citation metadata.",
    access_method: "Manual Curation",
    refresh_frequency: "One-time",
  },
] as const;

export type RecognizedSource = (typeof RECOGNIZED_SOURCES)[number];
