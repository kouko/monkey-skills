---
name: workflow-agent-results-and-courier-args-need-guards
description: Workflow scripts — every agent() result can be null (skip/terminal error) and must degrade to a failed item, and any operator arg interpolated into a courier agent's Bash instruction text needs a per-segment character allow-list; leading-slash or non-empty checks are not enough
type: gotcha
origin: branch feat-principles-replay-loop-l1-l2 (2026-07-11) — round-1 🔴 + whole-branch 🟡 on principles-replay-matrix.js
---

In `.claude/workflows/*.js` scripts, two guard obligations recur and were
both missed once each on the same file despite the sibling precedent
(`code-toolkit-sweep.js:113`, `driver_10_guard.js:112-123`) being named
in the dispatch:

1. `agent()` returns null when the user skips the agent or it dies on a
   terminal error. EVERY stage's result needs its own null-guard that
   degrades to a failed row/item — guarding one stage and dereferencing
   the next stage's result unguarded is the observed failure shape
   (Replay guarded, Grade crashed).
2. Operator-supplied args that end up interpolated into a courier
   agent's Bash instruction text (path segments, labels) need a
   `^[A-Za-z0-9._-]+$` allow-list — per path segment for absolute
   paths. A "starts with /" or "non-empty" check lets `;`-payloads
   through to the command line.

**Why:** static text tests on the .js cannot see either runtime hole;
both surfaced only in review. A crashed stage loses the whole seed's
verdict instead of recording a failure; an unguarded arg is a shell
injection surface even in trusted-operator eval harnesses.

**How to apply:** when authoring or reviewing a Workflow script, for
each `await agent(...)` write the `if (!result) { return failedRow }`
guard immediately, and run an args audit: every arg that reaches a
prompt's Bash text gets the allow-list (segment-wise for paths). Pin
both with static tests (regex/error-string presence).
