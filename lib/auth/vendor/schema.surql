-- =============================================================================
-- Ascent Partners — Central Identity Schema (SurrealDB 3.x)
-- Single login record store shared by all ecosystem sites.
--
-- Namespace: ascent          Database: identity
-- Tables: user, account, session, verification_token
--
-- This is the canonical login record DB. Every site in the Ascent Partners
-- ecosystem (startup-valuation, valuation.report, esg-hub, apf-website,
-- simonmak.com, apg-website) authenticates against this single database.
--
-- Password hashing: bcrypt via bcryptjs (app-side). Hashes are stored in
-- `user.password`. SurrealDB `crypto::argon2` is available as a future
-- native alternative (see decision log).
-- =============================================================================

DEFINE DATABASE IF NOT EXISTS identity;

-- -----------------------------------------------------------------------------
-- user — a single identity across all sites (email/password + OAuth linked).
-- -----------------------------------------------------------------------------
DEFINE TABLE user SCHEMAFULL;

DEFINE FIELD email        ON user TYPE string ASSERT string::is_email($value);
DEFINE FIELD name         ON user TYPE option<string>;
DEFINE FIELD image        ON user TYPE option<string>;
DEFINE FIELD password     ON user TYPE option<string>;  -- bcrypt hash; NONE for OAuth-only users
DEFINE FIELD role         ON user TYPE string DEFAULT 'user';
DEFINE FIELD emailVerified ON user TYPE option<datetime>;
DEFINE FIELD resetToken       ON user TYPE option<string>;
DEFINE FIELD resetTokenExpiry ON user TYPE option<datetime>;
DEFINE FIELD createdAt    ON user TYPE datetime DEFAULT time::now();
DEFINE FIELD updatedAt    ON user TYPE datetime DEFAULT time::now();

DEFINE INDEX idx_user_email ON user FIELDS email UNIQUE;

-- -----------------------------------------------------------------------------
-- account — OAuth/external identity links (GitHub, Google, WeChat, ...).
-- Maps (provider, providerAccountId) -> user. Replaces the legacy
-- apf-website / simonmak-website `users.openId` / `loginMethod` fields.
-- -----------------------------------------------------------------------------
DEFINE TABLE account SCHEMAFULL;

DEFINE FIELD userId            ON account TYPE string;
DEFINE FIELD type              ON account TYPE string;
DEFINE FIELD provider          ON account TYPE string;
DEFINE FIELD providerAccountId ON account TYPE string;
DEFINE FIELD refresh_token     ON account TYPE option<string>;
DEFINE FIELD access_token      ON account TYPE option<string>;
DEFINE FIELD expires_at        ON account TYPE option<int>;
DEFINE FIELD token_type        ON account TYPE option<string>;
DEFINE FIELD scope             ON account TYPE option<string>;
DEFINE FIELD id_token          ON account TYPE option<string>;
DEFINE FIELD session_state     ON account TYPE option<string>;

DEFINE INDEX idx_account_provider ON account FIELDS provider, providerAccountId UNIQUE;
DEFINE INDEX idx_account_user     ON account FIELDS userId;

-- -----------------------------------------------------------------------------
-- session — database-backed sessions (used by the adapter; Auth.js JWT
-- strategy keeps sessions stateless, but this table supports session
-- revocation and password-reset invalidation).
-- -----------------------------------------------------------------------------
DEFINE TABLE session SCHEMAFULL;

DEFINE FIELD sessionToken ON session TYPE string;
DEFINE FIELD userId       ON session TYPE string;
DEFINE FIELD expires      ON session TYPE datetime;

DEFINE INDEX idx_session_token ON session FIELDS sessionToken UNIQUE;
DEFINE INDEX idx_session_user  ON session FIELDS userId;

-- -----------------------------------------------------------------------------
-- verification_token — email verification + password reset tokens.
-- -----------------------------------------------------------------------------
DEFINE TABLE verification_token SCHEMAFULL;

DEFINE FIELD identifier ON verification_token TYPE string;
DEFINE FIELD token      ON verification_token TYPE string;
DEFINE FIELD expires    ON verification_token TYPE datetime;

DEFINE INDEX idx_vtoken ON verification_token FIELDS identifier, token UNIQUE;

-- =============================================================================
-- Migration note (from legacy apf-website / simonmak-website `users` table):
--
--   Legacy `users` record with { openId, loginMethod } maps to:
--     user (new)                        + account
--       email    -> user.email            provider          = loginMethod
--       name     -> user.name             providerAccountId = openId
--       role     -> user.role             userId            = user.id
--       password -> user.password (NONE)
--
--   Run after creating this schema:
--     INSERT INTO account ...  FROM (SELECT ... FROM legacy_users WHERE loginMethod IS NOT NONE)
-- =============================================================================
