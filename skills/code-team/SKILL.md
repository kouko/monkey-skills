---
name: code-team
description: Feature development workflow — Arch → Implement → Test → Review → Verify. Use for new features, bug fixes, or any code implementation task.
---

# Code Team

Sequential Arch → Implement → Test → Checklist → Review → Verify.
Uses hybrid evaluation: binary checklist gate first, then qualitative flag gate.

## Step 1 — Plan

Use `feature-dev:code-architect` (plugin) for planning.

## Step 2 — Architecture Review (flag gate)

Launch `evaluator` with:
- Rubric: Read `skills/domain-code/rubrics/arch-gate.md`
- Artifact: the plan from Step 1

- **PASS** → proceed to Step 3
- **PASS_WITH_NOTES** → Revise plan → re-run Step 2
- **NEEDS_REVISION** → Stop, present alternatives to user

## Step 3 — Implement

Make changes in main conversation.
Worker should reference `skills/domain-code/standards/code-conventions.md`.
PostToolUse lint hook provides immediate syntax/style feedback.

## Step 3.5 — Test (optional)

Launch `worker` with:
- Protocol: Read `skills/domain-code/protocols/test-writing.md`
- Standards: Read `skills/domain-code/standards/code-conventions.md`
- Input: summary of new/changed modules

Tests must pass before proceeding to review.

## Step 4 — Security Checklist (binary gate)

Launch `evaluator` with:
- Checklist: Read `skills/domain-code/checklists/security-checklist.md`
- Artifact: code changes from Step 3

- All `PASS` → proceed to Step 5
- Any `FAIL` → `NEEDS_REVISION`, auto-fix → re-run Step 4

## Step 5 — Quality Review (flag gate)

Launch `evaluator` with:
- Rubric: Read `skills/domain-code/rubrics/quality-gate.md`
- Standards: Read `skills/domain-code/standards/code-conventions.md`
- Artifact: code changes from Step 3

- **PASS** → proceed to Step 6
- **PASS_WITH_NOTES** → Auto-fix based on feedback → re-run Step 5
- **NEEDS_REVISION** → Stop, present issues to user

## Step 6 — QA Verification (flag gate)

Launch `evaluator` with:
- Rubric: Read `skills/domain-code/rubrics/qa-gate.md`
- Artifact: code changes from Step 3 (post-review)

- **PASS** → Done, report to user
- **PASS_WITH_NOTES** → Auto-fix → go back to Step 5 (re-review)
- **NEEDS_REVISION** → Stop, present issues to user

## Step 7 — Documentation (optional)

Launch `worker` with:
- Protocol: Read `skills/domain-code/protocols/doc-writing.md`
- Standards: Read `skills/domain-code/standards/code-conventions.md`
- Input: new public APIs or significant behavior changes

## Context Isolation

Each agent launch starts fresh. Pass only:
- To evaluator: the checklist/rubric + standards + artifact + original requirements
- To worker: the protocol + standards + task description + relevant input

Use `context-compressor` to compress large artifacts before passing between phases if needed.

## Auto-Revise Loop (Context-Clean Retry)

When a gate returns `PASS_WITH_NOTES` or a checklist returns `FAIL_FIXABLE`:

1. Use `context-compressor` to compress the current artifact + feedback into a brief
2. Launch a **fresh** worker/main-conversation with ONLY:
   - Original requirements
   - Current artifact (V_n)
   - Evaluator feedback from this round
3. Discard all prior retry history — the new agent should NOT see V_1..V_(n-1)
4. Re-run the same gate on the new output

This prevents context bloat from polluting the LLM's attention across retries.

## Worker BLOCKED Handling

If a worker outputs `BLOCKED` status instead of an artifact:
- Do NOT proceed to evaluation gates
- Present the BLOCKED reason and suggested next steps to the user
- Wait for user input before re-dispatching

## Guard Rails

- Max 3 auto-revision rounds (across all gates) before escalating
- After QA fix, always re-run quality review — fixes may introduce bugs
- Run tests after each revision if test suite exists
- Each retry launches a fresh agent (no accumulated context from failed attempts)
