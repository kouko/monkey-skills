---
name: code-team
description: Feature development workflow — Arch → Implement → Test → Review → Verify. Use for new features, bug fixes, or any code implementation task.
---

# Code Team

Sequential Arch → Implement → Test → Review → Verify.

## Step 1 — Plan

Use `feature-dev:code-architect` (plugin) for planning.

## Step 2 — Architecture Review (Opus gate)

Launch `code-arch-reviewer`
- **PASS** → proceed to Step 3
- **PASS_WITH_NOTES** → Revise plan → re-run Step 2
- **NEEDS_REVISION** → Stop, present alternatives to user

## Step 3 — Implement

Make changes in main conversation.
PostToolUse lint hook provides immediate syntax/style feedback.

## Step 3.5 — Test (optional)

Launch `code-test-writer` for new/changed modules.
Tests must pass before proceeding to review.

## Step 4 — Review (Sonnet gate)

Launch `code-reviewer`
- **PASS** → proceed to Step 5
- **PASS_WITH_NOTES** → Auto-fix based on feedback → re-run Step 4
- **NEEDS_REVISION** → Stop, present issues to user

## Step 5 — Verify (Opus gate)

Launch `shared-qa-evaluator`
- **PASS** → Done, report to user
- **PASS_WITH_NOTES** → Auto-fix → go back to Step 4 (re-review from Sonnet)
- **NEEDS_REVISION** → Stop, present issues to user

## Step 6 — Documentation (optional)

Launch `code-doc-writer` for new public APIs or significant behavior changes.

## Guard Rails

- Max 3 auto-revision rounds (across both gates) before escalating
- After qa-evaluator fix, always re-run code-reviewer (fixes may introduce bugs)
- Run tests after each revision if test suite exists
