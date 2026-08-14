import { chatCompletion } from "./deepseek";
import { buildSystemPrompt } from "./prompts";
import { extractSlugs, resolveCitations, type Citation } from "./citations";

export interface OrchestratedResponse {
  text: string;
  recommendations: Citation[];
  error?: string;
}

/**
 * Full advisor pipeline: recommend (DeepSeek) → resolve citations (registry).
 *
 * The model only recommends methods and explains rationale; it NEVER computes
 * numbers. Computed figures are produced by the calculator, which the client
 * reaches via the citation's slug deep-link. This keeps every number auditable
 * against the open-source Python library (AC-E2: AI never computes).
 */
export async function analyzeValuationOrchestrated(query: string): Promise<OrchestratedResponse> {
  try {
    const text = await chatCompletion([
      { role: "system", content: buildSystemPrompt() },
      { role: "user", content: query },
    ]);
    const recommendations = resolveCitations(extractSlugs(text));
    return { text, recommendations };
  } catch (e) {
    return { text: "", recommendations: [], error: (e as Error).message };
  }
}
