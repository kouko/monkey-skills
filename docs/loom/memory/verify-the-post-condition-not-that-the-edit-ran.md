---
name: verify-the-post-condition-not-that-the-edit-ran
description: A scripted edit can report success on every observable signal — the assert passed, the script printed its summary, the citation checker stayed green — while having produced a structurally broken artifact; `text.replace("## Notes", block + "## Notes", 1)` matched an inline mention inside a task's own Description, split that task in two and created a dependency cycle, and only the next reviewer saw it
type: gotcha
origin: branch docs-reuse-adequacy-brief-and-backlog (loom-code 0.43.0, 2026-08-01) — plan-document-reviewer round that returned five cascading gaps
---

A new task block was inserted into a plan with
`text.replace("## Notes", task_block + "## Notes", 1)`. The **first** literal
`## Notes` in the file was not the heading — it sat inside Task 1's own
Description ("from the pinned vocabulary in ## Notes"). The block landed
mid-sentence: Task 1 was cut in half, the remainder of its Description became a
heading reading `## Notes; \`Intended\` specifies…`, and Task 6's declared
dependency on a Task 7 that now had no heading closed a cycle.

Every check said fine. The script's `assert` passed — the string *did* exist.
The script printed `plan amended: T7 added, 6 -> 7 tasks`. `check_doc_citations.py`
stayed green, because no citation had been touched. The orchestrator then quoted
the header it had just written back as evidence the structure was sound. The
break was found by the next `plan-document-reviewer`.

**Why:** an assertion that the anchor was *found* tests the precondition of the
edit, not its result. Every signal in that list measured the action; none
measured the artifact. Quoting a value you just wrote as confirmation that
writing it worked is circular, and it reads exactly like verification.

**How to apply:** anchor structural edits on a line-start-plus-newline form
(`"\n## Notes\n"`), never a bare substring that can legitimately appear in
prose. Then assert the **post-condition** before writing — heading counts, one
heading per expected section, an acyclic dependency graph — and re-derive it
from the file after writing. Beware the mirror-image trap when writing that
check: a naive `"## Notes;" not in text` post-condition later false-fired on the
paragraph *describing* this incident, because it tested a substring instead of a
line start. Related: [[a-silently-skipped-edit-reports-as-a-completed-one]]
(the same family — a tool that no-ops on a non-match reports the skip as a fix).
