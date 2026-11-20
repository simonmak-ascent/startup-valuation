/**
 * The shell's own words: navigation, legal links, and the footer line.
 *
 * These were hard-coded English inside `RootShell`, so `/zh` and `/hk` served a page whose `<html
 * lang>` said one thing and whose navigation said another — the body copy was localised by
 * `lib/landing.ts` and everything around it was not.
 *
 * Kept as data next to that file rather than behind an i18n framework: nine strings across three
 * locales is a lookup table, not a routing concern, and `next-intl` would add a dependency and a
 * request-time negotiation path for a site whose locale is fixed by the route.
 *
 * The hrefs stay in English because every route except the two landing pages is English-only; a
 * translated label pointing at `/benchmarks` is the honest description of what exists.
 */

import { LOCALE_META, locales, type Locale } from "./landing";

export type Chrome = {
  nav: { href: string; label: string }[];
  legal: { href: string; label: string }[];
  /** The footer's tail after the year and the company: the product name and the licence. */
  footer: { product: string; licence: string };
  /** The theme toggle's accessible name — a control on every page, so it is chrome too. */
  theme: { toLight: string; toDark: string };
};

const EN: Chrome = {
  nav: [
    { href: "/#methods", label: "Methods" },
    { href: "/benchmarks", label: "Benchmarks" },
    { href: "/public-companies", label: "Public Companies" },
    { href: "/api/playground", label: "API Playground" },
    { href: "/skills", label: "Skills" },
    { href: "/why-open-source", label: "Why Open Source" },
    { href: "/docs", label: "Docs" },
  ],
  legal: [
    { href: "/legal/terms", label: "Terms of Service" },
    { href: "/legal/privacy", label: "Privacy Policy" },
    { href: "/legal/cookies", label: "Cookie Policy" },
  ],
  footer: { product: "Startup Valuation Engine", licence: "MIT License" },
  theme: { toLight: "Switch to light mode", toDark: "Switch to dark mode" },
};

const ZH_HANS: Chrome = {
  nav: [
    { href: "/#methods", label: "方法" },
    { href: "/benchmarks", label: "基准" },
    { href: "/public-companies", label: "上市公司" },
    { href: "/api/playground", label: "API 试用" },
    { href: "/skills", label: "技能" },
    { href: "/why-open-source", label: "为何开源" },
    { href: "/docs", label: "文档" },
  ],
  legal: [
    { href: "/legal/terms", label: "服务条款" },
    { href: "/legal/privacy", label: "隐私政策" },
    { href: "/legal/cookies", label: "Cookie 政策" },
  ],
  footer: { product: "创业估值引擎", licence: "MIT 许可证" },
  theme: { toLight: "切换到浅色模式", toDark: "切换到深色模式" },
};

const ZH_HANT_HK: Chrome = {
  nav: [
    { href: "/#methods", label: "方法" },
    { href: "/benchmarks", label: "基準" },
    { href: "/public-companies", label: "上市公司" },
    { href: "/api/playground", label: "API 測試台" },
    { href: "/skills", label: "技能" },
    { href: "/why-open-source", label: "為何開源" },
    { href: "/docs", label: "文件" },
  ],
  // Hong Kong's own term is 私隱, not the mainland 隐私.
  legal: [
    { href: "/legal/terms", label: "服務條款" },
    { href: "/legal/privacy", label: "私隱政策" },
    { href: "/legal/cookies", label: "Cookie 政策" },
  ],
  footer: { product: "創業估值引擎", licence: "MIT 許可證" },
  theme: { toLight: "切換至淺色模式", toDark: "切換至深色模式" },
};

const CHROME: Readonly<Record<Locale, Chrome>> = {
  en: EN,
  zh: ZH_HANS,
  hk: ZH_HANT_HK,
};

/**
 * Resolve by the `htmlLang` the layouts already pass, using `LOCALE_META` as the one map from a
 * locale to its htmlLang — so adding a locale there cannot silently serve English chrome.
 */
export function chromeFor(lang: string): Chrome {
  const locale = locales.find((l) => LOCALE_META[l].htmlLang === lang);
  return CHROME[locale ?? "en"] ?? EN;
}
