const globalForRateLimit = globalThis as unknown as {
  rateLimitBuckets?: Map<string, number[]>;
};

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
