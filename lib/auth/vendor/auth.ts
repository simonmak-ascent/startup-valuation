import bcrypt from "bcryptjs";
import { randomBytes } from "node:crypto";
import { getDb } from "./client";
import type { CreateUserInput, SurrealAccount, SurrealSession, SurrealUser } from "./types";

const BCRYPT_ROUNDS = 10;

/**
 * Convert a SurrealDB record id (string or `RecordId` instance) to a plain
 * `table:id` string. `RecordId.toString()` yields the canonical `table:id` form.
 */
function toRecordIdString(id: unknown, table: string): string {
  const str = typeof id === "string" ? id : String(id);
  return str.startsWith(`${table}:`) ? str : `${table}:${str}`;
}

/** Strip the `table:` prefix, returning just the raw id portion. */
function rawId(id: string, table: string): string {
  const clean = String(id);
  return clean.startsWith(`${table}:`) ? clean.slice(table.length + 1) : clean;
}

function generateId(): string {
  return randomBytes(12).toString("hex");
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, BCRYPT_ROUNDS);
}

export async function validatePassword(user: SurrealUser, password: string): Promise<boolean> {
  if (!user.password) return false;
  return bcrypt.compare(password, user.password);
}

// -----------------------------------------------------------------------------
// User operations
// -----------------------------------------------------------------------------

export async function findUserByEmail(email: string): Promise<SurrealUser | null> {
  const db = await getDb();
  const [rows] = await db.query<[SurrealUser[]]>(
    `SELECT * FROM user WHERE email = $email LIMIT 1`,
    { email },
  );
  const user = rows[0] ?? null;
  if (user) user.id = toRecordIdString(user.id, "user");
  return user;
}

export async function findUserById(id: string): Promise<SurrealUser | null> {
  const db = await getDb();
  const [rows] = await db.query<[SurrealUser[]]>(`SELECT * FROM type::thing("user", $id)`, {
    id: rawId(id, "user"),
  });
  const user = rows[0] ?? null;
  if (user) user.id = toRecordIdString(user.id, "user");
  return user;
}

export async function createUser(data: CreateUserInput): Promise<SurrealUser> {
  const db = await getDb();
  const id = generateId();
  const hashedPassword = data.password ? await hashPassword(data.password) : undefined;

  const params: Record<string, unknown> = {
    id,
    email: data.email,
    role: data.role ?? "user",
  };
  if (data.name) params.name = data.name;
  if (data.image) params.image = data.image;
  if (hashedPassword) params.password = hashedPassword;

  const nameClause = data.name ? "name = $name" : "name = NONE";
  const imageClause = data.image ? "image = $image" : "image = NONE";
  const passwordClause = hashedPassword ? "password = $password" : "password = NONE";

  const [rows] = await db.query<[SurrealUser[]]>(
    `CREATE type::thing("user", $id) SET
      email = $email,
      ${nameClause},
      ${imageClause},
      ${passwordClause},
      role = $role,
      emailVerified = NONE,
      resetToken = NONE,
      resetTokenExpiry = NONE,
      createdAt = time::now(),
      updatedAt = time::now()
    RETURN AFTER`,
    params,
  );

  const user = rows[0]!;
  user.id = toRecordIdString(user.id, "user");
  return user;
}

export async function updateUser(id: string, data: Partial<SurrealUser>): Promise<SurrealUser> {
  const db = await getDb();
  const clauses: string[] = ["updatedAt = time::now()"];
  const params: Record<string, unknown> = { id: rawId(id, "user") };

  for (const [key, value] of Object.entries(data)) {
    if (value === undefined) continue;
    if (key === "id" || key === "createdAt" || key === "updatedAt") continue;

    if (key === "password") {
      const pwd = String(value);
      const hashed = pwd.startsWith("$2") ? pwd : await hashPassword(pwd);
      clauses.push("password = $password");
      params.password = hashed;
    } else if (value === null) {
      clauses.push(`${key} = NONE`);
    } else {
      clauses.push(`${key} = $${key}`);
      params[key] = value;
    }
  }

  const [rows] = await db.query<[SurrealUser[]]>(
    `UPDATE type::thing("user", $id) SET ${clauses.join(", ")} RETURN AFTER`,
    params,
  );

  const user = rows[0]!;
  user.id = toRecordIdString(user.id, "user");
  return user;
}

export async function deleteUser(id: string): Promise<void> {
  const db = await getDb();
  const rid = rawId(id, "user");
  await db.query(`DELETE account WHERE userId CONTAINS $id`, { id: rid });
  await db.query(`DELETE session WHERE userId CONTAINS $id`, { id: rid });
  await db.query(`DELETE type::thing("user", $id)`, { id: rid });
}

// -----------------------------------------------------------------------------
// Account operations (OAuth links)
// -----------------------------------------------------------------------------

export async function findAccountByProvider(
  provider: string,
  providerAccountId: string,
): Promise<SurrealAccount | null> {
  const db = await getDb();
  const [rows] = await db.query<[SurrealAccount[]]>(
    `SELECT * FROM account WHERE provider = $provider AND providerAccountId = $providerAccountId LIMIT 1`,
    { provider, providerAccountId },
  );
  return rows[0] ?? null;
}

export async function createAccount(data: Omit<SurrealAccount, "id">): Promise<SurrealAccount> {
  const db = await getDb();
  const id = generateId();
  const [rows] = await db.query<[SurrealAccount[]]>(
    `CREATE type::thing("account", $id) CONTENT $data RETURN AFTER`,
    { id, data },
  );
  return rows[0]!;
}

export async function deleteAccountsByUserId(userId: string): Promise<void> {
  const db = await getDb();
  const rid = rawId(userId, "user");
  await db.query(`DELETE account WHERE userId = $userId OR userId = user:$rawId`, {
    userId,
    rawId: rid,
  });
}

// -----------------------------------------------------------------------------
// Session operations
// -----------------------------------------------------------------------------

export async function findSessionByToken(sessionToken: string): Promise<SurrealSession | null> {
  const db = await getDb();
  const [rows] = await db.query<[SurrealSession[]]>(
    `SELECT * FROM session WHERE sessionToken = $sessionToken LIMIT 1`,
    { sessionToken },
  );
  return rows[0] ?? null;
}

export async function createSession(data: {
  sessionToken: string;
  userId: string;
  expires: Date;
}): Promise<SurrealSession> {
  const db = await getDb();
  const id = generateId();
  const [rows] = await db.query<[SurrealSession[]]>(
    `CREATE type::thing("session", $id) CONTENT $data RETURN AFTER`,
    {
      id,
      data: {
        sessionToken: data.sessionToken,
        userId: data.userId,
        expires: data.expires.toISOString(),
      },
    },
  );
  return rows[0]!;
}

export async function deleteSession(sessionToken: string): Promise<void> {
  const db = await getDb();
  await db.query(`DELETE session WHERE sessionToken = $sessionToken`, {
    sessionToken,
  });
}

export async function deleteSessionsByUserId(userId: string): Promise<void> {
  const db = await getDb();
  const rid = rawId(userId, "user");
  await db.query(`DELETE session WHERE userId = $userId OR userId = user:$rawId`, {
    userId,
    rawId: rid,
  });
}

// -----------------------------------------------------------------------------
// Password reset operations
// -----------------------------------------------------------------------------

export async function createPasswordResetToken(email: string): Promise<string | null> {
  const user = await findUserByEmail(email);
  if (!user) return null;

  const token = randomBytes(32).toString("hex");
  const expiry = new Date(Date.now() + 3600000);

  const db = await getDb();
  await db.query(
    `UPDATE type::thing("user", $id) SET resetToken = $token, resetTokenExpiry = $expiry RETURN AFTER`,
    { id: rawId(user.id, "user"), token, expiry },
  );

  return token;
}

export async function findUserByResetToken(token: string): Promise<SurrealUser | null> {
  const db = await getDb();
  const [rows] = await db.query<[SurrealUser[]]>(
    `SELECT * FROM user WHERE resetToken = $token AND resetTokenExpiry > time::now() LIMIT 1`,
    { token },
  );
  const user = rows[0] ?? null;
  if (user) user.id = toRecordIdString(user.id, "user");
  return user;
}

export async function resetPassword(token: string, newPassword: string): Promise<boolean> {
  const user = await findUserByResetToken(token);
  if (!user) return false;

  const hashedPassword = await hashPassword(newPassword);
  const db = await getDb();
  await db.query(
    `UPDATE type::thing("user", $id) SET password = $password, resetToken = NONE, resetTokenExpiry = NONE, updatedAt = time::now()`,
    { id: rawId(user.id, "user"), password: hashedPassword },
  );

  try {
    await deleteSessionsByUserId(user.id);
  } catch {
    // Session revocation must not roll back the password change.
  }

  return true;
}

export async function getUserCount(): Promise<number> {
  const db = await getDb();
  const [rows] = await db.query<[{ count: number }[]]>(`SELECT count() FROM user GROUP ALL`);
  return rows[0]?.count ?? 0;
}

export async function getAdminUsers(): Promise<SurrealUser[]> {
  const db = await getDb();
  const [rows] = await db.query<[SurrealUser[]]>(
    `SELECT * FROM user WHERE role = 'admin' ORDER BY createdAt`,
  );
  return rows.map((u) => ({ ...u, id: toRecordIdString(u.id, "user") }));
}
