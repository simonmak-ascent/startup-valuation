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
