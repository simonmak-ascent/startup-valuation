import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default:
      "Startup Valuation Engine — The Global Authority for Startup Valuation",
    template: "%s — Startup Valuation Engine",
  },
  description:
    "The most comprehensive, scientifically rigorous, and transparent startup valuation resource available. 14 valuation methods, 80+ formulas, full mathematical derivations, auditable audit trail. Open source.",
  keywords: [
    "startup valuation",
    "how to value a startup",
    "valuation calculator",
    "DCF",
    "Black-Scholes",
    "scorecard method",
    "venture capital",
    "MCP server",
    "Python library",
    "open source",
    "SaaS valuation",
    "biotech rNPV",
    "SAFE note valuation",
    "Monte Carlo valuation",
  ],
  authors: [{ name: "Simon Mak", url: "https://www.simonmak.com" }],
  creator: "Simon Mak — Ascent Partners",
  publisher: "Ascent Partners",
  metadataBase: new URL("https://startup-valuation.simonmak.com"),
  openGraph: {
    type: "website",
    title: "Startup Valuation Engine — 80+ Formulas, Open Source",
    description:
      "The most credible, detailed, and traceable startup valuation resource available. Every formula with step-by-step derivation. 14 methods. Audit trail. Open source.",
    url: "https://startup-valuation.simonmak.com",
    siteName: "Startup Valuation Engine",
    images: [
      {
        url: "/social-preview.png",
        width: 1280,
        height: 640,
        alt: "Startup Valuation Engine — The Global Authority",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Startup Valuation Engine",
    description: "80+ valuation formulas. Scientific rigor. Open source.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    google: "PLACEHOLDER_GOOGLE_VERIFICATION",
  },
  alternates: {
    canonical: "https://startup-valuation.simonmak.com",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="antialiased">
          {children}
          <Analytics />
        </body>
      </html>
    </ClerkProvider>
  );
}
