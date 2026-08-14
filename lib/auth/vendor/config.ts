import type { NextAuthConfig } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { SurrealDBAdapter } from "./adapter";
import { findUserByEmail, validatePassword } from "./auth";

export interface CreateAuthConfigOptions {
  /** Extra providers (GitHub, Google, WeChat, ...) in addition to email/password. */
  providers?: NextAuthConfig["providers"];
  /** Custom sign-in page path. Defaults to "/sign-in". */
  signInPage?: string;
  /**
   * Cookie domain for cross-site sessions within one parent domain.
   * e.g. ".simonmak.com" so startup-valuation.simonmak.com and
   * simonmak.com share a session. Omit for a single site / custom domains.
   */
  cookieDomain?: string;
  /** Shared AUTH_SECRET. Falls back to process.env.AUTH_SECRET. */
  secret?: string;
  /** Disable email/password credentials (OAuth-only sites). */
  credentials?: boolean;
}

/**
 * Build the canonical Auth.js v5 configuration for an Ascent Partners site.
 *
 * All sites share:
 *   - The SurrealDB `identity` store (via SurrealDBAdapter)
 *   - JWT session strategy (stateless, verifiable via shared AUTH_SECRET)
 *   - `id` + `role` claims propagated to the session
 *   - Email/password credentials provider (bcrypt-hashed passwords)
 *
 * Usage per site:
 *   // app/api/auth/[...nextauth]/route.ts
 *   import NextAuth from "next-auth";
 *   import { createAuthConfig } from "@simonplmak-cloud/auth";
 *   export const { handlers, auth, signIn, signOut } = NextAuth(createAuthConfig({ ... }));
 */
export function createAuthConfig(
  options: CreateAuthConfigOptions = {},
): NextAuthConfig {
  const providers: NextAuthConfig["providers"] = [];

  if (options.credentials !== false) {
    providers.push(
      Credentials({
        name: "credentials",
        credentials: {
          email: { label: "Email", type: "email" },
          password: { label: "Password", type: "password" },
        },
        async authorize(credentials) {
          const email =
            typeof credentials?.email === "string" ? credentials.email : "";
          const password =
            typeof credentials?.password === "string"
              ? credentials.password
              : "";

          if (!email || !password) return null;

          const user = await findUserByEmail(email);
          if (!user || !user.password) return null;

          const isValid = await validatePassword(user, password);
          if (!isValid) return null;

          return {
            id: user.id.replace("user:", ""),
            email: user.email,
            name: user.name ?? null,
            image: user.image ?? null,
            role: user.role,
          };
        },
      }),
    );
  }

  if (options.providers) {
    providers.push(...options.providers);
  }

  return {
    adapter: SurrealDBAdapter(),
    providers,
    session: { strategy: "jwt" },
    pages: options.signInPage ? { signIn: options.signInPage } : undefined,
    secret: options.secret ?? process.env.AUTH_SECRET,
    callbacks: {
      async jwt({ token, user }) {
        if (user) {
          token.id = user.id;
          token.role = (user as { role?: string }).role ?? "user";
        }
        return token;
      },
      async session({ session, token }) {
        if (session.user) {
          session.user.id = (token.id as string) ?? "";
          (session.user as { role?: string }).role =
            (token.role as string) ?? "user";
        }
        return session;
      },
    },
    ...(options.cookieDomain
      ? {
          cookies: {
            sessionToken: {
              name: "authjs.session-token",
              options: {
                domain: options.cookieDomain,
                httpOnly: true,
                sameSite: "lax",
                path: "/",
                secure: true,
              },
            },
          },
        }
      : {}),
  };
}
