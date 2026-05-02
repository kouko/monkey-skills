# ADR-0002: Layer 1 Staging-Tier Normalization

- **Status**: Accepted
- **Date**: 2026-05-02
- **Version target**: investing-toolkit v2.0.2 (PR series #177–#180)
- **Supersedes**: implicit "Layer 1 emits whatever upstream gives" assumption from v2.0.0
- **Contract reference**: [`docs/normalization-contract.md`](../normalization-contract.md)

## Context

[ADR-0001](0001-data-analysis-report-layers.md) split the toolkit into Data / Analysis / Report layers in v2.0.0 (2026-04-30). The split defined layer responsibilities (I/O / pure-compute / orchestration) but **never wrote the cross-layer data contract**. Each `data-*/scripts/pack.py` emitted whatever shape the upstream client returned; each `analysis-*/scripts/*_compute.py` defined its own input expectation in SKILL.md.

v2.0.1 (2026-05-02) added 30 JSON Schemas for `data-*` outputs. The schemas validated each Layer 1 emission against its own self-described shape — but did not validate that Layer 1 emissions match Layer 2 input expectations. This was a half-truth contract (single-side schema) that gave false confidence.

Two months after the v2.0.0 split landed, a smoke test of the three layers end-to-end revealed that **4 of 5 cross-layer chains were broken on `main`**:

| # | Chain | Failure mode |
|---|---|---|
| 1 | `data-us snapshot` → `analysis-technical` | Crash: `No OHLCV rows in input` |
| 2 | `data-us memo-fetch` → `analysis-dcf` | Crash: `missing income_statement.revenue` |
| 3 | `data-us comps-multiples` → `analysis-comps` | **Silent**: all multiples → None, composite scores garbage |
| 4 | `data-us screener-batch` → `analysis-screener` | Working |
| 5 | `data-us regime-pack` → `analysis-macro-regime` | **Silent**: all indicators → "flat" default, real_rates → None |

Detail at [`tests/integration/test_cross_layer_chains.py`](../../tests/integration/test_cross_layer_chains.py) (PR #176).

3 of 4 broken chains failed silently — Layer 2 produced well-formed JSON with semantically empty content. `report-equity-memo/SKILL.md` instructs the orchestrator to feed memo-fetch directly to dcf_compute; this chain was broken from v2.0.0 ship date with no end-to-end test catching it.

## Why the prior architecture failed

Two independent reasons:

1. **Wrong abstraction boundary for schema**. Schema was placed at Layer 1's emission boundary (validates "pack.py output matches its own schema"). The meaningful contract is at the Layer 1 → Layer 2 chain handoff. Schema correctness ≠ chain correctness.

2. **Asymmetric concept naming**. Each `analysis-*` script invented its own input field names independently of what `data-*` packs emit:

   ```
   ta_compute      reads  pack.history / pack.data           (top-level)
   data-us snapshot emits pack.price_history.data            (nested) → ✗

   dcf_compute             reads  pack.income_statement (flat)
   data-us memo-fetch      emits  pack.sec_facts (raw XBRL)  → ✗

   comps_compute           reads  pack.info[ticker]
   data-us comps-multiples emits  pack.tickers[ticker]       → ✗

   regime_compose          reads  pack.series (flat)
   data-us regime-pack     emits  pack.groups.{*}.series     → ✗
   ```

   No mechanism enforced alignment. Each side evolved independently. Three of four chains were never end-to-end tested before merge.

## Considered Alternatives

### Alternative A — Layer 2 input adapters (per-script)

Each `analysis-*` script tolerates multiple upstream shapes via internal adapter (`pack.get("history") or pack.get("data") or pack["price_history"]["data"]`).

**Pros**: smallest blast radius (5 scripts), no schema bump, prior art in `analysis-portfolio` (multi-shape input tolerance).

**Cons**:
- Couples each Layer 2 script to country-specific Layer 1 quirks (analysis-dcf needs to know about US XBRL concept names) → breaks the v2.0.0 promise that Layer 2 is country-agnostic pure compute
- Fragments the contract across multiple files; impossible to view canonically
- Information loss is silent (already 3 of 4 broken chains failed silently — adapter approach makes this MORE common, not less)
- Future analysis-* skills must re-implement adapter for each upstream shape

### Alternative B — Layer 1 staging-tier normalization (chosen)

Layer 1 emits both `raw` and `canonical` views. Canonical is the lowest common denominator across 5 countries; country-unique concepts live in `{country}_specific` extension blocks.

**Pros**:
- Layer 2 stays clean (zero adapter cruft, zero country-specific logic)
- Future analysis-* skills get canonical for free
- Cross-country symmetry — `analysis-dcf` reads same shape regardless of US/JP/TW/KR/CN
- Aligns with industry-standard dbt staging-tier pattern (proven across thousands of analytics shops)
- Information loss prevention is a contract (Principle 5 — lossless invariant CI test)

**Cons**:
- More work (touch 5 countries × multiple pack types)
- Layer 1 packs grow longer
- Tier 3 (financial statements) requires per-country concept mapping with ongoing maintenance

### Alternative C — Introduce a Layer 1.5 normalization layer (rejected)

Add new `normalize-{country}/` skills between data and analysis.

**Pros**: clean separation; staging logic in own location.

**Cons**: 25 new skill directories (5 country × 5 pack); over-engineered for current scale; YAGNI violation; adds orchestration complexity for marginal gain over Alternative B.

### Alternative D — LLM as runtime adapter (rejected)

Have the orchestrating LLM transform Layer 1 output into Layer 2 input shape on-the-fly via tool-call argument generation.

**Cons**:
- Non-deterministic — same input produces different output across runs, destroying reproducibility
- Token cost per cross-layer call (memo-fetch can be 100KB; LLM can't afford to re-emit it)
- Hallucination risk in math-heavy domain (financial numbers must be exact)
- Industry literature ([_Why Multi-Agent LLM Systems Fail_](https://arxiv.org/html/2503.13657v3)) explicitly identifies this as a cascading-failure anti-pattern

This was never seriously on the table for production code — listed for completeness because the question came up in design discussion.

## Decision

Adopt **Alternative B: Layer 1 Staging-Tier Normalization**.

The contract is codified in [`docs/normalization-contract.md`](../normalization-contract.md). Summary:

- Pack outputs are tiered (T1 / T2 / T3) by transform complexity
- Raw blocks are NEVER deleted (`sec_facts`, `edinet_xbrl`, `mops_raw` etc.)
- Canonical is the 5-country lowest common denominator
- Country-unique concepts go in `{country}_specific` extension blocks
- T3 (domain transforms) require mapping audit trail in `_meta` and a lossless invariant CI test

Five principles enforce information preservation. See contract document.

## Phasing

Three implementation PRs, each gated by the corresponding cross-layer integration test turning green:

| PR | Tier | Scope | Effort | Success criterion |
|---|---|---|---|---|
| #177 | T1 | OHLCV + Multiples canonical aliases across 5 countries | ~1h | Chain 1 + Chain 3 green |
| #178 | T2 | Macro time series flattening across 5 countries | ~2h | Chain 5 green |
| #179 | T3 (ADR + impl) | Financial statement normalization (XBRL / EDINET / MOPS / DART / akshare → canonical income_statement / cash_flow / balance_sheet) | ~4h impl + per-country review | Chain 2 green |

PR #176 (already open as Draft) provides the red-lights test suite that PR #177 / #178 / #179 turn green incrementally.

## Consequences

### Positive

- Layer 2 skills become country-agnostic pure compute (the v2.0.0 promise, finally enforceable)
- Future analysis-* skills get canonical for free
- Information loss is a contract violation, not silent garbage
- Cross-layer integration test suite is the success criterion — no new normalization can land without a green chain test

### Negative

- Layer 1 packs grow longer (each country pack.py adds ~50–200 lines for Tier 3)
- Maintenance cost of per-country concept mapping tables (T3 only) — XBRL / iXBRL / TIFRS / K-IFRS / CAS taxonomies evolve over time
- Some redundancy in pack output (raw + canonical both present)

The redundancy is intentional and tracks dbt's `sources/` + `staging/` model. Storage cost is negligible (cache TTL handles it); maintainability gain dwarfs storage.

### Migration

`v2.0.1` → `v2.0.2` is **non-breaking** (canonical fields are added alongside raw via `additionalProperties: true` slot in existing schemas). Existing Layer 2 callers that happen to read raw blocks continue to work. New canonical reads are forward-compatible.

`v2.0.2` schemas SHOULD bump to make canonical fields `required` once the implementation is mature; this is a follow-up consideration, not a blocker for v2.0.2 itself.

## Open Questions (deferred)

1. **Layer 2 input schemas.** Should each `analysis-*/scripts/*_compute.py` ship its own input JSON Schema next to its output schema? Would enable producer/consumer compatibility tests (Confluent Schema Registry / dbt contract pattern). Deferred to a future ADR if v2.0.2 normalization proves stable.

2. **`_meta` provenance for Tier 1**. Required for Tier 3, optional for Tier 1/2. Should it become required across the board for uniformity? Trade-off: smaller pack output vs. uniform debuggability.

3. **Cross-country canonical for non-equity asset classes.** Future skills (bond / FX / commodity / crypto) will introduce new pack types. The contract's Tier 1/2/3 framework should generalise but the specific canonical fields will differ. Will be addressed in a future ADR when those skills land.

## See Also

- [ADR-0001](0001-data-analysis-report-layers.md) — three-layer split (the prior decision this builds on)
- [`docs/normalization-contract.md`](../normalization-contract.md) — the developer-facing contract (rules to follow)
- [`docs/design-principles.md`](../design-principles.md) — empirical-first design rule (sister meta-rule)
- [`tests/integration/test_cross_layer_chains.py`](../../tests/integration/test_cross_layer_chains.py) — the red-light test suite that motivated this ADR
- PR #176 — diagnostic PR exposing the 4 broken chains
- [_Why Multi-Agent LLM Systems Fail_](https://arxiv.org/html/2503.13657v3) — academic basis for rejecting Alternative D
- dbt staging-tier pattern — <https://docs.getdbt.com/best-practices/how-we-structure/2-staging>
