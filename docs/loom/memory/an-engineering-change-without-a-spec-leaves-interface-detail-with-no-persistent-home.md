---
name: an-engineering-change-without-a-spec-leaves-interface-detail-with-no-persistent-home
description: When needs-design is no, the charter sends behaviour detail to a spec that does not exist — the exact interface an implementer needs (ids, exit codes, output shapes) then survives only in dispatch packets, which never enter the repo; until a lightweight engineering spec or an evidence note is the named home, write that packet text into docs/loom/<change-id>/evidence/ before dispatching, so a resumed build can find it
type: gotcha
origin: 2026-09-05-artifact-charter-boundaries-and-edit-rights — eight implementer dispatches returned zero NEEDS_CONTEXT, every one carrying 60–100 lines of interface text the 40-word plan fields could not hold; the plan charter's must_not sends behaviour to spec, and the change had none
---

The field caps did what they were meant to: the plan stayed at one line per
field. The detail did not disappear — it moved into the orchestrator's
dispatch packets (rule ids, BLOCK line shapes, exit codes, policy id names).
Those packets are transcript text; a resumed build or a later reader has no
way to recover them.

**Why:** the charter's `must_not` column is exhaustive by design and sends
"behaviour or REQ restatement" to the spec. An engineering change with
`needs-design: no` has no spec, so the column points at nothing. The
Current State Evidence section (≤30 words a line) is a fact list, not an
interface description.

**How to apply:** for an engineering change whose tasks carry a non-trivial
interface, either open the minimal spec (`contract/templates/spec-minimal.md`,
Requirements + the interface table, no decision point ②) or save each
dispatch packet's interface section under `docs/loom/<change-id>/evidence/`
before the dispatch, and point the task's Test line at that file. The A/B run
of this change measured it: on one task, two cold implementers each asked 2
questions of the 4,633-word plan and 3 then 4 of the 941-word charter plan;
the question unique to the charter arm every time was the design rationale.
The charter needs a named home for that rationale on engineering changes
before the caps can claim to be free.
