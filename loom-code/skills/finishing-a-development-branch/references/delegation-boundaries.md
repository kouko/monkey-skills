# Delegation boundaries — what the orchestrator does NOT do

Load when questioning why this skill doesn't reimplement a delegated step's logic. Companion to the Cross-skill contract table in SKILL.md.

The orchestrator does NOT:
- Duplicate git-memory's trailer-decision logic (P3-D — would create drift)
- Decide commit messages from scratch (delegates to git-memory output)
- Force the merge — merge stays with the user, never auto-run (PR-open is different: request-derived authorization, see below)

## What this skill does NOT do

Does **not** merge into main, force-push, amend commits (creates new per CLAUDE.md), or auto-remove worktrees — worktree removal needs explicit user authorization, while PR-open does not re-ask (authorization arrived with the close-out request). Delegation is by the Cross-skill contract table in SKILL.md; shortcut-refusal rationale for merge/force-push/amend lives in [`red-flags.md`](red-flags.md).

## See also

- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — Phase 1 delegate.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — Phase 2 delegate.
- [`../ui-verification/SKILL.md`](../ui-verification/SKILL.md) — Phase 2 conditional sibling (rendered-UI gate).
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — Phase 7 delegate (worktree cleanup).
- `dev-workflow:git-memory` — Phase 3 delegate (commit-trailer gate, P3-D MANDATORY).
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 8 (Branch close).
- CLAUDE.md §"Committing changes with git" — git policy (no amend, no skip hooks, no force-push without authorization) this skill inherits.
