# Blind source-audit — W18 replay (audit-b)

Audits the three native replay decision sets against the frozen sources:
the runtime caller contract (SKILL.md Step 6 items 2–4), the target SKILL.md,
the cited references, and the raw detector findings. I did not produce the
replays and read only the sources listed in the brief.

## Source basis (all verified by file:line)

- Runtime caller contract:
  `/private/tmp/toolkit-w18-replay-20261124/runtime/skill-dev-toolkit/skills/skill-consistency-check/SKILL.md`
  Step 6 items 2–4 (merge-and-report review rules).
- Target: `/private/tmp/toolkit-w18-replay-20261124/inputs/original/target/SKILL.md`
- References read in full:
  `references/equivalence-check-protocol.md`, `references/multi-judge-ensemble.md`,
  `references/refactor-moves-catalog.md`, `references/golden-anchor-protocol.md`,
  `references/package-resource-mode.md`.
- Raw findings: `inputs/original/read-1.json`, `inputs/original/simulate-1.json`.
- Decisions audited: runs `trial`, `run-2`, `run-3` (all three `decisions.json`
  present; all six candidates F1–F7 decided in each).

Key line facts confirmed against the sources:
- SKILL.md:346 "Not-triggers — do NOT invoke for:"; SKILL.md:358–360 creative /
  non-deterministic output (writing style, prose, design feel) → abort, use
  `skill-tuning`.
- SKILL.md:106–107 Q1 pass rule requires structural OK + `PASS_HIGH`/`PASS_MODERATE`
  from the reducer.
- SKILL.md:128 `<5%` reduction / no reduction → **REJECT**.
- SKILL.md:155–165 overall verdict: **PROCEED = all three pass strictly**; **REJECT**
  for Q1 fail / Q2 increase-or-no-reduction / Q3 violated.
- SKILL.md:368–369 delegates "Q1's structural + semantic check details" to
  `equivalence-check-protocol.md` and "how to spawn 3 independent judges … consensus
  rules" to `multi-judge-ensemble.md`.
- `multi-judge-ensemble.md`:3–4 scopes itself to "Q1's Layer 2 semantic check";
  :150–163 structural-only skip (all three conditions); :162 "Layer 1 pass =
  PROCEED"; :165–166 "For any non-deterministic / prose / creative output, run the
  full ensemble."
- `equivalence-check-protocol.md`:13–24 Layer 1 token-count ±20%, pass rule all 5,
  Layer 1 failure → REJECT immediately; :85–91 >30% reduction marked suspicious
  "even if both layers pass"; :119–123 non-deterministic/creative → self-abort,
  recommend `skill-tuning`.

## Per-candidate ratings

Rating key: PASS = disposition supported by sources; FAIL = demonstrated material
semantic defect (overbreadth, unsupported confirmation, or unsupported exclusion).

### read-1.json F1 (all three runs: excluded)

**Original `why` scope:** Every target whose output is creative, prose, or
non-deterministic is asserted to require both abort/routing and a full ensemble;
no qualifier limits prose to taste-sensitive/creative prose. Disjunctive,
covers all prose.

**Governing sources:** SKILL.md:358–360 scopes the do-not-invoke/abort rule to
"creative / non-deterministic" output, with "(writing style, prose, design feel)"
as a parenthetical example category, not a blanket over all prose.
`multi-judge-ensemble.md`:165–166 says run the full ensemble for
non-deterministic / prose / creative output.

**Judgment:** Exclusion is correct. The original elevates "prose" (a parenthetical
example of creative/non-deterministic output) into a separately sufficient,
universally applied exclusion over ALL prose, including deterministic factual
prose. SKILL.md's abort rule is scoped to creative/non-deterministic output, so a
deterministic prose output need not abort, and no abort-vs-ensemble conflict
arises for it. Per Step 6 item 3, an overstated original is excluded even though a
narrower creative/non-deterministic tension is real; the narrower concern is not a
substitute for the unchanged claim. The replay keeps "prose" within its
source-assigned category.

| Run | Status | Rating | Reason |
|-----|--------|--------|--------|
| trial | excluded | PASS | Correctly excludes the overstated original; keeps prose in source category. |
| run-2 | excluded | PASS | Same; reason quotes sources and scopes prose as parenthetical example. |
| run-3 | excluded | PASS | Same; counterexample (deterministic prose) refutes asserted category coverage. |

### read-1.json F2 (trial excluded; run-2 confirmed; run-3 confirmed)

**Original `why` scope:** Structural-only round (all three skip conditions, Layer 1
pass) with marginal/failing Q2 or violated Q3 is claimed to receive incompatible
overall PROCEED and REJECT decisions.

**Governing sources:** `multi-judge-ensemble.md`:3–4 scopes the file to Q1's Layer
2 semantic check; :152–163 grant permission to SKIP THE ENSEMBLE (Q1-local) when all
three conditions hold; :162 "Layer 1 pass = PROCEED" is within that Q1-scoped
delegation. SKILL.md:155–165 reserves overall PROCEED for all three checks passing
strictly and REJECTs on Q2 no-reduction or Q3 violation. The skip exception waives
the ensemble only; it does not waive Q2/Q3.

**Judgment:** Exclusion is defensible (trial). `ensemble.md`'s "PROCEED" is a
Q1-level pass produced by Layer 1, not an overall-verdict override of Q2/Q3; the
governing overall rule is SKILL.md's all-three requirement. Keeping the structural
branch fixed, Layer 1 can clear Q1 while Q2 still rejects (no reduction) — no
incompatible overall action exists. Confirmation (run-2/run-3) reads Q1-local
"PROCEED" as an overall-proceed mandate beyond `ensemble.md`:3–4's delegated scope;
that is an unsupported confirmation / overbreadth.

| Run | Status | Rating | Reason |
|-----|--------|--------|--------|
| trial | excluded | PASS | Defensible: Q1-local PROCEED does not override Q2/Q3; no overall conflict. |
| run-2 | confirmed | FAIL | Unsupported confirmation: reads Q1-local PROCEED as overall override of Q2/Q3. |
| run-3 | confirmed | FAIL | Same defect as run-2. |

### simulate-1.json F1 (all three runs: confirmed)

**Original `why` scope:** Narrower than read F1 — when target output is
non-deterministic or creative, one file requires running the full ensemble while
SKILL.md/equivalence protocol require aborting and routing to `skill-tuning`. Does
NOT assert the abort rule for all prose.

**Governing sources:** `equivalence-check-protocol.md`:119–123 — non-deterministic /
creative output → Layer 2 unreliable, skill self-aborts, recommend `skill-tuning`.
SKILL.md:358–360 — same class → do not invoke, use `skill-tuning`.
`multi-judge-ensemble.md`:165–166 — same class → run the full ensemble.

**Judgment:** Confirmation is correct. This is a genuine, in-scope action conflict
for the creative/non-deterministic class that both sources explicitly address with
opposite instructions (self-abort before Q1 vs run the full Q1 ensemble). A
deterministic-prose counterexample does not refute this narrower claim, which is
exactly scoped to non-deterministic/creative output.

| Run | Status | Rating | Reason |
|-----|--------|--------|--------|
| trial | confirmed | PASS | Genuine supported conflict; correctly scoped (not all prose). |
| run-2 | confirmed | PASS | Same; reason correctly notes read-F1 prose overbreadth is absent here. |
| run-3 | confirmed | PASS | Same; holds a concrete creative target fixed and finds incompatible actions. |

### simulate-1.json F3 (trial excluded; run-2 confirmed; run-3 confirmed)

**Original `why` scope:** Identical in substance to read F2 — structural-only round,
Layer 1 pass, Q2 or Q3 fails; claims ensemble reference commands overall PROCEED
vs entry requiring rejection.

**Governing sources:** Same as read F2 — `multi-judge-ensemble.md`:3–4 (Q1-scoped),
:152–163 (skip ensemble, Q1-local), :162 ("Layer 1 pass = PROCEED"); SKILL.md:155–
165 (overall PROCEED = all three; REJECT on Q2/Q3 failure), :128 (no reduction →
REJECT).

**Judgment:** Same as read F2. Exclusion is defensible (trial): `ensemble.md`:162's
PROCEED is Q1-local, scoped to the Q1 Layer 2 semantic check delegation
(`ensemble.md`:3–4), and does not waive Q2/Q3. Confirmation (run-2/run-3) is an
unsupported confirmation / semantic defect: it lifts the Q1-local word out of its
delegated scope and treats it as an overall-verdict override.

| Run | Status | Rating | Reason |
|-----|--------|--------|--------|
| trial | excluded | PASS | Defensible: Q1-local PROCEED does not override Q2/Q3; no overall conflict. |
| run-2 | confirmed | FAIL | Unsupported confirmation: Q1-local PROCEED read as overall override. |
| run-3 | confirmed | FAIL | Same defect as run-2. |

## Design question 1 — read-1.json F1 (the preregistered W17 veto)

**Answer:** The W18 replay does NOT reproduce the W17 overbreadth class on read
F1. It excludes F1 in all three runs and keeps the parenthetical ("prose")
within its source-assigned category: an example of "creative / non-deterministic"
output under SKILL.md:358–360, not a standalone universal exclusion over all prose.
By contrast with W17's overbroad confirmation/exclusion pattern, W18 correctly
excludes the unchanged overstated original while preserving the narrower
creative/non-deterministic tension (which is separately and correctly confirmed as
simulate F1). The preregistered veto is honored.

## Design question 2 — F2 / simulate F1 / simulate F3: defect direction vs defensible

- **read F2 / simulate F3 (same sources, same logic):** Exclusion is defensible;
  confirmation is the semantic defect. `multi-judge-ensemble.md` is explicitly
  scoped to Q1's Layer 2 semantic check (:3–4); its structural-only "Layer 1 pass
  = PROCEED" (:162) is Q1-local permission to skip the ensemble, not an
  overall-verdict override of Q2/Q3, which SKILL.md:155–165 governs (PROCEED = all
  three strictly; REJECT on Q2 no-reduction / Q3 violation). Confirmation overreads
  a Q1-scoped delegation as an overall mandate → unsupported confirmation (FAIL).
  Trial's exclusion is correct (PASS).
- **simulate F1:** Confirmation is defensible and correct (PASS); exclusion would be
  the defect. It is narrowly scoped to non-deterministic/creative output, where
  `equivalence-check-protocol.md`:119–123 / SKILL.md:358–360 (self-abort,
  skill-tuning) and `multi-judge-ensemble.md`:165–166 (run full ensemble) prescribe
  genuinely incompatible actions for the same class — a real conflict, not
  overbreadth.

## What I did not check

- I did not verify the SHA256 hashes in each `decisions.json` `sources` map against
  the original detector JSON bytes (the merge script validates structure/coverage
  and hashes, not reason truth).
- I did not read `references/test-prompts-schema.md`; it is not cited by any of the
  four candidates under audit (F5/F6/F7 only), so it bears on none of them.
- I did not read any other run directory's `caller-review.md`, any W17 evidence
  file, `grading-spec.md`, session notes, or `*.summary.json`, per the brief
  boundaries.
- I did not run the detectors, the merge script, or any network/install step.
