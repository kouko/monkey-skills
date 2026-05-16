---
name: writing-plans
description: 'Use AFTER brainstorming has produced a brief, BEFORE subagent-driven-development dispatches implementer subagents. Splits the brief into atomic ≤5-minute tasks with explicit acceptance criteria (RED test + GREEN condition) and a dependency graph. Self-reviews via plan-document-reviewer before declaring DONE. If brief produces >5 atomic tasks, routes back to brainstorming. If implementer returns BLOCKED, fallback re-splits the failing task into smaller children — Beck (2002) Test-Driven Development By Example Part II §Child Test pattern, ISBN 978-0321146533. 計画作成・原子タスク分解・Child Test fallback。計畫拆解・原子任務・遇阻再拆。'
version: 0.5.0-draft
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / debugger / plan-document-reviewer), the parent orchestrator already finished planning. **Do not** re-route through this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Takes a `brainstorming` output brief and produces a **plan**: an ordered list of atomic tasks that `subagent-driven-development` (SDD) can dispatch one at a time. Each task must be:

- **≤5 minutes** of work for the implementer subagent (P2-B);
- **One module** of touch surface (consistent with SDD's per-task scope);
- **Independently verifiable** — has a RED test (or RED diagnostic) that goes GREEN when the task is done.

The plan is the **paths-not-content handoff** between brainstorming and SDD. brainstorming wrote the brief; SDD consumes the plan; this skill produces the plan and self-reviews it before declaring DONE.

## The pipeline

```
brainstorming → brief (docs/superpowers/specs/<topic>.md)
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

If criteria 1+3 fight (≤5 min vs one-failing-test), criterion 3 wins: even a 1-minute task that needs 3 distinct assertions is 3 tasks. Time-box is a smell threshold, not a strict ceiling.

## Plan size ceiling — 5 atomic tasks

If the brief produces **>5 atomic tasks**, the brief is too big. **Do not silently produce a 10-task plan.** Two options:

1. **Route back to brainstorming**: the Smallest End State (Axis 3) was not actually smallest. Surface this and ask the user to re-cut.
2. **Split into multiple sequential briefs**: if the work genuinely needs >5 atomic tasks and the user agrees, write *N* briefs (each ≤5 tasks) explicitly labeled `<topic>-part-{1..N}.md`. Each brief gets its own plan and its own SDD run. The user ships them sequentially.

The 5-task ceiling is a deliberate forcing function for the brainstorming HARD-GATE. A 10-task plan is almost always a discovery failure, not a planning failure.

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
| Plan size ≤5 tasks | >5 tasks → route back to brainstorming, do not pass to reviewer |

If reviewer returns `NEEDS_REVISION`, writing-plans **fixes the plan** and re-runs the reviewer. Up to 2 rounds; if still NEEDS_REVISION after round 2, escalate to user (likely the brief itself needs revisiting).

## Output contract — the plan

Schema in [`references/plan-format.md`](references/plan-format.md). Plan lives at `docs/superpowers/plans/<date>-<topic>.md` (sibling to the brief). Minimum structure:

```markdown
# Plan: <topic>

Source brief: docs/superpowers/specs/<date>-<topic>.md
Total tasks: <N> (≤5)
Execution order: sequential | parallel-where-possible

## Task 1 — <short name>
- Description: <≤5 min unit of work, imperative voice>
- Module: <path or module name; one only>
- Context paths:
  - <path to existing code the implementer reads>
- Acceptance:
  - RED: <failing test name / diagnostic>
  - GREEN: <observable condition when done>
- Dependencies: <"none" | "Task N completes first" | "Tasks N, M parallel">

## Task 2 — ...
```

## Cross-skill contract

| Direction | Skill | Contract |
|---|---|---|
| **Upstream** | `brainstorming` | Produces brief at `docs/superpowers/specs/<topic>.md`. writing-plans reads it via Read tool. |
| **Downstream** | `subagent-driven-development` | Consumes plan at `docs/superpowers/plans/<topic>.md`. SDD reads plan + dispatches per-task triad. |
| **Self-review** | `plan-document-reviewer` (evaluator subagent) | writing-plans dispatches it after producing the plan. Returns PASS / NEEDS_REVISION. |
| **Recursive (BLOCKED fallback)** | `writing-plans` (self) | When SDD's implementer returns BLOCKED with decomposition signal, orchestrator re-invokes this skill on the failing task. |
| **Optional delegation** | `dev-workflow:complexity-critique` | If the plan produces >3 tasks and you suspect Axis 3 (smallest end state) was too generous, optionally invoke complexity-critique before falling back to brainstorming. |

Delegation contract per CLAUDE.md: pass **paths + structured seed context**, not file content. The target skill loads its own resources via Read.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Just skip planning, the brief is enough."* | The brief is the *what*; the plan is the *how-cut-into-atomic-pieces*. SDD needs atomicity, not just scope. | Refuse. Produce the plan even if it's only 1-2 tasks. If 1 task, the brief was an exemption candidate (§When NOT to Use). |
| *"This task is roughly an hour but I don't know how to split it."* | "I don't know how to split" is a discovery failure, not a planning failure. The brief did not articulate Axis 3 (smallest end state) tightly enough. | Surface back to brainstorming for Axis 3 re-cut, do not produce a 1-hour task that violates the ≤5-min rule. |
| *"10 atomic tasks is fine."* | No — see §Plan size ceiling. 10 tasks = brief too big. | Refuse the 10-task plan. Route back to brainstorming OR split into N briefs each with ≤5 tasks. |
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
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; this skill is Stage 2 (Planning).
