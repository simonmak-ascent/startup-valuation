import Image from "next/image";
import Link from "next/link";
import { LANDING_COPY, LOCALE_META, connectClients, hrefFor, locales, type Locale } from "@/lib/landing";
import { ConnectTabs } from "@/components/landing/ConnectTabs";

const TOOLS_URL = "https://www.ascent-partners.com/tools";
const TECH_URL = "https://www.ascent-partners.com/services/technology-advisory";
const CONTACT_URL = "https://www.ascent-partners.com/about#contact";
const DOCS_URL = "https://simonmak-ascent.github.io/startup-valuation/";
const REPO_URL = "https://github.com/simonmak-ascent/startup-valuation";

const HEADING = { fontFamily: "var(--font-family-heading)" } as const;

function LocaleSwitcher({ locale, label }: { locale: Locale; label: string }) {
  return (
    <nav aria-label={label} className="flex items-center gap-1">
      {locales.map((l) => (
        <Link
          key={l}
          href={hrefFor(l, "/")}
          hrefLang={LOCALE_META[l].htmlLang}
          className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold no-underline ${
            l === locale ? "border-brand text-brand" : "border-border text-muted"
          }`}
        >
          {LOCALE_META[l].label}
        </Link>
      ))}
    </nav>
  );
}

export function Landing({ locale }: { locale: Locale }) {
  const c = LANDING_COPY[locale];
  const clients = connectClients();

  return (
    <div className="flex w-full min-w-0 flex-col">
      <header data-hero className="relative h-[180px] w-full overflow-hidden bg-brand lg:h-[240px]">
        <Image src="/images/tool-startup-valuation.jpg" alt="" fill priority sizes="100vw" className="object-cover" />
        <div aria-hidden className="absolute inset-0 bg-gradient-to-r from-brand-dark/95 via-brand-dark/50 to-transparent" />
        <nav aria-label="Breadcrumb" className="absolute inset-x-0 top-1">
          <ol className="section flex flex-wrap gap-2 py-1 text-[12px]" style={{ paddingTop: 4, paddingBottom: 4 }}>
            <li><a className="text-white/90 no-underline hover:underline" href="https://www.ascent-partners.com/">{c.crumbHome}</a></li>
            <li><a className="text-white/90 no-underline hover:underline" href={TOOLS_URL}>{c.crumbTools}</a></li>
            <li className="text-white" aria-current="page">{c.name}</li>
          </ol>
        </nav>
        <div className="absolute inset-x-0 bottom-0">
          <h1 className="section pb-4 text-[clamp(1.75rem,5vw,3.25rem)] font-black leading-[1.05] text-white lg:pb-6" style={HEADING}>
            {c.name}
          </h1>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-[65.125rem] flex-col items-center gap-10 px-5 py-14 lg:py-16">
        <header className="flex w-full max-w-2xl flex-col items-center gap-4 text-center">
          <span className="rounded-full bg-brand/10 px-3 py-1 text-[12px] font-semibold uppercase tracking-wide text-brand">{c.type}</span>
          <p className="max-w-xl text-[18px] leading-relaxed text-muted">{c.value}</p>
          <p className="mt-1 border-s-2 border-gold ps-4 text-start text-[16px] italic text-text">{c.thesis}</p>
        </header>

        <dl className="grid w-full max-w-3xl grid-cols-2 gap-4 sm:grid-cols-4">
          {c.stats.map((s) => (
            <div key={s.label} className="flex flex-col gap-1 rounded-card border border-border bg-card p-4">
              <dt className="text-[14px] text-muted">{s.label}</dt>
              <dd className="text-[24px] font-bold text-brand" style={HEADING}>{s.value}</dd>
            </div>
          ))}
        </dl>

        <div className="flex w-full max-w-3xl flex-col gap-8">
          <section className="flex flex-col gap-3">
            <h2 className="text-[20px] font-bold text-brand" style={HEADING}>{c.capsHeading}</h2>
            <ul className="flex list-disc flex-col gap-2 ps-5">
              {c.capabilities.map((x) => (
                <li key={x} className="text-[16px] leading-relaxed text-text">{x}</li>
              ))}
            </ul>
          </section>

          <section className="flex flex-col gap-4">
            <h2 className="text-[20px] font-bold text-brand" style={HEADING}>{c.connectHeading}</h2>
            <p className="text-[16px] leading-relaxed text-text">{c.connectIntro}</p>
            <ConnectTabs clients={clients} copyLabel={c.copy} copiedLabel={c.copied} ariaLabel={c.connectHeading} />
          </section>

          <section className="flex flex-col gap-4">
            <h2 className="text-[20px] font-bold text-brand" style={HEADING}>{c.factsHeading}</h2>
            <dl className="flex flex-col gap-3">
              {c.facts.map((f) => (
                <div key={f.label} className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:gap-4">
                  <dt className="w-28 shrink-0 text-[14px] font-semibold uppercase tracking-wide text-text">{f.label}</dt>
                  <dd className="break-all text-[16px] text-muted">
                    {f.code ? <code className="rounded bg-card px-2 py-0.5 font-mono text-[14px]">{f.value}</code> : f.value}
                  </dd>
                </div>
              ))}
            </dl>
          </section>

          <section className="flex flex-col gap-4 rounded-card border border-border bg-card p-6">
            <h2 className="text-[18px] font-bold text-brand" style={HEADING}>{c.originHeading}</h2>
            <p className="text-[16px] leading-relaxed text-text">{c.originBody}</p>
            <div className="flex flex-wrap gap-4 text-[16px] font-semibold">
              <a className="text-brand no-underline hover:underline" href={TECH_URL}>{c.techLink}</a>
              <a className="text-brand no-underline hover:underline" href={CONTACT_URL}>{c.contact}</a>
            </div>
          </section>

          <div className="flex flex-wrap gap-3">
            <a href={DOCS_URL} className="rounded-button bg-brand px-6 py-2.5 text-[14px] font-semibold text-white no-underline transition-colors hover:bg-brand-dark">{c.docs}</a>
            <a href={REPO_URL} className="rounded-button border border-border px-6 py-2.5 text-[14px] font-semibold text-text no-underline transition-colors hover:bg-card">{c.source}</a>
          </div>

          <Link href={TOOLS_URL} className="text-[14px] font-semibold text-brand no-underline hover:underline">← {c.back}</Link>
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-[65.125rem] justify-center px-5 pb-8">
        <LocaleSwitcher locale={locale} label={c.langLabel} />
      </div>
    </div>
  );
}
