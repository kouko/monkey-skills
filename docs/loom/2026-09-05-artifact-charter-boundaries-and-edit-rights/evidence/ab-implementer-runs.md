# W3-01 harness: two cold implementer runs on the same task

## Chosen task

**T7 — params.md 的木色預設值更正** (both plan versions carry this task under
the same id/title). Chosen because:

- Its Files (`docs/loom/params.md`, `blender/build_mesh.py`,
  `src/kumiko/output/measurement.py`) exist verbatim in the sample repo at
  the base commit below — nothing to fabricate.
- Its Test is concrete and mechanically checkable: three named `核桃木`
  hits in `params.md`, each verified against a value read back from two
  other files, not asserted from memory.
- It sits mid-plan (task 7 of 12), depends on exactly one prior task (T2,
  already landed at the chosen base commit), so the run does not need the
  whole plan replayed to reach a valid starting state.
- Its own real landing commit (`b25f634` in the sample repo) shows the
  implementer had to discover a second, pre-existing doc defect (the CLI
  flag has no hex default at all — `default=None`) beyond what either
  plan version's Test line states outright. That gives the comparison a
  genuine chance to produce a NEEDS_CONTEXT in either arm, rather than a
  trivially clean task that can't discriminate.

## Base commit and scratch clone

- Source repo (read-only origin for the clone): `/Users/kouko/GitHub/kumiko-zaiku-app-icons`
- Base commit: `c1d8cc7` (T3's landing commit — T2's constants are shipped,
  T7 itself is not yet done; this is the parent of T7's own real landing
  commit `b25f634`, i.e. the state right before T7 was implemented).
- Both runs clone fresh from this same base commit into two separate
  scratch directories. Neither run's clone ever touches the other's, and
  neither touches the source repo.

## Dispatch packet (identical for both runs except the plan path)

```
### Task
Implement task T7 — params.md 的木色預設值更正 — from the plan below.
This is a read-only reconnaissance-and-report run: do NOT commit, do NOT
push, do NOT modify any file. Read what you need, determine the RED and
GREEN this task's Test line describes, and report your findings as if
you were about to implement it — including any question you would need
answered before writing code.

### Resource paths
- repo root (scratch clone, read-only): <RUN_A: /path/to/scratch-clone-original> | <RUN_B: /path/to/scratch-clone-charter>
- plan file: <RUN_A: evidence/ab-plan-original.md, task "Task 7"> | <RUN_B: evidence/ab-plan-charter.md, task "T7">
- baseline: none (this is a report-only run, no engineering baseline commit expected)

### What you do
1. Read the plan file's task for T7 only (do not read sibling tasks unless
   the Dependencies/after: line on T7 sends you to one).
2. Read the Files it names.
3. State the RED you would report, verbatim as you would write it in a
   real status report.
4. State the GREEN criteria as you understand them.
5. If anything is ambiguous or missing to proceed, say so explicitly and
   count it.

### Output contract
status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
RED found: <verbatim>
GREEN criteria as understood: <verbatim>
open_questions: <list, or "none">
```

Only the `plan file` line differs between the two dispatches; every other
line is byte-identical. Each run is a fresh-context agent with no memory
of the other run or of this harness document.

## Result slots (filled by the orchestrator after dispatching both runs)

### Run A — original plan (`evidence/ab-plan-original.md`, "Task 7")
- status: _(pending)_
- NEEDS_CONTEXT count: _(pending)_
- questions asked (verbatim): _(pending)_

### Run B — charter plan (`evidence/ab-plan-charter.md`, "T7")
- status: _(pending)_
- NEEDS_CONTEXT count: _(pending)_
- questions asked (verbatim): _(pending)_

## Comparison rule (Acceptance 4)

Acceptance 4 is satisfied when the charter version's (Run B) NEEDS_CONTEXT
count is not greater than the original version's (Run A) NEEDS_CONTEXT
count. Both runs' full status reports are saved verbatim (not
paraphrased) alongside this file once they complete, so the count can be
independently re-checked against the quoted questions rather than taken
on the run's own tally.
