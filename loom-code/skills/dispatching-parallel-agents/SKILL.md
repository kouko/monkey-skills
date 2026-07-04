---
name: dispatching-parallel-agents
description: |
  Use when 2+ independent domains can run concurrently — unrelated failing tests, atomic tasks marked independent:true, disjoint data fetches. Dispatch one subagent per domain in one message (multiple Agent calls). Not when domains share files/state.
version: 0.9.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, the parent orchestrator already chose the dispatch shape. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill solves

When the work is **2+ independent problem domains** — fixes in unrelated test files, audits across unrelated modules, data fetches for disjoint inputs — default sequential dispatch wastes wall-clock time. Each domain investigation is independent and can happen concurrently.

Core principle: **one agent per independent problem domain. Let them work concurrently.**

This is the **across-domain dispatch** layer. It is **not**:

- A replacement for `subagent-driven-development` — SDD's triad is per-task within one domain; this skill is across-task / across-domain.
- A license to parallelize implementers writing to the same files — file conflicts are forbidden.
- An exemption from `tdd-iron-law` per branch — every branch still writes the failing test first.

## When to use vs. when NOT to

| Scenario | Dispatch in parallel? |
|---|---|
| 3+ test files failing for unrelated reasons | ✅ Yes — one implementer per file |
| Security audit across multiple modules | ✅ Yes — one reviewer per module |
| Data fetch for N tickers / N regions / N feeds | ✅ Yes — one data agent per input |
| Plan atomic tasks marked `independent: true` AND `files touched` disjoint | ✅ Yes — dispatch those implementers concurrently |
| Two reviewers on one artifact (spec-rev + code-quality-rev) | ❌ SDD already does this per-task; don't double-wrap |
| Single domain, complex but cohesive | ❌ One focused subagent, not N fragmented ones |
| Tasks share a file or symbol | ❌ Merge conflicts + non-deterministic state — sequence, or split the file first |
| Sequential data dependency (B needs A's output) | ❌ By definition not parallel |
| Failures might share a root cause / root cause unknown | ❌ One agent investigates first — fragmenting hides the shared cause |

Default is **sequential**; parallel dispatch is the exception you justify per the criteria below.

## The pattern

### 1. Identify independent domains

A domain is independent when **all** hold:

- No shared file with any other domain (or the shared file is read-only in all branches).
- No shared symbol that any branch will rename / remove / re-export.
- No sequential data dependency (Agent B's input does not include Agent A's output).

If you cannot state the independence in one sentence per domain, the work is not independent. Stop and split better.

### 2. Compose focused agent prompts

Each agent gets:

- **Specific scope** — one domain, one set of files, one outcome.
- **Self-contained context** — all paths and reference docs in the prompt. Subagents do NOT inherit this session's history.
- **Constraints** — what NOT to touch (the other domains' files, by path).
- **Expected output** — the verdict / status shape (`status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED` for implementers; `PASS / PASS_WITH_NOTES / NEEDS_REVISION` for reviewers).

### 3. Dispatch all N subagents in one fan-out step

Your host determines exactly what "one fan-out step" looks like as a tool call — see your host's tool-mapping reference under `using-loom-code/references/` (`claude-code-tools.md`'s "concurrent calls in one assistant message" shape, or `codex-tools.md`'s native multi-agent spawn-and-wait) for the concrete syntax, and [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §A1 for a Claude-Code-specific naming pitfall to avoid (Codex has no equivalent). The invariant that holds regardless of host:

```
✅ Concurrent — all N dispatch calls issued together, in the same fan-out step
   implementer(domain A)  ·  implementer(domain B)  ·  implementer(domain C)

❌ Sequential — one dispatched and awaited, THEN the next dispatched
   implementer(domain A) → wait for A to return → implementer(domain B)
```

The same rule applies to mixed shapes — e.g. one implementer + one Explore + one reviewer for independent domains all dispatched in the same fan-out step.

### 4. Aggregate results

When all parallel agents return:

1. Read each verdict / status. Don't drop or smooth any of them.
2. Check for accidental file overlap: did any two agents edit the same file? Should not happen if step 1 was honest; if it did, treat as a plan error — resolve manually now, split better in the next plan.
3. Aggregate by rule:
   - All `DONE` / `PASS` → integrate, move on.
   - Any `DONE_WITH_CONCERNS` / `PASS_WITH_NOTES` → integrate, but surface the concerns / notes to the user; do not silently drop them (they are the non-blocking design-feedback channel).
   - Any `NEEDS_REVISION` → re-dispatch **only that one branch** with the findings. Other branches keep their results.
   - Any `BLOCKED` → apply the unblock step or surface to user.
   - Any `NEEDS_CONTEXT` → surface to user; do not re-dispatch blind.
4. Run the package-level test suite **once** at the integration point (per `verification-before-completion`) — not per branch. Per-branch suites pass in isolation; the combined diff can still fail.

## TDD iron-law per branch

Every parallel branch dispatched as a code writer still follows `tdd-iron-law` inside its scope. Parallel dispatch does **not** waive "failing test first" anywhere — "small + parallel" is the rationalization combo, refuse it.

If the branch's task is "fix failing test X", the failing test already exists; the branch's job is the GREEN step (and refactor). If the branch's task is "add new feature Y", the branch's first action is still writing the failing test.

## Plan markup (opt-in)

`writing-plans` can mark atomic tasks `independent: true` to signal that this skill may dispatch them concurrently. The marker is the plan author's claim, not a guarantee:

```markdown
## Task 3 — Add CSV export
- independent: true
- files touched: src/export/csv.ts, src/export/csv.test.ts
- ...

## Task 4 — Add JSON export
- independent: true
- files touched: src/export/json.ts, src/export/json.test.ts
- ...
```

The orchestrator may dispatch Task 3 and Task 4 in parallel only when **both** conditions hold:

1. Each task declares `independent: true`.
2. Their `files touched` sets are disjoint.

If either condition fails, fall back to SDD's sequential dispatch. `independent: true` is opt-in by the plan author.

## Multiple concurrent sessions on one repo (mode b)

Everything above is **mode (a)**: one orchestrator fans out subagents in a single assistant message — they **share one checkout**, the harness runs them concurrently, results aggregate in that orchestrator. Mode **(b)** is different: **several independent sessions/agents working the same repo at once** (e.g. you run two Claude sessions in parallel). The harness does **not** coordinate across sessions, so (b) needs an explicit convention. The industry-canonical stack (worktree + branch + partition + PR) applies:

1. **Worktree-per-agent** — each concurrent agent gets its own `git worktree` (see [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md); Claude Code's `isolation: worktree` automates create + cleanup). This isolates the working files.
2. **Static up-front partition** — assign each agent a **disjoint slice** of the plan's `Independent: true` tasks (e.g. agent A: tasks 1–4, agent B: tasks 5–8). Because the slices' `Files touched` sets are disjoint *by the plan*, no runtime locking/claiming is needed — partition is the simplest robust claim when the tasks are known up front. (Dynamic runtime claiming is out of scope; revisit only if many agents must load-balance an unknown task set.)
3. **Shared ledger = the plan's `Status` field** — each agent writes `claimed(@<its-worktree-branch>)` / `done(<sha>)` / `blocked` into the plan (see `../writing-plans/references/plan-format.md` §Progress ledger). The committed plan is the shared task-claim doc that lets the agents see who has what — worktrees isolate *files*, the ledger coordinates *work*.
4. **PR-per-agent** — each agent opens its own PR; merge is human-gated at the integration point (run the package suite once on the merged state, per `verification-before-completion`).

**Load-bearing pitfall (the #1 mistake):** a worktree isolates files but does **NOT** prevent overlapping-edit collisions — if two agents edit the same file in different worktrees, you get conflicting parallel solutions and the merge review becomes the bottleneck. **The `Files touched` disjointness partition (step 2) is the real collision defense, not the worktree.** Verify partition disjointness before launching concurrent agents.

**Practical ceiling:** ~3–5 concurrent agents. Beyond that, wait-time + integration/merge cost dominate and throughput stops scaling linearly.

## Red flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Let's run three implementers on the same branch at once."* | Multiple implementers on shared files = conflicts + non-deterministic state. | Refuse. Across-task parallelism requires disjoint `files touched`. |
| *"Skip the independence check — git will sort it out."* | Merge conflicts cost more than the parallelism saves. | Refuse. Honest independence check is the precondition. |
| *"Each parallel branch can skip TDD since they're small."* | "Small + parallel" is the rationalization combo. | Refuse. `tdd-iron-law` applies per branch. |
| *"Run the test suite once per branch and we're done."* | Per-branch suites pass in isolation; the combined diff can still fail. | Refuse. `verification-before-completion` runs once on the merged state. |
| *"Investigate these 3 failures in parallel."* (root cause unknown) | If the failures share a root cause, fragmenting the investigation hides it. | One agent investigates first, identifies domains, then dispatch parallel fixes. |
| *"They probably don't touch the same file — just dispatch."* | "Probably" is not "do not". | Verify file disjointness before dispatching. |
| 「重なってないから並行で / 應該不會衝突吧」 | Same rationalization, localized. | Same refusal — verify, don't assume. |

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream** | [`../writing-plans/SKILL.md`](../writing-plans/SKILL.md) | Produces the `independent: true` atomic tasks this skill consumes. |
| **Upstream** | Direct user invocation | "Fix these 3 unrelated test files in parallel" / "audit these 4 modules at once". |
| **Inside (per branch)** | [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) via `loom-code:implementer` | Each branch follows `tdd-iron-law`, reports `status`; not waived by parallel dispatch. |
| **Inside (per branch)** | `loom-code:code-quality-reviewer` / `code-reviewer` | Each branch produces a three-valued verdict; aggregation happens at this skill's layer. |
| **Downstream** | [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) | Runs **once** at integration, not per branch. |
| **Lateral** | [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) | Per-task triad inside one domain; this skill is the across-task complement. |
| **Lateral** | [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) | Mode (a) in-session agents share one checkout and need no worktree; **mode (b) concurrent sessions require worktree-per-agent** (see §Multiple concurrent sessions). |
| **Router** | [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) | This skill is auxiliary — no Skill Priority stage, on-demand. |

Original pattern: superpowers v5.1.0 `dispatching-parallel-agents`, adapted for loom-code's TDD iron-law + verdict aggregation.
