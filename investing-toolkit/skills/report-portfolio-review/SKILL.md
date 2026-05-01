---
name: report-portfolio-review
description: >-
  Layer 3 orchestrator that produces a portfolio P&L review document
  (Markdown) with optional macro-regime overlay. Parses holdings, groups
  tickers by country (US/JP/TW/KR/CN), batch-fetches prices via
  data-{country}/pack.py --pack screener-batch in parallel, runs
  analysis-portfolio for pure compute, optionally overlays
  analysis-macro-regime, then renders Markdown via review_format.py.
  ポートフォリオ評価レポート — マクロレジーム重ね合わせ可。
  投資組合損益回顧 — 可疊加總經 regime overlay。
---

# report-portfolio-review

Layer 3 (Report) orchestrator for portfolio review. Composes:
- **Layer 1** — `data-{country}/pack.py --pack screener-batch` (per country, parallel)
- **Layer 2** — `analysis-portfolio/scripts/portfolio_compute.py` (pure P&L compute)
- **Layer 2** — `analysis-macro-regime/scripts/regime_compose.py` (optional overlay)
- **Layer 3** — `report-portfolio-review/scripts/review_format.py` (pure Markdown formatter)

Rebalance / Kelly-sizing / sector concentration narrative are out of scope here —
delegate to `domain-teams:investing-team` Portfolio Review workflow when needed
(see "Optional follow-up" below).

---

## Inputs

| Param | Required | Notes |
|---|---|---|
| `holdings` | ✅ | Path to holdings file. CSV (header: `ticker,quantity,cost_basis`) or JSON list (`{ticker, quantity, cost_basis}`). `purchase_date` optional. Aliases accepted: `shares`, `avg_cost`, `cost`, `acquired_at`. |
| `regime_overlay` | optional | Boolean (default `true`). When `true`, also fetches regime-pack and runs analysis-macro-regime. |
| `output_language` | optional | `en` / `zh-TW` / `ja`. Default: auto-detect from holdings file content (CJK chars in headers/notes → `zh-TW` or `ja`); falls back to `en`. |

---

## Pipeline

### Step 1 — Parse holdings + group by country

Read the holdings file (CSV or JSON). For each ticker, classify by suffix:

| Suffix pattern | Country code | Skill |
|---|---|---|
| `.TW` / `.TWO` | `tw` | `data-tw` |
| `.T` (Tokyo) **or** bare 4-digit (e.g. `7203`) | `jp` | `data-jp` |
| `.KS` / `.KQ` | `kr` | `data-kr` |
| `.SS` / `.SZ` / `.HK` | `cn` | `data-cn` |
| anything else | `us` | `data-us` |

Notes:
- Bare 4-digit Japanese tickers (`7203`, `9984`) are normalised to `<ticker>.T` for yfinance compatibility before fetch — emit the normalised form into the per-country `--tickers` argument.
- Unknown suffixes default to `us`.

### Step 2 — Parallel batch price fetch (per country group)

For each non-empty country group, dispatch in parallel (main agent issues one Bash call per country in a single message):

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/../data-us/scripts/pack.py --tickers AAPL,MSFT --pack screener-batch > /tmp/portfolio-prices-us.json
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/../data-tw/scripts/pack.py --tickers 2330.TW,2317.TW --pack screener-batch > /tmp/portfolio-prices-tw.json
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/../data-jp/scripts/pack.py --tickers 7203.T,9984.T --pack screener-batch > /tmp/portfolio-prices-jp.json
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/../data-kr/scripts/pack.py --tickers 005930.KS --pack screener-batch > /tmp/portfolio-prices-kr.json
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/../data-cn/scripts/pack.py --tickers 600519.SS,0700.HK --pack screener-batch > /tmp/portfolio-prices-cn.json
```

Each pack returns `{tickers: {<TICKER>: {...screener fields including regularMarketPrice...}}}`.

### Step 3 — Concatenate per-country JSONs

Collapse the per-country `tickers` maps into a single flat JSON list that
`analysis-portfolio` accepts. Either form works (extractor in
`portfolio_compute.py` handles both):

```python
# pseudo — main agent writes this combined file
combined = []
for country_path in country_paths:
    pack = json.load(open(country_path))
    for tk, fields in (pack.get("tickers") or {}).items():
        # screener-batch records carry `regularMarketPrice` / `last_price`
        combined.append({"ticker": tk, **fields})
json.dump(combined, open("/tmp/portfolio-prices-combined.json", "w"))
```

### Step 4 — Compute portfolio P&L

```
uv run ${CLAUDE_SKILL_DIR}/../analysis-portfolio/scripts/portfolio_compute.py \
  --holdings <holdings-path> \
  --prices /tmp/portfolio-prices-combined.json \
  > /tmp/portfolio-review.json
```

Output schema: `{positions[], totals, _provenance}`. Ratios are fractional
(e.g. `pnl_ratio: 0.2033` = +20.33%). Positions are pre-sorted by descending
weight.

### Step 5 — (Optional) Macro regime overlay

If `regime_overlay = true`:

5a. Determine which countries have positions (the same set computed in Step 1).

5b. Dispatch `data-{country}/pack.py --pack regime-pack` per country in parallel:

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/../data-us/scripts/pack.py --pack regime-pack > /tmp/regime-us.json
# ...repeat for each country with positions
```

5c. Run analysis-macro-regime:

```
uv run ${CLAUDE_SKILL_DIR}/../analysis-macro-regime/scripts/regime_compose.py \
  --input us=/tmp/regime-us.json,jp=/tmp/regime-jp.json,tw=/tmp/regime-tw.json \
  > /tmp/regime-card.json
```

If a country's regime-pack fetch fails, drop that country from `--input`
rather than failing the whole pipeline (degraded mode — surface in
provenance footer).

### Step 6 — Render Markdown

```
uv run ${CLAUDE_SKILL_DIR}/scripts/review_format.py \
  --portfolio /tmp/portfolio-review.json \
  [--regime /tmp/regime-card.json] \
  --lang en
```

`review_format.py` is **pure** — no fetch, no subprocess, no compute beyond
formatting fractional ratios as percentages.

### Step 7 — (Optional follow-up) Rebalance memo

For Kelly-sizing / sector-concentration / rebalance recommendations, hand
the rendered review + the `/tmp/portfolio-review.json` + `/tmp/regime-card.json`
paths to `domain-teams:investing-team` Portfolio Review workflow as seed
context. That delegation is **not** automatic — invoke only when the user
explicitly requests rebalance recommendations (gate verdicts, Kelly memo,
etc.). See repo CLAUDE.md §Cross-Plugin Delegation Contract.

---

## review_format.py contract

```bash
uv run scripts/review_format.py \
  --portfolio /tmp/portfolio-review.json \
  [--regime /tmp/regime-card.json] \
  [--lang en|zh-TW|ja]
```

**Inputs**:
- `--portfolio` (required): analysis-portfolio JSON output
- `--regime` (optional): analysis-macro-regime regime-card JSON
- `--lang` (default `en`): output language

**Output**: Markdown to stdout — header, summary, position table (sorted by
weight desc), concentration analysis (max weight + top-3 weight + >30%
flag), optional regime overlay table + cross-country consensus, provenance
footer.

**Pure**: no HTTP, no subprocess, only stdlib (`argparse` / `json` / `pathlib`).
Renders fractional `pnl_ratio` as `{ratio*100:.2f}%`.

---

## Cross-Plugin Delegation Contract

Per repo `CLAUDE.md` §Cross-Plugin Delegation Contract:
- This skill = orchestration + Markdown rendering only. Data fetch lives in
  `data-{country}` skills; pure compute lives in `analysis-portfolio` and
  `analysis-macro-regime`.
- Rebalance / Kelly-sizing / regime-aligned sector tilts are
  `domain-teams:investing-team` territory — pass paths (not file content)
  and let the team enforce its own gates.
- Gate verdicts from delegated work flow back to this skill for delivery.

---

## Limitations

- Currency not converted — multi-currency portfolios produce notional sums
  (e.g. USD positions and TWD positions added without FX). Review the
  warning in the regime overlay or split into per-currency holdings files
  if mixing matters.
- yfinance `regularMarketPrice` is delayed 15-20 min for retail feeds.
- Tickers with no resolved price are listed in the provenance footer
  (`missing_prices`) and excluded from totals — they are not silently
  dropped.
- Bare 4-digit ticker → `.T` normalisation only covers JP. Other markets
  with bare-numeric tickers (e.g. KR `005930`) require the explicit suffix.
- Regime overlay degrades gracefully on per-country fetch failure.

---

## i18n

| Language | Term mapping |
|---|---|
| English | Portfolio Review / P&L / Concentration / Macro Regime Overlay |
| 繁體中文 | 投資組合回顧 / 損益 / 集中度 / 總經 Regime Overlay |
| 日本語 | ポートフォリオレビュー / 損益 / 集中度 / マクロレジーム |
