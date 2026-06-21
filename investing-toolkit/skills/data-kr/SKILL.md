---
name: data-kr
description: |
  Layer-1 data fetch for Korea (KOSPI/KOSDAQ) — yfinance .KS/.KQ + BOK ECOS macro (FinanceDataReader), one facade, 5 pack modes (snapshot / memo-fetch / comps / screener-batch / regime). Data-only, no analysis; JSON with provenance.
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
| Provenance | Every pack includes `_provenance` block with unified fields: `primary_source_status` (`available` / `deferred`), `primary_source_note` (free-form context), `tier`, plus pack-specific fields. Normalization warnings (if any) surface under `ticker_normalization_warnings`. |
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

**Schema is normalized**: single and batch both emit `info: {ticker:
{...}}` so `analysis-comps` consumes one contract:

```jsonc
// Single (--ticker 005930.KS)
{"info": {"005930.KS": {...multiples_dict...}}}
// Batch (--tickers 005930.KS,000660.KS)
{"info": {"005930.KS": {...}, "000660.KS": {...}}}
```

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
economic-sentiment K269). The PMI exclusion rationale is preserved in
git history (pre-v2.0.0 `korea-macro/SKILL.md`).

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
| `5930` (4-digit, leading-zero strip) | `5930` (passes through, **warns**) | `5930` (passes through, **warns**) |
| `XYZ` (non-numeric, no suffix) | `XYZ` (passes through, **warns**) | `XYZ` (passes through, **warns**) |

The default of `.KS` reflects KOSPI being the primary exchange.

For ambiguous numeric tickers known to be KOSDAQ-listed, pass `--kosdaq`
or supply the suffix explicitly. Tickers with already-set suffixes
(including `.KS` while `--kosdaq` is set) pass through unchanged so a
mixed list can be normalized in one pass.

**Edge-case warnings**: if a token is neither suffixed nor a valid
6-digit code (e.g. 4/5/7-digit typo or non-numeric noise), `pack.py`
emits a stderr warning and records it under
`_provenance.ticker_normalization_warnings: [...]`. The token is **not
refused** — it passes through unchanged so the consumer can investigate
the resulting yfinance lookup failure with full context.

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
  Free ECOS API key (https://ecos.bok.or.kr/api/#/AuthKeyApply) remains a
  deferred candidate for direct integration.

---

## Notes

- Skill directory: `${CLAUDE_SKILL_DIR}` resolves to this skill's path.
- All `pack.py` invocations preserve `INVESTING_TOOLKIT_CACHE` so cached
  client output is reused across pack types within a run.
- v1.x source skill `korea-macro` was deleted in v2.0.0; its full 54-indicator
  catalog + grouping rationale is now embedded in this skill's pack contracts
  above. Historical reference docs preserved in git history (pre-v2.0.0).

한국어: 한국 데이터 레이어. 한국은행 ECOS-KEYSTAT 매크로 + yfinance KOSPI/KOSDAQ.
日本語: 韓国データレイヤー（BOK ECOS マクロ + yfinance 株式）。
繁體中文: 韓國資料層（韓國銀行 ECOS 總經 + yfinance 韓股）。
