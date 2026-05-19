# AGENTS.md — Startup Valuation

## Commands

```bash
pip install -e ".[dev]"        # install with dev deps (pytest, ruff, coverage)
pytest                          # run all 50 tests
pytest --cov=startup_valuation  # with coverage
ruff check .                    # lint
```

CI runs `pytest --cov=... -v` on Python 3.10/3.11/3.12. No lint gate in CI.

## Architecture

- `src/startup_valuation/` — 14 modules, 80+ functions. All return `ValuationResult` (never bare numbers).
- `src/startup_valuation/types.py` — `ValuationResult`, `Distribution`, `Scenario`, `SensitivityResult` dataclasses.
- `mcp_server/server.py` — FastMCP server with 40+ tools. Run: `cd mcp_server && python server.py`. Requires `pip install -e ".[mcp]"`.
- `skills/` — 5 AI-Agent SKILL.md files (core, advanced, industry, stakeholder, emerging).
- `output/` — Textbook source markdown (reference material, not generated).
- `specs/` — SDD artifacts for valuation-engine and docx-to-md projects.

## Key Conventions

- Every library function returns `ValuationResult` with `value`, `method`, `inputs`, `assumptions`, `sensitivity`, `chapter`.
- MCP tools unwrap `ValuationResult` to plain dicts (`{"value": ..., "method": ...}`) for agent consumption.
- Tests validate against textbook example values — do not change expected values without verifying against the source book.
- `scipy.stats` used for Poisson and Black-Scholes `N(d)` calculations (avoids `math.factorial` overflow).
- `numpy` used for Monte Carlo simulations.

## Gotchas

- `src/` layout: must use `pip install -e` or set `PYTHONPATH=src` for imports to resolve.
- `fastmcp` is an optional dependency (`.[mcp]`) — not installed by default with `.[dev]`.
- Test tolerances use `pytest.approx(abs=N)` — textbook values have ±$1–5 rounding variance.
