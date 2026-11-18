import { defineConfig } from "@playwright/test";

/**
 * GUI end-to-end against the DEPLOYED product.
 *
 * Two differences from `playwright.config.ts`, both deliberate:
 *   * `webServer` is absent — these tests must observe the origin that serves users, not a local
 *     build, or they certify a page nobody visits;
 *   * the browser is the estate's Windows Chrome, attached over CDP, not a bundled headless
 *     Chromium — the attachment lives in the spec's fixture, because `connectOptions.wsEndpoint`
 *     needs a ws:// URL and Chrome advertises one with its own host, unreachable from here.
 *     `chromium.connectOverCDP(httpURL)` resolves and rewrites it.
 *
 *   PLAYWRIGHT_BASE_URL=https://startup-valuation.ascent-partners.com \
 *     pnpm exec playwright test --config=playwright.deployed.config.ts
 */

export default defineConfig({
  testDir: "./tests-webapp",
  testMatch: /deployed-gui\.spec\.ts/,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  // Every failure keeps a screenshot: a GUI claim that cannot be looked at is a claim, not evidence.
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report/deployed" }]],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "https://startup-valuation.ascent-partners.com",
    screenshot: "only-on-failure",
    video: "off",
    trace: "retain-on-failure",
    viewport: { width: 1280, height: 900 },
  },
});
