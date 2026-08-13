import type { Metadata } from "next";
import Link from "next/link";
import { getAllMethods } from "@/lib/methods";

const methods = getAllMethods().map((m) => ({
  name: m.name,
  description: m.description,
  category: m.category,
  slug: m.slug,
}));

const stats = [
  { num: "80+", label: "Valuation Formulas" },
  { num: "14", label: "Python Modules" },
  { num: "60+", label: "MCP Tools" },
  { num: "14", label: "Interactive Calculators" },
  { num: "100%", label: "Audit Trail Coverage" },
];

const resources = [
  {
    title: "Wiki — Theory & Derivations",
    description: "13-step Scorecard derivation, glossary, notation table, and method deep-dives.",
    href: "https://github.com/simonplmak-cloud/startup-valuation/wiki",
  },
  {
    title: "PyPI Package",
    description: "pip install startup-valuation. Python 3.10+. MIT licensed.",
    href: "https://pypi.org/project/startup-valuation/",
  },
  {
    title: "GitHub Repository",
    description: "Source code, CI/CD pipeline, contributing guide, open source.",
    href: "https://github.com/simonplmak-cloud/startup-valuation",
  },
  {
    title: "Companion Textbook",
    description: "338 pages · 15 chapters · 300+ exercises · 20+ cases. By Simon Mak.",
    href: "https://www.amazon.com/Startup-Valuation-Comprehensive-Fast-Growing-Pre-Revenue-ebook/dp/B0FYTGNVWS/",
  },
];

const categoryColors: Record<string, string> = {
  Core: "bg-blue-50 text-blue-700",
  Advanced: "bg-purple-50 text-purple-700",
  Industry: "bg-green-50 text-green-700",
  Foundation: "bg-amber-50 text-amber-700",
  Emerging: "bg-teal-50 text-teal-700",
  Stakeholder: "bg-pink-50 text-pink-700",
};

export default function HomePage() {
  return (
    <>
      <header className="hero-gradient text-white py-20 px-5 text-center">
        <h1 className="text-5xl mb-4 font-bold tracking-tight">Startup Valuation Engine</h1>
        <p className="text-xl opacity-90 max-w-[700px] mx-auto mb-8">
          The most comprehensive, scientifically rigorous, and transparent startup valuation
          resource available. 80+ formulas. Full derivations. Open source. Audit trail. AI-powered.
        </p>
        <div className="inline-flex items-center gap-2 bg-green-50 text-green-700 border border-green-200 px-5 py-2.5 rounded-full font-semibold mb-6">
          <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse" />
          API Online — v1.0.2 — 45+ MCP Tools
        </div>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link href="/methods/scorecard" className="btn-primary">
            Try the Calculator
          </Link>
          <Link href="/why-open-source" className="btn-outline">
            Why Open Source?
          </Link>
          <a
            href="https://github.com/simonplmak-cloud/startup-valuation"
            className="btn-outline"
            target="_blank"
            rel="noopener noreferrer"
          >
            View on GitHub
          </a>
        </div>
      </header>

      <main>
        <section className="section">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-6">
            {stats.map((stat) => (
              <div key={stat.label} className="card text-center py-8 px-6">
                <div className="text-[2.5rem] font-bold text-[#0083AB]">{stat.num}</div>
                <div className="text-muted mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Valuation Methods</h2>
          <p className="section-subtitle">
            Every formula with full mathematical derivation, assumptions audit, worked example, and
            textbook cross-reference.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {methods.map((method) => (
              <Link
                key={method.slug}
                href={`/methods/${method.slug}`}
                className="card block no-underline text-text hover:no-underline"
              >
                <h3 className="text-lg font-semibold mb-2">{method.name}</h3>
                <p className="text-muted text-sm mb-3">{method.description}</p>
                <div className="flex gap-1.5 flex-wrap">
                  <span
                    className={`inline-block px-2.5 py-0.5 rounded-xl text-xs font-medium ${
                      categoryColors[method.category] ?? "bg-gray-50 text-gray-700"
                    }`}
                  >
                    {method.category}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <section className="section">
          <div className="card max-w-[700px] mx-auto p-8">
            <h2 className="text-2xl font-bold mb-4 text-[#0083AB]">API Access — Free &amp; Open</h2>
            <p className="text-muted mb-6">
              MCP-compatible JSON-RPC endpoint. No API key required. 45+ tools available on Vercel.
              Full 60+ tool library via Python package.
            </p>
            <div className="bg-slate-800 text-slate-200 p-5 rounded-lg font-mono text-sm overflow-x-auto">
              <div className="mb-3">
                <span className="inline-block px-2 py-0.5 rounded bg-green-500 text-white text-xs font-bold mr-2">
                  GET
                </span>
                <code>/api/health</code> — Health check + tool inventory
              </div>
              <div className="mb-3">
                <span className="inline-block px-2 py-0.5 rounded bg-indigo-500 text-white text-xs font-bold mr-2">
                  POST
                </span>
                <code>/api</code> — MCP JSON-RPC 2.0 (initialize, tools/list, tools/call)
              </div>
              <div>
                <span className="inline-block px-2 py-0.5 rounded bg-indigo-500 text-white text-xs font-bold mr-2">
                  POST
                </span>
                <code>/api/calculate</code> — Generic calculator endpoint with step-by-step
                traceability
              </div>
            </div>
            <div className="mt-4">
              <Link href="/api/playground" className="btn-brand">
                Open API Playground
              </Link>
            </div>
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Resources</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {resources.map((r) => (
              <a
                key={r.href}
                href={r.href}
                className="card block no-underline text-text hover:no-underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                <h3 className="text-lg font-semibold mb-1.5">{r.title}</h3>
                <p className="text-muted text-sm">{r.description}</p>
              </a>
            ))}
          </div>
        </section>

        <section className="section">
          <div className="card text-center px-8 py-10">
            <h2 className="text-2xl font-bold mb-3 text-[#0083AB]">Why Open Source?</h2>
            <p className="text-muted max-w-[600px] mx-auto mb-6">
              Every formula is auditable. Every number traces to a textbook source. No black boxes.
              No proprietary math. Trusted by the auditor community.
            </p>
            <Link href="/why-open-source" className="btn-brand">
              Compare vs. Equidam, Carta &amp; PitchBook
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-border py-8 px-5 text-center text-muted text-sm">
        <p>
          Built by{" "}
          <a
            href="https://www.simonmak.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-brand"
          >
            Simon Mak
          </a>{" "}
          ·{" "}
          <a
            href="https://ascent-partners.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-brand"
          >
            Ascent Partners
          </a>
        </p>
        <p className="mt-2">
          MIT License · Version 1.0.2 ·{" "}
          <a
            href="https://github.com/simonplmak-cloud/startup-valuation"
            target="_blank"
            rel="noopener noreferrer"
            className="text-brand"
          >
            GitHub
          </a>
        </p>
      </footer>
    </>
  );
}
