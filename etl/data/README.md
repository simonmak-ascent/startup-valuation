# ETL Data Files

All data imported into SurrealDB must come from **recognized public sources**
with full provenance. No seed/synthetic data is permitted (see
`vdd/specs/webapp-platform/spec.md` AC-13 / AC-E5).

## `assumptions.json`

Market/economic assumptions (risk-free rate, market risk premium, sector
growth, etc.). Each row must carry `source_url`, `source_name`,
`source_retrieved_at`, and `source_version`. Rows missing any field are
rejected at import.

```json
[
  {
    "name": "Risk-Free Rate (10Y Treasury)",
    "value": 0.042,
    "unit": "decimal",
    "valid_from": "2026-08-01T00:00:00Z",
    "source_url": "https://www.federalreserve.gov/releases/h15/",
    "source_name": "Federal Reserve H.15",
    "source_retrieved_at": "2026-08-12T00:00:00Z",
    "source_version": "2026-08-11 release"
  }
]
```

Populate this file with real data before running `pnpm etl:import`. The values
above are illustrative only — replace them with actual sourced figures.
