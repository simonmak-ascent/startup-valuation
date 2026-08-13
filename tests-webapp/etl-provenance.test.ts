import { describe, it, expect } from "vitest";
import { validateProvenance } from "../etl/validate-provenance";

const valid = {
  source_url: "https://www.federalreserve.gov/releases/h15/",
  source_name: "Federal Reserve H.15",
  source_retrieved_at: "2026-08-12T00:00:00Z",
  source_version: "2026-08-11 release",
};

describe("validateProvenance (AC-E5 — no seed data)", () => {
  it("accepts a record with full provenance", () => {
    expect(() => validateProvenance(valid)).not.toThrow();
  });

  it("rejects a record missing source_url", () => {
    const { source_url: _omit, ...missing } = valid;
    expect(() => validateProvenance(missing)).toThrow(/source_url/);
  });

  it("rejects a record missing source_name", () => {
    const { source_name: _omit, ...missing } = valid;
    expect(() => validateProvenance(missing)).toThrow(/source_name/);
  });

  it("rejects a record missing source_retrieved_at", () => {
    const { source_retrieved_at: _omit, ...missing } = valid;
    expect(() => validateProvenance(missing)).toThrow(/source_retrieved_at/);
  });

  it("rejects a record missing source_version", () => {
    const { source_version: _omit, ...missing } = valid;
    expect(() => validateProvenance(missing)).toThrow(/source_version/);
  });

  it("rejects an invalid (non-URL) source_url", () => {
    expect(() => validateProvenance({ ...valid, source_url: "not-a-url" })).toThrow();
  });

  it("rejects an invalid source_retrieved_at", () => {
    expect(() => validateProvenance({ ...valid, source_retrieved_at: "yesterday" })).toThrow();
  });
});
