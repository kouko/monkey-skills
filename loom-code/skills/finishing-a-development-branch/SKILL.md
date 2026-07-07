---
name: finishing-a-development-branch
description: |
  Use when ready to close out a development branch — about to merge or open a PR. Fires on 'finish this branch', 'wrap up', 'ready to merge', 'open a PR', 'ship it'. Orchestrates review → verification → git-memory commit → git push. No auto-merge.
version: 0.10.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (code-reviewer / plan-document-reviewer / implementer), the parent orchestrator already invoked this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Orchestrates the close-branch sequence. The agent acts as conductor — invoking each step's specialist skill in order, gating progress on each step's verdict, and surfacing the final state to the user. **The user retains agency for the final merge decision** (push + PR is automated; actual merge into main is not).

```
finishing-a-development-branch (this skill)
  │
  ├─→ Phase 1: requesting-code-review
  │     dispatches code-reviewer subagent → verdict: PASS / PASS_WITH_NOTES / NEEDS_REVISION
  │     blocks on NEEDS_REVISION (any 🔴, or 2+ 🟡); PASS_WITH_NOTES (1 🟡) surfaces + asks
  │
  ├─→ Phase 2: verification-before-completion
  │     runs package-level test command → exit 0 + N>0 tests → PASS
  │     blocks on test failure
  │     + ui-verification (CONDITIONAL): branch touched UI AND a
  │       ui-flows.md exists → drive the rendered app through its
  │       enumerated states; otherwise N/A (honest skip, stated)
  │
  ├─→ Phase 3: dev-workflow:git-memory (P3-D MANDATORY)
  │     decides on Decision: / Learning: / Gotcha: trailers for the close-out commit
  │     orchestrator hands the diff + recent commits; git-memory returns trailer set
  │
  ├─→ Phase 4: git commit (orchestrator runs this)
  │     uses the message + trailers from Phase 3
  │     does NOT bypass hooks; does NOT amend
  │     then verifies the carrier landed: memory-grep.sh --verify HEAD
  │     (memory-worthy + exit 4 → STOP before push; both-carrier policy)
  │
  ├─→ Phase 5: git push (orchestrator runs this)
  │     pushes the branch; if branch is local-only, sets upstream first
  │
  ├─→ Phase 6 (optional): gh pr create
  │     only if user has gh CLI configured AND has not opted out
  │     PR body uses git-memory's PR-body convention
  │
  └─→ Phase 7 (optional): git worktree cleanup
        if branch was in .worktrees/, offer (do NOT auto-execute) the worktree remove
        per using-git-worktrees §Removing a worktree

(The diagram above is the **phase overview** — which sub-skill fires in what order.
The numbered **Step** list in §Default flow below is the granular procedure; "Phase N"
and "Step N" are distinct numbering schemes.)
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
| 2b | `ui-verification` (conditional) | Rendered-UI runtime gate has its own tooling/degradation contract (browser/device automation, N/A-loud); fires only when the branch touched UI and a `ui-flows.md` exists |
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
3. Dispatch requesting-code-review — route on the returned verdict, not raw severity:
   - If NEEDS_REVISION (any 🔴 fatal, or 2+ 🟡 should-fix): surface findings; STOP. Wait
     for user remediation. (Consistent with requesting-code-review: NEEDS_REVISION → do NOT push.)
   - If PASS_WITH_NOTES (exactly 1 🟡, no 🔴): surface findings; ASK user to proceed or remediate.
   - If PASS (all 🟢): proceed silently.
   - Budget/quota failure fallback: if the code-reviewer subagent fails to launch due to
     budget or quota exhaustion, perform an inline B2 self-review — Read the diff, surface
     🔴 / 🟡 / 🟢 findings with an explicit "(self-review — code-reviewer unavailable)" caveat,
     then derive the verdict by the same aggregation (any 🔴 or 2+ 🟡 → NEEDS_REVISION;
     exactly 1 🟡 → PASS_WITH_NOTES; all 🟢 → PASS) and apply the gate above. NEVER suggest
     `/ultrareview` or any external review command in AskUserQuestion options or in the PR body
     without first verifying it exists via `claude --help`.
4. Before applying any review findings from Step 3: Read each file you intend to Edit
   (Bash inspection does NOT satisfy the Edit/Write precondition) — details in
   [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §S1.
5. Dispatch verification-before-completion
   - MANDATORY even if tests were run immediately before invoking this skill. Step 3
     fix-ups may have modified files; a pre-invocation test run does NOT satisfy this gate.
   - If test failure: surface output; STOP. Route user to tdd-iron-law or systematic-debugging.
   - If 0 tests ran: surface as failure (configuration bug, not a pass).
   - If PASS: proceed silently.
5b. Dispatch ui-verification (CONDITIONAL — skip as N/A when the branch touched no UI
    surface or no ui-flows.md exists; state the N/A, don't silently omit)
   - NEEDS_REVISION (state mismatch, or unreachable state whose ui-flows.md row is NOT
     marked future/deferred): surface findings; STOP — route to the
     implementer, or flag the design station if the enumeration itself is wrong.
   - PASS_WITH_NOTES: proceed; carry untestable-state notes into the PR body.
6. Invoke dev-workflow:git-memory
   - Pass: diff, recent commits, branch name
   - Receive: trailer set (Decision: / Learning: / Gotcha: lines) + commit body suggestion
7. Show user the proposed commit message + trailers; ASK for approval
   - If approved: proceed
   - If rejected / edited: use user's version
8. git hygiene before the close-out commit:
   - Living-spec index regen (orchestrator-only, ONCE per branch): if the repo has a
     `docs/loom/` tree, run
     `python3 loom-code/scripts/check-living-spec-index.py --write-index docs/loom/INDEX.md <repo-root>`
     once, then stage the regenerated `docs/loom/INDEX.md` (`git add docs/loom/INDEX.md`)
     so it lands in THIS close-out commit. This is EXPLICITLY orchestrator-only, NOT
     per-implementer / per-wave: the index is a repo-wide generated file, so a per-implementer
     regen under parallel SDD would merge-conflict the file and reflect only a partial tree.
     This mirrors loom's existing "orchestrator commits, implementers don't" rule.
   - Memory-timing check (orchestrator-only, ONCE per branch): if this branch surfaced
     a durable, already-known fact (practice / gotcha / process per the jurisdiction
     table), record it into `docs/loom/memory/` NOW so it lands in THIS close-out
     commit — see `docs/loom/memory/README.md` §"When to record" for the exact rule
     and its one exception.
   - Run `git status --short` to confirm exactly which files are staged and untracked.
   - Stage with an explicit file list (`git add <file1> <file2> …`) — avoid `git add -A <dir>`
     which sweeps unrelated untracked files into the commit.
   - Use the branch-qualified push form `git push -u origin <branch>` (or `git push origin
     <branch>` if upstream already set) — NEVER a bare `git push`, which trips the sandbox
     "do not push to main" guard on the first push of a new branch.
   - Compound `git push && gh pr create` must be two separate Bash calls, and any rebase-conflict
     resolution uses Read+Edit (not Bash `cat`+`Write`) — details in
     [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §S2/§D1.
   - If any review-driven fixes were applied in Steps 3–4, re-run verification-before-completion
     here (Step 5 result is stale) before committing.
9. git commit (only after user approval at Step 7)
9b. Commit-carrier verify gate — MANDATORY, runs AFTER the commit, BEFORE push:
    - Run `dev-workflow/skills/git-memory/scripts/memory-grep.sh --verify HEAD`
      (exit 0 = a Decision/Learning/Gotcha trailer is retrievable from HEAD's body;
      exit 4 = none).
    - If Phase 3 (Step 6) returned a NON-empty trailer set (the branch is
      memory-worthy) AND `--verify HEAD` exits 4: STOP. Surface "the close-out
      commit did not capture the memory trailers — fix before push." Do NOT push.
      Root cause this gate closes: a memory-worthy branch must not ship with an empty
      commit carrier — the decision would be unretrievable via `git log --grep` on
      main (the #445 leak). This is a hard STOP, consistent with finishing's other
      gates (NEEDS_REVISION review / test-failure both STOP).
    - If Phase 3 returned an EMPTY trailer set (routine branch), exit 4 is expected →
      proceed to push.
    - If `--verify HEAD` exits 0: the carrier landed → proceed to push.
9c. Gate markers at the FINAL HEAD — the `hooks/git-guard.py` PreToolUse gate blocks
    `git push` / `gh pr create` without both markers matching current HEAD:
    - Re-run the package suite at the final HEAD, then mint
      `python3 <plugin-root>/scripts/loom_gate_markers.py verified --suite-line "<tail line>"`
      — verification evidence must POSTDATE the close-out commit; a green run from before
      it is exactly the stale-green-light failure this gate exists to kill.
    - Mint the review marker at the final HEAD (save the Step-3 verdict text to a file,
      run `… loom_gate_markers.py review-pass --verdict-file <file>`) — allowed ONLY when
      the delta since the reviewed verdict is mechanical close-out content (living-spec
      INDEX regen, memory trailers). ANY substantive post-verdict change → re-dispatch
      requesting-code-review first: review what you ship, not what you reviewed an
      amend ago.
    - User explicitly waives review ("skip review, push now") → record it:
      `… loom_gate_markers.py waiver --reason "<user's words>"` — one-shot, consumed and
      logged by the gate on the next push. Never self-mint a waiver.
10. git push (branch-qualified form per Step 8)
11. ASK user: "Open a PR? (y/N)" — only if gh CLI configured
    - If yes: gh pr create with title/body from git-memory + branch name
    - PR-carrier check (memory-worthy branch only): before declaring the PR ready,
      grep the PR body you just composed for a `## Memory` section. If Phase 3
      returned a non-empty trailer set and the body has no `## Memory` section,
      flag it and add the section (both-carrier policy — commit AND PR carry the
      memory). No new tooling: it is a grep on the body you are about to submit.
    - If no: stop after push
12. ASK user: "Branch was in .worktrees/; remove the worktree? (y/N)"
    - If yes: cd to repo root; git worktree remove .worktrees/<slug>
    - If no: leave it
13. Report final state: commit SHA, push status, PR URL if created, worktree status
```

**ASK = stop and wait for user.** This is deliberately NOT autonomous — close-out is a high-blast-radius operation (shipping code → teammates / production). Each user-visible action has a confirmation.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Skip review, just push."* | Review-skip rationalization — same shape as `requesting-code-review`'s. | Refuse; dispatch requesting-code-review (Phase 1). If reviewer PASSes in 30 seconds, you lose 30 seconds; if NEEDS_REVISION, you gain a fix-before-prod. |
| *"Tests passed locally yesterday, skip the verification step."* | Code may have changed since yesterday. Test results have a half-life of "current uncommitted state". | Re-run verification-before-completion. |
| *"Don't bother with git-memory, message is obvious."* | P3-D MANDATORY — git-memory itself decides whether memory trailers are warranted. *"Message is obvious"* may be true (git-memory returns "no trailers needed for this routine commit"); the determination is the skill's job, not the user's pre-decision. | Invoke git-memory anyway. The skill outputs an empty trailer set for routine commits; the invocation itself is the discipline (audit trail of "we considered memory and decided no"). See git-memory §Invocation policy. |
| *"Auto-merge after push."* | Merge into main is a visible action with consequences for teammates. Always user-decision. | Push only; report PR URL if created. Let user merge via UI / explicit command. |
| *"Force-push to clean up history."* | Force-push to shared branches is destructive. Force-push to your own feature branch may be appropriate but always requires explicit user authorization. | Refuse unless user explicitly authorizes; warn about implications for any teammates with the branch checked out. |
| *"Just amend the last commit."* | Amend loses the previous commit's SHA → loses any in-flight reviews referencing that SHA. Per CLAUDE.md commit policy: *"Always create NEW commits rather than amending."* | Refuse; create new commit. |
| *"I already have a commit message from SDD."* | Per-task SDD commits cover per-task work. The close-out commit captures the full branch; its Decision/Learning/Gotcha trailers require a fresh git-memory call over the whole diff. | Invoke `dev-workflow:git-memory` (Skill call, not an orchestrator-composed message). Even if it returns no trailers ("routine commit"), the invocation is the audit trail. |
| 「review skip / 跳過審查」 | Same rationalization, localized. | Same refusal — dispatch requesting-code-review (Phase 1). |

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

- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — Phase 1 delegate.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — Phase 2 delegate.
- [`../ui-verification/SKILL.md`](../ui-verification/SKILL.md) — Phase 2 conditional sibling (rendered-UI gate).
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — Phase 7 delegate (worktree cleanup).
- `dev-workflow:git-memory` — Phase 3 delegate (commit-trailer gate, P3-D MANDATORY).
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 8 (Branch close).
- CLAUDE.md §"Committing changes with git" — git policy (no amend, no skip hooks, no force-push without authorization) this skill inherits.
