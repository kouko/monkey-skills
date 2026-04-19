---
name: japan-stock-snapshot
description: >-
  JP 個股 snapshot — EDINET (金融庁 Tier A) 有報/四半期/臨時/大量保有 + TDnet
  (Yanoshin 適時開示 index) + yfinance .T (價格 + 指標). Dual-mode: EDINET_API_KEY
  present → primary-source Tier A fundamentals; absent → yfinance financials
  Tier 2 fallback. Composes a snapshot card covering company basics, latest
  BS/PL/CF, key timely-disclosures, price + valuation ratios, ready for
  domain-teams:investing-team handoff. 日本株スナップショット取得。
---

# japan-stock-snapshot

> **Dual-mode execution (v1.15.0+, corrected v1.16.1)**: The `uv run scripts/...` commands below are canonical. Matching MCP tools are registered alongside (`investing-toolkit:*` namespace) — Claude may use either; both return identical JSON. ⚠️ **Cowork limitation**: MCP does NOT bypass Cowork sandbox URL allowlist (v1.14.0 premise was wrong, confirmed v1.16.1). Use Claude Code CLI. Full catalog: [`docs/mcp-setup.md`](../../docs/mcp-setup.md).

Japan equity data snapshot built on **dual-mode tier routing**. When
`EDINET_API_KEY` is set, fundamentals come from the 金融庁 EDINET v2 REST
API — primary-source Tier A, same rigour as `us-stock-snapshot` (SEC EDGAR)
and `taiwan-stock-snapshot` (MOPS). Without the key, the skill falls back
to yfinance financials (Tier 2, Yahoo-scraped) and explicitly labels the
provenance as degraded. Either way, TDnet timely-disclosure index (via the
Yanoshin aggregator) and yfinance `.T` price/valuation snapshot come for
free, no key required.

This skill is **data-only** — it does not analyze or generate verdicts.

**Requires** (all ship with investing-toolkit v1.15.0):
- `scripts/edinet_client.py` — EDINET v2 API (fundamentals, Tier A; needs `EDINET_API_KEY`)
- `scripts/tdnet_client.py` — Yanoshin TDnet index wrapper (no key)
- `scripts/yfinance_client.py` — Yahoo Finance `.T` adapter (price + info + financials fallback)

---

## Data Sources (v1.15.0)

| Tier | Source | Script | Coverage | Key needed? |
|------|--------|--------|----------|-------------|
| **1 Primary (Tier A)** | EDINET v2 (金融庁) | `edinet_client.py` | 有報 120 / 四半期 140 / 半期 160 / 臨時 180 / 自己株買付 220 / 大量保有 350 + CSV-parsed BS/PL/CF key metrics | **yes** — `EDINET_API_KEY` (5-min free self-service registration) |
| **1 Primary (index)** | TDnet via Yanoshin WEB-API | `tdnet_client.py` | 適時開示 — 決算短信 / 業績予想 / 配当予想 / 自己株買付 / 株主総会 / 役員異動 — index only, link-out to JPX-hosted PDFs/XBRL | no |
| **1 Primary (price)** | Yahoo Finance `.T` | `yfinance_client.py --action history/info` | OHLCV 15-min delay / marketCap / P/E / 52W / beta / sector / industry | no |
| **2 Fallback (fundamentals)** | Yahoo Finance financials | `yfinance_client.py --action financials` | BS / PL / CF — used only when EDINET_API_KEY not set; explicitly `data_tier: "tier_2"` in provenance; Yahoo-scraped, may diverge from regulator filings | no |

**Why dual-mode**: non-developer users can get a working JP snapshot
immediately after plugin install (Tier 2, exploratory grade). Users who
want ISQ-grade memo support register an EDINET API key in 5 min and
auto-upgrade to Tier A. Matches the v1.14.0 silent-auto design
philosophy — zero-friction first run, upgradeable later.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | 4-digit JP 証券コード e.g. `7203`, `7203.T`, `7203.TO` (suffix stripped) |
| `period` | no | `1y` | Historical OHLCV lookback for yfinance `.T` |
| `days` | no | `365` | EDINET filings scan window (`/documents.json` date range) |
| `--mode` | no | auto | `tier-a` / `tier-2` override; default auto-picks based on `EDINET_API_KEY` |
| `--deep` | no | false | Extended fetch (past 20 quarterly filings + 5-year annual history) |

Ticker detection in `investment-memo-writer`: if the ticker matches
`^\d{4}(\.T|\.TO)?$` (4-digit code optionally with JP market suffix), the
memo pipeline routes to japan-stock-snapshot.

---

## Phase 1 — Data Fetch

Launch the `data-fetcher` agent. Commands route by mode:

### Tier A mode (EDINET_API_KEY set) — primary-source

```
# 1. Company master + EDINET code resolution (always run first — public, no key)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/edinet_client.py --action resolve-code --ticker {ticker4}

# 2. One-shot fundamentals bundle — resolves + lists + fetches latest 有報 (120) + 四半期 (140)
#    with auto key_metrics extraction from type=5 CSV (2024-04+ filings; ~11 metrics canonical shape)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/edinet_client.py --action filing-summary --ticker {ticker4} --days 365

# 3. Recent material events (臨時報告書 180 + 自己株買付 220 + 大量保有 350)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/edinet_client.py --action list-filings --ticker {ticker4} --forms 180,220,350 --days 180 --limit 15

# 4. Timely-disclosure index (decisions/events surfaced on TDnet before EDINET 臨時)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/tdnet_client.py --ticker {ticker4} --limit 20

# 5. Price + valuation (yfinance .T — uses Yahoo's real-time snapshot, 15-min delay)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --period {period}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --action info
```

### Tier 2 mode (no EDINET_API_KEY) — degraded fallback

```
# 1. TDnet index still works for disclosure titles/dates (no key needed)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/tdnet_client.py --ticker {ticker4} --limit 20

# 2. Price + valuation snapshot (same as Tier A)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --period {period}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --action info

# 3. **Degraded fundamentals** — Yahoo-scraped annual + quarterly BS/PL/CF
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --action financials --period annual
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --action financials --period quarterly
```

When emitting the snapshot, **prominently surface the Tier-2 label**:
> ⚠️ Fundamentals sourced via Yahoo Finance (Tier 2 scraper). Set
> `EDINET_API_KEY` for primary-source 金融庁 filings. Register free at
> https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html

### Extended (`--deep`)

```
# Additional past 5 years of annual reports (up to 5 × 120 filings)
uv run edinet_client.py --action list-filings --ticker {ticker4} --forms 120 --days 1825 --limit 6

# Past 20 quarterly filings (~5 years of 140)
uv run edinet_client.py --action list-filings --ticker {ticker4} --forms 140 --days 1825 --limit 20

# TDnet full year (for 決算短信 time-series)
uv run tdnet_client.py --ticker {ticker4} --keyword 決算短信 --limit 20
```

Tier 2 deep mode: multiple consecutive `--action financials --period quarterly` calls give ~4-6 past quarters from yfinance (Yahoo caches ~4-6 recent periods only).

---

## Output Shape

```json
{
  "ticker": "7203",
  "mode": "tier_a",                       // or "tier_2"
  "edinet_code": "E02144",                // (tier_a only)
  "name": "トヨタ自動車株式会社",
  "name_en": "TOYOTA MOTOR CORPORATION",
  "industry": "輸送用機器",               // EDINET 業種 (tier_a) or yfinance sector (tier_2)
  "market": "東名",                       // TDnet markets_string
  "fiscal_year_end": "3月31日",

  "snapshot": {                            // from yfinance .T info
    "market_cap_jpy": 45000000000000,
    "trailing_pe": 10.2,
    "price_to_book": 1.12,
    "dividend_yield": 0.0284,
    "beta": 0.85,
    "52w_high": 3200,
    "52w_low": 2150,
    "latest_close": 2988.50,
    "latest_date": "2026-04-17"
  },

  "price_history": { "period": "1y", "rows": 250, "latest_close": 2988.50, ... },

  "fundamentals": {
    "tier": "tier_a",                      // or "tier_2"
    "latest_annual": { "doc_id": "S100VWVY", "period_start": "2024-04-01",
                       "period_end": "2025-03-31", "key_metrics": {...} },
    "latest_quarterly": { "doc_id": "S100X...", "period_start": "2025-10-01",
                          "period_end": "2025-12-31", "key_metrics": {...} }
    // tier_2 uses yfinance financials shape: income_statement / balance_sheet / cash_flow
  },

  "material_events": {                     // EDINET 180/220/350 (tier_a only)
    "count": 8,
    "recent_filings": [{doc_type_label, doc_description, submit_datetime, ...}]
  },

  "timely_disclosures": {                  // TDnet Yanoshin index
    "count": 20,
    "disclosures": [{pubdate, disclosure_type, title, document_url, ...}]
  },

  "_provenance": {
    "primary_source": "EDINET v2 (金融庁)" // or "Yahoo Finance (unofficial)",
    "data_tier": "tier_a",                 // or "tier_2"
    "license": "PDL 1.0 ... (EDINET)",
    "fetched_at": "2026-04-19T..."
  }
}
```

---

## Known Gaps (v1.15.0)

These JP-specific datasets are NOT covered by the v1.15.0 Tier 1 free
tier. Documented here so `domain-teams:investing-team` knows what's
missing vs US / TW snapshots:

| Gap | Why | Path forward |
|---|---|---|
| **信用取引残高 per-stock** (margin balance) | J-Quants Free tier lacks this; needs Standard (paid) | Skip in v1.15.0; surface "unavailable" in snapshot; defer to v1.15.x if demand |
| **空売り残高 per-stock** | Same — J-Quants Standard locked | Same |
| **daily 投資部門別 per-stock flow** (TW 三大法人 equivalent) | JPX does not publish daily per-stock institutional flow freely; weekly aggregate only (http://www.jpx.co.jp/markets/statistics-equities/investor-type/) | Skip — genuinely not available in any free tier |
| **EPS via EDINET** | Aliases in `edinet_client.KEY_CONCEPTS` occasionally miss EPS when issuer uses IFRS KeyFinancialData namespace | yfinance `.T` info fills the gap; v1.15.x: expand EDINET aliases after probing more issuers |
| **narrative Item extraction from 有報** (事業等のリスク / MD&A equivalent) | Type=5 CSV is table-only; narrative lives in iXBRL 本文 | v1.15.x: add iXBRL text-section parser mirroring sec_edgar_client.py HTML parse |
| **pre-April-2024 filings via CSV** | type=5 was added 2024-04 | Historical filings must use type=1 iXBRL (deferred to v1.15.x) |

---

## Handoff to `domain-teams:investing-team`

Emit the snapshot as a structured fixture. investing-team's
Deep-Equity-Research-Memo workflow will:
1. Use `fundamentals.key_metrics` to seed DCF valuation (via
   `dcf-valuation` skill, JP branch).
2. Use `material_events` + `timely_disclosures` to anchor the Narrative
   Anchor gate (primary-source citations for corporate events).
3. Route to Japan-Specific Diagnosis gate when `investment-memo-writer`
   emits `output_language: ja` (inferred from ticker suffix `.T`).
4. If `fundamentals.tier == "tier_2"`, the Fundamentals Primary-Source
   gate downgrades from MUST to SHOULD and emits a flag in the ISQ
   gate run.

---

## Upgrade path to Tier A

Display this in the snapshot footer when running in Tier 2 mode:

> 🔓 **Upgrade to Tier A (primary-source fundamentals)**:
> 1. Register at https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html (free, ~5 min, email → MFA)
> 2. `export EDINET_API_KEY=<your-key>` (or add to shell rc file)
> 3. Re-run this skill. Fundamentals block will switch to EDINET
>    CSV-parsed BS/PL/CF with `data_tier: "tier_a"` in provenance.

---

## See also

- `us-stock-snapshot` — SEC EDGAR JSON parallel (US regulator-filed fundamentals)
- `taiwan-stock-snapshot` — MOPS JSON API parallel (TW regulator-filed fundamentals)
- `dcf-valuation` — will auto-source EDINET BS/PL/CF via `edinet_filing_summary` when ticker detected as JP in v1.15.x
- `investment-memo-writer` — routes JP tickers to this skill in Phase 1 (v1.15.0)
