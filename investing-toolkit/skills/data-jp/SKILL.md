---
name: data-jp
description: |
  Layer-1 fetch-only Japan data bundler — yfinance .T, EDINET (金融庁 Tier A), TDnet, BOJ, e-Stat, ECB behind one pack.py facade with 5 pack types. EDINET_API_KEY routes to Tier-A filings, else yfinance fallback. No analysis.
---

# data-jp

**Layer 1 contract** — fetch-only Japan equity + macro data bundler. Returns
structured JSON for Layer 2 (`analysis-*`) and Layer 3 (`report-*`) skills.
Does **not** analyze, score, or render reports.

This skill merges the fetch logic from `japan-macro` (BOJ + e-Stat + ECB) and
`japan-stock-snapshot` (EDINET + TDnet + yfinance .T) under a single
`pack.py` facade, with Tier-A / Tier-2 routing handled internally.

---

## Pack types

| Pack              | Single | Batch | Use case                                        |
|-------------------|:------:|:-----:|-------------------------------------------------|
| `snapshot`        |   ✅   |   ⚠   | Quick overview card (info + 2y price + TDnet)   |
| `memo-fetch`      |   ✅   |   ❌  | Equity memo full data (Tier A or Tier 2)        |
| `comps-multiples` |   ✅   |   ✅  | Comps analysis (anchor + N peers, multiples-only) |
| `screener-batch`  |   ❌   |   ✅  | Screener (50–500 tickers, lightweight fields)   |
| `regime-pack`     |  n/a   |  n/a  | JP macro indicators only (no per-ticker dim)    |

---

## Ticker convention

JP tickers are passed as **4-digit 証券コード** (e.g. `7203`, `6758`,
`9984`). `pack.py` auto-appends `.T` when calling `yfinance_client.py` and
strips suffixes for `edinet_client.py` / `tdnet_client.py`. Inputs with `.T`
or `.TO` already attached are accepted and normalized.

`{ticker4}` placeholder below = bare 4-digit code.

---

## EDINET tier routing (memo-fetch only)

`pack.py` checks the `EDINET_API_KEY` environment variable at runtime:

| Key state | Path                              | Provenance label                                   |
|-----------|-----------------------------------|----------------------------------------------------|
| set       | EDINET filing-summary + 180/220/350 events | `tier_a` — `Tier A (EDINET 金融庁 primary-source)` |
| unset     | yfinance financials annual + quarterly      | `tier_2` — `Tier 2 fallback` + `upgrade_hint`       |

Tier 2 fallback `_provenance.upgrade_hint` includes the EDINET registration
URL (https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html).
Layer 3 report skills surface the upgrade hint to the user when emitting the
final card.

`snapshot`, `comps-multiples`, `screener-batch`, `regime-pack` never need
`EDINET_API_KEY` — they depend on always-public sources only.

---

## CLI

All commands run from this skill directory and inherit the cache env
(`INVESTING_TOOLKIT_CACHE` / `CLAUDE_PLUGIN_DATA`).

### snapshot (single ticker)

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker {ticker4} --pack snapshot
```

Bundles:
- `yfinance_client.py --action info`        (price, marketCap, P/E, sector...)
- `yfinance_client.py --action history --period 2y`
- `tdnet_client.py --ticker {ticker4} --limit 20`

### memo-fetch (single ticker, tier-routed)

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker {ticker4} --pack memo-fetch
```

Tier A path (EDINET_API_KEY set):
- snapshot bundle (above)
- `edinet_client.py --action filing-summary --ticker {ticker4} --days 365`
- `edinet_client.py --action list-filings --forms 180,220,350 --days 180 --limit 15`

Tier 2 fallback path (no key):
- snapshot bundle
- `yfinance_client.py --action financials --period annual`
- `yfinance_client.py --action financials --period quarterly`
- `_provenance.tier_label = "Tier 2 fallback"`

### comps-multiples (single OR batch)

```
# anchor only
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 7203 --pack comps-multiples

# anchor + peers
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --tickers 7203,7267,7269,7270 --pack comps-multiples
```

Returns yfinance `info` filtered to the multiples-only whitelist:
`trailingPE / forwardPE / priceToSales / priceToBook / enterpriseToEbitda /
enterpriseToRevenue / marketCap / enterpriseValue`.

### screener-batch (batch)

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --tickers 7203,6758,9984,8035,8316 --pack screener-batch
```

Lightweight `yfinance` batch — info + 1y price history. No EDINET, no TDnet.
Designed for `report-screener-list` consumption where Layer-3 splits a
mixed-market ticker list by country and dispatches to per-country pack
scripts in parallel.

### regime-pack (no ticker)

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --pack regime-pack
```

Bundles JP macro Tier-A primary sources:
- BOJ Call Rate O/N (`boj_client.py --db FM01 --code STRDCLUCON`)
- BOJ Tankan 企業物価見通し 1Y/3Y/5Y (`boj_client.py --tankan-price-outlook`)
- e-Stat preset bundle: `cpi,core-cpi,ip,unemployment,jgb10y`
- ECB JP real 10Y yield ex-post (`ecb_client.py --series M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA`)

v2.0.0 ships a focused starter regime-pack covering the IC / GIP regime-
classification core (rates / inflation / growth / real-rates). The full
BOJ + e-Stat + ECB indicator catalogue (labor / consumption / tankan /
forex / money / balance) is preserved as fetch capability via the bundled
clients (boj_client.py, estat_client.py, ecb_client.py); Layer 3 / 2 callers
that need additional series can invoke the clients directly. Future versions
will expand the pack fields based on Layer-3 demand.

---

## Output shape

All packs share the envelope:

```json
{
  "pack": "snapshot",
  "ticker": "7203",
  "yf_ticker": "7203.T",
  "fetched_at": "2026-05-01T00:00:00+00:00",
  "...pack-specific blocks...": "...",
  "_provenance": {
    "tier": "tier_1",
    "tier_label": "Tier 1 (yfinance + TDnet, no key needed)",
    "sources": ["Yahoo Finance (.T)", "TDnet via Yanoshin"]
  }
}
```

`memo-fetch` adds `fundamentals.tier` (`tier_a` or `tier_2`) and a
top-level `material_events` block. The Tier 2 fallback variant carries
`_provenance.upgrade_hint` with the EDINET registration URL so Layer-3
report skills can surface it to the user.

`screener-batch` and `comps-multiples` use a `tickers[]` array instead of a
single-ticker envelope.

`regime-pack` uses a `groups{}` object grouped by indicator family
(rates / inflation / real_rates).

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

## Bundled clients (canonical copies)

All six client scripts are byte-identical copies of
`investing-toolkit/scripts/{name}_client.py` (verified MD5). Drift detection
should be wired into the v2.0.0 `sync-scripts.sh` follow-up.

| Script               | Source             | Auth?               |
|----------------------|--------------------|---------------------|
| `yfinance_client.py` | Yahoo Finance      | none                |
| `edinet_client.py`   | EDINET v2 (金融庁)  | `EDINET_API_KEY`    |
| `tdnet_client.py`    | Yanoshin TDnet idx | none                |
| `boj_client.py`      | BOJ Time-Series    | none                |
| `estat_client.py`    | 統計ダッシュボード    | none                |
| `ecb_client.py`      | ECB Data Portal    | none                |

---

## Layer contract (v2.0.0)

```
data-jp           (this skill — fetch only, returns JSON)
   │
   ▼
analysis-{dcf|comps|screener|technical|portfolio|macro-regime}
   │
   ▼
report-{equity-memo|stock-snapshot|portfolio-review|screener-list}
```

This skill **must not**:
- compute scores / ratios / indicators (analysis layer's job)
- render Markdown / cards / memos (report layer's job)
- delegate to `domain-teams:*` (only report layer delegates)

This skill **must**:
- expose every external data source via `pack.py` (no scattered ad-hoc clients)
- carry primary-source provenance on every payload
- handle Tier A / Tier 2 routing internally and label the result
- support both `--ticker` (single) and `--tickers` (batch) where the pack
  semantics permit

---

## See also

- `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md`
  — §4.2 Layer 1 data skill spec
- `investing-toolkit/docs/adr/0001-data-analysis-report-layers.md` — ADR
  pinning the three-layer architecture
- v1.x source skills (`japan-macro`, `japan-stock-snapshot`) were deleted
  in v2.0.0; their indicator catalogues + EDINET tier-routing rationale
  are now embedded in this skill's pack contracts. Historical reference
  docs preserved in git history (pre-v2.0.0 commits)

---

日本株・日本マクロのデータ取得層。EDINET API キーが設定されていれば
金融庁の primary-source filings、未設定なら yfinance financials
（"Tier 2 fallback" として明示）に自動ルーティング。

日本股票與日本總經的資料抓取層。EDINET API key 已設定則走金融庁
primary-source filings，未設定則自動退回 yfinance financials（明確標
示 "Tier 2 fallback"）。
