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
    version: "2026-08-13",
    sections: [
      {
        heading: "1. Acceptance of Terms",
        body: 'By accessing startup-valuation.simonmak.com (the "Service"), you agree to these Terms of Service. If you do not agree, do not use the Service.',
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
        body: "Creating an account is optional. You are responsible for maintaining the confidentiality of your credentials and for all activity under your account.",
      },
      {
        heading: "6. Paid Subscriptions",
        body: "Paid tiers (Pro, Enterprise) provide additional features such as audit-report export. Payments are processed by Stripe. Subscription terms, including cancellation, are described at checkout.",
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
    version: "2026-08-13",
    sections: [
      {
        heading: "1. Data We Collect",
        body: "We collect: (a) account information (email, name) if you create an account; (b) valuation inputs you submit to the calculators, stored in an audit log for traceability; (c) usage analytics (page views, calculator usage) via Vercel Analytics; and (d) error telemetry via Sentry.",
      },
      {
        heading: "2. How We Use Data",
        body: "Account data enables saved workspaces and audit-report export. Calculator inputs are stored to provide an auditable trace of every valuation. Analytics and telemetry help us improve reliability.",
      },
      {
        heading: "3. Storage",
        body: "Data is stored in SurrealDB (3.x), hosted on Surreal Cloud. Valuation runs are stored in an immutable audit log.",
      },
      {
        heading: "4. Data Minimization",
        body: "We collect only what is needed for the features we provide. We do not sell personal data. We do not engage in cross-site tracking of calculator inputs.",
      },
      {
        heading: "5. Analytics and Cookies",
        body: "We use Vercel Analytics (aggregate, privacy-respecting) and set a session cookie for authentication. See our Cookie Policy for details.",
      },
      {
        heading: "6. Your Rights",
        body: "Depending on your jurisdiction (including GDPR), you may request access to, correction of, or deletion of your personal data. Contact support@ascent-partners.com.",
      },
      {
        heading: "7. Third-Party Processors",
        body: "We use Stripe (payments), Vercel (hosting/analytics), Sentry (error monitoring), and Surreal Cloud (database). Each processes data only as necessary to provide the Service.",
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
    version: "2026-08-13",
    sections: [
      {
        heading: "1. Cookies We Use",
        body: 'We use a session cookie ("authjs.session-token") to keep you signed in across pages. This is an essential cookie required for authentication.',
      },
      {
        heading: "2. Analytics",
        body: "Vercel Analytics may set a cookie to distinguish unique visitors. It is aggregate and does not track you across unrelated websites.",
      },
      {
        heading: "3. Payment",
        body: "Stripe sets cookies during the checkout flow to process payments securely.",
      },
      {
        heading: "4. Managing Cookies",
        body: "You can block or delete cookies in your browser settings. Blocking the session cookie will prevent sign-in but will not affect the free calculators.",
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
