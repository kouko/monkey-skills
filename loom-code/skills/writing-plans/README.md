# writing-plans

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Bridge between [`brainstorming`](../brainstorming) (produces the brief) and [`subagent-driven-development`](../subagent-driven-development) (dispatches subagents). Splits the brief into ≤5 atomic tasks with explicit RED-GREEN acceptance, self-reviews via plan-document-reviewer, and handles BLOCKED fallback per Kent Beck (2002) §Child Test pattern (ISBN 978-0321146533).

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## The pipeline writing-plans sits in

```
brainstorming → brief                         (Discovery stage)
                  ↓
              writing-plans → plan + self-review  (THIS SKILL — Planning stage)
                  ↓ (PASS)
              subagent-driven-development → per-task triad
                                                 (Execution stage)
                  ↓
              tdd-iron-law (inside each implementer)
```

## The hard rule

**Per-task, one failing test.** If you can't write ONE failing test that goes green when a task is done, it's not one task — split it (or if it needs 3 tests, it's 3 tasks). No time estimate is part of this criterion: an LLM agent has no experiential grounding in wall-clock duration, and no rigorous source ties a plan-writer's completion-time guess to agent reliability — see [`SKILL.md`](SKILL.md) §No time-box criterion for the full research this rests on.

This pushes back on briefs that try to do too much and on plans that hide complexity in vague tasks — the forcing function is the test, not a clock.

*(Separately, plan size is governed by critical-path **depth** ≤5 — the longest chain of dependent tasks, not total task count; a wide-but-shallow plan with many independent tasks is fine. See [`SKILL.md`](SKILL.md) §Plan size ceiling.)*

## What each task carries

Per [`references/plan-format.md`](references/plan-format.md), every task ships with:

- **Description**: one-assertion imperative-voice action
- **Module**: one path / module name (not two)
- **Context paths**: existing code the implementer reads (paths-not-content)
- **Acceptance**: RED test name + GREEN observable condition
- **Dependencies**: `none` | `Task N completes first` | `Tasks N, M parallel`
- **Brief item covered**: quote / reference from the brief's Smallest End State / Decision

This shape is what `subagent-driven-development` consumes when dispatching the three subagents per task.

## Self-review before declaring DONE

After producing the plan, writing-plans dispatches [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) as an evaluator subagent. The reviewer runs 16 checks (2 non-blocking: one retired, one advisory — 14 can actually fail) covering per-task one-failing-test acceptance, brief-task coverage map, DAG no-cycles, etc., and returns PASS / NEEDS_REVISION. If NEEDS_REVISION, writing-plans patches the plan and re-reviews. Up to 2 rounds; if still failing, escalate to user (the brief itself likely needs revisiting).

The plan-document-reviewer is **separate from** SDD's spec-reviewer / code-quality-reviewer — those evaluate code; this one evaluates plan structure.

## BLOCKED fallback — Beck 2002 §Child Test

When SDD dispatches an implementer subagent and it returns `BLOCKED` with `unblock_step: "this task needs to be split smaller"`, the orchestrator **re-invokes writing-plans** on the failing task. This skill then splits the failing task into smaller children that ladder up — Kent Beck's Child Test pattern from Part II of *Test-Driven Development: By Example*:

> "When you are working on a test and it gets too big, write a smaller test that represents the broken part of the bigger test. Get the smaller test working. Then go back to the bigger test."

writing-plans applies the same pattern to plan tasks. This is the **primary recursive value** of the skill — not just initial planning, but adaptive re-planning when SDD encounters atomicity failures mid-run.

## When NOT to use

Enumerated exemptions in [`SKILL.md`](SKILL.md) §When NOT to Use:

- No upstream brief yet (route to brainstorming first)
- Brief's Smallest End State is itself one file with one assertion, and Out of Scope is exhaustive (brief IS the plan)
- Explicit user override AND a task list that already satisfies the plan-format schema

## What this skill does NOT do

- Does **not** write code. Plans are metadata about future work.
- Does **not** dispatch SDD subagents (implementer / spec-reviewer / code-quality-reviewer) — that's SDD's job.
- Does **not** estimate dev-time at all — the split-trigger is "can you write one failing test," not a clock.
- Does **not** decide priority / sequencing beyond what the dependency graph requires.

## See also

- [`SKILL.md`](SKILL.md) — operational spec (splitting framework, BLOCKED fallback flow, Red Flags).
- [`references/plan-format.md`](references/plan-format.md) — plan schema with worked example.
- [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) — self-review evaluator prompt.
- [`../brainstorming/SKILL.md`](../brainstorming/SKILL.md) — upstream brief producer.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — downstream plan consumer.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — discipline fired inside each implementer subagent.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 2 (Planning).
