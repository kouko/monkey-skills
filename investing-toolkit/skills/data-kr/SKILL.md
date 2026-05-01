---
name: data-kr
description: >-
  Korea (KOSPI / KOSDAQ) Layer 1 data skill — single facade exposing pack
  modes (snapshot / memo-fetch / comps-multiples / screener-batch /
  regime-pack) over yfinance .KS/.KQ tickers and BOK ECOS-KEYSTAT macro
  indicators (54 series via FinanceDataReader). Data-only — no analysis,
  no formatting. Returns structured JSON with provenance for handoff to
  Layer 2 analysis skills (analysis-comps / analysis-screener /
  analysis-macro-regime) or domain-teams:investing-team.
  한국 데이터 레이어 — yfinance + BOK ECOS 매크로.
  韓國資料層 — yfinance + 韓國銀行 ECOS 總經指標。
---

# data-kr

Korea data layer for the investing-toolkit v2.0.0 three-layer architecture.
Bundles all clients needed for KR equity + macro fetch into a single
`pack.py` facade, dispatched by `--pack` mode.

This skill is **data-only**. It performs no analysis, no regime mapping,
and no formatting. Output JSON is consumed by Layer 2 (analysis-*) or
Layer 3 (report-*) skills, or handed off to `domain-teams:investing-team`
for full equity research memos.

---

## Tier status

| Source | Tier | Coverage |
|--------|------|----------|
| **BOK ECOS-KEYSTAT** (via FinanceDataReader) | A (primary) | Macro — 54 indicators across 13 groups |
| **FRED** (DEXKOUS only) | A (primary) | KRW/USD daily fallback |
| **yfinance** (.KS / .KQ) | 2 (unofficial) | Equity price / info / financials |
| DART (전자공시시스템) | — | **Deferred** — Korea has no primary-source equity client wired in this skill yet. Planned for a future minor version. |

Equity-side memo content is therefore Tier 2 only in v2.0.0. Macro pulls
remain primary-source-grounded.

---

## Layer 1 contract

| Property | Behavior |
|----------|----------|
| Inputs | `--ticker` / `--tickers` (equity packs) or `--indicators` (regime-pack) |
| Output | Structured JSON to stdout, exit 0 on success / exit 1 on partial failure |
| Side effects | Cache writes to `$INVESTING_TOOLKIT_CACHE` (yfinance: 1h TTL; fdr: 24h TTL) |
| Provenance | Every pack includes `_provenance` block (tier, primary-source status, source URLs) |
| Cross-skill | Other skills MAY invoke `pack.py` via Bash — bundled-file ownership ≠ execution permission |

---

## Pack types

### `--pack snapshot` (single ticker)

Quick overview card. Pulls yfinance `info` + 1y price `history`.

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 005930.KS --pack snapshot
```

### `--pack memo-fetch` (single ticker, Tier 2 only)

Full memo data: yfinance `info` + 5y `history` + annual + quarterly
financials. **Tier 2 only** — Korean primary-source equity (DART) is not
wired in this skill. The `_provenance.primary_source_status` field
explicitly flags this so downstream analysis layer can reflect the
limitation.

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 005930.KS --pack memo-fetch
```

### `--pack comps-multiples` (single or batch)

Multiples-only fetch (yfinance `info`) for anchor + peers. Used by
`analysis-comps` to compute peer-multiple statistics. Multiples extracted
downstream: trailingPE, forwardPE, evEbitda, priceToSales, priceToBook.

```
# Anchor only
pack.py --ticker 005930.KS --pack comps-multiples
# Anchor + peers
pack.py --tickers 005930.KS,000660.KS,373220.KS --pack comps-multiples
```

### `--pack screener-batch` (batch required)

Lightweight batch info pull for screening (50–500 tickers). Returns
yfinance batch dict; analysis-screener projects fields downstream.

```
pack.py --tickers 005930.KS,000660.KS,035420.KS,051910.KS --pack screener-batch
```

### `--pack regime-pack` (no ticker)

BOK ECOS-KEYSTAT 54-indicator pull via FinanceDataReader. Indicator groups:

```
rates, inflation, growth, industry, labor, trade, money, sentiment,
cycle (선행/동행 CI pair = monthly GDP proxy), markets (KOSPI/KOSDAQ),
fx, realestate, demographics
```

KRW/USD (`fx.krw-usd`) sourced via FRED DEXKOUS — ECOS-KEYSTAT does not
expose a clean KRW/USD series.

```
# All groups
pack.py --pack regime-pack
# Subset
pack.py --pack regime-pack --indicators rates,inflation,growth,cycle
```

PMI (S&P Global) is **not fetched** — licensed commercial data. Closest
free proxies are the `sentiment` group (consumer-sentiment K252 +
economic-sentiment K269). See korea-macro SKILL.md (data-kr's source
skill) for full PMI rationale.

---

## Ticker suffix convention

Korean equities require an exchange suffix on yfinance:

| Suffix | Exchange | Examples |
|--------|----------|----------|
| `.KS` | **KOSPI** (Korea Stock Exchange — large cap) | 005930.KS (Samsung Electronics), 000660.KS (SK Hynix) |
| `.KQ` | **KOSDAQ** (small/mid cap, growth) | 035420.KQ (NAVER), 091990.KQ (Celltrion Healthcare) |

### Auto-suffix rule

`pack.py` accepts bare 6-digit numeric tickers and appends a default
suffix:

| Input | Default output | With `--kosdaq` flag |
|-------|----------------|----------------------|
| `005930.KS` | `005930.KS` (unchanged) | `005930.KS` (unchanged) |
| `005930` | `005930.KS` | `005930.KQ` |
| `005930.KQ` | `005930.KQ` (unchanged) | `005930.KQ` (unchanged) |

The default of `.KS` reflects KOSPI being the primary exchange.

For ambiguous numeric tickers known to be KOSDAQ-listed, pass `--kosdaq`
or supply the suffix explicitly. Tickers with already-set suffixes
(including `.KS` while `--kosdaq` is set) pass through unchanged so a
mixed list can be normalized in one pass.

---

## Underlying clients

| Script | Source | Cache TTL |
|--------|--------|-----------|
| `scripts/yfinance_client.py` | Yahoo Finance (unofficial scraper) | 1h |
| `scripts/fdr_client.py` | FinanceDataReader → BOK ECOS-KEYSTAT (+ FRED for DEXKOUS) | 24h |

Both are exact MD5 copies of the canonical clients in
`investing-toolkit/scripts/`. CI MD5 sync-check enforces drift-free
duplication across the 5 `data-{country}` skills.

---

## Cross-Layer Handoff

```
data-kr (Layer 1) -> analysis-comps / analysis-screener / analysis-macro-regime (Layer 2)
                  -> report-equity-memo / report-stock-snapshot / report-screener-list (Layer 3)
                  -> domain-teams:investing-team (full memo authoring)
```

Pass the pack JSON output verbatim as the `### Input` section when
launching downstream skills.

---

## Limitations

- **Equity primary-source deferred**: DART (전자공시시스템, dart.fss.or.kr)
  integration not yet wired. Memo-fetch is Tier 2 only.
- **PMI absent**: S&P Global South Korea Manufacturing PMI is licensed —
  closest proxies are BOK BSI sentiment indicators.
- **FinanceDataReader endpoint risk**: BOK ECOS access is via an
  undocumented internal endpoint that the FDR library reverse-engineers.
  See korea-macro SKILL.md for fallback discussion (free ECOS API key
  remains a deferred candidate).

---

## Notes

- Skill directory: `${CLAUDE_SKILL_DIR}` resolves to this skill's path.
- All `pack.py` invocations preserve `INVESTING_TOOLKIT_CACHE` so cached
  client output is reused across pack types within a run.
- Source skill `korea-macro` is **kept** during the v2.0.0 migration —
  do not delete it until report-layer cutover is complete.

한국어: 한국 데이터 레이어. 한국은행 ECOS-KEYSTAT 매크로 + yfinance KOSPI/KOSDAQ.
日本語: 韓国データレイヤー（BOK ECOS マクロ + yfinance 株式）。
繁體中文: 韓國資料層（韓國銀行 ECOS 總經 + yfinance 韓股）。
