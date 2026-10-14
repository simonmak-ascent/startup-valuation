import type { Metadata } from "next";
import { Open_Sans, Titillium_Web, Raleway } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import { SessionProvider } from "@/components/SessionProvider";
import { CookieConsent } from "@/components/CookieConsent";
import { ThemeToggle } from "@/components/ThemeToggle";
import "@/app/globals.css";

const openSans = Open_Sans({ subsets: ["latin"], variable: "--font-open-sans", display: "swap" });
const titillium = Titillium_Web({ subsets: ["latin"], weight: ["400", "600", "700"], variable: "--font-titillium", display: "swap" });
const raleway = Raleway({ subsets: ["latin"], variable: "--font-raleway", display: "swap" });

export const metadata: Metadata = {
  title: { default: "Startup Valuation Engine — The Global Authority for Startup Valuation", template: "%s — Startup Valuation Engine" },
  description:
    "The most comprehensive, scientifically rigorous, and transparent startup valuation resource available. 14 valuation methods, 80+ formulas, full mathematical derivations, auditable audit trail. Open source.",
  keywords: ["startup valuation", "how to value a startup", "valuation calculator", "DCF", "Black-Scholes", "scorecard method", "venture capital", "MCP server", "Python library", "open source", "SaaS valuation", "biotech rNPV"],
  authors: [{ name: "Simon Mak", url: "https://www.simonmak.com" }],
  creator: "Simon Mak — Ascent Partners",
  publisher: "Ascent Partners",
  metadataBase: new URL("https://startup-valuation.ascent-partners.com"),
  openGraph: {
    type: "website",
    title: "Startup Valuation Engine — 80+ Formulas, Open Source",
    description: "The most credible, detailed, and traceable startup valuation resource available. Every formula with step-by-step derivation. 14 methods. Audit trail. Open source.",
    url: "https://startup-valuation.ascent-partners.com",
    siteName: "Startup Valuation Engine",
    images: [{ url: "/social-preview.png", width: 1280, height: 640, alt: "Startup Valuation Engine" }],
  },
  twitter: { card: "summary_large_image", title: "Startup Valuation Engine", description: "80+ valuation formulas. Scientific rigor. Open source." },
  robots: { index: true, follow: true, googleBot: { index: true, follow: true, "max-video-preview": -1, "max-image-preview": "large", "max-snippet": -1 } },
  alternates: {
    canonical: "https://startup-valuation.ascent-partners.com",
    languages: {
      "en-GB": "https://startup-valuation.ascent-partners.com",
      "zh-Hans": "https://startup-valuation.ascent-partners.com/zh",
      "zh-Hant-HK": "https://startup-valuation.ascent-partners.com/hk",
      "x-default": "https://startup-valuation.ascent-partners.com",
    },
  },
};

// Blocking theme init — dark default, persisted choice (APG parity, no FOUC).
const THEME_INIT =
  "try{var v=localStorage.getItem('apg-theme');document.documentElement.setAttribute('data-theme',v==='light'||v==='dark'?v:'dark');}catch(e){document.documentElement.setAttribute('data-theme','dark');}";

const NAV = [
  { href: "/#methods", label: "Methods" },
  { href: "/ai-advisor", label: "AI Advisor" },
  { href: "/benchmarks", label: "Benchmarks" },
  { href: "/public-companies", label: "Public Companies" },
  { href: "/api/playground", label: "API Playground" },
  { href: "/skills", label: "Skills" },
  { href: "/why-open-source", label: "Why Open Source" },
];

export function RootShell({ lang, children }: { lang: string; children: React.ReactNode }) {
  return (
    <html lang={lang} data-theme="dark" suppressHydrationWarning className={`${openSans.variable} ${titillium.variable} ${raleway.variable}`}>
      <body className="antialiased">
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
        <nav className="border-b border-border bg-card">
          <div className="mx-auto flex max-w-[65.125rem] items-center gap-5 overflow-x-auto px-5 py-3 text-sm">
            <a href="/" className="whitespace-nowrap font-semibold text-text no-underline hover:no-underline">Startup Valuation</a>
            {NAV.map((n) => (
              <a key={n.href} href={n.href} className="whitespace-nowrap text-muted no-underline hover:text-brand">{n.label}</a>
            ))}
            <ThemeToggle />
          </div>
        </nav>
        <SessionProvider>{children}</SessionProvider>
        <CookieConsent />
        <footer className="border-t border-border px-5 py-6 text-center text-xs text-muted">
          <div className="mb-2 flex flex-wrap justify-center gap-4">
            <a href="/legal/terms" className="hover:text-brand">Terms of Service</a>
            <a href="/legal/privacy" className="hover:text-brand">Privacy Policy</a>
            <a href="/legal/cookies" className="hover:text-brand">Cookie Policy</a>
          </div>
          <p>© {new Date().getFullYear()} Ascent Partners · Startup Valuation Engine · MIT License</p>
        </footer>
        <Analytics />
      </body>
    </html>
  );
}
