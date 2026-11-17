const globalForRateLimit = globalThis as unknown as {
  rateLimitBuckets?: Map<string, number[]>;
};

/**
 * Client address used to key a rate limit.
 *
 * The ALB appends the peer address to `X-Forwarded-For`, so the rightmost entry is the
 * only hop this deployment can trust — everything to its left is supplied by the caller
 * and trivially forged, which made the previous `split(",")[0]` key attacker-chosen.
 */
export function clientKey(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  if (!forwarded) {
    return "unknown";
  }
  const hops = forwarded
    .split(",")
    .map((hop) => hop.trim())
    .filter(Boolean);
  return hops[hops.length - 1] ?? "unknown";
}

/**
 * In-memory sliding-window rate limiter (per Vercel warm instance).
 * Good enough for abuse prevention on a single-tenant deployment.
 */
export function rateLimit(
  key: string,
  limit: number,
  windowMs: number,
): { success: boolean; retryAfter?: number } {
  if (!globalForRateLimit.rateLimitBuckets) {
    globalForRateLimit.rateLimitBuckets = new Map();
  }
  const buckets = globalForRateLimit.rateLimitBuckets;
  const now = Date.now();
  const windowStart = now - windowMs;

  const timestamps = (buckets.get(key) ?? []).filter((t) => t > windowStart);

  if (timestamps.length >= limit) {
    const oldest = timestamps[0]!;
    buckets.set(key, timestamps);
    return { success: false, retryAfter: Math.ceil((oldest + windowMs - now) / 1000) };
  }

  timestamps.push(now);
  buckets.set(key, timestamps);
  return { success: true };
}
