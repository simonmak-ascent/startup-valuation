import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests-webapp",
  // Only `*.spec.ts`. Playwright's default match also takes `*.test.ts`, which in this directory are
  // vitest files — it tried to load them and the listing died before a single browser started.
  testMatch: /.*\.spec\.ts/,
  // `deployed-gui.spec.ts` drives the live origin in the Windows Chrome over CDP and is run by
  // `playwright.deployed.config.ts`; without this it is collected here too — twice, once per project
  // — and `pnpm test:e2e` silently hits production.
  testIgnore: /deployed-gui\.spec\.ts/,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "mobile",
      use: { ...devices["Pixel 5"] },
    },
  ],
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
