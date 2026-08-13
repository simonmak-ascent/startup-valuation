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

  const auditRecord = {
    valuation_run: valuationRunId,
    user: userId ?? null,
    action: "calculate",
    method,
    inputs,
    result,
    steps,
    formula_number: formulaNumber,
    chapter,
    library_version: libraryVersion,
    git_commit: gitCommit ?? null,
    user_agent: userAgent ?? null,
  };

  const [rows] = await db.query<[AuditLog[]]>(
    `CREATE ${TABLES.AUDIT_LOG} CONTENT $data RETURN AFTER`,
    { data: auditRecord },
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
