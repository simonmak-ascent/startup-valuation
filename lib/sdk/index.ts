import { StartupValuationClient, type ValuationResult } from "./client";

/**
 * TypeScript SDK for the Startup Valuation Engine.
 *
 * Typed wrapper functions mirror the Python library (via the `/api/calculate`
 * endpoint). Every method returns a `ValuationResult` with the computed value,
 * step-by-step derivation, and formula/chapter traceability.
 *
 * Usage:
 *   import { scorecard, capm } from "@simonmak/startup-valuation";
 *   const r = await scorecard(1500000, [0.3,0.25,...], [1.25,1.5,...]);
 */

export { StartupValuationClient, startupValuation, type ValuationResult } from "./client";

function make<P extends unknown[]>(client: StartupValuationClient, method: string) {
  return (...params: P): Promise<ValuationResult> =>
    client.calculate(method, params as unknown as Record<string, unknown>);
}

const sdk = new StartupValuationClient();

export const scorecard = make<[number, number[], number[]]>(sdk, "scorecard");
export const berkus = make<[number, number, number, number, number]>(sdk, "berkus");
export const riskFactor = make<[number, number[]]>(sdk, "risk_factor");
export const vcPostMoney = make<[number, number]>(sdk, "vc_post_money");
export const vcPreMoney = make<[number, number]>(sdk, "vc_pre_money");
export const terminalValue = make<[number, number]>(sdk, "terminal_value");
export const saasLtv = make<[number, number, number]>(sdk, "saas_ltv");
export const saasCac = make<[number, number]>(sdk, "saas_cac");
export const saasNrr = make<[number, number, number]>(sdk, "saas_nrr");
export const saasMagicNumber = make<[number, number]>(sdk, "saas_magic_number");
export const saasRuleOf40 = make<[number, number]>(sdk, "saas_rule_of_40");
export const capm = make<[number, number, number]>(sdk, "capm");
export const startupCapm = make<[number, number, number, number, number]>(sdk, "startup_capm");
export const presentValue = make<[number, number, number]>(sdk, "present_value");
export const annuity = make<[number, number, number]>(sdk, "annuity");
export const peRatio = make<[number, number]>(sdk, "pe_ratio");
export const psRatio = make<[number, number]>(sdk, "ps_ratio");
export const evEbitda = make<[number, number]>(sdk, "ev_ebitda");
export const evRevenue = make<[number, number]>(sdk, "ev_revenue");
export const dilution = make<[number, number, number]>(sdk, "dilution");
export const commonDiscount = make<[number, number]>(sdk, "common_discount");
export const opm = make<[number, number, number, number, number]>(sdk, "opm");
export const ventureDebt = make<[number, number, number]>(sdk, "venture_debt");
export const gmvMultiple = make<[number, number]>(sdk, "gmv_multiple");
export const networkValue = make<[number, number, number]>(sdk, "network_value");
