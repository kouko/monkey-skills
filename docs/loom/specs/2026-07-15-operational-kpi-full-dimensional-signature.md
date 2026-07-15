# Brief — operational-kpi: full dimensional-signature extraction + binding

Status: brainstorming output, awaiting sign-off → `writing-plans`. User: "正式實作"
(formal build); confirmed no more breadth-sampling needed (4 assumption-probes validated
the design + fail-loud covers the tail).
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), the slice AFTER the
tier-② pilot. Builds on the shipped pilot (feat-operational-kpi-xbrl-pilot, investing-toolkit
2.19.0, closed out locally/unpushed). Prior brief: docs/loom/specs/2026-07-14-operational-kpi-companyfacts-pilot.md.

## Design-side on-ramp

Axis 0: brownfield increment on shipped, specced capability. No new design-side station.
Empirical grounding: the shipped pilot + a 23-company case survey + 4 targeted assumption-probes
(all live SEC XBRL) — baked into Current State Evidence + the case taxonomy below.

## Problem

**Job:** *When I point the toolkit at ANY US filer (not just a clean single-dimension company
like Apple), I want its own company-specific operating KPIs — product-line, segment, or
geographic revenue — pulled as a CORRECT one-value-per-period trend, no matter how its filing
tags dimensions; and when the tool meets a situation it can't unambiguously resolve, it must
FAIL LOUD (a review-item), never silently pick a wrong number.*

The pilot proved the chain on Apple, whose iPhone revenue is single-dimensioned. Live-testing
other companies (NFLX, MSFT, JPM, + a 23-company survey) showed Apple is the EASY case: most
large filers tag revenue across MULTIPLE axes on one fact, and the pilot's "one fact = one axis
member" model CONFLATES a total with its slices (NFLX StreamingMember matched the $45B total AND
each ~$5-20B regional slice → 15 points where 3 were meant). This slice makes the extraction
correct across the real-world taxonomy.

## Users

**Job story:** *When I bind a KPI like "Netflix streaming revenue" I want exactly the total
(one value per year), and when I bind "Netflix streaming in US & Canada" I want that slice — the
tool must tell the two apart from the filing's dimensional tags; and for a company/situation it
hasn't seen, I want a loud refusal, not a plausible-looking wrong trend.*

Consumer: the equity-memo pipeline (a TRUSTED memo feed of filing-native KPI trends), now for
any US filer, not only single-dimension ones.

## Smallest End State

Upgrade the pilot's data model from "one fact = one axis member" to **"one fact = its FULL
dimensional signature"**, and match bindings on that signature. Concretely:

1. **Full-signature fact-pack** (`sec_edgar_client.extract_dimensional_revenue`): each emitted
   fact carries a `dimensions` map — ALL real-breakdown axis→member pairs on that fact
   (ProductOrService / StatementBusinessSegments / StatementGeographical / Subsegments) — NOT a
   single `{axis, member}`. `srt:ConsolidationItemsAxis` is captured SEPARATELY as a
   reconciliation QUALIFIER (its member, e.g. OperatingSegments vs eliminations), never as a
   breakdown axis — it is the "which view" tag, not a second cut.
2. **Signature-based binding match** (`kpi_xbrl.resolve_binding`): a source specifies
   `{concept, dimensions: {axis: member, ...}}` and matches a fact whose real-breakdown
   `dimensions` EXACTLY equal that map (empty map = the top-level total for that concept). This
   disambiguates NFLX `{ProductOrService: Streaming}` (total, $45.18B) from
   `{ProductOrService: Streaming, StatementGeographical: US&Canada}` (slice, $19.96B) —
   VERIFIED live: one value per (signature, period).
3. **ConsolidationItems handling**: for the segment-view companies (AAPL/JPM/BAC/WMT/COST/NVDA/
   DAL), a binding resolves against the OperatingSegments view and never double-counts the
   eliminations/reconciliation members — the qualifier is matched or defaulted explicitly, not
   conflated into the signature.
4. **Concept hygiene** (`_is_revenue_concept`): EXCLUDE deferred-revenue / contract-liability
   reconciliation concepts (`ContractWithCustomerLiabilityRevenue*`) that merely CONTAIN
   "Revenue" but are NOT operating revenue (found via CMG/TXRH). Keep the real revenue concepts
   (RevenueFromContract… / SalesRevenueNet / Revenues / RevenuesNetOfInterestExpense[…] /
   AdvertisingRevenue). A binding still NAMES its concept; the extractor just must not pollute.
5. **Form filter**: `extract_dimensional_revenue` must extract from an EXACT `10-K` (not a
   `10-K/A` amendment — TSLA's `.latest()` returned a 0-dimensional 10-K/A).
6. **ANTI-FABRICATION (the core, unchanged in spirit, extended to signatures)**: a bound
   signature matching >1 value for a `(signature, period)` RAISES; an unmatched signature is
   skipped (never defaulted). So an UNSEEN dimensional situation surfaces as a loud failure /
   review-item, never a fabricated number.

**Composes with the pilot's era-binding + declared-break machinery**: an era source is now a
full signature (probe B confirmed old-era Google is ALSO cross-dim, with a different concept
`AdvertisingRevenue` + different members) — the declared-break / dual-series stays as-is.

**Explicitly NOT in this slice:** multi-filing historical fetch (the ~16-year live history — a
separate follow-up; a single 10-K still yields ~3 years); LLM-locate; non-XBRL narrative KPIs
(units/subscribers — tier-③); non-US (20-F) filers; auto-DISCOVERING a company's bindings (the
binding is still authored/config; auto-proposal is later); a fiscal-calendar map for
start-year-named fiscal years (probe A confirmed period_end[:4] is correct for US end-year-named
FYs — the theoretical start-year-named case is deferred, and would fail loud if it mis-slotted).

## Current State Evidence

- **Forward (consumer):** `kpi_memo_feed.build_memo_feed` bundles a TRUSTED feed's kpi_series
  verbatim; a conflated series (15 points where 3 were meant) would ship a wrong trend — this
  slice fixes it upstream at extraction+binding.
- **Reverse (what exists):** `sec_edgar_client.extract_dimensional_revenue` (sec_edgar_client.py:1924)
  currently flattens each fact to ONE axis/member via `_is_dimensional_revenue_fact`
  (:1869) + `_build_dimensional_revenue_fact` (:1885) — the single-member model this slice
  replaces. `kpi_xbrl.resolve_binding` matches `concept+axis+member` (single). `_is_revenue_concept`
  (:1845) is a bare substring `"Revenue" in concept` — the pollution source. Extraction uses
  `filings.latest()` (:1962) with no exact-form guard — the amendment source.
- **Error (fail-loud):** the pilot already RAISES on an ambiguous binding (`resolve_binding` >1
  source match) and a missing period_end/value/provenance — this slice EXTENDS the same posture
  to signatures (>1 value per bound signature+period → RAISE).
- **Data (live-verified taxonomy, 23 companies + 4 probes):**
  - CLEAN single-dim (MSFT/AMZN/GS/V/MA); CONSOLIDATION-qualified (~7 incl. AAPL/JPM/BAC/WMT/
    COST/NVDA/DAL — real axis + ConsolidationItems reconciliation qualifier); GENUINELY cross-dim
    (~10 incl. GOOGL/META/NFLX/DIS/F/JNJ/UNH/XOM/VZ/HD — 2-3 real breakdown axes on one fact);
    AMENDMENT (TSLA 10-K/A); CONCEPT POLLUTION (CMG/TXRH ContractWithCustomerLiabilityRevenue*).
  - NFLX signature disambiguation VERIFIED: `{ProductOrService:Streaming}`=total 45.18B vs
    `{Streaming, Geographical:US&Canada}`=19.96B, one value per full signature+period, all
    duration, no instant pollution. Revenue concept varies by industry (banks
    RevenuesNetOfInterestExpense[FullTaxEquivalentBasis]; media/retail Revenues; old-era Google
    AdvertisingRevenue). period_end[:4] fiscal labeling verified correct for WMT (Jan) + COST (Sept).
- **Boundary:** ConsolidationItemsAxis is the one axis that is a QUALIFIER not a breakdown — the
  code must special-case it (the recorded whitespace/identity-guard discipline generalizes: a
  guard must encode the real property, here "real breakdown axes only").

Evidence paths: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`,
`investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py`, the 4 probe JSONs (discover_cases,
validate_full, probe_assumptions) + the pilot fixture/tests.

## Decision

Upgrade the fact-pack to carry each fact's FULL real-breakdown dimensional signature (with
ConsolidationItems as a separate reconciliation qualifier), match bindings on the exact
signature (empty = total), exclude deferred-revenue/contract-liability pollution from the revenue
concept filter, and extract only from an exact 10-K. Keep the anti-fabrication posture: an
ambiguous (>1-value) bound signature RAISES, an unmatched one is skipped — unseen situations fail
loud, never fabricate. This one data-model change resolves the whole live taxonomy; the pilot's
era-binding + declared-break machinery composes unchanged (era sources become full signatures).

**We will NOT:** pick-first / pick-largest on ambiguity (fabrication); treat ConsolidationItems
as a breakdown; multi-filing historical fetch; LLM-locate; non-US; auto-propose bindings; build a
start-year fiscal-calendar map.

## Alternatives Considered

- **Disambiguating multi-dimensional facts** — (a) match on the FULL dimensional signature
  **[chosen]**; (b) pick-first / pick-largest member (rejected — this IS what the single-member
  model did, and it fabricated NFLX's conflation); (c) skip any multi-dim fact (rejected — throws
  away the genuinely-wanted slices AND the cross-dim totals). Grounded in the XBRL dimensional
  model itself: a fact's identity IS its full context (concept + all dimension members), so
  keying a KPI by the full signature is the only faithful disambiguation — and the anti-fabrication
  intent forces fail-loud over guess. (No external library fork; this is a data-model decision the
  live probes determined, not an industry-tool choice.)
- **ConsolidationItemsAxis** — treat as a breakdown (rejected — inflates every segment company to
  false cross-dim, verified across AAPL/JPM/BAC/WMT/COST) vs a reconciliation qualifier **[chosen]**.

## What Becomes Obsolete

The pilot's single-`{axis, member}` fact representation and the single-member `resolve_binding`
match are replaced by the full-signature model IN THE SAME CHANGE (the pilot's iphone_revenue
binding is rewritten as a full signature `{ProductOrService: iPhone}`). The bare-substring
`_is_revenue_concept` is tightened. No dead code left behind.

## Out of Scope

- Multi-filing historical fetch; LLM-locate; narrative/non-XBRL KPIs; non-US filers; binding
  auto-proposal; start-year fiscal-calendar map; XBRL cross-check (analysis-xval already ships);
  archiving.

## Open Questions

1. **ConsolidationItems default view** — when a binding doesn't specify the qualifier, default to
   the OperatingSegments member (the standard segment view) and fail loud if both an
   operating-segments value AND a reconciled/total value match? Default: yes — bind to the
   operating-segments view, RAISE on ambiguity. Confirm in plan.
2. **Signature match: exact vs subset** — a binding's `dimensions` must match a fact's real-
   breakdown dimensions EXACTLY (an empty binding map matches only the top-level total, NOT any
   slice). Default: exact-match (this is what de-conflates NFLX). Confirm in plan.
