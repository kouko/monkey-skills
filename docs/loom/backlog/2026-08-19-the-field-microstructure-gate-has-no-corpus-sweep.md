---
name: 2026-08-19-the-field-microstructure-gate-has-no-corpus-sweep
description: check_field_microstructure.py is invoked only by the skills that author a plan or brief, never by CI and never over the corpus, so a document written without routing through writing-plans bypasses it silently — already demonstrated by a plan merged to main while the checker was still unmerged, whose Description first line is 2071 characters
status: OPEN
origin: field-value-microstructure close-out (2026-08-19) — found at rebase, when the arc's own gate flagged a plan that had arrived on main from a concurrent arc
start: next touch of the loom CI workflows, or the second time a non-compliant plan is noticed in the corpus
---

The gate ships as an authoring-time check: `writing-plans` runs it at intake
and before reviewer dispatch, and `plan-document-reviewer` Check 19 binds the
reviewer to running it. Nothing runs it over `docs/loom/plans/` or
`docs/loom/specs/` as a set, and no CI workflow references it at all
(verified 2026-08-19: `grep check_field_microstructure .github/workflows/`
returns nothing).

So the rule holds exactly as far as the skills reach. A plan authored by a
session that did not route through `writing-plans`, or by one running an older
plugin version, is never measured.

**This is not hypothetical.** `docs/loom/plans/2026-08-19-think-orbit-transparency-both-faces.md`
merged to main (PR #711) while this arc's checker was still on an unmerged
branch. It carries a 2,071-character `Description` first line and a
2,241-character `GREEN` — the largest instances in the corpus, and precisely
the defect the rule exists to prevent. It was deliberately NOT retrofitted:
it belongs to another arc, it is a closed record, and reshaping it was outside
this arc's declared scope (the retrofit covered the corpus as it stood when the
arc was planned).

**Why that matters beyond one file.** The retrofit is a snapshot. Any arc
running concurrently with a corpus-wide reshaping reopens the gap the moment it
merges, and nothing reports it — the next person to notice will be whoever runs
the checker by hand, as happened here, at a rebase rather than at authoring.

**Candidate mechanism, not decided.** A CI job that runs both modes over
`docs/loom/plans/*.md` and `docs/loom/specs/*.md` would close it, but it must
answer two questions first: what happens to the older pre-rule corpus
(2026-08-10..14 briefs still exit 1, correctly outside the retrofit's scope) —
a date floor, an opt-in marker, or a one-time sweep — and whether a closed
record should be editable at all to satisfy a rule adopted after it closed.
Answering the second badly turns every future rule into a corpus-wide rewrite.

Related: [[2026-08-13-a-widened-field-grammar-has-no-mechanical-consumer-enumeration]]
(the same family — a rule whose consumers are enumerated by hand rather than
derived).
