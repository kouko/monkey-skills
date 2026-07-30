# Craft-trap probe — cold copywriter-evaluator, round-2 re-gate (1.15.0)

Date: 2026-07-30 · Branch: `feat-copywriting-convergence-modernization` (pre-merge)
Recipe: the evidence-class trap probe (see repo memory
`docs/loom/memory/docs-review-dogfood-must-probe-the-evidence-class-trap.md`),
adapted from loom-code 0.42.0's instruction/evidence split to
copywriting-toolkit 1.15.0's contract/craft split.

## Setup

- Cold agent (no arc context), **sonnet tier** — deliberately below the
  evaluator's designed opus tier, so a pass demonstrates the weak floor.
- Prompt: act as `copywriter-evaluator`, read the real agent contract +
  voice-tone gate SKILL + voice-consistency rubric + CLAUDE.md (branch
  state), render the Voice Consistency verdict for a round-2 re-gate.
  Blind: no hint that a trap exists.
- Fixture: `fixture-envelope-round2.json`. Round-1 findings carried
  verbatim: R1-F1 `contract` (cute-register subline violating declared
  `tone_notes.axis_target` — FIXED in the current draft) and R1-F2
  `craft` (staccato headline rhythm — deliberately left unchanged).

## Trap semantics

A converging evaluator must return a PASSING verdict: the only surviving
round-1 finding is craft-class, which is recorded and never gates. The
retired rule ("2 or more 🟡 → NEEDS_REVISION") or round-1 re-litigation
("the rhythm is still clipped" reworded as a new finding) would both
produce a wrong NEEDS_REVISION.

## Result — CLEAN (all oracles held)

| Oracle | Outcome |
|---|---|
| Verdict is passing | ✅ `PASS_WITH_NOTES` |
| R1-F1 (contract, fixed) → fix-verified with quote | ✅ quoted the revised subline |
| R1-F2 (craft, surviving) → non-gating recorded note | ✅ yellow flag explicitly marked "Craft-class, non-gating (per contract-class-only aggregation)"; suggestion labeled optional |
| No re-litigation of closed/recorded findings | ✅ noted "no round-1 fix was requested for this since it was recorded, not mandated" |
| New findings still allowed at round 2 | ✅ raised a genuinely new contract-class finding (see below) |

Unplanned discriminator: the fixture's hand-written quadrant label
`"Q2-companion"` (non-standard, drifting toward Q3 evidence style) was
surfaced as a NEW contract-class finding — so the final picture held TWO
🟡 flags (one craft non-gating, one contract new). Under the retired
count rule this exact picture is a NEEDS_REVISION; the 1.15.0 semantics
correctly returned PASS_WITH_NOTES driven by the contract finding alone.
The probe therefore exercised both halves: craft-never-gates AND
count-accumulation-retired, in one run.

## Caveats

- Single run, sonnet, one gate (voice-consistency Mode 2). Ethics
  checklist mode (FATAL/FIXABLE) not probed — its semantics were
  unchanged by this arc.
- The evaluator was simulated via a general-purpose subagent reading the
  agent contract (the in-session dispatch path), not a headless
  end-to-end pipeline run.
- Post-run fixture correction (whole-branch review 🟢): the
  `audit_trail` entries were re-sorted into chronological order — the
  as-probed file listed the round-2 `skill-entered` entry first, an
  order an append-only trail cannot produce. Entry contents unchanged;
  the probe verdict did not depend on trail order.
