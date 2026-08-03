# Brief: completeness-critic diverse-critic panel (v0.2.0)

> Source: `docs/spec-toolkit/design/2026-06-12-diverse-critic-decorrelation-and-experiment.md`
> (Part A design + Part C 2-run defect-seeding experiment). This brief turns the
> experiment-validated design into a buildable change. Date: 2026-06-12.

## Problem

(Axis 1 — JTBD)

When completeness-critic sweeps its 5 fixed lenses as a **single agent doing
sequential blind passes**, the passes still **anchor on each other** (shared
context within one agent) and **drift off-lens** (one agent hunting "everything"
produces noisy, overlapping findings). The job to be done: **recover the
omission classes a generic omissions-hunt is structurally blind to (above all
NFR/security) while keeping each critic in its lane** — so the panel finds *more
distinct* gaps with *far less noise*, and **never manufactures a false
completeness signal**. The empirical lever for this (validated, not assumed) is
**decorrelating the critics**: distinct defect-class mandate + persona + input
view per lens, run as a real panel with fresh context, unioned.

## Users

(Axis 2)

The **agent running completeness-critic** (this skill is agent-portable like
`research-toolkit:deep-research`) — invoked on-demand by a human reviewing a
`spec-expansion` draft, after GENERATE and before code-toolkit VERIFY. Not a hot
loop: a human triggers it per spec draft, reads the round summary + blind spots,
then decides whether to feed the extended spec to VERIFY. Cost tolerance is
moderate (a panel of N subagents × loop rounds), acceptable because it runs once
per spec review, not per commit.

## Current State Evidence

(Touches existing code: `spec-toolkit/skills/completeness-critic/SKILL.md` v0.1.0, 194 lines)

- **Forward** (what runs today): `§The multi-lens fixed interrogation checklist`
  (`SKILL.md:79-113`) defines **5 fixed lenses** — (1) missing object/actor,
  (2) state completeness, (3) cross-object & system-layer failures, (4) NFR
  [incl security], (5) policy/legal/permissions — instructed to "run them as
  **separate passes** … blind to the others" (`SKILL.md:82-84`). This is a
  **single-agent sequential checklist**, NOT a dispatched panel: no per-lens
  persona, no per-lens input view, no fresh context per lens.
- **Reverse** (SSOT / who owns what): the executable contract is
  `spec-toolkit/scripts/validate_spec_output.py` — it checks `## Blind spots —
  needs human/field input` is present AND non-empty (`SKILL.md:191-193`). The
  SKILL.md owns the *behavioral* lens spec; the validator owns the *structural*
  required-section gate. **This change touches only the behavioral half
  (SKILL.md) — the validator is intentionally NOT modified** (the panel +
  overlap diagnostic are disciplines, not new required sections; keeping the
  fuzzy diagnostic out of a binary gate is deliberate).
- **Error** (failure-handling today): `§loop-until-dry` (`SKILL.md:61-77`) K=2
  consecutive dry rounds; `§Ban claiming "complete"` (`SKILL.md:147-152`) bans
  the word `complete`. Honesty rails exist but say **nothing about a statistical
  completeness % / capture-recapture estimate** — the exact false-completeness
  failure the experiment isolated (`design §A1`, `§Part C H2`).
- **Data** (the lens list + tags): lenses are prose-enumerated; provenance tags
  are `seeded` / `inferred` / `critic-found` (`SKILL.md:163-171`).
- **Boundary** (existing emphasis): `§Dual role` (`SKILL.md:46-58`) already says
  the critic is "refocused not lighter" under v0.2 and **wins the
  single-object-failure regime**; NFR/security is currently just lens #4 of 5
  with **no load-bearing emphasis** — yet the experiment found it the **#1
  unique-recovery lens** (`design §Part C H4`).
- **Evidence paths**: `spec-toolkit/skills/completeness-critic/SKILL.md`,
  `spec-toolkit/scripts/validate_spec_output.py`,
  `docs/spec-toolkit/design/2026-06-12-diverse-critic-decorrelation-and-experiment.md`.

## Smallest End State

(Axis 3 — minimum shippable resolution)

A **v0.2.0 SKILL.md-only** change that turns the lens checklist into an
experiment-validated **diverse-critic panel**:

1. **Panel dispatch (the core).** Reframe `§The multi-lens fixed interrogation
   checklist` so each lens is dispatched as **one critic subagent with fresh
   context** (portable fan-out, phrased abstractly like deep-research — "dispatch
   one subagent per lens", not bound to one harness), each carrying a **distinct
   persona** (e.g. malicious user / confused first-timer / 3am on-call ops /
   compliance auditor / competitor probing edges) and, where it helps, a
   **distinct input view** (draft-only vs **original-requirements-only** to catch
   "requirements entail X, draft dropped it"). Findings are **UNIONed**, then
   deduped + re-seeded (existing loop).
2. **nfr_security = load-bearing #1.** Promote the NFR/security lens to the
   panel's most-load-bearing mandate with an explicit "generic hunting is
   structurally blind here" note (experiment H4); permissions/data-boundary
   secondary.
3. **Overlap-rate diagnostic.** After each round, note pairwise finding-overlap
   qualitatively: high overlap (~>70%) → "panel not diverse enough, add a more
   orthogonal lens", with the **explicit honesty rail: high overlap signals
   redundancy, NOT near-completeness** (the capture-recapture misread).
4. **Reject the completeness estimate.** A new honesty rule banning any
   **capture-recapture point estimate / completeness percentage** (same-base-model
   critics are positively correlated → estimator under-counts residual → false
   completeness). Reinforces the existing "ban complete" word-level rail with the
   statistical-level rail.
5. **Lens deletability (Bitter Lesson).** A one-paragraph design note: each lens
   is designed **deletable** — a future stronger model that subsumes a lens
   unaided can have it removed without redesign; re-baseline periodically.

Version bump `0.1.0 → 0.2.0`. Tighten the overlapping `§Dual role` prose so the
panel framing doesn't duplicate it.

## Decision

**Build:** the 5 deltas above, **all in `completeness-critic/SKILL.md`**. The
change is a **single-module structural reframe** of the lens section + 2 short
new rules (overlap diagnostic, reject-estimate) + 1 design note (deletability) +
an nfr_security emphasis pass + version bump.

**Do NOT build:**
- **No capture-recapture estimator / completeness-%** — the experiment rejected
  it (homog false-completeness reproduced, `design §Part C H2`). We *ban* it, we
  don't ship it.
- **No validator change** — the panel + overlap diagnostic are behavioral
  disciplines surfaced in the round summary, not new validator-enforced required
  sections. Keeps the change one module and keeps a fuzzy diagnostic out of a
  binary gate.
- **No new lens beyond the existing 5** — the experiment validated the existing
  defect-class partition; the change is *how* they run (panel vs checklist),
  not *which* classes.
- **No script** (no `scripts/overlap.py` etc.) — overlap is a qualitative
  round-summary judgment, not a computed metric this version needs.

**Why:** the experiment's headline value is **~3–4× precision + NFR/security
recovery + higher saturation ceiling**, driven by *decorrelation* (persona +
input-view + fresh context per lens) — none of which the current single-agent
checklist delivers. Recall lift is modest, so the change is deliberately scoped
to the decorrelation mechanism + the honesty rails, not a coverage expansion.

## Alternatives Considered

(Axis 4 — alternatives were tested **empirically in this repo**, stronger than a web search)

1. **Single-agent N-blind-passes + personas (no subagent dispatch)** — cheaper,
   but one agent's passes anchor on shared context → weaker decorrelation. The
   experiment's decorrelation (overlap 0.22–0.40 vs 0.67–0.96) came from
   *fresh-context* critics. **Rejected** as the primary mechanism; the panel
   dispatch is the validated lever.
2. **Capture-recapture completeness estimate** — a number for the unseen
   residual. **Rejected** (`design §A1` + `§Part C H2`): correlated same-base
   critics → systematic under-estimate → false completeness (the most dangerous
   honesty failure). Kept only as a banned anti-pattern.
3. **Add more lenses (expand defect classes)** — **Rejected**: the experiment
   validated the *existing* 5-class partition; the gap was decorrelation, not
   coverage breadth. Adding lenses without decorrelation just adds noise.

Named industry grounding (from the design doc's research, not re-searched):
**Basili Perspective-Based Reading** (distinct-perspective inspectors out-detect
homogeneous ones), Anthropic **Planner-Generator-Evaluator** (writer≠judge),
Leveson input-space partitioning. The panel = PBR applied to spec omissions.

## What Becomes Obsolete

(Axis 5)

- The **"run them as separate passes … blind to the others"** single-agent
  framing (`SKILL.md:82-84`) is replaced by the panel-dispatch framing — removed
  in the same change, not left as a contradictory parallel instruction.
- Part of `§Dual role` (`SKILL.md:46-58`) that hand-waves "refocused not lighter"
  is tightened so it doesn't duplicate the new explicit panel + load-bearing-lens
  spec.

## Out of Scope

- `validate_spec_output.py` — untouched (no new required section).
- `spec-expansion/SKILL.md` — untouched (writer half; this is the judge half).
- Any new script under `spec-toolkit/scripts/`.
- A gold-fixed critic-variance experiment variant (design §Part C confound note)
  — deferred; not a build prerequisite.
- Model-diversity lever (different model family per critic) — aspirational,
  single-family host today (`design §A3` lever 5).

## Open Questions

None blocking. The panel-vs-checklist fork and the validator-untouched decision
are both resolved above (committed, not open).
