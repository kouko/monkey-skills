# distill-sessions proposals — 2026-05-22

**Target SKILL.md**: `/fake/skills/example/SKILL.md`
**Counts**: 1 addition(s), 0 modification(s), 0 anchor mismatch(es), 1 pending cross-session evidence, 1 deferred to v0.2.

> No silent writes — review the proposals below, then run `python -m apply --approved ...` to commit the diff.

## Proposed additions

### Addition 1 [insert into §When to use]

```
**Successful pattern: parallel subagent dispatch**

_Success: dispatched 3 implementers in parallel, all returned DONE._

When tasks are file-disjoint and Independent: true, dispatch all implementers in a single assistant message with multiple Agent tool calls.

_(supported by 2 session(s): session-aaa-111, session-bbb-222)_
```

## Proposed modifications

_(none)_

## Anchor mismatch — needs review

_(none)_

## Cross-session evidence pending

_These items were observed in only 1 session and did not reach the minimum cross-session evidence threshold (min_n=2). They are NOT auto-applied — re-run after more sessions accumulate to promote them._

### Use Read before Edit on existing files
_Failure: agent attempted Edit before Read; tool errored._

When editing an existing file, always invoke Read first so the harness can track file state. Edit fails on un-Read files.

_Observed in 1 session: `session-aaa-111` — re-run after more session evidence accumulates._

## Marked for v0.2

_These proposals require new reference files; per Q4 of the v0.1 brief, defer them to a future iteration._

### Add new section: edge-case taxonomy for cross-plugin delegation
_Would require a dedicated reference file (>500 token taxonomy)._

**Target section**: §Anti-patterns
**Kind**: success
**Deferred to v0.2**: requires new reference file (per Q4 — v0.1 is SKILL.md only).

Comprehensive edge-case taxonomy for cross-plugin delegation including path-resolution, gate-bypass refusal, version-mismatch detection, and structured-seed-context passing. Best owned by a new references/cross-plugin-delegation.md file.

_source session: `session-bbb-222`_
