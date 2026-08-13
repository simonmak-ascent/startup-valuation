import { getDb } from "../client";
import { TABLES, type AuditLog, type Step } from "../schema";

export async function createAuditLog(
  valuationRunId: string,
  userId: string | undefined,
  method: string,
  inputs: Record<string, unknown>,
  result: number,
  steps: Step[],
  formulaNumber: string,
  chapter: string,
  libraryVersion: string,
  gitCommit?: string,
  userAgent?: string,
): Promise<AuditLog> {
  const db = await getDb();

  // Extract the raw UUID (valuation_run:<uuid> → <uuid>).
  const vrId = valuationRunId.startsWith("valuation_run:")
    ? valuationRunId.slice("valuation_run:".length)
    : valuationRunId;

  const clauses = [
    "valuation_run = type::record('valuation_run', $vr_id)",
    "action = $action",
    "method = $method",
    "inputs = $inputs",
    "result = $result",
    "steps = $steps",
    "formula_number = $formula_number",
    "chapter = $chapter",
    "library_version = $library_version",
  ];
  const bindings: Record<string, unknown> = {
    vr_id: vrId,
    action: "calculate",
    method,
    inputs,
    result,
    steps,
    formula_number: formulaNumber,
    chapter,
    library_version: libraryVersion,
  };

  if (userId) {
    clauses.push("user = type::record('user', $user_id)");
    bindings.user_id = userId.startsWith("user:") ? userId.slice(5) : userId;
  }
  if (gitCommit) {
    clauses.push("git_commit = $git_commit");
    bindings.git_commit = gitCommit;
  }
  if (userAgent) {
    clauses.push("user_agent = $user_agent");
    bindings.user_agent = userAgent;
  }

  const [rows] = await db.query<[AuditLog[]]>(
    `CREATE ${TABLES.AUDIT_LOG} SET ${clauses.join(", ")} RETURN AFTER`,
    bindings,
  );
  const created = rows[0];
  if (!created) {
    throw new Error("Failed to create audit log entry");
  }
  return created as unknown as AuditLog;
}

export async function getAuditLogForRun(valuationRunId: string): Promise<AuditLog | null> {
  const db = await getDb();
  const [result] = await db.query<[AuditLog[]]>(
    `SELECT * FROM ${TABLES.AUDIT_LOG} WHERE valuation_run = $valuationRunId`,
    { valuationRunId },
  );
  return result[0] ?? null;
}

export async function getAuditLogsForUser(userId: string, limit = 50): Promise<AuditLog[]> {
  const db = await getDb();
  const [result] = await db.query<[AuditLog[]]>(
    `SELECT * FROM ${TABLES.AUDIT_LOG} WHERE user = $userId ORDER BY created_at DESC LIMIT $limit`,
    { userId, limit },
  );
  return result;
}
