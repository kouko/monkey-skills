# investing-toolkit v2.2.0-c — Sector-Adjusted Multiples for Comps

**Status**: DRAFT (2026-05-04)
**Owner**: kouko
**Branch**: `feat/v2.2.0-c-sector-multiples`
**Worktree**: `/Users/kouko/GitHub/monkey-skills-v2.2.0-c`
**Predecessor specs**: `2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md`
**Roadmap entry**: `investing-toolkit/ROADMAP.md §v2.2.0-c`

---

## 1. Problem

`analysis-comps --mode compute` (shipped in v2.2.0-b/l) computes a **fixed
5-multiple set** (`trailingPE / forwardPE / evEbitda / priceToSales /
priceToBook`) for every anchor regardless of sector. This produces
nonsense for several large equity-issuer categories:

| Issuer category | Why fixed-5 fails |
|---|---|
| **Banks** | EBITDA undefined for banks; P/E noisy (loan-loss provisions); P/B + ROE is the canonical lens. |
| **Insurance** | Same as banks but combined-ratio-driven; book value is anchor. |
| **REITs** | Earnings dominated by non-cash D&A; P/FFO + EV/EBITDAre are NAREIT-canonical. |
| **Asset managers** | EBITDA usable but ROE on equity (regulatory float) drives multiple. |
| **Tech / SaaS** | Often loss-making → P/E meaningless; revenue-growth-on-margin (Rule of 40) drives valuation. |
| **Energy E&P** | EBITDA + reserves; book value reflects depleted assets. |
| **Utilities** | Regulated returns → P/B + dividend-payout focus. |

Cross-sector ranking on a fixed 5-multiple set therefore mixes apples
with oranges. The composite_rank in current `analysis-comps` output is
mathematically valid but semantically wrong when the peer set spans
sectors with incompatible multiple definitions.

## 2. Goal

Replace the fixed 5-multiple set with **sector-aware schema selection**:

1. Classify the anchor (and each peer) by `(yfinance.info.sector,
   yfinance.info.industry)` plus a manual override table for known
   misroutes (holdcos / multi-segment).
2. Look up a sector schema (multiples + indicators).
3. `--mode compute` recomputes the schema's multiples + indicators from
   the anchor's memo-fetch raw fundamentals (Layer-1 SEC EDGAR Tier A,
   already in v2.2.0-l).
4. Emit a single output document carrying both `multiples_compute`
   (price-based ratios) and a NEW `indicators` block (operating-context
   metrics like ROE / Rule-of-40), with full per-multiple
   `compute_provenance`.

**Non-goals** (deferred — see §11):

- Per-country symmetry (JP/TW/KR/CN). v2.2.0-c is **US-only**;
  non-US `data-{country}` packs do not yet expose `gross_profit /
  D&A / SBC / equity / intangibles / goodwill`. Cross-country
  follow-up is `v2.2.0-l-{jp,tw,kr,cn}` (predecessor) → then
  `v2.2.0-c-{jp,tw,kr,cn}` (successor).
- Industry-specific concepts NOT in standard US-GAAP XBRL: NIM,
  combined ratio, AUM, AFFO straight-line-rent adjustment, oil reserves,
  ARPU, RevPAR. These are deliberately omitted from schemas (not
  emitted as `null`); see §6.4.
- Peer-list discovery (still report-layer's job per Spec §5.5).

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  data-us/pack.py --pack memo-fetch (anchor, Tier A)        │
│  data-us/pack.py --pack comps-multiples (anchor + peers)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  analysis-comps/scripts/sector_classifier.py  (NEW)         │
│   Inputs:                                                    │
│     - anchor comps-multiples pack (info.sector, info.industry)│
│     - sector-routing.yaml                                    │
│     - sector-overrides.yaml                                  │
│   Output: schema_id ∈ {default, bank, insurance,             │
│              asset-manager, reit, tech-saas, tech-semis,     │
│              energy, utilities}                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  analysis-comps/references/schemas/<schema_id>.json         │
│   {multiples: [...], indicators: [...], notes: {...}}        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  analysis-comps/scripts/comps_compute.py (EXTENDED)         │
│   - load schema for anchor's sector                          │
│   - compute multiples per schema.multiples                   │
│   - compute indicators per schema.indicators                 │
│   - peers stay direct-mode (per anchor schema's multiple set)│
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
                  comps table JSON
                  (with schema_id + indicators block)
```

## 4. Sector routing

### 4.1 yfinance taxonomy primer

yfinance exposes two granularities per ticker:

- `info.sector` — 11 GICS-aligned high-level categories (e.g.
  `Financial Services`, `Real Estate`).
- `info.industry` — ~150 finer categories within sectors (e.g.
  `Banks - Diversified`, `Insurance - Property & Casualty`,
  `REIT - Retail`).

Routing requires **both** because two sectors are internally heterogeneous:
- `Financial Services` covers banks / insurance / asset managers
- `Real Estate` covers REITs / property developers

All other sectors are sufficiently homogeneous that `sector` alone routes correctly.

### 4.2 `sector-routing.yaml` SoT

```yaml
# investing-toolkit/skills/analysis-comps/references/sector-routing.yaml
# Source-of-truth for (yfinance.info.sector, yfinance.info.industry) → schema_id.
# Per-sector ordered list of (industry_pattern, schema_id) — first match wins.
# industry_pattern is a case-insensitive substring match.
# Sectors with a single homogeneous schema use a `_default:` shortcut.

version: 1

routes:
  # Heterogeneous sectors — industry-level routing required
  Financial Services:
    - industry_contains: "Bank"           # "Banks - Diversified", "Banks - Regional"
      schema: bank
    - industry_contains: "Insurance"       # all insurance sub-industries
      schema: insurance
    - industry_contains: "Asset Management"
      schema: asset-manager
    - industry_contains: "Capital Markets" # exchanges / brokerages → asset-manager-flavored
      schema: asset-manager
    - industry_contains: "Credit Services" # AmEx / Visa style — payments
      schema: default
    - _default: asset-manager              # fallback for unclassified FinSvcs

  Real Estate:
    - industry_contains: "REIT"            # "REIT - Retail", "REIT - Office", etc.
      schema: reit
    - industry_contains: "Real Estate Services"
      schema: default
    - _default: default                    # property developers / real-estate ops

  Technology:
    - industry_contains: "Software"        # SaaS, application software, infrastructure software
      schema: tech-saas
    - industry_contains: "Information Technology Services"
      schema: tech-saas
    - industry_contains: "Internet"
      schema: tech-saas
    - industry_contains: "Semiconductor"
      schema: tech-semis
    - _default: default                    # Hardware, electronics — bucket as default

  Communication Services:
    - industry_contains: "Internet Content"
      schema: tech-saas
    - industry_contains: "Software"
      schema: tech-saas
    - _default: default                    # Telecom, Media, Entertainment

  # Homogeneous sectors — single schema
  Energy:
    - _default: energy
  Utilities:
    - _default: utilities

  # All else → default
  Healthcare:
    - _default: default
  Consumer Cyclical:
    - _default: default
  Consumer Defensive:
    - _default: default
  Industrials:
    - _default: default
  Basic Materials:
    - _default: default

# Fallback when info.sector is missing or not in `routes`
_unknown_sector: default
```

### 4.3 `sector-overrides.yaml` SoT

```yaml
# investing-toolkit/skills/analysis-comps/references/sector-overrides.yaml
# Issuer-level override for known yfinance misroutes (holdcos, multi-business).
# ticker → schema_id (one of: default, bank, insurance, asset-manager,
#                              reit, tech-saas, tech-semis, energy, utilities)

version: 1

overrides:
  # Holdcos — yfinance's Financial Services classification is misleading
  BRK-B: default     # Berkshire — diversified holdco; insurance + railroad + utilities + ...
  BRK-A: default
  BAM:   default     # Brookfield Asset Management — but parent BN is conglomerate

  # Conglomerates classified as a single sector but operate across many
  GE:    default     # post-spin still industrial conglomerate
  9984.T: default    # SoftBank Group — VC + telecom + tech holdco
  6758.T: default    # Sony — electronics + entertainment + finance

  # Examples below are NOT yet locked — populate as discovered during dogfooding
  # SHOP:  tech-saas  # if yfinance routes "Internet Retail" instead of Software
  # ARES:  asset-manager  # if yfinance routes Industrials/Capital Markets edge
```

The override table is intentionally minimal at v2.2.0-c launch; entries
accrete as dogfooding surfaces misroutes.

### 4.4 Resolution rule

```python
def classify(ticker: str, sector: str | None, industry: str | None) -> tuple[str, str]:
    """Returns (schema_id, source).
    source ∈ {"override", "industry_match", "sector_default", "unknown_sector"}
    """
    if ticker in OVERRIDES:
        return OVERRIDES[ticker], "override"
    if not sector or sector not in ROUTES:
        return UNKNOWN_SECTOR_FALLBACK, "unknown_sector"
    for rule in ROUTES[sector]:
        if "_default" in rule:
            return rule["_default"], "sector_default"
        if industry and rule["industry_contains"].lower() in industry.lower():
            return rule["schema"], "industry_match"
    # No industry rule matched + no sector default — should not happen if yaml well-formed
    return UNKNOWN_SECTOR_FALLBACK, "unknown_sector"
```

## 5. Schema definitions

Each schema lives at `references/schemas/<id>.json`. Format:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "schema_id": "bank",
  "version": 1,
  "label": "Banks (P/B + ROE focus)",
  "applies_to_industries_example": ["Banks - Diversified", "Banks - Regional"],
  "multiples": [
    {"id": "trailingPE",          "kind": "compute",  "formula_id": "trailingPE_FY"},
    {"id": "forwardPE",           "kind": "passthrough"},
    {"id": "priceToBook",         "kind": "compute",  "formula_id": "priceToBook_FY"},
    {"id": "priceToTangibleBook", "kind": "compute",  "formula_id": "priceToTangibleBook_FY"}
  ],
  "indicators": [
    {"id": "ROE",                 "formula_id": "ROE_FY"}
  ],
  "deferred_concepts": [
    {"id": "NIM",            "reason": "Net interest margin requires interest_income / interest_earning_assets — not standard US-GAAP XBRL tags"},
    {"id": "efficiency_ratio", "reason": "Non-interest_expense / (NII + non-interest_income) — bank supplemental disclosure"},
    {"id": "NPL_ratio",      "reason": "Loan-loss disclosure — bank supplemental"}
  ],
  "notes": "Bank EBITDA is undefined (no operating cash-flow concept of cash earnings); evEbitda intentionally absent. forwardPE is a sell-side consensus pass-through (no primary source)."
}
```

The 9 schemas:

| schema_id | Multiples | Indicators | Deferred (out of scope) |
|---|---|---|---|
| **default** | trailingPE, forwardPE, evEbitda, priceToSales, priceToBook | gross_margin, operating_margin, FCF_yield | — |
| **bank** | trailingPE, forwardPE, priceToBook, priceToTangibleBook | ROE | NIM, efficiency_ratio, NPL_ratio |
| **insurance** | trailingPE, priceToBook, priceToTangibleBook | ROE, book_value_growth | combined_ratio, premium_growth |
| **asset-manager** | trailingPE, priceToBook, evEbitda | ROE | AUM_growth, fee_margin |
| **reit** | priceToFFO, evEbitdare, priceToBook, priceToTangibleBook | (none in v2.2.0-c) | AFFO, dividend_yield (until v2.2.0-c-reit-divs) |
| **tech-saas** | forwardPE, priceToSales, evRevenue | rule_of_40, gross_margin, FCF_margin | — |
| **tech-semis** | trailingPE, forwardPE, priceToSales, evEbitda | gross_margin, FCF_margin | inventory_turnover (no inventory in memo-fetch) |
| **energy** | evEbitda, priceToBook, priceToCFO | FCF_yield, debt_to_equity | reserves, production |
| **utilities** | trailingPE, evEbitda, priceToBook | debt_to_equity | dividend_payout (until divs landed) |

## 6. Compute formulas

All formulas operate on memo-fetch fields shipped in v2.2.0-l (PR #239).

### 6.1 Multiples — net new vs v2.2.0-b/l

Already implemented (v2.2.0-b/l):
- `trailingPE_FY` = `current_price ÷ (net_income[0] / shares_outstanding)`
- `priceToSales_FY` = `marketCap / revenue[0]`
- `priceToBook_FY` = `marketCap / total_stockholders_equity[0]`
- `evEbitda_FY` = `(marketCap + total_debt − cash) / (operating_income[0] + D&A[0])`

NEW in v2.2.0-c:

| Formula | Definition | Notes |
|---|---|---|
| `priceToTangibleBook_FY` | `marketCap / (equity[0] − goodwill[0] − intangibles[0])` | If goodwill/intangibles arrays are `[]` (immaterial), substitute `0`; document via `note`. Guard against tangible_book ≤ 0 (over-amortized intangibles edge). |
| `priceToFFO_FY` | `marketCap / (net_income[0] + D&A[0])` | **APPROXIMATION**: strict NAREIT FFO subtracts gains_on_sale_of_property; not in standard XBRL → omitted. `note: "FFO ≈ NI + D&A; gains_on_sale not subtracted (XBRL gap)"`. |
| `evEbitdare_FY` | `(marketCap + total_debt − cash) / (operating_income[0] + D&A[0])` | **APPROXIMATION**: strict NAREIT EBITDAre adds back impairment + gains_on_sale; not in standard XBRL → reverts to plain EBITDA. `note: "EBITDAre ≈ EBITDA; impairment/gains_on_sale not added back (XBRL gap)"`. |
| `priceToCFO_FY` | `marketCap / operating_cash_flow[0]` | Energy/midstream lean; OCF is a Tier-A primary-source concept. |
| `evRevenue_FY` | `(marketCap + total_debt − cash) / revenue[0]` | Tech-SaaS lean (often loss-making, P/E meaningless). |

### 6.2 Indicators — all NEW

Indicators are emitted as **percentages** (number, not "%-suffixed string") with explicit `unit: "pct"` field for downstream rendering.

| Indicator | Definition | Unit |
|---|---|---|
| `ROE_FY` | `net_income[0] / equity[0] × 100` | pct |
| `book_value_growth_FY` | `(equity[0] − equity[1]) / equity[1] × 100` | pct |
| `gross_margin_FY` | `gross_profit[0] / revenue[0] × 100` | pct |
| `operating_margin_FY` | `operating_income[0] / revenue[0] × 100` | pct |
| `FCF_yield_FY` | `(operating_cash_flow[0] − capex[0]) / marketCap × 100` | pct |
| `FCF_margin_FY` | `(operating_cash_flow[0] − capex[0]) / revenue[0] × 100` | pct |
| `debt_to_equity_FY` | `total_debt / equity[0] × 100` | pct |
| `rule_of_40_FY` | `revenue_growth_yoy + operating_margin` where `revenue_growth_yoy = (revenue[0] − revenue[1]) / revenue[1] × 100`. **Sum of two pcts.** | pct |

Each indicator carries `compute_provenance.{indicator}` mirroring the
multiple-provenance shape (`numerator_source`, `denominator_source`,
`accession_basis`, `fiscal_year_end`, `computed`, optional `note`).

### 6.3 Edge cases

- **Tangible book ≤ 0**: emit `null` + `note: "tangible book non-positive (over-amortized intangibles or goodwill > equity)"`.
- **revenue[1] missing or zero**: rule_of_40 / book_value_growth → `null` + `note`.
- **gross_profit / D&A / SBC / intangibles / goodwill array empty (`[]`)**: per v2.2.0-l convention, treat as `0` for goodwill/intangibles (immaterial-empty signal); for gross_profit treat as `null` (= absent disclosure).
- **EBITDA == 0**: existing v2.2.0-l guard (negative EBIT offsetting D&A) applies to evEbitdare too.

### 6.4 Why deferred concepts are NOT emitted as null

Schemas list deferred concepts in a separate `deferred_concepts` field, not in `multiples` or `indicators`. The output payload **does not** carry these as null fields. Rationale:
- Permanent-null fields invite consumers to "wait for them" and clutter output schema validation
- `deferred_concepts` is a documentation hatch — listed for human readers, not for code paths
- If a future PR adds (e.g.) `total_assets` to memo-fetch enabling ROA, it gets added as a multiple/indicator and removed from `deferred_concepts` in the same PR

## 7. CLI surface

No new flags. Sector classification is **automatic** when `--mode compute` runs:

```bash
uv run scripts/comps_compute.py \
    --anchor <comps-multiples.json> \
    --peers  <peer1.json>,<peer2.json>,... \
    --mode compute \
    --anchor-base <memo-fetch.json>
```

Two new optional flags:

| Flag | Purpose |
|---|---|
| `--sector-override <id>` | Force a schema_id (debug; bypasses both yaml routing and override table). |
| `--show-routing` | Stderr: print resolved schema_id + source ({override, industry_match, sector_default, unknown_sector}). Useful when adding to overrides yaml. |

Direct mode (`--mode direct`) is **unchanged** — still emits the
fixed-5-multiple statistics + ranking. v2.2.0-c sector logic is compute-mode-only.

## 8. Output schema additions

```json
{
  "anchor": {
    "ticker": "JPM",
    "sector": "Financial Services",
    "industry": "Banks - Diversified",
    "schema_id": "bank",
    "schema_routing_source": "industry_match",

    "multiples_direct": {
      "trailingPE": 12.5,
      "forwardPE":  11.0,
      "priceToBook": 1.8,
      "priceToTangibleBook": null   // not in comps-multiples pack; null in direct
    },
    "multiples_compute": {
      "trailingPE": 12.6,
      "forwardPE":  11.0,
      "priceToBook": 1.81,
      "priceToTangibleBook": 2.05
    },
    "indicators": {
      "ROE":       {"value": 16.2, "unit": "pct"}
    },
    "divergence": {
      "trailingPE":          {"abs_diff": 0.1,  "pct_diff": 0.8,  "alert": "low"},
      "forwardPE":           {"abs_diff": 0.0,  "pct_diff": 0.0,  "alert": "n/a", "note": "pass-through"},
      "priceToBook":         {"abs_diff": 0.01, "pct_diff": 0.6,  "alert": "low"},
      "priceToTangibleBook": {"abs_diff": null, "pct_diff": null, "alert": "n/a", "note": "direct-mode value not in comps-multiples pack"}
    },
    "compute_provenance": {
      "trailingPE":          {...},
      "forwardPE":           {"computed": false, "note": "pass-through ..."},
      "priceToBook":         {...},
      "priceToTangibleBook": {
        "numerator_source": "memo-fetch.company_info.marketCap",
        "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[0] - goodwill[0] - intangible_assets[0]",
        "accession_basis": ["0000019617-26-000001"],
        "fiscal_year_end": "2025-12-31",
        "computed": true,
        "note": "intangibles + goodwill from FY balance sheet"
      },
      "ROE": {
        "numerator_source": "memo-fetch.income_statement.net_income[0]",
        "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[0]",
        "accession_basis": ["0000019617-26-000001"],
        "fiscal_year_end": "2025-12-31",
        "computed": true
      }
    }
  },
  "peers": [...],     // unchanged shape; peers stay direct-mode
  "statistics": {...},  // computed across the schema's multiples (not the universal 5)
  "anchor_delta": {...},
  "ranking": [...],
  "_provenance": {
    "skill": "analysis-comps",
    "anchor_data_source": "...",
    "anchor_base_source": "...",
    "peer_data_sources": [...],
    "computed_at": "...",
    "io": "none",
    "mode": "compute",
    "requested_mode": "compute",
    "schema_id": "bank",
    "schema_version": 1,
    "schema_routing_source": "industry_match",
    "warnings": [...]
  }
}
```

### 8.1 Statistics + ranking

Statistics and ranking are computed across **the schema's multiples**, not the universal 5. So:
- `bank` anchor → `statistics.{trailingPE, forwardPE, priceToBook, priceToTangibleBook}` only
- `tech-saas` anchor → `statistics.{forwardPE, priceToSales, evRevenue}` only

Composite_rank averages across whatever multiples the schema lists.

### 8.2 Peer schema mismatch handling

If a peer's classified schema_id differs from the anchor's, emit:
- Warning in `_provenance.warnings`: `Peer {ticker} classified as schema {peer_schema}; anchor schema is {anchor_schema}. Statistics may be misleading; recommend per-sector peer set.`
- The peer is still included in statistics (the report layer is responsible for peer hygiene).
- Per-peer `schema_id` is added to each `peers[*]` entry for downstream visibility.

## 9. References file layout

```
analysis-comps/
├── SKILL.md                              (extended §"Sector schemas")
├── scripts/
│   ├── comps_compute.py                  (extended)
│   └── sector_classifier.py              (NEW)
└── references/
    ├── divergence-thresholds.md          (unchanged)
    ├── schema-compute-output.json        (extended: anchor.{sector,industry,schema_id,indicators})
    ├── sector-routing.yaml               (NEW — SoT)
    ├── sector-overrides.yaml             (NEW — SoT)
    └── schemas/                          (NEW)
        ├── default.json
        ├── bank.json
        ├── insurance.json
        ├── asset-manager.json
        ├── reit.json
        ├── tech-saas.json
        ├── tech-semis.json
        ├── energy.json
        └── utilities.json
```

### Drift rules

Per repo-wide SSOT-and-functional-copy convention:

1. **Multiple/indicator formulas** — code is SoT; spec table §6 is the human-readable mirror; same-PR drift requirement.
2. **Sector routing** — `sector-routing.yaml` is SoT; `sector_classifier.py` reads it at runtime (no functional copy in code).
3. **Override table** — `sector-overrides.yaml` is SoT; same as routing.
4. **Schema files** — schema JSONs are SoT for what each sector emits; spec table §5 is the human-readable mirror.

## 10. Acceptance tests

`tests/analysis/test_comps_sector_routing.py` (NEW) + extension to existing
`tests/analysis/test_comps_compute_mode.py`.

### 10.1 Routing tests (offline; mocked yfinance shape)

| Ticker | Mocked sector | Mocked industry | Expected schema_id | Routing source |
|---|---|---|---|---|
| AAPL  | Technology              | Consumer Electronics  | default        | sector_default |
| MSFT  | Technology              | Software - Infrastructure | tech-saas  | industry_match |
| TSM   | Technology              | Semiconductors        | tech-semis     | industry_match |
| JPM   | Financial Services      | Banks - Diversified   | bank           | industry_match |
| MET   | Financial Services      | Insurance - Diversified | insurance    | industry_match |
| BLK   | Financial Services      | Asset Management      | asset-manager  | industry_match |
| O     | Real Estate             | REIT - Retail         | reit           | industry_match |
| LEN   | Consumer Cyclical       | Residential Construction | default     | sector_default |
| XOM   | Energy                  | Oil & Gas Integrated  | energy         | sector_default |
| NEE   | Utilities               | Utilities - Regulated Electric | utilities | sector_default |
| BRK-B | Financial Services      | Insurance - Diversified | default      | override |
| FOO   | (missing / unknown)     | (anything)            | default        | unknown_sector |

### 10.2 Compute tests (network; existing `not network` marker pattern)

Live SEC EDGAR fetch via existing `data-us/scripts/pack.py` infrastructure:

| Ticker | Schema | Acceptance |
|---|---|---|
| **AAPL** | default | trailingPE / forwardPE / evEbitda / priceToSales / priceToBook all non-null; gross_margin > 30%, operating_margin > 25% |
| **JPM** | bank | trailingPE + forwardPE + priceToBook + priceToTangibleBook all non-null; ROE > 10%; evEbitda absent (not in schema) |
| **O** (Realty Income) | reit | priceToFFO + evEbitdare + priceToBook + priceToTangibleBook all non-null; **note** mentions "FFO ≈ NI + D&A" approximation |
| **MSFT** | tech-saas | forwardPE + priceToSales + evRevenue non-null; rule_of_40 > 30 (sum of revenue_growth + operating_margin); gross_margin > 60% |
| **XOM** | energy | evEbitda + priceToBook + priceToCFO non-null; FCF_yield computed; debt_to_equity computed |
| **NEE** | utilities | trailingPE + evEbitda + priceToBook non-null; debt_to_equity > 100% expected |
| **BRK-B** | default (via override) | falls back to fixed 5-multiple set; routing_source = "override" |

### 10.3 Edge-case tests

- Anchor with empty goodwill `[]` (immaterial) + non-empty intangibles `[]` → priceToTangibleBook == priceToBook (both substitute 0); note explains.
- Anchor with negative tangible book → priceToTangibleBook null + note.
- Tech-SaaS anchor with `revenue[1]` missing → rule_of_40 null + note; other tech multiples still computed.
- Peer schema mismatch (e.g. anchor=bank, peer=default) → warning emitted; peer included in stats.
- `--sector-override unknown-id` → exit 2 with helpful stderr message.

## 11. Migration from v2.2.0-b/l

- Default mode (`--mode direct`) **unchanged** — fixed-5-multiple still works.
- `--mode compute` output gains 4 new fields: `anchor.sector`, `anchor.industry`, `anchor.schema_id`, `anchor.indicators`. Existing consumers reading `multiples_compute` keep working when schema = `default`; for non-default schemas the keys differ.
- `report-equity-memo` Phase 2.5 currently calls `--mode compute --anchor-base` and expects the fixed-5 keys. **Action: wire Phase 2.5 to read schema-aware keys**. Non-trivial; tracked as same-PR follow-up.
- Output JSON schema (`schema-compute-output.json`) extended; existing Layer-3 tests need a fixture refresh.

## 12. PR plan

Subagent-driven (per `feedback_subagent_driven_development_validated.md`).

| # | Task | Files touched | Reviewer focus |
|---|---|---|---|
| 1 | sector-routing.yaml + sector-overrides.yaml + sector_classifier.py | references/, scripts/sector_classifier.py | YAML completeness; routing.py edge cases |
| 2 | 9 schema JSONs in references/schemas/ | references/schemas/*.json | Schema correctness vs spec §5 table |
| 3 | comps_compute.py — schema loading + per-multiple dispatch | scripts/comps_compute.py | Per-formula correctness |
| 4 | comps_compute.py — indicators block + provenance | scripts/comps_compute.py | Provenance shape parity with multiples |
| 5 | output schema-compute-output.json extension | references/schema-compute-output.json | JSON Schema validity |
| 6 | routing tests (offline) | tests/analysis/test_comps_sector_routing.py | Coverage of all 9 schemas + override + unknown |
| 7 | compute tests (network) | tests/analysis/test_comps_sector_compute.py (NEW) + extension | Live SEC fetch; 7 ticker acceptance |
| 8 | report-equity-memo Phase 2.5 schema-aware wiring | skills/report-equity-memo/scripts/* | Phase 4 input bundle assembly still passes |
| 9 | SKILL.md + ROADMAP.md + spec → versioned | analysis-comps/SKILL.md, ROADMAP.md, this spec moved | Doc parity |
| 10 | (optional) ADR-0009 if architecture warrants | docs/adr/ | Decision rationale |

Each task is a fresh-subagent commit with 2-stage review (spec then code-quality), per the validated v2.2.0-l pattern.

## 13. Open questions

(To be resolved during implementation; flagged here so reviewers see them.)

1. **REIT P/FFO without gains_on_sale** — How loud should the approximation note be? Lean: `note` field at multiple level + `notes` field in schema file; do not block emission.
2. **Tangible book negative edge** — Some software / pharma companies have negative tangible book (e.g. WBD). Currently emit null + note; alternative is emit the negative number with a `negative_tangible_book: true` flag. Lean: null + note (analytically a negative ratio is meaningless).
3. **Per-peer sector classification** — Is calling sector_classifier per peer pack expensive? Each peer pack has its own `info.sector` / `info.industry` already; classifier is pure-function over yaml. Lean: yes, classify each peer for the warning path.
4. **Override scope creep** — Should `sector-overrides.yaml` carry a `note:` field per ticker explaining the override? Lean: yes, for audit.

---

## Appendix A — Computability matrix

| Field needed | In memo-fetch v2.2.0-l? | Source |
|---|---|---|
| revenue (FY array) | ✅ | XBRL `Revenues` chain |
| operating_income | ✅ | `OperatingIncomeLoss` |
| net_income | ✅ | `NetIncomeLoss` |
| gross_profit | ✅ (PR #239) | `GrossProfit` |
| operating_cash_flow | ✅ | `NetCashProvidedByUsedInOperatingActivities` |
| capex | ✅ | `PaymentsToAcquirePropertyPlantAndEquipment` |
| D&A | ✅ (PR #239) | `DepreciationDepletionAndAmortization` chain |
| SBC | ✅ (PR #239) | `ShareBasedCompensation` |
| total_debt | ✅ | LongTermDebt + DebtCurrent |
| cash | ✅ | `CashAndCashEquivalentsAtCarryingValue` |
| total_stockholders_equity | ✅ (PR #239) | `StockholdersEquity` chain |
| intangible_assets | ✅ (PR #239; may be `[]`) | `IntangibleAssetsNetExcludingGoodwill` chain |
| goodwill | ✅ (PR #239; may be `[]`) | `Goodwill` |
| marketCap | ✅ | yfinance company_info |
| current_price | ✅ | yfinance |
| shares_outstanding | ✅ | yfinance |
| **gains_on_sale_of_property** | ❌ | REIT supplemental — not standard XBRL |
| **interest_income / earning_assets** | ❌ | Bank supplemental |
| **claims / earned_premiums** | ❌ | Insurance supplemental |
| **AUM** | ❌ | Asset-manager supplemental |
| **inventory** | ❌ (deferred) | XBRL `InventoryNet` exists; could add later |
| **dividends paid / per share** | ❌ (deferred) | XBRL `PaymentsOfDividends` exists; could add later |
| **total_assets** | ❌ (deferred) | XBRL `Assets` exists; could add for ROA |

Adding inventory / dividends / total_assets is a candidate for v2.2.0-c-followup but **not in scope for v2.2.0-c launch**.

---

**End of spec.**
