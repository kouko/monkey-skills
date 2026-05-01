---
name: report-screener-list
description: >-
  Layer 3 orchestrator for cross-country stock screening. Parses a comma-separated
  ticker list (US / TW / JP / KR / CN mixed allowed), groups by country suffix,
  fans out parallel `data-{country}/pack.py --pack screener-batch` fetches,
  concatenates batches, runs `analysis-screener` (pure compute — preset filters +
  composite score + ranking), then renders a Markdown top-N table via
  `screener_format.py`. 8 presets: value / deep-value / quality / high-dividend /
  growth / growth-value / momentum / balanced. クロスカントリー個別銘柄スクリーナー。
  跨市場個股篩選器。
---

# report-screener-list

> **Layer 3 contract (v2.0.0)**: Orchestration only. Data fetch is delegated to
> `data-{country}/pack.py --pack screener-batch`. Filtering / scoring / ranking
> is delegated to `analysis-screener/scripts/screener_compute.py` (pure compute,
> no I/O). This skill only does **(1) ticker routing**, **(2) parallel batch
> dispatch**, **(3) batch concatenation**, **(4) Markdown formatting** of the
> ranked JSON via `screener_format.py`.

Replaces the orchestration portion of legacy `stock-screener`. The compute
portion moved to `analysis-screener`. The fetch portion moved to
`data-{country}/pack.py --pack screener-batch`.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `tickers` | yes | — | Comma-separated; mixed-country allowed: `AAPL,MSFT,2330.TW,7203,005930.KS` |
| `--preset` | no | `balanced` | One of 8: `value`, `deep-value`, `quality`, `high-dividend`, `growth`, `growth-value`, `momentum`, `balanced` |
| `--top-n` | no | 10 | Return top N ranked results |
| `--pe-max` | no | preset | Override: trailing PE ≤ value |
| `--pb-max` | no | preset | Override: price/book ≤ value |
| `--rsi-min` | no | preset | Override: RSI ≥ value |
| `--rsi-max` | no | preset | Override: RSI ≤ value |
| `--above-sma200` | no | preset | Override: require price > SMA-200 |
| `--min-volume` | no | preset | Override: avg daily volume ≥ value (shares) |
| `--div-min` | no | preset | Override: dividend yield ≥ value (decimal, 0.02 = 2%) |
| `--roe-min` | no | preset | Override: ROE ≥ value (decimal) |
| `--output-language` | no | `en` | `en` / `zh-TW` / `ja` — table headers + footer language |

---

## Preset Strategies

User-supplied flags override preset defaults when both specified. (Same table
as `analysis-screener/SKILL.md` — kept here for orchestrator-side discoverability.)

### Value strategies

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `value` | PE ≤ 15, PB ≤ 1.5, div ≥ 2%, ROE ≥ 5% | valuation 60%, trend 25%, momentum 15% | Classic value |
| `deep-value` | PE ≤ 8, PB ≤ 0.5 | valuation 70%, trend 20%, momentum 10% | Contrarian deep discount |
| `quality` | PE ≤ 15, PB ≤ 1.5, ROE ≥ 15%, div ≥ 2% | valuation 40%, quality 35%, trend 25% | Compounders |
| `high-dividend` | div ≥ 3%, PE ≤ 20, ROE ≥ 5% | valuation 55%, trend 25%, momentum 20% | Income |

### Growth strategies

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `growth` | ROE ≥ 15%, rev-growth ≥ 5%, earnings-growth ≥ 10% | momentum 45%, trend 35%, valuation 20% | Quality growth |
| `growth-value` | PE ≤ 20, ROE ≥ 10%, rev-growth ≥ 5% | valuation 40%, momentum 35%, trend 25% | GARP |

### Tactical strategies

| Preset | Filters | Scoring Emphasis | Style |
|--------|---------|-----------------|-------|
| `momentum` | RSI 50–80, above SMA200 | momentum 50%, trend 40%, valuation 10% | Trend following |
| `balanced` | (none) | valuation 40%, momentum 30%, trend 30% | Baseline — default |

---

## Cross-country routing

The same suffix→country map used by `report-stock-snapshot` and
`report-portfolio-review`. Apply the **first** rule that matches:

| Suffix / Pattern | Country | data-{country} | Examples |
|---|---|---|---|
| `.TW`, `.TWO` | `tw` | `data-tw` | `2330.TW`, `2454.TWO` |
| `.T`, `.TO` | `jp` | `data-jp` | `7203.T`, `9984.TO` |
| 4-digit numeric only (no suffix) | `jp` | `data-jp` | `7203`, `9984` |
| `.KS`, `.KQ` | `kr` | `data-kr` | `005930.KS`, `035720.KQ` |
| `.SS`, `.SZ`, `.HK` | `cn` | `data-cn` | `600519.SS`, `000333.SZ`, `0700.HK` |
| Alphabetic (no suffix) | `us` | `data-us` | `AAPL`, `MSFT`, `BRK-B` |

Tickers that do not match any rule are surfaced as an `unrouted` warning
(included in the formatter footer).

---

## How It Works

### Step 1 — Parse + group by country

Split user input on `,`, trim whitespace, normalize to upper-case (preserve
suffix dots). Bucket by the routing table above into per-country lists.

### Step 2 — Parallel batch fetch (one Bash call per non-empty country group)

The main agent dispatches multiple Bash tool invocations **in parallel** (one
message, multiple tool calls — see superpowers `dispatching-parallel-agents`).
Each call writes its country-scoped batch JSON to a unique temp file:

```bash
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache \
  uv run ${CLAUDE_SKILL_DIR}/../data-us/scripts/pack.py \
  --tickers AAPL,MSFT --pack screener-batch > /tmp/screener-us.json

INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache \
  uv run ${CLAUDE_SKILL_DIR}/../data-tw/scripts/pack.py \
  --tickers 2330.TW,2454.TWO --pack screener-batch > /tmp/screener-tw.json

# … similarly for jp / kr / cn groups when present
```

If any country batch fails entirely (network error, all tickers invalid), keep
going with `_partial: true` semantics — record the failure in warnings but do
not abort.

### Step 3 — Concatenate batches into one input

Each `pack.py --pack screener-batch` returns:

```json
{
  "pack": "screener-batch",
  "fetched_at": "2026-...",
  "tickers": {
    "AAPL": {"trailingPE": 34.35, "priceToBook": 45.2, "ticker": "AAPL", ...},
    "MSFT": {...}
  }
}
```

`analysis-screener/scripts/screener_compute.py` accepts both **bare lists** and
**wrapped packs**, including the `{"tickers": {ticker: {...}}}` dict form
(see `_normalize_records` in that script). To concatenate multiple country
packs into one input, the main agent merges the `tickers` dicts:

```python
import json, pathlib
combined = {"tickers": {}, "_provenance": []}
for f in ["/tmp/screener-us.json", "/tmp/screener-tw.json"]:
    p = json.loads(pathlib.Path(f).read_text())
    combined["tickers"].update(p.get("tickers", {}))
    combined["_provenance"].append({
        "source": f, "pack": p.get("pack"),
        "fetched_at": p.get("fetched_at"),
    })
pathlib.Path("/tmp/screener-combined.json").write_text(json.dumps(combined))
```

(Or via `jq -s 'reduce .[] as $x ({tickers: {}}; .tickers += $x.tickers)'` if
shelling out is preferred.)

### Step 4 — Pure-compute filter + score + rank

```bash
uv run ${CLAUDE_SKILL_DIR}/../analysis-screener/scripts/screener_compute.py \
  --input /tmp/screener-combined.json \
  --preset {preset} --top-n {N} \
  [--pe-max ...] [--rsi-min ...] [--above-sma200] \
  > /tmp/screener-ranked.json
```

The compute script handles preset filter logic, override merging, weight
normalization, and per-ticker missing-data fallbacks (neutral defaults +
`warnings` array). See `analysis-screener/SKILL.md` for the full algorithm
and JSON output schema.

### Step 5 — Render Markdown top-N table

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/screener_format.py \
  --input /tmp/screener-ranked.json \
  [--lang en|zh-TW|ja] \
  > /tmp/screener-report.md
```

The formatter is **pure** — no fetch, no scoring. It reads the
`analysis-screener` output and emits a Markdown document with:

- Header — preset name + filter summary + universe size + top-N
- Top-N ranked table — rank / ticker / composite_score / valuation /
  momentum / trend / quality breakdown / key metrics (P/E, P/B, RSI, SMA200)
- Filtered-out summary — count + first 3 with reason (collapsed for the rest)
- Warnings — collapsible note when any ranked record carries `warnings`
- Provenance footer — data source + compute layer + asof timestamp

---

## Example Usage

```bash
# Single-country US, value preset, top 5
/invest-screen AAPL,MSFT,NVDA,GOOGL,META --preset value --top-n 5

# Mixed JP + TW + KR, momentum preset
/invest-screen 7203,2330.TW,005930.KS --preset momentum

# US growth with manual P/E cap override
/invest-screen AAPL,MSFT,NVDA --preset growth --pe-max 50

# Default balanced (no preset filters), top 10
/invest-screen AAPL,MSFT,2330.TW,7203,005930.KS
```

---

## Score Interpretation

Composite score is **relative within the screened universe**, not absolute. A
score of 70 means this ticker ranks well against the others in your input list
— it does NOT mean "buy".

**After screening**: route top candidates to:

- `report-stock-snapshot` for a deeper data card
- `report-equity-memo` (which delegates to `domain-teams:investing-team`) for
  an investment verdict

---

## Limitations

- yfinance `trailingPE`, `priceToBook`, `returnOnEquity` can be stale (~daily)
- yfinance volume is latest-day, not average — use `--min-volume` cautiously
- Cross-country lists pay a per-country fetch round-trip; very large lists
  (50+ tickers in 5 countries) may take 30–60s
- TW / JP / KR / CN packs may have country-specific field gaps — surfaced as
  per-record `warnings` (neutral defaults applied, see `analysis-screener`)
- TW OTC stocks (`.TWO`) sometimes lack PE / PB via yfinance

---

<!-- i18n -->
日本語: クロスカントリー個別銘柄スクリーナーのオーケストレーター。
ティッカーリスト（US / TW / JP / KR / CN 混在可）を国別に分割し、
`data-{country}/pack.py --pack screener-batch` を並列実行してデータを取得、
`analysis-screener` で純計算（プリセット 8 種：value / deep-value / quality /
high-dividend / growth / growth-value / momentum / balanced）+ ランキングを
行い、`screener_format.py` で Markdown のトップ N 表に整形する。

繁體中文：跨市場個股篩選器的編排層。將使用者的個股列表（US / TW / JP / KR /
CN 混合皆可）依後綴分組，並行呼叫 `data-{country}/pack.py --pack
screener-batch` 取得資料，交由 `analysis-screener` 進行純計算（八種策略：
value / deep-value / quality / high-dividend / growth / growth-value /
momentum / balanced）+ 排序，最後以 `screener_format.py` 輸出 Markdown 排名表。
