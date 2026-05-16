---
name: requesting-code-review
description: 'Use when you have a non-trivial diff ready for whole-PR review — branch about to merge, feature complete and seeking quality verdict, refactor finished and wanting structural sanity check, or you''re about to push and want a final pass. Examples: "review my branch before I open the PR", "look at my changes", "is this ready to merge", "code review please", "audit the diff", "I''ve finished feature X, look it over". Different from `subagent-driven-development`''s per-task code-quality-reviewer (that fires per atomic task during execution) — this skill is whole-PR review at the end of work. Dispatches a code-reviewer subagent that loads code-toolkit''s functional-copy rubrics (quality-gate / arch-gate / security-checklist) directly per P3-A (not via SDD wrapper). Output is severity-tagged structured review (🔴 fatal / 🟡 should-fix / 🟢 nit) with verdict aggregation. コードレビュー・PR 全体審査・ブランチ完了レビュー。程式碼審查・PR 全面審查・分支收尾審查。'
version: 0.3.0-draft
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / debugger / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
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

## Process

1. **Determine diff scope**. Default: `git diff main...HEAD` (everything on this branch not on main). Override with explicit commit range if user specifies (`git diff <SHA1>..<SHA2>`).
2. **Dispatch code-reviewer subagent** with [`agents/code-reviewer-prompt.md`](agents/code-reviewer-prompt.md). The orchestrator passes: diff range, paths to rubrics + checklists, branch context (recent commits, related issues if known).
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

- [`agents/code-reviewer-prompt.md`](agents/code-reviewer-prompt.md) — the dispatched subagent's role prompt + input/output contracts.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — per-task reviewer (different scope, same rubrics).
- [`../subagent-driven-development/rubrics/quality-gate.md`](../subagent-driven-development/rubrics/quality-gate.md) — functional copy of code-team's quality rubric.
- [`../subagent-driven-development/rubrics/arch-gate.md`](../subagent-driven-development/rubrics/arch-gate.md) — functional copy of code-team's architecture rubric.
- [`../subagent-driven-development/checklists/security-checklist.md`](../subagent-driven-development/checklists/security-checklist.md) — functional copy of code-team's security checklist.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — sibling skill that fires alongside this one in finishing-a-branch flow.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator that invokes this skill.
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; this skill is Stage 6 (Review).
- `domain-teams:code-team` — passive gate for large audits; this skill may escalate there for >500 LOC or security-sensitive reviews.
