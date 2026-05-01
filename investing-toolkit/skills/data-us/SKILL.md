---
name: data-us
description: >-
  Layer 1 (Data) — multi-source US data bundler. Fetch-only role; pure I/O, no
  analysis. Composes yfinance (price + multiples), SEC EDGAR (10-K/10-Q/8-K +
  XBRL facts + Item-section narrative), and FRED (macro indicators) into
  structured JSON via `pack.py`. Supports `--ticker` (single) and `--tickers`
  (batch). Pack types: snapshot / memo-fetch / comps-multiples /
  screener-batch / regime-pack. Designed for handoff to Layer 2 analysis-*
  skills (analysis-dcf, analysis-comps, analysis-macro-regime,
  analysis-screener) and Layer 3 report-* skills.
  米国データバンドル取得（fetch only）。美國資料擷取與打包（純 I/O）。
---

# data-us

Layer 1 data skill for the US market in the v2.0.0 three-layer architecture
(Data / Analysis / Report). This skill is **fetch-only** — it does not
analyze, score, or compose narrative. All output is structured JSON intended
for direct handoff to a Layer 2 `analysis-*` skill or a Layer 3 `report-*`
orchestrator.

## Sources

| Layer | Source | Script | Returns |
|-------|--------|--------|---------|
| Snapshot / multiples | yfinance (unofficial) | `${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py` | OHLCV history, info dict (PE/PB/marketCap/beta/dividendYield/sector etc.) |
| Fundamental | SEC EDGAR (`data.sec.gov`, official Tier A) | `${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py` | 10-K / 10-Q / 8-K filings index, XBRL us-gaap facts, Item-section narrative |
| Macro | FRED CSV | `${CLAUDE_SKILL_DIR}/scripts/fred_client.py` | Time-series for rates / inflation / growth / nowcast / real-rates / swap-spreads |

All three client scripts are byte-identical copies of the canonical
versions under `investing-toolkit/scripts/` (drift is enforced by CI; see
repo `scripts/sync-check.sh`).

---

## Pack types

| Pack | Single ticker | Batch tickers | Use case |
|------|---------------|---------------|----------|
| `snapshot` | required | n/a | Quick overview (yfinance info + 2y price) |
| `memo-fetch` | required | n/a (heavy) | Equity memo full bundle (yfinance + SEC filings + XBRL facts) |
| `comps-multiples` | exactly one of `--ticker` / `--tickers` (mutually exclusive) | — | Comps anchor + peers; multiples-only fields |
| `screener-batch` | n/a | required (≥2) | Screener input; lightweight info fields |
| `regime-pack` | n/a | n/a | FRED macro indicators only (no ticker dimension) |

### `comps-multiples` field set

`trailingPE`, `forwardPE`, `priceToSales`, `priceToBook`,
`enterpriseToEbitda`, `enterpriseToRevenue`, `marketCap`, `enterpriseValue`.

### `screener-batch` field set

`trailingPE`, `priceToBook`, `marketCap`, `dividendYield`, `beta`,
`fiftyTwoWeekHigh`, `fiftyTwoWeekLow`, `regularMarketPrice`, `sector`,
`industry`, `shortName`.

### `regime-pack` FRED groups

`rates` (T10Y2Y, DGS10, DGS2, FEDFUNDS) · `inflation` (CPIAUCSL, CPILFESL) ·
`growth` (GDPC1, INDPRO) · `nowcast` (GDPNOW, CFNAI, USALOLITOAASTSAM) ·
`wei` (WEI) · `real_rates` (T5YIE, T10YIE, DFII5, DFII10) ·
`swap_spreads` (DGS3MO, SOFR30DAYAVG).

---

## Inputs

| Parameter | Required | Notes |
|-----------|----------|-------|
| `--pack` | yes | One of: `snapshot`, `memo-fetch`, `comps-multiples`, `screener-batch`, `regime-pack` |
| `--ticker` | conditional | Single ticker (e.g. `AAPL`). Required for `snapshot` / `memo-fetch`. Mutually exclusive with `--tickers` (argparse-enforced). |
| `--tickers` | conditional | Comma-separated (e.g. `AAPL,MSFT,GOOGL`). Required for `screener-batch`; one of `--ticker` / `--tickers` (exactly one) for `comps-multiples`. |

`INVESTING_TOOLKIT_CACHE` env var is passed through to all three underlying
clients (yfinance / SEC EDGAR / FRED), enabling cache reuse across packs.

---

## How It Works

`pack.py` is a thin facade that shells out to the three client scripts with
correct flags per pack type, then merges the JSON.

### snapshot

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker AAPL --pack snapshot
```

Internally runs:
- `yfinance_client.py --ticker AAPL --action info`
- `yfinance_client.py --ticker AAPL --period 2y`

### memo-fetch

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker NVDA --pack memo-fetch
```

Internally runs (sequential — SEC EDGAR is rate-limited):
- `yfinance_client.py --ticker NVDA --action info`
- `yfinance_client.py --ticker NVDA --period 2y`
- `sec_edgar_client.py --ticker NVDA --action filings --forms 10-K,10-Q,8-K --limit 8`
- `sec_edgar_client.py --ticker NVDA --action facts`

### comps-multiples (single OR batch)

```
# Single (anchor only)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker AAPL --pack comps-multiples

# Batch (peers)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --tickers MSFT,GOOGL,META,AMZN --pack comps-multiples
```

Single: `yfinance_client.py --ticker {T} --action info`; output filtered to
multiples fields. Batch: `yfinance_client.py --tickers {T1,T2,...} --action
info` (native batch path); each ticker filtered to multiples fields.

### screener-batch (batch only)

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --tickers AAPL,MSFT,GOOGL,META,AMZN --pack screener-batch
```

Internally runs `yfinance_client.py --tickers {list} --action info`; each
ticker filtered to the screener field set.

### regime-pack (no ticker)

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --pack regime-pack
```

Internally runs `fred_client.py --series ... --periods ...` per indicator
group (rates / inflation / growth / nowcast / wei / real_rates /
swap_spreads). For the full FRED 14-group sector ETF mapping, call
`fred_client.py` directly or compose at the report layer.

---

## Output Format

All packs return a JSON object on stdout with these top-level keys:

| Key | Notes |
|-----|-------|
| `pack` | Echo of the pack name |
| `fetched_at` | UTC ISO 8601 timestamp at composition time |
| `ticker` | Present for `snapshot` / `memo-fetch` only |
| `tickers` | Present for batch packs (`comps-multiples`, `screener-batch`); map of upper-case ticker → fields |
| `country` | `"US"` for `regime-pack` |
| `groups` | Indicator groups dict for `regime-pack` |
| `company_info`, `price_history`, `sec_filings`, `sec_facts` | Per-pack payload keys |

If an underlying client fails, its slot is replaced with a structured error
object: `{ "error": "...", "script": "...", "stderr": "..." }`. For batch
packs (`comps-multiples` / `screener-batch`), if the entire batch fetch
fails, the result has an empty `tickers: {}` map and a top-level `error`
field carrying the client error blob (the `tickers` map never contains a
`_error` sentinel — consumers may safely iterate `tickers.items()`).
Subprocess timeouts are reported as `{ "error": "client timeout after 300s",
"_cmd": [...], "_returncode": -1 }`. The pack itself still exits 0
(partial-failure semantics — aligned with batch contract elsewhere in the
toolkit).

---

## Output schema

Formal JSON Schemas for each pack type live in `references/`:

| Pack | Schema |
|---|---|
| `snapshot` | [`references/schema-snapshot.json`](references/schema-snapshot.json) |
| `memo-fetch` | [`references/schema-memo-fetch.json`](references/schema-memo-fetch.json) |
| `comps-multiples` | [`references/schema-comps-multiples.json`](references/schema-comps-multiples.json) |
| `screener-batch` | [`references/schema-screener-batch.json`](references/schema-screener-batch.json) |
| `regime-pack` | [`references/schema-regime-pack.json`](references/schema-regime-pack.json) |
| Error / provenance wrapper | [`references/schema-error-envelope.json`](references/schema-error-envelope.json) |

Cross-pack field-level conventions (currency / time-zone / units / tier
provenance / cache TTL / error envelope / cross-skill consumers) are
documented in [`references/output-schema-overview.md`](references/output-schema-overview.md).

CI validates each pack output against its schema (see
`tests/data/test_pack_schemas.py`).

---

## Cross-skill handoff

```
data-us → analysis-{dcf,comps,macro-regime,screener} → report-{equity-memo,stock-snapshot,screener-list,portfolio-review}
```

Pass the pack JSON verbatim as the `### Input` block when launching the
next-layer skill. Layer 2 skills are pure compute; Layer 3 skills compose
narrative and delegate to `domain-teams:investing-team` for verdicts.

---

## Limitations

- yfinance is an unofficial scraper (Tier 2). For income statement / balance
  sheet / cash flow, use SEC EDGAR (`memo-fetch`) — never rely on yfinance
  `financials` for verdict-grade memos.
- `memo-fetch` is heavy (4 sequential fetches; SEC rate-limited 10 req/s).
  Single-ticker only by design.
- FRED data has publication lags (1 day for Treasury yields, 2-3 weeks for
  CPI/RSAFS, 1-2 months for GDP/CSUSHPISA). Always check the `latest.date`
  field downstream.
- Cross-country batches (e.g. mixed US + JP + TW tickers) must be split at
  the report layer — `data-us` is country-scoped to US tickers only.

---

US data bundler · 米国データバンドル取得 · 美股資料擷取與打包
