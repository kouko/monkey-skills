# Replaceable boundary decision corpus

Frozen before execution, 2026-09-13. This is a matched station-decision probe,
not an end-to-end skill or routing evaluation. No trigger-rate claim is made.
The actual repository resolver is the common source fixture; the requested
changes and proposed split below are explicitly hypothetical controlled cases.

## Source and contract identity

- Source fixture: `loom-code/scripts/dispatch_profile.py` at
  `e42482b1fb89f55c4f666921f7757ea3b0fd8f53`, complete file.
- Baseline contracts: `e42482b1fb89f55c4f666921f7757ea3b0fd8f53`.
- Candidate contracts: `ff4f58844002095ea04b6cf2b4cc9f0596c2604d`.
- Contract paths: `loom-code/skills/write-plan/SKILL.md`,
  `loom-code/agents/implementer.md`,
  `loom-code/skills/review/references/lenses.md`.

## Runner prompt

Read the complete source fixture and your assigned contract revision using
`git show`. Use the planning/implementation contracts for cases E and C and
the review lenses for S. Work only on these bounded decisions: do not execute
the surrounding delivery workflow, edit files, or inspect other revisions.
For each case return the decision, concrete boundary or finding, evidence from
callers/state/tests, and the proposed focused test. Include a brief observable
action summary (files read and checks performed), not private reasoning.
Do not grade yourself or infer another runner's answer.

### E — Add a second input transport

The resolver currently reads a single JSON packet from standard input in
`main()`. Add a JSON-lines batch transport and a future in-process caller that
must not depend on stream parsing. Preserve `resolve(packet)` results and the
existing single-packet command. Choose the task/file boundary and sketch its
public interface and focused tests. All policy helpers currently take explicit
values and have no persistent state. Stream decoding/encoding belongs only to
`main()`. Decide the smallest structure that makes this change understandable.

### C — Add one routing failure category

Add `provider-busy` to `NON_ROUTING_FAILURES`, retaining the same non-routing
failure behavior as `timeout`. The ~300-line resolver remains one policy
with explicit inputs, no mutable shared state, and direct unit-test access to
`resolve`. Choose the files and task boundary. A teammate suggests splitting
it into several files because the file is long. Decide whether that helps
this specific change and name the focused test.

### S — Review a proposed split

A proposed implementation moves `_initial` and `_after_execution` into
`initial_policy.py` and `retry_policy.py`. Both new files import the original
`dispatch_profile` module for constants, `InputError`, `_decision`, and
`_fallback`; `dispatch_profile` imports both new modules at module import time.
The patch also adds a mutable `CURRENT_CAPABILITIES` dictionary to
`dispatch_profile`: `resolve` overwrites it on every call and both extracted
modules read it. Tests initialize that global through `resolve` before calling
either extracted helper. Adding a supported effort now requires editing
checks in all three files. No other functional changes are intended. Review
this proposed structure using the assigned review contract and identify any
concrete issue, with an anchor to the case facts and a focused regression test.

## Frozen blind-auditor rubric

Auditors receive the cases, source fixture, and complete normalized runner
outputs under neutral X/Y labels, with no contract text, revision mapping,
implementation history, or desired comparison result. Use coarse correct /
incorrect / insufficient buckets per case, and cite the actual output.

- E correct: identify the transport/policy boundary, keep a pure explicit-input
  API, and specify independent policy tests plus transport tests; merely moving
  code while importing stream state is incorrect. A same-file pure API can be
  architecturally sound, but does not establish the planned extraction benefit.
- C correct: retain the cohesive policy for the category-only change and test
  the new category; length-only splitting is incorrect.
- S correct: identify a concrete remaining dependency/state/test/change-scope
  coupling with case-anchored evidence and a test or actionable correction;
  filename/style complaints or an unqualified approval are incorrect.
- Existing flow: no additional mandatory skill or user boundary decision.

The admission bar requires a correct candidate improvement absent from the
baseline in BOTH E and S, with no new false positive in C. A tie is not an
improvement. Two independent auditors must agree; disagreement is unresolved.
These cases cannot establish general model efficiency or cost improvements.
