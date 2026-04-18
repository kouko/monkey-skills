---
name: us-macro
description: >-
  Fetch US macroeconomic and sector-level indicators via FRED CSV. Data layer
  only — no analysis or regime mapping. Returns structured JSON with latest
  values and direction for 13 indicator groups: rates, inflation, growth,
  nowcast, real-rates, pmi, housing, industrials, energy, financials,
  consumer, tech, and ppi.
  Designed for handoff to macro-regime-snapshot (IC/GIP mapping) or
  domain-teams:investing-team (sector ETF analysis).
  米国マクロ・セクター指標取得。美國總經與產業指標擷取。
---

# US Macro

Fetches US macroeconomic and sector-level indicators from FRED and outputs
structured JSON. Covers 29 distinct series across 13 groups: 6 core macro
groups (rates, inflation, growth, nowcast, real-rates, pmi) and 7 sector
groups (housing, industrials, energy, financials, consumer, tech, ppi)
mapped to sector ETFs. The `pmi` group shares `USALOLITOAASTSAM` with
`nowcast` as the OECD CLI proxy for the FRED-unavailable ISM / S&P Global
PMI (see `references/us-macro-indicators.md` "PMI" section). This skill is
**data-only** — it does not analyze, map to regimes, or generate investment
verdicts. The output is designed for immediate handoff to
`macro-regime-snapshot` for IC/GIP regime mapping, or to
`domain-teams:investing-team` for sector ETF analysis.

**Monthly GDP proxy note**: US official GDP is quarterly (`GDPC1`). The
`nowcast` group provides four Fed-published series (GDPNow, CFNAI, WEI, OECD
CLI) that collectively proxy real-time GDP momentum — parallel to china-macro's
三大數據 package and japan-macro's 景気動向指数 CI trio, forming a cross-market
symmetric framework for monthly GDP tracking.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated group names: `rates`, `inflation`, `growth`, `nowcast`, `real-rates`, `pmi`, `housing`, `industrials`, `energy`, `financials`, `consumer`, `tech`, `ppi`, or `all` |

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

### nowcast (monthly GDP proxies)

| Series | Name | Frequency |
|--------|------|-----------|
| GDPNOW | Atlanta Fed GDPNow Real GDP Nowcast (SAAR %) | Quarterly snapshot, updated 6-7×/mo during quarter |
| CFNAI | Chicago Fed National Activity Index | Monthly |
| WEI | NY Fed Weekly Economic Index | Weekly |
| USALOLITOAASTSAM | OECD Composite Leading Indicator (USA, amplitude-adjusted) | Monthly |

### real-rates (breakeven inflation + TIPS market real yields)

| Series | Name | Frequency |
|--------|------|-----------|
| T5YIE | 5-Year Breakeven Inflation Rate (DGS5 − DFII5) | Daily |
| T10YIE | 10-Year Breakeven Inflation Rate (DGS10 − DFII10) | Daily |
| DFII5 | 5-Year Treasury Inflation-Indexed Security (market real yield) | Daily |
| DFII10 | 10-Year Treasury Inflation-Indexed Security (market real yield) | Daily |

Used by `macro-regime-snapshot` for the real-rate decomposition block:
`Real = Nominal − Breakeven` (identity-check with DFIIxx market yield).
Signal thresholds (four-tier, 2025-2026 calibration):
`< 0%` Accommodative / `0–1.0%` Neutral / `1.0–1.75%` Moderately
Restrictive / `≥ 1.75%` Clearly Restrictive. Calibrated against HLW r*
(1.42%), Lubik-Matthes (2.15%), NY Fed composite (~1.7%), and Williams'
"modestly restrictive" qualitative guidance (Dec 2025 / Jan 2026
speeches). See `references/us-macro-indicators.md` "Real Rates" section
and `../macro-regime-snapshot/references/investment-clock-cheatsheet.md`
"Threshold provenance" for full audit.

### pmi (OECD CLI cycle-phase proxy for manufacturing/services PMI)

| Series | Name | Frequency |
|--------|------|-----------|
| USALOLITOAASTSAM | OECD Composite Leading Indicator (USA, amplitude-adjusted) — PMI proxy | Monthly |

FRED does **not** host ISM PMI (removed June 2016) or S&P Global / Markit
PMI (S&P Global licenses commercially, not on FRED). OECD CLI
(`USALOLITOAASTSAM`) is the FRED-available leading-indicator proxy —
same underlying cycle signal, different construction (amplitude-adjusted
composite of cyclical series, NOT a diffusion index).
Signal thresholds (OECD CLI calibration, NOT the ISM 50-point threshold):
`> 100 & rising` Expansion / `> 100 & falling` Pre-peak / `< 100 & falling`
Contraction / `< 100 & rising` Recovery. Series is shared with the
`nowcast` group (single fetch, two logical groupings). For real ISM / S&P
Global PMI readings, cross-check manually against ISM and S&P Global
press releases — see `references/us-macro-indicators.md` "PMI" section.

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
| `nowcast` | GDPNOW,CFNAI,WEI,USALOLITOAASTSAM |
| `real-rates` | T5YIE,T10YIE,DFII5,DFII10 |
| `pmi` | USALOLITOAASTSAM (shared with `nowcast` — fetched once) |
| `housing` | PERMIT,HOUST,CSUSHPISA,MORTGAGE30US |
| `industrials` | DGORDER |
| `energy` | DCOILWTICO,DHHNGSP |
| `financials` | BAMLH0A0HYM2 |
| `consumer` | RSAFS,UMCSENT |
| `tech` | CES3133440001,PCUAINFOAINFO |
| `ppi` | PCUOMFGOMFG |
| `all` | All 29 distinct series above (USALOLITOAASTSAM serves both `nowcast` and `pmi`) |

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
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series GDPNOW,CFNAI,USALOLITOAASTSAM --periods 24
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series WEI --periods 52
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T5YIE,T10YIE,DFII5,DFII10 --periods 24
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

If `--indicators pmi` is specified alone, reuse the `nowcast` fetch path
that includes `USALOLITOAASTSAM` (there is no separate PMI fetch — OECD
CLI is the shared FRED-available proxy).

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
    "nowcast": {
      "GDPNOW":           { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "CFNAI":            { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "WEI":              { "latest": { ... }, "prior": { ... }, "direction": "..." },
      "USALOLITOAASTSAM": { "latest": { ... }, "prior": { ... }, "direction": "..." }
    },
    "pmi": {
      "USALOLITOAASTSAM": { "latest": { ... }, "prior": { ... }, "direction": "..." }
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
| GDPNOW | Quarter-level snapshot; updated 6-7×/mo within the current quarter, final value fixes when GDPC1 prints |
| CFNAI | ~2-3 months after reference month |
| WEI | ~1 week after reference week |
| USALOLITOAASTSAM | ~1 month after reference month (OECD CLI release) |

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
