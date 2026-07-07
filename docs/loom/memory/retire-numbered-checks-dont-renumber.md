---
name: retire-numbered-checks-dont-renumber
description: When a numbered check/criterion is dropped but other files cross-reference it by number, retire it in place (mark permanently N/A) rather than renumber — renumbering cascades edits into every file citing a specific number
type: process
origin: PR #516 (writing-plans time-box removal, 2026-07-08) — plan-document-reviewer-prompt.md's Check 5 retired, not renumbered
---

Removing writing-plans' ≤5-min task-sizing criterion also meant retiring
`plan-document-reviewer-prompt.md`'s Check 5 (the check that enforced it).
The obvious move — delete the row, renumber 6→5, 7→6, ... 16→15 — was
rejected: multiple OTHER files in the plugin (`subagent-driven-development/
SKILL.md`, `writing-plans/references/plan-format.md`) cross-reference
specific check numbers like "Check 16" by literal number, not by name.
Renumbering would have required finding and updating every one of those
cross-references across the whole plugin, with no compiler to catch a
missed one.

**What was done instead:** Check 5's row stays in place, reworded to
"RETIRED — always N/A, never applied", with an explicit "never fails, do
not emit a gap under any circumstance" instruction. The `checks_passed`
denominator and the gap `check_id` range were updated to exclude it
(`<14>` and `<1-4, 6-14, 16>`), matching the existing pattern for Check 15
(an advisory-only check that already never fails).

**Why:** numbered enum/index values that other files reference by number
are an external contract, even inside one plugin — the same reasoning
that keeps deprecated API enum values retired-not-reused. A skipped
number in a list looks odd but costs nothing; a silently-wrong
cross-reference (Check 16 now meaning something else) is a real defect
that's easy to miss because nothing greps for it automatically.

**How to apply:** before renumbering ANY numbered check/step/criterion
list, grep the whole plugin for `Check N` / `criterion N` / `step N`
references to that specific number. If any exist outside the file being
edited, retire in place instead of renumbering — reuse the "advisory,
never fails" framing already established for Check 15 as the template.
