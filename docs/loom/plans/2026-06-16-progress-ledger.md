# Plan: code-toolkit progress ledger + multi-agent coordination

**Source brief**: docs/loom/specs/2026-06-16-progress-ledger.md
**Total tasks**: 4
**Critical-path depth**: 2 (≤5 ✓) — T1 (Status field) → {T2, T3, T4}
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-16, 14/14)

> **Scope:** 4 surgical, backward-compatible **doc edits** to code-toolkit (no executable code; RED =
> grep diagnostics). T1 defines the optional `Status` ledger field; T2/T3/T4 consume it (SDD write-back,
> multi-agent convention, reviewer acceptance) — disjoint files, all depend only on T1. Status vocabulary
> is fixed once in T1 and referenced verbatim by the others: `pending | claimed(@<agent>) | done(<sha>) | blocked`.
> `plan-format.md` is NOT in the synced SSOT, so direct edits are safe. Governance: synthetic examples;
> identifiable-token grep before commit; explicit `git add <paths>`.

---

## Task 1 — Add the optional `Status` ledger field to plan-format.md

- **Description**: In `code-toolkit/skills/writing-plans/references/plan-format.md`, add an **optional** per-task field `- **Status**: pending | claimed(@<agent>) | done(<sha>) | blocked` to the per-task schema block, plus a short `### Progress ledger (v…+, optional)` subsection explaining: SDD maintains it per task (dispatched → `claimed(@agent)`, DONE → `done(<sha>)`, BLOCKED → `blocked`); the plan thereby becomes the durable, shared progress record that survives interruption and coordinates parallel agents; **default omitted → fully backward compatible** (a plan with no Status fields behaves exactly as today). Note it is runtime state, not authoring content.
- **Module**: `code-toolkit/skills/writing-plans/references/plan-format.md`
- **Files touched**: `code-toolkit/skills/writing-plans/references/plan-format.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-06-16-progress-ledger.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/writing-plans/references/plan-format.md`
- **Acceptance**:
  - **RED**: `grep -ciE 'Status:|progress ledger' plan-format.md` returns 0.
  - **GREEN**: the per-task schema lists the optional `Status` field with the exact 4-value vocabulary; a Progress-ledger subsection explains SDD maintenance + backward-compat (default omitted) + durable/shared/resume purpose.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Plan-as-live-ledger. Add an optional per-task field to plan-format.md: `Status: pending | claimed(@<agent>) | done(<sha>) | blocked`."

## Task 2 — SDD maintains Status + resumes from the ledger

- **Description**: In `code-toolkit/skills/subagent-driven-development/SKILL.md`, document that the orchestrator **writes the task's `Status` back into the plan per task** (on dispatch → `claimed(@agent)`; on resolved DONE → `done(<sha>)` with the commit sha; on BLOCKED → `blocked`) and **commits it** (lean: per task, to keep the ledger current for crash recovery), and that on **resume after interruption** it reads the ledger to skip `done(<sha>)` tasks and redo only the in-flight (`claimed`) one. Keep it additive to the existing per-task triad + per-task-commit behavior; reference the `Status` vocabulary defined in plan-format.md.
- **Module**: `code-toolkit/skills/subagent-driven-development/SKILL.md`
- **Files touched**: `code-toolkit/skills/subagent-driven-development/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/subagent-driven-development/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/writing-plans/references/plan-format.md`
- **Acceptance**:
  - **RED**: `grep -ciE 'ledger|Status|resume' subagent-driven-development/SKILL.md` is below the post-edit count (status/ledger/resume write-back not documented).
  - **GREEN**: SDD documents per-task Status write-back + commit (claimed/done(sha)/blocked) + resume-from-ledger (skip done, redo in-flight); references the plan-format Status vocabulary; additive (does not change the existing triad/commit rules).
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "SDD writes it back + commits as each task resolves … resume reads it."

## Task 3 — Multi-agent (b) convention in dispatching-parallel-agents

- **Description**: In `code-toolkit/skills/dispatching-parallel-agents/SKILL.md`, add a section extending the skill from single-orchestrator fan-out (a) to **multiple concurrent sessions/agents (b)**: the canonical stack = **worktree-per-agent** (reuse `using-git-worktrees`) + **static up-front partition** of the plan's `Independent: true` tasks across agents (assign disjoint task slices; the simplest robust claim when tasks are known + `Files touched`-disjoint) + each agent updates **its slice's `Status`** in the shared plan ledger + **PR-per-agent** (human-gated merge). State the load-bearing pitfall: **worktree isolation does NOT prevent overlapping-edit collisions — the `Files touched` disjointness partition is the real defense.** Note practical parallelism is ~3–5 agents. Keep the existing (a) single-message-fan-out content intact.
- **Module**: `code-toolkit/skills/dispatching-parallel-agents/SKILL.md`
- **Files touched**: `code-toolkit/skills/dispatching-parallel-agents/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/dispatching-parallel-agents/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/using-git-worktrees/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/writing-plans/references/plan-format.md`
- **Acceptance**:
  - **RED**: `grep -ciE 'worktree|static partition|per-agent|concurrent session' dispatching-parallel-agents/SKILL.md` is below the post-edit count (the (b) convention absent).
  - **GREEN**: a multi-session (b) section documents worktree-per-agent + static `Independent`-task partition + shared-ledger Status + PR-per-agent + the "worktree ≠ collision prevention; Files-touched partition is the defense" pitfall + ~3–5 parallelism; the existing (a) content is unchanged.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "Multi-agent coordination convention … worktree-per-agent + static up-front partition … + PR-per-agent."

## Task 4 — plan-document-reviewer accepts the optional Status field

- **Description**: In `code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md`, add a one-line note that the optional `Status` field (runtime ledger state) is **accepted and ignored** by the reviewer — it is not plan-authoring content and does not affect any check verdict.
- **Module**: `code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- **Files touched**: `code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/writing-plans/references/plan-format.md`
- **Acceptance**:
  - **RED**: `grep -ci 'Status' plan-document-reviewer-prompt.md` returns 0.
  - **GREEN**: the prompt notes the optional Status field is accepted + ignored (runtime state, not gated by any check).
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "plan-document-reviewer: accept + ignore — Status is runtime state, not plan-authoring content."

## Notes

- **Parallel leaves:** after T1, tasks T2/T3/T4 are `Independent: true` with disjoint `Files touched` → may dispatch concurrently. Critical-path depth = T1 → (any of T2/T3/T4) = 2.
- **Execution note:** these are 4 tightly-coupled DOC edits (shared `Status` vocabulary) to merged code-toolkit core. The orchestrator may execute them directly for cross-file consistency rather than via separate implementer subagents; the load-bearing quality gate is the **whole-branch review** + the **dogfood verification** (re-run SDD on a multi-task plan + interruption simulation), not per-task TDD (no executable code).
- **Out of plan (per brief Out of Scope):** dynamic runtime claiming, living-SoT / OpenSpec-CLI, code↔spec conformance, status DB/Temporal, the DESIGN→spec seam.
