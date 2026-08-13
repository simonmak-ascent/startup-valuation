import { NextResponse } from "next/server";
import { createAuditLog } from "@/lib/db/repositories/audit";

export async function POST(request: Request) {
  let body: {
    method?: string;
    inputs?: Record<string, unknown>;
    result?: number;
    steps?: { label: string; value: number; formula: string }[];
    formula_number?: string;
    chapter?: string;
    library_version?: string;
    git_commit?: string;
  };

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "VALIDATION_ERROR", message: "Invalid JSON body" },
      { status: 400 },
    );
  }

  if (!body.method || body.result === undefined) {
    return NextResponse.json(
      { error: "VALIDATION_ERROR", message: "method and result are required" },
      { status: 400 },
    );
  }

  try {
    const valuationRunId = `valuation_run:${crypto.randomUUID()}`;
    const audit = await createAuditLog(
      valuationRunId,
      undefined,
      body.method,
      body.inputs ?? {},
      body.result,
      body.steps ?? [],
      body.formula_number ?? "",
      body.chapter ?? "",
      body.library_version ?? "",
      body.git_commit ?? "",
      request.headers.get("user-agent") ?? undefined,
    );

    return NextResponse.json({
      audit_id: audit.id,
      audit_status: "logged",
    });
  } catch (error) {
    return NextResponse.json({
      audit_status: "failed",
      reason: error instanceof Error ? error.message : "Database unavailable",
    });
  }
}
