---
name: 2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies
description: Anti-copy acceptance greps pass paraphrase copies
status: OPEN
origin: 2026-07-06 loom-memory-skill task 1 quality review — the plan's anti-copy GREEN criterion grepped for verbatim charter-row text; the implementer shipped a complete five-row PARAPHRASE of the charter's jurisdiction table that passed the mechanical grep while violating its intent; only the quality reviewer's judgment leg caught it
start: writing-plans/SKILL.md's next touch, expected to be the slimming arc's slim round 2 pass over that file (2026-07-14-pocock-loom-roadmap-arcs-c-d-e-remainder.md leg D — the deferred leg)
---

- Start: writing-plans/SKILL.md's next touch, expected to be the slimming
  arc's slim round 2 pass over that file
  (2026-07-14-pocock-loom-roadmap-arcs-c-d-e-remainder.md leg D — the
  deferred leg)
- Origin: 2026-07-06 loom-memory-skill task 1 quality review — the
  plan's anti-copy GREEN criterion grepped for verbatim charter-row
  text; the implementer shipped a complete five-row PARAPHRASE of the
  charter's jurisdiction table that passed the mechanical grep while
  violating its intent; only the quality reviewer's judgment leg
  caught it
- What: anti-copy / SSOT-protection acceptance criteria authored in
  plans need TWO legs — the mechanical verbatim grep AND an explicit
  reviewer-judgment check ("no paraphrase reproduction of the
  protected content"); candidate: one line in writing-plans'
  acceptance-criteria guidance + one check hint in the
  plan-document-reviewer prompt.

- **2026-08-13: start condition FIRED and was consciously not taken.** The
  brief-item addressability arc's Task 8 edits
  `loom-code/skills/writing-plans/SKILL.md`, which is this entry's named
  trigger. It was not folded in: the subject here is acceptance-criteria
  authoring guidance (an anti-copy criterion needs a mechanical leg AND a
  reviewer-judgment leg), a different deliverable with its own RED test, and
  taking it would have pushed that plan past its critical-path depth ceiling.
  Recorded rather than skipped silently — the condition stays fired, so the
  next `writing-plans/SKILL.md` touch has no excuse.

- **Split decided 2026-08-13** (open-question-dispatch-gate arc), superseding
  the flat FIRED-but-not-taken note above. The reviewer-prompt leg is
  committed to this arc as Task 7 of
  `docs/loom/plans/2026-08-13-open-question-dispatch-gate.md`: it will add a
  check hint to `plan-document-reviewer-prompt.md` stating that a plan whose
  acceptance criterion protects content from copying must carry BOTH the
  mechanical verbatim grep AND an explicit reviewer-judgment check ("no
  paraphrase reproduction of the protected content"), and that a
  mechanical-only criterion is a gap. As of this writing Task 7 has not yet
  executed — `plan-document-reviewer-prompt.md` carries no such hint and no
  occurrence of "paraphrase" / "anti-copy" / "reviewer-judgment". The
  `writing-plans/SKILL.md` leg is deferred to the slimming arc
  (`2026-07-14-pocock-loom-roadmap-arcs-c-d-e-remainder.md` leg D):
  `SKILL.md` sits at 4249 words against the hard ≤4250-word ceiling pinned
  by `test_word_count_at_most_4250`, and a third ceiling raise is not the
  plan of record. This entry stays `OPEN` until the committed leg (Task 7)
  actually lands; the `start:` condition above tracks both remaining
  triggers — Task 7's landing (to confirm the committed leg shipped) and
  the `writing-plans/SKILL.md` leg's deferred touch — and will narrow to
  just the latter once Task 7 lands.

- **2026-08-14: Task 7 landed — the reviewer-prompt leg shipped.**
  `plan-document-reviewer-prompt.md`'s Check 7 row now carries the
  anti-copy / SSOT-protection rider requiring BOTH the mechanical verbatim
  grep AND an explicit reviewer-judgment check ("no paraphrase
  reproduction of the protected content"), grounded in the five-row
  paraphrase incident. The `start:` above narrowed to track only the
  deferred `writing-plans/SKILL.md` acceptance-criteria guidance leg
  (slimming arc leg D). Entry stays `OPEN` for that leg.

- **2026-08-18: a SECOND failure of the same family measured, and its
  mechanical form rejected on the evidence.** Sibling defect: a
  *self-satisfying* acceptance criterion — `Acceptance.RED` greps a file
  that the same task's `Files touched` lists, so passing it proves only
  that the task wrote the words, never that the described work happened.
  Check 6 accepts it legitimately (a grep IS "a specific failing
  diagnostic"); nothing in Checks 1–18 asks whether the diagnostic is
  satisfiable by the task's own prose. Worked example: this arc's own
  Task 8 RED was first drafted as a completion-tense grep and only
  survived because review caught it — see
  `docs/loom/plans/2026-08-13-open-question-dispatch-gate.md` §Task 8
  Acceptance, whose rationale paragraph is the record (the RED line
  itself is now the corrected decision-tense version).

  A mechanical two-question detector was proposed — (a) is the RED a
  text match (grep / contains)? (b) is the matched file in that task's
  `Files touched`? — and **measured against the corpus before building**:
  220 plans, 213 parsed on the current `## Task N` schema, 1,495 tasks;
  **160 tasks flagged (10.7% of all tasks, 24.5% of the 653 the detector
  can actually decide — 842 are undecidable because their RED names no
  file), across 70 of 213 plans (32.9%)**. Inspection of the flagged set
  shows the detector cannot separate the classes: a RED-as-absence
  pre-check ("does the old pattern still exist before I remove it",
  "these files do not exist yet") is structurally identical to a
  self-satisfying one. The discriminator is whether the task's
  deliverable IS the text or something the text merely asserts — a
  judgment, not derivable from plan text. The proposal's whole selling
  point was that it needed no judgment, so **the mechanical form is
  rejected**: as specified it fires on roughly a quarter of decidable
  tasks, mostly benign. (Measurement script was scratch-only, not
  committed; re-derive from the numbers above if it is needed again.)

  **What survives, and where it goes.** The concern is real; only its
  mechanical form died. The remedy is a *judgment* rider — "does passing
  this RED prove the work, or only that the words were written?" — and
  it belongs on **Check 6** (which already polices `Acceptance.RED`
  quality), exactly mirroring the Check 7 rider this entry already
  shipped for GREEN. That placement is not a fresh guess: the same fork
  was decided four days earlier and the reasoning is recorded verbatim
  in `loom-code/scripts/test_plan_reviewer_anticopy_judgment_leg.py:14-21`
  ("attached to existing Check 7 … rather than a new numbered Check 19").
  A new numbered check costs 7 edit points across 4 files — the row, the
  three hand-maintained contract lines (`checks_passed: <N>/<16>`,
  `check_id: <1-4, 6-14, 16-18>`, the `NEEDS_REVISION` `16–18` mapping),
  `PRE_EXISTING_MAX_CHECK_NUMBER` plus its ledger comment,
  `test_sdd_review_weight_marker.py`'s `<16>` literal, and a new pin
  test — against 2 edit points for a rider, which touches none of the
  hand-maintained lines. This arc is itself the evidence for preferring
  the smaller blast radius: Check 18 shipped INVERTED on its most common
  case and was caught only in review round 2.

  Folded into this entry rather than filed separately: same file, same
  `start:` condition, same conclusion shape (a mechanical leg is not
  enough — add a judgment leg). Doing them together shares the one
  round of edits instead of paying it twice.
