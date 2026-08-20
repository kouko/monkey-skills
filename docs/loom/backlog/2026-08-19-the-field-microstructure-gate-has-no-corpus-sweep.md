---
name: 2026-08-19-the-field-microstructure-gate-has-no-corpus-sweep
description: check_field_microstructure.py is invoked only by the three skills that author a plan or brief, never by CI and never over the corpus, so a document written outside that route is never measured — and the corpus it would measure is 216 of 224 plans failing, because the arc's retrofit deliberately covered 5 plans and 4 briefs, not the history
status: open
origin: field-value-microstructure close-out (2026-08-19) — found at rebase, when the arc's own gate flagged a plan that had arrived on main from a concurrent arc
start: next touch of the loom CI workflows, or the second time a non-compliant plan is noticed in the corpus
---

The gate ships as an authoring-time check with exactly three callers:
`writing-plans` runs it at intake and again before reviewer dispatch,
`plan-document-reviewer` Check 19 binds the reviewer to running it, and
`brainstorming/SKILL.md` runs `--brief` as a pre-handoff self-check. Nothing
runs it over `docs/loom/plans/` or `docs/loom/specs/` as a set, and no CI
workflow references it at all (verified 2026-08-19: `grep
check_field_microstructure .github/workflows/` returns nothing across all 19
workflows).

So the rule holds exactly as far as the skills reach. A plan authored by a
session that did not route through `writing-plans`, or by one running an older
plugin version, is never measured.

**This is not hypothetical.** `docs/loom/plans/2026-08-19-think-orbit-transparency-both-faces.md`
merged to main (PR #711) while this arc's checker was still on an unmerged
branch. It carries a 2,071-character `Description` first line and a
2,241-character `GREEN` — precisely the defect the rule exists to prevent.

**Size the gap correctly before designing for it.** Measured 2026-08-19:
**216 of 224 files under `docs/loom/plans/` exit 1**. This arc's retrofit was
deliberately narrow — 5 plans and 4 briefs, the documents the brief named —
never the history. The think-orbit file is not a straggler in a clean corpus
and not even the worst instance: `2026-08-07-loom-arc4b-finishing-collapse.md`
carries 3,555 characters and `2026-08-07-loom-direction-layer.md` 2,255, so it
ranks third.

**Why it was not retrofitted — the arithmetic, not the scope argument.** At
1-of-216, reshaping that one file would not make the shipped corpus consistent
with the rule; it would make one file consistent and leave 215. Picking it
because a rebase happened to surface it is arbitrary. (It is also another arc's
closed record and outside this arc's declared scope, but those are the weaker
reasons and should not be the ones a future reader inherits.)

**Why that matters beyond one file.** The retrofit is a snapshot, and the
snapshot was always partial. Any arc running concurrently reopens whatever gap
was closed, and nothing reports it — the next person to notice will be whoever
runs the checker by hand, as happened here, at a rebase rather than at
authoring.

**Candidate mechanism, not decided.** A CI job that runs both modes over
`docs/loom/plans/*.md` and `docs/loom/specs/*.md` would close it, but it must
answer two questions first, and the first is the expensive one: what happens to
the 216 already-failing plans — a date floor, an opt-in marker, or a one-time
sweep of the whole history. A CI job added without answering it fails on day
one against nearly every document in the repo. Second, and independent of
scale: whether a closed record should be editable at all to satisfy a rule
adopted after it closed.
Answering the second badly turns every future rule into a corpus-wide rewrite.

Related: [[2026-08-13-a-widened-field-grammar-has-no-mechanical-consumer-enumeration]]
(the same family — a rule whose consumers are enumerated by hand rather than
derived).
