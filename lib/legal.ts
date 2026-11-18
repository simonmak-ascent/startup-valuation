export interface LegalDoc {
  slug: string;
  title: string;
  version: string;
  sections: { heading: string; body: string }[];
}

export const LEGAL_DOCS: LegalDoc[] = [
  {
    slug: "terms",
    title: "Terms of Service",
    version: "2026-11-18",
    sections: [
      {
        heading: "1. Acceptance of Terms",
        body: 'By accessing startup-valuation.ascent-partners.com (the "Service"), you agree to these Terms of Service. If you do not agree, do not use the Service.',
      },
      {
        heading: "2. The Service",
        body: "The Service provides startup valuation calculators, an MCP API, and educational content. The 27 calculators and the MCP API are provided free of charge and are open source (MIT licensed).",
      },
      {
        heading: "3. No Financial Advice",
        body: "The Service provides valuation calculations for educational and informational purposes only. It does not constitute financial, investment, legal, or tax advice. Consult a qualified professional before making investment decisions.",
      },
      {
        heading: "4. Accuracy and Liability",
        body: 'All formulas are implemented from the Startup Valuation textbook (Mak, 2025) and are open source and auditable. However, the Service is provided "as is" without warranty of any kind. We are not liable for decisions made based on its output.',
      },
      {
        heading: "5. User Accounts",
        body: "There are no accounts. The site has no sign-in, and nothing you enter is associated with an identity.",
      },
      {
        heading: "6. Paid Subscriptions",
        body: "The service is free and has no paid tiers, no checkout and no payment processing.",
      },
      {
        heading: "7. Intellectual Property",
        body: "The valuation library is open source (MIT license). The Service's design, branding, and content are owned by Ascent Partners unless otherwise noted.",
      },
      {
        heading: "8. Acceptable Use",
        body: "You may not abuse the Service, attempt to disrupt it, scrape content for unauthorized commercial use, or access it in violation of applicable law.",
      },
      {
        heading: "9. Termination",
        body: "We may suspend or terminate access for violations of these Terms. You may stop using the Service at any time.",
      },
      {
        heading: "10. Changes to These Terms",
        body: 'We may update these Terms. Material changes will be reflected in the version number and "Last updated" date. Continued use constitutes acceptance.',
      },
    ],
  },
  {
    slug: "privacy",
    title: "Privacy Policy",
    version: "2026-11-18",
    sections: [
      {
        heading: "1. Data We Collect",
        body: "We collect: (a) valuation inputs you submit to the calculators, sent to the calculation service to produce a result and not stored by it; and (b) error telemetry via Sentry. There are no accounts and no analytics tied to an identity.",
      },
      {
        heading: "2. How We Use Data",
        body: "There are no accounts and no saved workspaces. Calculator inputs are sent to the calculation service to produce a result and are not stored. Error telemetry helps us improve reliability.",
      },
      {
        heading: "3. Storage",
        body: "There is no database. Calculations are computed per request and are not retained; the public comparables pages read live market data from Yahoo Finance.",
      },
      {
        heading: "4. Data Minimization",
        body: "We collect only what is needed for the features we provide. We do not sell personal data. We do not engage in cross-site tracking of calculator inputs.",
      },
      {
        heading: "5. Analytics and Cookies",
        body: "We run no analytics and set no cookies. See our Cookie Policy for details.",
      },
      {
        heading: "6. Your Rights",
        body: "Depending on your jurisdiction (including GDPR), you may request access to, correction of, or deletion of your personal data. Contact support@ascent-partners.com.",
      },
      {
        heading: "7. Third-Party Processors",
        body: "We use Yahoo Finance (market data), GitHub (the open-source badge: your browser asks their API for the repository's star count) and Sentry (error monitoring). Each processes data only as necessary to provide the Service.",
      },
      {
        heading: "8. Changes to This Policy",
        body: "We may update this policy. Material changes are reflected in the version number and date.",
      },
    ],
  },
  {
    slug: "cookies",
    title: "Cookie Policy",
    version: "2026-11-18",
    sections: [
      {
        heading: "1. Cookies We Use",
        body: "We set no session cookie. There is no sign-in, so there is nothing to keep you signed in to.",
      },
      {
        heading: "2. Analytics",
        body: "No analytics cookie is set, because no analytics script runs. ",
      },
      {
        heading: "3. Payment",
        body: "No third party sets a cookie during a checkout, because there is no checkout.",
      },
      {
        heading: "4. Managing Cookies",
        body: "You can block or delete cookies in your browser settings. There is no session cookie to block, and nothing here affects the free calculators.",
      },
      {
        heading: "5. Changes",
        body: "We may update this policy. Material changes are reflected in the version number and date.",
      },
    ],
  },
];

export function getLegalDoc(slug: string): LegalDoc | undefined {
  return LEGAL_DOCS.find((d) => d.slug === slug);
}
