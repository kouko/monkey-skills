---
name: us-macro
description: >-
  Fetch US macroeconomic indicators via FRED CSV. Data layer only — no analysis
  or regime mapping. Returns structured JSON with latest values and direction
  for rates, inflation, and growth indicator groups. Designed for handoff to
  macro-regime-snapshot (IC/GIP mapping) or domain-teams:investing-team
  (analysis). 米国マクロ指標取得。美國總經指標擷取。
---

# US Macro

Fetches US macroeconomic indicators from FRED and outputs structured JSON.
This skill is **data-only** — it does not analyze, map to regimes, or generate
investment verdicts. The output is designed for immediate handoff to
`macro-regime-snapshot` for IC/GIP regime mapping, or to
`domain-teams:investing-team` for full analysis.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated group names: `rates`, `inflation`, `growth`, or `all` |

---

## Indicator Groups

### rates

| Series | Name | Frequency |
|--------|------|-----------|
| T10Y2Y | 10Y-2Y Treasury spread | Daily |
| DGS10 | 10-Year Treasury yield | Daily |
| DGS2 | 2-Year Treasury yield | Daily |
| FEDFUNDS | Effective Federal Funds rate | Monthly |

### inflation

| Series | Name | Frequency |
|--------|------|-----------|
| CPIAUCSL | Headline CPI (All Items) | Monthly |
| CPILFESL | Core CPI (Less Food & Energy) | Monthly |

### growth

| Series | Name | Frequency |
|--------|------|-----------|
| GDPC1 | Real GDP | Quarterly |
| INDPRO | Industrial Production Index | Monthly |

---

## How It Works

### Step 1 — Resolve series list

Map `--indicators` to FRED series IDs:

| Input | Series resolved |
|-------|-----------------|
| `rates` | T10Y2Y,DGS10,DGS2,FEDFUNDS |
| `inflation` | CPIAUCSL,CPILFESL |
| `growth` | GDPC1,INDPRO |
| `all` | All 8 series above |

### Step 2 — Launch data-fetcher agent

Launch `../../agents/data-fetcher.md` with fetch requests grouped by
frequency to use appropriate period counts:

```
### Task
Fetch US macro indicators from FRED. Return structured JSON.
Do not analyze or interpret.

### Scripts
base_path: {absolute path to investing-toolkit/scripts/}

### Fetch Requests
- uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T10Y2Y,DGS10,DGS2,FEDFUNDS --periods 24
- uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series CPIAUCSL,CPILFESL --periods 24
- uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series GDPC1,INDPRO --periods 12

### Output Format
Return raw JSON from each fetch request.
```

Only include fetch requests for the resolved indicator groups. If
`--indicators growth` is specified, only run the GDPC1,INDPRO fetch.

### Step 3 — Structure output

For each series in the fetched JSON, extract:

- `series`: FRED series ID
- `latest`: `{ date, value }` — most recent observation
- `prior`: `{ date, value }` — second most recent observation
- `direction`: `Rising` if latest > prior, `Falling` if latest < prior, `Flat` if equal
- `count`: number of observations returned

Group results under their indicator group key.

---

## Output Format

```json
{
  "fetched_at": "2026-04-16T08:00:00Z",
  "groups": {
    "rates": {
      "T10Y2Y": { "latest": { "date": "...", "value": ... }, "prior": { "date": "...", "value": ... }, "direction": "..." },
      "DGS10":  { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "DGS2":   { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "FEDFUNDS": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "inflation": {
      "CPIAUCSL": { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "CPILFESL": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "growth": {
      "GDPC1":  { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "INDPRO": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    }
  }
}
```

---

## Reference

For detailed documentation on each FRED series (units, frequency, publication
lag, interpretation, common pitfalls):

- `references/us-macro-indicators.md`

---

## Limitations

FRED data has publication lags — the latest observation may be weeks behind
real-world conditions:

| Series | Typical lag |
|--------|-------------|
| T10Y2Y, DGS10, DGS2 | 1 business day |
| FEDFUNDS | ~1 week after month-end |
| CPIAUCSL, CPILFESL | ~2-3 weeks after reference month |
| INDPRO | ~3-4 weeks after reference month |
| GDPC1 | ~1 month (advance estimate) |

Always check the `latest.date` field to confirm the reference period.

---

## Cross-Plugin Handoff

```
us-macro (this skill) → macro-regime-snapshot → domain-teams:investing-team
```

1. `us-macro` (this skill) — fetch FRED data, return structured JSON
2. `macro-regime-snapshot` — map to IC phase + GIP quadrant, output regime call
3. `domain-teams:investing-team` — full analysis, conviction, portfolio implications

Pass the output JSON verbatim as the `### Input` section when launching
`macro-regime-snapshot`.
