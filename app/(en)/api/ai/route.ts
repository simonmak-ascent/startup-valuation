import { NextResponse } from "next/server";
import { analyzeValuationOrchestrated } from "@/lib/ai/orchestrator";
import { clientKey, rateLimit } from "@/lib/rate-limit";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const ip = clientKey(request);
  const rl = rateLimit(`ai:${ip}`, 10, 60_000);
  if (!rl.success) {
    return NextResponse.json(
      { error: "RATE_LIMITED", message: "Too many requests. Please try again later." },
      { status: 429, headers: { "Retry-After": String(rl.retryAfter ?? 60) } },
    );
  }

  let query: string;
  try {
    const body = (await request.json()) as { query?: string };
    query = body.query?.trim() ?? "";
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!query) {
    return NextResponse.json({ error: "Query is required" }, { status: 400 });
  }

  if (query.length > 2000) {
    return NextResponse.json({ error: "Query too long (max 2000 chars)" }, { status: 400 });
  }

  const result = await analyzeValuationOrchestrated(query);
  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: 502 });
  }

  return NextResponse.json({ text: result.text, recommendations: result.recommendations });
}
