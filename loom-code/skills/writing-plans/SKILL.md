---
name: writing-plans
description: |
  Use AFTER brainstorming produces a brief, BEFORE subagent-driven-development dispatches implementers. Splits it into atomic ≤5-min tasks with acceptance criteria (RED + GREEN) + a dependency graph. Re-splits a BLOCKED task into children.
version: 0.10.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / plan-document-reviewer), the parent orchestrator already finished planning. **Do not** re-route through this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Takes a `brainstorming` output brief and produces a **plan**: an ordered list of atomic tasks that `subagent-driven-development` (SDD) can dispatch one at a time. Each task must be:

- **≤5 minutes** of work for the implementer subagent (P2-B);
- **One module** of touch surface (consistent with SDD's per-task scope);
- **Independently verifiable** — has a RED test (or RED diagnostic) that goes GREEN when the task is done.

The plan is the **paths-not-content handoff** between brainstorming and SDD. brainstorming wrote the brief; SDD consumes the plan; this skill produces the plan and self-reviews it before declaring DONE.

## The pipeline

```
brainstorming → brief (docs/code-toolkit/specs/<topic>.md)
                  ↓
              writing-plans
                  ↓
              plan + plan-document-reviewer self-review
                  ↓ (PASS)
              subagent-driven-development
                  ↓ (per task: implementer → spec-reviewer + code-quality-reviewer)
              tdd-iron-law (inside each implementer)
                  ↓
              finishing-a-development-branch (Phase 3)
```

## When NOT to use

Enumerated exemptions only.

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **No brief upstream** | brainstorming has not produced a brief yet — routing this skill prematurely. | "I have a vague idea" — that needs brainstorming first, not skipping to plans. |
| **Brief explicitly says "single atomic task"** | brainstorming's Smallest End State is itself ≤5 min and Out of Scope is exhaustive. The brief IS the plan. | Brief that says "small" but Open Questions are non-empty — Open Questions block. |
| **Implementer returned BLOCKED with a sub-task fallback request** | This is the entry condition for the §BLOCKED fallback flow below — see that section, not §When NOT to Use. | An implementer returning BLOCKED for non-decomposition reasons (broken test infra, missing dependency) — that surfaces to user, not re-planned. |
| **Explicit user override** | User literally says "skip planning, here are the tasks" AND hands in a list that already satisfies the plan-format schema. | "Just figure it out" — that's an instruction to plan, not skip. |

## The splitting framework

Walk these in order for each prospective task. Stop expanding a task as soon as **all four** criteria are met.

| # | Criterion | Test |
|---|---|---|
| 1 | **Time-box** | Could a focused implementer subagent complete this in ≤5 minutes? If "maybe 10," split. |
| 2 | **Module scope** | Does this touch ≤1 module / ≤1 file boundary? If it crosses, split by boundary. |
| 3 | **Acceptance criterion** | Can you write ONE failing test now that goes green when this task is done? If you need 3 tests, this is 3 tasks. |
| 4 | **No hidden coupling** | Could this task be done in isolation, with only its declared dependencies satisfied? If you need to "also remember to update X," that's a missing dep — declare it. |

**Runnable-capability note.** When a task introduces a runnable capability — a new test suite, build step, lint target, e2e suite, migration command, or similar — its `Acceptance` criterion must include a line stating that the new verb is declared in the command surface (the project's declared commands — `AGENTS.md` commands section, `make`/`just` recipes, `package.json` scripts) and verified to run. This makes command-surface accretion visible at plan time, before the implementer ships it silently without a declared entry point.

If criteria 1+3 fight (≤5 min vs one-failing-test), criterion 3 wins: even a 1-minute task that needs 3 distinct assertions is 3 tasks. Time-box is a smell threshold, not a strict ceiling.

**Post-split parallel-marking pass.** After splitting, for each pair of tasks at the **same dependency level**: if their `Files touched` are disjoint **AND** there is no semantic dependency (no shared data / symbol, no doc-mirrors-code relationship), mark **both** `Independent: true`. This is the step that turns a flat task list into a parallelism-aware plan.

**Guard — disjoint files ≠ independent.** Disjoint `Files touched` is necessary but not sufficient. A real semantic dependency keeps two tasks sequential **regardless** of file-disjointness — e.g. a doc task that mirrors a code task (doc-mirrors-code), or a consumer task that imports a symbol the producer task defines. In those cases the tasks touch different files yet must run in order. The `Dependencies` field is the **execution floor**: if a semantic dependency exists, declare it in `Dependencies` and leave `Independent: false`, even when the files do not overlap.

## Plan size ceiling — critical-path depth ≤5

The ceiling is on **critical-path depth**, NOT total task count. Critical-path depth is the **longest chain of tasks linked by `Dependencies`** (the longest sequential path through the dependency DAG). N independent tasks at the **same dependency level** (disjoint `Files touched`, no semantic dependency) count as **ONE level**, not N. A plan with 8 tasks where 6 are parallel leaves at one level has a depth of ~2-3, not 8.

**No hard width cap in the plan.** Mark every parallel-eligible task `Independent: true` and let the dispatch / harness layer queue the concurrency — `dispatching-parallel-agents` names no numeric cap, so the plan declares eligibility and defers throttling downstream. A very wide wave (many `Independent: true` leaves) gets at most a soft "sanity-check that these really are independent" advisory; it is **never** a hard split-trigger. The only hard split-trigger is **depth >5**.

If the critical-path **depth** exceeds 5, the brief is too big. **Do not silently produce a deep chain.** Two options:

1. **Route back to brainstorming**: the Smallest End State (Axis 3) was not actually smallest — it baked in a long sequential dependency chain. Surface this and ask the user to re-cut.
2. **Split into multiple sequential briefs**: if the work genuinely needs a chain deeper than 5 and the user agrees, write *N* separate brief files (each with depth ≤5), explicitly labeled `<topic>-part-{1..N}.md`. Each brief is a standalone input to its own `writing-plans` run and its own SDD run. **Split = N brief files, not N plans from one brief.** A plan is 1-to-1 with one brief; producing two `## Part 1 / ## Part 2` sections inside a single plan file is not valid splitting.

The depth ceiling is a deliberate forcing function for the brainstorming HARD-GATE. A **deep chain** (critical-path depth >5) is almost always a discovery failure, not a planning failure. A **wide-but-shallow** plan (many independent leaves, shallow depth) is fine — it parallelizes cleanly and is NOT a discovery failure.

**Why depth — and why `5` is a heuristic, not a law.** For an LLM agent the binding constraint is the *sequential* chain: errors **compound** across dependent steps (chain reliability ≈ per-step-success^depth) and per-step accuracy itself **decays** as the chain lengthens. A depth-5 chain at ~95% per-step reliability succeeds only ~77% of the time — about where re-cutting scope starts to pay off. But the long-horizon-execution literature finds **no universal optimal step count** — the principled limit is a *function of per-step reliability*, not a constant. So treat **`5` as a deliberate default trigger, not a measured value**; tune it if your atomic-task steps are more or less reliable. (Grounding: error-compounding / long-horizon decay in LLM agents — e.g. "The Illusion of Diminishing Returns: Measuring Long-Horizon Execution in LLMs", arXiv 2509.09677. The depth-not-count *framing* also matches Bazel critical-path scheduling and Kanban WIP limits, which cap concurrency, not backlog — but those are human/scheduling analogies; the agent-native reason is error compounding. The `5` itself is inherited from the prior count-based ceiling, not independently derived.)

**Structural-split escape hatch (round-2 NEEDS_REVISION only):** If the plan-document-reviewer returns NEEDS_REVISION for a second round and the *sole* failure is a structural-size violation (a task is clearly >5 min but cannot be shrunk further without a brief change), split that oversized task into a fresh sibling part (a new `<topic>-part-N.md` brief → new plan) and treat it as a round-1 input to a fresh `writing-plans` run. The original plan's 2-round cap applies to the original tasks only; the new sibling part starts its own clean round count.

## BLOCKED fallback — Beck 2002 Child Test pattern

This is the **primary defining mechanism** of writing-plans's recursive value.

When SDD dispatches an implementer subagent and the implementer returns `BLOCKED` with `unblock_step: "this task needs to be split smaller"`, the orchestrator re-invokes writing-plans on the failing task. writing-plans then:

1. Reads the failing task description + the implementer's `unblock_step`.
2. Applies the splitting framework to produce **child tasks** that ladder up to the original.
3. The original task becomes a "parent" — when all children are DONE, the parent is DONE.
4. Self-reviews the child decomposition via plan-document-reviewer.
5. Returns the child plan to SDD.

This is **Kent Beck (2002) *Test-Driven Development: By Example*, Addison-Wesley, ISBN 978-0321146533, Part II §"Child Test"** verbatim:

> *"When you are working on a test and it gets too big, write a smaller test that represents the broken part of the bigger test. Get the smaller test working. Then go back to the bigger test."*

writing-plans applies the same pattern to plan tasks. The implementer's BLOCKED signal is the equivalent of "the test got too big to make pass in one step" — the fix is to write smaller tests (= split into child tasks), get them green, then re-attempt the parent.

**Anti-pattern**: silently ignoring BLOCKED and re-dispatching the same task hoping the implementer will figure it out. That violates SDD's 3-round retry cap and burns subagent budget. Always re-invoke writing-plans when BLOCKED carries a decomposition signal.

## Self-review — plan-document-reviewer

After producing the plan, writing-plans **must** dispatch [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) as an evaluator subagent. The reviewer checks:

| Check | Failure → NEEDS_REVISION |
|---|---|
| Each task ≤5 min (criterion 1) | Task estimated >5 min |
| Each task touches ≤1 module (criterion 2) | Task lists 2+ modules in `module` field |
| Each task has a failing-test acceptance (criterion 3) | `acceptance` field empty or doesn't name a RED test |
| Every brief item maps to ≥1 task | Brief Smallest End State item has no covering task |
| No orphan tasks (untraceable to brief) | Task exists but doesn't appear in brief's scope |
| Dependencies form a DAG (no cycles) | Task A depends on Task B which depends on Task A |
| Critical-path depth ≤5 | depth >5 → route back to brainstorming, do not pass to reviewer (total task count is uncapped) |

**Pre-patch before dispatch (saves a NEEDS_REVISION round):** Before dispatching the reviewer, Read [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) and scan Check 1 and Check 3. If the plan is missing `Plan-document-reviewer verdict: PENDING` in the top-level header, or if any task is missing a `Brief item covered:` line, patch those fields now. These two omissions are the most common Check-1 / Check-3 failures; pre-patching costs one Read and saves one full round-trip.

If reviewer returns `NEEDS_REVISION`, writing-plans **fixes the plan** and re-runs the reviewer. Up to 2 rounds; if still NEEDS_REVISION after round 2, escalate to user (likely the brief itself needs revisiting).

**Amending a PASS plan:** If the plan is changed after the reviewer returned PASS (e.g., a task description is tightened, a dependency is updated), either (a) re-run the plan-document-reviewer on the amended plan, OR (b) record a one-line skip note in the plan's `Notes` section explaining why the amendment is additive and schema-safe (e.g., "amended Task 2 description for clarity; all required fields and DAG structure unchanged — re-review skipped"). A stale PASS without a skip note is a silent gap.

## Output contract — the plan

Schema in [`references/plan-format.md`](references/plan-format.md). Plan lives at `docs/code-toolkit/plans/<date>-<topic>.md` (sibling to the brief). Minimum structure:

```markdown
# Plan: <topic>

Source brief: docs/code-toolkit/specs/<date>-<topic>.md
Total tasks: <N>   ← uncapped; width is fine (many parallel leaves OK)
Critical-path depth: <D> (≤5)   ← longest Dependencies chain; this is the ceiling
Execution order: sequential | parallel-where-possible
Plan-document-reviewer verdict: PENDING   ← required; reviewer will flip to PASS (timestamp)

## Task 1 — <short name>
- Description: <≤5 min unit of work, imperative voice>
- Module: <path or module name; one only>
- Files touched: <comma-separated paths the implementer will Write / Edit>
- Context paths:
  - <path to existing code the implementer reads>
- Acceptance:
  - RED: <failing test name / diagnostic>
  - GREEN: <observable condition when done>
- External surfaces: <per-task field — required when the task touches a non-stdlib
    external surface (the five categories in `references/plan-format.md` §External surfaces;
    a third-party lib like `packaging` for version/format work counts — prefer stdlib).
    Omit if pure internal logic. Per-task field, not a Notes catch-all.>
- Dependencies: <"none" | "Task N completes first" | "Tasks N, M complete first" |
    "Tasks N, M parallel" — semantics in `references/plan-format.md`; cross-part ordering
    uses "none" + a plan-level Notes entry (the field is within-plan only).>
- Independent: <true | false>  # opt-in marker for dispatching-parallel-agents
- Brief item covered: <quote or close paraphrase from brief's Smallest End State /
    Decision section — required; plan-document-reviewer Check 3 blocks on this field>

## Task 2 — ...
```

### Parallel-dispatch markup (v0.8.0+)

Two per-task fields signal eligibility for [`../dispatching-parallel-agents/SKILL.md`](../dispatching-parallel-agents/SKILL.md):

- **`Independent: true`** — the plan author's claim that this task has no shared symbol / no sequential data dependency with other `Independent: true` tasks. Default is `false`.
- **`Files touched: <paths>`** — the disjointness oracle. Two tasks are dispatch-parallel-safe **only when** both declare `Independent: true` AND their `Files touched` sets are disjoint.

If both conditions hold across N tasks, `dispatching-parallel-agents` MAY dispatch their implementers in one assistant message with N `Agent` calls. If either condition fails, SDD's sequential dispatch is the floor.

The markup is **opt-in**. A plan that omits it (or sets `Independent: false`) routes through SDD's standard sequential per-task triad. Claiming `Independent: true` with overlapping `Files touched` is a plan error — `plan-document-reviewer` should catch it; if not, `dispatching-parallel-agents` will refuse to dispatch.

## Cross-skill contract

| Direction | Skill | Contract |
|---|---|---|
| **Upstream** | `brainstorming` | Produces brief at `docs/code-toolkit/specs/<topic>.md`. writing-plans reads it via Read tool. |
| **Downstream** | `subagent-driven-development` | Consumes plan at `docs/code-toolkit/plans/<topic>.md`. SDD reads plan + dispatches per-task triad. |
| **Downstream (opt-in)** | `dispatching-parallel-agents` | Consumes tasks marked `Independent: true` with disjoint `Files touched`. Dispatches their implementers in one assistant message for concurrent execution. Fall back to SDD's sequential dispatch if either condition fails. |
| **Self-review** | `plan-document-reviewer` (evaluator subagent) | writing-plans dispatches it after producing the plan. Returns PASS / NEEDS_REVISION. |
| **Recursive (BLOCKED fallback)** | `writing-plans` (self) | When SDD's implementer returns BLOCKED with decomposition signal, orchestrator re-invokes this skill on the failing task. |
| **Optional delegation** | `dev-workflow:complexity-critique` | If the plan produces >3 tasks and you suspect Axis 3 (smallest end state) was too generous, optionally invoke complexity-critique before falling back to brainstorming. |

Delegation contract per CLAUDE.md: pass **paths + structured seed context**, not file content. The target skill loads its own resources via Read.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Just skip planning, the brief is enough."* | The brief is the *what*; the plan is the *how-cut-into-atomic-pieces*. SDD needs atomicity, not just scope. | Refuse. Produce the plan even if it's only 1-2 tasks. If 1 task, the brief was an exemption candidate (§When NOT to Use). |
| *"This task is roughly an hour but I don't know how to split it."* | "I don't know how to split" is a discovery failure, not a planning failure. The brief did not articulate Axis 3 (smallest end state) tightly enough. | Surface back to brainstorming for Axis 3 re-cut, do not produce a 1-hour task that violates the ≤5-min rule. |
| *"This chain is 8 tasks deep, that's fine."* | No — see §Plan size ceiling. Critical-path depth >5 = brief too big. (A wide-but-shallow 8-task plan is fine; a deep 8-link chain is not.) | Refuse the deep chain. Route back to brainstorming OR split into N briefs each with depth ≤5. |
| *"Skip the plan-document-reviewer, it's overkill."* | The reviewer catches the failure modes the splitting framework misses (orphan tasks, cycle dependencies, brief-task coverage gaps). | Refuse. Self-review is non-negotiable. If you genuinely produced a perfect plan, the reviewer takes 30 seconds to confirm. |
| *"Implementer returned BLOCKED, just retry."* | Beck Child Test pattern says split smaller, not retry. Silent retry burns SDD's 3-round cap. | Re-invoke writing-plans on the failing task per §BLOCKED fallback. |
| *"This task depends on Task 1, Task 3, AND a thing not in the plan."* | The "thing not in the plan" is a missing task. Declare it. | Add the missing task to the plan. Re-run plan-document-reviewer. |
| 「先跳過 plan 直接派 SDD 吧 / プランは飛ばして」 | Same rationalization, localized. | Same refusal — produce the plan. |

## What this skill does NOT do

- Does **not** write code. Atomic-task production is metadata about future work, not the work.
- Does **not** dispatch SDD subagents. That's SDD's job. writing-plans hands off the plan; SDD picks it up.
- Does **not** invoke the implementer / spec-reviewer / code-quality-reviewer prompts directly. Only plan-document-reviewer (a different evaluator scope).
- Does **not** estimate dev-time beyond the ≤5-min atomic-task threshold. If a task needs >5 min, that's a split-trigger, not an estimation exercise.
- Does **not** decide priority or sequencing beyond what the dependency graph requires. The user (or SDD) decides which independent tasks run first.

## See also

- [`references/plan-format.md`](references/plan-format.md) — full plan schema.
- [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) — evaluator subagent prompt.
- [`../brainstorming/SKILL.md`](../brainstorming/SKILL.md) — upstream brief producer.
- [`../brainstorming/references/handoff-brief-format.md`](../brainstorming/references/handoff-brief-format.md) — input contract.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — downstream plan consumer.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — discipline that fires inside each implementer subagent.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 2 (Planning).
