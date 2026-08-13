import type { Metadata } from "next";
import Link from "next/link";
import { CompetitorComparison } from "@/components/CompetitorComparison";
import { OpenSourceBadge } from "@/components/OpenSourceBadge";

export const metadata: Metadata = {
  title: "Why Open Source — Startup Valuation Engine",
  description:
    "Every formula is open source and auditable. No black boxes, no proprietary math, no paywall. Compare us against Equidam, Carta, and PitchBook.",
  alternates: {
    canonical: "https://startup-valuation.simonmak.com/why-open-source",
  },
};

const pillars = [
  {
    title: "Every formula is open source",
    body: "27 interactive calculators and 80+ formulas are MIT-licensed. Read the Python source, verify the math, audit the derivation — nothing is hidden.",
  },
  {
    title: "Every number is traceable",
    body: "Each calculation traces to a textbook chapter, formula number, library version, and source commit. An immutable SurrealDB audit log records every run.",
  },
  {
    title: "No paywall, no proprietary math",
    body: "Why pay $49 per report when all 27 methods are free? The mathematics of startup valuation is public knowledge — it shouldn't be locked behind a subscription.",
  },
  {
    title: "Trusted by auditors",
    body: "Financial auditors can replay any valuation from inputs through formulas to results, and verify every step against the textbook source.",
  },
];

export default function WhyOpenSourcePage() {
  return (
    <>
      <header className="hero-gradient text-white py-16 px-5 text-center">
        <div className="mb-4">
          <OpenSourceBadge showStars={false} />
        </div>
        <h1 className="text-4xl font-bold tracking-tight mb-3">Why Open Source?</h1>
        <p className="text-xl opacity-90 max-w-[680px] mx-auto">
          Startup valuation is too important to be a black box. We publish every formula, every
          assumption, and every line of code.
        </p>
      </header>

      <main>
        <section className="section">
          <h2 className="section-title">The transparency difference</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {pillars.map((p) => (
              <div key={p.title} className="card">
                <h3 className="text-lg font-semibold mb-2 text-text">{p.title}</h3>
                <p className="text-muted text-sm">{p.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">How we compare</h2>
          <p className="section-subtitle">
            Feature and pricing comparison against the leading commercial platforms.
          </p>
          <div className="card p-6">
            <CompetitorComparison />
          </div>
        </section>

        <section className="section">
          <div className="card text-center px-8 py-10">
            <h2 className="text-2xl font-bold mb-3 text-[#0083AB]">Methodology, fully disclosed</h2>
            <p className="text-muted max-w-[600px] mx-auto mb-6">
              Our formula reference is the <em>Startup Valuation</em> textbook (Mak, 2025). Every
              method page cites its chapter and formula number, links to the source commit, and
              shows the step-by-step derivation. No proprietary math — ever.
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Link href="/" className="btn-brand">
                Try the Calculators
              </Link>
              <a
                href="https://github.com/simonplmak-cloud/startup-valuation"
                className="btn-outline text-brand border-brand/40 hover:text-brand"
                target="_blank"
                rel="noopener noreferrer"
              >
                View Source on GitHub
              </a>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
