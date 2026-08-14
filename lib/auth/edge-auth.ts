import NextAuth from "next-auth";

/**
 * Edge-safe NextAuth instance for middleware. The full config
 * (lib/auth/config.ts) pulls in the SurrealDB adapter, bcryptjs, and
 * `node:crypto`, none of which can be bundled into the Edge runtime.
 * Middleware only needs stateless JWT session verification, so this config
 * omits the adapter and the credentials provider.
 *
 * Keep the jwt/session callbacks in sync with
 * lib/auth/vendor/config.ts createAuthConfig().
 */
export const { auth: edgeAuth } = NextAuth({
  providers: [],
  secret: process.env.AUTH_SECRET,
  session: { strategy: "jwt" },
  pages: { signIn: "/sign-in" },
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
        (session.user as { role?: string }).role = (token.role as string) ?? "user";
      }
      return session;
    },
  },
});
