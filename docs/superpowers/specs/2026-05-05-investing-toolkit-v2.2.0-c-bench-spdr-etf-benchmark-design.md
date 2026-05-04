# investing-toolkit v2.2.0-c-bench — SPDR sector ETF aggregate benchmark layer

**Status**: Design (implementation-ready, post-reframe)
**Date**: 2026-05-05 (rewritten 2026-05-05 after v2.2.0-c shipped)
**Authors**: kouko + Claude (brainstorming session)
**Predecessor**: v2.2.0-c sector multiples (PR #242 — `sector_classifier.py`, `sector-routing.yaml`, `sector-overrides.yaml`, 9 schemas, 5 new multiples + 8 indicators) — `2026-05-04-investing-toolkit-v2.2.0-c-sector-multiples-design.md`
**Skill**: `investing-toolkit/skills/analysis-comps`

---

> **Reframe note (2026-05-05)** — this spec was originally drafted as a competing v2.2.0-c design before the in-progress `feat/v2.2.0-c-sector-multiples` branch was rediscovered. After branch comparison, the user chose the OLD design (schema-driven, 9 schemas, 5 new multiples + 8 indicators) for v2.2.0-c. Sector classification, override mechanism, and sector-specific multiples are SHIPPED in v2.2.0-c. The durable contribution of this spec — and the **only net-new surface for v2.2.0-c-bench** — is the SPDR sector ETF aggregate benchmark layer that overlays on top of v2.2.0-c output. The original §1b/§1c/§6.1/§6.3/§6.5 sections covering classification / overrides / sector-specific formulas are obsolete and have been removed from this rewrite (preserved in git history if needed).

---

## 1. Goal

Layer a **SPDR sector ETF aggregate benchmark** on top of v2.2.0-c's sector-aware compute output, so a single-ticker memo answers not only "is this expensive?" (vs direct mode — already shipped) but also "is this expensive **for its sector**?":

1. **Holdings-weighted ETF aggregate** — weekly GitHub Actions job computes aggregate multiples + indicators for each of the 11 SPDR Select Sector ETFs (XLE / XLB / XLI / XLY / XLP / XLV / XLF / XLK / XLC / XLU / XLRE) using the v2.2.0-c schema each ETF maps to, and commits 11 JSON files to `references/`.
2. **Per-multiple / per-indicator divergence** — anchor's compute output vs ETF aggregate, classified into `in_line` (≤20%) / `notable` (20–50%) / `extreme` (>50%) bands.
3. **11-GICS warning matrix** — sector-specific interpretive caveats (e.g. "P/E for energy issuers is commodity-cycle distorted") loaded from `references/sector-warnings.md`, plucked by the anchor's classified `schema_id`.
4. **Opt-in CLI flag** — `comps_compute.py --sector-benchmark` adds an `etf_benchmark` block to compute-mode output. Absent flag → output unchanged from v2.2.0-c shape (backward compatible).

**Architectural note**: this is a runtime-side **read** of pre-built JSON. v2.2.0-c sector classification + `anchor.schema_id` are the FOUNDATION; v2.2.0-c-bench reads `anchor.schema_id` from the runtime classifier and reads `references/sector-etf-aggregate-<ETF>.json` for the matching SPDR ETF. Per-ETF schema_id mapping is fixed (XLF→bank, XLK→tech-saas, XLRE→reit, XLE→energy, XLU→utilities, XLB/XLI/XLY/XLP/XLV/XLC→default).

**Non-goals**: classifier work, schema work, new multiple/indicator formulas, non-US tickers (emit `etf_benchmark.status: "skipped"`), AFFO, dividend-yield aggregate, time-series aggregate store. All deferred.

## 2. Why

- v2.2.0-c gives "is this expensive vs my own historicals?" via `multiples_compute` + `divergence` (vs direct mode). The next question buy-side memos actually need is "is this expensive **for its sector**?" — that requires a sector benchmark.
- SPDR Select Sector ETFs are the most common reference benchmark for US equity sector-relative valuation; aligning aggregate output to XLE/XLB/.../XLRE makes the divergence directly actionable.
- All compute math already lives in `comps_compute.py` (per-schema formulas + indicator dispatch). Aggregator just needs to drive that math over each ETF's holdings + holdings-weight blend.
- v2.2.0-l unblocked the underlying memo-fetch raw fields (`net_income` / `total_stockholders_equity` / `depreciation_amortization` / `revenue` / etc.); no new XBRL fetch work is required.

## 3. Scope decisions (carried forward from brainstorming)

| Decision | Choice | Reasoning |
|---|---|---|
| Aggregate composition | **Use each ETF's mapped schema** (XLF→bank → trailingPE/forwardPE/priceToBook/priceToTangibleBook + ROE; XLK→tech-saas; …) | Schema is already the SoT for "which multiples apply to this sector"; dual-coding fixed-5+sector-specific would drift. Divergence emitted only for keys both sides have. |
| Indicators in aggregate | **Yes** — also weight indicators (ROE / FCF_margin / Rule-of-40 / etc., per schema) | The 8 v2.2.0-c indicators are precisely the sector-relative signal users care about; aggregate without indicators would underuse v2.2.0-c. |
| Aggregate fetch timing | **Eager scheduled (weekly GHA cron)** | Runtime always fast (read local JSON); freshness predictable. Cold-start lazy fetch (~70 min for one ETF) ruled out. |
| Per-holding compute path | **Reuse `comps_compute.compute_multiples_from_memo_fetch` + `compute_indicators_from_memo_fetch`** (rename them to drop the `_` prefix so etf_aggregator can import) | Single source of truth for compute math; no duplication / drift. |
| ETF holdings source | **yfinance `funds_data.top_holdings`** | Stays inside primary-source backbone; SPDR factsheet PDF not needed; no new external scraper. |
| Output block name | **`etf_benchmark`** (NOT `sector`) | `anchor.sector` is already a string field in v2.2.0-c output (yfinance industry sector name); reusing the key would be a collision. ROADMAP entry uses `etf_benchmark`. |
| Divergence threshold | **20% / 50%** (`in_line` / `notable` / `extreme`) | Sector-relative valuation is a business signal (premium / discount), not a data integrity check; wider bands than v2.2.0-c's 5% / 15% direct-vs-compute alert. |
| Geographic scope | **US-only**; non-US tickers emit `etf_benchmark: {status: "skipped"}` | Mirrors v2.2.0-c's discipline; cross-country ETF benchmarks deferred to v2.2.0-c-{jp,tw,kr,cn}. |
| Backward compat | `--sector-benchmark` flag **opt-in**; absent flag → output identical to v2.2.0-c shape, no `etf_benchmark` key | Mirrors v2.2.0-c's flag-gated additive philosophy. |

## 4. Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│  Build-time (weekly GHA — .github/workflows/sector-etf-aggregates.yml) │
│  ────────────────────────                                              │
│  cron 'sat 06:00 UTC' (+ workflow_dispatch)                            │
│    └─ uv run skills/analysis-comps/scripts/etf_aggregator.py --all     │
│         For ETF in [XLE, XLB, XLI, XLY, XLP, XLV, XLF,                 │
│                    XLK, XLC, XLU, XLRE]:                               │
│           1. yfinance funds_data.top_holdings → list of (ticker, wt)   │
│              (via `yfinance_client.py --action holdings --ticker XLK`) │
│           2. per holding: data-us pack.py --pack memo-fetch (cached)   │
│           3. for each holding, run compute_multiples_from_memo_fetch + │
│              compute_indicators_from_memo_fetch under the ETF's        │
│              mapped schema (XLF→bank etc.)                             │
│           4. drop outliers per multiple (out of [0, 200] bound)        │
│           5. holdings-weighted average over surviving values           │
│         writes references/sector-etf-aggregate-<ETF>.json (×11)        │
│                                                                         │
│  Runtime (analysis-comps --mode compute --sector-benchmark)            │
│  ────────────────────────                                              │
│  comps_compute.py                                                      │
│    ├─ classify anchor (already done in v2.2.0-c) → anchor.schema_id    │
│    ├─ if --sector-benchmark + US ticker:                               │
│    │    ├─ schema_id → ETF_id (fixed map)                              │
│    │    ├─ load references/sector-etf-aggregate-<ETF>.json             │
│    │    ├─ compute divergence per multiple_id ∈ schema.multiples       │
│    │    │   (anchor.multiples_compute[m] vs aggregate.multiples[m])    │
│    │    │   bands: 20% / 50% — in_line / notable / extreme             │
│    │    ├─ same for indicators (anchor.indicators[i].value vs          │
│    │    │   aggregate.indicators[i])                                    │
│    │    ├─ load references/sector-warnings.md → pluck row by schema_id │
│    │    └─ emit anchor.etf_benchmark = {etf, as_of, aggregate,         │
│    │                                     divergence, warnings}         │
│    ├─ if --sector-benchmark + non-US ticker:                           │
│    │    emit anchor.etf_benchmark = {status: "skipped", reason: ...}   │
│    └─ else (no flag): output unchanged (no etf_benchmark key)          │
└────────────────────────────────────────────────────────────────────────┘
```

## 5. Files added / modified

**New**:
- `skills/analysis-comps/scripts/etf_aggregator.py` — build-time aggregator (CLI: `--etf XLK` / `--all`)
- `skills/analysis-comps/references/sector-etf-aggregate-<ETF>.json` × 11 (initial commit; weekly GHA refreshes)
- `skills/analysis-comps/references/sector-warnings.md` — 11-row markdown table indexed by `schema_id`
- `skills/analysis-comps/references/etf-schema-map.json` — `{XLF: bank, XLK: tech-saas, ...}` SoT
- `tests/analysis/test_etf_aggregator.py` — unit tests for aggregator math (deterministic fixtures, no network)
- `tests/analysis/test_comps_etf_benchmark.py` — runtime `--sector-benchmark` tests using offline aggregate fixtures
- `tests/analysis/fixtures/sector-etf-aggregate-{XLK,XLF,XLRE}-sample.json` — small fake aggregates for offline runtime tests
- `.github/workflows/sector-etf-aggregates.yml` — weekly cron + `workflow_dispatch`

**Modified**:
- `skills/analysis-comps/scripts/comps_compute.py` — (a) rename `_compute_multiples_from_memo_fetch` → `compute_multiples_from_memo_fetch` and same for `_compute_indicators_from_memo_fetch` (export contract for etf_aggregator); (b) add `--sector-benchmark` CLI flag; (c) add `etf_benchmark` block emission
- `skills/analysis-comps/references/schema-compute-output.json` — add `etf_benchmark` block under `anchor` (allOf branch on `--sector-benchmark` invocation)
- `skills/analysis-comps/SKILL.md` — document `--sector-benchmark` flag + opt-in workflow
- `skills/data-us/scripts/yfinance_client.py` — add `--action holdings` (returns top-holdings list with weights)
- `investing-toolkit/ROADMAP.md` — close v2.2.0-c-bench entry; spawn v2.2.0-c-{jp,tw,kr,cn} placeholders
- Memory pointer `project_investing_toolkit_v2x_roadmap.md` — note v2.2.0-c-bench shipped

## 6. Component specs

### 6.1 ETF → schema_id mapping (`etf-schema-map.json`)

```json
{
  "XLE":  "energy",
  "XLB":  "default",
  "XLI":  "default",
  "XLY":  "default",
  "XLP":  "default",
  "XLV":  "default",
  "XLF":  "bank",
  "XLK":  "tech-saas",
  "XLC":  "default",
  "XLU":  "utilities",
  "XLRE": "reit"
}
```

Routing rationale (one-line per ETF):
- **XLF→bank**: top weights are JPM/BAC/WFC/C/GS — banks dominate; insurance/asset-manager subgroups handled by per-holding classification (see §6.2).
- **XLK→tech-saas**: top weights are MSFT/AAPL/AVGO/ORCL/CRM — software dominates; semis (NVDA/INTC) handled per-holding via `tech-semis` schema.
- **XLRE→reit**: ETF is REIT-only by construction.
- **XLE→energy** / **XLU→utilities**: ETFs are sector-pure.
- **XLB/XLI/XLY/XLP/XLV/XLC→default**: heterogeneous sub-industries; default 5-multiple set is the safe common denominator.

**Per-holding override**: when computing the ETF aggregate, each holding is itself classified (using v2.2.0-c `classify_pack`) and computed under ITS schema. The ETF-level schema only governs which multiples appear in the aggregate output — the holdings-weighted average is taken across holdings whose schema includes that multiple. (E.g. XLF aggregate `priceToBook` averages over banks + insurance + asset-managers — all three schemas include `priceToBook`. ROE averages only over banks because only `bank` schema includes ROE.)

### 6.2 `etf_aggregator.py`

```python
def aggregate_etf(etf: str) -> dict:
    """
    Returns:
      {
        "etf": "XLK",
        "schema_id": "tech-saas",
        "as_of": "2026-05-04",
        "_meta": {
          "holdings_count": 75,
          "weight_coverage_pct": 94.2,
          "outliers_dropped": {"trailingPE": 2, "priceToSales": 1},
          "source": "yfinance funds_data + data-us memo-fetch"
        },
        "multiples": {
          "trailingPE": 24.1, "forwardPE": null, "priceToSales": 6.2, "priceToBook": 5.8,
          "evEbitda": 18.4
        },
        "indicators": {
          "gross_margin":     58.3,
          "operating_margin": 22.1,
          "FCF_yield":        4.8,
          "rule_of_40":       0.42
        }
      }
    """
```

**Algorithm**:
1. `yfinance_client.py --action holdings --ticker <etf>` → list `[{ticker, weight}, …]` (top ~75 by weight; sufficient — `weight_coverage_pct` records actual coverage).
2. For each `(holding_ticker, weight)`:
   - Skip if holding non-US (ADR like NXPI / ASML) — log into `_meta.skipped_holdings`.
   - `data-us/scripts/pack.py --pack memo-fetch <holding_ticker>` (reuses cache; offline if cached fresh).
   - Run `compute_multiples_from_memo_fetch(memo, direct={}, schema=holding_schema)` and `compute_indicators_from_memo_fetch(memo, holding_schema)` where `holding_schema` is the holding's classified schema (per `classify_pack`).
3. For each multiple_id in the **ETF's mapped schema** (§6.1): collect all non-null values from holdings whose schema includes that multiple_id; drop values outside `[0, 200]` (logged in `_meta.outliers_dropped`); take holdings-weighted average — `Σ(weight × value) / Σ(weight where value is non-null and in bounds)`.
4. Same for indicators (per indicator_id in ETF's mapped schema; bound `[-100, 200]` for percentage indicators since margins/ROE are pct).
5. Persist to `references/sector-etf-aggregate-<etf>.json`.

**CLI**:
- `etf_aggregator.py --etf XLK` (single ETF — useful for ad-hoc refresh / debugging)
- `etf_aggregator.py --all` (all 11 — used by GHA workflow)

**Rate limits**: SEC EDGAR companyfacts rate-limited; rely on `data-us pack.py` existing cache. Cold cache: ~825 holdings × ~10s memo-fetch = ~140 min; well under GHA 6h budget. Warm cache: < 5 min.

### 6.3 `sector-warnings.md`

Markdown table SoT, one row per `schema_id` (9 schemas + 2 unmapped — total 11 schema_ids actively used by routing). Loaded by `comps_compute.py --sector-benchmark` and pasted into `etf_benchmark.warnings: [...]`.

Schema-id-keyed (NOT yfinance sector name) to align with v2.2.0-c routing source-of-truth.

Example rows:

| `schema_id` | warning_text |
|---|---|
| `default` | "Default 5-multiple set; appropriate for cash-generating businesses with positive earnings. Verify operating-margin / FCF_yield indicators are non-negative; if not, sector_specific schema may be more appropriate." |
| `bank` | "Bank P/E and P/B work; EV/EBITDA is undefined (no operating-cash-flow concept of cash earnings). ROE is the primary profitability lens. Tier 1 capital + credit quality (deferred — supplemental disclosure) drive equity multiples in conjunction." |
| `insurance` | "Combined ratio, reserves, premium-growth are the primary disclosures (deferred — bank/insurance supplemental disclosure not in standard XBRL). P/B is the most reliable price multiple." |
| `asset-manager` | "P/AUM is the canonical valuation metric (deferred — AUM not standard XBRL). P/E and P/B available but interpretive." |
| `reit` | "P/FFO + EV/EBITDAre are REIT-canonical valuation; net-income-based P/E is misleading (depreciation distortion). AFFO requires gain-on-sale + straight-line rent adjustments — not in standard XBRL — so P/FFO only." |
| `tech-saas` | "Rule-of-40 (revenue growth + operating margin) is the primary growth/quality lens. Pre-profit SaaS issuers may have negative trailingPE — interpret with operating-margin floor." |
| `tech-semis` | "Cyclical industry; trailingPE near cycle troughs may be inflated and near peaks deflated. Inventory + book-to-bill ratios are sector-supplemental." |
| `energy` | "P/E and EV/EBITDA on energy issuers are commodity-cycle distorted; production-volume + EV/EBITDAX (deferred — exploration_expense not standard XBRL) are more reliable in extreme cycle phases." |
| `utilities` | "Dividend yield is the canonical valuation metric for utilities (deferred — dividend per share not standard XBRL); P/E and EV/EBITDA available but interpretive given regulated-rate-base economics." |

(Total 9 rows; `unknown_sector` falls back to `default` warning per v2.2.0-c routing.)

### 6.4 Output schema extension — `etf_benchmark` block

Existing v2.2.0-c output **unchanged** when `--sector-benchmark` is absent. When the flag is present, anchor block gains a sibling `etf_benchmark` key:

```jsonc
{
  "anchor": {
    "ticker": "AAPL",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "schema_id": "default",
    "schema_routing_source": "sector_default",
    "multiples_direct":  { "...v2.2.0-c shape unchanged..." },
    "multiples_compute": { "...v2.2.0-c shape unchanged..." },
    "divergence":        { "...v2.2.0-c shape unchanged..." },
    "indicators":        { "...v2.2.0-c shape unchanged..." },
    "compute_provenance":{ "...v2.2.0-c shape unchanged..." },
    "etf_benchmark": {
      "etf":       "XLK",
      "schema_id": "tech-saas",
      "as_of":     "2026-05-04",
      "_meta":     {"holdings_count": 75, "weight_coverage_pct": 94.2, "freshness_days": 1},
      "multiples": {
        "trailingPE":  {"individual": 28.0, "etf_aggregate": 24.1, "delta_pct": 16.2,  "band": "in_line"},
        "priceToBook": {"individual": 7.2,  "etf_aggregate": 5.8,  "delta_pct": 24.1,  "band": "notable"},
        "priceToSales":{"individual": 8.1,  "etf_aggregate": 6.2,  "delta_pct": 30.6,  "band": "notable"},
        "evEbitda":    {"individual": 21.0, "etf_aggregate": 18.4, "delta_pct": 14.1,  "band": "in_line"},
        "forwardPE":   {"individual": 25.0, "etf_aggregate": null, "delta_pct": null,  "band": "n/a"}
      },
      "indicators": {
        "gross_margin":     {"individual": 45.2, "etf_aggregate": 58.3, "delta_pct": -22.5, "band": "notable"},
        "operating_margin": {"individual": 30.1, "etf_aggregate": 22.1, "delta_pct":  36.2, "band": "notable"},
        "FCF_yield":        {"individual": 5.9,  "etf_aggregate": 4.8,  "delta_pct":  22.9, "band": "notable"}
      },
      "warnings": [
        "Default 5-multiple set; appropriate for cash-generating businesses with positive earnings. ..."
      ]
    }
  },
  ...
}
```

> **AAPL routing nuance**: AAPL classifies as `default` per `sector-routing.yaml` (Technology + "Consumer Electronics" not matching any `industry_contains` rule). XLK maps to `tech-saas`. The aggregate's `schema_id` field surfaces "tech-saas"; the divergence is computed only over multiples present in *both* the anchor's `multiples_compute` and the aggregate (intersection of `default` and `tech-saas` schemas, which share the universal 5). Indicators likewise — the intersection of `default.indicators` (gross_margin/operating_margin/FCF_yield) and `tech-saas.indicators` (rule_of_40/operating_margin/FCF_yield/...).

**Divergence band thresholds**:
- `|delta_pct| ≤ 20%` → `in_line`
- `20% < |delta_pct| ≤ 50%` → `notable`
- `|delta_pct| > 50%` → `extreme`
- one side `null` → `band: "n/a"`, `delta_pct: null`

**Non-US ticker**:
```json
"etf_benchmark": {
  "status": "skipped",
  "reason": "non-US ticker; SPDR sector ETFs are US-only. Cross-country sector benchmark deferred to v2.2.0-c-{jp,tw,kr,cn}."
}
```

**`--sector-benchmark` flag absent** — `etf_benchmark` key absent entirely (v2.2.0-c output unchanged).

**Stale aggregate guard**: when loaded `sector-etf-aggregate-<etf>.json` is `>14` days old, append `etf_benchmark.warnings: ["aggregate stale: as_of=YYYY-MM-DD, freshness_days=N — weekly cron may have skipped a Saturday"]`.

## 7. Testing

### 7.1 Unit tests — `tests/analysis/test_etf_aggregator.py` (no network)

- `test_holdings_weighted_average_basic` — three holdings with weights [0.5, 0.3, 0.2] and known multiples → weighted average matches hand-computed result.
- `test_outlier_drop_low_high` — multiples [-5, 8, 12, 250] with weights [0.25, 0.25, 0.25, 0.25] → drop -5 and 250, average the middle two; `_meta.outliers_dropped["trailingPE"] == 2`.
- `test_weight_coverage_partial` — total holdings weight 1.00, two holdings (weights 0.4 + 0.3) skipped (non-US ADR) → `_meta.weight_coverage_pct == 30.0` (only 0.3 consumed; 0.4 was skipped explicitly).
- `test_per_holding_schema_dispatch` — XLF aggregate over [JPM(bank), MET(insurance), BLK(asset-manager)] → ROE averaged only over JPM (bank schema includes ROE; insurance/asset-manager don't); priceToBook averaged over all 3.
- `test_indicator_aggregate_pct_unit` — indicator aggregate uses the same `value` field shape as comps_compute output (numeric, percentage).
- `test_missing_data_holding_handled` — one holding's memo-fetch missing equity → priceToBook null for that holding → weighted average uses only contributors; warning logged.
- `test_etf_to_schema_map_loaded` — `etf-schema-map.json` exposes all 11 ETFs and only known schema_ids.

### 7.2 Runtime tests — `tests/analysis/test_comps_etf_benchmark.py` (no network, offline aggregate fixtures)

- `test_etf_benchmark_block_emitted_when_flag` — anchor pack + memo-fetch fixture + `--sector-benchmark` → output has `anchor.etf_benchmark.etf == "XLK"`, `multiples.trailingPE.band` ∈ {`in_line`, `notable`, `extreme`}.
- `test_no_etf_benchmark_block_without_flag` — same anchor without flag → output unchanged from v2.2.0-c (no `etf_benchmark` key); existing v2.2.0-c golden snapshot still passes.
- `test_band_classification_in_line` — anchor 28.0 vs aggregate 24.1 → `band: "in_line"` (delta 16.2%).
- `test_band_classification_notable` — anchor 7.2 vs aggregate 5.8 → `band: "notable"` (delta 24.1%).
- `test_band_classification_extreme` — anchor 100 vs aggregate 50 → `band: "extreme"` (delta 100%).
- `test_band_n_a_on_null_aggregate` — `forwardPE` null in aggregate → `band: "n/a"`.
- `test_non_us_ticker_skipped` — anchor `7203.T` → `etf_benchmark: {status: "skipped", reason: ...}`.
- `test_stale_aggregate_warning` — fixture `as_of` 20 days ago → `warnings` includes "aggregate stale".
- `test_etf_unmapped_schema_falls_back_to_default` — anchor classified as `default` (XLB/XLI/etc.) → routed to that ETF if present; otherwise XLY (default-mapped fallback). Verify divergence emitted only over intersection of anchor schema multiples and aggregate schema multiples.

### 7.3 Network smoke tests — `tests/analysis/test_etf_aggregator_live.py` (`@pytest.mark.network`)

- `test_aggregate_xlk_live` — real yfinance + SEC EDGAR fetch of XLK aggregate; deselected by default; weekly CI runs only.
- `test_compute_with_sector_benchmark_aapl_live` — end-to-end AAPL → XLK aggregate divergence, asserts `multiples.trailingPE.delta_pct` non-null and band ∈ {in_line, notable, extreme}.

## 8. CI integration

### 8.1 New workflow: `.github/workflows/sector-etf-aggregates.yml`

- Trigger: cron `'0 6 * * 6'` (UTC sat 06:00 = Asia/Taipei sat 14:00); also `workflow_dispatch` for manual refresh.
- Job: `uv run skills/analysis-comps/scripts/etf_aggregator.py --all`
- Output: 11 JSON files committed by GHA bot user; commit message `chore(sector-aggregates): weekly refresh YYYY-MM-DD`.
- Failure handling: on job failure, open GitHub issue tagged `sector-aggregate-stale` (use `peter-evans/create-issue-from-file` or equivalent).
- Caching: GHA cache for `~/.cache/investing-toolkit/sec_edgar/companyfacts/*.json` keyed by week to avoid re-fetching the same companyfacts each Saturday.
- `PYTHONDONTWRITEBYTECODE=1` env (per memory: avoids `__pycache__` triggering skill-folder validator).

### 8.2 Existing offline CI (`investing-toolkit pytest -m "not network"`)

New unit + runtime tests automatically picked up by the offline selection; no workflow change needed.

## 9. ROADMAP closeout

When v2.2.0-c-bench ships:

1. Move §v2.2.0-c-bench entry from "Future Roadmap (planning)" to a new closed section `### ~~v2.2.0-c-bench — SPDR sector ETF aggregate benchmark layer~~ ✅ closed YYYY-MM-DD (PR #N)` with PR link.
2. Add new "Future Roadmap" entries:
   - **v2.2.0-c-{jp,tw,kr,cn}** — per-region sector ETF benchmark; gated on observed buy-side memo workflow demand. Candidates: iShares MSCI Japan sector ETFs / NEXT FUNDS TOPIX-17 (JP); FTSE TWSE Taiwan 50 sector slices (TW); KODEX 200 sector ETFs (KR); CSI 300 sector indexes (CN).
3. Update memory pointer `project_investing_toolkit_v2x_roadmap.md` to reflect the new closed entry.

## 10. Deferred items (NOT in v2.2.0-c-bench)

- Per-region sector ETF benchmarks (JP/TW/KR/CN) — separate `v2.2.0-c-{jp,tw,kr,cn}` follow-ups.
- AFFO (REIT goes P/FFO only — already handled in v2.2.0-c reit schema).
- Sector-warnings i18n (EN-only in v1).
- SPDR factsheet PDF cross-check (audit redundancy; primary stays holdings-weighted compute).
- ETF holdings fallback to SPDR official CSV (yfinance only in v1; fallback added if yfinance breaks).
- Historical ETF aggregate time-series store (commit history acts as informal time-series; no dedicated DB).
- Dividend Yield in SPDR aggregate (XLU's canonical multiple; needs new dividend XBRL field — deferred to memo-fetch extension PR).
- Per-issuer override CLI for ETF aggregate routing (currently fixed via `etf-schema-map.json`).

## 11. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| yfinance `funds_data.top_holdings` API instability / rate limit | medium-high | weekly aggregate job fails | GHA fail → auto-issue; retry × 3 with exponential backoff; runtime always reads last successful committed JSON; stale-aggregate guard surfaces freshness in output |
| SEC EDGAR rate limit on weekly batch | medium | aggregate job slow / partial | sequential fetch + 100ms delay (existing data-us cache layer); GHA cache for companyfacts; warm-cache run < 5 min |
| Mega-cap dominated ETF (XLK top-10 ~60% weight) | low-medium | aggregate becomes "AAPL+MSFT estimate" not sector estimate | `_meta.weight_coverage_pct` + `holdings_count` documents; warnings can flag; user-side interpretation responsibility — by design |
| Non-US holdings in ETF (XLK has NXPI / ASML ADRs) | low | aggregate contaminated by non-US issuers | classifier skip for non-US tickers; `_meta.weight_coverage_pct` reflects actual non-skipped weight |
| Per-holding schema mismatch (e.g. NVDA in XLK → tech-semis, not tech-saas) | medium | XLK aggregate `rule_of_40` averages over both saas and semis | by design — aggregate represents the ETF's heterogeneous reality. Per-holding schema dispatch ensures each holding's *math* is correct under its own schema; ETF aggregate exposes the average of the surviving values. Documented in `_meta.schema_dispatch` |
| Aggregate JSON git churn | low | history noise | 11 files / 1 commit per week; commit message tagged `chore(sector-aggregates):` for filterability |
| Weekly cron skips a Saturday (GHA outage) | low | aggregate stale by 1-2 weeks | freshness recorded in `_meta`; runtime warns when > 14 days |
| `etf_benchmark` block adds breadth to compute output | low | downstream parsers need to ignore unknown key | flag-gated additive; v2.2.0-c shape preserved when flag absent |

## 12. Acceptance criteria

- [ ] `uv run skills/analysis-comps/scripts/comps_compute.py --mode compute --sector-benchmark --anchor <aapl.json> --anchor-base <aapl-memo.json> --peers ...` produces `anchor.etf_benchmark.etf == "XLK"`, `etf_benchmark.multiples.trailingPE.delta_pct` numeric, `band ∈ {in_line, notable, extreme}`.
- [ ] Same for JPM (`bank` schema) → `etf == "XLF"`, `etf_benchmark.indicators.ROE` non-null with band classification.
- [ ] Same for Realty Income (O) (`reit` schema) → `etf == "XLRE"`, `etf_benchmark.multiples.priceToFFO.delta_pct` numeric.
- [ ] Same for non-US 7203.T → `etf_benchmark: {status: "skipped"}`.
- [ ] Without `--sector-benchmark`, output identical to v2.2.0-c shape (no `etf_benchmark` key); existing v2.2.0-c golden snapshot passes.
- [ ] `etf_aggregator.py --all` populates 11 `references/sector-etf-aggregate-*.json` files; each has non-null `as_of`, `multiples`, `indicators`, `_meta`.
- [ ] GHA workflow `sector-etf-aggregates.yml` runs end-to-end on a `workflow_dispatch` invocation.
- [ ] Existing `pytest -m "not network"` passes (no regressions); new unit + runtime tests included.
- [ ] ROADMAP.md updated; v2.2.0-c-{jp,tw,kr,cn} entries created.
- [ ] `schema-compute-output.json` validates against actual emitted output for both with-flag and without-flag invocations.
- [ ] Stale-aggregate guard surfaces "aggregate stale" warning when `as_of > 14 days`.

## 13. References

- v2.2.0-c sector multiples spec: `docs/superpowers/specs/2026-05-04-investing-toolkit-v2.2.0-c-sector-multiples-design.md`
- v2.2.0-b comps-compute spec: `docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md`
- v2.2.0-l memo-fetch raw-field extension: PR #239
- ROADMAP §v2.2.0-c-bench
- ADR-0003: US T3 mapping pattern
- ADR-0008: analysis-comps single-consumer model (no MCP exposure)
- yfinance docs: `funds_data` API for ETF holdings
- SPDR Select Sector ETFs: ssga.com/us/en/intermediary/etfs (factsheet reference, NOT used as primary source)
