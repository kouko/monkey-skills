# Brief: loom living-spec — slice 3 (E-core) persistent intent layer

Status: **BRAINSTORM COMPLETE** — ready for `writing-plans` once the user signs off the
Axis 1 / Smallest-End-State / Out-of-Scope checkpoint. Date: 2026-06-23.
Parent design: `docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md`
(decisions #4 TOP/MID cut rule, #6 loom-spec owns the intent layer + validator).
Slice plan: this is **E-core** — the "why" layer only. Per the scope triage, **status
(active/deferred) is deferred to the capstone G slice that consumes it**, and **F (the
closed loop / prior-state read) is the next slice**. E→F ordering holds.

## Problem

(Axis 1 — JTBD) loom-spec emits a per-change change-folder (proposal.md + `specs/
<capability>/spec.md` delta), and slices 1–2 made the loom-code side read tags into an
index + drift gate. But loom- still has **no persistent, accumulating "why" layer**: the
cross-cutting model (object state machines, invariants, system-level out-of-scope) and
the per-capability **intent/why/scope** that tests structurally **cannot** hold. Today a
reader — a new contributor, or the next loom-spec cycle — can reconstruct **WHAT** the
system does (from tests) but not **WHY** a capability exists or which cross-cutting
invariants hold. The per-change proposal.md is a working/audit artifact, not a durable
model that survives and accumulates across changes.

Job: **"give loom- a durable, human-authored 'why' layer — a cross-cutting model + a
per-capability intent doc — that persists and accumulates alongside the tests, holding
only what tests can't, so future readers/cycles get the WHY not just the WHAT."**

## Users

(Axis 2) loom-spec authors (writing the model/intent during GENERATE) + future readers:
a new contributor onboarding to a capability, or the next loom-spec cycle reading prior
state (the F slice will machine-consume this; E-core delivers the human-read value +
the persisted substrate F will read). Job story: *When I (or the next cycle) approach an
existing capability, I want a durable doc of its WHY + the cross-cutting invariants, so I
build on the intent instead of re-deriving it from test assertions.*

## Smallest End State

A **persistent intent-layer convention + its structural validator**:
1. **Persistent location (Model α, NEW additive tree)** — `docs/loom/spec/`:
   - `docs/loom/spec/MODEL.md` (**TOP**) — cross-cutting invariants (the `@invariant-ref`
     targets), object state machines, system-level out-of-scope.
   - `docs/loom/spec/<capability>/README.md` (**MID**) — that capability's intent / why /
     scope, where `<capability>` matches the namespace capability key.
2. **Authoring convention** — a new section in `spec-expansion/SKILL.md`: how to author
   TOP vs MID via **cut rule #4** ("remove this capability — does this content get
   deleted?" YES→MID, NO→TOP) + the anti-pattern (**MID MUST NOT restate behavior a test
   owns** — the residual rot surface; human-reviewed, NOT CI-gated).
3. **Structural validator** — checks the intent layer's **presence + shape** when it
   exists: TOP `MODEL.md` present + has the required top-level sections; each capability
   dir has a MID `README.md`. Light/structural only (does NOT police "MID restates
   behavior" — that stays human review).
4. **Tests** — TDD for the validator + a behavioral test for the SKILL convention.

**Not built**: active/deferred status (capstone G consumes it — building it now = an
unread field); the F closed loop (next slice); any relocation of spec-expansion's
existing change-folder output; repo-wide index wiring (capstone).

## Current State Evidence

- **Forward (entry → behavior):** `spec-expansion/SKILL.md:285 §The hybrid output format`
  emits `docs/loom/<change-id>/` = `proposal.md` (7 additive sections) + `specs/
  <capability>/spec.md` (OpenSpec-pure delta). The `### Requirement:` headings in spec.md
  ARE the namespace slice-1 `load_namespace` reads (`living_spec_index.py:18`).
- **Reverse (SSOT ownership):** `validate_spec_output.py` is a **standalone validator**
  (no distribute/sync SSOT — not a functional copy); its `_SKELETON_CHECKS` +
  `_ADDITIVE_CHECKS` registries (`validate_spec_output.py:259,271`) are the clean
  extension point — adding an intent-layer check group mirrors how Task-3 (per its
  comment line 257) appended the additive group. Authorship direction = **loom-spec
  authors, loom-code reads** (#406 split); E-core is purely loom-spec-side.
- **Error (existing failure paths):** each check returns `list[str]` of problems, empty
  == ok; `validate()` (line 282) aggregates. The intent-layer checks follow the same
  contract. The new tree being **absent** must be tolerated (a repo mid-adoption has no
  intent layer yet) — checks fire only when the layer exists, mirroring the
  ui-flows-seam "if absent, ignore" stance (`SKILL.md:78`).
- **Data (contract/shapes):** the change-folder shape is `proposal.md` + `specs/
  <capability>/spec.md`. The NEW persistent tree is `docs/loom/spec/MODEL.md` +
  `docs/loom/spec/<capability>/README.md` — additive, distinct path (`spec/` singular vs
  the per-change `<change-id>/specs/` plural), so no collision with existing output.
- **Boundary (external I/O):** none new — pure file reads (the validator) + a SKILL.md
  doc-convention. The point-don't-copy seam to model is `SKILL.md:53 §Consuming a
  ui-flows.md seed` (F will mirror it; E-core only authors the layer F later reads).

Evidence paths: `loom-spec/skills/spec-expansion/SKILL.md`,
`loom-spec/scripts/validate_spec_output.py`, `loom-code/scripts/living_spec_index.py`
(all on `origin/main`).

## Decision

Build **E-core**: the persistent intent-layer convention (TOP `docs/loom/spec/MODEL.md` +
MID `docs/loom/spec/<capability>/README.md`, cut rule #4, the MID-no-restate anti-pattern
as author discipline) + a **structural validator** (presence/shape, tolerant when the
layer is absent) + tests, authored entirely loom-spec-side.

- **Persistent location = Model α** (a NEW `docs/loom/spec/` tree the change edits in
  place via PR diff), chosen because slice-1's `load_namespace` + the brief's "TOP/MID
  changes go through normal PR review (files in the diff)" both require a STABLE tree, not
  the per-change `<change-id>/` folder. Serenity BDD's **readme-per-container-level** is
  the cited blueprint (parent brief §Industry grounding).
- **Validator extends the existing registry pattern** (a new intent-layer check group in
  `validate_spec_output.py`, or a sibling `validate_intent_layer.py` if cleaner) — checks
  presence/shape only; the layer being absent is tolerated (mid-adoption).
- **Deferred**: active/deferred status (capstone G); the F closed loop (next slice); MID-
  restates-behavior detection (human review per parent brief §Residual rot surface);
  spec-expansion output relocation + repo-wide index wiring (capstone).

## Alternatives Considered (Axis 4)

Industry grounding is inherited from the parent design brief (already WebSearch-sourced):

1. **Serenity BDD — readme.md per container level + a generated tree** (chosen blueprint).
   Persisted intent homed per container, leaf tests annotated. Maps directly to TOP +
   per-capability MID. Source: parent brief §Industry grounding.
2. **Ship status (active/deferred) now, with E** (rejected) — YAGNI: nothing consumes the
   status until the capstone active-coverage check; building it now is an unread field.
3. **Co-locate intent in the per-change folder** (rejected) — the change-folder is
   per-change/transient; the intent layer must persist + accumulate, so it needs a stable
   tree (Model α), not `<change-id>/`.

**My take:** Recommend the chosen E-core (Serenity-style persistent TOP/MID + structural
validator, status & loop deferred). **Conditional reversal:** if the capstone slice lands
sooner than F, pull status forward into the slice that wires the active-coverage check
(status only earns its place beside its consumer).

## What Becomes Obsolete (Axis 5)

Nothing removed — E-core is additive (a new persistent tree + a new validator check
group). It does NOT obsolete the per-change proposal.md (that stays the working/audit
artifact). Note: this is a planned slice from a converged design, not speculative
addition — the "purely additive ⇒ YAGNI" smell is answered by the deferral of status/loop
to where they earn their place.

## Out of Scope

- active/deferred requirement **status** — capstone G (its only consumer).
- **F closed loop** (loom-spec seed reads persisted TOP/MID + INDEX as prior-state) — next
  slice; E-core only authors the layer F will read.
- Relocating spec-expansion's existing change-folder output; repo-wide index wiring; the
  required PR checks — capstone.
- A CI check that **MID doesn't restate behavior** — human PR review per parent brief
  §Residual rot surface (the validator is structural only).

## Open Questions (impl-level)

1. **Validator home** — extend `validate_spec_output.py` with an intent-layer check group
   vs a sibling `validate_intent_layer.py`. Resolve in `writing-plans` (lean: extend the
   existing registry; one validator surface).
2. **TOP required sections** — exact section headers `MODEL.md` must carry (e.g.
   `## Invariants`, `## Object state machines`, `## Out of scope`) for the structural
   check. Pin in `writing-plans`.
3. **Persistent location reconciliation** — how `docs/loom/spec/` (intent) relates to the
   eventual repo-wide namespace/index location is a **capstone** concern; E-core only
   needs the tree to exist + validate.
