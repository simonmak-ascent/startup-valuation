import type { Metadata } from "next";
import { AIChat } from "@/components/AIChat";

export const metadata: Metadata = {
  title: "AI Valuation Advisor — Startup Valuation Engine",
  description:
    "Ask the AI valuation advisor which method applies to your startup. Recommendations cite textbook chapters and are verifiable in the open-source calculators.",
  alternates: {
    canonical: "https://startup-valuation.simonmak.com/ai-advisor",
  },
};

export default function AiAdvisorPage() {
  return (
    <div className="section max-w-[800px]">
      <h1 className="text-3xl font-bold text-text mb-2">AI Valuation Advisor</h1>
      <p className="text-muted mb-8">
        Describe your startup and the advisor will recommend the right valuation methods with
        textbook citations. The AI never computes — you verify every figure in the open-source
        calculator.
      </p>

      <AIChat />
    </div>
  );
}
