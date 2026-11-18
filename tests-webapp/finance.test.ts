import { describe, expect, it } from "vitest";
import { median } from "@/lib/finance/yahoo";

/**
 * The two pages depend on `median` never inventing a figure: a metric a company does not report is
 * dropped, not counted as zero. That rule was prose in `lib/finance/yahoo.ts` until this file.
 */
describe("median", () => {
  it("returns null rather than zero for an empty set", () => {
    expect(median([])).toBeNull();
    expect(median([null, null])).toBeNull();
  });

  it("ignores undefined members instead of treating them as zero", () => {
    // Two companies report a P/E of 20 and 30; one does not report one at all.
    expect(median([20, null, 30])).toBe(25);
  });

  it("averages the middle pair for an even count", () => {
    expect(median([10, 20, 30, 40])).toBe(25);
  });

  it("returns the middle value for an odd count", () => {
    expect(median([5, 1, 3])).toBe(3);
  });

  it("drops non-finite values, which is what a vendor sometimes returns", () => {
    expect(median([Number.NaN, Number.POSITIVE_INFINITY, 12])).toBe(12);
  });

  it("does not mutate the caller's array", () => {
    const input = [3, 1, 2];
    median(input);
    expect(input).toEqual([3, 1, 2]);
  });
});
