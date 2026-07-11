# CN output schema overview

> This document describes the CN pack payload shapes. Invocation now
> goes through the unified `data-markets` facade —
> `skills/data-markets/scripts/pack.py` (ticker suffix auto-detects
> the CN market; `--market cn` is required for `regime-pack`, which
> has no ticker dimension).

Schemas in this directory document the JSON output produced by
`investing-toolkit/skills/data-markets/scripts/pack.py` for each of the
five CN pack types. Each schema is JSON Schema **draft-2020-12**, validated by the
`jsonschema` Python library (used in `tests/data/test_pack_schemas.py`).
Schemas are descriptive, not strictly closed — `additionalProperties: true`
is the default because upstream sources (NBS new-SPA / akshare / FRED /
yfinance) evolve and we want forward compatibility, not lockdown.

## Pack-to-schema map

| Pack | Schema file | Tier | Use case |
|------|-------------|------|----------|
| `snapshot` | [`cn-schema-snapshot.json`](cn-schema-snapshot.json) | 2 | Quick yfinance overview (info + 6mo daily) for a single .SS / .SZ / .HK ticker. Feeds `analysis-screener` lightweight paths and `report-stock-snapshot`. |
| `memo-fetch` | [`cn-schema-memo-fetch.json`](cn-schema-memo-fetch.json) | **2 only** | Equity memo bundle (yfinance info + 2y price + annual + quarterly financials). **Tier 2 floor — CN primary-source disclosure (cninfo / HKEXnews) deferred from v2.0.0.** Feeds `analysis-dcf` and `report-equity-memo` with explicit tier-status warning. |
| `comps-multiples` | [`cn-schema-comps-multiples.json`](cn-schema-comps-multiples.json) | 2 | Multiples-only filter on yfinance info. Single (anchor) or batch (peers); both modes uniformly shaped as `tickers: []`. Feeds `analysis-comps`. |
| `screener-batch` | [`cn-schema-screener-batch.json`](cn-schema-screener-batch.json) | 2 | Lightweight screener-input fields, batch only (≥2 tickers). Feeds `analysis-screener`. |
| `regime-pack` | [`cn-schema-regime-pack.json`](cn-schema-regime-pack.json) | A + 2 | NBS (21) + akshare (8) + FRED (2) + market indices (5) = **36 series**. Feeds `analysis-macro-regime`. No ticker dimension. |
| Shared | [`cn-schema-error-envelope.json`](cn-schema-error-envelope.json) | — | Reusable error sentinels; documents stderr-only ticker-normalisation warnings for orchestrators. |

## Source mix and tier per pack

| Source | Authority | Used by packs |
|---|---|---|
| **NBS new-SPA API** | Tier A primary (国家统计局) | `regime-pack` (21 indicators) |
| **akshare** (PBOC chinamoney + SHIBOR + Caixin via eastmoney) | Tier 2 aggregator | `regime-pack` (8 indicators) |
| **FRED CSV** | Tier A (Fed as cross-source for FX) | `regime-pack` (DEXCHUS, TRESEGCNM052N) |
| **yfinance** | Tier 2 unofficial scraper | All ticker-level packs + market indices in `regime-pack` |

CN memo-fetch is **deliberately Tier 2 only** in v2.0.0 — see
`cn-schema-memo-fetch.json#/properties/_provenance` for the locked
`tier: 2 (integer) / primary_source_status: "deferred"` block. Compare
with data-us where memo-fetch composes Tier A SEC EDGAR filings + XBRL
facts on top of yfinance.

## Sample fixture trim convention

> **Fixture trim convention**: To keep fixtures small while preserving
> validation coverage, history `data` arrays and observation lists in
> `tests/data/fixtures/data-cn-*.json` are **head-truncated** (oldest
> rows kept). The summary fields `latest_close` / `latest_date` (and
> equivalently `latest` / `reference_period` on macro indicators)
> reflect the most-recent observation **at fixture-capture time** and
> may not align with the head-truncated rows. Live `pack.py` output is
> not truncated. This convention applies to all fixtures across
> `data-{cn,jp,kr,tw,us}`.

## Ticker normalisation

`pack.py` auto-suffixes bare numeric codes per the CN/HK convention:

| Pattern | Suffix | Example |
|---|---|---|
| 6-digit `/6,9` | `.SS` (Shanghai) | `600519` → `600519.SS` |
| 6-digit `/0,2,3` | `.SZ` (Shenzhen) | `000858` → `000858.SZ`, `300750` → `300750.SZ` |
| 4-digit | `.HK` | `0700` → `0700.HK` |
| 5-digit | `.HK` (leading-zero form) | `09988` → `09988.HK` |
| 6-digit `/4,8` | **passthrough + warning** | BSE — yfinance does not cover Beijing Stock Exchange |
| Other digit length | **passthrough + warning** | "Unrecognized CN ticker format" |

Warnings are stderr-only — see
`cn-schema-error-envelope.json#/ticker_normalization_warnings`. They are
**not** part of the JSON output. Consumers that want to surface them
must capture stderr separately. Downstream yfinance failure (likely for
BSE codes) propagates as a normal `_error` entry inside the batch
`tickers` map.

## Field dictionary (cross-pack conventions)

### Currency and units

- yfinance fields are in **native exchange currency**:
  - `.SS` / `.SZ` → **CNY** (`marketCap`, `regularMarketPrice`,
    `totalRevenue`, `enterpriseValue` etc. all in raw RMB; a `marketCap`
    of `1734131318784` is ~CNY 1.73T)
  - `.HK` → **HKD**
  - Cross-country normalisation is the responsibility of Layer 2
    (`analysis-comps` / `analysis-screener`); Layer 1 preserves raw values.
- `dividendYield` from yfinance is reported as a **percentage**
  (e.g. `3.73` means 3.73%, not 373%). Consumers must NOT multiply by 100
  again. (Same convention as data-us.)
- NBS indicator units are **explicit per indicator** in the
  `unit` field. Common values:
  - `%` for YoY rates (CPI, PPI, GDP, retail, FAI, industrial, M1, M2,
    real-estate, services-production)
  - 亿元 (100 million CNY) for trade balance
  - Index level for PMIs (manufacturing / non-mfg / composite)
- akshare (PBOC) units:
  - `%` for LPR-1Y / LPR-5Y / RRR / SHIBOR-3M / Caixin PMIs
  - 亿元 for 社融增量 (TSF flow) / new-loans
- FRED units:
  - `DEXCHUS` is **CNY per USD** (note: opposite of common USD/CNY quote convention)
  - `TRESEGCNM052N` is **USD millions**, FX reserves ex-gold (SAFE/IMF pipeline)
- yfinance OHLC values inherit ticker currency. `volume` is shares (raw integer).

### NBS-specific quirk: CPI index = 100 + YoY%

NBS publishes CPI/PPI as `100 + YoY%` (so 101.0 means +1.0% YoY, not
101% inflation). This is documented per-indicator in the `_notes` field
on the NBS observation block (e.g. `"_notes": "Index = 100 + YoY%.
Subtract 100 for signed YoY delta."`). Layer 2 `analysis-macro-regime`
must apply this transform before comparing CN CPI to US/JP CPI.

### Time zones and date formats

- `fetched_at` (top-level + nested) is **UTC ISO 8601** with second
  precision (client-script stamped).
- yfinance `data[].date` (OHLCV) is **CST market date** for `.SS` / `.SZ`
  and **HKT market date** for `.HK`, formatted as `YYYY-MM-DD`.
- **NBS observation `date` is `YYYYMMDD` string** (no separators), with
  day-of-month always `01` for monthly series (e.g. `20260301` =
  March 2026 monthly print). Quarterly series use first month of quarter
  (`20260101` = Q1 2026).
- **akshare observation `date` is also `YYYYMMDD` string**.
- FRED observation `date` is **`YYYY-MM-DD`** (period-start, native FRED
  format) — different from the NBS/akshare format. Consumers must
  format-detect, not assume.
- 民國 (ROC) year is **N/A** for CN. (Reminder: `data-tw` returns
  Western years; `data-jp` does same; CN never uses ROC.)

### Special types

- `_source` is a stable enum tag inherited from each client:
  - `nbs_spa` (NBS new-SPA reverse-engineered API)
  - `akshare` (akshare aggregator)
  - `csv` (FRED CSV download — same client as data-us)
  - `yfinance` (Yahoo Finance unofficial)
- `direction` (NBS/akshare indicators) is pre-computed `"Rising"` /
  `"Falling"` / `"Flat"` based on `latest` vs `prior`. Used by
  analysis-macro-regime for Investment Clock direction tagging.
- `cid` and `indicator_id` (NBS `_provenance` only) are NBS catalogue
  UUIDs preserved for primary-source traceability — humans verify
  individual prints by combining cid + indicator_id against NBS web UI.

### Provenance wrapper (`_provenance`)

Two distinct provenance shapes coexist in CN packs:

1. **Per-payload `_provenance`** — every fetched payload (yfinance info,
   yfinance history, NBS indicator, akshare indicator, FRED series)
   carries a `_provenance` object inherited from its underlying client.
   See per-source schemas. NBS adds `cid` + `indicator_id`; FRED follows
   the data-us FRED shape; yfinance follows the data-us yfinance shape.
2. **Pack-level `_provenance`** in `regime-pack` lists the 4 sub-fetch
   compositions (`nbs_indicators`, `akshare_indicators`, `fred_series`,
   `market_tickers`) so consumers know exactly which 36 series were
   composed without parsing the indicator maps.
3. **Tier-status `_provenance`** in `memo-fetch` is the **CN-specific
   integer-tier block** (`tier: 2`, `primary_source_status: "deferred"`,
   `primary_source_candidates: ["cninfo (CSRC)", "HKEXnews"]`).

Tier semantics across the toolkit:

- **Tier A** — official primary source (NBS new-SPA for macro, FRED for
  Fed-mediated cross-rates). Verdict-grade.
- **Tier 2** — unofficial / scraper (yfinance, akshare). OK for
  exploration; NOT for verdict-grade fundamentals on its own. CN memo
  bundles are Tier 2 by design until cninfo / HKEXnews integrations land.

## Cache TTL

Cache is opt-in via `INVESTING_TOOLKIT_CACHE` env var. When set, all
four underlying clients (yfinance / NBS / akshare / FRED) participate.
TTL defaults (per client; refer to canonical scripts in
`investing-toolkit/scripts/` for authoritative values):

- yfinance info: 1 hour
- yfinance OHLCV history: 1 hour
- NBS new-SPA: 12 hours (NBS publishes monthly; long TTL is safe)
- akshare: 6 hours (mixed daily LPR + monthly 社融 — short TTL is safest)
- FRED CSV: 6 hours

Each fetched payload reports `_cache: "hit"` or `_cache: "miss"`.

## Error envelope

All five packs implement **partial-failure semantics** (the pack itself
exits 0 even when an underlying client fails). Failure surfaces in three
ways:

1. **Nested slot replaced** by an error sentinel — see
   `cn-schema-error-envelope.json#/$defs/clientError` and `/$defs/invalidJson`.
   Consumers detect via `_error` key presence.
2. **Per-ticker error inside batch payload** — when a single ticker fails
   inside `yfinance --tickers ...` batch mode, that ticker's entry under
   `tickers: {}` carries `_error` and `_summary[ticker]` is a non-`"ok"`
   string. The batch envelope itself remains shaped per
   `batchInfo` / `batchHistory` with `_partial: true`. See
   `/$defs/batchTickerError`.
3. **Stderr-only ticker-normalisation warnings** — BSE codes (`/4,8`)
   and unrecognised digit lengths emit stderr warnings and pass through
   unchanged. Documented at
   `cn-schema-error-envelope.json#/$defs/tickerNormalizationWarnings`
   (under `$defs` since this is stderr-only and not a schema-validated
   stdout field).

Subprocess timeouts (reserved shape) produce
`{"_error": "client timeout after Ns", "_cmd": [...], "_returncode": -1}`.
Aligned with the data-us contract (uses `_error`, not bare `error`,
to match sibling shapes).

## Cross-skill consumers

```
data-cn  ──┬─→  analysis-dcf            ──→  report-equity-memo
           │    (reads memo-fetch)              (with explicit Tier-2
           │                                     warning surfaced)
           │
           ├─→  analysis-comps          ──→  report-equity-memo
           │    (reads comps-multiples)        report-stock-snapshot
           │
           ├─→  analysis-macro-regime   ──→  report-portfolio-review
           │    (reads regime-pack)            report-equity-memo (macro section)
           │
           └─→  analysis-screener       ──→  report-screener-list
                (reads screener-batch + snapshot)
```

Layer 2 `analysis-*` skills are **pure compute** (no I/O); they consume
the JSON output documented here verbatim. Layer 3 `report-*` skills
compose narrative on top of Layer 2 output and delegate verdict logic
to `domain-teams:investing-team` — which **must** surface the CN
memo-fetch Tier 2 status as a memo-footer disclosure (see
`tier_note` field).

## CN-specific deferred work (out of v2.0.0 scope)

- **cninfo (巨潮資訊網)** — CSRC-mandated annual / interim / 公告 disclosure
  for .SS / .SZ stocks. Tier A primary. Memo-fetch will upgrade to mixed
  Tier A + Tier 2 once integrated.
- **HKEXnews** — HKEX disclosure portal for .HK stocks. Tier A primary.
- **BSE (北京证券交易所)** — yfinance does not cover; primary-source
  integration would require a separate parser.
- **70-city housing price index** — NBS publishes monthly PDF only.
- **社融存量 同比增长** (TSF stock YoY) — only in PBOC press release
  text; akshare gives flow (增量) only.
- **Li Keqiang Index composite** — components available individually
  (electricity / rail freight / new loans); composite preset deferred
  pending market-consensus methodology.

These deferrals are documented in SKILL.md "Limitations" and surfaced
schema-side via the `memo-fetch._provenance.primary_source_candidates`
array.
