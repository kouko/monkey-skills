---
name: us-macro
description: >-
  Fetch US macroeconomic and sector-level indicators via FRED CSV. Data layer
  only — no analysis or regime mapping. Returns structured JSON with latest
  values and direction for 10 indicator groups: rates, inflation, growth,
  housing, industrials, energy, financials, consumer, tech, and ppi. Designed
  for handoff to macro-regime-snapshot (IC/GIP mapping) or
  domain-teams:investing-team (sector ETF analysis).
  米国マクロ・セクター指標取得。美國總經與產業指標擷取。
---

# US Macro

Fetches US macroeconomic and sector-level indicators from FRED and outputs
structured JSON. Covers 21 series across 10 groups: 3 core macro groups
(rates, inflation, growth) and 7 sector groups (housing, industrials, energy,
financials, consumer, tech, ppi) mapped to sector ETFs. This skill is
**data-only** — it does not analyze, map to regimes, or generate investment
verdicts. The output is designed for immediate handoff to
`macro-regime-snapshot` for IC/GIP regime mapping, or to
`domain-teams:investing-team` for sector ETF analysis.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated group names: `rates`, `inflation`, `growth`, `housing`, `industrials`, `energy`, `financials`, `consumer`, `tech`, `ppi`, or `all` |

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

### housing

| Series | Name | Frequency |
|--------|------|-----------|
| PERMIT | New Privately-Owned Housing Units Authorized | Monthly |
| HOUST | New Privately-Owned Housing Units Started | Monthly |
| CSUSHPISA | S&P/Case-Shiller U.S. National Home Price Index | Monthly |
| MORTGAGE30US | 30-Year Fixed Rate Mortgage Average | Weekly |

### industrials

| Series | Name | Frequency |
|--------|------|-----------|
| DGORDER | Manufacturers' New Orders: Durable Goods | Monthly |

### energy

| Series | Name | Frequency |
|--------|------|-----------|
| DCOILWTICO | Crude Oil Prices: WTI | Daily |
| DHHNGSP | Henry Hub Natural Gas Spot Price | Daily |

### financials

| Series | Name | Frequency |
|--------|------|-----------|
| BAMLH0A0HYM2 | ICE BofA US High Yield Option-Adjusted Spread | Daily |

### consumer

| Series | Name | Frequency |
|--------|------|-----------|
| RSAFS | Advance Retail Sales: Retail and Food Services | Monthly |
| UMCSENT | University of Michigan Consumer Sentiment | Monthly |

### tech

| Series | Name | Frequency |
|--------|------|-----------|
| CES3133440001 | Semiconductor and Electronic Component Mfg Employment | Monthly |
| PCUAINFOAINFO | PPI: Information Services | Monthly |

### ppi

| Series | Name | Frequency |
|--------|------|-----------|
| PCUOMFGOMFG | PPI: Total Manufacturing Industries | Monthly |

---

## How It Works

### Step 1 — Resolve series list

Map `--indicators` to FRED series IDs:

| Input | Series resolved |
|-------|-----------------|
| `rates` | T10Y2Y,DGS10,DGS2,FEDFUNDS |
| `inflation` | CPIAUCSL,CPILFESL |
| `growth` | GDPC1,INDPRO |
| `housing` | PERMIT,HOUST,CSUSHPISA,MORTGAGE30US |
| `industrials` | DGORDER |
| `energy` | DCOILWTICO,DHHNGSP |
| `financials` | BAMLH0A0HYM2 |
| `consumer` | RSAFS,UMCSENT |
| `tech` | CES3133440001,PCUAINFOAINFO |
| `ppi` | PCUOMFGOMFG |
| `all` | All 21 series above |

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
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T10Y2Y,DGS10,DGS2,FEDFUNDS --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series CPIAUCSL,CPILFESL --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series GDPC1,INDPRO --periods 12
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series PERMIT,HOUST,CSUSHPISA --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series MORTGAGE30US --periods 52
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series DGORDER --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series DCOILWTICO,DHHNGSP --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series BAMLH0A0HYM2 --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series RSAFS,UMCSENT --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series CES3133440001,PCUAINFOAINFO --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series PCUOMFGOMFG --periods 24

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
    },
    "housing": {
      "PERMIT":       { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "HOUST":        { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "CSUSHPISA":    { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "MORTGAGE30US": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "industrials": {
      "DGORDER": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "energy": {
      "DCOILWTICO": { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "DHHNGSP":    { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "financials": {
      "BAMLH0A0HYM2": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "consumer": {
      "RSAFS":   { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "UMCSENT": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "tech": {
      "CES3133440001": { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "PCUAINFOAINFO": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "ppi": {
      "PCUOMFGOMFG": { "latest": { ... }, "prior": { ... }, "direction": "..." }
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

## Sector ETF Mapping

Each indicator group maps to one or more sector ETFs for investment analysis.
Some indicators appear in one group but provide cross-sector signals.

| Group | Primary ETFs | Key Indicators | Cross-Sector Signal |
|-------|-------------|----------------|---------------------|
| housing | XLRE, XHB | PERMIT, HOUST, CSUSHPISA, MORTGAGE30US | MORTGAGE30US also affects XLF (bank mortgage revenue) |
| industrials | XLI | DGORDER | INDPRO (in growth group) also signals XLI |
| energy | XLE | DCOILWTICO, DHHNGSP | Oil affects XLI (airlines), consumer spending, inflation |
| financials | XLF | BAMLH0A0HYM2 | T10Y2Y (in rates) drives bank net interest margins |
| consumer | XLY, XLP | RSAFS, UMCSENT | Retail sales drives XLY vs XLP rotation |
| tech | XLK | CES3133440001, PCUAINFOAINFO | Semiconductor employment tracks supply chain health |
| ppi | (cross-sector) | PCUOMFGOMFG | Leads CPI by 3-6 months; margin compression early warning |

---

## Limitations

FRED data has publication lags — the latest observation may be weeks behind
real-world conditions:

| Series | Typical lag |
|--------|-------------|
| T10Y2Y, DGS10, DGS2 | 1 business day |
| DCOILWTICO, DHHNGSP | 1 business day |
| BAMLH0A0HYM2 | 1 business day |
| MORTGAGE30US | ~1 week (weekly release) |
| FEDFUNDS | ~1 week after month-end |
| CPIAUCSL, CPILFESL | ~2-3 weeks after reference month |
| PERMIT, HOUST | ~2-3 weeks after reference month |
| DGORDER | ~4 weeks after reference month |
| INDPRO | ~3-4 weeks after reference month |
| RSAFS | ~2 weeks after reference month |
| UMCSENT | ~2 weeks (preliminary), ~4 weeks (final) |
| CES3133440001 | ~3-4 weeks after reference month |
| PCUOMFGOMFG, PCUAINFOAINFO | ~2-3 weeks after reference month |
| CSUSHPISA | ~2 months after reference month |
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
