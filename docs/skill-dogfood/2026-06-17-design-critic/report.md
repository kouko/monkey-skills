# Dogfood report — design-critic

- **Skill under test:** `interface-design-toolkit:design-critic` (working-tree, uninstalled)
- **Date:** 2026-06-17
- **Probes run:** A (activation, fallback `fidelity:approximate`), B (executor+auditor — covered by the redundancy dogfood), C (cold-reader)
- **Distractor set:** `completeness-critic` (nearest — spec-behavioral completeness critic), `spec-expansion`, `design-system`, `interaction-flows`, `requesting-code-review`

## Severity summary

| Severity | Count | Status |
|---|---|---|
| Critical | 0 | — |
| High | 1 | FIXED (severity scale undefined) |
| Medium | 3 | FIXED (input contract; input-path+wrong-artifact guard; 7-dim not enumerated) |
| Low | 3 | 2 FIXED ("design view" undefined; agent-type mapping), 1 ACCEPTED (targeted-reseed gap→lens map left to judgment — mirror skill is equally lenient) |

## Probe A — Activation (fallback routing, ≥2 passes)

- **TPR = 10/10** should-fire design-review queries → `design-critic`.
- **TNR = 7/7** distractor queries → correct sibling (zero over-trigger).
- Deterministic across both passes; subtlest discriminations resolved cleanly:
  vs `completeness-critic` (surface vs spec-behavioral — Q8 "DESIGN.md + ui-flows.md
  before spec-expansion" is the sharpest, routed correctly), vs `interaction-flows`
  (critique-existing vs generate), vs `design-system` (review vs create).
- **No trigger-miss, no over-trigger.** `fidelity:approximate` (fallback path; real-harness
  `claude -p` sandbox available but not run — cost).

## Probe B — Output quality + redundancy (executor + blind auditor)

Run earlier against the synthetic invoice-tracker. Panel fired (6 lenses incl. conditional
principles), produced 11 ranked surface omissions (top: Invoice Detail screen never drawn),
non-empty blind spots, never claimed "complete". **Redundancy verdict: UNIQUE=6 / SHIFT-LEFT=5
/ REDUNDANT=0** vs the spec-stage critic — orthogonal on the surface↔behavior axis as the
boundary claims. Friction (boundary drift under load) already folded in via the references
worked-example table.

## Probe C — Cold-reader (zero-context first reader)

Surfaced 7 executability/robustness gaps. Resolution:

| # | Finding | Severity | Fix |
|---|---|---|---|
| 1 | `severity` used in rank formula but never defined | High | Added a 3-point scale (3 blocks-core-job / 2 should-add / 1 polish). |
| 2 | No lens-critic input contract (vs repo Agent Launch Convention) | Med | Added explicit contract: paths + heuristics-ref + persona + lens row. |
| 3 | Input paths assumed; no wrong-artifact rejection guard | Med | Added input-path convention + a STOP guard (decline a spec/code artifact, name the right skill). |
| 4 | "7 UX dimensions" never enumerated in-scope | Med | Enumerated all 7 in `references/design-heuristics.md`. |
| 5 | "the design view" undefined | Low | Defined inline (working copy of artifacts + gaps so far). |
| 6 | Agent-type ("general reasoning agent") left to inference | Low | Named it: the host's general-purpose subagent, never search/explore. |
| 7 | targeted re-seed gives no gap→lens map | Low | ACCEPTED — judgment-executable; mirror skill (`completeness-critic`) is equally lenient. |

Strongest parts (cold-reader): surface-vs-behavior boundary (prose + worked pairs), non-empty
blind-spots rule, ban-"complete", K=2 termination.

## Verdict (floor, not ceiling)

Activation is clean (10/10 TPR, 7/7 TNR) and output is non-redundant. The 6 cold-reader gaps
worth fixing were fixed in this same branch; test suite stays green (13/13 skill test; 62 pkg).
Not a pass-stamp — the human is the final calibrator; raw probe outputs are the transcripts
linked in the task notifications.

## Raw outputs

- Probe A transcript: task `a1311f92b2cb127e3` (17-query corpus × 2 passes).
- Probe B transcript: task `a8e16c6786063f1c2` (executor + blind auditor + redundancy).
- Probe C transcript: task `a9f9d419cfcdbdfd7` (cold-reader 5-question set).
