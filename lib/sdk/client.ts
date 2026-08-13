export interface ValuationResult {
  value: number;
  method: string;
  formula_number: string;
  chapter: string;
  steps: { label: string; value: number; formula: string }[];
  inputs: Record<string, unknown>;
  assumptions: Record<string, unknown>;
  library_version: string;
  timestamp: string;
  git_commit: string;
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
    this.baseUrl = options.baseUrl ?? "https://startup-valuation.simonmak.com";
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

  /** Health check + tool inventory. */
  async health(): Promise<{
    status: string;
    version: string;
    tools: number;
    pure_python_tools: number;
    full_library_tools: number;
  }> {
    const res = await fetch(`${this.baseUrl}/api/health`);
    return (await res.json()) as Awaited<ReturnType<StartupValuationClient["health"]>>;
  }
}

export const startupValuation = new StartupValuationClient();
