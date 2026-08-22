---
name: 2026-08-22-check-19-version-tag-carries-two-meanings-in-one-table
description: the plan-document-reviewer prompt's check table uses one `(vX.Y.Z+)` notation for two different things — every other row means "introduced in" and never moves, while row 19 alone is bound by a live test to the current shipping version, so after every bump row 19 falsely asserts the check did not apply at the previous version
status: open
origin: 2026-08-22 code-as-spec-lens-no-op-bar arc — the 0.93.0 → 0.94.0 bump made row 19 read `(v0.94.0+)`, and a whole-branch docs reviewer filed the notation collision as an evidence-class finding
start: the next touch of plan-document-reviewer-prompt.md's check table, or of test_check19_version_tag_matches_shipping_version
---

- The collision. In `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`,
  rows 5, 13, 14, 17 and 18 carry tags like `(v0.13.0+)`, `(v0.8.0+)`,
  `(v0.43.0+)`, `(v0.79.0+)`. They mean *introduced in that version* and never
  move again. Row 19 carries the same notation but is pinned by
  `test_check19_version_tag_matches_shipping_version` to whatever
  `plugin.json` currently reads, so it moves at every bump.

- What that makes row 19 assert. Read by the table's own convention, a row
  tagged `(v0.94.0+)` says the check did not apply at 0.93.0. Check 19 did
  apply at 0.93.0 — it was introduced at `6e0a835e`, which shipped 0.93.0.
  The tag is true against its test and false against its table.

- Why it matters beyond tidiness: the reviewer contract's Rule R1 dates a
  verdict against a rubric revision. A version tag that means two things
  defeats that dating for whichever row the reader guesses wrong about.

- Two fixes, and the choice is a real one. Either mark row 19's tag as a live
  shipping pin with distinct notation, so the table carries two clearly
  different things; or stop moving it and let it mean "introduced in 0.93.0"
  like every other row, which retires
  `test_check19_version_tag_matches_shipping_version`. The second is smaller
  and restores one meaning to the notation; the first keeps whatever the live
  pin was buying, which nobody has yet written down.

- Not fixed in the arc that surfaced it: the finding is evidence-class and
  non-gating, the defect predates that arc's changes, and deciding between
  the two fixes means deciding what the live pin is for — which is a question
  for whoever owns that test, not a rider on a version bump.

- Evidence: the whole-branch docs review of `dogfood-deployed-lens-run`,
  finding on `plan-document-reviewer-prompt.md` row 19, recorded in that
  branch's PR body.
