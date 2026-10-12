import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { CalculatorPage } from "@/components/CalculatorPage";
import { getMethodBySlug, getAllMethods } from "@/lib/methods";
import { buildHowToJsonLd, buildBreadcrumbJsonLd, buildFaqJsonLd } from "@/lib/seo";
import { getCurrentAssumptions } from "@/lib/assumptions";

interface MethodPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  return getAllMethods().map((m) => ({ slug: m.slug }));
}

export async function generateMetadata({ params }: MethodPageProps): Promise<Metadata> {
  const { slug } = await params;
  const method = getMethodBySlug(slug);
  if (!method) return {};

  return {
    title: `${method.name} — Startup Valuation Calculator`,
    description: method.description,
    openGraph: {
      title: `${method.name} — Startup Valuation Calculator`,
      description: method.description,
      url: `https://startup-valuation.simonmak.com/methods/${slug}`,
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: `${method.name} — Startup Valuation Calculator`,
      description: method.description,
    },
    alternates: {
      canonical: `https://startup-valuation.simonmak.com/methods/${slug}`,
    },
  };
}

export default async function MethodPage({ params }: MethodPageProps) {
  const { slug } = await params;
  const method = getMethodBySlug(slug);

  if (!method) {
    notFound();
  }

  let assumptions: Awaited<ReturnType<typeof getCurrentAssumptions>> = [];
  try {
    assumptions = await getCurrentAssumptions();
  } catch {
    assumptions = [];
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(buildHowToJsonLd(method)) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(buildBreadcrumbJsonLd(method)) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(buildFaqJsonLd(method)) }}
      />
      <CalculatorPage slug={slug} />
      {assumptions.length > 0 && (
        <div className="section max-w-[900px] pt-0">
          <div className="card">
            <h2 className="text-lg font-semibold text-text mb-3">Current Market Assumptions</h2>
            <p className="text-muted text-sm mb-4">
              Up-to-date inputs sourced from recognized providers — beyond the textbook&apos;s
              static examples.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {assumptions.map((a) => (
                <div
                  key={a.name}
                  className="flex items-baseline justify-between gap-3 border-b border-border py-2"
                >
                  <span className="text-muted text-sm">{a.name}</span>
                  <span className="font-mono tabular-nums font-semibold text-text">
                    {a.value}
                    {a.unit ? ` ${a.unit}` : ""}
                  </span>
                </div>
              ))}
            </div>
            {assumptions[0] && (
              <p className="text-xs text-muted mt-3">
                Source: {assumptions[0].source_name} · Retrieved{" "}
                {assumptions[0].source_retrieved_at.slice(0, 10)}
              </p>
            )}
          </div>
        </div>
      )}
    </>
  );
}
