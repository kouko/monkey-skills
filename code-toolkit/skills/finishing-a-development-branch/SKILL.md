---
name: finishing-a-development-branch
description: 'Use when ready to close out a development branch — feature done, tests pass, about to merge or open a PR. Examples: "finish this branch", "wrap up the feature", "ready to merge", "open a PR for this branch", "ship it", "close out this branch", "I''m done here, what''s next?". Orchestrates the full close-branch sequence: requesting-code-review (Step 1 human-judgment review) → verification-before-completion (Step 2 package-level test invocation) → mandatory dev-workflow:git-memory delegation for commit message (P3-D) → git push → optional gh pr create → optional git worktree cleanup. Does NOT duplicate git-memory logic (delegates per P3-D); does NOT auto-merge (user agency for the final merge call). ブランチ収了・PR 準備・merge 前収尾。分支收尾・PR 準備・merge 前完工。'
version: 0.5.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (code-reviewer / plan-document-reviewer / implementer), the parent orchestrator already invoked this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Orchestrates the close-branch sequence. The agent acts as conductor — invoking each step's specialist skill in order, gating progress on each step's verdict, and surfacing the final state to the user. **The user retains agency for the final merge decision** (push + PR is automated; actual merge into main is not).

```
finishing-a-development-branch (this skill)
  │
  ├─→ Step 1: requesting-code-review
  │     dispatches code-reviewer subagent → verdict: PASS / PASS_WITH_NOTES / NEEDS_REVISION
  │     blocks on 🔴 fatal; surfaces 🟡 / 🟢 findings
  │
  ├─→ Step 2: verification-before-completion
  │     runs package-level test command → exit 0 + N>0 tests → PASS
  │     blocks on test failure
  │
  ├─→ Step 3: dev-workflow:git-memory (P3-D MANDATORY)
  │     decides on Decision: / Learning: / Gotcha: trailers for the close-out commit
  │     orchestrator hands the diff + recent commits; git-memory returns trailer set
  │
  ├─→ Step 4: git commit (orchestrator runs this)
  │     uses the message + trailers from Step 3
  │     does NOT bypass hooks; does NOT amend
  │
  ├─→ Step 5: git push (orchestrator runs this)
  │     pushes the branch; if branch is local-only, sets upstream first
  │
  ├─→ Step 6 (optional): gh pr create
  │     only if user has gh CLI configured AND has not opted out
  │     PR body uses git-memory's PR-body convention
  │
  └─→ Step 7 (optional): git worktree cleanup
        if branch was in .worktrees/, offer (do NOT auto-execute) the worktree remove
        per using-git-worktrees §Removing a worktree
```

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Mid-task work** | The SDD task plan is not yet complete; tasks still pending | "I'm tired of this branch" — that's bailing, not finishing. SDD plan completes first. |
| **Trivial direct-to-main commits** | Solo project, no review process, tiny doc fix | Feature branch with multiple commits — even solo, the discipline catches regressions |
| **Branch you're abandoning** | The work isn't merging; you're discarding | Skill doesn't apply — just delete the branch. But re-examine whether the work was real: if so, the branch deserves close-out before deletion (decisions worth recording via git-memory) |
| **Explicit user override** | User says "skip review, just push" AND there's a real reason (cherry-pick to release branch / known-trivial cleanup) | "I trust myself" — that's the rationalization this skill exists for |

## When to use

| Trigger phrase | Route here |
|---|---|
| *"finish this branch"* / *"wrap up the feature"* / *"ready to merge"* | ✅ Yes |
| *"open a PR for this branch"* / *"ship it"* / *"close out this branch"* | ✅ Yes |
| *"I'm done here, what's next?"* | ✅ Yes (the "done" framing — finish the branch before next task) |
| SDD's task plan just completed all tasks DONE | ✅ Yes (proactive — natural handoff point) |
| User wants per-task review during implementation | ❌ No — that's SDD's per-task triad |
| User wants whole-branch review WITHOUT merging | ❌ Route directly to `requesting-code-review` (no close-out flow needed) |

## Cross-skill contract — heavy delegation

This skill is intentionally light on novel logic. Its value is orchestration; the work happens in delegated specialists:

| Step | Delegate | Why this skill doesn't do it directly |
|---|---|---|
| 1 | `requesting-code-review` | Human-judgment quality review is its own skill with its own subagent; this orchestrator just dispatches |
| 2 | `verification-before-completion` | Package-level test invocation has its own per-stack command table; this orchestrator just invokes the gate |
| 3 | `dev-workflow:git-memory` | P3-D MANDATORY — git-memory decides whether memory trailers are warranted on this commit. Orchestrator passes the diff + recent commits; git-memory returns the trailer set (or empty, if routine) |
| 4 | git CLI | Standard `git commit -m "<msg>" -m "<body with trailers>"` |
| 5 | git CLI | `git push -u origin <branch>` if new; `git push` if upstream set |
| 6 | gh CLI | `gh pr create --title "<title>" --body "<body>"`; user must opt in |
| 7 | `using-git-worktrees` | Worktree cleanup pattern lives in that skill; this orchestrator just offers to invoke its `git worktree remove` flow |

**The orchestrator does NOT**:
- Duplicate git-memory's trailer-decision logic (P3-D — would create drift)
- Decide commit messages from scratch (delegates to git-memory output)
- Force the merge (user agency for the final merge decision)
- Auto-create PRs without user opt-in (PR creation is visible to teammates → user must explicitly authorize)

## Default flow — what happens if user just says "finish this branch"

```
1. Read branch state — git status + git log main..HEAD + git diff main...HEAD
2. Verify branch has commits (else: "nothing to finish; branch matches main")
3. Dispatch requesting-code-review
   - If 🔴 fatal: surface findings; STOP. Wait for user remediation.
   - If 🟡 / 🟢: surface findings; ASK user to proceed or remediate.
   - If PASS: proceed silently.
4. Dispatch verification-before-completion
   - If test failure: surface output; STOP. Route user to tdd-iron-law or systematic-debugging.
   - If 0 tests ran: surface as failure (configuration bug, not a pass).
   - If PASS: proceed silently.
5. Invoke dev-workflow:git-memory
   - Pass: diff, recent commits, branch name
   - Receive: trailer set (Decision: / Learning: / Gotcha: lines) + commit body suggestion
6. Show user the proposed commit message + trailers; ASK for approval
   - If approved: proceed
   - If rejected / edited: use user's version
7. git commit (only after user approval at Step 6)
8. git push (set upstream if branch is local-only)
9. ASK user: "Open a PR? (y/N)" — only if gh CLI configured
   - If yes: gh pr create with title/body from git-memory + branch name
   - If no: stop after push
10. ASK user: "Branch was in .worktrees/; remove the worktree? (y/N)"
    - If yes: cd to repo root; git worktree remove .worktrees/<slug>
    - If no: leave it
11. Report final state: commit SHA, push status, PR URL if created, worktree status
```

**ASK = stop and wait for user.** This is deliberately NOT autonomous — close-out is a high-blast-radius operation (shipping code → teammates / production). Each user-visible action has a confirmation.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Skip review, just push."* | Review-skip rationalization — same shape as `requesting-code-review`'s. | Refuse; dispatch Step 1. If reviewer PASSes in 30 seconds, you lose 30 seconds; if NEEDS_REVISION, you gain a fix-before-prod. |
| *"Tests passed locally yesterday, skip step 2."* | Code may have changed since yesterday. Test results have a half-life of "current uncommitted state". | Re-run verification-before-completion. |
| *"Don't bother with git-memory, message is obvious."* | P3-D MANDATORY — git-memory itself decides whether memory trailers are warranted. *"Message is obvious"* may be true (git-memory returns "no trailers needed for this routine commit"); the determination is the skill's job, not the user's pre-decision. | Invoke git-memory anyway. The skill outputs an empty trailer set for routine commits; the invocation itself is the discipline (audit trail of "we considered memory and decided no"). See git-memory §Invocation policy. |
| *"Auto-merge after push."* | Merge into main is a visible action with consequences for teammates. Always user-decision. | Push only; report PR URL if created. Let user merge via UI / explicit command. |
| *"Force-push to clean up history."* | Force-push to shared branches is destructive. Force-push to your own feature branch may be appropriate but always requires explicit user authorization. | Refuse unless user explicitly authorizes; warn about implications for any teammates with the branch checked out. |
| *"Just amend the last commit."* | Amend loses the previous commit's SHA → loses any in-flight reviews referencing that SHA. Per CLAUDE.md commit policy: *"Always create NEW commits rather than amending."* | Refuse; create new commit. |
| 「review skip / 跳過審查」 | Same rationalization, localized. | Same refusal — dispatch Step 1. |

## What this skill does NOT do

- Does **not** review code itself (delegates to `requesting-code-review`).
- Does **not** run tests itself (delegates to `verification-before-completion`).
- Does **not** decide memory trailers itself (delegates to `dev-workflow:git-memory` per P3-D).
- Does **not** merge into main (user agency).
- Does **not** force-push without authorization.
- Does **not** amend commits (creates new commits per CLAUDE.md policy).
- Does **not** auto-create PRs without opt-in.
- Does **not** auto-remove worktrees without confirmation.

## See also

- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — Step 1 delegate.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — Step 2 delegate.
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — Step 7 delegate (worktree cleanup).
- `dev-workflow:git-memory` — Step 3 delegate (commit-trailer gate, P3-D MANDATORY).
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; this skill is Stage 8 (Branch close).
- CLAUDE.md §"Committing changes with git" — git policy (no amend, no skip hooks, no force-push without authorization) this skill inherits.
