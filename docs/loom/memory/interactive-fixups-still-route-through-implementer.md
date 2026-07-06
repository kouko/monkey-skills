---
name: interactive-fixups-still-route-through-implementer
description: In interactive fix-up rounds outside an SDD dispatch, reviewer findings must still be routed through an implementer dispatch — the main agent fixing them by direct edit is the recorded test-skipping leak path
type: process
origin: PR #492 (loom-code 0.23.0; TDD-miss mining across 57 sessions, 2026-07-04)
---

In loom-code's subagent-driven development (SDD) workflow — where an
orchestrating agent dispatches implementer subagents that work
test-first and reviewer subagents that produce verdicts — the formal
re-dispatch contract only governs work inside a dispatch. In
INTERACTIVE fix-up rounds (the main agent working directly, outside
any SDD dispatch), reviewer findings must STILL be routed through an
implementer dispatch. The main agent fixing findings by direct edit
is the recorded leak path by which untested production code ships:
mining of past sessions found this exact pattern (miss pattern A3 —
25 production edits with zero tests, and review PASS never flagged
them).

**Why:** the implementer dispatch is what carries the test-first
discipline; direct edits bypass it silently, and reviewers did not
catch the bypass after the fact.

**How to apply:** when a review returns findings and you are working
interactively, dispatch an implementer to fix them (with a failing
test first) instead of editing production code yourself — even for
"small" fixes.
