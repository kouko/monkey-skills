# ADR-0003: T3 Financial Statement Normalization

- **Status**: Accepted
- **Date**: 2026-05-02
- **Version target**: investing-toolkit v2.0.2 (PR #181 implementation)
- **Required by**: [ADR-0002](0002-layer-1-staging-tier-normalization.md) gate "T3 requires an ADR before implementation"
- **Contract reference**: [`docs/normalization-contract.md`](../normalization-contract.md) §Tier 3
- **Predecessor PRs**: #178 (T1 alias), #179 (T2 macro flatten)

## Context

Cross-layer Chain 2 (`data-us memo-fetch` → `analysis-dcf`) is the last broken chain on `main` after PR #178/#179. ADR-0002 routed it to Tier 3 because — unlike T1 (rename) and T2 (flatten) — converting SEC EDGAR XBRL `companyfacts` into a flat `income_statement` / `cash_flow` / `balance_sheet` requires **domain knowledge**:

- Concept name mapping (e.g. `us-gaap:Revenues` ↔ `RevenueFromContractWithCustomerExcludingAssessedTax`)
- Fiscal-year alignment (different companies, different fiscal year-ends)
- Multi-period selection (annual / quarterly / restated)
- Unit normalisation (USD raw vs USD millions)
- Accounting-standard awareness (US GAAP / IFRS / JP-GAAP / TIFRS / K-IFRS / CAS)

Two unresolved problems surface during ADR drafting:

### Problem 1 — pack.py currently does not fetch financial values

`data-us/scripts/pack.py:177` invokes `sec_edgar_client.py --action facts` **without `--concept`**. Per `sec_edgar_client.py:564–573`, when `--concept` is absent, the client returns only a **summary**:

```json
{
  "ticker": "AAPL",
  "concept_counts": {"us-gaap": 487, "dei": 41},
  "us_gaap_concepts": ["AccountsPayable", ..., "Revenues", ...],
  "entityName": "Apple Inc."
}
```

No financial values. The actual time-series for any concept requires a separate call with `--concept Revenues` etc. So the existing `sec_facts` block in `pack.py memo-fetch` output is documentation, not data.

This means T3 is not just normalize — it must also extend pack.py to **fetch** the financial values.

### Problem 2 — `analysis-dcf` input contract granularity

`analysis-dcf/SKILL.md` documents the input contract as:

```json
{
  "ticker": "AAPL",
  "income_statement": {"revenue": [r0, r-1, ...], "net_income": [...], "ebit": [...]},
  "cash_flow": {"fcf": [...], "capex": [...]},
  "balance_sheet": {"total_debt": [...], "cash": [...]},
  "shares_outstanding": 15728000000,
  "current_price": 175.0
}
```

7 fields total: revenue / net_income / ebit / fcf / capex / total_debt / cash + shares + price.

This is the canonical surface — and per Principle 2 of `normalization-contract.md`, all 5 countries must be able to populate it from primary source.

## Decision

### High-level approach

Adopt a **two-stage normalization in `pack.py`**:

1. **Stage 1 — Fetch**: pack.py invokes `sec_edgar_client.py --action facts --concept X` for each concept in a per-country mapping table. The raw companyfacts time-series for each concept lands under `pack.sec_facts.concepts.{concept_name}` (preserved per Principle 1).

2. **Stage 2 — Transform**: pack.py reduces the per-concept observations into canonical annual arrays (most-recent-first per `analysis-dcf` contract), with `_meta` provenance per Principle 4.

The same two-stage pattern applies to data-jp (EDINET concepts), data-tw (MOPS t164sb04/05/03), data-kr (DART when wired; yfinance fallback), data-cn (yfinance fallback until A-share fundamentals primary source identified).

### US mapping table (data-us, this PR's deliverable)

```python
DCF_CONCEPT_MAPPING = {
    # canonical_field → fallback chain of us-gaap concept names
    "revenue": [
        "Revenues",                                              # legacy + ASC 606 most common
        "RevenueFromContractWithCustomerExcludingAssessedTax",   # ASC 606 strict
        "Revenue",                                                # ifrs-full, fallback
        "SalesRevenueNet",                                        # deprecated, fallback
    ],
    "operating_income": [
        "OperatingIncomeLoss",                                   # standard
    ],
    "ebit": [
        "OperatingIncomeLoss",                                   # operating income proxy
    ],
    "net_income": [
        "NetIncomeLoss",                                         # standard
        "ProfitLoss",                                             # IFRS-style fallback
    ],
    "fcf": [],  # NOT directly in XBRL; derived as OperatingCashFlow - CapEx (see below)
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",            # most common
        "PaymentsToAcquireProductiveAssets",                      # alternative
    ],
    "total_debt": [
        "LongTermDebt",                                          # core long-term debt
        "DebtCurrent",                                            # adds to total via sum (see _meta)
        # Note: total_debt = LongTermDebt + ShortTermBorrowings + DebtCurrent
        #       implementation MAY sum multiple components; _meta records sum_of_concepts
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",                 # standard
        "Cash",                                                   # rare fallback
    ],
    "shares_outstanding": [
        # Special: pulled from sec_facts.dei.EntityCommonStockSharesOutstanding
        # OR from yfinance company_info.sharesOutstanding (cross-source compare in _meta)
    ],
    "current_price": [
        # NOT from XBRL — pulled from yfinance company_info.regularMarketPrice
    ],
}
```

**Concept fallback chain semantics** (per Principle 4):
- Try concepts in order; first non-empty wins
- `_meta.{field}.source_concept` records which concept actually supplied the value
- `_meta.{field}.fallback_used: true` if non-primary concept supplied
- If ALL concepts in chain are empty, canonical field = `null`, and `_meta.{field}.source_concept = null` with explanation in `_meta.{field}.note`

### Period selection

XBRL `companyfacts` returns observations like:

```json
{
  "units": {
    "USD": [
      {"end": "2024-09-28", "val": 391035000000, "fy": 2024, "fp": "FY", "form": "10-K", "filed": "2024-11-01"},
      {"end": "2024-06-29", "val": 85777000000, "fy": 2024, "fp": "Q3", "form": "10-Q", "filed": "2024-08-02"},
      {"end": "2023-09-30", "val": 383285000000, "fy": 2023, "fp": "FY", "form": "10-K", "filed": "2023-11-03"},
      ...
    ]
  }
}
```

**Rule**: T3 selects ONLY annual (`fp == "FY"`) observations from the most recent `form == "10-K"` filing per fiscal year. Multiple amendments (`10-K/A`) prefer the most recent `filed` date.

Returned canonical array is **most-recent-first** (matching `analysis-dcf/SKILL.md` contract):

```json
"income_statement": {
  "revenue": [394328000000, 383285000000, 365817000000, 274515000000, 260174000000]
}
```

5 years is the default depth (matches DCF's CAGR derivation needs); fewer if companyfacts returns less.

### `_meta` provenance fields (Principle 4 compliance)

```json
"income_statement": {
  "revenue": [394328, 383285, 365817, 274515, 260174],
  "_meta": {
    "revenue": {
      "source_concept": "Revenues",
      "fallback_used": false,
      "fallback_chain_tried": ["Revenues"],
      "fiscal_year_ends": ["2024-09-28", "2023-09-30", "2022-09-24", "2020-09-26", "2019-09-28"],
      "amendments_seen": [],
      "accounting_standard": "us_gaap",
      "unit": "USD",
      "filings_used": ["10-K filed 2024-11-01", "10-K filed 2023-11-03", ...]
    },
    "fcf": {
      "source_concept": null,
      "derivation": "operating_cash_flow - capex",
      "fallback_used": false,
      "components": {
        "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities",
        "capex": "PaymentsToAcquirePropertyPlantAndEquipment"
      }
    }
  }
}
```

### Country-specific extension block (Principle 3, deferred)

Per `normalization-contract.md` §Principle 3, country-unique concepts go into `{country}_specific` blocks. For US:

```json
"us_specific": {
  "non_gaap_eps": null,
  "non_gaap_eps_note": "Non-GAAP adjusted EPS lives in 8-K narratives, not XBRL — out of scope for T3 v1; future skill may parse 8-K text",
  "segment_revenue": null,
  "segment_revenue_note": "us-gaap:RevenuesFromExternalCustomers by segment — out of scope for T3 v1, future enhancement"
}
```

For US, the country-specific block is mostly empty placeholders for known gaps. JP/TW/KR/CN extension blocks are non-trivial (経常利益 / 月營收 / 별도재무제표 / 限售股) but out of this PR's scope.

### Lossless invariant test (Principle 5 compliance)

```python
def test_canonical_revenue_traces_to_raw():
    pack = json.loads((FIXTURE_DIR / "data-us-memo-fetch-sample.json").read_text())
    canonical = pack["income_statement"]["revenue"][0]
    meta = pack["income_statement"]["_meta"]["revenue"]
    concept = meta["source_concept"]
    raw_concept = pack["sec_facts"]["concepts"][concept]
    annual_obs = [o for o in raw_concept["units"]["USD"] if o.get("fp") == "FY"]
    assert canonical == max(annual_obs, key=lambda o: o["filed"])["val"]
```

CI enforces. If the test fails, the canonical block has drifted from raw — bug in normalize logic.

## Considered Alternatives

### Alternative A — Pre-fetch full companyfacts dump, transform downstream

Pack.py changes `--action facts` to fetch the full XBRL dump (companyfacts JSON, ~500KB-2MB per ticker). Stash entire dump in `sec_facts.facts.us-gaap`. Layer 2 (or a separate normalize step) transforms.

**Pros**: single HTTP call (companyfacts is a single endpoint).

**Cons**:
- Large pack output (~2MB per ticker bloats memo-fetch JSON)
- Transform logic in Layer 2 violates ADR-0002's "Layer 2 stays clean" principle
- Caching the full dump per-ticker is expensive (vs caching ~10 concepts)

### Alternative B — Per-concept fetch + transform in pack.py (chosen)

For each concept in DCF_CONCEPT_MAPPING, invoke `sec_edgar_client.py --action facts --concept X`. Each returns ~5-50 observation records (not the full dump). Pack.py transforms inline.

**Pros**:
- Smaller pack output (~50KB sec_facts vs 2MB)
- Transform stays in Layer 1 per the staging-tier model
- Per-concept caching is more granular (concept changes infrequently)

**Cons**:
- More HTTP calls per pack (~10 concepts × 1 req = 10 req per memo-fetch)
- SEC EDGAR rate limit 10 req/sec; each concept call is a separate request

The HTTP cost is acceptable: 10 concepts at 10 req/s = 1 second worst-case. SEC EDGAR concept endpoints are also CDN-cached, so most calls return in <100ms.

### Alternative C — Defer to analysis-dcf

Make `analysis-dcf` smart enough to read raw `sec_facts` and do its own concept mapping.

**Cons**: directly violates ADR-0002 (Layer 2 country-agnostic pure compute). Also bloats `analysis-dcf` with country-specific XBRL knowledge.

Rejected immediately.

## Decision summary

Adopt **Alternative B**: per-concept fetch in pack.py + inline transform into canonical income_statement / cash_flow / balance_sheet. _meta records full provenance per Principle 4.

## Phasing

| PR | Scope | Effort |
|---|---|---|
| **PR #181** (this ADR's deliverable) | data-us only — DCF_CONCEPT_MAPPING + 2-stage normalize + fixture regeneration with real concept data + lossless invariant tests | ~4 hours |
| PR #181a | data-jp T3 (EDINET key_metrics already mapped via `KEY_CONCEPTS` table; needs canonical surface alignment) | ~3 hours |
| PR #181b | data-tw T3 (MOPS t164sb04/05/03 → canonical; 月營收 → tw_specific) | ~3 hours |
| PR #181c | data-kr T3 (yfinance fallback Tier 2; DART deferred) | ~1 hour |
| PR #181d | data-cn T3 (yfinance fallback Tier 2; A-share primary deferred) | ~1 hour |

**PR #181 success criterion**: integration test Chain 2 (memo-fetch → analysis-dcf) turns green; xfail marker removed; all 5 cross-layer chains passing.

## Implementation Sketch (data-us, PR #181)

```python
# data-us/scripts/pack.py

DCF_CONCEPT_MAPPING = {  # canonical → us-gaap fallback chain
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", ...],
    ...
}

def _fetch_dcf_concepts(ticker: str) -> dict:
    """Per-concept fetch; ~10 calls."""
    out = {}
    for canonical, chain in DCF_CONCEPT_MAPPING.items():
        for concept in chain:
            result = run_client(SEC, ["--ticker", ticker, "--action", "facts",
                                      "--concept", concept])
            if result.get("observations"):
                out[concept] = result
                break  # first non-empty wins
    return out

def _normalize_dcf(raw_concepts: dict) -> dict:
    """Reduce raw concepts to canonical income_statement / cash_flow / balance_sheet."""
    # 1. Filter annual observations
    # 2. Sort by filed date desc; dedup by fiscal year
    # 3. Build {revenue: [...], _meta: {...}}
    ...

def pack_memo_fetch(ticker: str) -> dict:
    info = run_client(YF, ["--ticker", ticker, "--action", "info"])
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    filings = run_client(SEC, ["--ticker", ticker, "--action", "filings", ...])
    facts_summary = run_client(SEC, ["--ticker", ticker, "--action", "facts"])
    raw_concepts = _fetch_dcf_concepts(ticker)
    canonical = _normalize_dcf(raw_concepts)

    return {
        "pack": "memo-fetch",
        "ticker": ticker.upper(),
        "fetched_at": iso_now(),
        "company_info": info,
        "price_history": history,
        "history": history.get("data", []),  # T1 (already shipped)
        "sec_filings": filings,
        "sec_facts": {
            **facts_summary,
            "concepts": raw_concepts,        # T3 raw — concept-keyed time-series
        },
        # T3 canonical staging:
        "income_statement": canonical["income_statement"],
        "cash_flow":        canonical["cash_flow"],
        "balance_sheet":    canonical["balance_sheet"],
        "shares_outstanding": canonical["shares_outstanding"],
        "current_price":      canonical["current_price"],
        "us_specific": {
            "non_gaap_eps_note": "Out of scope for T3 v1; lives in 8-K narratives.",
            "segment_revenue_note": "Out of scope for T3 v1; future enhancement."
        },
    }
```

## Open Questions (deferred to PR #181 implementation)

1. **Cache strategy for per-concept fetches**: should each concept have its own cache file vs. one combined? (Lean toward per-concept — better CDN match.)

2. **Quarterly aggregation**: should T3 emit quarterly arrays alongside annual? Defer until a downstream consumer needs it.

3. **shares_outstanding cross-source verification**: the `_meta` block could record both XBRL `dei:EntityCommonStockSharesOutstanding` and yfinance `info.sharesOutstanding`, flagging discrepancies. This adds fidelity at the cost of complexity. Lean toward yfinance-primary for T3 v1, log XBRL value to `_meta.note` if available.

4. **Restatement handling**: `10-K/A` amendments alter prior-year values. Current rule "max by filed date" handles this naively. Edge case: dual amendments to same FY end. Defer; flag in `_meta.amendments_seen`.

## See Also

- [ADR-0001](0001-data-analysis-report-layers.md) — three-layer split
- [ADR-0002](0002-layer-1-staging-tier-normalization.md) — staging-tier model
- [`docs/normalization-contract.md`](../normalization-contract.md) — contract this ADR implements
- [`tests/integration/test_cross_layer_chains.py`](../../tests/integration/test_cross_layer_chains.py) — Chain 2 test
- SEC EDGAR XBRL companyfacts API: <https://www.sec.gov/edgar/sec-api-documentation>
- US GAAP taxonomy: <https://xbrl.fasb.org/us-gaap/>
