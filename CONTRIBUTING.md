# Contributing to Startup Valuation

Thank you for your interest in contributing! This project implements 80+ valuation formulas from the Startup Valuation textbook.

## Development Setup

```bash
# Clone and install
git clone https://github.com/simonplmak-cloud/startup-valuation.git
cd startup-valuation
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=startup_valuation --cov-report=term-missing

# Lint
ruff check .

# Type check
mypy src/startup_valuation --ignore-missing-imports
```

## Adding a New Valuation Method

1. **Create the module function** in the appropriate file under `src/startup_valuation/`
   - All functions must return `ValuationResult` with `value`, `method`, `inputs`, `assumptions`, and `chapter`
   - Include a docstring with formula, args, returns, and a doctest example
   - Add input validation with clear error messages

2. **Write tests** in `tests/test_<module>.py`
   - Test against textbook example values
   - Test edge cases and error conditions
   - Use `pytest.approx()` for floating-point comparisons

3. **Add an MCP tool** in `mcp_server/server.py`
   - Wrap the library function and return a plain dict for agent consumption
   - Include a descriptive docstring

4. **Update documentation** in `docs/`
   - Add to the appropriate `docs/api/<module>.md`
   - Update `docs/chapters.md` if it's a new function

5. **Verify everything passes**
   ```bash
   pytest --cov=startup_valuation -v
   ruff check .
   mypy src/startup_valuation --ignore-missing-imports
   mkdocs build --strict
   ```

## Pull Request Guidelines

1. **Create a branch** from `main` with a descriptive name
2. **Keep commits focused** — one logical change per commit
3. **Write a clear PR description** — what changed and why
4. **Ensure CI passes** — tests, lint, type check, docs build
5. **Link related issues** in the PR description

## Code Conventions

- **TypeScript-style Python**: strict typing, explicit types, named exports
- **ValuationResult**: every function returns this — never bare numbers
- **Docstrings**: Google-style with formula, args, returns, example
- **Line length**: 120 characters max
- **Imports**: sorted (ruff I001)
- **Tests**: validate against textbook example values

## Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

This runs ruff automatically on each commit. Skip with `git commit --no-verify` if needed.

## Reporting Issues

- **Bugs**: Use the bug report template
- **Feature requests**: Use the feature request template
- **Security vulnerabilities**: See [SECURITY.md](SECURITY.md)

## Code of Conduct

Please note that this project follows the [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to abide by its terms.
