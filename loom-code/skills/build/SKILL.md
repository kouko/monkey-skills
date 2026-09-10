---
name: build
description: |
  Implements a committed plan with test-first changes, focused verification, and one integration pass before the closing Review. Use when a confirmed intent and plan are ready to build.
version: 1.2.0
---

# Build

Build produces functional content. It does not maintain review accounting or
generate publication evidence.

## 1. Establish scope

Read the confirmed intent, spec when present, plan, current branch, and branch
base. Preserve unrelated and untracked work. Work only on planned paths.

## 2. Implement test first

Before every host-native dispatch, the station must read the
[shared dispatch profile](../../references/dispatch-profile.md), classify the
task from its evidence, and resolve the atomic model-and-effort profile against
the selected model's verified host capabilities. Record the requested and
effective profile with its evidence-grounded reason in active task context only.
Apply the resolved overrides at invocation time; a static model or effort pin in
an agent contract is invalid.

For every behavior change:

1. Write the smallest failing test and run it to observe RED.
2. Implement the minimum change and run it to GREEN.
3. Refactor only while the focused suite stays green.

An implementation agent never acts as its own closing reviewer. Parallel work
is optional and used only for genuinely independent file sets; no dispatch ledger is created.

Internal plans, commits, and verification evidence are written in English.

## 3. Verify integration

Run focused tests after each task. After all tasks land, run the relevant
integration checks once to expose cross-task defects. Do not run the complete
package suite as a speculative push preflight; `finalize-review` owns its one
content-bound execution.

## 4. Hand off to Review

Commit functional changes normally. Report the branch base, HEAD, changed
paths, focused test results, and any unresolved risk. Call `loom-code:review`
once over the cumulative branch. Build never writes `attestation.json` and
never edits it after Review generates it.
