import { buildSystemPrompt } from "./prompts";

const DEEPSEEK_URL = "https://api.deepseek.com/chat/completions";
const MODEL = "deepseek-chat";

export interface AdvisorResponse {
  text: string;
  error?: string;
}

/**
 * DeepSeek LLM client — OpenAI-compatible chat completions. Temperature 0.1 for
 * financial-domain accuracy (the model recommends methods, never computes).
 */
export async function chatCompletion(
  messages: { role: "system" | "user" | "assistant"; content: string }[],
): Promise<string> {
  const apiKey = process.env.DEEPSEEK_API_KEY;
  if (!apiKey) {
    throw new Error("DEEPSEEK_API_KEY is not configured");
  }

  const res = await fetch(DEEPSEEK_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: MODEL,
      messages,
      temperature: 0.1,
      stream: false,
    }),
  });

  if (!res.ok) {
    const err = await res.text().catch(() => "");
    throw new Error(`DeepSeek API error ${res.status}: ${err.slice(0, 200)}`);
  }

  const data = (await res.json()) as {
    choices?: { message?: { content?: string } }[];
  };

  return data.choices?.[0]?.message?.content ?? "";
}

/** One-shot valuation advisor: recommend methods for a natural-language query. */
export async function analyzeValuation(query: string): Promise<AdvisorResponse> {
  try {
    const text = await chatCompletion([
      { role: "system", content: buildSystemPrompt() },
      { role: "user", content: query },
    ]);
    return { text };
  } catch (e) {
    return { text: "", error: (e as Error).message };
  }
}
