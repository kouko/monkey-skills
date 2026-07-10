# requesting-code-review

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Whole-branch / whole-PR review skill. Different from `subagent-driven-development`'s per-task reviewer — this fires at the END of branch work, before merge, to catch cross-task interactions that per-task review can't see. Dispatches a code-reviewer subagent that loads loom-code's rubrics + checklists + standards (functional-copied from `domain-teams:code-team`) and produces severity-tagged structured review.

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## Per-task vs whole-branch review

| | SDD per-task reviewer | This skill (whole-branch) |
|---|---|---|
| Scope | One atomic one-failing-test task | All cumulative branch changes vs main |
| Fires | During each SDD task triad | After all SDD work DONE; before merge |
| Catches | Per-task quality lapses | Cross-task interactions, scope creep, architectural coherence |

Same rubrics, different scope. Both layers serve different failure modes — neither replaces the other.

## When to use

- *"Review my branch before I open the PR"* / *"Look at my changes"* / *"Is this ready to merge"*
- *"Code review please"* / *"Audit the diff"* / *"I've finished feature X, look it over"*
- Proactively after `subagent-driven-development` completes a multi-task plan
- Automatically invoked by `finishing-a-development-branch` as Step 1 of close-branch flow

## When NOT to use

Per [`SKILL.md`](SKILL.md) §When NOT to Use:
- Trivial diffs (one-line typo / doc-only / version bump / generated regen)
- Already-reviewed branch with no changes since
- Legacy code audit (use `domain-teams:code-team` passive gate instead — different use case)
- Explicit user override AND the change qualifies as trivial

## Output

Every verdict carries:

- **`standards_version`** stamp (from `plugin.json` `version`) — lets downstream readers date the review against a specific rubric revision (v0.7.0 reviewer-discipline R1).
- 7-dimension scores (security / architecture / correctness / naming / tests / refactoring / **cross-task-coherence** — branch-only).
- Severity-tagged findings (🔴 fatal / 🟡 should-fix / 🟢 nit), each citing `where:` (file:line or commit SHA range). **Missing `where` flips the verdict to `NEEDS_REVISION`** regardless of severity (v0.7.0 reviewer-discipline R2 — opaque findings are unfixable).
- ≤5-bullet summary.

Aggregation (aligned with `rubrics/quality-gate.md` SSOT):

- Any 🔴 → `NEEDS_REVISION`
- Any finding missing `where` → `NEEDS_REVISION` (malformed)
- **2 or more 🟡** → `NEEDS_REVISION` (aggregated warnings = systemic concern)
- Exactly 1 🟡, no 🔴, all with `where` → `PASS_WITH_NOTES`
- No 🔴, no 🟡 → `PASS`

R1+R2 discipline lives in `loom-code/scripts/_reviewer-discipline.md` (SSOT) and is auto-injected into the 3 reviewer agents by `distribute.py`.

## Cross-skill

- **Invoked by** `finishing-a-development-branch` (Step 1 of close-branch).
- **Optionally escalates to** `domain-teams:code-team` for large audits (>500 LOC, security-sensitive surface, incident-driven review).
- **Loads rubrics from** `../subagent-driven-development/{rubrics,checklists,standards}/` — same SSOT as per-task reviewer; no drift between layers.

## What this skill does NOT do

- Does **not** modify code (evaluator-only).
- Does **not** replace per-task SDD review.
- Does **not** run tests (`verification-before-completion`'s job).
- Does **not** trigger CI (pushing to remote does that; this skill runs before push).

## See also

- [`SKILL.md`](SKILL.md) — operational spec.
- [`../../agents/code-reviewer.md`](../../agents/code-reviewer.md) — subagent role prompt.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — per-task reviewer (different scope, same rubrics).
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — sibling pre-merge gate (test-suite).
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 6 (Review).
