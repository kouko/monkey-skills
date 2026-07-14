# Brief — operational-kpi slice 5: reliability gate + ground-truth label set

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 5 of the
multi-slice program**. Stacked on slice 4. Spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder covers discovery. Proceed direct.

## Problem

**Job:** *Before any company's operational-KPI series is fed to a memo, I want proof
that extraction is reliable ENOUGH for that company — measured as cell-level accuracy
against a held-out set of human-labeled ground-truth values — and I want an
un-evaluated company to be WITHHELD by default (fail-closed), never trusted by
omission.* (The confirmed intent: a per-company trend is only worth trusting if the
numbers behind it are demonstrably accurate.)

Two durable objects + a compute gate: (a) a **ground-truth label set** (human-labeled
correct (company, kpi_id, period) → value), (b) a **reliability-gate record** per
(company, schema-version) holding the measured accuracy + verdict, and (c) the
**evaluation** that compares extracted values to the labels and issues TRUSTED /
WITHHELD / NOT_EVALUATED — fail-closed by default.

## Users

**Job story:** *When I have a held-out label set for a company, I want to evaluate its
extraction accuracy against a run's extracted values, record the metric + sample size +
verdict, and have the memo pipeline get TRUSTED only when accuracy ≥ the threshold
(inclusive) on a large-enough sample — otherwise WITHHELD (below bar) or NOT_EVALUATED
(no/too-few labels); and a company never evaluated defaults to WITHHELD.*

Consumers (later slices / memo): the memo-feed reads `is_trusted(company, schema_version)`
and only bundles a TRUSTED series; a recast series is evaluated the same way before it
is fed.

## Smallest End State

A new durable-store module `investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py`
(reuses `_store_fs` for durable dir + lock + atomic write, like kpi_store/review_queue/
kpi_schema) providing:

1. **Ground-truth label set (first-class object)** — `add_labels(company, labels)` +
   `get_labels(company)`: persist human-labeled `{kpi_id, period, value}` entries per
   company under a durable, locked, versioned envelope. This is the held-out truth the
   gate measures against.
2. **Gate evaluation** — `evaluate(company, schema_version, extracted_values,
   threshold=None, min_samples=<default>)`: match each labeled (kpi_id, period) to the
   corresponding extracted value, compute **cell-level accuracy** = correct / total
   labeled cells; record a gate record `{company, schema_version, metric, sample_size,
   verdict, evaluated_at}` (evaluated_at caller-supplied — NO wall-clock). Verdict:
   - **NOT_EVALUATED** if no labels OR sample_size < min_samples (never a verdict from
     too few samples).
   - **TRUSTED** if sample_size ≥ min AND accuracy ≥ threshold (INCLUSIVE boundary).
   - **WITHHELD** if sample_size ≥ min AND accuracy < threshold.
3. **Threshold calibration (deferred, fail-closed default)** — `threshold` is an
   OPTIONAL operator-set numeric bar. Until explicitly set, the gate uses its
   fail-closed default (a company is WITHHELD/NOT_EVALUATED, never TRUSTED-by-omission).
   The user's chosen calibration value is **0.95** (recorded as the recommended
   threshold once pilot data exists); the mechanism ships configurable + fail-closed.
4. **Fail-closed trust query** — `gate_verdict(company, schema_version)` returns the
   recorded verdict, defaulting **WITHHELD** when no gate record exists (a never-
   evaluated company is fail-closed, NOT trusted). `is_trusted(company, schema_version)`
   → True ONLY when the recorded verdict is TRUSTED.
5. **Recast series is itself gated** — a recast (post-break) series is evaluated by the
   SAME `evaluate` under its own schema_version; nothing special-cases it into trust.
   (This slice makes the mechanism version-scoped so a recast is naturally re-gated;
   the break-event machinery that PRODUCES a recast is a later slice.)
6. A thin **CLI** — `add-labels` / `evaluate` / `verdict` subcommands.

**Explicitly NOT in this slice:** the LLM locate / parse that produces extracted_values
(a later slice — this evaluates values given to it); the break-event detection that
creates a recast series (later slice); the memo-feed artifact (later slice); populating
real ground-truth labels (an ops/pilot activity — the OBJECT + lifecycle ship here, the
content does not). This slice is the label-set object + the gate mechanism ONLY.

## Current State Evidence

- **Forward (consumers):** the memo-feed slice will call `is_trusted`; not built yet.
- **Reverse (reuse):** `_store_fs.py` owns the durable-store primitives; kpi_gate reuses
  them (same-skill import) exactly like kpi_schema — label-set + gate records are
  per-company/per-(company,version) file-per-key JSON. NO cache_util, NO reimplemented
  lock.
- **Error (fail-closed):** the spec's whole posture — a never-evaluated or below-bar
  company is WITHHELD, never trusted; too-few-samples → NOT_EVALUATED, never a spurious
  verdict. Reject loud only on malformed input; a WITHHELD verdict is a normal result.
- **Data (shapes):** spec `reliability-gate` attrs (proposal.md): `gate_id, company,
  metric(cell-level-accuracy), sample_size, verdict, evaluated_at`; states
  `not_evaluated → evaluated → {trusted | withheld} → (schema bump) → not_evaluated`.
- **Boundary:** spec Requirements "Reliability-gate evaluation against a held-out
  labeled set" (:233), "Reliability-gate withhold-below-bar" (:249), "Reliability
  threshold calibration [deferred]" (:264), "Ground-truth label set is a first-class
  object" (:366), "Recast series is itself gated" (:350). At-threshold INCLUSIVE +
  minimum-sample guard are explicit spec scenarios (:379, :374).

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py`,
`.../kpi_schema.py` (the reuse pattern), `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Decision

Build `kpi_gate.py`: a durable label-set store (`add_labels`/`get_labels`) + a
`evaluate` that measures cell-level accuracy vs the held-out labels and records a
version-scoped gate record with a TRUSTED/WITHHELD/NOT_EVALUATED verdict (at-threshold
inclusive, minimum-sample guarded, threshold operator-set with a fail-closed default),
+ fail-closed `gate_verdict`/`is_trusted` (default WITHHELD), + a CLI. Reuse `_store_fs`.

**We will NOT:** trust a never-evaluated or below-bar or too-few-samples company; read
the wall clock (evaluated_at caller-supplied); produce extracted_values or a recast
series (later slices); persist real labels' content (the object ships, ops populate it);
hardcode a threshold (configurable; 0.95 recorded as the user's calibration target).

## Alternatives Considered

Fork — **fail-open vs fail-closed default** — resolved by the spec + the confirmed
anti-fabrication intent: fail-CLOSED (WITHHELD by default) is mandatory; a
trusted-by-omission gate would defeat the whole reliability posture. Threshold is
operator-configurable (deferred calibration) rather than a baked constant, so 0.95 (the
user's pick) is data, not code. No external library fork. Substrate = `_store_fs`
file-per-key JSON (slice-1..4 precedent).

## What Becomes Obsolete

Nothing removed — additive. Establishes the trust contract the memo-feed slice MUST
consult (`is_trusted`) before bundling any series.

## Out of Scope

- LLM locate/parse; break-event detection/recast production; memo-feed artifact; real
  label population; non-US markets; archiving the change-folder.

## Open Questions

1. **min_samples default** — a 1-cell held-out set yielding a spurious 100% is the
   spec's named hazard (:374). Default a conservative min (e.g. 5) with an operator
   override; confirm the number at plan time (it's a fail-closed guard, so a slightly-
   high default is the safe direction).
2. **"correct" match tolerance** — is an extracted value "correct" vs a label on exact
   equality or within a tolerance? Default: exact for integers/strings; a relative
   tolerance (xval-band precedent) for floats. Resolve in plan.
