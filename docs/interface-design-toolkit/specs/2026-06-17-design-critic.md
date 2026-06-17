# Brief — design-critic: writer≠judge omission critic for the design surface

**Date:** 2026-06-17
**Plugin:** `interface-design-toolkit` (new skill `design-critic`)
**Type:** new skill (SKILL.md + references). Mirrors `spec-toolkit:completeness-critic` structurally.

## Problem

(Axis 1 — JTBD) The design station emits `DESIGN.md` + `ui-flows.md`, then they are validated
**structurally only** (`validate_design_output.py` checks section *presence*, not content) and fed
straight to spec-expansion. There is **no writer≠judge blind-spot hunt on the design surface** — the
one pipeline station without an adversarial completeness gate (spec has completeness-critic; code has
requesting-code-review incl. P2's principles dimension; design has nothing). So surface omissions —
an undrawn error/empty screen, a navigational dead-end, a screen no flow reaches, a missing exit —
propagate into spec + code where they cost more to fix.

Job story: *When the design station has produced ui-flows.md/DESIGN.md, I want an independent critic
to hunt the surface omissions the designer missed (missing render-states, dead-ends, unreachable
screens, modality gaps) BEFORE the spec is expanded — so the loop can run with less human design
review and gaps are caught at the cheapest stage.*

Industry (Axis 4, WebSearch EN+JA): this is **heuristic evaluation** (Nielsen & Molich) — the
canonical structured expert-review method that catches UI usability/omission problems **early,
without users**; JP sources confirm it catches 抜け漏れ including empty/error/loading 画面状態.
Automated analogue: **UICrit** (arXiv 2407.08850, a UICritique dataset for automated design
evaluation). Distinct from a casual critique: structured, heuristic-grounded (NN/G).

## Users

(Axis 2) An agent (or kouko) running the interface-design pipeline on a feature, right after
`design-system` + `interaction-flows` have emitted into `docs/interface-design-toolkit/`, before
handing `ui-flows.md` to spec-expansion. Modality-aware (GUI/TUI/CLI). Key-free, host-agent model.

## Smallest End State

(Axis 3) A new skill `interface-design-toolkit:design-critic` that **reuses completeness-critic's
proven panel pattern** (writer≠judge, fresh-context lens subagents decorrelated, loop-until-dry,
union+dedup+rank, mandatory non-empty blind-spots honesty rail) but with **design-surface lenses
grounded in canon — NOT a freshly invented checklist**:

- Lenses = **Nielsen's 10 usability heuristics** intersected with the **existing 7 UX dimensions**
  (`interaction-flows/references/ux-flow-checklist.md`) + render-state coverage. Concretely, the
  load-bearing design lenses:
  1. **Render-state completeness** (Nielsen H1 visibility of status) — every surface's
     empty / loading / error / success variant present? (the flag rule already names these)
  2. **Dead-end & exit / user control** (Nielsen H3 user control & freedom) — every surface offers
     forward/back/out; destructive actions reversible/undo; no dead-ends (dim 6).
  3. **Navigation reachability & entry coverage** (Nielsen H2/H7) — every screen reachable; all
     entry points enumerated (dim 5); no orphan screens.
  4. **Error prevention & recovery** (Nielsen H5/H9) — error screens designed; confirms on
     irreversible actions.
  5. **Modality fit & accessibility** (Nielsen H4 consistency + a11y) — responsive/narrow-terminal/
     non-TTY-piped variants flagged (dim 7); a11y omissions.
- **Boundary** (mirror "flag here, fan-out there"): design-critic hunts **surface/usability
  omissions** on ui-flows.md/DESIGN.md; it does NOT hunt spec behavioral omissions (completeness-
  critic) or code (review). Surface-completeness, not behavioral-completeness.
- **Governed by PRINCIPLES.md** if present (omission-framed, like completeness-critic's lens 6 from
  P2): "what principle-entailed UI surface did the design omit?" — N/A no-op when absent.
- **Router wiring**: `using-interface-design-toolkit` routes to design-critic AFTER design-system +
  interaction-flows emit (the router currently has no review step).
- **Bitter-Lesson note** (carry completeness-critic's): the panel (writer≠judge) is
  verification-class → keep; each lens is deletable; re-baseline periodically.

## Current State Evidence

- **Forward:** `interface-design-toolkit/scripts/validate_design_output.py` is **structural only**
  (docstring: "checks the change-folder STRUCTURE (presence + well-formedness)"; `_CHECKS` =
  presence + 8-section + ui-flows-sections substring). No semantic/omission layer → design-critic is
  the missing semantic gate above it (exactly as completeness-critic sits above spec-expansion's
  structural output).
- **Pattern source:** `spec-toolkit/skills/completeness-critic/SKILL.md` — the panel machinery
  (multi-lens fresh-context dispatch :105-141; loop-until-dry K=2 :57-98; the 5 lenses :187-218;
  blind-spots rail :220-228; Bitter-Lesson deletable-lens note :146-159). REUSE the pattern; the
  lens *content* differs (design-surface vs spec-behavioral). Separate plugin → reference, don't copy.
- **Lens grounding source:** `interaction-flows/references/ux-flow-checklist.md` (the 7 dimensions +
  render-variant flag rule: empty/loading/error/success; dim 6 "kill dead-ends"; dim 5 entry points;
  dim 7 density+modality). Plus Nielsen's 10 heuristics (canon — must cite, not reinvent).
- **Router:** `using-interface-design-toolkit/SKILL.md` has NO critic/review step (grep = 0) — the
  wiring is an addition.
- **Boundary precedent:** P1 established the surface(design)/depth(spec) split; design-critic
  inherits it.

## Decision

Build `interface-design-toolkit:design-critic` as a new skill mirroring completeness-critic's
writer≠judge panel, with **design-surface lenses grounded in Nielsen's heuristics + the 7 UX
dimensions** (cite canon, do not invent a checklist), a PRINCIPLES.md omission lens (N/A when
absent), and router wiring to run it after the design artifacts emit. We will **NOT** duplicate the
structural validator, **NOT** hunt spec-behavioral omissions (completeness-critic's job), **NOT**
invent a novel heuristic set (ground in Nielsen + existing 7 dims). Verify by dogfooding against
`~/pipeline-dogfood/invoice-tracker/`'s ui-flows.md — confirm it surfaces real surface omissions —
AND **run a comparison check against completeness-critic** to test the redundancy risk below.

## Alternatives Considered

(Axis 4 — WebSearch EN+JA)
1. **Heuristic evaluation / expert design review** (Nielsen-Molich; NN/G; UICrit arXiv 2407.08850) —
   **CHOSEN.** Canonical, catches omissions early without users; EN+JA converge.
2. **Add a design lens to completeness-critic instead of a new skill** — **REJECTED.** Different
   plugin, different artifact, different stage; a new skill keeps the design station self-contained
   (parallels the principles/interface split) — but see redundancy risk.
3. **Invent a fresh design-completeness checklist** — **REJECTED** per
   `feedback_synthesized_checklist_likely_reinvents_canon`: a self-authored checklist reinvents
   Nielsen's heuristics. Ground in canon.
4. **Rely on the structural validator + downstream completeness-critic** — **REJECTED** as the
   default, but this is the redundancy risk to actually test (below).

## What Becomes Obsolete

(Axis 5) Nothing deleted. Additive (new skill + router step). The structural validator stays (design-
critic is the semantic layer above it). Verification-class scaffolding (writer≠judge) →
Bitter-Lesson-proof per `feedback_two_kinds_of_scaffolding_bitter_lesson`.

## Out of Scope

- Spec-behavioral omission hunting (completeness-critic owns it).
- A visual/screenshot critic (agent-device runtime) — design-critic reads the text artifacts only.
- Replacing/extending `validate_design_output.py` structural checks.
- Full TUI/CLI modality build (separate P3 item) — design-critic is modality-aware in its lenses but
  doesn't depend on the TUI/CLI build.

## Open Questions

- **Redundancy risk (must test, not assume):** does design-critic find surface/usability omissions
  that `completeness-critic` (one stage later, on the spec) would NOT recover? Per
  `feedback_spec_coverage_value_greenfield_regime` + `feedback_l3_journey_nav_coverage_not_regime_gated`,
  state-coverage value is regime-dependent. **Plan a comparison dogfood**: run both on the same seed;
  if completeness-critic recovers everything design-critic finds, design-critic's value is only
  shift-left (cheaper-stage), not unique recall — surface that honestly before declaring it
  load-bearing. (This is the same eval discipline P1/P2 used.)
- Lens count / which Nielsen heuristics are load-bearing vs deletable — a writing-plans / dogfood
  detail; default to the 5 above, prune by the comparison result.
