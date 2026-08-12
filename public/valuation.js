// valuation.js — WASM loader + high-level API
// Loads startup-valuation WASM module and exposes calculators to the browser.
// <1KB gzipped. Zero dependencies.

const WASM_URL = '/valuation.wasm';

let wasm = null;

async function init() {
  if (wasm) return wasm;
  const { default: initWasm, ...exports } = await import(WASM_URL);
  await initWasm();
  wasm = exports;
  return wasm;
}

// ── Public API ──────────────────────────────────────────────────────

export async function scorecard(averageValuation, weights, scores) {
  const w = await init();
  return JSON.parse(w.scorecard_valuation_json(averageValuation, weights, scores));
}

export async function blackScholes(underlying, strike, riskFreeRate, volatility, timeToMaturity) {
  const w = await init();
  return JSON.parse(w.black_scholes_json(underlying, strike, riskFreeRate, volatility, timeToMaturity));
}

export async function vcMethodPostMoney(terminalValue, targetReturn) {
  const w = await init();
  return JSON.parse(w.vc_method_post_money_json(terminalValue, targetReturn));
}

export async function expectedValue(outcomes, probabilities) {
  const w = await init();
  return JSON.parse(w.expected_value_json(outcomes, probabilities));
}

export async function poissonProbability(lambda, k) {
  const w = await init();
  return JSON.parse(w.poisson_probability_json(lambda, k));
}

export async function saasMetrics(arr, churnRate, cac, growthRate, profitMargin) {
  const w = await init();
  return JSON.parse(w.saas_metrics_json(arr, churnRate, cac, growthRate, profitMargin));
}

export async function dcf(revenue, growthRate, discountRate, terminalGrowth, projectionYears) {
  const w = await init();
  return JSON.parse(w.dcf_valuation_json(revenue, growthRate, discountRate, terminalGrowth, projectionYears));
}

export async function listTools() {
  const w = await init();
  return JSON.parse(w.list_tools_json());
}

export async function getVersion() {
  const w = await init();
  return w.version();
}

export { init };
