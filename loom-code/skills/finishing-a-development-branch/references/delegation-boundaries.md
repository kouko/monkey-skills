# Delegation boundaries — what the orchestrator does NOT do

Load when questioning why this skill doesn't reimplement a delegated step's logic. Companion to the Cross-skill contract table in SKILL.md.

The orchestrator does NOT:
- Duplicate git-memory's trailer-decision logic (P3-D — would create drift)
- Decide commit messages from scratch (delegates to git-memory output)
- Force the merge — merge stays with the user, never auto-run (PR-open is different: request-derived authorization, see below)

## Why each step delegates

| Step | Delegate | Why this skill doesn't do it directly |
|---|---|---|
| 1 | `requesting-code-review` (four-way dispatch; docs-only → `requesting-docs-review`) | Human-judgment quality review is its own skill with its own subagent; this orchestrator just dispatches |
| 2 | `verification-before-completion` | Package-level test invocation has its own per-stack command table; this orchestrator just invokes the gate |
| 2b | `ui-verification` (conditional) | Main acceptance stage for a UI-bearing branch; has its own tooling/degradation contract (browser/device automation, N/A-loud); fires only when the branch touched UI and a `ui-flows.md` exists |
| 3 | `dev-workflow:git-memory` | P3-D MANDATORY — git-memory decides whether memory trailers are warranted on this commit. Orchestrator passes the diff + recent commits; git-memory returns the trailer set (or empty, if routine) |
| 4 | git CLI | Standard `git commit -m "<msg>" -m "<body with trailers>"` |
| 5 | git CLI | `git push -u origin <branch>` if new; `git push` if upstream set |
| 6 | gh CLI | `gh pr create --title "<title>" --body "<body>"`; authorization is request-derived — it arrived with the close-out request, so Step 11 opens the PR without a re-ask (up-front opt-out honored) |
| 7 | `using-git-worktrees` | Worktree cleanup pattern lives in that skill; this orchestrator just offers to invoke its `git worktree remove` flow |

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
