# Brief — code-toolkit run-scoped progress ledger + multi-agent coordination

> Date: 2026-06-16 · Stage: brainstorming → (next) writing-plans
> Surfaced by the design→spec→code pipeline dogfood (2026-06-15) + a deep-research pass on
> multi-agent coordination. Touches code-toolkit (merged, on-main, most-used) — surgical edits only.

## Problem

(Axis 1 — JTBD) When kouko runs a build that is **large**, gets **interrupted** (crash / session
death), or is worked by **several agents/sessions concurrently** on one repo, he needs **durable,
live, shared** execution progress — which atomic tasks are `done` / `claimed` / `blocked` — so that:
(1) interrupted work resumes without redo or loss; (2) parallel agents don't duplicate or collide on
the same task; (3) progress scales past what he can hold in his head. Today progress is **git commits**
(coarse, reconstruct-from-`git log`) + **ephemeral** in-run orchestrator state + a **manual** handoff
doc. There is no durable live ledger, and no convention for coordinating multiple concurrent sessions.

## Users

(Axis 2) kouko — solo dev, running `code-toolkit`'s SDD flow. Two confirmed modes: **(a)** one
orchestrator fanning out implementer subagents (already supported), and **(b)** multiple independent
sessions/agents on one repo at once (currently uncoordinated). Builds are sometimes large, sometimes
interrupted. He confirmed both (a) and (b) happen.

## Smallest End State

(Axis 3 — minimal core, ~90% reuse of existing primitives) **Two thin additions:**

1. **Plan-as-live-ledger.** Add an *optional* per-task field to `plan-format.md`:
   `Status: pending | claimed(@<agent>) | done(<sha>) | blocked`. SDD writes it back + commits as each
   task resolves (DONE → `done(<sha>)`; dispatched → `claimed(@agent)`; BLOCKED → `blocked`). The plan
   file becomes the **durable, shared progress ledger** — resume reads it; it scales (explicit status
   vs reconstructing from `git log`); it is the "shared task doc" the research names as the
   collision-prevention layer that worktrees alone cannot provide. Default omitted → fully backward
   compatible (a plan with no Status fields behaves exactly as today).

2. **Multi-agent coordination convention** (the (b) gap). Document — in `dispatching-parallel-agents`
   (extending it from (a)-only to also cover (b)) — the canonical stack the research converged on:
   **worktree-per-agent** (reuse `using-git-worktrees`) + **static up-front partition** of the plan's
   `Independent: true` tasks across agents (the simplest robust claim when tasks are known + file-disjoint)
   + each agent updates **its slice's `Status`** in the shared ledger + **PR-per-agent**. State the key
   pitfall the research surfaced: *worktree isolation does NOT prevent overlapping-edit collisions — the
   `Files touched` disjointness partition is the real defense.* Practical parallelism 3–5 agents.

**Verified by:** re-running SDD on a real multi-task plan AND simulating an interruption (kill mid-plan
→ resume purely from the ledger, redoing only the in-flight task).

## Current State Evidence

- **Forward (the touch point):** `code-toolkit/skills/writing-plans/references/plan-format.md:47-59` —
  the per-task block has Description / Module / Files-touched / Context-paths / Acceptance /
  External-surfaces / Dependencies / Independent / Brief-item-covered, but **no `Status` field**. The
  plan is a **static** artifact; progress is not represented in it.
- **Reverse (SSOT ownership):** `plan-format.md` is **NOT** in `code-toolkit/scripts/distribute.py`'s
  synced canonical set (grep returned nothing) — it is a writing-plans reference, safe to edit directly
  without tripping the byte-identity drift gate.
- **Error / recovery:** `code-toolkit/skills/subagent-driven-development/SKILL.md:99` — SDD "commit each
  task's `PASS` artifacts immediately" → durable progress today = git commits (task-level, coarse). Per-
  task `status` (SKILL.md:94-96) is tracked **in-run only**, never written to a durable ledger.
- **Data:** cross-session recovery today = `dev-workflow:handoff` (manual, on graceful wrap-up). No
  continuous/finer-grained durable progress.
- **Boundary:** `code-toolkit/skills/dispatching-parallel-agents/SKILL.md:62-65` — the harness runs
  concurrent `Agent` calls only within one assistant message → **single-orchestrator fan-out only**. No
  multi-session / worktree / claim coordination. `code-toolkit/skills/using-git-worktrees/SKILL.md`
  exists (the isolation primitive) but is **uncoupled** from any progress/claim ledger.

### Evidence paths appendix
- `code-toolkit/skills/writing-plans/references/plan-format.md`,
  `code-toolkit/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- `code-toolkit/skills/subagent-driven-development/SKILL.md`,
  `code-toolkit/skills/dispatching-parallel-agents/SKILL.md`, `code-toolkit/skills/using-git-worktrees/SKILL.md`
- Research (2026-06-15, deep-research): multi-agent coordination = worktree+branch+PR+static-partition+
  commit-per-task+shared-task-doc (O'Reilly, Claude Code docs, maildir/Kleppmann, Temporal); none of
  OpenSpec/Kiro/Spec-Kit verify code↔spec (our tests/VERIFY already do).

## Decision

Add a **run-scoped, git-backed progress ledger** to code-toolkit as two surgical, backward-compatible
edits: (1) an optional `Status` field in `plan-format.md` that SDD maintains + commits per task; (2) a
documented multi-agent coordination convention (worktree-per-agent + static `Independent`-task partition
+ shared-ledger status + PR-per-agent) in `dispatching-parallel-agents`. We will **NOT** build a status
DB, a durable-execution engine, dynamic runtime task-claiming, a living-SoT, or code↔spec conformance
tracking — the research shows git-commit-per-task + a shared status doc + static partition is the
industry-canonical, lowest-debt stack for a solo/few-agent setup, and tests already cover conformance.

## Out of Scope

- **Dynamic runtime claiming** (atomic-mv directory-queue / lease + fencing tokens). Static partition
  covers solo/few-agents (tasks are known + `Files touched`-disjoint at plan time). Re-trigger: many-agent
  dynamic load-balancing where static partition wastes idle agents.
- **Living-SoT / OpenSpec-CLI adoption** — separate, spec-layer-only concern; orthogonal to run progress.
- **code↔spec conformance tracking** — already covered by tests / `verification-before-completion`
  (research confirmed we are ahead of OpenSpec/Kiro/Spec-Kit here).
- **A status DB / Temporal / non-git durable store** — git-commit-per-task is the durable ledger.
- **The DESIGN→spec seam** (the other parked phase-2 item) — separate brief.
- **A TodoWrite replacement** — TodoWrite stays the in-session ephemeral view; the ledger is the durable
  cross-session one.

## Alternatives Considered

(Axis 4 — research-grounded, deep-research 2026-06-15, EN+JA)
- **plan-as-live-ledger + static partition + worktree-per-agent** — *chosen.* Industry-canonical
  (O'Reilly conductors→orchestrators; Claude Code `isolation: worktree`; JA Zenn). Lowest debt; ~90%
  reuse. Con: static partition can idle agents on skew (acceptable for few-agents).
- **Atomic-mv directory-queue (maildir/FSQ) for dynamic claiming** — *deferred.* Simplest *dynamic*
  claim primitive (POSIX atomic rename, no locks) + TTL sweeper; only needed when tasks aren't known up
  front or load must rebalance. Heavier than static partition for the solo case.
- **Lease + fencing tokens** (Kleppmann) — *rejected for now.* Correct under pauses/clock-skew, but
  fencing-token machinery is overkill without a shared mutable store; static partition sidesteps it.
- **Durable-execution engine (Temporal / Step Functions)** — *rejected.* Replay-from-history is powerful
  but infra-heavy; git-commit-per-task gives replay-from-last-checkpoint with zero infra for solo.

## What Becomes Obsolete

(Axis 5) Nothing is deleted. The manual "reconstruct progress from `git log` + author a handoff to
recover" becomes **partly redundant** for in-run recovery (the live ledger is the continuous version) —
but `handoff` stays for cross-session narrative + verification commands. The ledger makes in-run progress
**explicit** where it was previously implicit (commits) or ephemeral (orchestrator state).

## Open Questions

- **Where SDD writes Status:** does the orchestrator edit the plan file per task (one commit each), or
  batch per wave? (Lean: per task, to keep the ledger maximally current for crash-recovery.)
- **Status vocabulary:** `claimed(@agent)` owner format for (b) — agent id source? (Lean: the worktree
  branch name, which is unique per agent.)
- **plan-document-reviewer:** should it accept/ignore the optional Status field, or validate its values?
  (Lean: accept + ignore — Status is runtime state, not plan-authoring content the reviewer gates.)
- **Governance:** synthetic examples only; no company/customer/sibling-project names in any committed
  file (run the identifiable-token grep before commit); explicit `git add <paths>`, never `-A`.
