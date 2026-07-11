---
name: report-stock-snapshot
description: |
  Layer-3 single-page Markdown snapshot card for any equity (US/JP/TW/KR/CN/HK). Auto-detects market by suffix, dispatches data-markets snapshot (disclosures + price + valuation), renders a card. No analysis; hands off to report-equity-memo.
---

# report-stock-snapshot

**Layer 3 — Report** in the investing-toolkit v2.0.0 three-layer architecture
(Data → Analysis → Report). This skill is **orchestration + formatting** only:
it routes the ticker to the right country data skill, runs the snapshot pack,
then renders a Markdown card. It does **not** call any analysis-* skill, does
**not** invoke `domain-teams:investing-team`, and does **not** issue verdicts.

Replaces three v1 skills (`us-stock-snapshot`, `japan-stock-snapshot`,
`taiwan-stock-snapshot`) with a single 5-market entry point.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | Examples: `AAPL`, `7203`, `7203.T`, `2330.TW`, `2454.TWO`, `005930.KS`, `600519.SS`, `0700.HK` |
| `output_language` | no | auto | `en` / `zh-TW` / `ja`. Auto-detect: `.TW`/`.TWO`/`.HK` → `zh-TW`; `.T`/`.TO`/4-digit JP code → `ja`; `.KS`/`.KQ` → `en` (KR has no native renderer yet); `.SS`/`.SZ` → `zh-TW`; default → `en`. |

---

## Pipeline

### Step 1 — Country auto-routing (ticker suffix detection)

Parse the ticker (case-insensitive, trimmed) and pick the market:

| Pattern | Country | market code |
|---|---|---|
| Ends with `.TW` or `.TWO` | TW | `tw` |
| Ends with `.T` or `.TO`, **or** matches `^\d{4}$` (bare 4-digit JP 証券コード) | JP | `jp` |
| Ends with `.KS` or `.KQ` | KR | `kr` |
| Ends with `.SS`, `.SZ`, or `.HK` | CN/HK | `cn` |
| Otherwise (alphabetic ticker, e.g. `AAPL`, `MSFT`, `BRK.B`) | US | `us` |

Edge cases:
- Bare 6-digit numeric (`005930`) → ambiguous between KR and CN; assume KR if a `.KS`/`.KQ` hint follows context, else CN. **Default for bare 6-digit: KR** (`--market kr` auto-suffixes `.KS`; `--market cn` requires the user to disambiguate via suffix).
- Bare 4-digit numeric (`7203`) → JP (`data-markets` auto-appends `.T`).
- Bare 4-/5-digit numeric ending pattern is JP first, HK second; suffix is the disambiguator.

### Step 2 — Fetch snapshot pack

Run `data-markets/scripts/pack.py` and capture JSON (market auto-detected
from the ticker; the routing above documents what `pack.py` does
internally):

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/data-markets/scripts/pack.py \
    --ticker {ticker} --pack snapshot \
    > /tmp/{ticker_safe}-snap.json
```

Where `{detected_country}` ∈ `{us, jp, tw, kr, cn}` and `{ticker_safe}` is the
ticker with `/` and `.` replaced by `_` for filesystem safety.

### Step 3 — Format Markdown card

Run the pure-formatter script on the captured JSON:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/snapshot_format.py \
  --input /tmp/{ticker_safe}-snap.json \
  --country {detected_country} \
  [--lang en|zh-TW|ja]
```

Pass `--country {detected_country}` (one of `us|jp|tw|kr|cn`) so the formatter
honours Step 1's ticker-suffix routing as the single source of truth. The
default `--country auto` falls back to `pack["country"]` → ticker-suffix →
pack-shape sniffing in that order, but explicit is preferred whenever the
country is already known.

`snapshot_format.py` is **pure** — no HTTP, no subprocess. It reads the pack
JSON, extracts whatever fields are present (different countries have different
top-level keys), and renders a Markdown card to stdout. Missing fields are
gracefully replaced with `N/A` so partial packs still produce readable output.

### Step 4 — Surface output

Print the Markdown card. If the pack JSON carries `_partial: true` or any
`_provenance.upgrade_hint`, surface that as a callout box above the card so
the user sees data-quality warnings (Tier 2 fallback, missing EDINET key,
TWSE OpenAPI partial failure, etc.).

---

## Output Format

```
## {TICKER} Snapshot — {date}

**{name}** | {exchange} | {sector}
**Price**: {currency} {close} | 52W: {low}–{high} | vs 52W High: {pct}%
**Valuation**: P/E {pe} | P/B {pb} | Market Cap: {currency} {mcap_b}B | EV: {currency} {ev_b}B
**Returns / Dividends**: 1Y return {ret_1y}% | Beta {beta} | Div Yield {div_yield}%

### Recent Disclosures
{country-specific disclosures section — see snapshot_format.py for details}

---
_Data: {tier_routing_provenance}_
```

The `{country-specific disclosures section}` differs by market:
- **US** — Latest 10-K date / accession + recent 8-K count (SEC EDGAR; only present if pack carried `sec_filings`, which `--pack snapshot` itself does NOT include — show "(use --pack memo-fetch for SEC filings)" instead).
- **JP** — TDnet timely-disclosure list (top 5 by date) — `decision_date`, `disclosure_type`, `title`.
- **TW** — MOPS 重大訊息 list + 三大法人 30d net flow snapshot.
- **KR / CN** — Minimal block: just price + valuation. Note "primary-source disclosure deferred" in provenance footer.

---

## Tier-routing provenance footer

The footer reflects what the pack actually carried:

| Country | Footer text |
|---|---|
| US | `Data: yfinance Tier 2 (price + valuation). For SEC filings, see report-equity-memo.` |
| JP, EDINET key set | `Data: yfinance .T (price) + TDnet (disclosures, Tier A index). For full EDINET filings, see report-equity-memo.` |
| JP, no key | `Data: yfinance .T + TDnet. ⚠ Set EDINET_API_KEY for primary-source 金融庁 fundamentals (free 5-min registration).` |
| TW | `Data: MOPS Tier A (公司揭露) + TWSE/TPEx OpenAPI Tier A (交易) + FinMind Tier 2-gap (T86 三大法人).` |
| KR | `Data: yfinance Tier 2 (.KS/.KQ price + valuation). DART primary-source integration deferred.` |
| CN/HK | `Data: yfinance Tier 2 (.SS/.SZ/.HK price + valuation). cninfo / HKEX primary-source integration deferred.` |

The exact provenance is read from the pack JSON's `_provenance` block (US/JP/KR/CN) or `_tier` envelope (TW); `snapshot_format.py` synthesizes the footer from those values.

---

## Cross-skill / cross-plugin handoff

Snapshot card is a leaf output. For deeper analysis, hand off to:

- `report-equity-memo` — full investment memo via `domain-teams:investing-team`
- `analysis-dcf` — 3-stage DCF valuation
- `analysis-comps` — relative valuation against peer set
- `domain-teams:investing-team` directly — Buy/Hold/Sell verdict with primary-source anchoring

This skill does NOT call any of the above. Orchestration is the user / parent agent's responsibility.

---

## Limitations

- **Snapshot is light by design** — for SEC filings / EDINET 有報 narrative / MOPS BS-IS-CF / FRED macro, use `--pack memo-fetch` via `report-equity-memo`.
- **KR / CN primary-source** — DART (Korea), cninfo (China), HKEX (HK) integrations are deferred to a future minor version. KR/CN/HK snapshots are yfinance-only (Tier 2).
- **Market suffix is the source of truth** — the auto-router never guesses across markets. If the user passes `0700` (a bare 4-digit), JP wins (assumed 証券コード). For HK Tencent, pass `0700.HK` explicitly.
- **Cross-listed tickers** — if a company trades on multiple exchanges (e.g. `BABA` on NYSE + `9988.HK`), the user picks which listing to snapshot. This skill does not unify cross-listed views.

---

## See also

- `data-markets` — Layer 1 fetch packs (5 markets, auto-detected)
- `report-equity-memo` — full memo orchestrator (memo-fetch pack → analysis-* → investing-team)
- `report-portfolio-review` — multi-position review with country-grouped fetches
- `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md` §4.4

---

_Layer 3 (Report) skill • investing-toolkit v2.0.0 • 個股快照卡片（5 市場路由） • 個別株スナップショットカード（5 市場ルーティング）_
