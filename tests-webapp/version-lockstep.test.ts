import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";

/**
 * `/api/health` reports `pkg.version`, so this file is what an operator reads to answer "which
 * release is live?". It was `1.0.0` while every other carrier said `2.1.4`, and the deployed
 * assertion only checked the *shape* of the string — so the one field that identifies the release
 * could never be wrong in a way a test would notice. This makes the lockstep mechanical.
 */
const root = path.resolve(__dirname, "..");
const read = (file: string) => readFileSync(path.join(root, file), "utf8");

describe("release version", () => {
  it("package.json matches pyproject.toml", () => {
    const pkg = JSON.parse(read("package.json")) as { version: string };
    const pyproject = read("pyproject.toml").match(/^version\s*=\s*"([^"]+)"/m)?.[1];
    expect(pyproject).toBeTruthy();
    expect(pkg.version).toBe(pyproject);
  });

  it("the server card and the MCP package agree with it", () => {
    const pkg = JSON.parse(read("package.json")) as { version: string };
    const card = JSON.parse(read("public/.well-known/mcp.json")) as { version?: string };
    // `if (card.version)` let the card drop the field entirely and stay green: the guard was
    // conditional on the thing it guards.
    expect(card.version, "the server card must state a version").toBeTruthy();
    expect(card.version).toBe(pkg.version);
  });
});
