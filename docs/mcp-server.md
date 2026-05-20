# MCP Server

The MCP (Model Context Protocol) server exposes all 60+ valuation functions as tools for AI agents. Connect with Claude Desktop, Cursor, OpenCode, or any MCP-compatible client.

## Installation

```bash
pip install startup-valuation[mcp]
```

## Quick Start (stdio mode)

```bash
cd mcp_server && python server.py
```

The server runs in stdio mode by default — it reads JSON-RPC from stdin and writes responses to stdout.

## Connecting with Claude Desktop

1. Open Claude Desktop settings
2. Go to **Developer** → **Edit Config**
3. Add the MCP server to `mcp.json`:

```json
{
  "mcpServers": {
    "startup-valuation": {
      "command": "python",
      "args": ["/path/to/startup-valuation/mcp_server/server.py"],
      "cwd": "/path/to/startup-valuation/mcp_server"
    }
  }
}
```

4. Restart Claude Desktop
5. Claude will now have access to all 60+ valuation tools

## Connecting with Cursor

1. Open Cursor settings
2. Go to **Features** → **MCP Servers**
3. Add a new MCP server:

```json
{
  "mcpServers": {
    "startup-valuation": {
      "command": "python",
      "args": ["/path/to/startup-valuation/mcp_server/server.py"],
      "cwd": "/path/to/startup-valuation/mcp_server"
    }
  }
}
```

4. Restart Cursor
5. Use `@` to invoke valuation tools in chat

## Connecting with OpenCode

Add to your `opencode.json`:

```json
{
  "mcp": {
    "servers": {
      "startup-valuation": {
        "command": "python",
        "args": ["/path/to/startup-valuation/mcp_server/server.py"],
        "cwd": "/path/to/startup-valuation/mcp_server"
      }
    }
  }
}
```

## SSE Transport (Remote Mode)

For remote access, use SSE transport instead of stdio:

```python
# mcp_server/server.py — modify the run line:
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

Then connect your client to `http://your-server:8000/sse`.

## Tool Reference

### Probability

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_expected_value` | `outcomes: list[float]`, `probabilities: list[float]` | `{"value": float, "method": str, "inputs": dict}` |
| `valuation_joint_probability` | `probabilities: list[float]` | `{"value": float, "method": str}` |
| `valuation_probability_weighted` | `probabilities: list[float]`, `values: list[float]` | `{"value": float, "method": str}` |
| `valuation_portfolio_return` | `probabilities: list[float]`, `returns: list[float]` | `{"value": float, "method": str}` |
| `valuation_expected_value_continuous` | `lower: float`, `upper: float` | `{"value": float, "method": str}` |

### Time Value

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_present_value` | `future_value: float`, `rate: float`, `periods: float` | `{"value": float, "method": str}` |
| `valuation_npv` | `cash_flows: list[float]`, `rate: float` | `{"value": float, "method": str}` |

### CAPM

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_capm` | `risk_free_rate: float`, `beta: float`, `market_return: float` | `{"value": float, "method": str}` |
| `valuation_portfolio_beta` | `weights: list[float]`, `betas: list[float]` | `{"value": float, "method": str}` |
| `valuation_startup_capm` | `risk_free_rate: float`, `beta: float`, `market_risk_premium: float`, `size_premium: float = 0`, `startup_premium: float = 0` | `{"value": float, "method": str}` |

### Core Valuation

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_scorecard` | `average_valuation: float`, `weights: list[float]`, `scores: list[float]` | `{"value": float, "method": str}` |
| `valuation_berkus` | `sound_idea: float = 0`, `prototype: float = 0`, `quality_team: float = 0`, `strategic_relationships: float = 0`, `product_rollout: float = 0` | `{"value": float, "method": str}` |
| `valuation_risk_factor_summation` | `base_valuation: float`, `risk_ratings: list[float]` | `{"value": float, "method": str}` |
| `valuation_vc_post_money` | `terminal_value: float`, `target_return: float` | `{"value": float, "method": str}` |
| `valuation_vc_pre_money` | `post_money: float`, `investment: float` | `{"value": float, "method": str}` |

### Advanced

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_black_scholes` | `underlying: float`, `strike: float`, `risk_free_rate: float`, `volatility: float`, `time_to_maturity: float` | `{"value": float, "method": str}` |
| `valuation_scenario_analysis` | `scenarios: list[dict]` — each dict: `{name: str, probability: float, value: float}` | `{"value": float, "method": str}` |
| `valuation_binomial` | `underlying: float`, `strike: float`, `risk_free_rate: float`, `volatility: float`, `time_to_maturity: float`, `steps: int = 50` | `{"value": float, "method": str}` |

### SaaS

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_saas_ltv` | `arpu: float`, `gross_margin: float`, `churn_rate: float` | `{"value": float, "method": str}` |
| `valuation_rule_of_40` | `growth_rate: float`, `profit_margin: float` | `{"value": float, "method": str}` |
| `valuation_saas_multiple` | `arr: float`, `multiple: float` | `{"value": float, "method": str}` |

### Biotech

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_decision_tree` | `probabilities: list[float]`, `terminal_value: float` | `{"value": float, "method": str}` |
| `valuation_peak_sales` | `patient_population: float`, `penetration: float`, `price: float`, `compliance: float = 1.0` | `{"value": float, "method": str}` |
| `valuation_pipeline` | `drugs: list[dict]`, `discount_rate: float` | `{"value": float, "method": str}` |

### Fintech

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_payment_revenue` | `transaction_volume: float`, `take_rate: float` | `{"value": float, "method": str}` |
| `valuation_lending` | `loan_book: float`, `roe: float`, `pe_multiple: float`, `npl_reserves: float = 0` | `{"value": float, "method": str}` |
| `valuation_payment_processor` | `transaction_volume: float`, `take_rate: float`, `growth_rate: float`, `discount_rate: float`, `terminal_multiple: float`, `years: int = 5` | `{"value": float, "method": str}` |
| `valuation_neobank` | `customers: int`, `arpu: float`, `gross_margin: float`, `churn_rate: float`, `pe_multiple: float` | `{"value": float, "method": str}` |

### Marketplace

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_take_rate` | `revenue: float`, `gmv: float` | `{"value": float, "method": str}` |
| `valuation_gmv_multiple` | `gmv: float`, `multiple: float` | `{"value": float, "method": str}` |
| `valuation_buyer_retention` | `buyers_period_1: int`, `buyers_repeat: int` | `{"value": float, "method": str}` |
| `valuation_network_density` | `active_buyers: int`, `active_sellers: int`, `total_users: int` | `{"value": float, "method": str}` |

### Hardware

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_trl` | `market_size: float`, `market_share: float`, `margin: float`, `multiple: float`, `trl_discount: float` | `{"value": float, "method": str}` |

### International

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_ppp` | `spot_rate: float`, `inflation_foreign: float`, `inflation_domestic: float` | `{"value": float, "method": str}` |
| `valuation_crp` | `sovereign_yield: float`, `us_treasury_yield: float` | `{"value": float, "method": str}` |
| `valuation_intl_capm` | `risk_free_rate: float`, `beta: float`, `mrp: float`, `crp: float` | `{"value": float, "method": str}` |

### Stakeholders

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_dilution` | `ownership_before: float`, `investment: float`, `post_money: float` | `{"value": float, "method": str}` |
| `valuation_opm` | `enterprise_value: float`, `liquidation_pref: float`, `time_to_exit: float`, `volatility: float` | `{"value": float, "method": str}` |
| `valuation_pwerm` | `scenarios: list[dict]` | `{"value": float, "method": str}` |
| `valuation_liquidation` | `assets: dict`, `recovery_rates: dict` | `{"value": float, "method": str}` |
| `valuation_risk_adjusted_synergy` | `revenue_synergies: float`, `cost_synergies: float`, `prob_revenue: float = 0.4`, `prob_cost: float = 0.8`, `discount_rate: float = 0.10`, `years: int = 3` | `{"value": float, "method": str}` |
| `valuation_intrinsic_option` | `strike_price: float`, `fair_market_value: float`, `shares: int` | `{"value": float, "method": str}` |
| `valuation_employee_option` | `scenarios: list[dict]` | `{"value": float, "method": str}` |
| `valuation_vesting_adjusted` | `total_value: float`, `vested_fraction: float`, `annual_vest_rate: float = 0.25`, `retention_prob: float = 0.8`, `years_remaining: int = 3` | `{"value": float, "method": str}` |
| `valuation_cash_equity_breakeven` | `salary_reduction: float`, `equity_value: float`, `tax_rate: float = 0.30`, `discount_rate: float = 0.20`, `years: int = 4` | `{"value": float, "method": str}` |
| `valuation_max_asset_loan` | `cash: float = 0`, `accounts_receivable: float = 0`, `inventory: float = 0`, `equipment: float = 0`, `real_estate: float = 0` | `{"value": float, "method": str}` |

### Emerging

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_safe_discount` | `series_a_price: float`, `discount: float` | `{"value": float, "method": str}` |
| `valuation_safe_cap` | `cap: float`, `series_a_price: float` | `{"value": float, "method": str}` |
| `valuation_safe_expected` | `investment: float`, `cap: float`, `discount: float`, `series_a_valuation: float`, `series_a_price: float` | `{"value": float, "method": str}` |
| `valuation_token_value` | `transaction_volume: float`, `price_per_tx: float`, `velocity: float`, `supply: float` | `{"value": float, "method": str}` |
| `valuation_nvt_ratio` | `market_cap: float`, `daily_transaction_volume: float` | `{"value": float, "method": str}` |
| `valuation_esg_rate` | `base_rate: float`, `risk_premium: float = 0`, `opp_discount: float = 0` | `{"value": float, "method": str}` |
| `valuation_esg_premium` | `base_valuation: float`, `esg_score: float`, `premium_per_point: float = 0.02` | `{"value": float, "method": str}` |
| `valuation_esg_discount` | `base_valuation: float`, `esg_risk_score: float`, `discount_per_point: float = 0.01` | `{"value": float, "method": str}` |
| `valuation_metcalfes` | `n: float`, `k: float = 1.0` | `{"value": float, "method": str}` |
| `valuation_data_moat` | `data_volume: float`, `data_uniqueness: float`, `monetization_rate: float`, `competitive_advantage_years: float`, `discount_rate: float = 0.15` | `{"value": float, "method": str}` |
| `valuation_remote_npv` | `annual_savings: float`, `discount_rate: float` | `{"value": float, "method": str}` |
| `valuation_remote_premium` | `base_valuation: float`, `cost_savings_pct: float = 0.20`, `talent_access_premium: float = 0.10`, `productivity_gain: float = 0.05` | `{"value": float, "method": str}` |

### Compound Tool

| Tool | Parameters | Returns |
|---|---|---|
| `valuation_full_analysis` | `average_valuation: float`, `weights: list[float]`, `scores: list[float]`, `terminal_value: float`, `target_return: float`, `investment: float` | `{"scorecard": dict, "vc_post_money": dict, "vc_pre_money": dict, "triangulated_mean": float}` |

## Example: Using a Tool

Ask Claude: *"Use the valuation_scorecard tool with average valuation of $1.5M, weights [0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05], and scores [1.25, 1.50, 1.20, 0.75, 1.00, 0.90, 1.00]"*

Claude will call the tool and return:

```json
{
  "value": 1800000.0,
  "method": "Scorecard Method"
}
```
