# us-macro

US macroeconomic and sector-level data skill for investing-toolkit.

## Overview

Fetches 21 US macroeconomic and sector-level indicators from FRED (Federal
Reserve Economic Data) and returns structured JSON grouped by 10 indicator
groups: rates, inflation, growth (core macro), plus housing, industrials,
energy, financials, consumer, tech, and ppi (sector-level). Sector groups
map to sector ETFs for investment analysis. This is a data-only skill -- it
does not analyze, map to regimes, or generate investment verdicts.

## Data Source

**FRED CSV endpoint** -- no API key required. The script downloads CSV data
directly from the Federal Reserve Bank of St. Louis public endpoint:

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES}&cosd={START}
```

An optional JSON API mode (`--use-api`) is available for more flexible queries,
but requires a `FRED_API_KEY` environment variable. The default CSV mode covers
all use cases for this skill.

## Indicators

### Core Macro

| Series | Name | Group | Frequency | Typical Lag |
|--------|------|-------|-----------|-------------|
| T10Y2Y | 10Y-2Y Treasury spread | rates | Daily | 1 business day |
| DGS10 | 10-Year Treasury yield | rates | Daily | 1 business day |
| DGS2 | 2-Year Treasury yield | rates | Daily | 1 business day |
| FEDFUNDS | Effective Federal Funds rate | rates | Monthly | ~1 week after month-end |
| CPIAUCSL | Headline CPI (All Items) | inflation | Monthly | ~2-3 weeks |
| CPILFESL | Core CPI (Less Food & Energy) | inflation | Monthly | ~2-3 weeks |
| GDPC1 | Real GDP | growth | Quarterly | ~1 month (advance est.) |
| INDPRO | Industrial Production Index | growth | Monthly | ~3-4 weeks |

### Sector-Level

| Series | Name | Group | Frequency | Typical Lag |
|--------|------|-------|-----------|-------------|
| PERMIT | Building Permits | housing | Monthly | ~2-3 weeks |
| HOUST | Housing Starts | housing | Monthly | ~2-3 weeks |
| CSUSHPISA | Case-Shiller Home Price Index | housing | Monthly | ~2 months |
| MORTGAGE30US | 30-Year Mortgage Rate | housing | Weekly | ~1 week |
| DGORDER | Durable Goods Orders | industrials | Monthly | ~4 weeks |
| DCOILWTICO | WTI Crude Oil Price | energy | Daily | 1 business day |
| DHHNGSP | Henry Hub Natural Gas Price | energy | Daily | 1 business day |
| BAMLH0A0HYM2 | High Yield Credit Spread | financials | Daily | 1 business day |
| RSAFS | Advance Retail Sales | consumer | Monthly | ~2 weeks |
| UMCSENT | Consumer Sentiment (UMich) | consumer | Monthly | ~2-4 weeks |
| CES3133440001 | Semiconductor Employment | tech | Monthly | ~3-4 weeks |
| PCUAINFOAINFO | PPI: Information Services | tech | Monthly | ~2-3 weeks |
| PCUOMFGOMFG | PPI: Total Manufacturing | ppi | Monthly | ~2-3 weeks |

Organized in 10 groups:

- **rates**: T10Y2Y, DGS10, DGS2, FEDFUNDS
- **inflation**: CPIAUCSL, CPILFESL
- **growth**: GDPC1, INDPRO
- **housing**: PERMIT, HOUST, CSUSHPISA, MORTGAGE30US
- **industrials**: DGORDER
- **energy**: DCOILWTICO, DHHNGSP
- **financials**: BAMLH0A0HYM2
- **consumer**: RSAFS, UMCSENT
- **tech**: CES3133440001, PCUAINFOAINFO
- **ppi**: PCUOMFGOMFG

## Sector ETF Mapping

| Group | Primary ETFs | Notes |
|-------|-------------|-------|
| housing | XLRE, XHB | MORTGAGE30US also signals XLF |
| industrials | XLI | INDPRO (growth group) also relevant |
| energy | XLE | Oil affects airlines, consumer spending, inflation |
| financials | XLF | T10Y2Y (rates group) drives bank margins |
| consumer | XLY, XLP | Retail sales drives discretionary vs staples rotation |
| tech | XLK | Semiconductor employment tracks supply chain |
| ppi | (cross-sector) | Leads CPI by 3-6 months; margin pressure signal |

## Architecture

```
us-macro skill
├── SKILL.md                    <- Claude reads this
├── scripts/
│   ├── fred_client.py          <- FRED CSV adapter (no API key)
│   └── setup.sh                <- auto-install uv
└── references/
    └── us-macro-indicators.md  <- 21 indicator entries + interpretation
```

Scripts are synced copies from `investing-toolkit/scripts/` via
`sync-scripts.sh`. The skill directory is self-contained so Claude Code
resolves all paths relative to the skill root.

## How It Works

1. **Resolve series list** -- The `--indicators` parameter (default: `all`)
   maps to FRED series IDs. For example, `--indicators rates` resolves to
   T10Y2Y, DGS10, DGS2, FEDFUNDS.

2. **Launch data-fetcher agent** -- The skill dispatches fetch requests to
   the `data-fetcher` agent, which runs `fred_client.py` via `uv run`.
   Requests are grouped by frequency to use appropriate period counts
   (e.g., 24 periods for daily/monthly, 12 for quarterly).

3. **Structure output** -- For each series, the skill extracts the latest
   and prior observations, computes direction (Rising / Falling / Flat),
   and groups results under their indicator group key.

## Output Contract

```json
{
  "fetched_at": "2026-04-16T08:00:00Z",
  "groups": {
    "rates": {
      "T10Y2Y": {
        "latest": { "date": "2026-04-15", "value": 0.42 },
        "prior":  { "date": "2026-04-14", "value": 0.38 },
        "direction": "Rising"
      },
      "DGS10":    { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "DGS2":     { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "FEDFUNDS": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "inflation": {
      "CPIAUCSL": { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "CPILFESL": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "growth": {
      "GDPC1":  { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "INDPRO": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "housing": { "PERMIT": { "..." }, "HOUST": { "..." }, "CSUSHPISA": { "..." }, "MORTGAGE30US": { "..." } },
    "industrials": { "DGORDER": { "..." } },
    "energy": { "DCOILWTICO": { "..." }, "DHHNGSP": { "..." } },
    "financials": { "BAMLH0A0HYM2": { "..." } },
    "consumer": { "RSAFS": { "..." }, "UMCSENT": { "..." } },
    "tech": { "CES3133440001": { "..." }, "PCUAINFOAINFO": { "..." } },
    "ppi": { "PCUOMFGOMFG": { "..." } }
  }
}
```

The `_provenance` for all entries is implicitly FRED. Check `latest.date`
to confirm the reference period, as publication lags vary by series.

## Cross-Plugin Usage

```
us-macro (this skill) -> macro-regime-snapshot -> domain-teams:investing-team
```

1. **us-macro** -- fetch FRED data, return structured JSON
2. **macro-regime-snapshot** -- map to Investment Clock phase + Growth-Inflation
   Positioning (GIP) quadrant, output regime call
3. **domain-teams:investing-team** -- full analysis, conviction scoring,
   portfolio implications

Pass the output JSON verbatim as the `### Input` section when launching
`macro-regime-snapshot`.

## Setup

Requires only `uv` (Python package runner). The `setup.sh` script
auto-installs `uv` if not found. No API keys are needed for the default
CSV endpoint.

```bash
# Manual test
uv run scripts/fred_client.py --series T10Y2Y,DGS10 --periods 24
```

## Maintenance & Verification

### Verify all series return data

```bash
cd investing-toolkit/scripts

for series in T10Y2Y DGS10 DGS2 FEDFUNDS CPIAUCSL CPILFESL GDPC1 INDPRO PERMIT HOUST CSUSHPISA MORTGAGE30US DGORDER DCOILWTICO DHHNGSP BAMLH0A0HYM2 RSAFS UMCSENT CES3133440001 PCUAINFOAINFO PCUOMFGOMFG; do
  uv run fred_client.py --series "$series" --periods 3 --no-cache 2>&1 | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
l = d.get('latest') or {}
pv = d.get('_provenance') or {}
err = d.get('error', '')
if err:
    print(f'$series: ERROR - {err}')
else:
    print(f'$series: date={l.get(\"date\",\"???\")}  value={l.get(\"value\",\"\")}  staleness={pv.get(\"staleness_days\",\"?\")}d')
"
done
```

**Expected staleness by frequency:**

| Frequency | Series | Expected Staleness |
|-----------|--------|-------------------|
| Daily | T10Y2Y, DGS10, DGS2, DCOILWTICO, DHHNGSP, BAMLH0A0HYM2 | < 5 days |
| Weekly | MORTGAGE30US | < 10 days |
| Monthly | FEDFUNDS, CPIAUCSL, CPILFESL, INDPRO, PERMIT, HOUST, DGORDER, RSAFS, UMCSENT, CES3133440001, PCUOMFGOMFG, PCUAINFOAINFO | < 60 days |
| Monthly (lagging) | CSUSHPISA | < 90 days |
| Quarterly | GDPC1 | < 200 days |

### Verify FRED CSV endpoint

```bash
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10" | tail -3
```

### Verify series IDs are still valid

FRED occasionally retires or renames series:

```bash
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}" | head -3
```

If retired, check successor at: `https://fred.stlouisfed.org/series/{SERIES_ID}`

### Add a new FRED series

1. Find series ID at https://fred.stlouisfed.org
2. Verify: `uv run fred_client.py --series {ID} --periods 12 --no-cache`
3. Update `SKILL.md` (add to group) + `references/us-macro-indicators.md` (add entry)
4. No code change needed in `fred_client.py` (accepts any FRED series ID)

### Latest verification

**Date**: 2026-04-17 — All 21 series ACTIVE, returning 2026 data via CSV endpoint.
