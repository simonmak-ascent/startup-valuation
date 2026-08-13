import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import { createAuthConfig } from "@simonplmak-cloud/auth";

/**
 * startup-valuation site auth — built on the shared `@simonplmak-cloud/auth`
 * package (SurrealDB 3.x identity store + Auth.js v5).
 *
 * Email/password credentials come from the shared config factory (bcrypt-hashed
 * passwords stored in the central `identity` database). GitHub OAuth is added
 * per-site. JWT sessions + id/role claims are shared across the ecosystem.
 *
 * Required env vars (see .env.example):
 *   AUTH_SECRET            — shared secret across all ecosystem sites
 *   AUTH_GITHUB_ID/SECRET  — GitHub OAuth app (optional; omit to disable)
 *   SURREAL_URL            — SurrealDB 3.x endpoint
 *   SURREAL_USERNAME/PASSWORD
 *   SURREAL_NAMESPACE      — default "ascent"
 *   SURREAL_DATABASE       — default "identity"
 */
export const { handlers, signIn, signOut, auth } = NextAuth(
  createAuthConfig({
    providers: [
      GitHub({
        clientId: process.env.AUTH_GITHUB_ID ?? "",
        clientSecret: process.env.AUTH_GITHUB_SECRET ?? "",
      }),
    ],
    signInPage: "/sign-in",
    cookieDomain: process.env.AUTH_COOKIE_DOMAIN || undefined,
  }),
);
