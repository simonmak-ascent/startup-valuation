import type { MethodConfig } from "@/lib/valuation/types";

const BASE_URL = "https://startup-valuation.simonmak.com";

/**
 * Build a JSON-LD `HowTo` structured-data object for a valuation calculator.
 * Enables rich-result eligibility (step-by-step "how to value a startup" cards)
 * in Google Search.
 */
export function buildHowToJsonLd(config: MethodConfig): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: `How to value a startup: ${config.name}`,
    description: config.description,
    url: `${BASE_URL}/methods/${config.slug}`,
    totalTime: "PT5M",
    supply: {
      "@type": "HowToSupply",
      name: "Startup Valuation Engine",
      url: BASE_URL,
    },
    tool: {
      "@type": "HowToTool",
      name: `${config.name} Calculator`,
      url: `${BASE_URL}/methods/${config.slug}`,
    },
    step: config.inputs.map((input) => ({
      "@type": "HowToStep",
      name: input.label,
      text: input.description ?? `Enter the ${input.label.toLowerCase()}.`,
    })),
  };
}

/** Build a JSON-LD `SoftwareApplication` object for the landing page. */
export function buildSoftwareApplicationJsonLd(): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "Startup Valuation Engine",
    applicationCategory: "FinanceApplication",
    operatingSystem: "Cross-platform",
    description:
      "Open-source startup valuation platform with 27+ interactive calculators, 80+ formulas, and full mathematical derivations.",
    url: BASE_URL,
    author: { "@type": "Person", name: "Simon Mak" },
    license: "https://opensource.org/licenses/MIT",
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };
}

/** Build a JSON-LD `BreadcrumbList` for a method page. */
export function buildBreadcrumbJsonLd(config: MethodConfig): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: BASE_URL },
      { "@type": "ListItem", position: 2, name: "Methods", item: `${BASE_URL}/#methods` },
      {
        "@type": "ListItem",
        position: 3,
        name: config.name,
        item: `${BASE_URL}/methods/${config.slug}`,
      },
    ],
  };
}

/** Build a JSON-LD `FAQPage` for a method page (top valuation questions). */
export function buildFaqJsonLd(config: MethodConfig): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: `What is the ${config.name}?`,
        acceptedAnswer: {
          "@type": "Answer",
          text: config.description,
        },
      },
      {
        "@type": "Question",
        name: `How accurate is the ${config.name}?`,
        acceptedAnswer: {
          "@type": "Answer",
          text: `The ${config.name} is implemented from the Startup Valuation textbook (${config.textbookChapter}) and is open source and auditable. All formulas are traceable to the source.`,
        },
      },
      {
        "@type": "Question",
        name: `Is the ${config.name} calculator free?`,
        acceptedAnswer: {
          "@type": "Answer",
          text: "Yes. All 27 calculators and the MCP API are free and open source (MIT licensed).",
        },
      },
    ],
  };
}
