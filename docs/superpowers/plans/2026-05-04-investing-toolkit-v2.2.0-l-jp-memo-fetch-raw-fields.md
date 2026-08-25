# investing-toolkit v2.2.0-l-jp — JP cross-country symmetry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend JP `data-jp` memo-fetch with the 6 canonical raw fields surfaced by US v2.2.0-l (PR #239), maintaining cross-country symmetry on the canonical T3 surface for Tier 2 (yfinance fallback) path + Tier A (EDINET) concept-mapping future-prep.

**Architecture:** JP uses a different data architecture than US — Tier A (EDINET) canonical extraction is currently **placeholder only** (deferred to a future PR), while Tier 2 (yfinance fallback via `_build_canonical_from_yf_financials_jp()`) is fully populated with 11 canonical fields. This PR extends BOTH paths: (1) `_YF_LABEL_MAP_JP` + Tier 2 canonical assembly with 6 new yfinance labels routed into the same income_statement / cash_flow / balance_sheet block structure used by data-us; (2) `KEY_CONCEPTS` in edinet_client.py with 6 new EDINET XBRL concept fallback chains (jpcrp/jppfs taxonomy, NOT us-gaap) — Tier A raw extraction picks them up automatically since it filters within already-downloaded full filings (no new network calls). **Cross-country compute-mode end-to-end testing on JP** is deliberately deferred (would require new JP peer fixtures + cross-currency normalization design) — separate follow-up PR.

**Tech Stack:** Python 3.11, `uv run` (PEP 723), pytest, EDINET (金融庁 Tier A), yfinance scrape (Tier 2 fallback), JSON Schema draft-07.

**Reference:**
- US PR #239 (v2.2.0-l) — the precedent this PR mirrors for JP
- `investing-toolkit/skills/data-jp/scripts/edinet_client.py:95-158` — existing `KEY_CONCEPTS` dict with 13 fields
- `investing-toolkit/skills/data-jp/scripts/pack.py:174-294` — existing `_YF_LABEL_MAP_JP` + `_build_canonical_from_yf_financials_jp()`
- `investing-toolkit/tests/data/fixtures/data-jp-memo-fetch-sample.json` — Toyota 7203 Tier 2 fixture (2542 lines)
- ROADMAP §v2.2.0-l (closed entry mentions cross-country symmetry as `v2.2.0-l-{jp,tw,kr,cn}` follow-ups)

**Scope:**
- ✅ Tier 2 (yfinance) canonical extraction extended with 6 new fields
- ✅ Tier A (EDINET) `KEY_CONCEPTS` extended with 6 new XBRL chains (raw extraction works automatically; canonical block routing deferred)
- ✅ Toyota 7203 fixture regenerated with 6 new fields (graceful `[]` for SBC + standalone goodwill — neither disclosed by yfinance for Toyota)
- ✅ Network smoke test asserting Tier 2 surfaces the new fields
- ❌ **OUT OF SCOPE**: JP slim fixture for analysis-comps (would need JP peer fixtures + cross-currency design)
- ❌ **OUT OF SCOPE**: Tier A EDINET canonical block routing (full `_normalize_edinet()` equivalent of US `_normalize_dcf()` — separate future PR)
- ❌ **OUT OF SCOPE**: TW / KR / CN cross-country symmetry (separate per-country PRs)

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `investing-toolkit/skills/data-jp/scripts/pack.py` | Modify | Extend `_YF_LABEL_MAP_JP` with 6 new entries; extend `_build_canonical_from_yf_financials_jp()` to emit them in 3 canonical blocks |
| `investing-toolkit/skills/data-jp/scripts/edinet_client.py` | Modify | Extend `KEY_CONCEPTS` dict with 6 new EDINET XBRL fallback chains (raw extraction future-prep) |
| `investing-toolkit/skills/data-jp/references/schema-memo-fetch.json` | Modify | Update `income_statement` / `cash_flow` / `balance_sheet` description strings to mention new fields |
| `investing-toolkit/tests/data/fixtures/data-jp-memo-fetch-sample.json` | Modify | Regenerate / extend Toyota 7203 fixture with 6 new fields |
| `investing-toolkit/tests/data/test_data_jp.py` | Modify | Add network test `test_jp_memo_fetch_toyota_has_extended_canonical_fields` asserting Tier 2 surfaces new fields |
| `investing-toolkit/ROADMAP.md` | Modify | Move v2.2.0-l-jp from spawned-future to closed; note Tier A canonical extraction still pending |

---

## Field Mapping Reference

For each new canonical field, **two parallel mappings** are added:
1. **Tier 2 (yfinance label)** in `_YF_LABEL_MAP_JP` — picked from actual labels observed in Toyota 7203 fixture
2. **Tier A (EDINET XBRL concept)** in `KEY_CONCEPTS` — based on jpcrp/jppfs taxonomy convention (jp_cor namespace prefix dropped per existing `KEY_CONCEPTS` style)

| Canonical field | Block | Tier 2 yfinance labels | Tier A EDINET XBRL concepts |
|---|---|---|---|
| `gross_profit` | income_statement | `["Gross Profit"]` | `["GrossProfitLossSummaryOfBusinessResults", "GrossProfitLossIFRSSummaryOfBusinessResults", "GrossProfit"]` |
| `depreciation_amortization` | cash_flow | `["Depreciation And Amortization", "Depreciation Amortization Depletion", "Reconciled Depreciation"]` | `["DepreciationAndAmortizationOpeCFCashFlowStatement", "DepreciationDepletionAndAmortizationCashFlowStatement", "DepreciationAndAmortizationCashFlowStatement"]` |
| `stock_based_compensation` | cash_flow | `["Stock Based Compensation", "Stock Based Compensation Expense"]` | `["ShareBasedCompensationExpense", "EmployeeStockOptionExpense", "ShareBasedPaymentArrangements"]` |
| `total_stockholders_equity` | balance_sheet | `["Stockholders Equity", "Common Stock Equity"]` | `["StockholdersEquityAttributableToParentCompanySummaryOfBusinessResults", "EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults", "StockholdersEquity"]` |
| `intangible_assets` | balance_sheet | `["Other Intangible Assets", "Goodwill And Other Intangible Assets"]` | `["IntangibleAssetsNetExcludingGoodwillSummaryOfBusinessResults", "OtherIntangibleAssetsNetIFRSSummaryOfBusinessResults", "IntangibleAssets"]` |
| `goodwill` | balance_sheet | `["Goodwill"]` | `["GoodwillSummaryOfBusinessResults", "GoodwillIFRSSummaryOfBusinessResults", "Goodwill"]` |

**JP-specific behaviour notes** (asserted by tests, not bugs):
- **Stock-based compensation**: Toyota 7203 (JP-GAAP transitioning to IFRS) does NOT disclose SBC to yfinance → array will be `[]`. Most JP issuers same. IFRS adopters (Sony 6758, SoftBank 9984) have richer coverage. Pattern follows US AAPL goodwill / intangibles `[]` precedent.
- **Standalone goodwill**: yfinance combines goodwill into "Goodwill And Other Intangible Assets" line for many JP issuers (including Toyota) → standalone `Goodwill` label may be missing. Captured as `[]`.
- **Equity terminology**: JP-GAAP 純資産 (net assets) includes minority interest; we EXCLUDE the `Total Equity Gross Minority Interest` yfinance label deliberately — `Stockholders Equity` is the parent-attributable variant matching US convention.

---

## Tasks

### Task 1: Extend `_YF_LABEL_MAP_JP` with 6 new yfinance labels

**Files:**
- Modify: `investing-toolkit/skills/data-jp/scripts/pack.py:174-185`

- [ ] **Step 1: Read current dict**

Confirm current `_YF_LABEL_MAP_JP` has 10 entries (revenue / operating_income / net_income / operating_cash_flow / capex / free_cash_flow / long_term_debt / short_term_debt / total_debt / cash).

- [ ] **Step 2: Extend dict in place**

Replace the existing dict literal (lines 174-185) with:

```python
_YF_LABEL_MAP_JP = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "operating_income": ["Operating Income", "Total Operating Income As Reported"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "gross_profit": ["Gross Profit"],
    "operating_cash_flow": ["Operating Cash Flow"],
    "capex": ["Capital Expenditure"],
    "free_cash_flow": ["Free Cash Flow"],
    "depreciation_amortization": [
        "Depreciation And Amortization",
        "Depreciation Amortization Depletion",
        "Reconciled Depreciation",
    ],
    "stock_based_compensation": [
        "Stock Based Compensation",
        "Stock Based Compensation Expense",
    ],
    "long_term_debt": ["Long Term Debt"],
    "short_term_debt": ["Current Debt"],
    "total_debt": ["Total Debt"],
    "cash": ["Cash And Cash Equivalents"],
    "total_stockholders_equity": [
        "Stockholders Equity",
        "Common Stock Equity",
    ],
    "intangible_assets": [
        "Other Intangible Assets",
        "Goodwill And Other Intangible Assets",
    ],
    "goodwill": ["Goodwill"],
}
```

(New entries placed contiguously near related existing keys: `gross_profit` after `net_income`; `depreciation_amortization` + `stock_based_compensation` after `free_cash_flow`; `total_stockholders_equity` + `intangible_assets` + `goodwill` after `cash`.)

- [ ] **Step 3: Lint quick-check**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run python -c "import ast; ast.parse(open('investing-toolkit/skills/data-jp/scripts/pack.py').read())"`
Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/skills/data-jp/scripts/pack.py
git commit -m "$(cat <<'EOF'
feat(data-jp): extend _YF_LABEL_MAP_JP with 6 raw fields (v2.2.0-l-jp)

Adds yfinance label fallback chains for: gross_profit, depreciation_amortization,
stock_based_compensation, total_stockholders_equity, intangible_assets, goodwill.
Tier 2 _build_canonical wiring + emission in next commit.

Mirrors US PR #239 v2.2.0-l for JP cross-country symmetry.
Reference: ROADMAP §v2.2.0-l (spawned cross-country follow-up).
EOF
)"
```

---

### Task 2: Wire 6 new fields into `_build_canonical_from_yf_financials_jp()`

**Files:**
- Modify: `investing-toolkit/skills/data-jp/scripts/pack.py:188-294` (`_build_canonical_from_yf_financials_jp` function)

- [ ] **Step 1: Add new `_extract` calls**

In the assembly section (after the existing `cash, cash_label = _extract(balance, "cash")` line at ~232), add 6 new local variable bindings:

```python
    gross_profit, gp_label = _extract(income, "gross_profit")
    depreciation_amortization, da_label = _extract(cashflow, "depreciation_amortization")
    stock_based_compensation, sbc_label = _extract(cashflow, "stock_based_compensation")
    total_stockholders_equity, eq_label = _extract(balance, "total_stockholders_equity")
    intangible_assets, intang_label = _extract(balance, "intangible_assets")
    goodwill, gw_label = _extract(balance, "goodwill")
```

- [ ] **Step 2: Extend the return dict**

Locate the existing `return {` block (line ~251). REPLACE it with:

```python
    return {
        "income_statement": {
            "revenue": revenue,
            "operating_income": operating_income,
            "ebit": operating_income,
            "net_income": net_income,
            "gross_profit": gross_profit,
            "_meta": {
                "revenue": _meta("revenue", rev_label, periods[: len(revenue)]),
                "operating_income": _meta("operating_income", op_label, periods[: len(operating_income)]),
                "ebit": {**_meta("operating_income", op_label, periods[: len(operating_income)]), "note": "alias of operating_income"},
                "net_income": _meta("net_income", ni_label, periods[: len(net_income)]),
                "gross_profit": _meta("gross_profit", gp_label, periods[: len(gross_profit)]),
            },
        },
        "cash_flow": {
            "operating_cash_flow": ocf,
            "capex": capex,
            "fcf": fcf,
            "depreciation_amortization": depreciation_amortization,
            "stock_based_compensation": stock_based_compensation,
            "_meta": {
                "operating_cash_flow": _meta("operating_cash_flow", ocf_label, periods[: len(ocf)]),
                "capex": {**_meta("capex", capex_label, periods[: len(capex)]), "note": "absolute value"},
                "fcf": _meta("free_cash_flow", fcf_label, periods[: len(fcf)]),
                "depreciation_amortization": _meta("depreciation_amortization", da_label, periods[: len(depreciation_amortization)]),
                "stock_based_compensation": _meta("stock_based_compensation", sbc_label, periods[: len(stock_based_compensation)]),
            },
        },
        "balance_sheet": {
            "long_term_debt": long_term_debt,
            "short_term_debt": short_term_debt,
            "total_debt": total_debt,
            "cash": cash,
            "total_stockholders_equity": total_stockholders_equity,
            "intangible_assets": intangible_assets,
            "goodwill": goodwill,
            "_meta": {
                "long_term_debt": _meta("long_term_debt", ltd_label, periods[: len(long_term_debt)]),
                "short_term_debt": _meta("short_term_debt", std_label, periods[: len(short_term_debt)]),
                "total_debt": (
                    _meta("total_debt", td_label, periods[: len(total_debt)])
                    if total_debt_raw
                    else {
                        "source_label": None,
                        "derivation": "long_term_debt + short_term_debt",
                        "components": {"long_term_debt": ltd_label, "short_term_debt": std_label},
                    }
                ),
                "cash": _meta("cash_and_equivalents", cash_label, periods[: len(cash)]),
                "total_stockholders_equity": _meta("total_stockholders_equity", eq_label, periods[: len(total_stockholders_equity)]),
                "intangible_assets": _meta("intangible_assets", intang_label, periods[: len(intangible_assets)]),
                "goodwill": _meta("goodwill", gw_label, periods[: len(goodwill)]),
            },
        },
    }
```

- [ ] **Step 3: Lint quick-check**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run python -c "import ast; ast.parse(open('investing-toolkit/skills/data-jp/scripts/pack.py').read())"`
Expected: no output.

- [ ] **Step 4: Run offline test suite — verify no regression**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: same baseline (356 passed / 27 skipped / 35 deselected, post-#239). The fixture has not been updated yet; existing JP tests assert old shape but should not fail because `additionalProperties: true` permits new keys, and existing assertions index specific old keys (still present).

If anything newly fails, STOP and report.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/data-jp/scripts/pack.py
git commit -m "$(cat <<'EOF'
feat(data-jp): emit 6 new raw fields in Tier 2 canonical blocks (v2.2.0-l-jp)

income_statement.gross_profit; cash_flow.depreciation_amortization +
stock_based_compensation; balance_sheet.total_stockholders_equity +
intangible_assets + goodwill. Each gets per-concept _meta entry mirroring
existing JP _meta convention (source_label + source_labels_tried +
fiscal_year_ends + accounting_standard + unit + tier).

JP-specific note: SBC + standalone goodwill expected as [] for many
issuers (yfinance doesn't surface these consistently for JP);
graceful empty-array handling per US AAPL goodwill precedent.
EOF
)"
```

---

### Task 3: Extend `KEY_CONCEPTS` in edinet_client.py (Tier A future-prep)

**Files:**
- Modify: `investing-toolkit/skills/data-jp/scripts/edinet_client.py:95-158`

- [ ] **Step 1: Read current KEY_CONCEPTS**

Confirm current dict has 13 fields (revenue, operating_income, ordinary_income, net_income, total_assets, net_assets, cash_and_equivalents, eps, bps, operating_cash_flow, investing_cash_flow, financing_cash_flow, employees).

- [ ] **Step 2: Extend dict in place**

Open `edinet_client.py` and locate the `KEY_CONCEPTS` dict (starts ~line 95). Add 6 new entries at the end of the dict (preserving existing ordering). Use exact concept-name strings:

```python
    "gross_profit": [
        "GrossProfitLossSummaryOfBusinessResults",
        "GrossProfitLossIFRSSummaryOfBusinessResults",
        "GrossProfit",
    ],
    "depreciation_amortization": [
        "DepreciationAndAmortizationOpeCFCashFlowStatement",
        "DepreciationDepletionAndAmortizationCashFlowStatement",
        "DepreciationAndAmortizationCashFlowStatement",
    ],
    "stock_based_compensation": [
        "ShareBasedCompensationExpense",
        "EmployeeStockOptionExpense",
        "ShareBasedPaymentArrangements",
    ],
    "total_stockholders_equity": [
        "StockholdersEquityAttributableToParentCompanySummaryOfBusinessResults",
        "EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults",
        "StockholdersEquity",
    ],
    "intangible_assets": [
        "IntangibleAssetsNetExcludingGoodwillSummaryOfBusinessResults",
        "OtherIntangibleAssetsNetIFRSSummaryOfBusinessResults",
        "IntangibleAssets",
    ],
    "goodwill": [
        "GoodwillSummaryOfBusinessResults",
        "GoodwillIFRSSummaryOfBusinessResults",
        "Goodwill",
    ],
```

(Preserve existing 13 entries unchanged. Add as bullets at end of the dict literal.)

- [ ] **Step 3: Lint quick-check**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run python -c "import ast; ast.parse(open('investing-toolkit/skills/data-jp/scripts/edinet_client.py').read())"`
Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/skills/data-jp/scripts/edinet_client.py
git commit -m "$(cat <<'EOF'
feat(data-jp): extend KEY_CONCEPTS with 6 EDINET XBRL fallback chains (v2.2.0-l-jp)

Mirrors yfinance Tier 2 surface added in the previous commit. Concepts
use jpcrp/jppfs taxonomy (NOT us-gaap):
- GrossProfitLossSummaryOfBusinessResults / IFRS / fallback
- DepreciationAndAmortizationOpeCFCashFlowStatement / IFRS / fallback
- ShareBasedCompensationExpense / EmployeeStockOptionExpense / IFRS
- StockholdersEquityAttributableToParentCompany... (excludes minority
  interest deliberately — JP-GAAP "純資産" includes minority)
- IntangibleAssetsNetExcludingGoodwill... (excludes goodwill)
- Goodwill (のれん)

Tier A raw extraction picks these up automatically via _extract_key_metrics
substring matching once a filing is downloaded — no new network calls.
Tier A canonical block routing (full _normalize_edinet equivalent of US
_normalize_dcf) deferred to separate future PR.
EOF
)"
```

---

### Task 4: Update memo-fetch schema descriptions

**Files:**
- Modify: `investing-toolkit/skills/data-jp/references/schema-memo-fetch.json`

- [ ] **Step 1: Locate the 3 description strings**

Use Read tool. Find the `income_statement` / `cash_flow` / `balance_sheet` properties (each has `{type: "object", description: "...", additionalProperties: true}` shape). Note the exact existing description text — it likely already mentions JP-specific structure (Tier 2 vs Tier A).

- [ ] **Step 2: Update each description**

Use Edit tool to update each description string. Append (do not replace) "v2.2.0-l-jp" mentions of the new fields to each description. Example edits (adapt to match existing wording style):

For `income_statement.description`, ensure it mentions: `revenue / operating_income / ebit / net_income / gross_profit`.

For `cash_flow.description`, ensure it mentions: `operating_cash_flow / capex / fcf / depreciation_amortization / stock_based_compensation`.

For `balance_sheet.description`, ensure it mentions: `long_term_debt / short_term_debt / total_debt / cash / total_stockholders_equity / intangible_assets / goodwill`.

If existing descriptions follow a particular sentence structure (e.g. mention "Tier 2 — yfinance scrape" tier annotation), preserve that and append the new field names.

- [ ] **Step 3: Validate JSON**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run python -c "import json; json.load(open('investing-toolkit/skills/data-jp/references/schema-memo-fetch.json'))"`
Expected: no output.

- [ ] **Step 4: Run schema sanity test**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest investing-toolkit/tests/data/test_pack_schemas.py -q -m "not network"`
Expected: same pass count as before.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/data-jp/references/schema-memo-fetch.json
git commit -m "$(cat <<'EOF'
docs(data-jp): document new memo-fetch canonical fields in schema (v2.2.0-l-jp)

Description-only update — additionalProperties:true already permits
the new keys. Tells consumers (cross-country compute mode, future
v2.2.0-c sector multiples) what to expect on JP packs.
EOF
)"
```

---

### Task 5: Regenerate Tier 2 fixture (Toyota 7203) with new fields

**Files:**
- Modify: `investing-toolkit/tests/data/fixtures/data-jp-memo-fetch-sample.json`

- [ ] **Step 1: Regenerate via live yfinance pull**

Toyota 7203 is the existing fixture ticker. Regenerate the fixture in place using the actual `pack.py` (which now emits the 6 new fields per Tasks 1+2):

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 INVESTING_TOOLKIT_CACHE=/tmp/v2.2.0-l-jp-cache uv run investing-toolkit/skills/data-jp/scripts/pack.py --ticker 7203 --pack memo-fetch > /tmp/jp-fixture-new.json`

Expected: success exit, JSON written to /tmp.

(Note: this is a Tier 2 path because no `EDINET_API_KEY` is set — Tier A path requires the key and would fail / fallback. The test suite is designed for Tier 2 fixtures.)

- [ ] **Step 2: Sanity-check the new fixture**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run python -c "
import json
d = json.load(open('/tmp/jp-fixture-new.json'))
inc = d['income_statement']
cf = d['cash_flow']
bs = d['balance_sheet']
# Toyota FY2025 yfinance: gross_profit ~9.58T; D&A ~2.25T; equity ~35.92T
assert 'gross_profit' in inc, 'income_statement missing gross_profit'
assert inc['gross_profit'] and inc['gross_profit'][0] > 1_000_000_000_000, f'gross_profit suspicious: {inc[\"gross_profit\"]}'
assert 'depreciation_amortization' in cf, 'cash_flow missing depreciation_amortization'
assert cf['depreciation_amortization'] and cf['depreciation_amortization'][0] > 100_000_000_000, f'D&A suspicious'
assert 'stock_based_compensation' in cf  # may be []
assert 'total_stockholders_equity' in bs, 'balance_sheet missing total_stockholders_equity'
assert bs['total_stockholders_equity'] and bs['total_stockholders_equity'][0] > 1_000_000_000_000, f'equity suspicious'
assert 'intangible_assets' in bs  # may be partial
assert 'goodwill' in bs  # may be []
print('fixture OK; sbc:', len(cf['stock_based_compensation']), 'goodwill:', len(bs['goodwill']))
"`
Expected: `fixture OK; sbc: 0 goodwill: 0` (or non-zero counts if yfinance happens to surface them — both acceptable).

- [ ] **Step 3: Move fixture into place**

Run: `cp /tmp/jp-fixture-new.json /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp/investing-toolkit/tests/data/fixtures/data-jp-memo-fetch-sample.json`

- [ ] **Step 4: Run offline test suite**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: same baseline (356 passed / 27 skipped / 35 deselected). New fields are additive — no test should newly fail.

If anything newly fails, INVESTIGATE — likely a cross-layer drift guard (similar to `test_slim_memo_fetch_fixture_is_production_subset` from US v2.2.0-l). Report findings; may need a small follow-up edit.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/tests/data/fixtures/data-jp-memo-fetch-sample.json
git commit -m "$(cat <<'EOF'
test(data-jp): regenerate Toyota 7203 fixture with v2.2.0-l-jp canonical fields

Live yfinance pull (Tier 2 path; no EDINET key required for fixture
generation). Toyota FY2025 (year ending 2025-03-31) values:
  gross_profit                    ~9.58T JPY
  depreciation_amortization       ~2.25T JPY
  total_stockholders_equity       ~35.92T JPY
  intangible_assets (combined)    ~1.36T JPY
  stock_based_compensation        []  (Toyota does not disclose to yfinance)
  goodwill                        []  (yfinance combines into intangibles)

Empty arrays for SBC + standalone goodwill mirror US AAPL goodwill /
intangibles precedent — the canonical upstream signal that the issuer
does not separately tag the field, NOT a parser bug.
EOF
)"
```

---

### Task 6: Add network test asserting Tier 2 surfaces new fields

**Files:**
- Modify: `investing-toolkit/tests/data/test_data_jp.py`

- [ ] **Step 1: Locate insertion point**

Read the existing JP tests. Find the existing memo-fetch network test (likely `test_jp_memo_fetch_*` named function with `@pytest.mark.network` decorator). Insert the new test immediately after it.

- [ ] **Step 2: Add the new network test**

Replace `TICKER` / `_run_pack` references with whatever the existing convention is in the file (mirror the surrounding tests — likely `JP_TICKER = "7203"` or similar at top of file, plus a `_run_pack(args)` helper).

```python
@pytest.mark.network
def test_jp_memo_fetch_toyota_has_extended_canonical_fields():
    """v2.2.0-l-jp: Tier 2 (yfinance) memo-fetch should surface 6 new canonical fields.

    Toyota 7203 coverage:
      - income_statement.gross_profit            (Gross Profit; yfinance)       — populated
      - cash_flow.depreciation_amortization      (Depreciation And Amortization) — populated
      - cash_flow.stock_based_compensation       (Stock Based Compensation)      — empty array OK (Toyota does not disclose)
      - balance_sheet.total_stockholders_equity  (Stockholders Equity)           — populated
      - balance_sheet.intangible_assets          (Other Intangible Assets)       — populated (combined w/ goodwill in yfinance)
      - balance_sheet.goodwill                   (Goodwill)                      — empty array OK (yfinance combines into intangibles for JP)
    """
    out = _run_pack(["--ticker", "7203", "--pack", "memo-fetch"])

    inc = out["income_statement"]
    cf = out["cash_flow"]
    bs = out["balance_sheet"]

    # Income statement: gross_profit must populate (Toyota FY2025 ~¥9.58T)
    assert "gross_profit" in inc, "income_statement missing gross_profit (v2.2.0-l-jp)"
    assert isinstance(inc["gross_profit"], list) and inc["gross_profit"], (
        "Toyota gross_profit array empty — yfinance Gross Profit label fallback failed"
    )
    assert inc["gross_profit"][0] > 1_000_000_000_000, (
        f"Toyota FY[0] gross_profit suspiciously small: {inc['gross_profit'][0]}"
    )

    # Cash flow: D&A must populate (Toyota FY2025 ~¥2.25T)
    assert "depreciation_amortization" in cf, "cash_flow missing depreciation_amortization (v2.2.0-l-jp)"
    assert isinstance(cf["depreciation_amortization"], list) and cf["depreciation_amortization"], (
        "Toyota D&A array empty — yfinance Depreciation And Amortization label fallback failed"
    )
    assert cf["depreciation_amortization"][0] > 100_000_000_000, (
        f"Toyota FY[0] D&A suspiciously small: {cf['depreciation_amortization'][0]}"
    )

    # Cash flow: SBC presence required, empty list OK (Toyota does not disclose)
    assert "stock_based_compensation" in cf, "cash_flow missing stock_based_compensation (v2.2.0-l-jp)"
    assert isinstance(cf["stock_based_compensation"], list)

    # Balance sheet: equity must populate (Toyota FY2025 ~¥35.92T)
    assert "total_stockholders_equity" in bs, "balance_sheet missing total_stockholders_equity (v2.2.0-l-jp)"
    assert isinstance(bs["total_stockholders_equity"], list) and bs["total_stockholders_equity"], (
        "Toyota total_stockholders_equity array empty — yfinance Stockholders Equity label fallback failed"
    )
    assert bs["total_stockholders_equity"][0] > 1_000_000_000_000, (
        f"Toyota FY[0] equity suspiciously small: {bs['total_stockholders_equity'][0]}"
    )

    # Intangibles + goodwill: presence required, empty list OK (yfinance combines for JP)
    assert "intangible_assets" in bs, "balance_sheet missing intangible_assets (v2.2.0-l-jp)"
    assert "goodwill" in bs, "balance_sheet missing goodwill (v2.2.0-l-jp)"
    assert isinstance(bs["intangible_assets"], list)
    assert isinstance(bs["goodwill"], list)

    # _meta presence for newly-added populated fields (whichever populate)
    inc_meta = inc.get("_meta", {})
    cf_meta = cf.get("_meta", {})
    bs_meta = bs.get("_meta", {})
    assert "gross_profit" in inc_meta
    assert "depreciation_amortization" in cf_meta
    assert "stock_based_compensation" in cf_meta
    assert "total_stockholders_equity" in bs_meta
    assert "intangible_assets" in bs_meta
    assert "goodwill" in bs_meta
```

- [ ] **Step 3: Run the new network test**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 INVESTING_TOOLKIT_CACHE=/tmp/v2.2.0-l-jp-cache uv run --with pytest pytest investing-toolkit/tests/data/test_data_jp.py::test_jp_memo_fetch_toyota_has_extended_canonical_fields -v -m network`
Expected: PASS (live yfinance call; ~30-60s).

- [ ] **Step 4: Confirm offline suite still skips this test by mark**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q | tail -3`
Expected: deselected count up by 1 (35 → 36).

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/tests/data/test_data_jp.py
git commit -m "$(cat <<'EOF'
test(data-jp): assert v2.2.0-l-jp canonical fields in live memo-fetch (network)

Tier-2 yfinance live-pull guard for the 6 new canonical fields.
Toyota 7203 FY2025 thresholds: ~1T JPY for gross_profit / equity,
~100B JPY for D&A. SBC + standalone goodwill tested for key-presence
only (Toyota does not disclose SBC to yfinance, and yfinance combines
goodwill into "Other Intangible Assets" for JP issuers — both are
canonical upstream signals, not bugs).
EOF
)"
```

---

### Task 7: Update ROADMAP

**Files:**
- Modify: `investing-toolkit/ROADMAP.md`

- [ ] **Step 1: Read current ROADMAP**

Find the "Spawned from v2.2.0-l closure" subsection (added by v2.2.0-l US PR #239 closure) which lists `v2.2.0-l-{jp,tw,kr,cn}` as a single bullet.

- [ ] **Step 2: Move JP entry to closed**

Add a closed-style entry for `v2.2.0-l-jp` immediately after the existing `### ~~v2.2.0-l~~ ✅ closed 2026-05-04 (PR #239)` section. Use this content:

```markdown
### ~~v2.2.0-l-jp — JP cross-country symmetry~~ ✅ closed 2026-05-04 (PR #TBD <!-- TODO Task 8: backfill actual PR# after gh pr create -->)

- ✅ **v2.2.0-l-jp** Tier 2 yfinance + Tier A KEY_CONCEPTS extension (PR #TBD <!-- TODO Task 8: backfill actual PR# after gh pr create -->) — Extended `data-jp/scripts/pack.py` `_YF_LABEL_MAP_JP` with 6 new yfinance label fallback chains; wired into `_build_canonical_from_yf_financials_jp()` to emit in 3 canonical blocks (gross_profit / depreciation_amortization / stock_based_compensation / total_stockholders_equity / intangible_assets / goodwill). Same fields added to `data-jp/scripts/edinet_client.py` `KEY_CONCEPTS` with EDINET XBRL fallback chains (jpcrp / jppfs / fallback) for Tier A raw extraction (no new network calls — concepts ride existing full-filing download). Toyota 7203 fixture regenerated via live yfinance: gross_profit ~¥9.58T, D&A ~¥2.25T, equity ~¥35.92T populated; SBC + standalone goodwill `[]` (Toyota does not disclose SBC to yfinance; yfinance combines goodwill into "Other Intangible Assets" for JP issuers — both canonical upstream signals per US AAPL goodwill precedent). Network smoke test `test_jp_memo_fetch_toyota_has_extended_canonical_fields` added. **Tier A canonical block routing** (full `_normalize_edinet` equivalent of US `_normalize_dcf` for EDINET full-filing CSV parsing) **deferred to separate future PR** — current Tier A path emits placeholder blocks. Cross-country compute-mode end-to-end testing (would require new JP peer fixtures + cross-currency normalization design) deferred to separate follow-up.
```

- [ ] **Step 3: Update the "Spawned from v2.2.0-l closure" line**

Find the existing line under v2.2.0-l closure subsection that says something like:
> **v2.2.0-l-{jp,tw,kr,cn}** Cross-country symmetry — extend new raw fields to JP EDINET, TW MOPS, KR fdr/DART, CN akshare per existing per-country pack patterns.

Update to mark JP as done:
> **v2.2.0-l-{tw,kr,cn}** Cross-country symmetry — extend new raw fields to TW MOPS, KR fdr/DART, CN akshare per existing per-country pack patterns. **JP closed 2026-05-04 (PR #TBD <!-- TODO Task 8: backfill actual PR# after gh pr create -->)** — see entry below.

- [ ] **Step 4: Update "Recommended next-pickup priority" list**

Find the list. Update the JP-related item (currently item #3 "v2.2.0-l-{jp,tw,kr,cn}") to:

```markdown
3. **v2.2.0-l-{tw,kr,cn}** Cross-country symmetry remainder — TW MOPS / KR fdr+DART / CN akshare. JP closed 2026-05-04. Each remaining country needs fresh design pass against its native taxonomy.
```

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/ROADMAP.md
git commit -m "$(cat <<'EOF'
docs(roadmap): close v2.2.0-l-jp; remaining cross-country list updated

JP cross-country symmetry shipped (Tier 2 yfinance + Tier A KEY_CONCEPTS
extension; Tier A canonical block routing deferred). Updates:
- New closed entry for v2.2.0-l-jp with closure summary
- Spawned-cross-country-list updated: {jp,tw,kr,cn} → {tw,kr,cn}
- Recommended-priority list updated to reflect JP done
EOF
)"
```

---

### Task 8: Final verification + push + PR

**Files:** none (operations only)

- [ ] **Step 1: Run full offline suite — final green check**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: same baseline (356 passed / 27 skipped / 36 deselected — the +1 is the new JP network test).

- [ ] **Step 2: Run network test once locally**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && PYTHONDONTWRITEBYTECODE=1 INVESTING_TOOLKIT_CACHE=/tmp/v2.2.0-l-jp-cache uv run --with pytest pytest investing-toolkit/tests/data/test_data_jp.py::test_jp_memo_fetch_toyota_has_extended_canonical_fields -v -m network`
Expected: PASS.

- [ ] **Step 3: Verify Conventional Commits**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp && git log main..HEAD --oneline`
Expected: 7 commits, each matching `^(feat|fix|chore|docs|refactor|test)\(([a-z][a-z0-9-]*)\): .+$`. Scopes should be `data-jp` / `roadmap`.

- [ ] **Step 4: Push branch + open PR**

Run:
```bash
cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp
git push -u origin feat/v2.2.0-l-jp-memo-fetch-raw-fields
gh pr create --title "feat(investing-toolkit): v2.2.0-l-jp JP cross-country symmetry" --body "$(cat <<'EOF'
## Summary

- Extends `data-jp/scripts/pack.py` `_YF_LABEL_MAP_JP` with 6 new yfinance label fallback chains; wired into `_build_canonical_from_yf_financials_jp()` to emit in 3 canonical blocks (`gross_profit`, `depreciation_amortization`, `stock_based_compensation`, `total_stockholders_equity`, `intangible_assets`, `goodwill`).
- Same 6 fields added to `data-jp/scripts/edinet_client.py` `KEY_CONCEPTS` with EDINET XBRL fallback chains (jpcrp / jppfs / fallback). No new network calls — concepts ride existing full-filing download.
- Toyota 7203 fixture regenerated via live yfinance pull. SBC + standalone goodwill `[]` per US AAPL goodwill precedent (Toyota does not disclose SBC to yfinance; yfinance combines goodwill into "Other Intangible Assets" for JP issuers).
- Network smoke test `test_jp_memo_fetch_toyota_has_extended_canonical_fields` added.

## Test plan

- [x] Offline suite: `PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q` → 356 passed / 27 skipped / 36 deselected / 0 failed
- [x] Network smoke (live yfinance for 7203): `pytest test_jp_memo_fetch_toyota_has_extended_canonical_fields -v -m network` → PASS
- [x] Conventional Commits: 7 commits, all match `feat|test|docs(<kebab-scope>): <subject>`

## What's NOT in this PR (deferred)

- **Tier A (EDINET) canonical block routing** — current Tier A path emits placeholder blocks; full `_normalize_edinet` equivalent of US `_normalize_dcf` deferred to separate future PR. KEY_CONCEPTS extension in this PR is future-prep.
- **JP analysis-comps cross-country compute mode** — would require new JP peer fixtures (Honda 7267 / Nissan 7201) + cross-currency normalization design. Separate follow-up.
- **TW / KR / CN cross-country symmetry** — `v2.2.0-l-{tw,kr,cn}` follow-up per-country PRs (each needs fresh design pass against its native taxonomy).

## References

- ROADMAP §v2.2.0-l-jp (closed in this PR; entry added under §v2.2.0-l-jp)
- US PR #239 (v2.2.0-l) — the precedent this PR mirrors for JP

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 5: Backfill PR# in ROADMAP**

After PR is created and number known, backfill all `PR #TBD` markers (4 occurrences):

```bash
cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l-jp
# Replace 4 occurrences (use the actual PR number from gh pr create output)
sed -i '' "s/PR #TBD <!-- TODO Task 8: backfill actual PR# after gh pr create -->/PR #<NUM>/g" investing-toolkit/ROADMAP.md
git add investing-toolkit/ROADMAP.md
git commit -m "docs(roadmap): backfill PR number for v2.2.0-l-jp"
git push
```

- [ ] **Step 6: Wait for CI + monitor**

Run `gh pr checks <pr-number> --watch` until all 5+ required checks pass.

---

## Self-Review

**1. Spec coverage** (against investigation report findings):

- ✅ Tier 2 yfinance extension → Tasks 1+2
- ✅ Tier A KEY_CONCEPTS extension → Task 3
- ✅ Schema doc update → Task 4
- ✅ Toyota fixture regen → Task 5
- ✅ Network test → Task 6
- ✅ ROADMAP update → Task 7
- ✅ Out-of-scope items explicitly documented (Tier A canonical block routing; cross-country compute-mode tests; TW/KR/CN follow-ups)

**2. Placeholder scan**: No "TBD" / "implement later" / "similar to Task N". `PR #TBD` markers in Task 7 are explicitly documented as "backfill in Task 8" — same pattern that worked in v2.2.0-l US.

**3. Type consistency**:
- Variable names in Task 2 (`gp_label`, `da_label`, `sbc_label`, `eq_label`, `intang_label`, `gw_label`) are unique within `_build_canonical_from_yf_financials_jp` scope.
- KEY_CONCEPTS in Task 3 uses identical canonical field names as Tier 2 — unifies cross-tier vocabulary.
- Network test in Task 6 references the canonical names verbatim.

**4. Sequencing**: Each task ends commit-clean. Tasks 1-3 are pure additions (no behavior change for existing tests since fixture not yet updated; Tier A KEY_CONCEPTS extension is silently future-prep). Task 4 doc-only. Task 5 (fixture regen) introduces the new fields into the existing fixture. Task 6 adds a deselected-by-default network test (no offline impact). Task 7 docs. Task 8 ship.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-04-investing-toolkit-v2.2.0-l-jp-memo-fetch-raw-fields.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Per `feedback_subagent_driven_development_validated.md`, this pattern caught 5 real drift items on US v2.2.0-l (PR #239) that monolithic implementation would have missed.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints for review.

**Which approach?**
