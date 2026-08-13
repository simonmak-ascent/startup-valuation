import { Surreal } from "surrealdb";

interface SurrealDBConfig {
  url: string;
  namespace: string;
  database: string;
  user: string;
  password: string;
}

function getConfig(): SurrealDBConfig {
  const url = process.env.SURREALDB_URL;
  const namespace = process.env.SURREALDB_NS;
  const database = process.env.SURREALDB_DB;
  const user = process.env.SURREALDB_USER;
  const password = process.env.SURREALDB_PASS;

  if (!url || !namespace || !database || !user || !password) {
    throw new Error(
      "SurrealDB configuration missing. Required: SURREALDB_URL, SURREALDB_NS, SURREALDB_DB, SURREALDB_USER, SURREALDB_PASS",
    );
  }

  return { url, namespace, database, user, password };
}

const globalForDb = globalThis as unknown as {
  surrealClient: Surreal | undefined;
  surrealPromise: Promise<Surreal> | undefined;
};

async function createConnection(): Promise<Surreal> {
  const config = getConfig();
  const db = new Surreal();

  try {
    await db.connect(config.url, {
      namespace: config.namespace,
      database: config.database,
      authentication: { username: config.user, password: config.password },
    });
    return db;
  } catch (error) {
    await db.close().catch(() => undefined);
    throw error;
  }
}

export async function getDb(): Promise<Surreal> {
  if (globalForDb.surrealClient?.status === "connected") {
    return globalForDb.surrealClient;
  }

  if (!globalForDb.surrealPromise) {
    globalForDb.surrealPromise = createConnection().then((db) => {
      globalForDb.surrealClient = db;
      return db;
    });
  }

  return globalForDb.surrealPromise;
}

export async function healthCheck(): Promise<{
  status: "connected" | "disconnected";
  version?: string;
}> {
  try {
    const db = await getDb();
    const result = await db.query<[string]>("RETURN <string>info();");
    return {
      status: "connected",
      version: result[0],
    };
  } catch {
    return { status: "disconnected" };
  }
}

export async function closeDb(): Promise<void> {
  if (globalForDb.surrealClient) {
    await globalForDb.surrealClient.close();
    globalForDb.surrealClient = undefined;
    globalForDb.surrealPromise = undefined;
  }
}
