# Brief — operational-kpi slice 7: apply break → dual as-reported/recast series

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 7 of the
multi-slice program**. Stacked on slice 6. Spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder covers discovery. Proceed direct.

## Problem

**Job:** *Once a definition-drift break-event is human-CONFIRMED (slice 6), I want the
affected KPI series split into an as-reported sub-series (old definition, pre-break) and
a recast sub-series (new definition, post-break) with a VISIBLE break marker — and I
NEVER want a flat multi-period trend silently spliced across a known break, because
that would compare two different definitions as if they were one number.*

Two parts: (a) **apply** a CONFIRMED break (CONFIRMED → APPLIED, recording the break
period boundary); (b) a **dual-series view** that splits a series by its applied
break(s) into as-reported / recast with a break marker, and REFUSES to return a
naively-concatenated flat series across a break unless the caller explicitly chooses a
basis (as-reported | recast | dual-with-flag).

## Users

**Job story:** *When I query a company's KPI series that has an APPLIED break, I want to
choose a basis: as-reported (pre-break, old definition), recast (post-break), or
dual-with-flag (both, marked at the transition); and if I ask for a flat trend across
the break without choosing, I want it REFUSED — the caller must pick, never a silent join.*

Consumers: the memo-feed slice (bundles a break-aware series); a downstream trend view.

## Smallest End State

A new module `investing-toolkit/skills/analysis-kpi/scripts/kpi_series.py` (reuses
`kpi_break` for applied breaks; pure-compute for the split, no new store — the break
APPLY state lives on the existing kpi_break record):

1. **Apply a confirmed break** — `apply_break(company, break_id, break_period)`: require
   the break-event is CONFIRMED (slice 6); transition CONFIRMED → APPLIED, recording the
   `break_period` (the period boundary at which the series splits). Reject applying a
   non-CONFIRMED break (FLAGGED/DISMISSED/already-APPLIED) loud. Routes through kpi_break's
   store (lock-guarded); this is a state transition, NOT a new human-confirm (the human
   already confirmed in slice 6 — apply is the mechanical follow-through).
2. **Split a series by its applied breaks** — `split_series(points, applied_breaks)`
   (PURE COMPUTE): given a series `points` (each `{period, value, ...}`, period-ordered)
   and the APPLIED breaks (each carrying `break_period`), partition into
   `{"as_reported": [pre-break points], "recast": [post-break points], "break_markers":
   [{break_period, ...}]}`. A point at a period < the earliest break_period is
   as-reported; at/after is recast; the marker sits at each break_period. No applied
   breaks → all points are a single unbroken as_reported series, no markers.
3. **Basis-required view (no naive concat)** — `series_view(points, applied_breaks,
   basis)`: `basis` ∈ `"as-reported"` | `"recast"` | `"dual"`. Returns the chosen view
   (as_reported list / recast list / the full dual+markers dict). If there IS an applied
   break AND `basis` is None/absent → raise loud ("a series across a break requires an
   explicit basis; refusing a naive concatenation"). No break → any basis (or None)
   returns the flat series (nothing to disambiguate).
4. A thin **CLI** — `apply` / `view` subcommands.

**Explicitly NOT in this slice:** the LLM locate/parse that produces the series points;
the break detection/adjudication (slice 6 — this consumes a CONFIRMED break); the
memo-feed artifact (slice 8); recast-series RE-GATING against the reliability gate (that
lives in slice 5's `evaluate`, which already treats a recast as its own schema_version —
this slice just splits/labels, it does not re-run the gate). This slice = apply + split
+ basis-required view ONLY.

## Current State Evidence

- **Forward (consumers):** the memo-feed (slice 8) will request a break-aware series; not
  built yet.
- **Reverse (reuse):** `kpi_break.py` owns the break-event store + its CONFIRMED state
  (slice 6); `apply_break` extends its lifecycle CONFIRMED → APPLIED (reuse its store +
  lock). `kpi_store.py` owns the series points; the split is a PURE-COMPUTE function over
  points the CALLER reads from kpi_store (this slice does not itself query kpi_store — it
  takes `points` as an argument, mirroring how kpi_validate takes a value). Distinct
  concerns kept separate.
- **Error (fail-loud):** apply a non-CONFIRMED break → raise; a flat query across an
  applied break with no basis → raise (the anti-silent-join guard). A split with no
  breaks is a normal single-series result.
- **Data (shapes):** spec Requirement "Dual as-reported/recast series with visible break
  flag" (`operational-kpi/spec.md` :217): once CONFIRMED+applied, split into as-reported +
  recast each with a break flag; "Naive concatenation is rejected" (:228) — a flat trend
  across a known break must make the caller choose. break-event states
  `... confirmed → applied ...` (proposal.md).
- **Boundary:** `apply_break` mutates the kpi_break record — respect its lock; the state
  guard (only CONFIRMED can be applied) mirrors slice-6's confirm-once discipline.

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py`,
`.../kpi_store.py`, `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Decision

Build `kpi_series.py`: `apply_break` (CONFIRMED → APPLIED on the kpi_break record,
recording break_period, lock-guarded, reject non-CONFIRMED); `split_series` (pure-compute
partition of points into as_reported/recast/markers by applied breaks); `series_view`
(basis-required: as-reported/recast/dual, REFUSING a naive flat concat across a break);
a CLI. Reuse kpi_break's store; take series points as an argument (don't couple to
kpi_store's query).

**We will NOT:** re-run the reliability gate here (slice 5 owns it); produce the series
points (later slice); silently concatenate across a break (the core guard); apply a
non-CONFIRMED break; build the memo-feed (slice 8).

## Alternatives Considered

Fork — **default a flat series vs refuse-without-basis across a break** — resolved by the
spec ("Naive concatenation is rejected") + the confirmed intent (a same-company trend
must not silently compare two definitions): REFUSE without an explicit basis. No external
library fork; the split is stdlib pure compute.

## What Becomes Obsolete

Nothing removed — additive. slice-1's stored-but-uninterpreted `lineage`/`restates`
fields on series-points now gain a consumer (the break-aware split), though this slice
splits by APPLIED-break period rather than by a per-point lineage tag (keeping the split
driven by the adjudicated break, not by raw producer tags).

## Out of Scope

- LLM locate/parse; memo-feed; reliability re-gating; non-US markets; archiving.

## Open Questions

1. **break_period vs point period comparison** — periods are strings (e.g. "FY2024",
   "2024-Q3"). The split compares point.period to break_period; default lexical/explicit
   ordering as the caller supplies period-ordered points + a break_period drawn from the
   same period vocabulary. Confirm the comparison basis in plan (a point AT the
   break_period goes to recast — the break takes effect from that period).
2. **Multiple applied breaks** — a series with 2+ applied breaks splits into >2 segments;
   default: as_reported = before the FIRST break, recast = after the LAST? Or per-segment?
   Default for this slice: as_reported = points before the earliest break_period; recast =
   points at/after it; multiple breaks collapse to the earliest boundary for the
   two-way as-reported/recast split, with all break_markers surfaced. Revisit if
   per-segment lineage is needed (flag as a known limitation).
