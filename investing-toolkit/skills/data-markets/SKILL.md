---
name: data-markets
description: |
  Layer-1 unified data fetch across US/JP/TW/KR/CN equities + macro — one
  pack.py facade, auto market detection from ticker suffix (.TW/.KS/.SS/.T/
  bare-4-digit), 5 pack types (snapshot / memo-fetch / comps-multiples /
  screener-batch / regime-pack). Pure I/O, no analysis. Consolidates the
  per-country data-{us,jp,tw,kr,cn} client scripts behind one CLI + shared
  cache layer.
---

# data-markets

**Layer 1 — Data** in the investing-toolkit three-layer architecture
(Data → Analysis → Report). Pure fetch across 5 markets — 18 client
scripts (yfinance, SEC EDGAR, FRED, EDINET, TDnet, BOJ, e-Stat, ECB, MOPS,
TWSE/TPEx OpenAPI, FinMind, CBC, DGBAS, NDC, stat.gov.tw, NBS, akshare,
FinanceDataReader) behind one CLI. Does not analyze, score, or compose
narrative — output is structured JSON for a Layer 2 `analysis-*` skill or
a Layer 3 `report-*` orchestrator.

## THE invocation

One command shape covers every market and pack type:

```
uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 2330.TW --pack snapshot
```

No plugin-data env var is needed or should be passed here — that class
of variable is hook-context-only and is not set in a normal tool
invocation (an unset/misexpanded one used to silently collapse to a
bogus literal path in the pre-migration clients). Cache location is
resolved internally by `cache_util.py` via an XDG-style ladder, highest
precedence first:

```
INVESTING_TOOLKIT_CACHE env var  >  $XDG_CACHE_HOME/investing-toolkit  >  ~/.cache/investing-toolkit
```

The resolved directory is probed with a real write; if unwritable, a loud
`WARNING:` line prints to stderr and resolution falls back to a tempdir —
it never fails silently and never raises unless even the tempdir fallback
is unwritable.

## Pack types

| Pack | Ticker mode | Worked example |
|---|---|---|
| `snapshot` | single | `pack.py --ticker AAPL --pack snapshot` |
| `memo-fetch` | single (heavy) | `pack.py --ticker 7203 --pack memo-fetch` |
| `comps-multiples` | single or batch | `pack.py --tickers 005930.KS,000660.KS --pack comps-multiples` |
| `screener-batch` | batch (≥2) | `pack.py --tickers 600519.SS,000858.SZ,300750.SZ --pack screener-batch` |
| `regime-pack` | none — **requires `--market`** | `pack.py --pack regime-pack --market tw` |

`regime-pack` has no ticker dimension; omitting `--market` is a usage
error (exit 64).

## Ticker-suffix routing

| Suffix / form | Market |
|---|---|
| `.TW` / `.TWO` | `tw` |
| `.KS` / `.KQ` | `kr` |
| `.SS` / `.SZ` / `.HK` | `cn` |
| `.T` or bare 4-digit | `jp` |
| anything else | `us` (historical default — surfaced as a `_status.warnings` entry, not silent) |

`--market <us\|jp\|tw\|kr\|cn>` overrides detection entirely. **One
market per invocation**: a `--tickers` list whose members resolve to more
than one market is rejected (exit 64) rather than silently picking one —
split cross-market batches at the caller.

## Exit contract — always check `_status` first

| Exit | Meaning | `_status` fields |
|---|---|---|
| `0` | all sections ok | `status: "ok"` |
| `2` | some sections failed | `status: "partial"`, `failed_sections: [...]` |
| `1` | all sections failed, or an unexpected exception | `status: "failed"`, `traceback` (on crash) |
| `64` | usage error (bad args/pack name, mixed-market tickers, missing `--market` for regime-pack) | `status: "usage_error"`, `message` |

`_status` is injected at the top level of every emitted JSON object.
This is the fail-loud contract: **never consume a pack payload without
checking `_status.status` first**. A `partial` (exit 2) result still
emits every section it could fetch — only `_status.failed_sections`
tells you which ones to distrust.

## Cache-hit metadata

A payload served from cache carries three bookkeeping keys injected by
`cache_util.load_cache`: `_cache: "hit"`, `_cache_age_seconds`,
`_cache_ttl_seconds`. A fresh fetch has no `_cache` key (or `_cache:
"miss"` where the client sets it explicitly). Downstream skills may use
these to decide whether to force a re-fetch.

## API keys

| Env var | Market | Effect |
|---|---|---|
| `EDINET_API_KEY` | jp | Unlocks Tier-A EDINET (金融庁) primary-source filings for `memo-fetch`. Unset → yfinance Tier-2 fallback with `_provenance.upgrade_hint` pointing to free EDINET registration. |
| `FRED_API_KEY` | us (+ macro cross-source for kr/cn) | Optional — the CSV endpoint works keyless; the key only enables the more flexible JSON API. |
| `FINMIND_API_TOKEN` | tw | Optional — anonymous access is 300 req/hr; a free token raises this to 600 req/hr. |

Per-market source inventories, authority tiers, additional keys, rate
limits, and caveats: see `references/market-us.md`,
`references/market-jp.md`, `references/market-tw.md`,
`references/market-kr.md`, `references/market-cn.md`. External-surface
grounding for the cache-layer migration itself: `references/migration-grounding.md`.

---

統一 5 市場（美/日/台/韓/中）資料抓取層 · 5市場統合データ取得レイヤー
