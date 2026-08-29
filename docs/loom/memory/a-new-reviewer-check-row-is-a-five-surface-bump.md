---
name: a-new-reviewer-check-row-is-a-five-surface-bump
description: Appending a check row to plan-document-reviewer-prompt.md moves five surfaces in one commit — the row itself, the prompt's own output-contract counts (denominator + two check-id ranges), the obligation-sweep max-row constant, two sibling <N> literals, and the tracked-byte fingerprint — grep the pin tests for the old count before shipping the row
type: gotcha
origin: direction-surfacing branch, Check 22 addition (2026-08-29)
---

The plan-document-reviewer's checks table is pinned from four
directions: `test_plan_reviewer_output_contract_count.py` derives the
applicable total from the table and compares it to the prompt's own
output-contract lines (`checks_passed: <N>/<20>`, the `check_id` range,
the NEEDS_REVISION range); `test_plan_obligation_sweep.py` pins the
table's legitimate maximum row number as a constant; and
`test_sdd_review_weight_marker.py` plus
`test_writing_plans_complexity.py` hardcode the denominator literal.
Adding Check 22 without touching those turned the suite red in four
places, and each fix round also re-triggered the loom-code
tracked-byte fingerprint.

**Why:** the pins exist to stop silent renumbering and stale contracts,
so they fire on a legitimate new row exactly as hard as on an accidental
one; the cost is that "add one row" is never a one-file edit.

**How to apply:** before committing a new check row, grep the scripts
tree for the old denominator (`<19>`-style literals), the old maximum
row number, and the old ranges; retarget them in the SAME commit as the
row — the release-ritual pattern in
[[tracked-byte-pin-tests-repin-in-the-same-commit-as-the-bytes]] —
then re-pin the fingerprint last.
