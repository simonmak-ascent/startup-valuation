import { describe, it, expect } from "vitest";
import { extractSlugs, resolveCitations } from "../lib/ai/citations";

/**
 * Citation traceability (AC-E4): the advisor's recommendations must resolve to
 * registry-backed citations — slug, chapter, and formula number — so every
 * recommendation links to an auditable calculator run.
 */
describe("AI citation traceability", () => {
  it("extracts slugs from free-text recommendations", () => {
    const slugs = extractSlugs(
      "For a pre-revenue SaaS startup, use the Scorecard method and the SaaS LTV model.",
    );
    expect(slugs).toContain("scorecard");
    expect(slugs).toContain("saas-ltv");
  });

  it("resolves citations with chapter + formula", () => {
    const citations = resolveCitations(["scorecard", "capm"]);
    expect(citations).toHaveLength(2);
    const scorecard = citations.find((c) => c.slug === "scorecard")!;
    expect(scorecard.chapter).toMatch(/^Chapter \d+/);
    expect(scorecard.formulaNumber).toBe("3.1");
    expect(scorecard.name).toBe("Scorecard Method");
  });

  it("ignores unknown slugs", () => {
    expect(resolveCitations(["not-a-method"])).toHaveLength(0);
  });

  it("deduplicates repeated slugs", () => {
    const citations = resolveCitations(["capm", "capm", "capm"]);
    expect(citations).toHaveLength(1);
  });
});
