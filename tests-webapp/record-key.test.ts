import { describe, expect, it } from "vitest";
import { recordKey } from "@/lib/db/repositories/audit";

const UUID = "9f1c2d3e-4a5b-6c7d-8e9f-0a1b2c3d4e5f";

describe("recordKey", () => {
  // surreal.js returns record-id fields as RecordId, whose toString() quotes a
  // hyphenated key: `valuation_run:⟨uuid⟩`. The export route round-trips that value
  // through the dashboard link and a URL, and `type::record()` must rebuild exactly
  // what createAuditLog stored — so every shape has to reduce to the same key.
  it("unwraps the record-id form the SDK returns", () => {
    expect(recordKey(`valuation_run:⟨${UUID}⟩`)).toBe(UUID);
  });

  it("unwraps the unquoted table:key form", () => {
    expect(recordKey(`valuation_run:${UUID}`)).toBe(UUID);
  });

  it("leaves a raw key alone (the write path's input)", () => {
    expect(recordKey(UUID)).toBe(UUID);
  });

  it("survives a URL round trip", () => {
    expect(recordKey(decodeURIComponent(encodeURIComponent(`valuation_run:⟨${UUID}⟩`)))).toBe(UUID);
  });

  it("normalises a user id the same way", () => {
    expect(recordKey("user:abc123")).toBe("abc123");
    expect(recordKey("user:⟨abc123⟩")).toBe("abc123");
  });
});
