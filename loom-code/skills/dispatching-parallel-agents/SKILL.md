---
name: dispatching-parallel-agents
description: |
  Use when 2+ independent domains can run concurrently — unrelated failing tests, atomic tasks marked independent:true, disjoint data fetches. Dispatch one subagent per domain in one message (multiple Agent calls). Not when domains share files/state.
version: 0.9.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, the parent orchestrator already chose the dispatch shape. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## When to use vs. when NOT to

Use concurrent agents for **2+ independent problem domains**: unrelated test-file fixes, separate module audits, or disjoint data inputs. Core rule: **one agent per independent domain, working concurrently**.

This is the across-domain layer. It does not replace `subagent-driven-development` (SDD's triad works within one task), permit concurrent writes to shared files, or waive `tdd-iron-law` on any branch.

| Scenario | Parallel? |
|---|---|
| Unrelated failing files; separate module audits; disjoint data inputs | Yes — one agent per domain/input |
| Plan tasks marked `independent: true` with disjoint `files touched` | Yes |
| Two SDD reviewers on one artifact; one cohesive domain | No — use the existing focused/SDD dispatch |
| Shared file/symbol/state; B needs A's output | No — sequence or split first |
| Failures may have shared a root cause, or cause is unknown | No — one agent investigates first, then fan out proven domains |

Sequential is the default; justify parallelism with the checks below.

## Procedure

### 1. Prove independent domains

All conditions must hold:

- No shared file with another domain, unless every branch reads it only.
- No shared symbol that any branch will rename, remove, or re-export.
- No sequential data dependency: one agent's input cannot require another's output.

State the proof in one sentence per domain. If you cannot, stop and split better. “Probably disjoint” is not proof, and git conflict handling is not a substitute.

Read-only overlap is safe only when no child can generate, format, rename, or otherwise mutate the shared artifact. Treat shared configuration, generated indexes, migration ledgers, package locks, and public export surfaces as writable state unless the prompt explicitly keeps them read-only. A task that is computationally independent may still be operationally coupled through one of these surfaces.

Examples of sound partitions include one failing test file per independently diagnosed cause, one security reviewer per unrelated module, or one fetch agent per region whose result can be collected without another region's output. “Three symptoms in one service” is not a partition until an initial investigator demonstrates distinct causes.

### 2. Write domain-focused prompts

Each child receives:

- one domain, its files, and one outcome;
- self-contained paths and reference context (children do not inherit session history);
- explicit paths it must not touch; and
- the expected result shape: implementers return `status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED`; reviewers return `PASS / PASS_WITH_NOTES / NEEDS_REVISION`.

For anchoring, provenance, locate arms, and reviewer independence, follow [`../subagent-driven-development/references/dispatch-hygiene-notes.md`](../subagent-driven-development/references/dispatch-hygiene-notes.md) §Dispatch-packet context.

Prompts must name evidence and boundaries rather than saying “handle domain A.” Include the exact test or acceptance condition, commands the child may run, and the files owned by other branches. Do not ask multiple children to solve the same problem competitively: that creates conflicting solutions rather than parallel progress. The parent retains orchestration and integration ownership.

### 3. Dispatch all N subagents in one fan-out step

**Resolve the dispatch profile** in [`../using-loom-code/references/dispatch-profile.md`](../using-loom-code/references/dispatch-profile.md) for every child before spawning. Then use the host mapping under `using-loom-code/references/` (`claude-code-tools.md` or `codex-tools.md`); Claude users must also heed [`../using-loom-code/references/environment-gotchas.md`](../using-loom-code/references/environment-gotchas.md) §A1.

The host syntax differs, but the invariant does not: **issue all N spawn calls before waiting for any result**. Claude may emit multiple Agent calls in one response; a host exposing one-child spawn operations issues them sequentially without an intervening wait. Mixed independent roles follow the same rule. Do not reinterpret one fan-out as one child containing N domains; domain isolation belongs in the child prompts.

### 4. Aggregate without smoothing

After every child returns:

1. Preserve every status, concern, and note.
2. Check actual edits for overlap. Any shared edit means the plan was wrong; resolve it manually and partition better next time.
3. Apply the result rules:
   - all `DONE` / `PASS`: integrate;
   - any `DONE_WITH_CONCERNS` / `PASS_WITH_NOTES`: integrate but surface the exact concerns;
   - `NEEDS_REVISION`: re-dispatch only that branch with its findings;
   - `BLOCKED`: perform its unblock step or ask the user;
   - `NEEDS_CONTEXT`: ask the user; never retry blindly.
4. **Run the package-level test suite once at the integration point** under [`verification-before-completion`](../verification-before-completion/SKILL.md). This integrated run is separate from each implementer's required pre-commit full run in [`../../agents/implementer.md`](../../agents/implementer.md); isolated passing branches do not prove the combined state.

Integration is not merely concatenating summaries. Inspect the produced artifacts, reconcile interfaces between otherwise disjoint branches, and retain attribution for each concern. When a revised branch returns, replace only its prior result; do not discard successful sibling evidence or rerun unrelated branches. If overlap appears after execution, record it as a planning error even when the edits merge cleanly.

## TDD per branch

Every code-writing branch follows [`tdd-iron-law`](../tdd-iron-law/SKILL.md): write the failing test first, then GREEN and refactor. An existing failing test already supplies RED for a fix; a feature branch must create RED. Reject “small + parallel” as an excuse to write production first.

## Plan markup

[`writing-plans`](../writing-plans/SKILL.md) may mark atomic tasks `independent: true`, but the marker is a claim, not proof. Dispatch marked tasks concurrently only when **each** is marked and their declared `files touched` sets are disjoint; otherwise use sequential SDD. The plan author opts in—an orchestrator cannot infer the marker.

Before dispatch, compare the complete declared file sets pairwise and check that no task consumes another task's output. If the work can be made independent by assigning ownership of a shared file to one task and moving other changes behind stable interfaces, revise the plan first; do not invent that partition during execution.

## Multiple concurrent sessions

The procedure above is mode (a): one orchestrator fans out children sharing one checkout. Mode (b)—separate sessions working in one repo—needs repository isolation and coordination:

1. **Worktree-per-agent**: create a dedicated git worktree and branch for each session; see [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md).
2. **Static up-front partition**: assign disjoint slices of `independent: true` tasks and verify their `Files touched` sets before launch. Worktrees isolate files on disk but do not prevent competing edits; this partition is the collision defense.
3. **Shared ledger**: record `claimed(@<branch>)`, `done(<sha>)`, or `blocked` in the plan's `Status` field per [`../writing-plans/references/plan-format.md`](../writing-plans/references/plan-format.md).
4. **PR-per-agent**: open one PR per session; merge remains human-gated, followed by the integrated package suite.

Dynamic claiming is out of scope. Prefer roughly 3–5 concurrent agents; above that, wait and integration costs usually dominate.

Mode (a) children deliberately share the orchestrator's checkout, so they require disjoint writes but not separate worktrees. Mode (b) sessions cannot rely on the in-session harness for coordination. Their branches and worktrees isolate working copies, while the committed plan ledger coordinates ownership across sessions. Neither mechanism replaces the static partition, and no session may silently claim an overlapping task.

## Mandatory refusals

Refuse and state the applicable remedy when asked to:

- run multiple implementers on shared files or “let git sort it out” — prove disjointness or sequence;
- skip TDD on a small parallel branch — `tdd-iron-law` still applies;
- treat per-branch tests as final evidence — run integrated verification;
- parallelize several unexplained failures — first identify whether they shared a root cause;
- trust “probably no overlap,” including 「重なってないから並行で」 or 「應該不會衝突吧」 — inspect files and dependencies.

## Composition

| Direction | Skill | Contract |
|---|---|---|
| Upstream | [`writing-plans`](../writing-plans/SKILL.md) or direct request | Supplies marked atomic tasks or explicitly disjoint domains. |
| Per branch | `tdd-iron-law` through `loom-code:implementer` | Keeps RED-first work and branch status. |
| Review | `code-quality-reviewer` / `code-reviewer` | Produces verdicts aggregated here. |
| Downstream | `verification-before-completion` | Verifies once at integration. |
| Lateral | [`subagent-driven-development`](../subagent-driven-development/SKILL.md) | Handles the within-task triad; this handles across-task concurrency. |
| Lateral | `using-git-worktrees` | Mode (a) shares a checkout; mode (b) requires worktree-per-agent. |
| Router | [`using-loom-code`](../using-loom-code/SKILL.md) | Loads this auxiliary skill on demand. |

Original pattern: superpowers v5.1.0 `dispatching-parallel-agents`, adapted for loom-code's TDD iron law and verdict aggregation.
