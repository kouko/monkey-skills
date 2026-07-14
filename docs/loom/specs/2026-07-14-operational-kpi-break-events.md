# Brief — operational-kpi slice 6: break-event detection + adjudication lifecycle

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 6 of the
multi-slice program**. Stacked on slice 5. Spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder covers discovery. Proceed direct.

## Problem

**Job:** *When a company changes how it reports a KPI across periods — re-segments,
relabels, or its parts stop reconciling — I want that DEFINITION DRIFT flagged as a
candidate break-event and adjudicated by a HUMAN (who records the old→new mapping)
before the series is treated as continuous, so a same-company trend never silently
splices two different definitions together.*

Two parts: (a) **detection** — a pure-compute comparison of consecutive periods that
raises a candidate break-event on resegmentation / relabel / arithmetic-mismatch; (b)
the **break-event lifecycle** — flag it, route it through the slice-2 review-queue
human-confirm seam, and record a human-adjudicated old→new mapping (CONFIRMED) or
dismiss it (DISMISSED). **Applying** a confirmed break to actually split the series into
as-reported/recast sub-series is the NEXT slice (7) — this slice detects + adjudicates.

## Users

**Job story:** *When two consecutive periods' KPI summaries differ in segment count,
a kpi_id label, or fail arithmetic reconciliation, I want a candidate break-event
FLAGGED and a review-item enqueued; and I want a human to CONFIRM it with an explicit
old→new mapping (or DISMISS a false positive) through the existing human-confirm seam —
the pipeline must never self-confirm a break.*

Consumers: slice 7 (applies a CONFIRMED break to split the series); the memo pipeline
(never trusts a series across an un-adjudicated break).

## Smallest End State

A new durable-store module `investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py`
(reuses `_store_fs` + `review_queue`, like kpi_schema/kpi_gate):

1. **Detection (pure compute)** — `detect_breaks(prev_summary, curr_summary)`: compares
   two consecutive-period KPI summaries (each carrying `segments` (a set/list of segment
   names), `kpi_labels` (kpi_id → label), and an optional `reconciliation` {parts, total}
   per kpi) and returns a list of candidate break-events `[{trigger, detail}]` where
   trigger ∈ `resegmentation` (segment count/set changed) / `relabel` (a kpi_id's label
   changed) / `arithmetic-mismatch` (parts no longer sum to total). No candidates → [].
   Side-effect-free.
2. **Flag + enqueue** — `flag_break(company, schema_version, candidate)`: persist a
   break-event record (status `FLAGGED`, trigger, detail, `mapping=None`) in a durable,
   lock-guarded store AND enqueue a `subject_type="break-event"` review-item via
   `review_queue` so a human adjudicates it.
3. **Adjudicate (human-confirm seam)** — `confirm_break(company, break_id, adjudicated_by,
   mapping)`: through `review_queue.adjudicate` (REUSING the auth boundary — empty/
   whitespace/pipeline identity rejected there) transition the break-event `FLAGGED →
   CONFIRMED`, recording the human-supplied old→new `mapping` (required — a confirm with
   no mapping is rejected). `dismiss_break(company, break_id, adjudicated_by)`: `FLAGGED →
   DISMISSED` (a false positive; the series continues unaffected). Illegal transitions
   (adjudicating an already-resolved break, unknown break_id) reject loud.
4. **Query** — `get_break(company, break_id)` / `list_breaks(company)` read-only.
5. A thin **CLI** — `detect` / `flag` / `confirm` / `dismiss` / `list` subcommands.

**Explicitly NOT in this slice:** APPLYING a confirmed break to split the series into
as-reported/recast sub-series + the naive-concatenation rejection (slice 7); the LLM
locate/parse that produces the period summaries (a later slice — detection consumes
summaries given to it); the memo-feed (later). This slice detects + adjudicates ONLY.

## Current State Evidence

- **Forward (consumers):** slice 7 will read CONFIRMED breaks + their mappings to split
  series; not built yet.
- **Reverse (reuse):** `_store_fs` (durable dir/lock/atomic-write) + `review_queue`
  (enqueue + the human-confirm `adjudicate` seam with its auth boundary) are reused by
  same-skill import, exactly like kpi_schema's confirm routes through review_queue. The
  break-event store is per-company file-per-key JSON with a distinct filename suffix.
- **Error (fail-loud + no self-confirm):** confirm/dismiss route through the review-queue
  auth boundary (no pipeline self-confirm); a confirm with no mapping, or an illegal
  transition, rejects loud; a detection with no drift returns [] (a normal result).
- **Data (shapes):** spec `break-event` attrs (proposal.md): `break_id, company,
  trigger(resegmentation|relabel|arithmetic-mismatch), mapping, status`; states
  `flagged → under_review → {confirmed → applied | dismissed}` (this slice covers
  flagged→confirmed/dismissed; `applied` is slice 7).
- **Boundary:** spec Requirements "Definition-drift detection triggers a break-event"
  (:187), "Break-event human adjudication and mapping" (:202). Nested schema→queue lock
  ordering must stay consistent (see `docs/loom/memory/nested-cross-file-locks-need-one-global-order.md`).

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py`,
`.../review_queue.py`, `.../kpi_schema.py` (confirm-via-review_queue precedent),
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Decision

Build `kpi_break.py`: `detect_breaks` (pure-compute drift detection: resegmentation /
relabel / arithmetic-mismatch), a durable break-event store with `flag_break` (FLAGGED +
review-item enqueue), `confirm_break` (FLAGGED→CONFIRMED with a required human-supplied
old→new mapping, through the review-queue human-confirm seam) / `dismiss_break`
(FLAGGED→DISMISSED), read-only queries, and a CLI. Reuse `_store_fs` + `review_queue`.

**We will NOT:** apply a break / split the series (slice 7); let the pipeline self-confirm
a break (reuse the review_queue auth boundary); confirm without a mapping; produce the
period summaries (later slice); read the wall clock (timestamps caller-supplied).

## Alternatives Considered

Fork — **detect-and-auto-apply vs detect-then-human-adjudicate** — resolved by the spec +
anti-fabrication intent: every break MUST be human-adjudicated with an explicit mapping
before it affects the series; auto-applying a detected break would silently rewrite
history. No external library fork; substrate = `_store_fs` file-per-key JSON precedent.

## What Becomes Obsolete

Nothing removed — additive. Establishes the break-event lifecycle slice 7 consumes to
split series.

## Out of Scope

- Applying breaks / dual as-reported-recast series / naive-concat rejection (slice 7);
  LLM locate/parse; memo-feed; non-US markets; archiving.

## Open Questions

1. **Summary input shape for detect_breaks** — this slice defines a minimal per-period
   summary (`segments`, `kpi_labels`, optional `reconciliation`); the parse slice will
   produce it. Confirm the shape at plan time; keep detection tolerant of missing
   optional sub-fields (a summary lacking `reconciliation` simply can't raise the
   arithmetic-mismatch trigger — N/A, not an error).
2. **Confirm routing** — like kpi_schema.confirm: `confirm_break` adjudicates the
   break's review-item through review_queue internally (single call, still enforcing the
   human-identity boundary). Default yes; resolve in plan.
