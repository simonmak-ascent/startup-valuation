import { getDb } from "../client";
import { TABLES, type AuditLog, type Step } from "../schema";

/**
 * The bare key of a SurrealDB record id, whatever shape it arrives in.
 *
 * `db.query` hands record-id fields back as `RecordId` instances, whose `toString()` is
 * `table:⟨key⟩` (the SDK quotes any key with a hyphen, e.g. a UUID). A caller may also pass
 * the raw key or the unquoted `table:key` form, so all three normalise to the same key —
 * `type::record()` must then rebuild exactly what the write path stored.
 */
export function recordKey(value: string): string {
  return value
    .replace(/^[A-Za-z_][A-Za-z0-9_]*:/, "")
    .replace(/^⟨/, "")
    .replace(/⟩$/, "");
}

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

  const vrId = recordKey(valuationRunId);

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
    inputs: JSON.stringify(inputs),
    result,
    steps: JSON.stringify(steps),
    formula_number: formulaNumber,
    chapter,
    library_version: libraryVersion,
  };

  if (userId) {
    clauses.push("user = type::record('user', $user_id)");
    bindings.user_id = recordKey(userId);
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

export async function getAuditLogForRun(valuationRunId: string, userId: string): Promise<AuditLog | null> {
  const db = await getDb();
  // `valuation_run` is a record id, not a string; SurrealDB 2.x does not coerce the two,
  // so the id has to be cast the same way createAuditLog writes it.
  const [result] = await db.query<[AuditLog[]]>(
    `SELECT * FROM ${TABLES.AUDIT_LOG}
     WHERE valuation_run = type::record('valuation_run', $vr_id)
       AND user = type::record('user', $user_id)`,
    { vr_id: recordKey(valuationRunId), user_id: recordKey(userId) },
  );
  return result[0] ?? null;
}

export async function getAuditLogsForUser(userId: string, limit = 50): Promise<AuditLog[]> {
  const db = await getDb();
  const rawId = recordKey(userId);
  const [result] = await db.query<[AuditLog[]]>(
    `SELECT * FROM ${TABLES.AUDIT_LOG} WHERE user = type::record('user', $userId) ORDER BY created_at DESC LIMIT $limit`,
    { userId: rawId, limit },
  );
  return result;
}
