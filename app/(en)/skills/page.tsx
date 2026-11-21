import type { Metadata } from "next";
import { CopyPromptButton } from "@/components/CopyPromptButton";

export const metadata: Metadata = {
  title: "AI-Agent Skills",
  description:
    "Reusable AI-agent skills for startup valuation — core, advanced, industry, foundations, stakeholder, and emerging methods.",
  alternates: {
    canonical: "https://startup-valuation.ascent-partners.com/skills",
  },
};

const GITHUB_BASE = "https://github.com/simonmak-ascent/startup-valuation/blob/main/skills";

const skills = [
  {
    slug: "valuation-core",
    name: "Core Valuation Methods",
    description:
      "Scorecard, Berkus, Risk Factor Summation, and the VC Method for pre-revenue startups.",
    tools: ["valuation_core"],
  },
  {
    slug: "valuation-advanced",
    name: "Advanced Valuation Methods",
    description:
      "Black-Scholes, binomial trees, and named bull/base/bear scenario analysis for contingent values.",
    tools: ["valuation_advanced"],
  },
  {
    slug: "valuation-industry",
    name: "Industry-Specific Methods",
    description: "SaaS, Biotech, Fintech, Marketplace, and Hardware valuation KPIs.",
    tools: ["valuation_saas", "valuation_biotech", "valuation_fintech", "valuation_marketplace", "valuation_hardware"],
  },
  {
    slug: "valuation-foundations",
    name: "Valuation Foundations",
    description:
      "Probability, time value of money, CAPM, market comparables, and cross-border adjustments.",
    tools: ["valuation_probability", "valuation_time_value", "valuation_capm", "valuation_comparables", "valuation_international"],
  },
  {
    slug: "valuation-stakeholder",
    name: "Stakeholder Perspectives",
    description: "Dilution, OPM, PWERM, liquidation preference, and acquisition synergies.",
    tools: ["valuation_stakeholder"],
  },
  {
    slug: "valuation-emerging",
    name: "Emerging Topics",
    description: "SAFE notes, token and network valuation, ESG adjustments, and data moats.",
    tools: ["valuation_emerging"],
  },
];

const copyPrompt = (slug: string) =>
  `Use the ${slug} skill from https://startup-valuation.ascent-partners.com/skills for ${slug.replace(
    "valuation-",
    "",
  )} valuation workflows.`;

export default function SkillsPage() {
  return (
    <div className="section max-w-[1100px]">
      <h1 className="text-3xl font-bold text-text mb-2">AI-Agent Skills</h1>
      <p className="text-muted mb-8">
        Reusable skill definitions for AI agents — each describes a valuation workflow, when to use
        it, and the MCP tools to call.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {skills.map((s) => (
          <div key={s.slug} className="card flex flex-col">
            <h3 className="text-lg font-semibold text-text">{s.name}</h3>
            <p className="text-muted text-sm mt-1 flex-1">{s.description}</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {s.tools.map((t) => (
                <code key={t} className="bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded">
                  {t}
                </code>
              ))}
            </div>
            <div className="mt-4 flex gap-2">
              <a
                href={`${GITHUB_BASE}/${s.slug}/SKILL.md`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-brand text-sm hover:underline"
              >
                View SKILL.md
              </a>
              <CopyPromptButton prompt={copyPrompt(s.slug)} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
