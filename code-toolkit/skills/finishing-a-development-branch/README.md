# finishing-a-development-branch

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Orchestrator skill — ties together the close-branch sequence: [`requesting-code-review`](../requesting-code-review) (Step 1 human review) → [`verification-before-completion`](../verification-before-completion) (Step 2 package-level test) → mandatory `dev-workflow:git-memory` delegation for commit-message trailers (P3-D) → git commit → push → optional gh pr create → optional `using-git-worktrees` cleanup. **Does NOT auto-merge** — user retains agency for the final merge decision.

Part of the [code-toolkit](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## The flow

```
finishing-a-development-branch
  ├─→ Step 1: requesting-code-review        (human-judgment quality)
  ├─→ Step 2: verification-before-completion (package-level tests pass)
  ├─→ Step 3: dev-workflow:git-memory       (commit-message trailers, P3-D MANDATORY)
  ├─→ Step 4: git commit                    (using Step 3's message)
  ├─→ Step 5: git push
  ├─→ Step 6: gh pr create                  (optional, user opt-in)
  └─→ Step 7: git worktree remove           (optional, user confirmation)
```

Each Step gates the next. 🔴 fatal review findings or test failures BLOCK progress. User confirmation is required before each user-visible action (commit message approval, push, PR creation, worktree removal).

## When to use

- *"finish this branch"* / *"wrap up the feature"* / *"ready to merge"* / *"ship it"* / *"close out this branch"*
- *"open a PR for this branch"*
- *"I'm done here, what's next?"* (the "done" framing → finish branch before moving on)
- Proactively after SDD completes all tasks DONE on a multi-task plan

## When NOT to use

[`SKILL.md`](SKILL.md) §When NOT to Use:
- Mid-task work (SDD plan not yet complete)
- Trivial direct-to-main commits (single-line doc fix on solo project)
- Branch being abandoned (skill doesn't apply; just delete)
- Explicit user override AND there's a real reason (cherry-pick / known-trivial cleanup)

## Heavy delegation — by design

This skill is intentionally light on novel logic. Every step delegates to a specialist:

| Step | Delegate | Why orchestrator doesn't do it directly |
|---|---|---|
| 1 | `requesting-code-review` | Quality review is its own skill |
| 2 | `verification-before-completion` | Package-level test invocation is its own skill |
| 3 | `dev-workflow:git-memory` | P3-D MANDATORY — git-memory decides trailer warranted-ness; orchestrator doesn't duplicate |
| 4 | git CLI | Standard git commit |
| 5 | git CLI | git push (set upstream if new branch) |
| 6 | gh CLI | gh pr create (opt-in) |
| 7 | `using-git-worktrees` | Worktree cleanup pattern lives there |

## What this skill does NOT do

- Does **not** review code itself (delegates).
- Does **not** run tests itself (delegates).
- Does **not** decide memory trailers (P3-D — delegates to git-memory).
- Does **not** merge into main (user agency).
- Does **not** force-push without authorization.
- Does **not** amend commits (per CLAUDE.md policy — always create NEW commits).
- Does **not** auto-create PRs without opt-in.
- Does **not** auto-remove worktrees without confirmation.

## See also

- [`SKILL.md`](SKILL.md) — operational spec + 7-step default flow + Red Flags.
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — Step 1 delegate.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — Step 2 delegate.
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — Step 7 delegate.
- `dev-workflow:git-memory` — Step 3 delegate (P3-D MANDATORY).
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; this skill is Stage 8 (Branch close).
- CLAUDE.md §"Committing changes with git" — inherited git policy.
