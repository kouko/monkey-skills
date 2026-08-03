# Brief: completeness-critic v0.2.1 — panel dogfood hardening

> Source: dogfood report `docs/spec-toolkit/dogfood/2026-06-12-completeness-critic-panel-dogfood.md`
> (ran the shipped v0.2.0 panel on the PiP-note-app draft). Date: 2026-06-12.
> Pattern mirror: spec-expansion v0.2.1 (PR #390) — real-execution dogfood surfaced adoption gaps the design + per-task review missed.

## Problem

(Axis 1 — JTBD)

The shipped completeness-critic **v0.2.0 panel works** (the dogfood found 4 🔴 high-value omissions the writer was blind to), but executing it on a real draft surfaced **two adoption gaps that are both consequences of the v0.1.0→v0.2.0 single-agent→panel change** — machinery inherited from the cheap single-agent era that wasn't reconciled with the new panel's cost and 5-way-union shape. Job: make the panel **actually runnable end-to-end without the executor being pulled to skip the loop, and without dumping 40 raw findings back into the spec**.

## Users

(Axis 2) The agent executing completeness-critic on a real spec draft (human-triggered, per spec review). Same as v0.2.0.

## Current State Evidence

(Touches `spec-toolkit/skills/completeness-critic/SKILL.md` v0.2.0, shipped `55abacb1`)

- **Forward**: `## loop-until-dry` (the round/termination rule) was **inherited verbatim from v0.1.0** — re-seed every gap, sweep all lenses, terminate after **K=2 consecutive dry rounds**. Written when a "round" was one agent's 5 cheap blind passes. v0.2.0 made each round **5 fresh-context subagent dispatches** but did NOT revisit the loop cost → K=2-dry ≈ 15 subagent calls. The dogfood executor was pulled to skip the loop (F-1, the F-1-pairwise-bypass pattern).
- **Reverse** (SSOT): the executable contract `scripts/validate_spec_output.py` checks `## Blind spots` non-empty + skeleton — it does NOT gate the loop or the consolidation. **No validator change** in this fix (both gaps are behavioral prose).
- **Error / write-back**: `## How you write back` assumes a **single consolidated finding list** (re-seed gaps as `critic-found` + candidate GIVEN/WHEN/THEN). The v0.2.0 panel emits a **5-way UNION with cross-lens duplicates** (dogfood: durability 2×, multi-device-merge 3–4×, autocomplete-privacy 4×); there is **no dedup-rank-triage step** between UNION and write-back → 40 raw findings risk dumping noise into the spec (F-2).
- **Data**: `### Overlap-rate diagnostic` is advisory prose, not a forcing step; the round-summary line half-implies reporting it (F-3, minor).
- **Boundary**: the experiment's ~3–4× precision win is **per-critic** (lens-scoping); the **panel-level union** still needs a merge/rank pass to realize panel-level precision — currently unspecified.
- **Evidence paths**: `spec-toolkit/skills/completeness-critic/SKILL.md`, `docs/spec-toolkit/dogfood/2026-06-12-completeness-critic-panel-dogfood.md`.

## Smallest End State

(Axis 3) A **v0.2.1 SKILL.md-only** prose hardening, 3 changes:

1. **F-1 — loop cost off-ramp (🔴).** Reconcile `## loop-until-dry` with the panel's per-round cost. Re-seeding becomes **targeted, not blanket**: after round 1, re-dispatch **only the lens(es) whose re-seeded gaps open a genuinely new object/actor/state-class**, and escalate to a **full** second panel round only when a re-seed surfaces a new defect *class* — not a blanket K=2-dry re-sweep of all 5 critics. Keep K=2-dry as the *logical* stop; bound the *mechanism* to "re-run a lens only when its input actually changed." Name the cost explicitly (a panel round = N subagents) so the executor doesn't silently skip the loop to save cost.
2. **F-2 — consolidation step before write-back (🟡).** Add a short step between UNION and `## How you write back`: **dedup semantically across lenses → rank by (severity × number-of-lenses-that-found-it)** (cross-lens convergence is the precision signal) → re-seed **only the ranked load-bearing set** as `critic-found` + candidate scenarios; the long tail goes under blind-spots/residue, never padded into the spec.
3. **F-3 — overlap forcing line (🟢).** One line making the overlap judgment a **reported** item in the round summary (not just advisory).

Version `0.2.0 → 0.2.1`.

## Decision

**Build:** the 3 prose changes above, all in `completeness-critic/SKILL.md`. Single-module.

**Do NOT build:** no validator change (behavioral, not structural); no script (consolidation is a qualitative rank, like the overlap diagnostic — no `scripts/rank.py`); no change to the 5 lenses / personas / panel-dispatch mechanics (those dogfooded as working); no change to the capture-recapture ban or deletability note.

**Why:** both gaps are v0.2.0 coherence debts (inherited cheap-single-agent machinery vs. the new expensive panel). Fixing them is what makes the validated panel actually adoptable — exactly the spec-expansion v0.2.1 precedent (imperative discipline + shape-fit). Scope is deliberately the loop-cost + union-consolidation reconciliation, not new capability.

## Alternatives Considered

(Axis 4)
1. **Leave loop-until-dry as-is** — rejected: the dogfood showed the executor skips it under panel cost (F-1 is the same real adoption gap class as spec-expansion's pairwise-bypass, which we DID fix in v0.2.1 there).
2. **A `scripts/rank.py` for consolidation** — rejected (complexity-critique deletion-first): ranking by severity×convergence is a qualitative judgment like the overlap diagnostic; a script would over-engineer a fuzzy call and add a non-stdlib-ish surface for no precision gain.
3. **Drop loop-until-dry entirely for the panel** — rejected: experiment H3 showed diverse panels climb higher and sometimes aren't saturated at 5 critics → the loop genuinely adds; the fix is to make it *cost-targeted*, not delete it.

## What Becomes Obsolete

- The blanket-K=2-dry **mechanism** framing (re-run all 5 critics) is replaced by targeted re-seed; the K=2-dry *logical stop* survives.
- The implicit "findings arrive pre-consolidated" assumption in `## How you write back` is replaced by an explicit consolidation step.

## Out of Scope

- `validate_spec_output.py`, `spec-expansion/SKILL.md`, any new script.
- The PiP dogfood spec itself (kouko's product, local-only — do not publish).
- Re-running the full panel dogfood as a build prerequisite (the report is the discovery).

## Open Questions

None blocking.
