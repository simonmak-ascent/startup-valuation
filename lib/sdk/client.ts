export interface ValuationResult {
  value: number;
  method: string;
  formula_number: string;
  chapter: string;
  steps: { label: string; value: number; formula: string }[];
  inputs: Record<string, unknown>;
  assumptions: unknown[];
  library_version: string;
  timestamp: string;
  git_commit: string;
  /** Always absent: the audit log was removed with the database on 2026-11-18. */
  audit_id?: string;
  audit_status: "logged" | "failed" | "skipped";
}

export interface SdkOptions {
  baseUrl?: string;
  apiKey?: string;
}

export class StartupValuationClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(options: SdkOptions = {}) {
    this.baseUrl = options.baseUrl ?? "https://startup-valuation.ascent-partners.com";
    this.apiKey = options.apiKey;
  }

  private async request<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: body ? "POST" : "GET",
      headers: {
        "Content-Type": "application/json",
        ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error((err as { message?: string }).message ?? `HTTP ${res.status}`);
    }
    return (await res.json()) as T;
  }

  /** Run a valuation calculation by method name. */
  calculate(method: string, params: Record<string, unknown>): Promise<ValuationResult> {
    return this.request<ValuationResult>("/api/calculate", { method, params });
  }

  /**
   * Health check. The endpoint answers 200 when the market-data source is reachable and 503 when it
   * is not; it no longer reports a database, because the service has none.
   */
  async health(): Promise<{
    status: "ok" | "degraded";
    version: string;
    dependency: { name: string; status: "reachable" | "unreachable"; detail: string; latency_ms: number };
  }> {
    const res = await fetch(`${this.baseUrl}/api/health`);
    return (await res.json()) as Awaited<ReturnType<StartupValuationClient["health"]>>;
  }
}

export const startupValuation = new StartupValuationClient();
