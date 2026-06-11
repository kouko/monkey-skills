# Brief: brainstorming greenfield UI-coverage nudge (Tier 1)

> **Type**: brainstorming brief (input to `writing-plans`)
> **Date**: 2026-06-11
> **Status**: Brief signed off → plan
> **Driver**: kouko — close the cheap part of the greenfield UI-coverage gap
> **Grounding**: 3-archetype greenfield A/B + memory `feedback_spec_coverage_value_greenfield_regime`; `docs/spec-toolkit/research/2026-06-11-spec-toolkit-openspec-research-synthesis.md`

## Problem
(Axis 1 — JTBD)

When starting a **UI/interaction feature in a greenfield / thin-context area**, the agent's brainstorming is evidenced-thin on systematic UI-state/edge enumeration — it does intent (why/smallest/alternatives) well but skips the empty/error/loading/transition/permission/boundary sweep, so those states get discovered one-by-one in the running app later. A 3-archetype greenfield A/B measured this gap: plain brainstorming covered 8/17 (eyedropper), 6/12 (collections), 3/13 (side-by-side) of the intrinsic UI states; the full spec-toolkit lens covered 16/17, 12/12, 13/13. The job: **add a cheap, greenfield-gated reminder so the common UI-state categories get enumerated up front** — the part that needs no cross-plugin machinery.

This is **Tier 1** of a two-tier design. Tier 2 (judge → delegate the full coverage to `spec-toolkit:spec-expansion`) is **deferred** because it must ride the OpenSpec change-folder contract, whose consumption side (writing-plans reading change-folders = the OpenSpec DECLARE layer, 2026-05-30 brief Q6=A) is unbuilt. Tier 1 is independent of that.

## Users
(Axis 2 — who, conditions)

kouko (and any code-toolkit user) starting a UI/interaction/stateful feature in a **greenfield or thin-context** area — a new app (e.g. a future komado-Viewfinder-style project) or a feature in a part of the codebase with little existing pattern to recon. **NOT brownfield** — there, brainstorming's Current-State-Evidence recon already recovers the coverage (the A/B showed ≈parity in brownfield), so the nudge must stay out of brownfield's way (else dead text).

## Smallest End State
(Axis 3)

A few prose lines added to `code-toolkit:brainstorming` that fire **only when both**: (a) Current-State-Evidence is `N/A — greenfield` / thin, AND (b) the feature has a UI / interaction / stateful surface — reminding the agent to enumerate states across the standard categories — **empty / error / loading / state-transition / permission / boundary** — before finalizing the brief. Plus a **forward-pointer**: for high-coverage / high-risk greenfield, the full systematic lens lives in `spec-toolkit:spec-expansion` (Tier 2 — active once writing-plans reads OpenSpec change-folders; deferred).

The reminder is a **category prompt**, not a method: it names the lens categories so the agent sweeps them; it does **not** reproduce spec-toolkit's BVA/state-machine/permission method (that stays SSOT in spec-toolkit).

## Current State Evidence

- **Forward (trigger signal already exists)**: `code-toolkit/skills/brainstorming/SKILL.md:145-146` — the `## Current State Evidence` section already requires marking `N/A — greenfield`; that determination IS the Tier-1 gate (no new detector needed). `:176+` `## Cross-skill delegation` table — natural home for the forward-pointer row to spec-toolkit.
- **Reverse (output / SSOT)**: brainstorming's output is the brief at `docs/code-toolkit/specs/`; `writing-plans` consumes it. Tier 1 only enriches the brief's content — no distribution/sync script, no SSOT mechanism involved (pure in-skill prose).
- **Error**: N/A — prose/behavior change to one SKILL.md; no runtime error paths.
- **Data**: the lens **categories** (empty/error/loading/state-transition/permission/boundary) are the reusable content. The **full method/matrix** SSOT is `spec-toolkit/skills/spec-expansion/SKILL.md` — Tier 1 must reference categories only, never copy the method (DRY).
- **Boundary**: `code-toolkit` plugin only; **zero cross-plugin dependency** (Tier 1's defining constraint). The folder-structure hook + SKILL.md token budget (~6000) apply. brainstorming is currently ~? tokens; the addition must stay within budget.

Evidence paths: `code-toolkit/skills/brainstorming/SKILL.md`, `spec-toolkit/skills/spec-expansion/SKILL.md`.

## Decision

Add to `code-toolkit:brainstorming` a **greenfield-gated, UI/state-surface-gated lightweight reminder** to enumerate UI states across the six standard categories before finalizing the brief, plus a **forward-pointer** to `spec-toolkit:spec-expansion` for the heavy greenfield case (noted as Tier 2 / deferred-wiring). Guard it so it does **not** fire in brownfield (where recon covers it) or for non-UI features. **NOT** built: any delegation/invocation of spec-toolkit, any OpenSpec contract / change-folder reading, any spec-toolkit change, any cross-plugin dependency.

## Out of Scope
- **Tier 2** — brainstorming judging + delegating the full spec to `spec-toolkit:spec-expansion` (depends on the OpenSpec DECLARE wiring).
- **OpenSpec DECLARE wiring** — writing-plans reading OpenSpec change-folders (the 2026-05-30 brief slice Tier 2 needs).
- Any edit to spec-toolkit.
- Brownfield firing (explicitly gated out).
- A skill-discovery/registry mechanism (over-engineering; the forward-pointer just names spec-toolkit).

## Alternatives Considered
(Axis 4 — grounded in the repo's own shipped delegation patterns + the investigation)
- **Inline reminder (chosen, Tier 1)** vs **cross-plugin delegate now (Tier 2)** — delegation is the right *eventual* mechanism but must ride the OpenSpec change-folder contract (unbuilt consumption side); deferred. Inline reminder is independent and ships now.
- **Unconditional UI lens in brainstorming** — rejected: brownfield A/B showed it'd be near-dead-text there (recon already covers); must be greenfield-gated.
- **spec-toolkit description-only (self-activate)** — rejected: relies on the user remembering to invoke; doesn't fix the "step gets skipped" problem.

## What Becomes Obsolete
(Axis 5)
Nothing removed — additive prose to one skill. Forward-looking: when Tier 2 + OpenSpec DECLARE wiring land, the forward-pointer becomes an active delegation; the Tier-1 reminder remains as the lightweight path for cases that don't escalate. (Additive → mild YAGNI flag, mitigated: targets an *evidenced* gap, and the cost is a few prose lines.)

## Open Questions
- **Tier-1 lift is a hypothesis** (per the A/B-baseline lesson): does adding the reminder actually raise greenfield coverage above the no-nudge baseline (8/17 etc.)? **Acceptance includes a post-build A/B** (greenfield with-nudge vs without, same seeds) to confirm it's not dead text — if it doesn't lift, reconsider.
- Exact gate wording for "has a UI/interaction/stateful surface" (vs pure-logic/data features) — refine in plan; keep it a judgment cue, not a rigid detector.
- Test strategy: the change is prose in a SKILL.md → grep-test guarding the load-bearing additions (the six categories named, the greenfield+UI gate, the forward-pointer, the DRY guardrail line) + the behavioral A/B as the real proof.
