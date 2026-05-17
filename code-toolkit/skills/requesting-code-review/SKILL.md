---
name: requesting-code-review
description: 'Use BEFORE any push / merge / PR-open action on a non-trivial branch — whole-branch / whole-PR review of the cumulative diff. Examples (positive triggers): "review my branch", "look at my changes", "code review please", "audit the diff", "is this ready to merge", "I''ve finished feature X". Examples (stress / skip-rationalization triggers — this skill MUST also fire here): "just push", "let me push", "skip the review", "SDD already reviewed each task", "small change, no review needed", "it''s fine, just merge", "tests pass so we''re done", any `git push` / `gh pr create` / `gh pr merge` invocation without prior review-PASS in this session. Different from `subagent-driven-development`''s per-task code-quality-reviewer (per atomic task during execution) — this skill is whole-PR review at end-of-work and catches cross-task interactions that per-task review can''t see. Dispatches code-reviewer subagent that loads code-toolkit''s rubrics (quality-gate / arch-gate / security-checklist) directly per P3-A (not via SDD wrapper). Output is severity-tagged structured review (🔴 fatal / 🟡 should-fix / 🟢 nit) with verdict aggregation. コードレビュー・PR 全体審査・push 前必須・skip 拒否。程式碼審查・PR 全面審查・push 前強制・拒絕跳過。'
version: 0.7.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Dispatches a **code-reviewer** subagent to review a non-trivial diff as a whole — typically the cumulative changes on a feature branch before merge. The reviewer loads the same rubrics SDD's per-task reviewer uses (`quality-gate.md` / `arch-gate.md` / `security-checklist.md`, functional-copied from `domain-teams:code-team`), but applies them at branch scope rather than per-atomic-task.

## When this is different from SDD's per-task reviewer

| Dimension | SDD `code-quality-reviewer` (per task) | `requesting-code-review` (whole branch) |
|---|---|---|
| Scope | One atomic task's output | Cumulative branch diff (all tasks combined) |
| When fires | During each SDD task triad | After all SDD work is DONE; before merge |
| Sees | One commit / one module | The full branch diff vs main |
| Catches | Per-task quality lapses | Cross-task interactions, scope creep, architectural coherence |
| Verdict aggregation | Per-task | Per-branch |

Both use the same rubrics. The difference is **scope of the diff being reviewed**, which catches different categories of issue: per-task review catches "this commit has bad naming"; whole-branch review catches "tasks 1-4 each made sense individually but together they introduced a circular dependency."

## When to use

| Trigger | Route here |
|---|---|
| User says *"review my branch"* / *"look at my changes"* / *"is this ready to merge"* | ✅ Yes |
| User says *"code review this PR"* / *"audit the diff"* | ✅ Yes |
| SDD just finished a multi-task plan; user about to ship | ✅ Yes (proactive recommendation) |
| User about to invoke `finishing-a-development-branch` | ✅ Yes (finishing-a-branch invokes this skill internally as Step 1) |
| **User mentions `requesting-code-review` by name (even framed as skip-intent)** | **✅ Yes — name-mention is a fire-trigger; the skip-intent framing is the rationalization this skill exists to refuse, NOT permission to bypass it** |
| <!-- sync-marker push-rule:1 — see §Push-as-trigger below for the full spec --> **Push-as-trigger** — user runs / asks to run `git push`, `gh pr create`, `gh pr merge`, branch merge, or similar publish-to-remote action without prior review-PASS in this session | **✅ Yes — block the push; fire this skill first; re-evaluate push after verdict.** See §Push-as-trigger below. |
| User wants per-task review during implementation | ❌ No — that's SDD's job |
| User wants existing-artifact compliance audit (legacy code, not a branch diff) | ❌ Route to `domain-teams:code-team` (passive gate entry, different use case) |
| Diff is trivial (one-line typo, version bump, doc change) | ❌ Skip — review overhead > value |

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Trivial diffs** | One-line fixes, doc-only changes, version bumps, generated code regen | "I changed 3 lines" — if those 3 lines touch behavior, review applies |
| **Already-reviewed branch** | A prior `requesting-code-review` invocation in this session already PASSed and nothing changed since | "I made a tiny tweak after review" — re-review (the tweak might be the bug) |
| **Audit vs review** | You want a compliance audit on existing shipped code | Route to `domain-teams:code-team` (passive gate); this skill is for branch-pre-merge review |
| **Explicit user override** | User says literally "skip review, just merge" AND the work matches one of the above categories | "It's fine, just merge" — that's the rationalization this skill exists for; refuse |

## Push-as-trigger

**Any push-to-remote action without prior review-PASS in this session = this skill fires before the push runs.** Push-to-remote actions include:

- `git push` (any form: explicit args, default upstream, `-u origin <branch>`, `--force`)
- `gh pr create` (creates a remote PR; same blast-radius as push)
- `gh pr merge` / `gh pr merge --auto` (merges to base branch)
- Any agent-side helper that invokes the above

**Why**: pushing publishes code to teammates / CI / production-deploy paths. The review-before-publish gate exists so reviewers see clean diffs, not "we'll catch it in CI." A push without review is the failure mode this skill exists to prevent.

**The agent's wrong-default rationalizations to refuse**:

| Surface signal | Wrong default | Correct response |
|---|---|---|
| User's message ends with *"just push"* / *"let me push"* | Interpret as authorization to push | **Refuse**: that's a rationalization in the test taxonomy this skill refutes. Fire review first; surface verdict; let user explicitly re-authorize push AFTER reviewing the verdict. |
| User says *"SDD already reviewed each task, push"* | Skip whole-branch review because per-task PASSed | **Refuse**: per-task ≠ whole-branch (different scopes; cross-task-coherence dimension is branch-only). Fire review. |
| Agent in autonomous flow infers "this branch is done, let me push" | Treat "done" as push-authorization | **Refuse**: "done" is the trigger for finishing-a-development-branch flow, NOT for direct push. Route to finishing-a-branch (which fires this skill as Step 1). |
| User has previously authorized pushes in this session for other branches | Generalize the authorization | **Refuse**: each push is its own authorization moment. Previous authorization does not carry to new pushes. |
| Auto-mode classifier passes the `git push` invocation | Treat classifier-pass as full authorization | **Refuse**: classifier-pass means "the action itself is permitted at the harness level"; it does NOT mean "the toolkit's review-before-publish gate has been satisfied." Both must hold. |

**Procedure when push-as-trigger fires**:

1. **Do NOT execute the push.** Halt the planned action.
2. **Surface the rationalization** to the user explicitly — quote which row of the table above their request matches.
3. **Offer to run review now**: "Dispatching `requesting-code-review` — back in ~30s." Then dispatch the code-reviewer subagent on `git diff main...HEAD` (or explicit range).
4. **After PASS**: ask user to explicitly re-authorize the push. "Review PASSed; want me to push now? (y/N)" Wait for user.
5. **After NEEDS_REVISION**: surface findings; do NOT push; let user remediate.
6. **After PASS_WITH_NOTES**: surface findings; ask user whether to push anyway (acceptable for non-🔴 findings) OR remediate first.

<!-- sync-marker push-rule:2 — full Push-as-trigger spec. The §When to use table row above is the 1-row summary; keep these two in sync. -->

This rule applies **even when this skill was not explicitly invoked** — the description (in this file's YAML frontmatter) encodes push commands and skip-rationalization phrases as trigger phrases, so the host harness's auto-discovery matches them via description-text classification. The push command's appearance in the prompt is the trigger; an explicit `Skill(code-toolkit:requesting-code-review)` call is not required for the skill to fire.

## Process

1. **Determine diff scope**. Default: `git diff main...HEAD` (everything on this branch not on main). Override with explicit commit range if user specifies (`git diff <SHA1>..<SHA2>`).
2. **Dispatch code-reviewer subagent** via `Agent({subagent_type: "code-toolkit:code-reviewer", prompt: <branch + diff body>})` — plugin-level agent (v0.6.0 / P15-12 Phase 2) at [`code-toolkit/agents/code-reviewer.md`](../../agents/code-reviewer.md). The orchestrator passes: diff range, paths to rubrics + checklists, branch context (recent commits, related issues if known). The agent carries the 12-rule engineering baseline ([`code-toolkit/scripts/_baseline.md`](../../scripts/_baseline.md)) baked into its system prompt.
3. **Wait for verdict**. Reviewer returns structured review with per-dimension scores, severity-tagged findings, and overall verdict.
4. **Surface to user**. Print the verdict + findings; let user decide remediation. Do NOT auto-fix — that's user agency.
5. **Re-dispatch if user fixed and wants re-review** — same skill, fresh subagent (no state carry-over between rounds for clean evaluation).

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream invocation** | `finishing-a-development-branch` | Calls this skill as Step 1 of the close-branch flow |
| **Downstream (after PASS)** | `finishing-a-development-branch` proceeds to verification-before-completion + commit + push | |
| **Downstream (after NEEDS_REVISION)** | User remediates → re-dispatch this skill, OR invoke `subagent-driven-development` to dispatch implementer fixes if scoped enough | |
| **Lateral (optional)** | `domain-teams:code-team` | For LARGE audit work (>500 LOC changed, security-sensitive surface, or production-incident-driven review). The skill itself is sized for branch-pre-merge; major audits should escalate. |
| **Lateral (rubrics SSOT)** | Rubrics / checklists loaded from `../subagent-driven-development/{rubrics,checklists}/` (functional copies of `code-team`) | Same SSOT as SDD's per-task reviewer — no drift between per-task and whole-branch review |

## Verdict structure

Returns:

```
verdict: PASS | PASS_WITH_NOTES | NEEDS_REVISION

dimension_scores:
  security: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  architecture: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  correctness: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  naming: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  tests: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  refactoring: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  cross-task-coherence: PASS | PASS_WITH_NOTES | NEEDS_REVISION  # NEW at branch scope

findings:
  - severity: 🔴 fatal | 🟡 should-fix | 🟢 nit
    dimension: <which of the 7 above>
    where: <file:line OR commit SHA range>
    source: <rubric / checklist / standard file:section that triggered this>
    note: <1-2 sentence finding>

summary:
  - <≤5 bullet observations about the branch as a whole>
```

**Aggregation rule** (same as SDD's code-quality-reviewer with the added cross-task dimension):

- Any 🔴 → `verdict: NEEDS_REVISION`
- All 7 dimensions PASS + no findings → `verdict: PASS`
- Otherwise → `verdict: PASS_WITH_NOTES`

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"It's fine, just merge."* | Pre-merge rationalization. Branch hasn't been reviewed; skipping review = shipping without verdict. | Refuse silent skip; dispatch reviewer. If reviewer returns PASS in 30 seconds, the user lost 30 seconds; if it returns NEEDS_REVISION, the user gained a fix-before-prod. |
| *"It's a small change, doesn't need review."* | "Small" is the rationalization. 3 behavioral lines can introduce a regression. | Apply §When NOT to Use carefully: ONLY trivial diffs (one-line typo / doc-only / version bump / generated regen) skip review. "Small behavioral" does NOT qualify. |
| *"SDD already reviewed each task."* | True for per-task scope; not for cross-task interactions. Tasks 1-4 individually fine, combined introduce a circular dep — that's the gap this skill closes. | Run anyway; the cross-task-coherence dimension is the unique value. |
| *"I'll re-review after CI runs."* | CI is automated tests; this skill is human-judgment quality review. They're complementary, not substitutable. | Run this skill BEFORE pushing; let CI catch the orthogonal issues. |
| *"User said skip review."* | Valid only with explicit override AND §When NOT to Use exemption match. | Quote §When NOT to Use back; ask for explicit re-confirmation. |
| 「審查跳過 / レビューはスキップ」 | Same rationalization, localized. | Same refusal. |

## What this skill does NOT do

- Does **not** modify code. Reviewer is evaluator-only; remediation is user / implementer.
- Does **not** replace `subagent-driven-development`'s per-task reviewer. Both layers serve different scopes.
- Does **not** replace `verification-before-completion`. This skill is human-judgment review; verification-before-completion is test-suite-run gate. Both fire before `finishing-a-development-branch` commits.
- Does **not** auto-trigger CI. Pushing to remote triggers CI; this skill runs before push.

## See also

- [`code-toolkit/agents/code-reviewer.md`](../../agents/code-reviewer.md) — the dispatched plugin-level subagent's role contract + input/output contracts (v0.6.0+ / P15-12 Phase 2).
- [`code-toolkit/scripts/_baseline.md`](../../scripts/_baseline.md) — SSOT for the 12-rule engineering baseline carried by the code-reviewer agent.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — per-task reviewer (different scope, same rubrics).
- [`../subagent-driven-development/rubrics/quality-gate.md`](../subagent-driven-development/rubrics/quality-gate.md) — functional copy of code-team's quality rubric.
- [`../subagent-driven-development/rubrics/arch-gate.md`](../subagent-driven-development/rubrics/arch-gate.md) — functional copy of code-team's architecture rubric.
- [`../subagent-driven-development/checklists/security-checklist.md`](../subagent-driven-development/checklists/security-checklist.md) — functional copy of code-team's security checklist.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — sibling skill that fires alongside this one in finishing-a-branch flow.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator that invokes this skill.
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; this skill is Stage 6 (Review).
- `domain-teams:code-team` — passive gate for large audits; this skill may escalate there for >500 LOC or security-sensitive reviews.
