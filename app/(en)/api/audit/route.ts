import { NextResponse } from "next/server";
import { createAuditLog } from "@/lib/db/repositories/audit";
import { AuditRequestSchema } from "@/lib/db/validation";
import { rateLimit } from "@/lib/rate-limit";
import { auth } from "@/lib/auth/config";

export async function POST(request: Request) {
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const rl = rateLimit(`audit:${ip}`, 60, 60_000);
  if (!rl.success) {
    return NextResponse.json(
      { error: "RATE_LIMITED", message: "Too many requests. Please try again later." },
      { status: 429, headers: { "Retry-After": String(rl.retryAfter ?? 60) } },
    );
  }

  const session = await auth().catch(() => null);
  const userId = session?.user?.id ? `user:${session.user.id}` : undefined;

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
      userId,
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
