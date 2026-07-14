# Brief — operational-kpi slice 4: rule-based value validation (pure compute)

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 4 of the
multi-slice program**. Stacked on slice 3. Spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder covers discovery. Proceed direct.

## Problem

**Job:** *Before a parsed operational-KPI value is allowed to become a trusted
series-point, I want it checked against deterministic sanity rules — right unit, legal
sign, segments that sum to their reported total, and no forcing a company's non-GAAP
metric against a GAAP tag — so an extraction slip is caught by arithmetic before it
ever reaches the store or the memo.*

This is the **Layer-2 pure-compute validation gate** — a value that fails any applicable
rule is NOT eligible to be stored (slice 1) or fed to the memo. It is deterministic
(no LLM, no network, no persistence): value in → verdict out.

## Users

**Job story:** *When the parse step (a later slice) produces a candidate KPI value with
its unit and — for a segmented KPI — its parts and reported total, I want a validator
that returns "eligible" only when the unit matches the schema def, the sign is legal,
the parts sum to the total within tolerance, and a non-GAAP metric is not rejected for
lacking a GAAP tag; otherwise it returns the specific rule that failed, so the
confidence-gated review-enqueue slice can route it to a human.*

Consumers (later slices): the parse→validate→store pipeline; the confidence-gated
review-enqueue (a rule failure is one of its enqueue triggers).

## Smallest End State

A new **pure-compute** module `investing-toolkit/skills/analysis-kpi/scripts/
kpi_validate.py` (no `_store_fs`, no lock, no network — mirrors the `analysis-comps` /
`analysis-dcf` compute-script shape: stdlib, JSON in → JSON out) providing:

1. **Sign check** — `check_sign(value, kpi_def)`: a KPI whose def marks it non-negative
   (e.g. `{"sign": "non-negative"}` for unit sales) fails when the value is negative;
   a KPI with no sign constraint (or `"any"`) always passes the sign rule.
2. **Unit check** — `check_unit(value_unit, kpi_def)`: the value's unit must equal the
   def's `unit`; a mismatch fails (a units-vs-USD confusion is a classic extraction slip).
3. **Subtotal check** — `check_subtotal(segments, total, tol=~0.01)`: the segment values
   must sum to the reported total within a relative tolerance; a mismatch is flagged,
   never silently accepted. If no segments/total are supplied, the rule is N/A (skip,
   not fail).
4. **GAAP-vs-non-GAAP rule** — `check_gaap(kpi_def, ...)`: a company-defined non-GAAP KPI
   is NOT required to match a GAAP tag — the validator must not fail a non-GAAP metric
   for lacking a GAAP counterpart (the rule models legitimate non-GAAP metrics, it does
   not force them).
5. **Aggregate** — `validate(value_record, kpi_def)`: runs every APPLICABLE rule and
   returns `{"eligible": bool, "failures": [{"rule", "detail"}, ...]}` — eligible only
   when no applicable rule failed. Deterministic, side-effect-free.
6. A thin **CLI** — `validate` reads a `{value_record, kpi_def}` JSON from stdin/--file,
   prints the verdict JSON; fail-loud exit codes (0 ok / 2 malformed) mirroring the
   sibling CLIs. (A rule FAILURE is a normal verdict with `eligible:false`, exit 0 —
   the value is validly-processed-and-rejected, not a CLI error.)

**Explicitly NOT in this slice:** the LLM locate / deterministic parse that PRODUCES the
value (a later slice — this validates a value given to it); the XBRL cross-check (its own
slice); the confidence-gated review-enqueue (consumes this verdict); storing anything
(slice 1). This slice is the deterministic rule engine ONLY.

## Current State Evidence

- **Forward (consumers):** none yet — the validator ships ahead of the parse step that
  will feed it. CLI + the pure functions are the exercisable surface.
- **Reverse (shape / sibling pattern):** the pure-compute analysis scripts
  `analysis-comps/scripts/comps_compute.py` + `analysis-dcf/scripts/dcf_compute.py` are
  the precedent for a stdlib, JSON-in/JSON-out, NO-persistence Layer-2 compute module —
  `kpi_validate.py` follows that shape (NOT the durable-store shape of kpi_store /
  review_queue / kpi_schema; it needs no `_store_fs`). The kpi_def shape (`unit`, plus a
  `sign` + a `gaap` flag this slice reads) extends slice-3's `kpi_defs` dict.
- **Error (fail-loud):** a value that fails a rule is a NORMAL `eligible:false` verdict
  (not an exception) — the caller decides what to do; only MALFORMED input (bad JSON,
  wrong shape) is a loud CLI error. A subtotal check on absent parts is N/A (skip), not
  a failure — don't conflate "rule not applicable" with "rule failed".
- **Data (record shapes):** spec Requirement "Rule-based validation of parsed values"
  (`operational-kpi/spec.md` :80) — unit / sign / subtotal-equals-sum / GAAP-vs-non-GAAP,
  applied before a value becomes a series-point. Scenarios: segment sum (:85), sign
  violation (:90), non-GAAP not forced (:95).
- **Boundary:** value tolerance echoes the xval band precedent (~1%) already in the repo
  (analysis-xval); reuse the same relative-tolerance idea for the subtotal check.

Evidence paths: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`,
`investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py`,
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Decision

Build `kpi_validate.py` as a stdlib, pure-compute, side-effect-free rule engine:
`check_sign` / `check_unit` / `check_subtotal` / `check_gaap` + an aggregate `validate`
returning an eligibility verdict with the specific failed rules, plus a thin CLI.
Follow the analysis-comps/dcf compute-script shape (NO persistence, NO `_store_fs`).

**We will NOT:** persist anything (no store/lock); locate or parse the value (later
slice); cross-check XBRL (own slice); enqueue review-items (the consumer's job);
fail on an N/A rule (skip it); force a non-GAAP metric against a GAAP tag.

## Alternatives Considered

The one design question — **module shape: durable-store vs pure-compute** — resolves to
pure-compute: validation reads a value and emits a verdict with no state, so it mirrors
`analysis-comps`/`analysis-dcf` (stdlib, JSON in/out), NOT the `_store_fs`-backed stores.
No external library fork. The ~1% subtotal tolerance follows the repo's existing xval
band precedent rather than a new invented constant.

## What Becomes Obsolete

Nothing removed — additive. Establishes the deterministic validation contract the
parse→store pipeline (later slices) must route values through before trusting them.

## Out of Scope

- LLM locate / deterministic parse; XBRL cross-check; confidence-gated review-enqueue;
  persistence; reliability gate; break-events; memo-feed; non-US markets; archiving.

## Open Questions

1. **kpi_def sign/gaap field names** — this slice reads `sign` (`"non-negative"`/`"any"`)
   and a `gaap` flag (`true`/`false`, absent → treat as non-GAAP/unconstrained) off the
   kpi_def. Default those names; confirm at plan time they don't collide with slice-3's
   stored def shape (slice 3 stored `{kpi_id, label, unit, locate_hint}` verbatim — the
   validator reads the OPTIONAL `sign`/`gaap` if present, ignores their absence).
2. **Subtotal tolerance** — relative ~1% (xval band precedent) vs absolute. Default:
   relative, `math.isclose`-style. Resolve in plan.
