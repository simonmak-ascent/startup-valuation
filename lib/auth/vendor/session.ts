import { decode } from "@auth/core/jwt";

export const SESSION_COOKIE_NAME = "authjs.session-token";

/**
 * Cross-site session verification for non-NextAuth consumers (tRPC/Vite/static
 * sites). Auth.js v5 stores the session as an encrypted JWT (JWE) in a cookie
 * named `authjs.session-token`. Any site that shares the ecosystem `AUTH_SECRET`
 * can decode it and recover the user session — enabling single sign-on across
 * sites without each one running the full Auth.js stack.
 *
 * The session payload includes: `id`, `role`, `email`, `name`, `picture`,
 * `sub`, and the JWT `iat`/`exp`.
 */
export interface VerifiedSession {
  id?: string;
  role?: string;
  email?: string | null;
  name?: string | null;
  picture?: string | null;
  sub?: string;
  [key: string]: unknown;
}

function parseCookie(cookieHeader: string, name: string): string | undefined {
  for (const part of cookieHeader.split(";")) {
    const idx = part.indexOf("=");
    if (idx === -1) continue;
    const key = part.slice(0, idx).trim();
    const value = part.slice(idx + 1).trim();
    if (key === name && value) {
      try {
        return decodeURIComponent(value);
      } catch {
        return value;
      }
    }
  }
  return undefined;
}

export async function verifySessionToken(
  token: string,
  secret: string,
): Promise<VerifiedSession | null> {
  if (!token || !secret) return null;
  const decoded = await decode({
    token,
    secret,
    salt: SESSION_COOKIE_NAME,
  });
  return (decoded as VerifiedSession | null) ?? null;
}

export async function verifySessionFromCookies(
  cookieHeader: string | null | undefined,
  secret: string,
): Promise<VerifiedSession | null> {
  if (!cookieHeader) return null;
  const token = parseCookie(cookieHeader, SESSION_COOKIE_NAME);
  if (!token) return null;
  return verifySessionToken(token, secret);
}

/**
 * Read `AUTH_SECRET` with a fallback for the legacy `NEXTAUTH_SECRET` name.
 */
export function getAuthSecret(): string {
  return (process.env.AUTH_SECRET ?? process.env.NEXTAUTH_SECRET ?? "").trim();
}
