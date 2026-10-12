import { NextResponse } from "next/server";
import { analyzeValuationOrchestrated } from "@/lib/ai/orchestrator";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
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
