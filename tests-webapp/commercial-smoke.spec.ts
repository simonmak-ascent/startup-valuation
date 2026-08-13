import { test, expect } from "@playwright/test";

test.describe("commercial-readiness smoke", () => {
  test("landing page renders with nav + legal footer", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Methods" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Terms of Service" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Privacy Policy" })).toBeVisible();
  });

  test("404 page renders", async ({ page }) => {
    const response = await page.goto("/does-not-exist");
    expect(response?.status()).toBe(404);
    await expect(page.getByText("404")).toBeVisible();
  });

  test("method calculator has labeled inputs and computes", async ({ page }) => {
    await page.goto("/methods/scorecard");
    await expect(page.getByLabel("Average Regional Valuation ($)")).toBeVisible();
    await page.getByRole("button", { name: "Calculate Valuation" }).click();
    await expect(page.getByText("Valuation Result")).toBeVisible({ timeout: 15000 });
  });

  test("legal pages render", async ({ page }) => {
    await page.goto("/legal/privacy");
    await expect(page.getByRole("heading", { name: "Privacy Policy" })).toBeVisible();
    await expect(page.getByText(/Version 2026/)).toBeVisible();
  });
});
