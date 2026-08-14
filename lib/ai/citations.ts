import { getAllMethods } from "@/lib/methods";

export interface Citation {
  slug: string;
  name: string;
  chapter: string;
  formulaNumber: string;
  description: string;
}

/**
 * Resolve method slugs to registry-backed citations. Every recommendation in
 * the AI advisor traces to a textbook chapter + formula number via the
 * canonical method registry (single source of truth).
 */
export function resolveCitations(slugs: string[]): Citation[] {
  const bySlug = new Map(getAllMethods().map((m) => [m.slug, m]));
  const citations: Citation[] = [];
  for (const slug of slugs) {
    const m = bySlug.get(slug);
    if (m && !citations.some((c) => c.slug === slug)) {
      citations.push({
        slug: m.slug,
        name: m.name,
        chapter: m.textbookChapter,
        formulaNumber: m.formulaNumber,
        description: m.description,
      });
    }
  }
  return citations;
}

/**
 * Extract method slugs from free-text by matching each registry slug (and its
 * space-normalized form) against the text. Deterministic and registry-backed —
 * never relies on the LLM to return slugs verbatim.
 */
export function extractSlugs(text: string): string[] {
  const lower = text.toLowerCase();
  return getAllMethods()
    .filter((m) => lower.includes(m.slug) || lower.includes(m.slug.replace(/-/g, " ")))
    .map((m) => m.slug);
}
