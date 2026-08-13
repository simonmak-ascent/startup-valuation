import { NextResponse } from "next/server";
import { createAuditLog } from "@/lib/db/repositories/audit";
import { AuditRequestSchema } from "@/lib/db/validation";

export async function POST(request: Request) {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "VALIDATION_ERROR", message: "Invalid JSON body" },
      { status: 400 },
    );
  }

  const parsed = AuditRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      {
        error: "VALIDATION_ERROR",
        message: "Invalid audit request",
        details: parsed.error.flatten().fieldErrors,
      },
      { status: 400 },
    );
  }

  const { method, inputs, result, steps, formula_number, chapter, library_version, git_commit } =
    parsed.data;

  try {
    const valuationRunId = `valuation_run:${crypto.randomUUID()}`;
    const audit = await createAuditLog(
      valuationRunId,
      undefined,
      method,
      inputs,
      result,
      steps,
      formula_number,
      chapter,
      library_version,
      git_commit || undefined,
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
