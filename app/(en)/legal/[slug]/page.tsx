import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getLegalDoc, LEGAL_DOCS } from "@/lib/legal";

interface LegalPageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return LEGAL_DOCS.map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({ params }: LegalPageProps): Promise<Metadata> {
  const { slug } = await params;
  const doc = getLegalDoc(slug);
  if (!doc) return {};
  return { title: `${doc.title} — Startup Valuation Engine` };
}

export default async function LegalPage({ params }: LegalPageProps) {
  const { slug } = await params;
  const doc = getLegalDoc(slug);

  if (!doc) {
    notFound();
  }

  return (
    <div className="section max-w-[760px]">
      <h1 className="text-3xl font-bold text-text mb-2">{doc.title}</h1>
      <p className="text-muted text-sm mb-8">
        Version {doc.version} · Last updated {doc.version}
      </p>
      {doc.sections.map((s) => (
        <div key={s.heading} className="mb-6">
          <h2 className="text-lg font-semibold text-text mb-2">{s.heading}</h2>
          <p className="text-muted leading-relaxed">{s.body}</p>
        </div>
      ))}
    </div>
  );
}
