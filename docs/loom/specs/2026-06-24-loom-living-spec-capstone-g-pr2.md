# Brief: loom living-spec capstone G — PR-2 (enforce intent)

Status: **BRAINSTORM — three forks resolved, awaiting sign-off → writing-plans.**
Date: 2026-06-24. Branch: `feat/loom-living-spec-capstone-g-pr2` (cut from `origin/main`, PR-1 #454 merged).

> **Design is CONVERGED upstream** — see `docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md`
> (decision #3 active-coverage gate, the active/deferred schema, decision #6 authorship split, Open-Q6
> ready-signal binding). This is the **implementation** layer for the intent-enforcement half. Axis 4
> (industry alternatives) was settled in the design brief (Tessl canonical-vs-inspirational mapping).

## Problem

PR-1 made the index *linkage-true* (it can't drift from the tags) but it does NOT yet enforce that a
requirement the authors **declare is meant to hold now** is actually backed by a passing test. Without
this, an `active` requirement can merge with zero verification — a silent "we said this works but never
proved it." PR-2 closes the intent half: requirements carry an **active/deferred** status, and a
merge-boundary CI gate **blocks** an `active` requirement that has no passing test.

JTBD: *When I finish a branch that declares a requirement as `active` (meant to be verified now), I want
CI to block the merge unless a passing test is bound to it, so a canonical requirement can never ship
unverified — while a `deferred` (aspirational) requirement is surfaced, not blocked.*

## Users

loom-suite maintainers (dogfood). Two surfaces: (a) **loom-spec authors** mark each requirement
`active`/`deferred` in the persistent intent layer; (b) **CI on the PR head** runs the active-coverage
gate after the green test suite and blocks merge on an `active`-with-no-test.

## Smallest End State

A merge-boundary CI step that FAILs iff some `active` requirement has **0 linked tests** (deferred + 0 →
printed as inspirational, never fails), plus the status authoring surface. **Key simplification (resolved
in discovery):** because CI runs the gate **after** a green pytest gate, "0 *passing* tests" reduces to
"0 *linked* tests" — a green suite means every linked test passed, so the gate needs only the req→test
linkage PR-1 already produces (`collect_structural_records`), NOT junit/per-test-result parsing.

## Current State Evidence

Brownfield. All citations verified by read-only recon at the PR-2 branch base.

- **Forward (status declaration → parse):** requirement IDs are declared as `### Requirement: <id>`
  headings in `docs/loom/spec/<capability>/spec.md`, parsed by `living_spec_index.py:15`
  (`_REQUIREMENT_RE = r"^###\s+Requirement:\s*(.+?)\s*$"`) inside `load_namespace` (`:18-31`, returns
  `{req_id: capability}` from `glob("*/spec.md")`). Status will be an **optional `[active|deferred]`
  suffix on that heading** — the regex must capture the id in group 1 **unchanged** (non-greedy, stops
  before the bracket) and the status in a new group, so `load_namespace`'s existing `req_id` stays clean
  and the index (PR-1) is unaffected.
- **Reverse (req→test linkage):** `living_spec_collect.py:113-180` `collect_structural_records(root)`
  returns `{test, reqs, invariant_refs}` records (test→reqs); invert to req→tests. This is the only
  data the active-coverage gate needs (per the smallest-end-state reduction).
- **Error (gate ordering = the "passing" guarantee):** `.github/workflows/loom-code-ci.yml:58-61` runs
  `pytest loom-code/scripts/ -v` **first**; the living-spec gates (structural `:79-85`, verify-index
  `:87-94`) run **after**. The active-coverage gate slots in the same post-pytest band, so a green suite
  is its precondition — that is what makes "0 linked ≡ 0 passing" sound. **Documented scope limit:**
  pytest covers `loom-code/scripts/` only; an `@req` test outside that path is not covered by this
  green-suite guarantee (no such test exists today; widen the suite scope when one lands).
- **Data (status validation — NOT in validate_intent_layer.py, per the RESHAPE):**
  `validate_intent_layer.py:58-62` `_TOP_SECTIONS` + `:127-151` `validate` validates intent-layer DOC
  structure (MODEL.md sections, README presence) and does **not** read `spec.md` requirement headings —
  so status-syntax validation does NOT belong there (it would complect two concerns). Instead the parser
  (piece 1) rejects an unrecognized status token fail-loud, surfaced by the existing structural lane's
  malformed path (`find_structural_violations`, PR-1). The intent layer `docs/loom/spec/` (singular)
  **does not exist yet** — the gate is correct but near-noop on this repo until a real requirement is
  declared (mirrors PR-1's empty base case; demo/dogfood via a seeded requirement).
- **Boundary (authoring docs):** `loom-spec/skills/spec-expansion/SKILL.md:388-417` is the "Authoring
  the persistent intent layer" section (TOP/MID schema); the status-authoring docs + gate-behavior note
  attach after `:417`.

Evidence paths: `loom-code/scripts/{living_spec_index,living_spec_collect,check-living-spec-index}.py`,
`loom-spec/scripts/validate_intent_layer.py`, `.github/workflows/loom-code-ci.yml`,
`loom-spec/skills/spec-expansion/SKILL.md`.

## Decision

Ship PR-2 as the loom-spec + CI intent-enforcement half, in **one slice** (smaller than PR-1; no
multi-PR split needed). **Four pieces** (a `complexity-critique` RESHAPE pass dropped a 5th — see below).
Build:

1. **Status syntax + parser** (loom-code/scripts/living_spec_index.py) — extend `_REQUIREMENT_RE` to
   optionally capture `[active|deferred]` (default `active`); add a loader returning req→status
   (e.g. `load_req_status(specs_dir) -> {req_id: "active"|"deferred"}`) WITHOUT changing
   `load_namespace`'s `{req_id: capability}` contract. **A status token that is neither `active` nor
   `deferred` (e.g. `[activ]`) is rejected fail-loud as a malformed declaration** — surfaced by the
   EXISTING every-push structural lane (`find_structural_violations` malformed path, PR-1), RED-safe.
   (This is where status-syntax validation lives — see the dropped piece below.)
2. **active-coverage check** (loom-code/scripts/check-living-spec-index.py) — a function +
   `--check-coverage` CLI mode: invert `collect_structural_records` to req→tests, and for each req in
   the namespace: `active` + 0 linked tests → violation (exit 1, name the req); `deferred` + 0 linked
   → print as "inspirational/surfaced" (never fails). Runs at merge-boundary (post-green-suite).
3. **CI gate step** (loom-code-ci.yml) — add the active-coverage step in the post-pytest band, after
   the existing living-spec gates.
4. **Authoring docs** (spec-expansion SKILL.md) — document the `[deferred]` suffix (active = default),
   the canonical-vs-inspirational mapping, and the gate behavior.

**DROPPED by complexity-critique (RESHAPE, design-is-taking-apart mindset):** a separate "loom-spec status
validation in `validate_intent_layer.py`" piece. It would **complect** two concerns — the intent-layer
DOC structure (MODEL.md sections, README presence) that validator owns, and requirement-tag SYNTAX — by
forcing `validate_intent_layer.py` to newly read `spec.md` requirement headings just to validate a token
the structural lane already parses. The composed design folds malformed-status detection into piece 1's
parser + PR-1's existing structural-lane malformed path: same rule, one validator, no new cross-plugin
read, ~40-50 fewer lines, no second drift surface.

**Status attach-point = in-spec metadata on the requirement heading** (`### Requirement: REQ-X [deferred]`)
— status is a per-requirement property, co-located with its declaration: one source of truth, no
status↔requirement drift surface, continuous with PR-1's `_REQUIREMENT_RE` machinery. (Rejected: a
central `## Requirement status` table in MODEL.md — divorces status from the requirement, two places to
sync; a per-capability `status.json` — new file + JSON-in-markdown inconsistency + new parser.)

**"0 passing tests" = "0 linked tests", guaranteed by post-green-suite CI ordering** — no junit/per-test
result parsing (the green suite IS the per-test-pass signal). (Rejected: junit-xml parsing — unnecessary
machinery given the ordering guarantee.)

**NOT building:** junit/per-test-result capture; the Open-Q6 ready-signal binding; widening the pytest
scope beyond loom-code/scripts/. (All deferred — see Out of Scope.)

## Out of Scope

- **Ready-signal binding (design Open-Q6)** — binding the merge-boundary gates to a finishing-emitted
  ready signal (not bare `not-draft`) so a mid-RED `active`-with-0-tests doesn't false-FAIL. This is a
  **cross-cutting CI-wiring concern affecting BOTH merge-boundary gates** (PR-1's verify-index already
  runs on PR without it); do it once for both in a follow-up, not bolted onto PR-2. PR-2's gate rides
  the same PR trigger as verify-index; the mid-RED edge (a non-draft PR opened before tests are written)
  is the documented residual until Open-Q6 lands.
- **junit/per-test-result parsing** — obviated by the post-green-suite reduction.
- **Widening pytest scope** beyond loom-code/scripts/ — no `@req` test lives outside it today.
- Re-opening any locked design decision; the PR-1 deferred debt (drift-lane tokenize, Rule-of-Three,
  argv sharp edge) — separate follow-ups.

## What Becomes Obsolete

- The slice-3 note "active/deferred status DEFERRED to capstone G (its only consumer = unread field
  now)" — PR-2 IS that consumer; the field is now read + enforced. Update the spec-expansion authoring
  text that flagged status as deferred.

## Open Questions (impl-level; resolved at writing-plans)

1. **Exact status syntax** — `[deferred]` vs `(deferred)` vs a trailing `— deferred`. Leaning
   `[active|deferred]` bracket suffix (visually distinct, regex-cheap). Confirm at plan time.
2. **`--check-coverage` vs fold into existing structural lane** — a separate CLI mode keeps the
   every-push structural lane (RED-safe) cleanly apart from the merge-boundary coverage gate
   (RED-unsafe). Leaning separate mode (matches the design's lane separation). Confirm at plan time.
3. **PR-2 dogfood vector** — like PR-1, demo via a seeded `active` req with no test (→ gate FAILs) and a
   `deferred` req with no test (→ surfaced, passes). Confirm the demo shape at writing-plans.
