# investing-toolkit v2.2.0-c-bench — SPDR sector ETF aggregate benchmark layer (follow-up)

**Status**: Design (follow-up PR; not yet scheduled)
**Date**: 2026-05-05
**Authors**: kouko + Claude (brainstorming session)
**Predecessor**: v2.2.0-c (sector classification + 9-schema dispatch + sector-specific multiples — `2026-05-04-investing-toolkit-v2.2.0-c-sector-multiples-design.md`)
**Skill**: `investing-toolkit/skills/analysis-comps`

---

> **Reframe note (2026-05-05)** — this spec was originally drafted as a competing v2.2.0-c design before the in-progress `feat/v2.2.0-c-sector-multiples` branch was rediscovered. After branch comparison, the user chose the OLD design (schema-driven, 9 sector schemas, 5 new multiples + 8 indicators) for v2.2.0-c. The durable contribution of this spec is the **SPDR sector ETF aggregate benchmark layer** — orthogonal to v2.2.0-c's sector classification + multiples; layers on top. Sections covering classification / multiple-routing / override-mechanism are SUPERSEDED by v2.2.0-c's `sector_classifier.py` + `sector-routing.yaml` + `sector-overrides.yaml`. Only the ETF-aggregate + divergence-band + 11-GICS-warning-matrix concepts remain net-new for v2.2.0-c-bench.

---

## 1. Goal (v2.2.0-c-bench scope, post-reframe)

Layer a **SPDR sector ETF aggregate benchmark** on top of v2.2.0-c's sector-aware compute output:

1. **Holdings-weighted ETF aggregate** — weekly GitHub Actions job computes aggregate multiples + indicators (per the v2.2.0-c schema each ETF maps to) for each of the 11 SPDR Select Sector ETFs (XLE / XLB / XLI / XLY / XLP / XLV / XLF / XLK / XLC / XLU / XLRE) and commits the 11 JSON files to `references/`.
2. **Per-multiple ETF divergence** — `individual` (anchor's compute output) vs `etf_aggregate` divergence per multiple, classified into `in_line` (≤20%) / `notable` (20–50%) / `extreme` (>50%) bands.
3. **11-GICS warning matrix** — sector-specific interpretive caveats (e.g. "P/E for energy issuers is commodity-cycle distorted") loaded from `references/sector-warnings.md`, plucked by anchor's classified GICS L1.
4. **Opt-in CLI flag** — `--sector-benchmark` adds an `etf_benchmark` block to compute output; absent flag → output unchanged from v2.2.0-c shape (backward compatible).

**Architecture note**: v2.2.0-c sector classification + sector-specific multiples are the FOUNDATION. v2.2.0-c-bench reads `anchor.schema_id` from v2.2.0-c output and reads `references/sector-etf-aggregate-<ETF>.json` (one of 11) for the matching SPDR ETF aggregate. Per-ETF schema_id mapping is fixed (XLF → bank; XLK → tech-saas; XLRE → reit; XLE → energy; XLU → utilities; XLB/XLI/XLY/XLP/XLV/XLC → default).

## 1b. Original Goal sections (SUPERSEDED — kept for context)

The sections below were drafted before the v2.2.0-c branch was rediscovered. **Sector classification, override mechanism, and sector-specific multiples (ROE / Rule-of-40 / P/FFO)** are already shipped in v2.2.0-c. They are kept here for historical reference but should NOT be re-implemented in v2.2.0-c-bench. The original Goal #1 (classification) and Goal #2 (sector-specific multiples) overlap with v2.2.0-c's far more comprehensive 9-schema design and are obsolete.

## 1c. Original Goal text (FROM PRE-REFRAME DRAFT — SUPERSEDED)

Extend `analysis-comps --mode compute` so that US-listed equity comps output:

1. **Sector classification** — every US ticker is mapped to one of the 11 SPDR Select Sector ETFs (XLE / XLB / XLI / XLY / XLP / XLV / XLF / XLK / XLC / XLU / XLRE) using `yfinance info.sector + info.industry`, with a per-ticker override mechanism for known misroutes. **[SUPERSEDED by v2.2.0-c sector_classifier.py]**
2. **Sector-specific multiples** — for sectors where the default 5 (trailingPE / forwardPE / priceToBook / priceToSales / evEbitda) are misleading, additionally compute one or two sector-specific multiples (ROE for banks; Rule-of-40 for IT; P/FFO for REITs). **[SUPERSEDED by v2.2.0-c 9-schema dispatch with 5 new multiples + 8 indicators]**
3. **SPDR ETF aggregate benchmark** — every week, a scheduled GitHub Actions job computes holdings-weighted aggregate multiples for each of the 11 ETFs and commits the JSON results to `references/`. Runtime reads these files as the comparison benchmark.
4. **Per-multiple divergence** — emit `individual` vs `etf_aggregate` divergence per multiple, classified into `in_line` / `notable` / `extreme` bands at 20% / 50% boundaries.

Non-goals for this PR (deferred to v2.2.0-c² and v2.2.0-c-{jp,tw,kr,cn}):
- Energy EV/EBITDAX, Insurance Combined Ratio, Asset Manager P/AUM, Health Care Cash Burn, Utilities Dividend Yield, Communication Services sub-industry split (require new XBRL fields beyond v2.2.0-l)
- AFFO (REIT goes P/FFO only — AFFO requires gain-on-sale + straight-line rent adjustments not in standard XBRL)
- Non-US tickers (JP / TW / KR / CN) — explicitly skipped with a status field; per-region sector ETF benchmarks deferred

## 2. Why

- **Default 5 are sector-blind** — P/E and EV/EBITDA on a bank, REIT, or pre-profit SaaS issuer are misleading or meaningless; trailingPE on a SaaS issuer at GAAP unprofitability flips sign or explodes.
- **SPDR sector ETFs are the most common reference benchmark** for US equity sector-relative valuation; aligning output to XLE/XLB/.../XLRE makes the divergence directly actionable.
- **v2.2.0-l unblocked the data** — `total_stockholders_equity`, `depreciation_amortization`, plus existing revenue / operating income / market cap / debt / cash, are sufficient for ROE / Rule-of-40 / P/FFO without further XBRL work.
- **Soft blocker resolution** — yfinance `info.sector` misroutes holdcos / multi-sector issuers (e.g. BRK, META, SQ, AMZN). The override file makes that misroute auditable instead of silent.

## 3. Scope decisions (made during brainstorming)

| Decision | Choice | Reasoning |
|---|---|---|
| Sector multiple vs default 5 relationship | **Mark + augment (additive)** | Preserve cross-sector comparability; non-applicable defaults get a warning, not deletion. Mirrors v2.2.0-b additive philosophy. |
| GICS coverage | **Full 11** for warning + classification; **5 sectors** (Materials / Cons Disc / XLF banks / XLK / XLRE REITs) for sector-specific multiples in v1 | Stay inside v2.2.0-l data boundary; the other 6 are deferred to v2.2.0-c² when missing XBRL fields are fetched. |
| SPDR alignment mode | **C — sector swap + ETF aggregate benchmark** | User-stated goal: align with how a SPDR-using investor thinks. Classification + per-sector multiples + per-multiple ETF benchmark divergence. |
| ETF aggregate data source | **Holdings-weighted compute** (yfinance holdings + SEC EDGAR memo-fetch) | Stays inside primary-source backbone; SPDR factsheet PDF not needed; no new external scraper. |
| Aggregate fetch timing | **Eager scheduled (weekly GHA cron)** | Runtime always fast (read local JSON); freshness predictable. Cold-start lazy fetch (~70 min for one ETF) ruled out. |
| Sub-industry routing | **yfinance `info.industry` substring match** with conservative bias | "Banks" / "REIT" prefix triggers sector-specific; everything else falls back to default + warning. Avoids over-applying ROE to non-banks in XLF. |
| Override mechanism | **`sector-overrides.json` + `--sector-override` CLI flag + per-ticker provenance** | Precedent: v2.2.0-b emitted `compute_provenance` per multiple. Sector classification follows same transparency principle. |
| Output schema shape | **Nested `sector` block** sibling to existing 5 multiples | v2.2.0-b shape unchanged → 100% backward compatible; `sector` block self-contained, easy to ignore for downstream not yet sector-aware. |
| Divergence threshold | **20% / 50%** (`in_line` / `notable` / `extreme`) | Sector-relative valuation is a business signal (premium / discount), not a data integrity check; wider bands than v2.2.0-b's 5% / 15%. |
| Geographic scope | **US-only**; non-US tickers emit `sector.status: "skipped"` | Mirrors v2.2.0-l's discipline; cross-country symmetry deferred to per-country follow-ups. |

## 4. Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  Build-time (weekly GHA)                                            │
│  ──────────────────────────                                         │
│  .github/workflows/sector-etf-aggregates.yml  (cron sat 06:00 UTC)  │
│    └─ uv run skills/analysis-comps/scripts/etf_aggregator.py        │
│         ├─ for ETF in [XLE, XLB, XLI, XLY, XLP, XLV, XLF,           │
│         │             XLK, XLC, XLU, XLRE]:                         │
│         │    1. fetch holdings (yfinance funds_data.top_holdings)   │
│         │    2. for each holding: data-us memo-fetch raw fields     │
│         │    3. holdings-weighted aggregate (default 5 + ROE +      │
│         │       Rule-of-40 + P/FFO where sector-classifier says     │
│         │       sector-specific multiple applies)                   │
│         └─ writes references/sector-etf-aggregate-<ETF>.json (×11)  │
│                                                                      │
│  Runtime (analysis-comps --mode compute --sector-benchmark)         │
│  ──────────────────────────                                          │
│  comps_compute.py                                                    │
│    ├─ if --sector-benchmark + ticker is US:                         │
│    │    ├─ sector_classifier.classify(ticker)                       │
│    │    │    ├─ check --sector-override CLI flag (provenance:cli)   │
│    │    │    ├─ check sector-overrides.json (provenance:override)   │
│    │    │    ├─ else yfinance info.sector + info.industry           │
│    │    │    │    (provenance:yfinance_info)                        │
│    │    │    └─ raise UnclassifiableTickerError on miss             │
│    │    ├─ if sub-industry triggers specific multiple:              │
│    │    │    compute ROE / Rule-of-40 / P/FFO using v2.2.0-l fields │
│    │    ├─ load references/sector-etf-aggregate-<ETF>.json          │
│    │    ├─ compute divergence per-multiple (20% / 50% bands)        │
│    │    ├─ load references/sector-warnings.md, pluck per-sector     │
│    │    │    warning string by classification.gics                  │
│    │    └─ emit `sector` block in output                            │
│    └─ else: output unchanged (v2.2.0-b shape preserved)             │
└────────────────────────────────────────────────────────────────────┘
```

## 5. Files added / modified

**New**:
- `skills/analysis-comps/scripts/sector_classifier.py`
- `skills/analysis-comps/scripts/etf_aggregator.py`
- `skills/analysis-comps/references/sector-overrides.json`
- `skills/analysis-comps/references/sector-warnings.md`
- `skills/analysis-comps/references/sector-etf-aggregate-XLE.json` through `-XLRE.json` (11 files, flat — single-level subfolder discipline per CLAUDE.md)
- `.github/workflows/sector-etf-aggregates.yml`

**Modified**:
- `skills/analysis-comps/scripts/comps_compute.py` — add `--sector-benchmark` flag, classifier wiring, divergence calc, sector block emission
- `skills/analysis-comps/references/schema-compute-output.json` — extend with `sector` block schema
- `skills/analysis-comps/SKILL.md` — document new flag + sector behavior + override mechanism
- `investing-toolkit/ROADMAP.md` — close v2.2.0-c entry; add v2.2.0-c² and v2.2.0-c-{jp,tw,kr,cn} entries

## 6. Component specs

### 6.1 `sector_classifier.py`

```python
def classify(ticker: str, override_cli: str | None = None) -> dict:
    """
    Returns: {
      "gics": "Technology",
      "sub_industry": "Software—Infrastructure",
      "etf": "XLK",
      "provenance": "yfinance_info" | "override_file" | "cli_flag",
      "exclude_specific_multiples": False
    }
    Raises: UnclassifiableTickerError (non-US, yfinance returns None, etc.)
    """
```

**Lookup order** (first hit wins):

1. `override_cli` (CLI `--sector-override <gics>` and optional `--sub-industry-override <industry>`) → provenance: `"cli_flag"`. ETF inferred from gics-to-etf mapping below. If `--sub-industry-override` not given, sub_industry defaults to `"user-override"` with implicit `exclude_specific_multiples: true` (conservative — sector-specific multiple requires explicit sub-industry).
2. `references/sector-overrides.json` lookup by ticker → provenance: `"override_file"`. Use full record fields (gics, sub_industry, etf, exclude_specific_multiples, reason).
3. yfinance `Ticker(ticker).info` → use `info.sector` (GICS L1 → ETF map) + `info.industry` (substring match for sub-industry routing) → provenance: `"yfinance_info"`.
4. None of the above resolve → `UnclassifiableTickerError`.

**GICS L1 → SPDR ETF mapping** (yfinance sector-name conventions):

| yfinance `info.sector` | SPDR ETF |
|---|---|
| Energy | XLE |
| Basic Materials | XLB |
| Industrials | XLI |
| Consumer Cyclical | XLY |
| Consumer Defensive | XLP |
| Healthcare | XLV |
| Financial Services | XLF |
| Technology | XLK |
| Communication Services | XLC |
| Utilities | XLU |
| Real Estate | XLRE |

**Sub-industry routing** (which sector-specific multiples apply):

| GICS L1 | `info.industry` substring trigger | Specific multiples added |
|---|---|---|
| Energy | (any) | — (warning only) |
| Basic Materials | (any) | — (warning only) |
| Industrials | (any) | — (no warning, default 5 OK) |
| Consumer Cyclical | (any) | — (no warning, default 5 OK) |
| Consumer Defensive | (any) | — (no warning, default 5 OK) |
| Healthcare | (any) | — (warning only — heterogeneous) |
| Financial Services | starts with `"Banks"` | + ROE |
| Financial Services | (other) | — (warning only — non-bank financial) |
| Technology | (any) | + Rule-of-40 |
| Communication Services | (any) | — (warning only — heterogeneous) |
| Utilities | (any) | — (warning only — Div Yield deferred) |
| Real Estate | starts with `"REIT"` | + P/FFO |
| Real Estate | (other) | — (warning only — non-REIT real estate) |

**`exclude_specific_multiples` short-circuit**: if override file sets this to true, classifier returns specific_multiples = none regardless of sub_industry. For conglomerates like BRK.

### 6.2 `etf_aggregator.py`

```python
def aggregate_etf(etf_ticker: str) -> dict:
    """
    Returns:
      {
        "etf": "XLK",
        "as_of": "2026-05-04",
        "holdings_count": 75,
        "_meta": {
          "source": "yfinance funds_data + data-us memo-fetch",
          "outliers_dropped": {"trailingPE": 2, "priceToBook": 1},
          "weight_coverage_pct": 94.2
        },
        "weighted_multiples": {
          "trailingPE": 24.1, "priceToBook": 5.8, "priceToSales": 6.2,
          "evEbitda": 18.4, "rule_of_40": 0.42
        }
      }
    """
```

**Algorithm**:
1. Fetch holdings via yfinance `Ticker(etf).funds_data.top_holdings` (returns top ~75-90 by weight, sufficient for sector aggregate; smaller-weight tail can be ignored — `weight_coverage_pct` records actual coverage).
2. For each `(holding_ticker, weight)`:
   - Skip if holding_ticker is non-US (ADR like NXPI / ASML) — log and continue
   - Run existing `data-us/scripts/pack.py --pack memo-fetch <ticker>` (reuses existing cache; offline if cached fresh)
   - Extract default 5 multiples + sector-specific (if sector_classifier indicates this issuer triggers a specific multiple)
3. Per multiple, compute holdings-weighted average over non-null values:
   - `weighted_avg = Σ(weight × multiple) / Σ(weight where multiple is non-null and within outlier bounds)`
   - Outlier guard: drop multiples outside `[0, 200]` per multiple (logged in `_meta.outliers_dropped`)
4. Persist to `references/sector-etf-aggregate-<ETF>.json`.

**CLI**:
- `etf_aggregator.py --etf XLK` (single ETF, useful for ad-hoc refresh)
- `etf_aggregator.py --all` (all 11 — used by GHA workflow)

**Rate limit**: SEC EDGAR companyfacts allows ~10 req/sec; sequential fetch with 100ms delay = ~10 req/sec; 825 holdings × 0.1s = ~85s pure fetch + parse overhead, well within GHA 6h budget.

### 6.3 `sector-overrides.json` (initial entries)

```json
{
  "BRK.A": {
    "gics": "Financial Services",
    "sub_industry": "Conglomerate",
    "etf": "XLF",
    "exclude_specific_multiples": true,
    "reason": "Multi-sector conglomerate; ROE driven by insurance float + non-financial operating businesses. Bank-style ROE comparison would be misleading."
  },
  "BRK.B": {
    "gics": "Financial Services",
    "sub_industry": "Conglomerate",
    "etf": "XLF",
    "exclude_specific_multiples": true,
    "reason": "Same as BRK.A (Class B share)."
  },
  "META": {
    "gics": "Technology",
    "sub_industry": "Software—Application",
    "etf": "XLK",
    "exclude_specific_multiples": false,
    "reason": "yfinance routes META to Communication Services > Internet Content & Information; widely benchmarked vs IT peers (advertising-driven SaaS economics)."
  },
  "SQ": {
    "gics": "Financial Services",
    "sub_industry": "Financial Data & Stock Exchanges",
    "etf": "XLF",
    "exclude_specific_multiples": false,
    "reason": "yfinance routes Block (SQ) to Software—Infrastructure; business is fintech / payment processing, more comparable to financial peers."
  },
  "AMZN": {
    "gics": "Technology",
    "sub_industry": "Internet Retail / Cloud",
    "etf": "XLK",
    "exclude_specific_multiples": false,
    "reason": "yfinance routes AMZN to Consumer Cyclical > Internet Retail; AWS cloud business material to valuation, IT-relative comparison preferred."
  }
}
```

### 6.4 `sector-warnings.md`

Markdown table SoT, one row per GICS L1 (11 rows). Each row includes `gics`, `sub_industry_trigger`, and `warning_text`. Loaded by `comps_compute.py` and pasted into `sector.warnings: [...]`.

Example rows:
- XLE / Energy / "P/E and EV/EBITDA on energy issuers are commodity-cycle distorted; prefer P/CF or production-volume multiples (deferred to v2.2.0-c²)."
- XLF / Financial Services (non-Banks) / "trailingPE and priceToSales for non-bank Financials (insurance / asset management / capital markets) require sub-industry-specific KPIs (Combined Ratio / AUM); not applied in this output (deferred to v2.2.0-c²)."
- XLV / Healthcare / "Default 5 vary widely across pharma / biotech / services / devices subsectors; biotech in particular often has negative earnings making P/E meaningless. Cash burn metrics deferred to v2.2.0-c²."
- XLU / Utilities / "Dividend yield is the canonical valuation metric for utilities but not yet computed in this output (deferred to v2.2.0-c²); P/E and EV/EBITDA available but interpretive."

### 6.5 Sector-specific multiple formulas

| Multiple | Output key | Formula | Source fields (all v2.2.0-l) | FY convention |
|---|---|---|---|---|
| ROE (XLF banks) | `roe` | `net_income[0] / total_stockholders_equity[0]` | `net_income`, `total_stockholders_equity` | FY-trailing (most recent FY) |
| Rule-of-40 (XLK) | `rule_of_40` | `(total_revenue[0] / total_revenue[1] - 1) + (operating_income[0] / total_revenue[0])` | `total_revenue`, `operating_income` | FY-trailing growth + FY-trailing margin |
| P/FFO (XLRE REITs) | `price_to_ffo` | `marketCap / (net_income[0] + depreciation_amortization[0])` | `marketCap`, `net_income`, `depreciation_amortization` | FY-trailing |

**Naming convention**: new sector-specific multiple keys use **snake_case** (`roe` / `rule_of_40` / `price_to_ffo`). Existing default 5 keys (`trailingPE` / `priceToBook` / `priceToSales` / `evEbitda` / `forwardPE`) stay camelCase because they are yfinance native field names — the mixed style within `sector.etf_aggregate` honestly reflects upstream provenance.

All FY-trailing (no LTM / quarterly logic introduced — matches v2.2.0-b convention). `_meta` per multiple records the fiscal_year_ends used (mirrors v2.2.0-b concept-nested provenance).

### 6.6 Output schema extension — `sector` block

Existing default 5 multiples (trailingPE / forwardPE / priceToBook / priceToSales / evEbitda) **unchanged** from v2.2.0-b shape. New `sector` key is sibling, optional (absent unless `--sector-benchmark` flag passed).

```json
{
  "trailingPE": { "...v2.2.0-b shape unchanged..." },
  "priceToBook": { "..." },
  "priceToSales": { "..." },
  "evEbitda": { "..." },
  "forwardPE": { "..." },
  "sector": {
    "classification": {
      "gics": "Technology",
      "sub_industry": "Software—Infrastructure",
      "etf": "XLK",
      "provenance": "yfinance_info"
    },
    "specific_multiples": {
      "rule_of_40": {
        "value": 0.58,
        "_meta": {
          "total_revenue": {"fiscal_year_ends": ["2024-09-28", "2023-09-30"]},
          "operating_income": {"fiscal_year_ends": ["2024-09-28"]}
        }
      }
    },
    "etf_aggregate": {
      "as_of": "2026-05-04",
      "trailingPE": 24.1,
      "priceToBook": 5.8,
      "priceToSales": 6.2,
      "evEbitda": 18.4,
      "rule_of_40": 0.42,
      "_meta": {"holdings_count": 75, "freshness_days": 1, "weight_coverage_pct": 94.2}
    },
    "divergence": {
      "trailingPE":  {"individual": 28.0,  "etf": 24.1, "delta_pct": 16.2,  "band": "in_line"},
      "priceToBook": {"individual": 7.2,   "etf": 5.8,  "delta_pct": 24.1,  "band": "notable"},
      "priceToSales":{"individual": 8.1,   "etf": 6.2,  "delta_pct": 30.6,  "band": "notable"},
      "evEbitda":    {"individual": 21.0,  "etf": 18.4, "delta_pct": 14.1,  "band": "in_line"},
      "rule_of_40":  {"individual": 0.58,  "etf": 0.42, "delta_pct": 38.1,  "band": "notable"}
    },
    "warnings": []
  }
}
```

**Divergence band thresholds**:
- `|delta_pct| ≤ 20%` → `in_line`
- `20% < |delta_pct| ≤ 50%` → `notable`
- `|delta_pct| > 50%` → `extreme`

**Non-US ticker** — `sector` block becomes:
```json
"sector": {
  "status": "skipped",
  "reason": "non-US ticker; SPDR sector ETFs are US-only. Cross-country sector benchmark deferred to v2.2.0-c-{jp,tw,kr,cn}."
}
```

**`--sector-benchmark` flag absent** — `sector` key absent entirely (v2.2.0-b output unchanged).

## 7. Testing

### 7.1 Unit tests (`tests/unit/`)

**`test_sector_classifier.py`**:
- Routing matrix: 13 fixtures covering every (GICS L1 × sub-industry trigger) row in §6.1
- Override file: BRK.A → conglomerate, exclude_specific_multiples=true
- CLI flag precedence: file < cli; absence of override → yfinance fallback
- Provenance field correctly tagged in all three paths
- Non-US ticker raises `UnclassifiableTickerError`
- yfinance returns None / missing fields → `UnclassifiableTickerError`

**`test_etf_aggregator.py`**:
- holdings-weighted average over canned holdings list (deterministic input)
- outlier drop: multiples outside `[0, 200]` excluded; `outliers_dropped` count correct
- `weight_coverage_pct` calculation
- non-US ADR holdings (e.g. NXPI) skipped + logged
- missing-data holdings (memo-fetch returns null for one multiple) handled — weighted average uses only non-null contributors

### 7.2 Integration tests (`tests/integration/test_cross_layer_chains.py`)

- `test_us_compute_with_sector_benchmark_aapl` — AAPL → XLK → Rule-of-40 + 5-multiple divergence vs XLK aggregate
- `test_us_compute_with_sector_benchmark_jpm` — JPM → XLF banks → ROE + 5-multiple divergence
- `test_us_compute_with_sector_benchmark_o` — Realty Income (O) → XLRE REITs → P/FFO + 5-multiple divergence
- `test_us_compute_with_sector_benchmark_brk_b` — BRK.B → override file → exclude_specific_multiples → only default 5 + warning, no ROE
- `test_compute_skip_sector_for_non_us` — 7203.T → `sector.status: "skipped"`
- `test_compute_without_sector_flag_unchanged` — backward compatibility: same input as v2.2.0-b integration test, `sector` key absent

Fixtures: `tests/data/fixtures/sector-etf-aggregate-{XLK,XLF,XLRE}-sample.json` for offline integration tests (do not depend on real ETF aggregate JSON which refreshes weekly).

### 7.3 Network smoke test (`tests/network/`)

- `test_etf_aggregator_xlk_live` — real yfinance + SEC EDGAR fetch of XLK; deselected by default; weekly CI runs.

## 8. CI integration

### 8.1 New workflow: `.github/workflows/sector-etf-aggregates.yml`

- Trigger: cron `'0 6 * * 6'` (UTC sat 06:00 = Asia/Taipei sat 14:00); also `workflow_dispatch` for manual refresh
- Job: `uv run skills/analysis-comps/scripts/etf_aggregator.py --all`
- Output: 11 JSON files committed by GHA bot user; commit message `chore(sector-aggregates): weekly refresh YYYY-MM-DD`
- Failure handling: on job failure, open GitHub issue via `peter-evans/create-issue-from-file` (or equivalent) tagged `sector-aggregate-stale`
- Caching: GHA cache for `~/.cache/investing-toolkit/sec_edgar/companyfacts/*.json` keyed by week to avoid re-fetching the same companyfacts each Saturday

### 8.2 Existing CI (`investing-toolkit pytest (offline)`)

- New unit tests + integration tests automatically picked up by the `pytest -m "not network"` selection; no workflow change needed.

### 8.3 Block-level cache helper sync (v2.2.0-j Phase 2)

`sector_classifier.py` and `etf_aggregator.py` do **not** participate in v2.2.0-j Phase 2 block-level cache helper sync. They are local to analysis-comps and use the `pack.py` cache layer indirectly (not a direct cache helper dependency).

## 9. ROADMAP closeout

When v2.2.0-c ships, ROADMAP.md updates:

1. Move §v2.2.0-c entry from "Future Roadmap (planning)" to a new versioned section `## v2.2.0-c — Sector multiples (released YYYY-MM-DD)` with PR link.
2. Add new "Future Roadmap" entries:
   - **v2.2.0-c²** — six-sector specific multiple coverage (Energy EV/EBITDAX / Insurance Combined Ratio / Asset Mgr P/AUM / Health Care Cash Burn / Utilities Div Yield / Comm Services sub-industry split). Requires new XBRL chains in v2.2.0-l-2 (OCF / Capex / Exploration Expense / Dividend per share).
   - **v2.2.0-c-jp** — JP regional sector ETF benchmarks. Candidates: iShares MSCI Japan sector ETFs / NEXT FUNDS TOPIX-17 sector ETFs.
   - **v2.2.0-c-{tw,kr,cn}** — sector ETF benchmark for the other three countries; gated on observed buy-side memo workflow demand.
3. Update `project_investing_toolkit_v2x_roadmap.md` memory pointer to reflect the new closed entry.

## 10. Deferred items (explicitly NOT in v2.2.0-c)

- AFFO (REIT goes P/FFO only) — AFFO needs gain-on-sale + straight-line rent adjustments
- Sub-industry warning i18n (EN-only in v1)
- SPDR factsheet PDF cross-check (audit redundancy; primary stays holdings-weighted compute)
- ETF holdings fallback to SPDR official CSV (yfinance only in v1; fallback added if yfinance breaks)
- Historical ETF aggregate time-series store (commit history acts as informal time-series; no dedicated DB)
- Dividend Yield in SPDR aggregate (XLU's canonical multiple; needs new dividend XBRL field)

## 11. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| yfinance `info.industry` schema changes | medium | sub-industry routing breaks → silent wrong multiple | classifier substring match has unit test fixtures; schema change → test fail; override file is emergency hatch |
| yfinance ETF holdings API instability / rate limit | medium-high | weekly aggregate job fails | GHA fail → auto-issue; retry × 3 with exponential backoff; runtime always reads last successful committed JSON |
| SEC EDGAR rate limit on weekly batch | medium | aggregate job >30min | sequential fetch + 100ms delay; GHA cache for companyfacts; ~85s pure fetch baseline (well under 6h GHA limit) |
| Mega-cap dominated ETF (XLK top-10 ~60% weight) | low-medium | aggregate becomes "AAPL+MSFT estimate" not sector estimate | `_meta.weight_coverage_pct` documents; warnings can flag; user-side interpretation responsibility |
| Non-US holdings in ETF (XLK has NXPI / ASML ADRs) | low | aggregate contaminated by non-US issuers | classifier rejects non-US tickers; `_meta.weight_coverage_pct` reflects actual non-skipped weight |
| BRK.B `exclude_specific_multiples` exception path bug | low | conglomerate gets meaningless ROE | dedicated unit test path; integration test with BRK.B fixture |
| Sector aggregate JSON git churn | low | history noise | 11 files / 1 commit per week; commit message tagged `chore(sector-aggregates):` for filterability |
| Weekly cron skips a Saturday (GHA outage) | low | aggregate stale by 1-2 weeks | freshness recorded in `_meta.freshness_days`; runtime warns when > 14 days |

## 12. Acceptance criteria

- [ ] `uv run skills/analysis-comps/scripts/comps_compute.py --mode compute --sector-benchmark <input.json>` for AAPL produces `sector.classification.etf == "XLK"`, `sector.specific_multiples.rule_of_40` non-null, `sector.divergence.trailingPE.band` ∈ {in_line, notable, extreme}
- [ ] Same invocation for JPM produces `etf == "XLF"`, `specific_multiples.roe` non-null
- [ ] Same invocation for Realty Income (O) produces `etf == "XLRE"`, `specific_multiples.price_to_ffo` non-null
- [ ] Same invocation for BRK.B produces `provenance: "override_file"`, `specific_multiples` empty (exclude_specific_multiples honored)
- [ ] Same invocation for non-US 7203.T produces `sector.status: "skipped"`
- [ ] Without `--sector-benchmark`, output identical to v2.2.0-b shape (no `sector` key)
- [ ] `etf_aggregator.py --all` populates 11 `references/sector-etf-aggregate-*.json` files
- [ ] GHA workflow `sector-etf-aggregates.yml` runs end-to-end on a `workflow_dispatch` invocation
- [ ] Existing `pytest -m "not network"` passes (no regressions); new unit + integration tests included
- [ ] ROADMAP.md updated; v2.2.0-c² and v2.2.0-c-{jp,tw,kr,cn} entries created
- [ ] schema-compute-output.json validates against actual emitted output for sector-bench mode

## 13. References

- v2.2.0-b design: `docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md`
- v2.2.0-l: PR #239 (memo-fetch raw-field extension)
- ROADMAP.md §v2.2.0-c
- ADR-0003: US T3 mapping pattern (XBRL concept nesting precedent)
- ADR-0004: per-country native classifier convention (cross-country deferral pattern)
- yfinance docs: `funds_data` API for ETF holdings
- SPDR Select Sector ETFs: ssga.com/us/en/intermediary/etfs (factsheet reference, NOT used as primary source)
