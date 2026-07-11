# data-us output schema overview

Schemas in this directory document the JSON output produced by
`investing-toolkit/skills/data-us/scripts/pack.py` for each of the five US
pack types. Each schema is JSON-Schema draft-07, validated by the
`jsonschema` Python library (used in `tests/data/test_pack_schemas.py`).
Schemas are descriptive, not strictly closed — `additionalProperties: true`
is the default because upstream sources (yfinance / FRED / SEC EDGAR) evolve
and we want forward compatibility, not lockdown.

## Pack-to-schema map

| Pack | Schema file | Tier | Use case |
|------|-------------|------|----------|
| `snapshot` | [`schema-snapshot.json`](schema-snapshot.json) | 2 | Quick yfinance overview (info + 2y price) for a single ticker. Feeds `analysis-screener` lightweight paths and `report-stock-snapshot`. |
| `memo-fetch` | [`schema-memo-fetch.json`](schema-memo-fetch.json) | A + 2 | Heavy bundle: yfinance + SEC EDGAR (10-K/10-Q/8-K + XBRL facts). Feeds `analysis-dcf` and `report-equity-memo`. |
| `comps-multiples` | [`schema-comps-multiples.json`](schema-comps-multiples.json) | 2 | Multiples-only filter on yfinance info. Single (anchor) or batch (peers). Feeds `analysis-comps`. |
| `screener-batch` | [`schema-screener-batch.json`](schema-screener-batch.json) | 2 | Lightweight screener-input fields, batch only (≥2 tickers). Feeds `analysis-screener`. |
| `regime-pack` | [`schema-regime-pack.json`](schema-regime-pack.json) | A | FRED macro indicator groups, no ticker dimension. Feeds `analysis-macro-regime`. |
| Shared | [`schema-error-envelope.json`](schema-error-envelope.json) | — | Reusable provenance + error wrapper definitions, `$ref`-d by all five packs. |

## Sample fixture trim convention

> **Fixture trim convention**: To keep fixtures small while preserving
> validation coverage, history `data` arrays and observation lists in
> `tests/data/fixtures/data-us-*.json` are **head-truncated** (oldest
> rows kept). The summary fields `latest_close` / `latest_date` (and
> equivalently `latest` / `reference_period` on macro indicators)
> reflect the most-recent observation **at fixture-capture time** and
> may not align with the head-truncated rows. Live `pack.py` output is
> not truncated. This convention applies to all fixtures across
> `data-{cn,jp,kr,tw,us}`.

## Field dictionary (cross-pack conventions)

### Currency and units

- All US-tickered yfinance fields (`marketCap`, `enterpriseValue`,
  `regularMarketPrice`, `trailingEps`, `totalRevenue`, etc.) are in **USD**
  and **raw values**, NOT in millions or thousands. A `marketCap` of
  `4138099539968` is $4.138T.
- `dividendYield` from yfinance is reported as a **percentage** (e.g.
  `0.38` means 0.38%, not 38%). Consumers must NOT multiply by 100 again.
  Cross-skill spec note: data-jp / data-tw normalize this to a decimal
  fraction in their normalization layer; data-us preserves Yahoo's native
  percentage to keep the schema purely fetch-only. Layer 2
  (analysis-screener / analysis-comps) is responsible for unit alignment
  across countries.
- FRED series values are in their **native FRED units** (e.g. percent for
  yields, index level for CPIAUCSL, billions of chained 2017 USD for
  GDPC1). Consumers should consult the FRED series page for unit detail.

### Time zones

- `fetched_at` (top-level, on every pack) is **UTC ISO 8601** with
  microsecond precision.
- `_provenance.fetched_at` (nested per-source) is also UTC ISO 8601, but
  client-script stamped (typically second precision).
- SEC EDGAR `filingDate` is **Eastern Time (US/Eastern)** per SEC
  convention, formatted as `YYYY-MM-DD` (no time component).
- yfinance `price_history.data[].date` is **US/Eastern market date** as
  `YYYY-MM-DD` (one record per US trading day).
- FRED observation `date` is the **period-start date** in the series'
  native frequency (daily / weekly / monthly / quarterly).

### Special types

- `cik` (SEC) renders as either `integer` or zero-padded 10-char `string`
  depending on the client path; consumers should accept both.
- `dei_concepts` and `us_gaap_concepts` (in `sec_facts`) are unsorted
  arrays of XBRL concept names; consumers fetch a specific concept's
  values via a separate `sec_edgar_client.py --action facts --concept X`
  call, not bundled here for size.
- ROC (民國) year is **N/A** for data-us. Documented here as a
  cross-skill reminder: `data-tw` returns Western years in `date` fields,
  but report-layer formatting may need ROC conversion.

### Provenance wrapper (`_provenance`)

Every fetched payload carries a `_provenance` object with at minimum
`source`, `source_authority`, `data_type`, `update_cycle`, `typical_lag`,
`fetched_at`. See `schema-error-envelope.json#/definitions/provenance` for
the full field set including the `tier` enum (`A`, `2`, `2-gap`,
`tier_1`, `tier_2`). `data_type` common values: `official_regulatory_filing`
(SEC filings), `official_macro_indicator` / `official_government_statistics`
(FRED — both seen in the wild; the latter used by FRED preset bundles),
`unofficial_scraper` (yfinance).

Tier semantics:

- **Tier A / `tier_1`** — official primary source (SEC EDGAR for
  fundamentals, FRED for macro). Verdict-grade.
- **Tier 2 / `tier_2`** — unofficial / scraper (yfinance). OK for
  exploration and price; NOT for verdict-grade fundamentals (use SEC
  EDGAR via `memo-fetch` instead).
- **`2-gap`** — Tier 2 used because Tier A is unavailable for this
  specific field.

## Cache TTL

Cache is opt-in via `INVESTING_TOOLKIT_CACHE` env var (path to a cache
directory). When set, all three underlying clients (yfinance / SEC EDGAR /
FRED) participate. Cache TTL defaults (per client):

- yfinance info: 1 hour
- yfinance OHLCV history: 1 hour
- SEC EDGAR filings index: 24 hours
- SEC XBRL facts: 24 hours
- FRED CSV: 6 hours

Each fetched payload reports `_cache: "hit"` or `_cache: "miss"`. Refer
to the canonical client scripts in `investing-toolkit/scripts/` for
authoritative TTL values; the schemas accept any string for `_cache`.

## Error envelope

All five packs implement **partial-failure semantics** (the pack itself
exits 0 even when an underlying client fails). Failure surfaces in two
ways:

1. **Nested slot replaced.** When the `yfinance_client.py` /
   `sec_edgar_client.py` / `fred_client.py` subprocess fails, the
   corresponding slot (`company_info`, `price_history`, `sec_filings`,
   `sec_facts`, `groups.<name>`, or `groups.<name>.series.<series_id>`)
   is replaced by an `error_wrapper` object — see
   `schema-error-envelope.json#/definitions/error_wrapper`. Consumers
   detect this via `error` (or `_error`) key presence.

2. **Top-level `error` for batch packs.** When the entire batch fetch
   fails for `comps-multiples` / `screener-batch`, the top-level pack
   carries `tickers: {}` AND a top-level `error` field with the client
   error blob. The `tickers` map itself never contains a `_error`
   sentinel — consumers can safely iterate `tickers.items()` without
   filtering.

Subprocess timeouts produce
`{"error": "client timeout after Ns", "_cmd": [...], "_returncode": -1}`.

## Cross-skill consumers

```
data-us  ──┬─→  analysis-dcf            ──→  report-equity-memo
           │    (reads memo-fetch)
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
compose narrative on top of Layer 2 output and delegate verdict logic to
`domain-teams:investing-team`.
