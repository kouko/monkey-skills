# systems-thinking-toolkit v0.4 — Dogfood Audit

**Date**: 2026-05-13
**Branch**: `feat/systems-thinking-toolkit-v0.3.0`
**Plugin state at audit time**: v0.4.0 (8 functional + 1 router), plugin mean 109.67/A, carry-1 cld-craft 120/120

## Test design

Three parallel fresh-opus subagents simulating distinct user contexts.
Each subagent had access to plugin files but no prior conversation
context.

| Test | Subagent role | Input | Skills invoked |
|---|---|---|---|
| A | systems-thinking practitioner | Prose summary of plugin's own 5 same-day PRs (v0.1.0 → v0.4.0 evolution including quota gates, race conditions, audit drift) | cld-craft → cld-archetypes |
| B | SaaS founder | "Retention dropped 6 months ago, doubled CS team, didn't help — onboarding stale, 4 majors shipped, 200:1 CSM ratio" | cld-craft → cld-archetypes → strategy-lever-and-cascade |
| C | "User who has never seen the plugin" | Engineering manager prose: code-review quality decline (12 engineers, 3 senior, +30% quota, juniors slow, seniors firefighting) | /stt router → resulting skill |

## Test A — Meta-dogfood (self-analysis)

**Result**: plugin successfully diagnosed its own development trajectory.

- cld-craft produced 7-node + 6-dangle CLD with 2 R-loops + 1 B-loop on
  cognitive load + 1 B-loop on coherence + Marginal Insight as
  one-way modifier (not a closed loop).
- cld-archetypes Step-0 router correctly classified as
  limits-to-growth from per-cycle delta sequence (105 → 108.4 →
  109.3-109.7 → 109.2 → 109.67); ran Branch L with Branch V flagged
  as secondary note (oscillation < deceleration × 3).
- Binding brake identified: cognitive-load (B2), with audit-diminishing-
  returns queued as next brake. Intervention: cycle-boundary cognitive
  reset + scope quantization.

## Test B — End-to-end chain (3-step deliverable)

**Result**: full carry-1 → consumer → strategy chain ran without
re-deriving inputs between steps.

- cld-craft: produced 3 vicious R-loops (workload-proficiency, review-
  depth-via-senior-participation, morale-self-reinforcing) + 1
  starved B-loop (review-depth capacity-suppressed). Diagnosed as
  inverted-limits-to-growth.
- cld-archetypes: Branch L correctly fired. Binding brake = Onboarding
  Adequacy. Next-queued brake = stable CSM ratio target.
- strategy-lever-and-cascade: produced 6 lever changes including the
  non-intuitive HOLD on CS headcount (the "don't pedal harder" move).
  Hand-off from B's "constraint-relief intervention" to C's "lever
  target change" was direct translation, no rethinking.

## Test C — Router intelligence (cold-start user)

**Result**: router correctly recommended cld-craft from prose with
brief disambiguation friction.

- Router's "I have a tangled situation — I want a logic diagram"
  row matched the prose unambiguously. "vicious cycle" trigger
  language fired correctly.
- Brief ambiguity: subagent considered whether to route directly to
  cld-archetypes (since prose has "death spiral" / "vicious cycle"
  language). Resolution: reading the "I have a CLD — now what?"
  section header revealed the prerequisite.
- cld-craft then produced 3 vicious R-loops + 1 starved B-loop
  diagnosis with highest-leverage intervention (decouple senior
  firefighting from same seniors doing review + mentoring).

## Findings — strengths confirmed

1. **carry-1 cld-craft is genuinely carry-1**: nobody needed to load
   `loop-and-link-primitives` first to emit a complete R/B-classified
   CLD. v0.4 R3-3 absorption holds.
2. **Mermaid block + Markdown caption is a working hand-off contract**:
   downstream skills consume the caption (not the Mermaid), and the
   `%%` + caption redundancy survives renderer differences.
3. **B's HOLD lever was the load-bearing output**: the 3-step chain
   surfaced "don't hire more CSMs" as the strategic move. A single
   big agent would likely have given a "hire more" recommendation.

## Findings — friction points

| # | Source | Friction | v0.4-PR fix? |
|---|---|---|---|
| 1 | A | cld-craft → cld-archetypes router needs 1-step inference | ✅ fixed in this PR (behavioral signature line) |
| 2 | A | candidate-loop-vs-modifier halt rule missing | deferred to v0.5 |
| 3 | A | archetypes "Both at once" no magnitude rule | deferred to v0.5 |
| 4 | A+B | cases.md 391-line front-load = limits-to-growth itself | ✅ fixed in this PR (cases-index.md) |
| 5 | B | vicious-R-loop-in-limits-to-growth vs standalone needs disambiguation | deferred to v0.5 |
| 6 | B | strategy Steps-2-3 vs Steps-4-8 lacks explicit stop | deferred to v0.5 |
| 7 | B | "HOLD lever" not named pattern | deferred to v0.5 |
| 8 | C | router archetypes row missing prerequisite | ✅ fixed in this PR (prerequisite callout + trigger phrases) |
| 9 | C | "vicious cycle" trigger may pull toward archetypes | ✅ fixed in this PR (trigger phrases moved to cld-craft row) |

## v0.5 backlog

- (#2) loop-classification-protocol.md halt rule: "candidate loop that
  on tracing goes back to start only through a non-feedback modifier =
  one-way modifier, not loop"
- (#3) cld-archetypes Step-0 magnitude rule for "Both at once" case
- (#5) cld-archetypes Branch L disambiguation: vicious R-loop as
  *brake mechanism in coupled limits-to-growth* vs *standalone
  runaway* (different intervention)
- (#6) strategy-lever-and-cascade explicit "STOP after Step 4 if
  scenario uncertainty low" rule
- (#7) strategy-lever-and-cascade named pattern: current-drifted-target
  → explicit HOLD lever
- New case candidates: plugin self-analysis (Case 11 in cld-craft
  cases.md; Case A4 in cld-archetypes) — software-engineering /
  agent-orchestration domain fills Sherwood's pre-platform-economy
  blind spot

## Conclusion

v0.4 is dogfood-validated. The carry-1 emergence + R3 CLD-centric
restructure produced a coherent toolkit where 3 distinct user contexts
(self / SaaS / cold-start) successfully reached actionable artifacts.
Friction points are concentrated in cross-skill hand-off discoverability
and case-loading cognitive load — both addressable as small patches.
This PR ships fixes for the 3 highest-ROI friction items; the remaining
6 ship in v0.5.
