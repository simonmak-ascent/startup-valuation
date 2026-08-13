import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Support — Startup Valuation Engine",
  description: "Get help with the Startup Valuation Engine.",
  alternates: {
    canonical: "https://startup-valuation.simonmak.com/support",
  },
};

export default function SupportPage() {
  return (
    <div className="section max-w-[720px]">
      <h1 className="text-3xl font-bold text-text mb-2">Support</h1>
      <p className="text-muted mb-8">
        Questions about the calculators, the API, or your subscription? We&apos;re here to help.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="text-lg font-semibold text-text mb-2">Email</h2>
          <p className="text-muted text-sm">
            <a href="mailto:support@ascent-partners.com" className="text-brand hover:underline">
              support@ascent-partners.com
            </a>
          </p>
          <p className="text-muted text-xs mt-2">Response within 1–2 business days.</p>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold text-text mb-2">Documentation</h2>
          <p className="text-muted text-sm">
            See the{" "}
            <a
              href="https://simonplmak-cloud.github.io/startup-valuation"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand hover:underline"
            >
              API reference
            </a>{" "}
            and{" "}
            <a
              href="https://github.com/simonplmak-cloud/startup-valuation/wiki"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand hover:underline"
            >
              theory wiki
            </a>
            .
          </p>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold text-text mb-2">API &amp; SDK</h2>
          <p className="text-muted text-sm">
            Test the API in the{" "}
            <a href="/api/playground" className="text-brand hover:underline">
              playground
            </a>{" "}
            or use the{" "}
            <a
              href="https://github.com/simonplmak-cloud/startup-valuation"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand hover:underline"
            >
              TypeScript SDK
            </a>
            .
          </p>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold text-text mb-2">Billing</h2>
          <p className="text-muted text-sm">
            Payments are processed by Stripe. For billing issues, contact{" "}
            <a href="mailto:support@ascent-partners.com" className="text-brand hover:underline">
              support@ascent-partners.com
            </a>
            .
          </p>
        </div>
      </div>
    </div>
  );
}
