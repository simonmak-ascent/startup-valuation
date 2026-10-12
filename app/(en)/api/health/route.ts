import { NextResponse } from "next/server";
import { healthCheck } from "@/lib/db/client";

export const dynamic = "force-dynamic";

export async function GET() {
  const db = await healthCheck();

  return NextResponse.json({
    status: db.status === "connected" ? "ok" : "degraded",
    version: "1.0.2",
    tools: 46,
    db_status: db.status,
  });
}
