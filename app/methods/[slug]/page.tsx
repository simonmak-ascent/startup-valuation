import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { CalculatorPage } from "@/components/CalculatorPage";
import { getMethodBySlug, getAllMethods } from "@/lib/methods";

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

  return <CalculatorPage slug={slug} />;
}
