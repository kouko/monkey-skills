# Layer 1 Normalization Contract

> **Audience**: developers extending `data-{country}/scripts/pack.py`,
> adding a new pack output type, or wiring a new analysis-* skill.
> **Authority**: this contract supersedes any per-skill SKILL.md claim
> about input shape. If a Layer 2 skill's input expectation contradicts
> this contract, the Layer 2 skill is wrong.

## TL;DR

1. **Layer 1 emits both `raw` and `canonical` views.** Raw is never deleted.
2. **Canonical is the lowest common denominator across 5 countries.** Country-unique concepts (経常利益, 月營收, etc.) live in `*_specific` extension blocks alongside canonical.
3. **Layer 2 skills (`analysis-*`) read canonical only.** They MUST NOT touch raw blocks or country-specific extensions.
4. **Cross-layer contract is the success criterion.** A new pack output is "done" when `tests/integration/test_cross_layer_chains.py` for it turns green.
5. **Never lose information.** Canonical is a *view* of raw, enforceable by CI invariant.

---

## Why this contract exists

v2.0.0 split the toolkit into Data / Analysis / Report layers (see
[ADR-0001](adr/0001-data-analysis-report-layers.md)) but never wrote
the Layer 1 → Layer 2 contract. Result: 4 of 5 cross-layer chains were
broken on `main` after v2.0.1 — see
[`tests/integration/test_cross_layer_chains.py`](../tests/integration/test_cross_layer_chains.py)
+ [ADR-0002](adr/0002-layer-1-staging-tier-normalization.md) for the
incident postmortem.

This document is the codified contract so it does not happen again.

---

## The Three-Tier Staging Model

Every pack output type goes into exactly one of three tiers. Tier
determines normalization effort and risk.

### Tier 1 — Canonical primitives

**Criterion**: 5 countries have the same concept AND the row shape is
mechanical (no domain knowledge needed to transform).

**Examples**:

- **OHLCV price series**: `[{date, open, high, low, close, volume}]` — every country has it via yfinance. Lowercase keys, ISO-8601 dates, float numerics. Trivial mechanical transform.
- **Multiples (PE / PB / PS / EV/EBITDA / market cap)**: every country has yfinance `info` snapshot. Same key names across countries.

**Cost**: ~5 lines per `pack.py`, no schema bump (pack schemas have
`additionalProperties: true`).

**Where to emit**: top level of pack output, alongside existing raw.

### Tier 2 — Canonical structured

**Criterion**: 5 countries have the same *primitive* row shape (e.g.
`{date, value}`) but the available indicators differ per country, and
the upstream wrapping is country-specific.

**Examples**:

- **Macro time series**: every country emits `{date, value}` rows but
  the wrappers differ — FRED groups (US), BOJ tankan (JP), CBC presets
  (TW), ECOS keystat (KR), NBS new-SPA (CN). Canonical = a flat
  `series: {indicator_id: [...]}` block alongside the existing nested
  `groups.{group}.series` raw.

**Cost**: ~20 lines per `pack.py`, schema gets new optional top-level
key.

**Where to emit**: top level, parallel to raw nested structure.

### Tier 3 — Domain normalization

**Criterion**: 5 countries have the same *concept* (revenue, net income,
etc.) but the upstream representation requires domain knowledge to
transform — concept-name mapping, fiscal-year alignment, accounting-
standard awareness, multi-version handling.

**Examples**:

- **Financial statements**: `us-gaap:Revenues` ↔ `EDINET 売上高` ↔ `MOPS 營業收入` ↔ DART 영업수익 ↔ akshare 营业收入. Each requires a country-specific concept mapping table.

**Cost**: ~50–150 lines per country, ongoing maintenance as upstream
taxonomies evolve. Schema MUST bump (add `income_statement` etc. as
required top-level when ready).

**Where to emit**: top level. **Country-unique concepts (経常利益, 月營收, etc.)
go into a sibling `{country}_specific` block, NOT into canonical.**

> **Tier 3 requires an ADR** before implementation. Use existing ADRs
> in [`docs/adr/`](adr/) as a format reference.

---

## The Five Principles (lossless contract)

These are non-negotiable. Any pack output that violates these is broken,
even if its tests pass.

### Principle 1 — Raw is never deleted

The original upstream payload is preserved in a top-level raw block,
unchanged from what `*_client.py` returned. Never replace raw with
canonical. Never strip "redundant" fields.

```
sec_facts        # raw — full XBRL companyfacts (3000+ concepts)
edinet_xbrl      # raw — full iXBRL flatten
mops_raw         # raw — all 16 MOPS endpoints
```

Justification: raw is the audit trail. If a Layer 2 verdict is wrong,
the only reproducible answer to "where did this number come from?" is
the raw block. Removing raw breaks reproducibility.

### Principle 2 — Canonical is the lowest common denominator

Canonical contains only fields that all 5 countries can populate from
their primary source. If a concept exists in one country but not
another, it does NOT go into canonical.

```
✅ revenue, operating_income, net_income, total_assets, total_equity,
   cash_and_equivalents, shares_outstanding, current_price

❌ ordinary_income       — JP-only (経常利益)
❌ monthly_revenue       — TW-only (月營收)
❌ adjusted_eps_non_gaap — US-only (8-K narrative)
```

Justification: canonical is what cross-country `analysis-*` skills
consume. If `analysis-dcf` references `ordinary_income`, it stops
working for US/TW/KR/CN. Keep the canonical surface portable.

### Principle 3 — Country-specific extension blocks

Concepts that fail Principle 2 still belong in pack output, just in a
namespaced extension block:

```python
# data-jp memo-fetch output
{
    "ticker": "7203",

    "edinet_xbrl": {...},          # raw
    "income_statement": {...},      # canonical (5-country common)

    "jp_specific": {                # ← JP-only extension
        "ordinary_income":     [...],   # 経常利益
        "consolidated_basis":  "consolidated",
        "accounting_standard": "ifrs",  # or "jp_gaap" / "us_gaap"
        "tdnet_disclosures":   [...],
    }
}

# data-tw memo-fetch output
{
    "ticker": "2330.TW",

    "mops_raw": {...},              # raw
    "income_statement": {...},      # canonical (TIFRS)

    "tw_specific": {                # ← TW-only extension
        "monthly_revenue":      [...],   # 月營收
        "report_basis":         "consolidated",  # 母公司|合併
        "three_investor_flow":  {...},
        "margin_trading":       {...},
    }
}
```

Justification: these concepts are valuable for country-specific
analysis (a Japanese investor reading 経常利益; a Taiwanese investor
tracking 月營收). Hiding them only inside raw makes them
discoverability-poor. The named extension block makes them first-class.

Layer 2 skills SHOULD NOT read `*_specific` blocks. Country-specific
analysis is the responsibility of country-specific report orchestrators
or future country-specific analysis skills.

### Principle 4 — Mapping audit trail

Every canonical field carries provenance metadata pointing back to its
raw source:

```json
{
  "income_statement": {
    "revenue": [394328, 383285, 365817],
    "_meta": {
      "revenue": {
        "source_concept":      "us-gaap:Revenues",
        "fallback_used":       false,
        "fiscal_year_ends":    ["2024-09-28", "2023-09-30", "2022-09-24"],
        "amendments_seen":     [],
        "accounting_standard": "us_gaap"
      }
    }
  }
}
```

Required `_meta` fields for Tier 3 normalize:

| Field | Purpose |
|---|---|
| `source_concept` | Which raw concept name was used (e.g. `us-gaap:Revenues`) |
| `fallback_used` | True if the primary concept was empty, fell back to alias |
| `fiscal_year_ends` | Aligns canonical periods with raw filings; surfaces FY-mismatch debugging |
| `amendments_seen` | List of restated periods (e.g. `["FY2022 — restated 2024-04-12"]`) |
| `accounting_standard` | `us_gaap` / `ifrs` / `jp_gaap` / `tifrs` / `cas` etc. |

For Tier 1 / Tier 2, `_meta` is optional but recommended (e.g. note
which yfinance period the OHLCV came from).

### Principle 5 — Lossless invariant CI test

Every canonical field MUST be derivable from a raw field. CI enforces
this via an integration test:

```python
def test_canonical_revenue_matches_raw_for_us():
    pack = json.loads(Path("fixtures/data-us-memo-fetch-sample.json").read_text())
    canonical_rev = pack["income_statement"]["revenue"][0]
    source_concept = pack["income_statement"]["_meta"]["revenue"]["source_concept"]
    raw_rev = pack["sec_facts"]["facts"]["us-gaap"][source_concept]["units"]["USD"][0]["val"]
    assert canonical_rev == raw_rev, "canonical drifted from raw — normalize bug"
```

This test catches: typos in mapping table; arithmetic drift; canonical
fabricating data not present in raw.

If canonical CANNOT be derived from raw (e.g. requires inter-period
arithmetic), it is NOT staging — it is analysis, and belongs in
`analysis-*`, not `data-*`.

---

## Anti-Patterns (PR rejection rules)

The following are grounds for rejection at code review, even if all
tests pass:

### A. "Just delete the raw block, canonical has everything"

No. Raw is the audit trail. See Principle 1.

### B. Adding country-unique concepts to canonical

`income_statement.ordinary_income` (JP 経常利益) — wrong. Goes in
`jp_specific`. See Principle 2.

### C. Computing in normalize step

```python
# WRONG — this is analysis, not staging
canonical["revenue_growth_yoy"] = (rev[0] - rev[1]) / rev[1]
```

If the field requires inter-period arithmetic, ratios, derivatives, or
domain judgement (e.g. "when SBC > 5% of rev, exclude from EBITDA"), it
belongs in `analysis-*`. Staging is mapping + cast + rename only.

### D. Layer 2 reading raw

```python
# WRONG — analysis-dcf reading sec_facts directly
revenue = pack["sec_facts"]["facts"]["us-gaap"]["Revenues"]["units"]["USD"]
```

Forces analysis-dcf to know about XBRL concepts → couples DCF to US.
Read canonical `pack["income_statement"]["revenue"]` instead. If
canonical does not have what you need, the fix is to extend the
canonical contract (with ADR), not to bypass it.

### E. Adapter inside Layer 2

```python
# WRONG — ta_compute fixing pack shape mismatch internally
rows = pack.get("history") or pack.get("data") or pack["price_history"]["data"]
```

If Layer 1 emit shape is wrong, fix Layer 1. Layer 2 must read clean
canonical. Tolerating multiple shapes inside Layer 2 fragments the
contract and pushes the failure mode silent.

### F. Lossy transform without audit trail

Mapping `us-gaap:Revenues OR us-gaap:RevenueFromContract...` to
canonical `revenue` without logging which one was used in `_meta` →
downstream can never reproduce. See Principle 4.

---

## Decision Tree — adding a new pack output type

```
Q1. Do all 5 countries have this concept available from their primary source?
    │
    ├── No  → Country-specific only. Goes in {country}_specific. Done.
    │
    └── Yes → Q2. Is the row-level shape identical across countries (no transform needed)?
              │
              ├── Yes → Tier 1 (canonical primitive). Top-level alias. ~5 lines/pack.
              │
              └── No  → Q3. Is the per-row shape mechanical (date+value, no domain knowledge)?
                        │
                        ├── Yes → Tier 2 (canonical structured). Flatten + alias. ~20 lines/pack.
                        │
                        └── No  → Tier 3. Requires ADR. ~50–150 lines/pack with mapping table.
```

---

## PR Checklist for new Layer 1 normalization

For every PR that adds or modifies a canonical field:

- [ ] **Tier classified** (T1 / T2 / T3) per decision tree above
- [ ] **Raw block preserved** unchanged (Principle 1)
- [ ] **Canonical is 5-country common** OR concept lives in `{country}_specific` (Principle 2 / 3)
- [ ] **`_meta` provenance present** for T3 (Principle 4)
- [ ] **Lossless invariant test added** (Principle 5)
- [ ] **Cross-layer integration test** in `tests/integration/test_cross_layer_chains.py` turns green
- [ ] **No computation in normalize** — pure rename / cast / lookup only (Anti-pattern C)
- [ ] **No Layer 2 changes** unless an analysis script genuinely lacks logic (Anti-pattern D / E)
- [ ] **T3 only**: ADR added under `docs/adr/` documenting the per-country mapping decisions

---

## Worked example — Tier 1 (OHLCV)

```python
# data-us/scripts/pack.py — pack_snapshot()

def pack_snapshot(ticker: str) -> dict:
    info    = run_client(YF, ["--ticker", ticker, "--action", "info"])
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    return {
        "pack":          "snapshot",
        "ticker":        ticker.upper(),
        "fetched_at":    iso_now(),

        # === Raw (unchanged from upstream) ===
        "company_info":  info,
        "price_history": history,         # ← yfinance native: {period, rows, data: [...]}

        # === Canonical Tier 1 alias ===
        "history":       history.get("data", []),  # ← top-level, what ta_compute reads
    }
```

**Lossless invariant**: `pack["history"] is pack["price_history"]["data"]` — they reference the same list, never copies. CI test asserts this identity.

---

## See also

- [ADR-0001](adr/0001-data-analysis-report-layers.md) — original three-layer split
- [ADR-0002](adr/0002-layer-1-staging-tier-normalization.md) — staging-tier decision + 4-broken-chain postmortem
- [`design-principles.md`](design-principles.md) — empirical-first design rule (sister doc)
- [`tests/integration/test_cross_layer_chains.py`](../tests/integration/test_cross_layer_chains.py) — the cross-layer red-light test suite
- dbt staging pattern: <https://docs.getdbt.com/best-practices/how-we-structure/2-staging>
