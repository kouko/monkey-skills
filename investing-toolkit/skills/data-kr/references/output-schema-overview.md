# data-kr — Output Schema Overview

JSON Schemas (Draft 2020-12) for every pack type emitted by
`skills/data-kr/scripts/pack.py`. Layer 2 / Layer 3 skills consume these
contracts; this document is the human-readable index.

## Schema files (this directory)

| Pack mode | Schema | Status notes |
|-----------|--------|--------------|
| `--pack snapshot` | [`schema-snapshot.json`](./schema-snapshot.json) | Tier 2 only (yfinance .KS / .KQ); DART deferred |
| `--pack memo-fetch` | [`schema-memo-fetch.json`](./schema-memo-fetch.json) | **Tier 2 only** — `_provenance.primary_source_status` always `"deferred"`; treat all financials as unverified scraper output |
| `--pack comps-multiples` | [`schema-comps-multiples.json`](./schema-comps-multiples.json) | Single + batch produce the **same** shape: `info: {ticker: {...}}` |
| `--pack screener-batch` | [`schema-screener-batch.json`](./schema-screener-batch.json) | Raw yfinance batch envelope under `batch` |
| `--pack regime-pack` | [`schema-regime-pack.json`](./schema-regime-pack.json) | Tier A primary — BOK ECOS-KEYSTAT (54 indicators / 13 groups) + FRED DEXKOUS fallback |
| (any pack) error path | [`schema-error-envelope.json`](./schema-error-envelope.json) | Top-level `error / _partial: true` envelope; pack.py exits 1 |

## Sample fixtures (in `investing-toolkit/tests/data/fixtures/`)

| Fixture | Source | Anchor ticker |
|---------|--------|---------------|
| `data-kr-snapshot-sample.json` | live `pack.py --pack snapshot` (history trimmed to 5 rows) | 005930.KS (Samsung Electronics) |
| `data-kr-memo-fetch-sample.json` | live `pack.py --pack memo-fetch` (history + financials trimmed) | 005930.KS |
| `data-kr-comps-multiples-sample.json` | live batch (`005930.KS,000660.KS`) | Samsung + SK Hynix |
| `data-kr-screener-batch-sample.json` | live batch (4 KOSPI large-caps) | 005930.KS / 000660.KS / 035420.KS / 051910.KS |
| `data-kr-regime-pack-sample.json` | live `--indicators rates,fx` (observations trimmed to last 5 per indicator) | n/a (macro) |

All fixtures validate against their corresponding schema (verified with
`jsonschema` 4.26.0).

> **Fixture trim convention**: To keep fixtures small while preserving
> validation coverage, history `data` arrays and observation lists are
> **head-truncated** (oldest 5 rows kept). The summary fields
> `latest_close` / `latest_date` (and equivalently `latest` /
> `reference_period` on macro indicators) reflect the most-recent
> observation **at fixture-capture time** and may not align with the
> head-truncated rows. Live pack.py output is not truncated. This
> convention applies to all fixtures across `data-{cn,jp,kr,tw,us}`.

## Pack-by-pack notes

### snapshot

```jsonc
{
  "pack": "snapshot",
  "country": "kr",
  "ticker": "005930.KS",
  "info":    { /* yfinance info dict */ },
  "history": { "period": "1y", "data": [...], ... },
  "_provenance": {
    "tier": "Tier 2 (yfinance unofficial)",
    "primary_source_status": "deferred",
    "primary_source_note": "Korea has no primary-source equity client wired in data-kr yet. Tier A would be DART (전자공시시스템, dart.fss.or.kr) — integration deferred ...",
    "exchange_suffix": "KS"
  }
}
```

`_provenance.exchange_suffix` is parsed from the normalized ticker (`KS`,
`KQ`, or `null` when the input did not end with a recognized suffix).

### memo-fetch

Identical envelope to snapshot but adds `financials_annual`,
`financials_quarterly`, switches `history.period` to `5y`, and pins
`tier: "Tier 2 only"` at the top level. `_provenance.primary_source_status`
is locked to `"deferred"` (schema constant) — DART is the future Tier A.

### comps-multiples (single = batch shape)

Wave 4 normalization in `pack.py` (`pack_comps_multiples`) unwraps the
yfinance batch envelope so consumers always see:

```jsonc
{
  "pack": "comps-multiples",
  "country": "kr",
  "tickers": ["005930.KS"],          // or many
  "info": {
    "005930.KS": { /* yfinance info — multiples readable here */ }
    // batch adds more keys here; single-mode produces a single-key dict.
  },
  "_provenance": {
    "multiples_set": ["trailingPE", "forwardPE", "evEbitda",
                      "priceToSales", "priceToBook"],
    ...
  }
}
```

This matches `analysis-comps`'s expectation: one access pattern,
`info[ticker][multiple]`, regardless of single vs batch invocation.
Verified live for both shapes against `schema-comps-multiples.json`.

### screener-batch

Wraps the **raw** yfinance batch envelope under `batch` — pack.py does
not unwrap it (analysis-screener projects fields itself). `batch.tickers`
is the per-ticker info dict; `batch._summary` is a per-ticker `'ok' /
error-string` map; `batch._partial` flips true if any single ticker fetch
failed.

### regime-pack (54 indicators / 13 groups)

Group set:

```
rates          (7)  — policy-rate, call-rate, cd-91d, koribor-3m,
                       treasury-3y, treasury-5y, corp-bond-3y
inflation      (5)  — cpi, core-cpi, ppi, import-pi, export-pi
growth         (7)  — gdp-qoq, gdp-nominal, ipi, manufacturing,
                       private-consumption, equipment-investment,
                       construction-investment
industry      (11)  — manufacturing-inventory, …, construction-orders
labor          (2)  — unemployment, employment-rate
trade          (3)  — current-account, terms-of-trade, goods-exports
money          (4)  — m1, m2, lf, household-credit
sentiment      (2)  — consumer-sentiment (BSI/CSI proxies for absent PMI)
cycle          (2)  — leading-cycle, coincident-cycle  (선행/동행 CI)
markets        (2)  — kospi, kosdaq
fx             (5)  — krw-usd*, krw-jpy, krw-eur, krw-cny, fx-reserves
realestate     (1)  — housing-price
demographics   (3)  — population, aging-ratio, fertility-rate
```

`*` `fx.krw-usd` is **FRED DEXKOUS** — ECOS-KEYSTAT does not expose a
clean KRW/USD daily series. All other indicators are BOK ECOS-KEYSTAT
via FinanceDataReader (Tier A). The schema treats this transparently:
`indicators.<slug>.code` is `"DEXKOUS"` for the FRED entry and `"K###"`
for ECOS entries, and `_provenance.primary_source_status` is
`"available"` (the only KR pack with this status).

PMI is **not fetched** — S&P Global South Korea Manufacturing PMI is
licensed commercial data. The closest free proxies are the `sentiment`
group (consumer-sentiment K252 + economic-sentiment K269). PMI is
documented as null-by-design; consumers should not retry on its
absence.

Per-indicator payload shape:

```jsonc
{
  "preset":  "policy-rate",
  "name":    "BOK Base Rate (한국은행 기준금리)",
  "code":    "K051",
  "fetched_at": "2026-05-01T15:10:10Z",
  "_cache":  "miss",
  "_source": "fdr_ecos",
  "observations": [
    {"date": "20260428", "value": 2.5},
    {"date": "20260429", "value": 2.5}
  ],
  "latest":    {"date": "20260429", "value": 2.5},
  "prior":     {"date": "20260428", "value": 2.5},
  "direction": "Flat",            // Rising / Falling / Flat
  "count":     6732,
  "_provenance": { /* fdr_client provenance block */ }
}
```

### error envelope

Used both at the top level (pack.py exits 1) and inline for nested
failures. Always carries `_partial: true`. For regime-pack with an
unknown group name:

```jsonc
{
  "error": "unknown indicator group(s): ['bogus']",
  "available": ["rates", "inflation", ..., "demographics"],
  "_partial": true
}
```

Subprocess failures (uv missing / client crash / non-JSON stdout)
inline `error` plus optional `stderr`, `stdout_tail`, `returncode` fields
inside the affected sub-block — the surrounding pack envelope still
returns and the consumer must inspect each section.

## Ticker normalization warnings

Whenever pack.py's `normalize_ticker` sees a token that is neither
`.KS` / `.KQ` suffixed nor a 6-digit numeric code, it:

1. Prints `[data-kr WARN] Unrecognized KR ticker format: '<token>' …` to stderr.
2. Records the same string under
   `_provenance.ticker_normalization_warnings: [...]` on the resulting pack.
3. **Does not refuse** the token — it passes through unchanged so the
   yfinance failure surfaces with full context.

The schemas type this field as an optional `array<string>` on the
`_provenance` object of every equity-side pack (snapshot, memo-fetch,
comps-multiples, screener-batch). regime-pack does not consume tickers
and so does not carry this field.

The `--kosdaq` flag flips the auto-suffix default from `.KS` to `.KQ`
for bare numeric input but does not affect already-suffixed tokens — a
mixed list is normalized in one pass without overrides.

## Validation recipe

```bash
INVESTING_TOOLKIT_CACHE=/tmp/kr-cache \
  uv run skills/data-kr/scripts/pack.py \
  --ticker 005930.KS --pack snapshot > /tmp/kr-snap.json

uv run --with jsonschema python3 - <<'PY'
import json, jsonschema
schema = json.load(open(
    'investing-toolkit/skills/data-kr/references/schema-snapshot.json'))
sample = json.load(open('/tmp/kr-snap.json'))
jsonschema.validate(sample, schema)
print('KR snapshot live output validates')
PY
```

Run analogous one-liners for the other four equity packs and for
`regime-pack --indicators rates,fx`. The bundled fixtures provide
already-trimmed examples that validate without re-fetching.
