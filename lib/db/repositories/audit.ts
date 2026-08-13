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

  const data: Record<string, unknown> = {
    valuation_run: valuationRunId,
    action: "calculate",
    method,
    inputs,
    result,
    steps,
    formula_number: formulaNumber,
    chapter,
    library_version: libraryVersion,
  };
  if (userId) data.user = userId;
  if (gitCommit) data.git_commit = gitCommit;
  if (userAgent) data.user_agent = userAgent;

  const [rows] = await db.query<[AuditLog[]]>(
    `CREATE ${TABLES.AUDIT_LOG} CONTENT $data RETURN AFTER`,
    { data },
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
