# Proposal — operational-kpi quarterly (scope B)

**Change-id:** 2026-07-16-operational-kpi-quarterly
**Seed:** add quarterly (10-Q) support to the SEC XBRL multi-filing operational-KPI
capability; extend the annual-only period-identity model to sub-annual periods.
**Governance:** ⚠️ **UNGOVERNED** — no `docs/loom/PRINCIPLES.md` in this repo. Expansion
proceeds with this explicit caveat (Rule 12 fail-loud); scope boundary and NFR posture are
taken from the scope-A brief (`docs/loom/specs/2026-07-15-multi-filing-historical-fetch.md`)
and the durable memory constraints, not a product constitution.
**Coverage statement:** coverage relative to seed + 6 lenses; blind spots listed in the
final section (NOT a completeness claim).

**Domain note:** this is a data-transformation pipeline, not a UI journey. The USM/OOUX
lenses are adapted honestly: "actors" = the calling analysis/agent layer + the data layer;
"objects" = the domain data records; the journey is the fetch→classify→identify→dedup→
stitch pipeline. Per §single-surface collapse, the linear journey is short; the structure
lives in the object state machines + the period-classification matrix.

## USM backbone

The happy-path spine (Phase ①), one ordered pipeline (nodes = stages; typed nav edges in
§Journey navigation):

| # | Stage | Actor | What happens | prov |
|---|---|---|---|---|
| 1 | Request | analysis/agent layer | asks for a company's KPI series at a granularity (annual \| quarterly) | seeded |
| 2 | Fetch | data layer | fetches the in-range filings (10-K for annual, 10-K+10-Q for quarterly) — reuses scope-A multi-filing fetch | seeded |
| 3 | Extract + duration | data layer | per fact, emits its dimensional signature AND its period DURATION (context span in months) | seeded |
| 4 | Classify | analysis layer | maps (duration, period_end, fiscal-calendar) → a `period_type` (Q1/Q2/Q3/Q4/FY) + a cumulative flag (single-quarter vs YTD) | seeded |
| 5 | Identify + dedup | analysis layer | keys each fact on (signature, period_type, duration-class, fiscal-year); de-conflates single-quarter from YTD; applies scope-A restatement policy C | seeded |
| 6 | Derive (optional) | analysis layer | derives Q4 = FY − 9mo-YTD where Q4 is untagged, flags it as computed | seeded |
| 7 | Stitch | analysis layer | builds a period-keyed series at ONE granularity; era-stitching within granularity | seeded |

**Single-surface collapse note:** stages 3–7 are a straight-line transform with no user
branching; the only real "navigation" is failure escapes (fail-loud skips). This is the
honest shape — not a degenerate one.

## OOUX object model

Objects the pipeline manipulates (Phase ②), each with its state machine. The objects share
state (Fact.duration feeds PeriodIdentity feeds SeriesPoint), so they are expanded as a
coherent set rather than fully-independent fan-out (the skill's fan-out precondition —
"disjoint objects, no shared state" — does not hold here; noted honestly).

### Object: XbrlFact  (prov: seeded)
- **Attributes:** concept, dimensions (full signature), consolidation, value, period_start,
  period_end, `duration_months` (NEW = months between start and end), accession, filed.
- **Relationships:** belongs-to a Filing; maps-to a PeriodIdentity.
- **CTAs:** extract, classify-duration.
- **States:** `raw` → `duration-derived` (start+end present, months computed) → `classified`
  (period_type assigned) → `keyed`. Terminal-reject: `instant-context` (no duration → not a
  flow, excluded), `malformed-period` (missing/invalid start or end → fail loud, never
  emitted).

### Object: PeriodIdentity  (prov: seeded)
- **Attributes:** period_type ∈ {Q1,Q2,Q3,Q4,FY}, duration_class ∈ {3mo, 6mo-YTD, 9mo-YTD,
  12mo-FY}, fiscal_year, cumulative? (bool).
- **Relationships:** derived-from an XbrlFact + the company FiscalCalendar.
- **CTAs:** classify, compare-for-dedup.
- **States:** `single-quarter` (3mo) | `ytd-cumulative` (6/9mo) | `annual` (12mo) | `derived`
  (Q4-by-subtraction). Legal: single-quarter and ytd-cumulative at the SAME period_end are
  DISTINCT identities (the core de-conflation).

### Object: FiscalCalendar  (prov: inferred)
- **Attributes:** fiscal-year-end month/day, quarter-end dates, 52/53-week? flag.
- **Relationships:** per-company; parameterizes PeriodIdentity classification.
- **CTAs:** quarter-of(period_end).
- **States:** `standard-Dec`, `non-Dec` (e.g. Apple Sept), `52-53-week`, `transition` (a
  fiscal-year change / stub period). Later three are edge sources.

### Object: SeriesPoint / Series  (prov: seeded)
- **Attributes:** period label (fiscal_year + period_type), value, granularity, dqc flags.
- **CTAs:** dedup, restatement-resolve (policy C), derive-Q4, stitch, break.
- **States:** `reported` | `deduped` | `restated (dqc)` | `derived (dqc)` | `broken/stitched`.
- **Invariant:** a Series carries ONE granularity; annual and quarterly are never silently
  mixed.

### Object: Filing  (prov: seeded, reused from scope A)
- **Attributes:** form (10-K \| 10-Q), accession, filed, period_of_report.
- **States:** `selected` (in range) | `10-K` (annual + Q4-context) | `10-Q` (single-quarter +
  YTD). Reused from scope A; NEW = 10-Q is now a first-class source.

## Path × edge matrix

Grid = `duration_class × period_type × filing-source × fact-state`, pruned through the
lenses (Phase ③). Surviving high-priority paths/edges:

| # | Path / edge | lens | keep/flag | prov |
|---|---|---|---|---|
| P1 | 3mo fact at fiscal Q1 end → Q1 single-quarter point | state-transition | KEEP | seeded |
| P2 | 3mo / 9mo facts SAME period_end → two distinct identities (de-conflate) | state-transition | KEEP (core) | seeded |
| P3 | 12mo fact → FY point (unchanged from scope A) | state-transition | KEEP | seeded |
| P4 | non-Dec fiscal end (Sept) → shifted quarter boundaries | BVA (date boundary) | KEEP | seeded |
| P5 | fiscal Q-end exact-match vs off-by-a-day → boundary classification | BVA | FLAG (edge) | inferred |
| E1 | instant context (balance) reaches the revenue path → excluded | empty/error | FLAG | seeded |
| E2 | missing period_start → duration underivable → fail loud | empty/error | KEEP (fail-loud) | seeded |
| E3 | Q4 untagged, FY + 9mo-YTD present → derive Q4, dqc-flag | CRUD (derived create) | KEEP | seeded |
| E4 | Q4 untagged, 9mo-YTD MISSING → cannot derive → skip + surface | empty/error | KEEP | seeded |
| E5 | directly-tagged Q4 present → use it, do NOT derive | state-transition | KEEP | seeded |
| E6 | same quarter restated across 10-Q and later 10-K comparative → policy C newest-wins + dqc | permissions/overlap | KEEP | seeded |
| E7 | mixing a quarterly point into an annual series request → rejected/separated | state-transition | KEEP | seeded |
| D1 | redundant interior nominal quarter (one mid-year Q2) | BVA | DROP (noise) | inferred |

**NFR lens:** the only binding NFR is the **anti-fabrication floor** (never emit a
conflated/derived value as reported; fail loud on underivable). Performance = scope-A cache
amortization (unchanged). No new security/concurrency surface.

## Cross-object combinations

Interaction-density gate (Phase ③b): the one stage where a joint reaction ≠ union of
per-object reactions is **Identify+dedup (stage 5)** — the joint state of `XbrlFact.duration`
× `PeriodIdentity.cumulative?` × `Filing.form` decides the reaction:

| XbrlFact.duration | PeriodIdentity | Filing | Joint reaction (≠ union) | prov |
|---|---|---|---|---|
| 3mo | single-quarter | 10-Q | emit Q<n> single-quarter point | seeded |
| 9mo | ytd-cumulative | 10-Q | emit YTD-9 point, DISTINCT key from any 3mo at same end | seeded |
| 3mo & 9mo (same end) | both | 10-Q | TWO points, never one; never RAISE against each other | seeded |
| 12mo | annual | 10-K | FY point | seeded |
| (FY − 9moYTD) | derived Q4 | 10-K (+ prior 10-Q) | cross-FILING derive; needs BOTH sources; dqc-flag | seeded |

Only 3 co-active objects on this stage (≤3) → full in-prompt enumeration suffices; the wide-
stage `pairwise.py` tool is **not** required here (gate not met). Other stages are single-
object-reaction → ③b skipped for them (per the density gate).

## Journey navigation

0-switch walk (Phase ③c) of the pipeline nav graph (few stages, mostly forward + error
escapes — the single-surface shape):

| edge | type | reaction | prov |
|---|---|---|---|
| Request → Fetch | forward | select filings by granularity + range | seeded |
| Extract → (malformed period) | error_escape | fail loud, skip the fact, never emit | seeded |
| Classify → (unknown quarter / transition period) | error_escape | flag as unclassifiable → surface, do not guess | seeded |
| Derive → (missing YTD source) | error_escape | skip Q4 derivation, surface, never fabricate | seeded |
| Identify → Stitch | forward | pass duration-keyed points to series build | seeded |
| Stitch → (mixed granularity) | retry_self/guard | reject; keep one granularity per series | seeded |

No back/skip/abandon/resume edges — a batch transform has no interactive re-entry (honest
single-surface collapse; not omitted, genuinely absent).

## Provenance

- **seeded** — every core requirement (duration discriminator, de-conflation, Q4-by-
  subtraction, fiscal-end variants, policy-C reuse, machine-captured fixtures): all stated in
  or directly entailed by the seed.
- **inferred** — FiscalCalendar as a first-class object; the off-by-a-day boundary edge (P5);
  the drop of redundant interior quarters (D1).
- **critic-found** — surfaced by the 5-lens completeness-critic panel (round 1), ranked by
  severity × cross-lens convergence, re-seeded as requirements/scenarios above:
  - Q4-derivation basis/vintage/unit consistency guard (4 lenses: NFR, provenance, object, state) — sev 3.
  - FiscalCalendar as a sourced, time-versioned object + two-pass collect-then-classify (5 lenses — full convergence) — sev 3.
  - Structured provenance on every point + a defined DQC-flag schema + dual-accession on derived Q4 + sub-annual restatement parity with policy C (NFR, provenance) — sev 3.
  - Per-filing/per-quarter coverage completeness + three distinguished fetch-failure states (NFR, provenance, system) — sev 3.
  - 6-month YTD (H1) classification scenario — a named enum member with zero coverage (state) — sev 3.
  - Intermittent/absent dimension in quarters flagged distinct from zero/discontinued (provenance, state, system) — sev 3.

## Blind spots — needs human/field input

- **52/53-week retailers (stub weeks):** quarters aren't clean 3-month spans; how to bucket a
  13-vs-14-week quarter, and the 53rd week, needs a decision (or explicit out-of-scope).
- **Transition periods (fiscal-year change):** irregular stub quarters — bucket, skip, or flag?
- **Q4-by-subtraction trust policy:** is a derived Q4 acceptable in a "reported KPI" series at
  all, or must it be opt-in / clearly segregated? (A product-judgment call — would be governed
  by PRINCIPLES.md if one existed.)
- **Per-company fiscal-calendar source:** classification needs each company's quarter-end
  dates — derive from the filing's own period_end sequence, or need an external calendar map?
  (Scope A flagged the FY-named-by-start-year variant as a later concern; quarters make it
  load-bearing.)
- **10-Q dimensional completeness:** are segment/product breakdowns tagged as richly in 10-Qs
  as in 10-Ks? (Scope-A brief flagged this as an open question for B — needs a live probe.)
- **Non-revenue KPIs / instant contexts:** if the capability later covers balance-type KPIs,
  the duration-vs-instant split needs its own model (currently revenue = duration flow only).

### Critic-panel blind spots (round 1) — needs human/field input

- **Derived-Q4 governance (PRODUCT DECISION, needs the user):** is a computed Q4 acceptable in
  a "reported KPI" series at all — default-on, opt-in, or a segregated derived-only lane? The
  spec writes the derivation scenarios but leaves the default/disclosure undefined; UNGOVERNED
  (no PRINCIPLES.md) makes a silent default risky. This is a value judgment, not a completeness
  gap — the user must decide (or a PRINCIPLES.md must).
- **Severity-2 residue re-seeded lightly or deferred (not padded into requirements):** unit/scale
  consistency before stitching; a stated duration→quarter tolerance (day-count boundary);
  10-Q/A amendment exact-form exclusion (scope A fixed 10-K/A — 4 lenses flag the quarterly
  analog); cross-form / N-way restatement resolution (policy C validated 2-way, annual only);
  instant-vs-duration context object for non-flow KPIs; cache granularity (store raw
  pre-classification facts so an annual-only cache entry doesn't starve a later quarterly
  request); zero-vs-missing parity; cascading-restatement staleness of an already-derived Q4;
  same-accession duplicate context. Each is real but secondary — carried as residue for a scope
  decision, deliberately NOT promoted into requirements to look thorough.
- **52/53-week + transition periods — systemic-vs-isolated (needs a scope decision):** even if
  full support is out-of-scope, a 52/53-week filer may make EVERY quarter unclassifiable, not
  one stub — so the safe floor is a detect-and-fail-loud (or skip-loud) guard at fetch/classify,
  not silent mislabeling. Whether to fail-loud the whole company or emit a flagged degenerate
  series is a product call.
- **Live-probe items (needs field data, not inferable from the docs):** real-world frequency of
  cross-vintage Q4 inputs, 10-K/A landing between two 10-Qs, same-accession duplicate contexts,
  and mid-history FYE changes; whether `dei:CurrentFiscalYearEndDate` (or equivalent) reliably
  gives the fiscal calendar; whether EDGAR's filing index distinguishes not-yet-filed from
  fetch-error before download; and the real 10-Q dimensional-tag completeness vs 10-K — all
  need a live probe against a pilot ticker set before their severity is settled.
- **Foreign-private-issuer semi-annual (20-F/6-K):** the 6mo-YTD scenario assumes a domestic Q2
  10-Q; whether FPI semi-annual reporting is in-view is a scope question (a different filing
  pipeline) the seed does not settle.

**Coverage statement:** coverage relative to seed + 5 lenses (principles lens N/A — no
PRINCIPLES.md), round 1. NOT a completeness claim — the blind spots above are the load-bearing
honest output; residual gaps beyond them are expected.
