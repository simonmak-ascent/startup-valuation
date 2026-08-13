import { NextResponse } from "next/server";
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
import { auth } from "@/lib/auth/config";
import { getAuditLogForRun } from "@/lib/db/repositories/audit";
import { getSubscriptionForUser } from "@/lib/db/repositories/billing";

export const dynamic = "force-dynamic";

function parseJsonSafe(v: unknown): Record<string, unknown> {
  if (typeof v === "object" && v !== null) return v as Record<string, unknown>;
  if (typeof v === "string") {
    try {
      return JSON.parse(v) as Record<string, unknown>;
    } catch {
      return {};
    }
  }
  return {};
}

function parseStepsSafe(v: unknown): { label: string; value: number }[] {
  const parsed = parseJsonSafe(v);
  if (Array.isArray(parsed)) {
    return parsed
      .filter((s): s is { label: string; value: number } => typeof s === "object" && s !== null)
      .map((s) => ({
        label: String((s as { label?: unknown }).label ?? ""),
        value: Number((s as { value?: unknown }).value ?? 0),
      }));
  }
  return [];
}

async function buildReportPdf(run: {
  method: string;
  inputs: unknown;
  result: number;
  steps: unknown;
  formula_number: string;
  chapter: string;
  library_version: string;
  created_at?: string;
  id: string;
}): Promise<Uint8Array> {
  const pdf = await PDFDocument.create();
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);
  const page = pdf.addPage([595, 842]);
  const { width } = page.getSize();

  let y = 800;
  const line = (text: string, size = 11, f = font, indent = 50) => {
    page.drawText(text, {
      x: indent,
      y,
      size,
      font: f,
      color: size > 12 ? rgb(0, 0.514, 0.671) : rgb(0.12, 0.16, 0.23),
    });
    y -= size + 6;
    if (y < 60) {
      y = 800;
      pdf.addPage([595, 842]);
    }
  };

  line("Startup Valuation Engine — Audit Report", 18, bold);
  line("Generated: " + new Date().toISOString(), 10);
  line(" ");
  line("Method: " + run.method, 13, bold);
  line("Result: $" + run.result.toLocaleString("en-US", { maximumFractionDigits: 2 }), 13, bold);
  line(" ");
  line("Formula: " + run.formula_number, 11);
  line("Chapter: " + run.chapter, 11);
  line("Library version: " + run.library_version, 11);
  line("Audit ID: " + run.id, 11);
  if (run.created_at) line("Timestamp: " + run.created_at, 11);
  line(" ");
  line("Inputs", 13, bold);
  const inputs = parseJsonSafe(run.inputs);
  for (const [k, v] of Object.entries(inputs)) {
    line(`${k}: ${JSON.stringify(v)}`, 10);
  }
  line(" ");
  line("Step-by-step derivation", 13, bold);
  const steps = parseStepsSafe(run.steps);
  if (steps.length === 0) {
    line("(no intermediate steps recorded)", 10);
  } else {
    for (const s of steps) {
      line(`${s.label}: ${s.value}`, 10);
    }
  }
  line(" ");
  line("All formulas are open source (MIT) and traceable to the Startup Valuation", 9);
  line("textbook (Mak, 2025). Verify at startup-valuation.simonmak.com.", 9);

  return pdf.save();
}

export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "UNAUTHORIZED" }, { status: 401 });
  }

  let subscription = null;
  try {
    subscription = await getSubscriptionForUser(session.user.id);
  } catch {
    subscription = null;
  }
  const isPro = subscription?.tier === "pro" || subscription?.tier === "enterprise";
  if (!isPro) {
    return NextResponse.json({ error: "UPGRADE_REQUIRED" }, { status: 402 });
  }

  const { searchParams } = new URL(request.url);
  const runId = searchParams.get("run_id");
  if (!runId) {
    return NextResponse.json({ error: "NOT_FOUND" }, { status: 404 });
  }

  let run;
  try {
    run = await getAuditLogForRun(runId);
  } catch {
    return NextResponse.json({ error: "DB_UNAVAILABLE" }, { status: 503 });
  }
  if (!run) {
    return NextResponse.json({ error: "NOT_FOUND" }, { status: 404 });
  }

  const pdfBytes = await buildReportPdf({
    method: run.method,
    inputs: run.inputs,
    result: run.result,
    steps: run.steps,
    formula_number: run.formula_number,
    chapter: run.chapter,
    library_version: run.library_version,
    created_at: run.created_at,
    id: run.id,
  });

  return new NextResponse(pdfBytes as unknown as BodyInit, {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="valuation-report-${runId.replace(/\W/g, "")}.pdf"`,
    },
  });
}
