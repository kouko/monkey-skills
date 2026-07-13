# Brief — financial-table cross-validation (xval)

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer, capability 2 of 3 (financial-table-xval)
Change-folder: `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/financial-table-xval/spec.md`
(9 requirements, ~15 scenarios — the WHAT; this brief adds the WHERE + a
live-verified grounding correction the spec needs.)

## Design-side on-ramp

Axis 0: a validated change-folder already covers this capability (reception
row 3 needs no new spec). Brownfield increment to an existing toolkit.
Proceed direct to loom-code. The change-folder is the spec SSOT — this
brief LINKS to it and records one grounding conflict; it does NOT edit it
(loom-spec consumer discipline).

## Problem

**Job:** *When I trust a number in a company's financial statement, I want
it cross-checked against an independent source of the same fact, so a
mis-tag, a restatement, or a display-rounding artifact is surfaced to me
loudly instead of silently flowing into my valuation.*

A filing presents its numbers twice: once as the rendered statement table a
human reads, and once as machine-readable XBRL facts. They should agree. A
disagreement is either a filing error, a restatement, or a legitimate
rounding/scale artifact — and which one it is matters. Today nothing in the
toolkit compares them; the memo trusts whatever the data layer hands it.

## Users

**Job story:** *When the memo pipeline (or I, at the CLI) evaluate a US
company, I want a divergence report that pairs each doc-table cell with its
independent XBRL fact, classifies the gap (low/medium/high), and states
honestly which numbers had no independent counterpart — so I can weight or
challenge a number instead of taking it on faith.*

Consumer: the equity-memo pipeline (a future wire-in, like narrative) and
direct CLI use. Producer of trust signals the memo's citation gates
(CHK-CIT-007) can lean on.

## Smallest End State

A new `analysis-xval` skill (SKILL.md + `scripts/xval_compute.py` + a CLI),
following the `analysis-comps` template (pure-compute over pre-fetched data
paths, JSON report to stdout, recorded-fixture tests). It:

1. Takes the doc-table cells (Source A) and the companyfacts facts
   (Source B) as input paths, matches them by (concept, period, dimension),
   computes divergence, classifies into low/medium/high/n-a, and emits a
   report where every compared number carries BOTH citations and every
   unmatched cell is stated "doc-only, no XBRL counterpart" — never dropped,
   never fabricated.
2. Surfaces high-alert divergence prominently with both values intact
   (mirrors comps direct-vs-compute surfacing — never silently reconcile).

Fetching Source A (edgartools statement extraction — net-new) is part of
this arc; wiring xval into the memo pack is DEFERRED (same cut narrative
took — CLI/compute first, memo-wiring is a natural pair with the memo's
other slices). Late-vetoable.

## Current State Evidence

- **Reuse (comps divergence):** `skills/analysis-comps/scripts/comps_compute.py`
  — `_compute_divergence` (`:955`) + `_classify_divergence_alert` (`:946`)
  are pure and importable. Edge-case discipline to reuse verbatim: either
  side `None` -> `alert:"n/a"` with note; `direct==0` -> `pct_diff:None,
  alert:"n/a"`; both values always retained. **BUT the alert BANDS differ:**
  comps uses low <=5% / med <=15% / high >15% (`DIVERGENCE_BAND_LOW=0.05`,
  `DIVERGENCE_BAND_HIGH=0.15`, `:67-68`); the xval spec mandates low ~1% /
  med 1-5% / high >5% (spec :68-73). So xval reuses the DIFF MATH + the
  n/a-never-drop discipline, but carries its OWN band constants (1%/5%) —
  do not import comps' bands.

- **Source A — doc-table XBRL statement extraction: ABSENT.**
  `skills/data-markets/scripts/sec_edgar_client.py` uses edgartools only for
  filing acquisition + item/narrative segmentation (`:824`, `:984`); there
  is NO `.financials` / `.balance_sheet` / statement-dataframe extraction
  anywhere. The doc-table side (concept, period, dimension, value, scale,
  decimals + cell citation) is net-new — via edgartools' financials/XBRL
  statement API.

- **Source B — companyfacts: present, but metadata-poor (LIVE-VERIFIED).**
  `fetch_facts(cik, concept)` (`sec_edgar_client.py:237`) preserves raw SEC
  JSON under `data`. `summarize_concept` (`:269`) flattens to
  `start,end,val,accn,form,fy,fp,filed`. **Live probe 2026-07-13 against the
  real companyconcept API (AAPL Revenue, all 113 facts):** the API carries
  ONLY `accn,end,start,val,fy,fp,form,filed,frame`. It has **no `scale`, no
  `decimals`/`precision`, no `dimension`/`segment`** — and `val` is already
  the full-precision integer (`229234000000`, not a display-rounded value).

- **Where it lives:** six `analysis-*` skills; none is a validation/xval
  skill -> this is a NEW `analysis-xval`. Template = analysis-comps: argparse
  CLI reading data-pack JSON path(s), `json.dump` to stdout, exit 2 on bad
  arg combos.

- **Tests:** `tests/analysis/` with `conftest.py`'s `run_script()`
  subprocess runner + `fixtures_dir`; recorded JSON fixtures, no live calls;
  live tests segregated into `*_live.py`. Mirror this.

## Decision

Build `analysis-xval` as a pure-compute skill mirroring analysis-comps,
reusing comps' divergence diff-math + n/a-never-drop discipline (with xval's
own 1%/5% bands), plus a net-new edgartools statement-extraction step for
the doc-table side.

**Source model — the HYBRID (user decision, 2026-07-13), reconciling the
spec's grounding error:** the spec's Requirement "companyfacts source
carries scale and decimals metadata" (change-folder spec :35-40) is
**factually wrong** — live verification shows the companyfacts API carries
none of scale/decimals/dimension. So:

- **Plain consolidated line items** (non-dimensional concept+period, e.g.
  Revenues, NetIncomeLoss, Assets) -> genuine TWO-SOURCE cross-validation:
  doc-table cell vs the independent companyfacts fact. This is the
  highest-value, genuinely-independent check and the core of the skill.
- **The 3 metadata-dependent requirements** — scale/rounding recognition
  (spec :92-104), DQC 2.4.1 decimal-disagreement (spec :119-143), and
  dimensional/segment matching (spec :53-59) — cannot be cross-validated
  against companyfacts (the metadata isn't there). They become
  **single-source STRUCTURAL checks against the doc-table's own iXBRL tags**
  (Source A carries scale/decimals/dimension from the raw instance). The
  report MUST LABEL each finding as two-source (doc-vs-companyfacts) or
  single-source (structural iXBRL check) — honesty about which guarantee is
  which is load-bearing, per the spec's own single-source-honesty
  requirement (:158-178).
- A dimensional doc cell has no companyfacts counterpart (companyfacts is
  consolidated-only) -> recorded "doc-only, no XBRL counterpart" on the
  two-source axis, while its dimension agreement is checked single-source on
  the iXBRL side. This is not a gap papered over — it is stated.

REJECTED: (2) both sources from the same filing's raw iXBRL — satisfies all
9 requirements but the two "sources" are one filing's rendered-vs-tagged
views, weaker independence (cannot catch a filing-level error). (3) send the
spec back to loom-spec first — correct in principle but the hybrid captures
the spec's INTENT faithfully while being honest about the API reality;
recorded here rather than round-tripping. **The change-folder spec scenario
at :35-40 is left untouched (consumer discipline) but is noted as
superseded-by-reality here; archiving the folder later should carry this
correction.**

**We will NOT:** fabricate any value (parser emits the number, never an
LLM — the arc's anti-fabrication invariant); match by table position, row
label, or label similarity (concept+period+dimension triple only); force a
non-GAAP/adjusted metric onto a GAAP tag; silently reconcile a high alert
(both values retained side by side).

## Alternatives Considered

The source-model fork (hybrid / all-iXBRL / re-spec) is recorded under
Decision with each rejection reason. No separate Axis-4 industry search was
run: the design is pinned by the spec + the live API reality, not by a
choice among shipped libraries (edgartools is already the arc's committed
XBRL tool).

## What Becomes Obsolete

- Nothing removed. This is additive (a new skill). If a future memo-wiring
  slice consumes xval, it may retire any ad-hoc "trust the number" comment
  in the memo seed contract — out of scope here.
- The change-folder's companyfacts-carries-scale/decimals scenario is
  factually obsolete (noted above); its correction rides this brief until
  the folder is re-cut or archived.

## Out of Scope

- `operational-kpi` (capability 3) — untouched, still blocked on user-domain
  decisions.
- Wiring xval into `pack_memo_fetch` / the memo seed contract — deferred to
  a follow-up slice (CLI/compute skill first).
- Non-US markets (companyfacts + edgartools statements are SEC-only).
- Editing the change-folder spec (consumer discipline — loom-spec owns it).
- Archiving the change-folder (2 of 3 capabilities still unshipped after
  this one).

## Grounding — RESOLVED by live probe (AAPL 10-K accn 0000320193-25-000079, edgartools 5.42.0, 2026-07-13)

Open Question 1 is settled; the hybrid is confirmed FEASIBLE. The working
spine for Source A:

- **Rendered doc-table rows:** `filing.xbrl().get_statement("BalanceSheet")`
  → `list` of row-dicts; raises **`StatementNotFound`** on an absent/
  unrecognized statement (satisfies the loud-extraction-failure requirement,
  spec :15-20). `xbrl.statements.balance_sheet()` also works.
- **Per-cell fact graph:** `filing.xbrl().facts.to_dataframe()` (1044×55) /
  `.get_facts()` (list of dicts). Each fact carries: `concept`
  (`us-gaap:Assets`), `period_type`/`period_instant`/`period_start`/`period_end`,
  `is_dimensioned` + `dimension` + `member` (+ `dim_*Axis` cols), `value`
  (str) + `numeric_value` (float), **`decimals`** (`"-6"`), and citation
  (`statement_type`, `statement_role`, `label`, `context_ref`, `fact_id`).
- **Dimensional facts ARE reachable** — real segment revenue pulled (iPhone
  `209586M` under `srt:ProductOrServiceAxis` member `aapl:IPhoneMember`),
  also `get_facts_with_dimensions()`. So dimensional matching is buildable.
- **DEAD traps (do NOT build on them):** `filing.xbrl().instance` and
  `Company("AAPL").financials` (returns `None`) — both NOT-EXPOSED on 5.42.0.

**Design refinement forced by the probe — `scale` is not a separate field.**
edgartools normalizes the value to full magnitude and keeps only `decimals`
(the raw iXBRL `scale` attribute is not preserved as its own field; the
`FactQuery.scale()` method is a display transform, not the source scale). And
`numeric_value` is already a full-magnitude integer, exactly like
companyfacts' `val`. Consequence for the scale/rounding requirement (spec
:92-104): a two-source diff of two full-magnitude values is naturally
near-zero, so "scale/rounding" is NOT that diff. It is a Source-A-internal
check: the doc-table's DISPLAYED (rendered, rounded) value vs the
full-magnitude fact, using `decimals` to know the rounding grain — a
single-source structural check, consistent with the hybrid. The plan must
model the scale/rounding + DQC-2.4.1 checks off `decimals` + the rendered
value, never off a nonexistent `scale` field.

## Open Questions

1. ~~edgartools statement API surface~~ — **RESOLVED above.**
2. **Restatement-signal source** — the spec's restatement check (:119-136)
   compares a period's comparative figure across two filings. Both filings'
   facts are in companyfacts (keyed by `accn`), so this is companyfacts-only
   and does not need Source A — confirm the accession keying at plan time.
