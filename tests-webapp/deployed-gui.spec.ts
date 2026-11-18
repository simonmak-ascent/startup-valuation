import { test as base, expect, chromium, type Browser } from "@playwright/test";

/**
 * GUI end-to-end against the DEPLOYED product.
 *
 * `chromium.connectOverCDP(httpUrl)` fetches `/json/version` and rewrites the advertised websocket
 * host; the config's `connectOptions` cannot, because it expects a ws:// endpoint and Chrome
 * advertises one with its own hostname, which does not resolve from this side.
 *
 * Overriding `browser` rather than `page` keeps Playwright's own `context`/`page` fixtures — so
 * `use.screenshot`, `use.trace`, `use.viewport` and `use.baseURL` still apply and the runner creates
 * and closes each test's context. A `page` fixture would bypass all of that and hand back a red run
 * with no artefact.
 */
const CDP = process.env.PLAYWRIGHT_CDP ?? "http://172.22.0.1:9223";

const test = base.extend<{}, { browser: Browser }>({
  browser: [
    // eslint-disable-next-line no-empty-pattern
    async ({}, use) => {
      const browser = await chromium.connectOverCDP(CDP);
      await use(browser);
      // On a CDP connection this closes the transport only; the user's Chrome keeps running.
      await browser.close();
    },
    { scope: "worker" },
  ],
});

/**
 * The workflows the product advertises, driven through a real browser against the deployed origin.
 *
 * `tests-deployed/` proves the same things over HTTP: status codes, JSON shapes, the MCP handshake.
 * This file proves what a user sees — that the numbers render, that the calculator responds to a
 * changed input, that the tables have rows rather than an empty state, and that a page which claims
 * a locale actually ships that locale's text. Both layers are needed: an API can be right while the
 * page renders `$NaN`, and a page can render while its fetch path is broken.
 */

test.describe("landing", () => {
  test("the advertised value and the MCP endpoint are on the page", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Startup Valuation");
    // The claim, not just a nav item: C1 in docs/test-plan.md.
    await expect(page.getByText(/pre-revenue and fast-growing startups/i).first()).toBeVisible();
    await expect(page.getByText(/finance\.yahoo|Streamable HTTP|127\.0\.0\.1:8000|\/mcp/i).first()).toBeVisible();
  });

  test("each locale ships its own language, not an English fallback", async ({ page }) => {
    // `html[lang]` alone comes from the layout and proves nothing about the copy: an English page
    // under lang="zh-Hans" passed the earlier version of this test. Each marker is a sentence from
    // that locale's own text in lib/landing.ts, so a fallback fails and zh/hk cannot be swapped.
    for (const [path, lang, marker] of [
      ["/", "en-GB", /pre-revenue and fast-growing startups/i],
      ["/zh", "zh-Hans", /高速增长的初创企业/],
      ["/hk", "zh-Hant-HK", /高速增長的初創企業/],
    ] as const) {
      await page.goto(path);
      expect(await page.locator("html").getAttribute("lang"), `${path} lang`).toBe(lang);
      await expect(page.locator("body"), `${path} copy`).toContainText(marker);
    }
  });
});

test.describe("calculator", () => {
  test("computes a total, a formula and its steps", async ({ page }) => {
    await page.goto("/methods/scorecard");
    await page.getByRole("button", { name: /Calculate/i }).click();

    await expect(page.getByText(/Result/i).first()).toBeVisible({ timeout: 20000 });
    const body = await page.locator("body").innerText();

    // C3: every result carries a formula, assumptions and steps — and a real number.
    expect(body).not.toContain("$NaN");
    expect(body).toMatch(/\$\s?[\d,]{4,}/);
    expect(body).toMatch(/Step-by-Step Derivation/i);
    expect(body).toMatch(/Scorecard Method/i);
  });

  test("the figure changes when an input changes, so it is computed rather than stored", async ({ page }) => {
    await page.goto("/methods/scorecard");
    const input = page.getByLabel(/Average Regional Valuation/i).first();
    await expect(input).toBeVisible();

    // Anchor on the result panel: copy elsewhere on the page could otherwise supply a number.
    const figure = async () => {
      const text = await page.locator("body").innerText();
      return text.match(/Valuation Result[\s\S]*?\$\s?([\d,]{4,})/)?.[1] ?? null;
    };

    await page.getByRole("button", { name: /Calculate/i }).click();
    await expect.poll(figure, { timeout: 20000 }).not.toBeNull();
    const first = await figure();
    expect(first, "the first run produced a figure").not.toBeNull();

    await input.fill("20000000");
    await page.getByRole("button", { name: /Calculate/i }).click();

    // The panel unmounts while a run is in flight, so a null read means "not yet". Requiring a
    // non-null value different from the first is what makes this assertion able to fail; a bare
    // `not.toBe(first)` was satisfied by `undefined` before any result arrived.
    await expect
      .poll(async () => {
        const value = await figure();
        return value !== null && value !== first ? value : null;
      }, { timeout: 20000 })
      .not.toBeNull();
  });
});

test.describe("market data", () => {
  // The pages are ISR (revalidate 300) and their source is a third party, so a vendor outage keeps
  // serving the source-down state for up to five minutes after recovery. Ask the probe that records
  // the dependency, and skip with that named rather than report a product failure for a vendor blip.
  test.beforeEach(async ({ request, baseURL }) => {
    const health = await request.get(`${baseURL}/api/health`);
    const body = await health.json().catch(() => ({}));
    test.skip(
      health.status() !== 200,
      `market-data dependency is not serving (${body?.dependency?.detail ?? health.status()})`,
    );
  });

  test("public companies renders priced rows and names its source", async ({ page }) => {
    await page.goto("/public-companies");
    const body = await page.locator("body").innerText();
    expect(body).toMatch(/Yahoo Finance/i);
    // The failure mode this exists to catch: the page's own copy names the symbols it could not
    // price, so a bare symbol match would pass on a page with nothing priced.
    expect(body).not.toMatch(/did not answer|No price resolved/i);
    expect(body).toMatch(/\d+\.\d{2}\s*(USD|×)/);
  });

  test("benchmarks states a median with the sample size it used", async ({ page }) => {
    await page.goto("/benchmarks");
    const body = await page.locator("body").innerText();
    expect(body).toMatch(/Median P\/E/i);
    expect(body).toMatch(/\(n=\d+\)/);
    expect(body).toMatch(/\d+\.\d{2}×/);
  });
});

test.describe("removed surfaces", () => {
  test("sign-in and the dashboard are gone, not redirected to a broken page", async ({ page }) => {
    for (const path of ["/sign-in", "/dashboard"]) {
      const res = await page.goto(path);
      expect(res?.status(), `${path} status`).toBe(404);
    }
  });
});

test.describe("legal", () => {
  test("the privacy page describes the product that exists", async ({ page }) => {
    await page.goto("/legal/privacy");
    await expect(page.getByRole("heading", { name: /Privacy/i })).toBeVisible();
    const body = await page.locator("body").innerText();
    // The corrected claims: no accounts, no Stripe, no audit log, no session cookie.
    expect(body).toMatch(/no accounts|There are no accounts/i);
    expect(body).not.toMatch(/processed by Stripe|authjs\.session-token|SurrealDB/);
  });
});
