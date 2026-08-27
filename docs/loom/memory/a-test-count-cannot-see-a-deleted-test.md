---
name: a-test-count-cannot-see-a-deleted-test
description: A commit that removes one test and adds another leaves the file's test count unchanged and the suite green, so neither the count nor the green is evidence the removal was intended — a span-cut edit between two helper definitions silently deleted the test sitting between them, and review found it only as four orphaned symbols; diff the collected test NAMES against the previous commit, never the count
type: gotcha
origin: codex/standardize-complexity-gate (stage-specific complexity gates, round-5 delta review, 2026-08-27)
---

A remediation edit removed two helper functions from
`scripts/test_stage_specific_complexity_behavior_evidence.py` by slicing the text
from the first definition to the second — `s[:i] + s[j:]`. A whole test function
sat between them and went with the slice. The same commit added a replacement
test, so the file reported three `def test_` functions before and after, and
`pytest` stayed green on the three that remained.

Nothing surfaced it. The reviewer that eventually caught it reported the
SYMPTOM — four now-unreferenced module symbols — and read it as an orphan-cleanup
miss. Tracing why those symbols went unused is what exposed the deletion.

**Why:** a test count answers "how many tests are here", never "are these the
same tests". Any edit that both adds and removes holds the count still, and the
suite cannot redden over an assertion that is no longer present to fail. This is
the coverage-regression blind spot from
[[retiring-a-mechanism-must-move-its-tests]] arriving by accident rather than by
decision — there, tests were deleted deliberately with the machinery they
guarded; here nobody chose anything.

**How to apply:** prefer an anchored replace over a start/end span cut when
editing source by text surgery — a cut takes everything between the anchors,
including whatever was added there since. Before committing an edit that touched
test files, diff the NAMES:
`diff <(git show HEAD:<path> | grep '^def test_') <(grep '^def test_' <path>)`.
When a reviewer reports unreferenced symbols, ask what stopped referencing them
before deleting them — the answer can be that the caller was removed by mistake,
and then restoring the caller is the fix, not removing the symbols.
