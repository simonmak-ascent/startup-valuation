import { describe, expect, it } from "vitest";
import { chromeFor } from "@/lib/chrome";
import { LOCALE_META, locales } from "@/lib/landing";

/**
 * The shell's words were hard-coded English inside `RootShell`, so `/zh` and `/hk` served a page
 * whose `<html lang>` said one thing and whose navigation and legalese said another. Nothing
 * asserted the localised chrome afterwards, so a revert to literals would pass every other test.
 */
describe("chrome for each locale", () => {
  it("resolves every locale the registry declares", () => {
    for (const locale of locales) {
      const chrome = chromeFor(LOCALE_META[locale].htmlLang);
      expect(chrome.nav.length, `${locale} nav`).toBeGreaterThanOrEqual(6);
      expect(chrome.legal.length, `${locale} legal`).toBe(3);
      expect(chrome.theme.toLight, `${locale} theme`).toBeTruthy();
    }
  });

  it("does not serve English chrome on a translated route", () => {
    const en = chromeFor("en-GB");
    for (const lang of ["zh-Hans", "zh-Hant-HK"]) {
      const chrome = chromeFor(lang);
      expect(chrome.nav.map((n) => n.label)).not.toEqual(en.nav.map((n) => n.label));
      expect(chrome.legal.map((l) => l.label)).not.toEqual(en.legal.map((l) => l.label));
      expect(chrome.theme.toDark).not.toBe(en.theme.toDark);
    }
  });

  it("uses the locale's own word for privacy", () => {
    // Hong Kong writes 私隱; the mainland writes 隐私. Getting this wrong is the kind of thing an
    // English-reading author does not notice in a diff.
    expect(chromeFor("zh-Hant-HK").legal.find((l) => l.href === "/legal/privacy")?.label).toContain("私隱");
    expect(chromeFor("zh-Hans").legal.find((l) => l.href === "/legal/privacy")?.label).toContain("隐私");
  });

  it("keeps the hrefs in one shape across locales, so a link cannot go missing in a translation", () => {
    const en = chromeFor("en-GB");
    for (const locale of locales) {
      const chrome = chromeFor(LOCALE_META[locale].htmlLang);
      expect(chrome.nav.map((n) => n.href)).toEqual(en.nav.map((n) => n.href));
      expect(chrome.legal.map((l) => l.href)).toEqual(en.legal.map((l) => l.href));
    }
  });

  it("falls back to English for a lang it has never seen rather than rendering nothing", () => {
    expect(chromeFor("fr-FR").nav.length).toBe(chromeFor("en-GB").nav.length);
  });
});
