import { describe, expect, it } from "vitest";
import { clientKey } from "@/lib/rate-limit";

function requestWith(forwarded?: string): Request {
  const headers = new Headers();
  if (forwarded !== undefined) {
    headers.set("x-forwarded-for", forwarded);
  }
  return new Request("https://example.test/api/ai", { headers });
}

describe("clientKey", () => {
  it("uses the rightmost hop, which is the one the ALB appended", () => {
    // A caller can prepend anything; only the last entry is added by our own edge.
    expect(clientKey(requestWith("1.2.3.4, 203.0.113.9"))).toBe("203.0.113.9");
  });

  it("ignores a forged leftmost value", () => {
    const forged = requestWith("10.0.0.1, 198.51.100.7");
    expect(clientKey(forged)).toBe("198.51.100.7");
    expect(clientKey(forged)).not.toBe("10.0.0.1");
  });

  it("trims whitespace and skips empty hops", () => {
    expect(clientKey(requestWith(" 1.1.1.1 ,  2.2.2.2 ,"))).toBe("2.2.2.2");
  });

  it("falls back to a single bucket when the header is absent", () => {
    expect(clientKey(requestWith())).toBe("unknown");
    expect(clientKey(requestWith(""))).toBe("unknown");
  });
});
