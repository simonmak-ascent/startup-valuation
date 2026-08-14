import { Surreal } from "surrealdb";

/**
 * SurrealDB client for the shared Ascent Partners identity store.
 *
 * Uses the official `surrealdb` SDK (2.x) which targets SurrealDB 3.x servers.
 * A single connection is reused via a `globalThis` singleton (survives hot
 * reload in dev and is re-created per serverless invocation when cold).
 *
 * Credentials are read from environment variables only:
 *   SURREAL_URL       — e.g. "ws://localhost:8000" or "http://localhost:8000"
 *   SURREAL_USERNAME  — root or a scoped user
 *   SURREAL_PASSWORD
 *   SURREAL_NAMESPACE — defaults to "ascent"
 *   SURREAL_DATABASE  — defaults to "identity"
 */

export interface IdentityDbConfig {
  url: string;
  username: string;
  password: string;
  namespace: string;
  database: string;
}

export function getIdentityDbConfig(): IdentityDbConfig {
  const url = (process.env.SURREAL_URL ?? "").trim();
  const username = (process.env.SURREAL_USERNAME ?? "").trim();
  const password = (process.env.SURREAL_PASSWORD ?? "").trim();
  const namespace = (process.env.SURREAL_NAMESPACE ?? "ascent").trim();
  const database = (process.env.SURREAL_DATABASE ?? "identity").trim();

  if (!url || !username) {
    throw new Error(
      "Identity DB not configured. Required: SURREAL_URL, SURREAL_USERNAME, SURREAL_PASSWORD (SURREAL_NAMESPACE/SURREAL_DATABASE optional).",
    );
  }

  return { url, username, password, namespace, database };
}

const globalForDb = globalThis as unknown as {
  identityDb?: Surreal;
  identityDbPromise?: Promise<Surreal>;
};

async function connect(): Promise<Surreal> {
  const config = getIdentityDbConfig();
  const db = new Surreal();

  try {
    await db.connect(config.url, {
      namespace: config.namespace,
      database: config.database,
      authentication: {
        username: config.username,
        password: config.password,
      },
    });
    return db;
  } catch (error) {
    await db.close().catch(() => undefined);
    throw error;
  }
}

export function getDb(): Promise<Surreal> {
  if (globalForDb.identityDb) {
    return Promise.resolve(globalForDb.identityDb);
  }

  if (!globalForDb.identityDbPromise) {
    globalForDb.identityDbPromise = connect().then((db) => {
      globalForDb.identityDb = db;
      return db;
    });
  }

  return globalForDb.identityDbPromise;
}

export async function closeDb(): Promise<void> {
  if (globalForDb.identityDb) {
    await globalForDb.identityDb.close().catch(() => undefined);
    globalForDb.identityDb = undefined;
    globalForDb.identityDbPromise = undefined;
  }
}
