/**
 * Shared identity types for the Ascent Partners SurrealDB identity store.
 */

export interface SurrealUser {
  id: string;
  email: string;
  name?: string | null;
  image?: string | null;
  password?: string | null;
  role: string;
  emailVerified?: string | null;
  resetToken?: string | null;
  resetTokenExpiry?: string | null;
  createdAt?: string;
  updatedAt?: string;
}

export interface SurrealAccount {
  id: string;
  userId: string;
  type: string;
  provider: string;
  providerAccountId: string;
  refresh_token?: string | null;
  access_token?: string | null;
  expires_at?: number | null;
  token_type?: string | null;
  scope?: string | null;
  id_token?: string | null;
  session_state?: string | null;
}

export interface SurrealSession {
  id: string;
  sessionToken: string;
  userId: string;
  expires: string;
}

export interface CreateUserInput {
  email: string;
  name?: string;
  password?: string;
  role?: string;
  image?: string;
}
