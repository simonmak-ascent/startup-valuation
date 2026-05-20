# Troubleshooting

Common issues and solutions for the Startup Valuation library, MCP server, and AI Agent Skills.

## Installation Issues

### `fastmcp not found`

**Error:** `ModuleNotFoundError: No module named 'fastmcp'`

**Solution:** Install the MCP extras:

```bash
pip install startup-valuation[mcp]
```

### `startup_valuation not found`

**Error:** `ModuleNotFoundError: No module named 'startup_valuation'`

**Solution:** Install the library:

```bash
pip install startup-valuation
```

### Version mismatch

**Error:** Unexpected behavior or missing functions

**Solution:** Check your installed version:

```bash
pip show startup-valuation
```

Ensure you're on the latest version:

```bash
pip install --upgrade startup-valuation
```

## MCP Server Issues

### Connection refused

**Error:** `Connection refused` or `ECONNREFUSED`

**Causes and solutions:**

1. **Server not running** — Start the server first:
   ```bash
   cd mcp_server && python server.py
   ```

2. **Wrong transport mode** — stdio mode doesn't use network ports. If you're trying to connect via HTTP, configure SSE transport:
   ```python
   mcp.run(transport="sse", host="0.0.0.0", port=8000)
   ```

3. **Firewall blocking** — Ensure port 8000 (or your configured port) is not blocked.

### Tool not found

**Error:** `Tool "valuation_xyz" not found`

**Solutions:**

1. **Check tool name spelling** — Tool names use `valuation_` prefix and snake_case:
   - ✅ `valuation_scorecard`
   - ❌ `valuation_score_card`
   - ❌ `scorecard_valuation` (this is the library function name, not the MCP tool name)

2. **Check the [tool reference](mcp-server.md#tool-reference)** for the complete list of 60+ tools.

### Server crashes on startup

**Error:** Python traceback on `python server.py`

**Solutions:**

1. **Check Python version** — Requires Python 3.10+:
   ```bash
   python --version
   ```

2. **Check dependencies** — Reinstall with MCP extras:
   ```bash
   pip install --force-reinstall startup-valuation[mcp]
   ```

3. **Check for conflicting packages** — If you have multiple versions of `fastmcp`:
   ```bash
   pip uninstall fastmcp
   pip install startup-valuation[mcp]
   ```

## AI Agent Skills Issues

### Skills not loading

**Error:** Agent doesn't recognize the skills

**Solutions:**

1. **Check file path** — For OpenCode, skills must be in `~/.config/opencode/skills/`:
   ```bash
   ls ~/.config/opencode/skills/
   # Should show: valuation-core  valuation-advanced  valuation-industry  valuation-stakeholder  valuation-emerging
   ```

2. **Check file name** — Each skill directory must contain a `SKILL.md` file:
   ```bash
   ls ~/.config/opencode/skills/valuation-core/
   # Should show: SKILL.md
   ```

3. **Check SKILL.md format** — The file must start with `# Skill:` header:
   ```bash
   head -1 ~/.config/opencode/skills/valuation-core/SKILL.md
   # Should show: # Skill: valuation-core
   ```

4. **Restart the agent** — Skills are loaded at startup. Restart OpenCode/Claude/Cursor after adding skills.

### Agent doesn't follow skill workflow

**Issue:** Agent ignores the skill instructions

**Solutions:**

1. **Check skill is in the right location** — Different agents use different skill paths:
   - OpenCode: `~/.config/opencode/skills/`
   - Claude: Custom Instructions (paste SKILL.md content)
   - Cursor: Custom Instructions (paste SKILL.md content)

2. **Make the skill name specific** — Rename the skill to match user queries:
   - ✅ `valuation-saas` (matches "value my SaaS startup")
   - ❌ `valuation-industry` (too generic)

3. **Add trigger keywords** — In the `When to Use` section, include phrases users commonly say:
   ```markdown
   ## When to Use
   - User says "value my SaaS" or "SaaS valuation"
   - User mentions ARR, MRR, churn, or LTV
   ```

## Python Library Issues

### Unexpected results

**Issue:** Function returns unexpected valuation

**Solutions:**

1. **Check parameter units** — All monetary values are in absolute dollars (not thousands or millions):
   ```python
   # Correct: $1.5 million
   scorecard_valuation(average_valuation=1_500_000, ...)

   # Wrong: passing 1.5 (interpreted as $1.50)
   scorecard_valuation(average_valuation=1.5, ...)
   ```

2. **Check parameter constraints** — Some functions validate inputs:
   - `scorecard_valuation`: weights must sum to 1.0
   - `berkus_valuation`: each factor must be 0 to max_per_factor
   - `risk_factor_summation`: exactly 12 risk ratings, each -2 to +2

3. **Check the [API reference](api/core.md)** for parameter details and constraints.

### Import errors

**Error:** `ImportError: cannot import name 'xyz' from 'startup_valuation'`

**Solution:** Check the correct module:

```python
# Core methods
from startup_valuation.core import scorecard_valuation, berkus_valuation

# Advanced methods
from startup_valuation.advanced import black_scholes, monte_carlo_valuation

# Industry-specific
from startup_valuation.saas import ltv_saas, cac
from startup_valuation.biotech import rnPV, decision_tree_ev

# All types
from startup_valuation.types import ValuationResult, Scenario, Distribution
```

See the [chapter index](chapters.md) for the full module-to-function mapping.
