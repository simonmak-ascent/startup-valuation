import { getDb } from "@/lib/db/client";
import { TABLES, type Secret } from "@/lib/db/schema";

/**
 * EODHD API client — fetches real-time quotes, EOD prices, and fundamentals.
 * Ported from valuation_report/lib/api/eodhd.ts (key validation + caching).
 *
 * The API key is resolved from the SurrealDB `secret` table (server-side) or
 * the `EODHD_API_KEY` environment variable — never hardcoded.
 */

const BASE_URL = "https://eodhd.com/api";

interface EodhdQuote {
  code: string;
  close: number;
  open: number;
  high: number;
  low: number;
  date: string;
}

interface EodhdFundamental {
  [key: string]: unknown;
}

let cachedKey: string | null = null;

async function resolveApiKey(): Promise<string> {
  if (cachedKey) return cachedKey;

  const envKey = (process.env.EODHD_API_KEY ?? "").trim();
  if (envKey) {
    cachedKey = envKey;
    return envKey;
  }

  try {
    const db = await getDb();
    const [rows] = await db.query<[Secret[]]>(
      `SELECT * FROM ${TABLES.SECRET} WHERE service = 'eodhd' LIMIT 1`,
    );
    const secret = rows[0];
    if (secret?.secret_value) {
      cachedKey = secret.secret_value;
      return cachedKey;
    }
  } catch {
    // fall through to error
  }

  throw new Error("EODHD API key not configured (set EODHD_API_KEY or store in secret table)");
}

function validateApiKey(key: string): void {
  if (key.length < 15) {
    throw new Error("EODHD API key is invalid (too short)");
  }
}

async function fetchJson<T>(path: string): Promise<T> {
  const apiKey = await resolveApiKey();
  validateApiKey(apiKey);
  const url = `${BASE_URL}/${path}?api_token=${apiKey}&fmt=json`;
  const response = await fetch(url);

  if (response.status === 429) {
    throw new Error("RATE_LIMIT_EXCEEDED: too many EODHD requests");
  }
  if (response.status === 404 || response.status === 400) {
    throw new Error(`TICKER_NOT_FOUND: ${path}`);
  }
  if (!response.ok) {
    throw new Error(`EODHD API error: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function getRealTimeQuote(ticker: string): Promise<EodhdQuote> {
  return fetchJson<EodhdQuote>(`real-time/${ticker}`);
}

export async function getEndOfDay(ticker: string): Promise<EodhdQuote> {
  return fetchJson<EodhdQuote>(`eod/${ticker}`);
}

export async function getFundamentals(ticker: string): Promise<EodhdFundamental> {
  return fetchJson<EodhdFundamental>(`fundamentals/${ticker}`);
}
