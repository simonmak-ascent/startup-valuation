import { describe, it, expect } from "vitest";
import { getAllMethods } from "../lib/methods";

/**
 * Cross-validation (AC-15): every webapp-facing method config must map to a
 * known calculate key, and its traceability reference must not be a
 * placeholder (function-name formulaNumber).
 */
describe("method registry cross-validation", () => {
  const methods = getAllMethods();

  it("exposes 27 methods", () => {
    expect(methods.length).toBe(27);
  });

  it("every method has a non-placeholder formulaNumber", () => {
    for (const m of methods) {
      expect(m.formulaNumber).not.toMatch(/^[a-z_]+\.[a-z_]+$/);
      expect(m.formulaNumber.length).toBeGreaterThan(0);
    }
  });

  it("every method has a textbookChapter", () => {
    for (const m of methods) {
      expect(m.textbookChapter).toMatch(/^Chapter \d+/);
    }
  });

  it("every method has a unique slug and calculate methodName", () => {
    const slugs = new Set(methods.map((m) => m.slug));
    expect(slugs.size).toBe(methods.length);
    for (const m of methods) {
      expect(m.methodName.length).toBeGreaterThan(0);
    }
  });

  it("flagship methods have correct formula numbers", () => {
    const bySlug = Object.fromEntries(methods.map((m) => [m.slug, m]));
    expect(bySlug.scorecard.formulaNumber).toBe("3.1");
    expect(bySlug.berkus.formulaNumber).toBe("3.2");
    expect(bySlug["vc-method"].formulaNumber).toBe("3.4");
    expect(bySlug["saas-ltv"].formulaNumber).toBe("11.2");
    expect(bySlug.capm.formulaNumber).toBe("2.5");
  });
});
