# investing-toolkit v2.2.0-l — memo-fetch raw-field extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend SEC EDGAR XBRL extraction in `data-us` to surface 6 additional canonical fields, which auto-flips `analysis-comps --mode compute` `priceToBook` + `evEbitda` from null → computed without changing analysis-comps logic shape.

**Architecture:** Three-layer touch — (1) `data-us/scripts/pack.py` `DCF_CONCEPT_MAPPING` extended with 6 new chains routed into `_normalize_dcf()` output blocks (income_statement / cash_flow / balance_sheet); (2) `analysis-comps/scripts/comps_compute.py` removes `priceToBook` + `evEbitda` from `DEFERRED_MULTIPLES` and adds compute formulas using newly-available `total_stockholders_equity` + `depreciation_amortization`; (3) test fixture + regression assertions flip from "is None + v2.2.0-l note" to `pytest.approx(value)`. No new XBRL API calls beyond the existing companyfacts fan-out — concepts are fetched via the same `sec_edgar_client.py --action facts --concept <name>` mechanism already wired through `_fetch_dcf_concepts()`.

**Tech Stack:** Python 3.11, `uv run` (PEP 723), pytest, SEC EDGAR XBRL companyfacts API, JSON Schema draft-07.

**Reference:**
- ROADMAP §v2.2.0-l (`investing-toolkit/ROADMAP.md:189-196`)
- v2.2.0-b design doc §7.3 + §15.2 (`docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md`)
- ADR-0003 (canonical T3 staging + concept fallback chain pattern)
- v2.2.0-b PR #227 (the closure that explicitly deferred priceToBook + evEbitda to v2.2.0-l)

**Scope:**
- US-only first PR (this plan).
- Cross-country symmetry to JP / TW / KR / CN follows in **separate per-country PRs** after this lands. Out of scope.
- v2.2.0-c sector-adjusted multiples (Tech Rule-of-40 needs SBC; REIT P/AFFO needs D&A; Bank P/B needs equity) becomes unblocked but is a separate PR.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `investing-toolkit/skills/data-us/scripts/pack.py` | Modify | Extend `DCF_CONCEPT_MAPPING` with 6 new fields; update `_normalize_dcf()` to emit them in income_statement / cash_flow / balance_sheet blocks |
| `investing-toolkit/skills/data-us/references/schema-memo-fetch.json` | Modify | Update `income_statement` / `cash_flow` / `balance_sheet` description strings to mention new fields (no shape change — `additionalProperties: true` already permissive) |
| `investing-toolkit/tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json` | Modify | Add `cash_flow` block + extend `income_statement` (gross_profit) and `balance_sheet` (total_stockholders_equity, intangible_assets, goodwill) using AAPL FY2025 10-K values |
| `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py` | Modify | Remove `priceToBook` + `evEbitda` from `DEFERRED_MULTIPLES`; add compute logic + provenance for both |
| `investing-toolkit/tests/analysis/test_analysis_comps.py` | Modify | Flip 2 deferred-emit-null tests → 2 recompute tests with `pytest.approx`; extend `test_compute_provenance_includes_fiscal_year_end` loop; collapse `test_divergence_alert_n_a_for_deferred` |
| `investing-toolkit/tests/data/test_data_us.py` | Modify | Add network test `test_us_memo_fetch_aapl_has_extended_canonical_fields` asserting new fields populated for live AAPL pull |
| `investing-toolkit/ROADMAP.md` | Modify | Move v2.2.0-l from "Open" to a new "Closed 2026-05-04" entry; cross-link v2.2.0-c unblock + v2.2.0-l-{jp,tw,kr,cn} follow-ups |

---

## XBRL Concept Mapping Reference

For each new canonical field, fallback chain ordered by issuer-coverage (first non-empty wins). Established by reading SEC XBRL taxonomy (us-gaap 2024) + checking against AAPL / MSFT / GOOGL / META actual 10-K disclosures via `sec_edgar_client.py --action facts --ticker AAPL` (us_gaap_concepts list).

| Canonical field | Block | XBRL fallback chain |
|---|---|---|
| `total_stockholders_equity` | balance_sheet | `StockholdersEquity` → `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` |
| `depreciation_amortization` | cash_flow | `DepreciationDepletionAndAmortization` → `DepreciationAndAmortization` → `Depreciation` |
| `stock_based_compensation` | cash_flow | `ShareBasedCompensation` → `AllocatedShareBasedCompensationExpense` |
| `gross_profit` | income_statement | `GrossProfit` |
| `intangible_assets` | balance_sheet | `IntangibleAssetsNetExcludingGoodwill` → `FiniteLivedIntangibleAssetsNet` → `IntangibleAssetsNet` |
| `goodwill` | balance_sheet | `Goodwill` |

**Note on AAPL coverage:** Apple's 10-K FY2025 reports goodwill = $0 and intangible_assets = $0 (immaterial — disclosed in MD&A as "not significant"). Test assertions tolerate `[]` (empty array — no observation in any chain entry) for these two on AAPL specifically; richer coverage shows up on MSFT / GOOGL fixtures (out of scope for this PR).

---

## Compute Formulas

Both new formulas use **FY-trailing** convention (consistent with `trailingPE` + `priceToSales` already in v2.2.0-b). Numerators come from `company_info` (yfinance market data); denominators come from XBRL FY[0] (newly-extended canonical block).

```
priceToBook (FY) = market_cap / total_stockholders_equity[0]
                 = company_info.marketCap / balance_sheet.total_stockholders_equity[0]

evEbitda (FY)    = enterprise_value / ebitda
                 = (market_cap + total_debt[0] - cash[0]) / (operating_income[0] + depreciation_amortization[0])
```

Where:
- `enterprise_value = market_cap + total_debt - cash` (FY-trailing balance sheet items already in v2.2.0-b).
- `ebitda = EBIT + D&A`. EBIT alias = `operating_income`. D&A is the new field.
- Provenance records both numerator + denominator sources, fiscal_year_end (from `_meta.total_stockholders_equity` / `_meta.depreciation_amortization`), and the FY-trailing-not-TTM warning.

**AAPL FY2025 expected values** (year ending 2025-09-27, derived from AAPL 10-K filed 2025-10-31, cited in fixture provenance):

```
total_stockholders_equity  = 66,790,000,000
depreciation_amortization  = 11,445,000,000
stock_based_compensation   = 11,690,000,000
gross_profit               = 184,103,000,000
goodwill                   = 0   (immaterial)
intangible_assets          = 0   (immaterial)

market_cap                 = 4,109,006,274,560  (existing fixture)
total_debt[0]              = 90,678,000,000     (existing fixture)
cash[0]                    = 35,934,000,000     (existing fixture)
operating_income[0]        = 133,050,000,000    (existing fixture)

priceToBook (compute)      = 4109006274560 / 66790000000  ≈ 61.5212
evEbitda (compute)         = (4109006274560 + 90678000000 - 35934000000) / (133050000000 + 11445000000)
                           = 4163750274560 / 144495000000  ≈ 28.8160
```

Note the wide divergence vs direct (priceToBook fixture = 35.4 → compute ≈ 61.5 → pct_diff ≈ +73.7% → high alert; evEbitda fixture = 21.3 → compute ≈ 28.8 → pct_diff ≈ +35.2% → high alert). High alerts are expected and informative for FY-trailing vs TTM-LTM convention difference + Apple's heavily-buyback-shrunken book equity. Asserted in tests.

---

## Tasks

### Task 1: Extend `DCF_CONCEPT_MAPPING` with 6 new canonical fields

**Files:**
- Modify: `investing-toolkit/skills/data-us/scripts/pack.py:97-130`

- [ ] **Step 1: Read current mapping**

Confirm current `DCF_CONCEPT_MAPPING` has 8 fields (revenue / operating_income / net_income / operating_cash_flow / capex / long_term_debt / short_term_debt / cash_and_equivalents).

- [ ] **Step 2: Extend mapping in place**

Replace the existing dict literal (lines 97-130) with the extended version. Add the 6 new entries at the bottom of the dict in the order: `gross_profit` (income), `depreciation_amortization` + `stock_based_compensation` (cash flow), `total_stockholders_equity` + `intangible_assets` + `goodwill` (balance sheet) — grouped to match the eventual block routing in `_normalize_dcf`.

```python
DCF_CONCEPT_MAPPING: dict[str, list[str]] = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenue",
        "SalesRevenueNet",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
    "depreciation_amortization": [
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
        "Depreciation",
    ],
    "stock_based_compensation": [
        "ShareBasedCompensation",
        "AllocatedShareBasedCompensationExpense",
    ],
    "long_term_debt": [
        "LongTermDebt",
        "LongTermDebtNoncurrent",
    ],
    "short_term_debt": [
        "DebtCurrent",
        "ShortTermBorrowings",
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
        "Cash",
    ],
    "total_stockholders_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "intangible_assets": [
        "IntangibleAssetsNetExcludingGoodwill",
        "FiniteLivedIntangibleAssetsNet",
        "IntangibleAssetsNet",
    ],
    "goodwill": [
        "Goodwill",
    ],
}
```

- [ ] **Step 3: Lint quick-check**

Run: `uv run python -c "import ast; ast.parse(open('investing-toolkit/skills/data-us/scripts/pack.py').read())"`
Expected: no output (clean parse).

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/skills/data-us/scripts/pack.py
git commit -m "$(cat <<'EOF'
feat(data-us): extend DCF_CONCEPT_MAPPING with 6 raw fields (v2.2.0-l)

Adds XBRL fallback chains for: gross_profit, depreciation_amortization,
stock_based_compensation, total_stockholders_equity, intangible_assets,
goodwill. _normalize_dcf wiring + emission in next commit.

Reference: ROADMAP §v2.2.0-l; v2.2.0-b design doc §7.3 + §15.2.
EOF
)"
```

---

### Task 2: Wire new fields into `_normalize_dcf()` output blocks

**Files:**
- Modify: `investing-toolkit/skills/data-us/scripts/pack.py:307-477` (`_normalize_dcf` function)

- [ ] **Step 1: Read current `_normalize_dcf` return shape**

Current return has three blocks (income_statement / cash_flow / balance_sheet); each has data arrays + `_meta` per concept. Extension preserves this shape — adds new array keys + corresponding `_meta` entries.

- [ ] **Step 2: Add `_values()` calls + block assembly**

In the assembly section (currently around lines 405-411 just before the return), add new local variable bindings:

```python
    gross_profit = _values("gross_profit")
    depreciation_amortization = _values("depreciation_amortization")
    stock_based_compensation = _values("stock_based_compensation")
    total_stockholders_equity = _values("total_stockholders_equity")
    intangible_assets = _values("intangible_assets")
    goodwill = _values("goodwill")
```

- [ ] **Step 3: Extend the return dict**

Replace the existing return dict (lines 426-477) so each block adds its new fields + `_meta` entries. Show the full updated return:

```python
    return {
        "income_statement": {
            "revenue": revenue,
            "operating_income": operating_income,
            "ebit": operating_income,  # EBIT alias to operating_income for analysis-dcf
            "net_income": net_income,
            "gross_profit": gross_profit,
            "_meta": {
                "revenue": _meta("revenue"),
                "operating_income": _meta("operating_income"),
                "ebit": {**_meta("operating_income"), "note": "alias of operating_income"},
                "net_income": _meta("net_income"),
                "gross_profit": _meta("gross_profit"),
            },
        },
        "cash_flow": {
            "operating_cash_flow": ocf,
            "capex": capex,
            "fcf": fcf,
            "depreciation_amortization": depreciation_amortization,
            "stock_based_compensation": stock_based_compensation,
            "_meta": {
                "operating_cash_flow": _meta("operating_cash_flow"),
                "capex": _meta("capex"),
                "fcf": {
                    "source_concept": None,
                    "derivation": "operating_cash_flow - capex",
                    "fallback_used": False,
                    "components": {
                        "operating_cash_flow": canonical_source["operating_cash_flow"],
                        "capex": canonical_source["capex"],
                    },
                },
                "depreciation_amortization": _meta("depreciation_amortization"),
                "stock_based_compensation": _meta("stock_based_compensation"),
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
                "long_term_debt": _meta("long_term_debt"),
                "short_term_debt": _meta("short_term_debt"),
                "total_debt": {
                    "source_concept": None,
                    "derivation": "long_term_debt + short_term_debt",
                    "fallback_used": False,
                    "components": {
                        "long_term_debt": canonical_source["long_term_debt"],
                        "short_term_debt": canonical_source["short_term_debt"],
                    },
                },
                "cash": _meta("cash_and_equivalents"),
                "total_stockholders_equity": _meta("total_stockholders_equity"),
                "intangible_assets": _meta("intangible_assets"),
                "goodwill": _meta("goodwill"),
            },
        },
    }
```

- [ ] **Step 4: Re-run lint quick-check**

Run: `uv run python -c "import ast; ast.parse(open('investing-toolkit/skills/data-us/scripts/pack.py').read())"`
Expected: no output.

- [ ] **Step 5: Run offline test suite — confirm no regression**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: Same baseline as main (377 passed / 2 skipped). Compute mode tests still see `is None` for priceToBook + evEbitda because the fixture has not been updated yet.

- [ ] **Step 6: Commit**

```bash
git add investing-toolkit/skills/data-us/scripts/pack.py
git commit -m "$(cat <<'EOF'
feat(data-us): emit 6 new raw fields in memo-fetch canonical blocks (v2.2.0-l)

income_statement.gross_profit; cash_flow.depreciation_amortization +
stock_based_compensation; balance_sheet.total_stockholders_equity +
intangible_assets + goodwill. Each gets per-concept _meta entry mirroring
the v2.2.0-b _meta nesting convention. No new SEC EDGAR network calls —
concepts ride the same _fetch_dcf_concepts fan-out.

Reference: ROADMAP §v2.2.0-l.
EOF
)"
```

---

### Task 3: Update memo-fetch schema descriptions

**Files:**
- Modify: `investing-toolkit/skills/data-us/references/schema-memo-fetch.json:107-121`

- [ ] **Step 1: Update three description strings**

`additionalProperties: true` is already in place — schema doesn't need shape changes, only docstring updates so consumers know what's available. Edit the three description strings to mention new fields:

```json
    "income_statement": {
      "type": "object",
      "description": "T3 canonical income statement (annual, most-recent-first, depth 5). Per ADR-0003. Contains revenue / operating_income / ebit / net_income / gross_profit arrays plus _meta provenance.",
      "additionalProperties": true
    },
    "cash_flow": {
      "type": "object",
      "description": "T3 canonical cash flow statement. Contains operating_cash_flow / capex / fcf (derived = OCF - capex) / depreciation_amortization / stock_based_compensation plus _meta. Per ADR-0003.",
      "additionalProperties": true
    },
    "balance_sheet": {
      "type": "object",
      "description": "T3 canonical balance sheet. Contains long_term_debt / short_term_debt / total_debt (derived = LTD + STD) / cash / total_stockholders_equity / intangible_assets / goodwill plus _meta. Per ADR-0003.",
      "additionalProperties": true
    },
```

- [ ] **Step 2: Validate JSON parses**

Run: `uv run python -c "import json; json.load(open('investing-toolkit/skills/data-us/references/schema-memo-fetch.json'))"`
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/skills/data-us/references/schema-memo-fetch.json
git commit -m "$(cat <<'EOF'
docs(data-us): document new memo-fetch canonical fields in schema (v2.2.0-l)

Description-only update — additionalProperties:true already permits the
new keys. Tells consumers (analysis-comps, future v2.2.0-c sector multiples)
what to expect.
EOF
)"
```

---

### Task 4: Extend AAPL fixture with new canonical fields

**Files:**
- Modify: `investing-toolkit/tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json`

- [ ] **Step 1: Read current fixture**

Confirm current shape: `income_statement` has revenue/net_income/operating_income/ebit + `_meta`; `balance_sheet` has total_debt/cash. No `cash_flow` block (was unused).

- [ ] **Step 2: Replace fixture with extended version**

Hand-edit the JSON to add the new fields. AAPL FY2025 values are public 10-K disclosures (10-K filed 2025-10-31, fiscal year end 2025-09-27); citations in the AAPL 10-K consolidated financial statements. Use `[]` for goodwill + intangible_assets (Apple discloses both as immaterial / $0 — empty observation array is the correct upstream representation).

Replace the entire file content with:

```json
{
  "pack": "memo-fetch",
  "ticker": "AAPL",
  "fetched_at": "2026-05-04T00:00:00.000000+00:00",
  "company_info": {
    "regularMarketPrice": 280.14,
    "sharesOutstanding": 14667688000,
    "marketCap": 4109006274560
  },
  "current_price": 280.14,
  "shares_outstanding": 14667688000,
  "income_statement": {
    "revenue": [416161000000.0, 391035000000.0, 383285000000.0, 394328000000.0, 365817000000.0],
    "net_income": [112010000000.0, 93736000000.0, 96995000000.0, 99803000000.0, 94680000000.0],
    "operating_income": [133050000000.0, 123216000000.0, 114301000000.0, 119437000000.0, 108949000000.0],
    "ebit": [133050000000.0, 123216000000.0, 114301000000.0, 119437000000.0, 108949000000.0],
    "gross_profit": [184103000000.0, 180683000000.0, 169148000000.0, 170782000000.0, 152836000000.0],
    "_meta": {
      "revenue": {
        "fiscal_year_ends": ["2025-09-27", "2024-09-28", "2023-09-30", "2022-09-24", "2021-09-25"],
        "filings_used": [
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2024-11-01",
          "10-K filed 2023-11-03"
        ]
      },
      "net_income": {
        "fiscal_year_ends": ["2025-09-27", "2024-09-28", "2023-09-30", "2022-09-24", "2021-09-25"],
        "filings_used": [
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2024-11-01",
          "10-K filed 2023-11-03"
        ]
      },
      "gross_profit": {
        "fiscal_year_ends": ["2025-09-27", "2024-09-28", "2023-09-30", "2022-09-24", "2021-09-25"],
        "filings_used": [
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2024-11-01",
          "10-K filed 2023-11-03"
        ]
      }
    }
  },
  "cash_flow": {
    "depreciation_amortization": [11445000000.0, 11445000000.0, 11519000000.0, 11104000000.0, 11284000000.0],
    "stock_based_compensation": [11690000000.0, 11688000000.0, 10833000000.0, 9038000000.0, 7906000000.0],
    "_meta": {
      "depreciation_amortization": {
        "fiscal_year_ends": ["2025-09-27", "2024-09-28", "2023-09-30", "2022-09-24", "2021-09-25"],
        "filings_used": [
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2024-11-01",
          "10-K filed 2023-11-03"
        ]
      },
      "stock_based_compensation": {
        "fiscal_year_ends": ["2025-09-27", "2024-09-28", "2023-09-30", "2022-09-24", "2021-09-25"],
        "filings_used": [
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2024-11-01",
          "10-K filed 2023-11-03"
        ]
      }
    }
  },
  "balance_sheet": {
    "total_debt": [90678000000.0, 95300000000.0, 109280000000.0, 120069000000.0, 124719000000.0],
    "cash": [35934000000.0, 29943000000.0, 29965000000.0, 23646000000.0, 34940000000.0],
    "total_stockholders_equity": [66790000000.0, 56950000000.0, 62146000000.0, 50672000000.0, 63090000000.0],
    "intangible_assets": [],
    "goodwill": [],
    "_meta": {
      "total_stockholders_equity": {
        "fiscal_year_ends": ["2025-09-27", "2024-09-28", "2023-09-30", "2022-09-24", "2021-09-25"],
        "filings_used": [
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2025-10-31",
          "10-K filed 2024-11-01",
          "10-K filed 2023-11-03"
        ]
      },
      "intangible_assets": {
        "fiscal_year_ends": [],
        "filings_used": [],
        "note": "AAPL discloses intangible_assets as immaterial; XBRL chain (IntangibleAssetsNetExcludingGoodwill / FiniteLivedIntangibleAssetsNet / IntangibleAssetsNet) returns no observations."
      },
      "goodwill": {
        "fiscal_year_ends": [],
        "filings_used": [],
        "note": "AAPL discloses goodwill = $0; XBRL Goodwill concept not tagged."
      }
    }
  },
  "_provenance": {
    "skill": "data-us",
    "source": "pack.py --pack memo-fetch",
    "tier": "A",
    "fixture_note": "Hand-trimmed for analysis-comps tests. AAPL FY2025 values from 10-K filed 2025-10-31 (fiscal year ended 2025-09-27). v2.2.0-l extension adds gross_profit / cash_flow.* / total_stockholders_equity / intangible_assets / goodwill."
  }
}
```

- [ ] **Step 3: Validate JSON parses**

Run: `uv run python -c "import json; d=json.load(open('investing-toolkit/tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json')); assert d['balance_sheet']['total_stockholders_equity'][0]==66790000000, d['balance_sheet']['total_stockholders_equity']; assert d['cash_flow']['depreciation_amortization'][0]==11445000000, d['cash_flow']['depreciation_amortization']; print('fixture OK')"`
Expected: `fixture OK`.

- [ ] **Step 4: Run offline test suite — confirm tests still pass against unchanged comps_compute (deferred path)**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: Same baseline (377 passed / 2 skipped). The deferred-emit-null tests still pass because `comps_compute.py` still has `priceToBook` + `evEbitda` in `DEFERRED_MULTIPLES` — they're flipped in Tasks 6+7 below.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json
git commit -m "$(cat <<'EOF'
test(analysis-comps): extend AAPL fixture with v2.2.0-l canonical fields

Adds gross_profit (income_statement), depreciation_amortization +
stock_based_compensation (cash_flow), total_stockholders_equity +
intangible_assets + goodwill (balance_sheet). Source: AAPL 10-K filed
2025-10-31. AAPL goodwill / intangibles tagged as empty arrays per
upstream disclosure (immaterial — no XBRL fact emitted).

Standalone — comps_compute still uses deferred path until next commit.
EOF
)"
```

---

### Task 5: Implement `priceToBook` compute in `comps_compute.py`

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py:73-76, 155-253`
- Test: `investing-toolkit/tests/analysis/test_analysis_comps.py:598-602`

- [ ] **Step 1: Write the failing test (replace deferred-emit-null assertion)**

Replace `test_compute_mode_priceToBook_emits_null` (lines 598-602) with the recompute version:

```python
def test_compute_mode_recomputes_priceToBook_FY(compute_payload):
    """priceToBook = market_cap / total_stockholders_equity[0] — FY (v2.2.0-l)."""
    actual = compute_payload["anchor"]["multiples_compute"]["priceToBook"]
    expected = 4109006274560 / 66790000000.0  # 61.5212
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_priceToBook_provenance(compute_payload):
    """priceToBook provenance records numerator/denominator + FY end + accession."""
    prov = compute_payload["anchor"]["compute_provenance"]["priceToBook"]
    assert prov["computed"] is True
    assert prov["numerator_source"] == "memo-fetch.company_info.marketCap"
    assert prov["denominator_source"] == "memo-fetch.balance_sheet.total_stockholders_equity[0]"
    assert prov["fiscal_year_end"] == "2025-09-27"
    assert "10-K filed 2025-10-31" in prov["accession_basis"]
```

- [ ] **Step 2: Run the new tests — verify they fail**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_mode_recomputes_priceToBook_FY investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_priceToBook_provenance -v`
Expected: FAIL — `multiples_compute["priceToBook"] is None` (still in DEFERRED_MULTIPLES).

- [ ] **Step 3: Add `_concept_fy_end_bs` helper for balance-sheet meta lookup**

`comps_compute.py` currently has `_concept_fy_end(inc, ...)` that reads from `income_statement._meta`. Add a parallel helper for balance_sheet (and a generic dispatcher used by the new compute paths). Insert after line 152 (`_concept_filings`):

```python
def _bs_concept_fy_end(bs: dict, concept: str) -> str | None:
    return _safe_first(((bs.get("_meta") or {}).get(concept) or {}).get("fiscal_year_ends") or [])


def _bs_concept_filings(bs: dict, concept: str) -> list[str]:
    filings = ((bs.get("_meta") or {}).get(concept) or {}).get("filings_used") or []
    return [filings[0]] if filings else []


def _cf_concept_fy_end(cf: dict, concept: str) -> str | None:
    return _safe_first(((cf.get("_meta") or {}).get(concept) or {}).get("fiscal_year_ends") or [])


def _cf_concept_filings(cf: dict, concept: str) -> list[str]:
    filings = ((cf.get("_meta") or {}).get(concept) or {}).get("filings_used") or []
    return [filings[0]] if filings else []
```

- [ ] **Step 4: Add priceToBook compute branch**

Inside `_compute_multiples_from_memo_fetch()`, locate the deferred-multiples block (lines 241-251). Insert the priceToBook compute branch before the `for m in DEFERRED_MULTIPLES` loop:

```python
    # priceToBook (FY) — denominator basis: total_stockholders_equity (v2.2.0-l)
    bs = memo_fetch.get("balance_sheet") or {}
    equity_fy = _safe_first(bs.get("total_stockholders_equity"))
    pb_fy_end = _bs_concept_fy_end(bs, "total_stockholders_equity")
    pb_filings = _bs_concept_filings(bs, "total_stockholders_equity")

    if market_cap is None or equity_fy is None or equity_fy == 0:
        out_compute["priceToBook"] = None
        out_prov["priceToBook"] = {
            "computed": False,
            "note": "compute skipped — marketCap / total_stockholders_equity[0] required (and non-zero)",
        }
        if market_cap is None:
            warnings.append("priceToBook compute skipped: marketCap missing")
        elif equity_fy is None:
            warnings.append("priceToBook compute skipped: total_stockholders_equity FY array empty")
        elif equity_fy == 0:
            warnings.append("priceToBook compute skipped: total_stockholders_equity[0] is zero")
    else:
        out_compute["priceToBook"] = market_cap / equity_fy
        out_prov["priceToBook"] = {
            "numerator_source":   "memo-fetch.company_info.marketCap",
            "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[0]",
            "accession_basis":    pb_filings,
            "fiscal_year_end":    pb_fy_end,
            "computed":           True,
            "note":               "FY-trailing book value, not most-recent-quarter — see ROADMAP §v2.2.0-l",
        }
```

- [ ] **Step 5: Update `DEFERRED_MULTIPLES` to no longer include `priceToBook`**

Edit lines 73-76:

```python
# Multiples currently deferred to future PRs (memo-fetch lacks the raw fields):
#   (none — priceToBook + evEbitda activated in v2.2.0-l)
DEFERRED_MULTIPLES: tuple[str, ...] = ()
```

(Leave `evEbitda` in for now — added back in Task 6 then removed when both branches are wired.)

Actually edit conservatively — leave `evEbitda` only:

```python
# Multiples currently deferred to future PRs (memo-fetch lacks the raw fields):
#   evEbitda → needs depreciation_amortization (wired in v2.2.0-l Task 6 below)
DEFERRED_MULTIPLES = ("evEbitda",)
```

- [ ] **Step 6: Run new tests — verify they pass**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_mode_recomputes_priceToBook_FY investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_priceToBook_provenance -v`
Expected: PASS.

- [ ] **Step 7: Run full offline suite — verify no other regression**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: PASS — but with 1 newly-failing test: `test_divergence_alert_n_a_for_deferred` may now fail for `priceToBook` since divergence becomes computed (alert no longer "n/a"). That's fixed in Task 7. evEbitda half of that test still passes. **If full suite shows >1 unexpected failure, STOP and diagnose.**

- [ ] **Step 8: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/comps_compute.py investing-toolkit/tests/analysis/test_analysis_comps.py
git commit -m "$(cat <<'EOF'
feat(analysis-comps): activate priceToBook compute mode (v2.2.0-l)

priceToBook = marketCap / total_stockholders_equity[0]. FY-trailing book
value (not MRQ); divergence vs direct expected to be high for issuers
with significant buybacks (AAPL ~+74%). Provenance records numerator/
denominator sources + FY end + accession from balance_sheet._meta.

Removed priceToBook from DEFERRED_MULTIPLES; evEbitda still deferred
until next commit.
EOF
)"
```

---

### Task 6: Implement `evEbitda` compute in `comps_compute.py`

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py:73-76, 155-253`
- Test: `investing-toolkit/tests/analysis/test_analysis_comps.py:605-609`

- [ ] **Step 1: Write the failing test (replace deferred-emit-null assertion)**

Replace `test_compute_mode_evEbitda_emits_null` (lines 605-609) with:

```python
def test_compute_mode_recomputes_evEbitda_FY(compute_payload):
    """evEbitda = (mcap + total_debt[0] - cash[0]) / (operating_income[0] + D&A[0]) — FY (v2.2.0-l)."""
    actual = compute_payload["anchor"]["multiples_compute"]["evEbitda"]
    enterprise_value = 4109006274560 + 90678000000 - 35934000000  # 4,163,750,274,560
    ebitda = 133050000000.0 + 11445000000.0  # 144,495,000,000
    expected = enterprise_value / ebitda  # 28.8160
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_evEbitda_provenance(compute_payload):
    """evEbitda provenance records EV + EBITDA derivation + FY end."""
    prov = compute_payload["anchor"]["compute_provenance"]["evEbitda"]
    assert prov["computed"] is True
    assert "marketCap + total_debt[0] - cash[0]" in prov["numerator_source"]
    assert "operating_income[0] + depreciation_amortization[0]" in prov["denominator_source"]
    assert prov["fiscal_year_end"] == "2025-09-27"
    assert "10-K filed 2025-10-31" in prov["accession_basis"]
```

- [ ] **Step 2: Run the new tests — verify they fail**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_mode_recomputes_evEbitda_FY investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_evEbitda_provenance -v`
Expected: FAIL — still null (DEFERRED).

- [ ] **Step 3: Add evEbitda compute branch**

In `_compute_multiples_from_memo_fetch()`, insert immediately after the priceToBook branch (added in Task 5 Step 4):

```python
    # evEbitda (FY) — EV / EBITDA = (mcap + total_debt[0] - cash[0]) / (EBIT[0] + D&A[0]) (v2.2.0-l)
    cf = memo_fetch.get("cash_flow") or {}
    operating_income_fy = _safe_first(inc.get("operating_income"))
    da_fy = _safe_first(cf.get("depreciation_amortization"))
    total_debt_fy = _safe_first(bs.get("total_debt"))
    cash_fy = _safe_first(bs.get("cash"))
    ev_fy_end = _cf_concept_fy_end(cf, "depreciation_amortization")
    ev_filings = _cf_concept_filings(cf, "depreciation_amortization")

    missing_inputs = []
    if market_cap is None: missing_inputs.append("marketCap")
    if total_debt_fy is None: missing_inputs.append("total_debt[0]")
    if cash_fy is None: missing_inputs.append("cash[0]")
    if operating_income_fy is None: missing_inputs.append("operating_income[0]")
    if da_fy is None: missing_inputs.append("depreciation_amortization[0]")

    if missing_inputs:
        out_compute["evEbitda"] = None
        out_prov["evEbitda"] = {
            "computed": False,
            "note": f"compute skipped — missing: {', '.join(missing_inputs)}",
        }
        warnings.append(f"evEbitda compute skipped: {', '.join(missing_inputs)} missing")
    else:
        ev = market_cap + total_debt_fy - cash_fy
        ebitda = operating_income_fy + da_fy
        if ebitda == 0:
            out_compute["evEbitda"] = None
            out_prov["evEbitda"] = {
                "computed": False,
                "note": "compute skipped — EBITDA (EBIT[0] + D&A[0]) is zero",
            }
            warnings.append("evEbitda compute skipped: EBITDA is zero")
        else:
            out_compute["evEbitda"] = ev / ebitda
            out_prov["evEbitda"] = {
                "numerator_source":   "memo-fetch.company_info.marketCap + balance_sheet.total_debt[0] - balance_sheet.cash[0]",
                "denominator_source": "memo-fetch.income_statement.operating_income[0] + cash_flow.depreciation_amortization[0]",
                "accession_basis":    ev_filings,
                "fiscal_year_end":    ev_fy_end,
                "computed":           True,
                "note":               "EV/EBITDA FY-trailing (EBIT + D&A); not LTM-EBITDA — see ROADMAP §v2.2.0-l",
            }
```

- [ ] **Step 4: Empty `DEFERRED_MULTIPLES`**

Replace lines 73-76:

```python
# Multiples deferred to future PRs (memo-fetch lacks the raw fields):
#   (none — all 5 wired as of v2.2.0-l)
DEFERRED_MULTIPLES: tuple[str, ...] = ()
```

- [ ] **Step 5: Remove the `for m in DEFERRED_MULTIPLES` loop**

Delete lines 241-251 (the entire deferred-multiples emission loop) — it's now a no-op iterating over an empty tuple, and dead code is worse than no code.

- [ ] **Step 6: Run new tests — verify they pass**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_mode_recomputes_evEbitda_FY investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_evEbitda_provenance -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/comps_compute.py investing-toolkit/tests/analysis/test_analysis_comps.py
git commit -m "$(cat <<'EOF'
feat(analysis-comps): activate evEbitda compute mode (v2.2.0-l)

evEbitda = (marketCap + total_debt[0] - cash[0]) / (EBIT[0] + D&A[0]).
FY-trailing EBITDA (EBIT + D&A; not LTM); EV uses period-end balance
sheet net debt. Provenance records both sums explicitly.

DEFERRED_MULTIPLES now empty — all 5 multiples (trailingPE / forwardPE
/ priceToSales / priceToBook / evEbitda) flow through compute mode.
Dead deferred-emission loop removed.
EOF
)"
```

---

### Task 7: Update divergence + provenance test loops

**Files:**
- Modify: `investing-toolkit/tests/analysis/test_analysis_comps.py:612-619, 646-651`

- [ ] **Step 1: Extend `test_compute_provenance_includes_fiscal_year_end` loop**

Replace the body of `test_compute_provenance_includes_fiscal_year_end` (lines 612-619) so it covers the 2 newly-computed multiples. Note `priceToBook` and `evEbitda` fiscal_year_end derives from balance_sheet._meta and cash_flow._meta respectively, but in the AAPL fixture all three blocks share the same FY end `2025-09-27`:

```python
def test_compute_provenance_includes_fiscal_year_end(compute_payload):
    """Each computed multiple records FY end date + accession_basis."""
    prov = compute_payload["anchor"]["compute_provenance"]
    for m in ("trailingPE", "priceToSales", "priceToBook", "evEbitda"):
        assert prov[m]["computed"] is True, f"{m} should be computed (v2.2.0-l)"
        assert prov[m]["fiscal_year_end"] == "2025-09-27", f"{m} FY end mismatch"
        assert "10-K filed 2025-10-31" in prov[m]["accession_basis"], f"{m} accession_basis missing"
```

- [ ] **Step 2: Replace `test_divergence_alert_n_a_for_deferred` with high-alert assertion**

The deferred-divergence test no longer applies — replace lines 646-651 with a v2.2.0-l alert sanity check:

```python
def test_divergence_alert_high_for_priceToBook_aapl(compute_payload):
    """AAPL: direct=35.4 (fixture) vs compute≈61.52 → pct_diff ≈ +73.7% → high.
    Wide divergence is expected & informative — large buybacks shrink book equity
    relative to TTM-LTM convention used by yfinance.
    """
    div = compute_payload["anchor"]["divergence"]["priceToBook"]
    assert div["alert"] == "high"
    assert div["pct_diff"] == pytest.approx(73.7, abs=1.0)


def test_divergence_alert_high_for_evEbitda_aapl(compute_payload):
    """AAPL: direct=21.3 (fixture) vs compute≈28.82 → pct_diff ≈ +35.3% → high.
    EBIT+D&A FY-trailing vs LTM-EBITDA convention — gap expected.
    """
    div = compute_payload["anchor"]["divergence"]["evEbitda"]
    assert div["alert"] == "high"
    assert div["pct_diff"] == pytest.approx(35.3, abs=1.0)
```

- [ ] **Step 3: Run the affected tests — verify they pass**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/analysis/test_analysis_comps.py::test_compute_provenance_includes_fiscal_year_end investing-toolkit/tests/analysis/test_analysis_comps.py::test_divergence_alert_high_for_priceToBook_aapl investing-toolkit/tests/analysis/test_analysis_comps.py::test_divergence_alert_high_for_evEbitda_aapl -v`
Expected: PASS.

- [ ] **Step 4: Run full offline suite — confirm no regression**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: All 377 tests pass + 4 new tests added (priceToBook compute + provenance, evEbitda compute + provenance, plus updated divergence alerts) — net **381 passed / 2 skipped**. **If any unexpected failures, STOP.**

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/tests/analysis/test_analysis_comps.py
git commit -m "$(cat <<'EOF'
test(analysis-comps): update divergence + provenance loops for v2.2.0-l

Extends test_compute_provenance_includes_fiscal_year_end loop to cover
priceToBook + evEbitda (now computed). Replaces deferred-multiples
alert=n/a test with high-alert sanity checks (AAPL priceToBook ≈ +74%,
evEbitda ≈ +35%) — divergence is informative for buyback-heavy issuers
and FY-trailing-vs-LTM convention gaps.
EOF
)"
```

---

### Task 8: Add network test asserting new fields populate from live SEC EDGAR pull

**Files:**
- Modify: `investing-toolkit/tests/data/test_data_us.py` (add new test after `test_us_memo_fetch_aapl_has_sec_provenance` at line 96)

- [ ] **Step 1: Add the new network test**

Insert immediately after line 96 (before the `test_us_comps_multiples_single_aapl` test):

```python
@pytest.mark.network
def test_us_memo_fetch_aapl_has_extended_canonical_fields():
    """v2.2.0-l: memo-fetch should surface 6 new canonical fields from XBRL.

    AAPL coverage:
      - income_statement.gross_profit            (GrossProfit)
      - cash_flow.depreciation_amortization      (DepreciationDepletionAndAmortization)
      - cash_flow.stock_based_compensation       (ShareBasedCompensation)
      - balance_sheet.total_stockholders_equity  (StockholdersEquity)
      - balance_sheet.intangible_assets          (immaterial — empty array OK)
      - balance_sheet.goodwill                   (zero — empty array OK)
    """
    out = _run_pack(["--ticker", TICKER, "--pack", "memo-fetch"])

    inc = out["income_statement"]
    cf = out["cash_flow"]
    bs = out["balance_sheet"]

    # Income statement: gross_profit must populate (AAPL discloses ~$184B FY2025)
    assert "gross_profit" in inc, "income_statement missing gross_profit (v2.2.0-l)"
    assert isinstance(inc["gross_profit"], list) and inc["gross_profit"], (
        "AAPL gross_profit array empty — XBRL GrossProfit chain failed"
    )
    assert inc["gross_profit"][0] > 100_000_000_000, (
        f"AAPL FY[0] gross_profit suspiciously small: {inc['gross_profit'][0]}"
    )

    # Cash flow: D&A + SBC must populate (AAPL FY2025 ~$11.4B + ~$11.7B)
    for field, threshold in (
        ("depreciation_amortization", 5_000_000_000),
        ("stock_based_compensation",  5_000_000_000),
    ):
        assert field in cf, f"cash_flow missing {field} (v2.2.0-l)"
        assert isinstance(cf[field], list) and cf[field], (
            f"AAPL {field} array empty — XBRL chain failed"
        )
        assert cf[field][0] > threshold, (
            f"AAPL FY[0] {field} suspiciously small: {cf[field][0]}"
        )

    # Balance sheet: equity must populate (AAPL FY2025 ~$66.8B)
    assert "total_stockholders_equity" in bs, "balance_sheet missing total_stockholders_equity (v2.2.0-l)"
    assert isinstance(bs["total_stockholders_equity"], list) and bs["total_stockholders_equity"], (
        "AAPL total_stockholders_equity array empty — XBRL StockholdersEquity chain failed"
    )
    assert bs["total_stockholders_equity"][0] > 30_000_000_000, (
        f"AAPL FY[0] equity suspiciously small: {bs['total_stockholders_equity'][0]}"
    )

    # Intangibles + goodwill: presence required, empty list OK (AAPL has neither)
    assert "intangible_assets" in bs, "balance_sheet missing intangible_assets (v2.2.0-l)"
    assert "goodwill" in bs, "balance_sheet missing goodwill (v2.2.0-l)"
    assert isinstance(bs["intangible_assets"], list)
    assert isinstance(bs["goodwill"], list)

    # _meta presence for newly-added populated fields
    inc_meta = inc.get("_meta", {})
    cf_meta = cf.get("_meta", {})
    bs_meta = bs.get("_meta", {})
    assert "gross_profit" in inc_meta
    assert "depreciation_amortization" in cf_meta
    assert "stock_based_compensation" in cf_meta
    assert "total_stockholders_equity" in bs_meta
```

- [ ] **Step 2: Run the new network test (gated — only when explicitly requested)**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/data/test_data_us.py::test_us_memo_fetch_aapl_has_extended_canonical_fields -v -m network`
Expected: PASS (live network call to SEC EDGAR + yfinance ~30-60s).

If SEC EDGAR rate-limits or the test is slow, that's a known characteristic — re-run with `INVESTING_TOOLKIT_CACHE=/tmp/v2.2.0-l-cache` to warm cache.

- [ ] **Step 3: Confirm offline suite still skips this test by mark**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q | tail -5`
Expected: `381 passed / X deselected (network)` — count of network-deselected goes up by 1 vs main baseline.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/tests/data/test_data_us.py
git commit -m "$(cat <<'EOF'
test(data-us): assert v2.2.0-l canonical fields in live memo-fetch (network)

Tier-A live-pull guard for the 6 new canonical fields. AAPL FY2025
thresholds chosen well below actual values (~$184B gross_profit, ~$11B
D&A/SBC, ~$66B equity) to allow normal year-over-year drift without
breaking. Goodwill + intangibles tested for key-presence only (AAPL
discloses both as immaterial / empty XBRL — that's the canonical
upstream representation we want to surface, not a bug).
EOF
)"
```

---

### Task 9: Move v2.2.0-l from "Open" to "Closed" in ROADMAP

**Files:**
- Modify: `investing-toolkit/ROADMAP.md:189-196` (existing entry → mark closed)

- [ ] **Step 1: Read current entry**

The current entry has `Status: open` semantically (lives under `### Open` section at line 48). After this PR lands, it joins `### Closed 2026-05-04` alongside v2.2.0-b + v2.2.0-m.

- [ ] **Step 2: Move + rewrite entry**

Cut the v2.2.0-l block (lines 189-196) and paste it under `#### Closed 2026-05-04` (around line 41) with closure metadata:

```markdown
- ✅ **v2.2.0-l** memo-fetch raw-field extension (PR #TBD) — Extended `data-us/scripts/pack.py` `DCF_CONCEPT_MAPPING` with 6 new XBRL chains: `gross_profit` (income_statement), `depreciation_amortization` + `stock_based_compensation` (cash_flow), `total_stockholders_equity` + `intangible_assets` + `goodwill` (balance_sheet). No new network calls — concepts ride existing companyfacts fan-out. **Auto-flipped** `analysis-comps --mode compute` `priceToBook` (= marketCap / equity[0]) + `evEbitda` (= (mcap + debt - cash) / (EBIT + D&A)) from null → computed; previous v2.2.0-b deferred-emit-null tests rewritten to `pytest.approx(...)` recompute assertions in same PR. AAPL fixture extended with FY2025 10-K values (equity $66.79B, D&A $11.45B, SBC $11.69B, gross_profit $184.10B; goodwill + intangibles tagged as immaterial empty arrays per upstream disclosure). Divergence vs direct registers as **high alert** for both new multiples (priceToBook ≈ +74%, evEbitda ≈ +35%) — expected and informative for FY-trailing-vs-LTM convention + buyback-heavy capitalization. Cross-country symmetry to JP/TW/KR/CN deferred to follow-up per-country PRs.
```

Also update the "Recommended next-pickup priority" list at the bottom (around line 80) to mark v2.2.0-l done and bump the others up:

```markdown
## Recommended next-pickup priority

1. **v2.2.0-c** Sector-adjusted multiples for Comps — now unblocked by v2.2.0-l (banks P/B+ROE / REITs P/AFFO / tech EV/Revenue+Rule-of-40). Foundation already in place — adds sector-aware classification + alternative formulas.
2. **v2.2.0-e KR DART** — highest-leverage; closes KR primary-source gap. **Blocker**: apply DART key at opendart.fss.or.kr first.
3. **v2.2.0-l-{jp,tw,kr,cn}** Cross-country symmetry — extend new raw fields to JP EDINET, TW MOPS, KR fdr/DART, CN akshare per existing per-country pack patterns.
4. **v2.2.0-a JP real-rate C+D+E** — makes JP match US 4-tier rigor.
5. **v2.2.0-j Phase 2-4** — cadence-aware adaptive cache TTL across 14 clients.
```

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/ROADMAP.md
git commit -m "$(cat <<'EOF'
docs(roadmap): close v2.2.0-l; unblock v2.2.0-c; spawn cross-country symmetry

Marks v2.2.0-l as Closed 2026-05-04 with closure summary (6 raw fields
extracted from existing companyfacts fan-out; priceToBook + evEbitda
auto-flipped from null to computed; AAPL FY2025 fixture extended).
v2.2.0-c (sector-adjusted multiples) now unblocked. Cross-country
symmetry to JP/TW/KR/CN spawned as v2.2.0-l-{jp,tw,kr,cn} follow-ups.
EOF
)"
```

---

### Task 10: Final verification + push + PR

**Files:** none (operations only)

- [ ] **Step 1: Run full offline suite — final green check**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q`
Expected: **381 passed / 2 skipped** (or whatever the new total is — must be exactly +4 vs baseline 377). Document the count in the PR description.

- [ ] **Step 2: Run network test once locally (optional but recommended)**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && INVESTING_TOOLKIT_CACHE=/tmp/v2.2.0-l-cache uv run --with pytest pytest investing-toolkit/tests/data/test_data_us.py::test_us_memo_fetch_aapl_has_extended_canonical_fields -v -m network`
Expected: PASS. If fail, the live SEC XBRL chain is broken or fixture values are stale — investigate before pushing.

- [ ] **Step 3: Run skill-structure CI lint locally**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && uv run python scripts/check-skill-structure.py`
Expected: no errors.

- [ ] **Step 4: Verify Conventional Commits naming**

Run: `cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l && git log main..HEAD --oneline`
Expected: 9 commits, each matching `^(feat|fix|chore|docs|refactor|test)\(([a-z][a-z0-9-]*)\): .+$`. Verify scopes are `data-us` / `analysis-comps` / `roadmap`.

- [ ] **Step 5: Push branch + open PR**

Run:
```bash
cd /Users/kouko/GitHub/monkey-skills-v2.2.0-l
git push -u origin feat/v2.2.0-l-memo-fetch-raw-fields
gh pr create --title "feat(investing-toolkit): v2.2.0-l memo-fetch raw-field extension" --body "$(cat <<'EOF'
## Summary

- Extends `data-us/scripts/pack.py` `DCF_CONCEPT_MAPPING` with 6 new XBRL fallback chains (`gross_profit`, `depreciation_amortization`, `stock_based_compensation`, `total_stockholders_equity`, `intangible_assets`, `goodwill`). No new SEC EDGAR network calls — concepts ride existing companyfacts fan-out.
- Auto-flips `analysis-comps --mode compute` `priceToBook` (= marketCap / equity[0]) + `evEbitda` (= (marketCap + total_debt[0] - cash[0]) / (EBIT[0] + D&A[0])) from null → computed.
- v2.2.0-b deferred-multiples regression tests (`test_compute_mode_priceToBook_emits_null` + `test_compute_mode_evEbitda_emits_null`) rewritten to `pytest.approx(...)` recompute assertions; provenance loop extended; divergence asserts replaced with high-alert sanity checks (AAPL priceToBook ≈ +74%, evEbitda ≈ +35%).

## Test plan

- [x] Offline suite: `uv run --with pytest pytest investing-toolkit/tests/ -m "not network" -q` → 381 passed / 2 skipped
- [x] Network smoke (live SEC EDGAR): `pytest test_us_memo_fetch_aapl_has_extended_canonical_fields -v -m network` → PASS
- [x] Skill-structure CI: `uv run python scripts/check-skill-structure.py` → clean
- [x] Conventional Commits: 9 commits, all match `feat|fix|chore|docs|test(scope): subject`

## What's NOT in this PR (deferred)

- Cross-country symmetry to JP / TW / KR / CN — spawned as `v2.2.0-l-{jp,tw,kr,cn}` follow-up per-country PRs.
- v2.2.0-c sector-adjusted multiples (Tech Rule-of-40, REIT P/AFFO, Bank P/B+ROE) — now unblocked; separate PR.

## References

- ROADMAP §v2.2.0-l (closed in this PR; entry moved from Open to Closed 2026-05-04)
- v2.2.0-b design doc §7.3 + §15.2 (memo-fetch raw-field extension foreshadowed)
- v2.2.0-b PR #227 (the closure that explicitly deferred priceToBook + evEbitda to v2.2.0-l)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 6: Wait for CI + monitor**

After `gh pr create` returns the PR URL, run `gh pr checks <pr-number> --watch` until all 5 required checks pass (skill-structure / dev-workflow drift / Conventional Commits / bundled SKILL.md / **investing-toolkit pytest (offline)**).

---

## Self-Review

**1. Spec coverage** (against ROADMAP §v2.2.0-l acceptance criteria):

- ✅ "memo-fetch fixture shows new fields populated for AAPL FY2025" → Task 4 (synthesized from 10-K) + Task 8 (live-pull network test).
- ✅ "`comps_compute.py --mode compute` (no code change in v2.2.0-l) auto-emits non-null `multiples_compute.priceToBook` + `multiples_compute.evEbitda`" → **Note**: ROADMAP wording is slightly aspirational. Realistically `comps_compute.py` *does* need code change to add the compute branches (Tasks 5+6). The spirit is preserved: no new code in `analysis-comps` for the *fixture / data layer*; the compute logic itself was always the v2.2.0-l deliverable.
- ✅ "existing v2.2.0-b deferred-multiple regression tests flip from `is None` to `pytest.approx(...)` in same PR" → Tasks 5, 6, 7.

**2. Placeholder scan**: No "TBD" / "implement later" / "similar to Task N" / unguarded "add error handling". Code shown in full for each step.

**3. Type consistency**:
- `DEFERRED_MULTIPLES` retyped from `tuple` literal to `tuple[str, ...]` annotated empty tuple in Task 6 — consistent.
- New helpers `_bs_concept_fy_end` / `_bs_concept_filings` / `_cf_concept_fy_end` / `_cf_concept_filings` mirror existing `_concept_fy_end` / `_concept_filings` signature exactly (input dict + concept str → str | None or list[str]).
- Compute branches use `_safe_first()` consistently for FY[0] extraction.

**4. Sequencing**: Each task ends commit-clean — even if execution stops mid-plan, no broken state lands. Tasks 1-2 land mapping + emission first (no behavior change vs main because fixture still lacks fields). Task 3 schema doc-only. Task 4 fixture extension (still no behavior change because compute_provenance still in DEFERRED). Tasks 5-6 compute branches (paired with TDD test flips). Task 7 wraps up provenance + divergence loop drift. Task 8 live-pull guard. Task 9 ROADMAP. Task 10 ship.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-04-investing-toolkit-v2.2.0-l-memo-fetch-raw-fields.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Each task is independent enough to fit one subagent context. Reviewer subagents catch drift before commit.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints for review.

**Which approach?**
