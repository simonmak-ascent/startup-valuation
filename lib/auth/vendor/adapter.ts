import type {
  Adapter,
  AdapterAccount,
  AdapterSession,
  AdapterUser,
  VerificationToken,
} from "@auth/core/adapters";
import { randomBytes } from "node:crypto";
import { getDb } from "./client";

function generateId(): string {
  return randomBytes(12).toString("hex");
}

function rawId(id: string, table: string): string {
  return id.startsWith(`${table}:`) ? id.slice(table.length + 1) : id;
}

type DbRow = Record<string, unknown>;

function toAdapterUser(row: DbRow): AdapterUser {
  const idStr = typeof row.id === "string" ? row.id : String(row.id);
  const user: AdapterUser = {
    id: rawId(idStr, "user"),
    email: (row.email as string) ?? "",
    name: (row.name as string | null) ?? null,
    image: (row.image as string | null) ?? null,
    emailVerified: row.emailVerified ? new Date(row.emailVerified as string) : null,
  };
  (user as AdapterUser & { role: string }).role = (row.role as string) ?? "user";
  return user;
}

function toAdapterSession(row: DbRow): AdapterSession {
  const userId = row.userId as string;
  return {
    sessionToken: row.sessionToken as string,
    userId: rawId(String(userId ?? ""), "user"),
    expires: new Date(row.expires as string),
  };
}

export function SurrealDBAdapter(): Adapter {
  return {
    // --- User -----------------------------------------------------------
    async createUser(user) {
      const db = await getDb();
      const id = generateId();

      const nameClause = user.name ? "name = $name" : "name = NONE";
      const imageClause = user.image ? "image = $image" : "image = NONE";
      const emailVerifiedClause = user.emailVerified
        ? "emailVerified = $emailVerified"
        : "emailVerified = NONE";

      const params: Record<string, unknown> = { id, email: user.email };
      if (user.name) params.name = user.name;
      if (user.image) params.image = user.image;
      if (user.emailVerified) params.emailVerified = user.emailVerified.toISOString();

      const [rows] = await db.query<[DbRow[]]>(
        `CREATE type::thing("user", $id) SET
          email = $email,
          ${nameClause},
          ${imageClause},
          ${emailVerifiedClause},
          role = 'user',
          password = NONE,
          resetToken = NONE,
          resetTokenExpiry = NONE,
          createdAt = time::now(),
          updatedAt = time::now()
        RETURN AFTER`,
        params,
      );

      return toAdapterUser(rows[0]!);
    },

    async getUser(id) {
      const db = await getDb();
      const [rows] = await db.query<[DbRow[]]>(`SELECT * FROM type::thing("user", $id)`, {
        id: rawId(id, "user"),
      });
      const row = rows[0];
      return row ? toAdapterUser(row) : null;
    },

    async getUserByEmail(email) {
      const db = await getDb();
      const [rows] = await db.query<[DbRow[]]>(`SELECT * FROM user WHERE email = $email LIMIT 1`, {
        email,
      });
      const row = rows[0];
      return row ? toAdapterUser(row) : null;
    },

    async getUserByAccount({ providerAccountId, provider }) {
      const db = await getDb();
      const [acctRows] = await db.query<[DbRow[]]>(
        `SELECT * FROM account WHERE provider = $provider AND providerAccountId = $providerAccountId LIMIT 1`,
        { provider, providerAccountId },
      );
      const acctRow = acctRows[0];
      if (!acctRow) return null;

      const userId = rawId(String(acctRow.userId ?? ""), "user");
      const [userRows] = await db.query<[DbRow[]]>(`SELECT * FROM type::thing("user", $id)`, {
        id: userId,
      });
      const userRow = userRows[0];
      return userRow ? toAdapterUser(userRow) : null;
    },

    async updateUser(user) {
      const db = await getDb();
      const updateData: DbRow = {};
      if (user.name !== undefined) updateData.name = user.name;
      if (user.email !== undefined) updateData.email = user.email;
      if (user.image !== undefined) updateData.image = user.image;
      if (user.emailVerified !== undefined) {
        updateData.emailVerified = user.emailVerified?.toISOString() ?? null;
      }
      const role = (user as { role?: string }).role;
      if (role !== undefined) updateData.role = role;

      const [rows] = await db.query<[DbRow[]]>(
        `UPDATE type::thing("user", $id) MERGE $data RETURN AFTER`,
        { id: rawId(user.id ?? "", "user"), data: updateData },
      );
      const row = rows[0];
      return row ? toAdapterUser(row) : toAdapterUser({ id: user.id, email: user.email ?? "" });
    },

    async deleteUser(userId) {
      const db = await getDb();
      const id = rawId(userId, "user");
      await db.query(`DELETE account WHERE userId CONTAINS $id`, { id });
      await db.query(`DELETE session WHERE userId CONTAINS $id`, { id });
      await db.query(`DELETE type::thing("user", $id)`, { id });
    },

    // --- Account (OAuth links) -----------------------------------------
    async linkAccount(account: AdapterAccount) {
      const db = await getDb();
      const id = generateId();

      const accountData = {
        userId: account.userId,
        type: account.type,
        provider: account.provider,
        providerAccountId: account.providerAccountId,
        refresh_token: account.refresh_token ?? null,
        access_token: account.access_token ?? null,
        expires_at: account.expires_at ?? null,
        token_type: account.token_type ?? null,
        scope: account.scope ?? null,
        id_token: account.id_token ?? null,
        session_state: account.session_state ?? null,
      };

      await db.query(`CREATE type::thing("account", $id) CONTENT $data`, {
        id,
        data: accountData,
      });

      return account;
    },

    async unlinkAccount({ providerAccountId, provider }) {
      const db = await getDb();
      await db.query(
        `DELETE account WHERE provider = $provider AND providerAccountId = $providerAccountId`,
        { provider, providerAccountId },
      );
    },

    // --- Session --------------------------------------------------------
    async createSession(session) {
      const db = await getDb();
      const id = generateId();
      const [rows] = await db.query<[DbRow[]]>(
        `CREATE type::thing("session", $id) CONTENT $data RETURN AFTER`,
        {
          id,
          data: {
            sessionToken: session.sessionToken,
            userId: session.userId,
            expires: session.expires.toISOString(),
          },
        },
      );
      return toAdapterSession(rows[0]!);
    },

    async getSessionAndUser(sessionToken) {
      const db = await getDb();
      const [sessionRows] = await db.query<[DbRow[]]>(
        `SELECT * FROM session WHERE sessionToken = $sessionToken LIMIT 1`,
        { sessionToken },
      );
      const sessionRow = sessionRows[0];
      if (!sessionRow) return null;

      const session = toAdapterSession(sessionRow);
      const [userRows] = await db.query<[DbRow[]]>(`SELECT * FROM type::thing("user", $id)`, {
        id: session.userId,
      });
      const userRow = userRows[0];
      if (!userRow) return null;

      return { session, user: toAdapterUser(userRow) };
    },

    async updateSession(session) {
      const db = await getDb();
      if (!session.expires) return session as AdapterSession;

      const [rows] = await db.query<[DbRow[]]>(
        `UPDATE session SET expires = $expires WHERE sessionToken = $sessionToken RETURN AFTER`,
        {
          sessionToken: session.sessionToken,
          expires: session.expires.toISOString(),
        },
      );
      const row = rows[0];
      return row ? toAdapterSession(row) : (session as AdapterSession);
    },

    async deleteSession(sessionToken) {
      const db = await getDb();
      await db.query(`DELETE session WHERE sessionToken = $sessionToken`, {
        sessionToken,
      });
    },

    // --- Verification token --------------------------------------------
    async createVerificationToken(verificationToken: VerificationToken) {
      const db = await getDb();
      await db.query(`CREATE verification_token CONTENT $data`, {
        data: {
          identifier: verificationToken.identifier,
          token: verificationToken.token,
          expires: verificationToken.expires.toISOString(),
        },
      });
      return verificationToken;
    },

    async useVerificationToken({ identifier, token }) {
      const db = await getDb();
      const [rows] = await db.query<[DbRow[]]>(
        `SELECT * FROM verification_token WHERE identifier = $identifier AND token = $token LIMIT 1`,
        { identifier, token },
      );
      const row = rows[0];
      if (!row) return null;

      await db.query(
        `DELETE verification_token WHERE identifier = $identifier AND token = $token`,
        { identifier, token },
      );

      return {
        identifier: row.identifier as string,
        token: row.token as string,
        expires: new Date(row.expires as string),
      };
    },
  };
}
