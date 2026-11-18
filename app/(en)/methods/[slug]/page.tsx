import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { CalculatorPage } from "@/components/CalculatorPage";
import { getMethodBySlug, getAllMethods } from "@/lib/methods";
import { buildHowToJsonLd, buildBreadcrumbJsonLd, buildFaqJsonLd } from "@/lib/seo";

interface MethodPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  return getAllMethods().map((m) => ({ slug: m.slug }));
}

// The page is generated from the method registry, which changes only when the generated
// lib/methods data is regenerated, so an hourly revalidation is enough and keeps the build fast.
export const revalidate = 3600;

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
      url: `https://startup-valuation.ascent-partners.com/methods/${slug}`,
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: `${method.name} — Startup Valuation Calculator`,
      description: method.description,
    },
    alternates: {
      canonical: `https://startup-valuation.ascent-partners.com/methods/${slug}`,
    },
  };
}

export default async function MethodPage({ params }: MethodPageProps) {
  const { slug } = await params;
  const method = getMethodBySlug(slug);

  if (!method) {
    notFound();
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
    </>
  );
}
