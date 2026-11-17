import { NextResponse } from "next/server";
import { healthCheck } from "@/lib/db/client";
import pkg from "../../../../package.json";

export const dynamic = "force-dynamic";

export async function GET() {
  const db = await healthCheck();
  const connected = db.status === "connected";

  return NextResponse.json(
    {
      status: connected ? "ok" : "degraded",
      version: pkg.version,
      db_status: db.status,
    },
    { status: connected ? 200 : 503 },
  );
}
