---
name: writing-plans
description: |
  Use AFTER brainstorming produces a brief, BEFORE subagent-driven-development dispatches implementers. Splits it into atomic tasks — each with one RED/GREEN test and a single module boundary — into a dependency graph.
version: 0.12.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / plan-document-reviewer), the parent orchestrator already finished planning. **Do not** re-route through this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Takes a `brainstorming` output brief and produces a **plan**: an ordered list of atomic tasks that `subagent-driven-development` (SDD) can dispatch one at a time. It can also consume a validated `loom-spec` change-folder as an alternate input — see §Consuming a loom-spec change-folder. Each task must be:

- **Independently verifiable** — has a RED test (or RED diagnostic) that goes GREEN when the task is done. This is the primary sizing constraint — see §The splitting framework.
- **One module** of touch surface (consistent with SDD's per-task scope).

The plan is the **paths-not-content handoff** between brainstorming and SDD. brainstorming wrote the brief; SDD consumes the plan; this skill produces the plan and self-reviews it before declaring DONE.

## The pipeline

```
brainstorming → brief (docs/loom/specs/<topic>.md)
                  ↓
              writing-plans
                  ↓
              plan + plan-document-reviewer self-review
                  ↓ (PASS) → kickoff briefing (one-way-door decisions)
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
| **Brief explicitly says "single atomic task"** | brainstorming's Smallest End State is itself one file with one assertion, and Out of Scope is exhaustive. The brief IS the plan. | Brief that says "small" but Open Questions are non-empty — Open Questions block. |
| **Implementer returned BLOCKED with a sub-task fallback request** | This is the entry condition for the §BLOCKED fallback flow below — see that section, not §When NOT to Use. | An implementer returning BLOCKED for non-decomposition reasons (broken test infra, missing dependency) — that surfaces to user, not re-planned. |
| **Explicit user override** | User literally says "skip planning, here are the tasks" AND hands in a list that already satisfies the plan-format schema. | "Just figure it out" — that's an instruction to plan, not skip. |

## The splitting framework

Walk these in order for each prospective task. Stop expanding a task as soon as **all three** criteria are met.

| # | Criterion | Test |
|---|---|---|
| 1 | **Acceptance criterion** (primary) | Can you write ONE failing test now that goes green when this task is done? If you need 3 tests, this is 3 tasks. |
| 2 | **Module scope** | Does this touch ≤1 module / ≤1 file boundary? If it crosses, split by boundary. |
| 3 | **No hidden coupling** | Could this task be done in isolation, with only its declared dependencies satisfied? If you need to "also remember to update X," that's a missing dep — declare it. |

**Runnable-capability note.** When a task introduces a runnable capability — a new test suite, build step, lint target, e2e suite, migration command, or similar — its `Acceptance` criterion must include a line stating that the new verb is declared in the command surface (the project's declared commands — `AGENTS.md` commands section, `make`/`just` recipes, `package.json` scripts) and verified to run. This makes command-surface accretion visible at plan time, before the implementer ships it silently without a declared entry point.

**No time-box criterion — why one isn't here.** A prior revision sized tasks by a fixed wall-clock estimate, later demoted to a smell-check, then removed. An LLM agent has no grounding in duration (arXiv:2510.23853); no source ties a plan-writer's time guess to actual reliability (arXiv:2505.05115 models decay against externally-benchmarked human-difficulty, a different quantity). Traditional size research uses file/diff boundary; surveyed coding-agent products document no time-based rule. Conclusion: no time-based sizing here. A task that "feels long" signals to re-examine criterion 1 — it likely resolves to more than one assertion or crosses a module boundary.

**Post-split parallel-marking pass.** After splitting, for each pair of tasks at the **same dependency level**: if their `Files touched` are disjoint **AND** there is no semantic dependency (no shared data / symbol, no doc-mirrors-code relationship), mark **both** `Independent: true`. This is the step that turns a flat task list into a parallelism-aware plan.

**Guard — disjoint files ≠ independent.** Disjoint `Files touched` is necessary but not sufficient. A real semantic dependency keeps two tasks sequential **regardless** of file-disjointness — e.g. a doc task that mirrors a code task (doc-mirrors-code), or a consumer task that imports a symbol the producer task defines. In those cases the tasks touch different files yet must run in order. The `Dependencies` field is the **execution floor**: if a semantic dependency exists, declare it in `Dependencies` and leave `Independent: false`, even when the files do not overlap.

## Plan size ceiling — critical-path depth ≤5

The ceiling is on **critical-path depth**, NOT total task count. Critical-path depth is the **longest chain of tasks linked by `Dependencies`** (the longest sequential path through the dependency DAG). N independent tasks at the **same dependency level** (disjoint `Files touched`, no semantic dependency) count as **ONE level**, not N. A plan with 8 tasks where 6 are parallel leaves at one level has a depth of ~2-3, not 8.

**No hard width cap in the plan.** Mark every parallel-eligible task `Independent: true` and let the dispatch / harness layer queue the concurrency — `dispatching-parallel-agents` names no numeric cap, so the plan declares eligibility and defers throttling downstream. A very wide wave (many `Independent: true` leaves) gets at most a soft "sanity-check that these really are independent" advisory; it is **never** a hard split-trigger. The only hard split-trigger is **depth >5**.

If the critical-path **depth** exceeds 5, the brief is too big. **Do not silently produce a deep chain.** Two options:

1. **Route back to brainstorming**: the Smallest End State (Axis 3) was not actually smallest — it baked in a long sequential dependency chain. Surface this and ask the user to re-cut.
2. **Split into multiple sequential briefs**: if the work genuinely needs a chain deeper than 5 and the user agrees, write *N* separate brief files (each with depth ≤5), explicitly labeled `<topic>-part-{1..N}.md`. Each brief is a standalone input to its own `writing-plans` run and its own SDD run. **Split = N brief files, not N plans from one brief.** A plan is 1-to-1 with one brief; producing two `## Part 1 / ## Part 2` sections inside a single plan file is not valid splitting.

The depth ceiling is a deliberate forcing function for the brainstorming HARD-GATE. A **deep chain** (critical-path depth >5) is almost always a discovery failure, not a planning failure. A **wide-but-shallow** plan (many independent leaves, shallow depth) is fine — it parallelizes cleanly and is NOT a discovery failure.

**Why depth — and why `5` is a heuristic, not a law.** For an LLM agent, errors **compound** across dependent steps and per-step accuracy itself decays as a chain lengthens — a depth-5 chain at ~95% per-step reliability succeeds only ~77% of the time. But the long-horizon literature finds no universal optimal step count — the limit is a function of per-step reliability, not a constant. So treat **`5` as a deliberate default, not a measured value**; tune it if your steps are more or less reliable. (Grounding: arXiv:2509.09677 on long-horizon error-compounding; Toby Ord, arXiv:2505.05115, models decay per minute of externally-benchmarked human-difficulty, not per agent step, and names no step-count — cited only as further decay-with-magnitude evidence, not support for "5". The `5` itself is inherited from the prior count-based ceiling, not independently derived.)

**Structural-split escape hatch (round-2 NEEDS_REVISION only):** If the plan-document-reviewer returns NEEDS_REVISION for a second round and the *sole* failure is a structural-size violation (a task structurally cannot resolve to one failing test within one module boundary — Check 6 keeps failing no matter how the description is reworded — and cannot be shrunk further without a brief change), split that oversized task into a fresh sibling part (a new `<topic>-part-N.md` brief → new plan) and treat it as a round-1 input to a fresh `writing-plans` run. The original plan's 2-round cap applies to the original tasks only; the new sibling part starts its own clean round count.

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

After producing the plan, writing-plans **must** dispatch [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) as an evaluator subagent — a one-shot blocking call that waits for and returns its verdict directly (see your host's tool-mapping reference for the exact shape, and [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §A1 for a Claude-Code-specific naming pitfall to avoid — Codex has no equivalent). That prompt holds the **authoritative, full check list** — do not maintain a duplicate copy here (it drifts). The highest-value checks, so you can self-pre-screen before dispatch:

- **one-failing-test acceptance** — each task names a specific RED test (criterion 1, primary);
- **every brief item covered** — every Smallest End State / Decision item maps to ≥1 task, no orphan tasks;
- **DAG, no cycles** — `Dependencies` form an acyclic graph with critical-path depth ≤5.

The prompt also enforces parallel-dispatch checks (`Independent: true` tasks need disjoint `Files touched`; missed-parallel advisory) — see it for the complete list.

**Pre-patch before dispatch (saves a NEEDS_REVISION round):** Before dispatching the reviewer, Read [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) and scan Check 1 and Check 3. If the plan is missing `Plan-document-reviewer verdict: PENDING` in the top-level header, or if any task is missing a `Brief item covered:` line, patch those fields now. These two omissions are the most common Check-1 / Check-3 failures; pre-patching costs one Read and saves one full round-trip.

If reviewer returns `NEEDS_REVISION`, writing-plans **fixes the plan** and re-runs the reviewer. Up to 2 rounds; if still NEEDS_REVISION after round 2, escalate to user (likely the brief itself needs revisiting).

**Amending a PASS plan:** If the plan is changed after the reviewer returned PASS (e.g., a task description is tightened, a dependency is updated), either (a) re-run the plan-document-reviewer on the amended plan, OR (b) record a one-line skip note in the plan's `Notes` section explaining why the amendment is additive and schema-safe (e.g., "amended Task 2 description for clarity; all required fields and DAG structure unchanged — re-review skipped"). A stale PASS without a skip note is a silent gap.

## Kickoff briefing

After PASS, before SDD handoff: run the kickoff briefing — read [`references/kickoff-briefing.md`](references/kickoff-briefing.md) and batch-brief the round's one-way-door decisions (expect 1-3); the rest route to the Decision Log.

## Output contract — the plan

Schema in [`references/plan-format.md`](references/plan-format.md). Plan lives at `docs/loom/plans/<date>-<topic>.md` (sibling to the brief). Minimum structure:

```markdown
# Plan: <topic>

Source brief: docs/loom/specs/<date>-<topic>.md
Total tasks: <N>   ← uncapped; width is fine (many parallel leaves OK)
Critical-path depth: <D> (≤5)   ← longest Dependencies chain; this is the ceiling
Execution order: sequential | parallel-where-possible
Plan-document-reviewer verdict: PENDING   ← required; reviewer will flip to PASS (timestamp)

## Task 1 — <short name>
- Description: <one-assertion unit of work, imperative voice>
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

**Worked micro-example** — two tasks, one `Independent: true` pair (disjoint files, no semantic dependency):

```markdown
## Task 1 — add slugify() helper
- Module: src/text/slug.py
- Files touched: src/text/slug.py, tests/test_slug.py
- Acceptance:
  - RED: tests/test_slug.py::test_slugify_lowercases_and_dashes fails (slugify undefined)
  - GREEN: slugify("Hello World") == "hello-world"
- Dependencies: none
- Independent: true
- Brief item covered: "URL slugs derived from titles"

## Task 2 — add truncate() helper
- Module: src/text/truncate.py
- Files touched: src/text/truncate.py, tests/test_truncate.py
- Acceptance:
  - RED: tests/test_truncate.py::test_truncate_adds_ellipsis fails (truncate undefined)
  - GREEN: truncate("abcdef", 3) == "abc…"
- Dependencies: none
- Independent: true
- Brief item covered: "preview text capped at N chars"
```

Both tasks touch disjoint files and share no symbol → both `Independent: true`, so `dispatching-parallel-agents` may dispatch them in one wave.

### Parallel-dispatch markup (v0.8.0+)

Two per-task fields signal eligibility for [`../dispatching-parallel-agents/SKILL.md`](../dispatching-parallel-agents/SKILL.md):

- **`Independent: true`** — the plan author's claim that this task has no shared symbol / no sequential data dependency with other `Independent: true` tasks. Default is `false`.
- **`Files touched: <paths>`** — the disjointness oracle. Two tasks are dispatch-parallel-safe **only when** both declare `Independent: true` AND their `Files touched` sets are disjoint.

If both conditions hold across N tasks, `dispatching-parallel-agents` MAY dispatch their implementers in one assistant message with N `Agent` calls. If either condition fails, SDD's sequential dispatch is the floor.

The markup is **opt-in**. A plan that omits it (or sets `Independent: false`) routes through SDD's standard sequential per-task triad. Claiming `Independent: true` with overlapping `Files touched` is a plan error — `plan-document-reviewer` should catch it; if not, `dispatching-parallel-agents` will refuse to dispatch.

## Consuming a loom-spec change-folder

Alongside the brainstorming brief, writing-plans can consume a **validated loom-spec change-folder** — `docs/loom/<change-id>/` emitted by `loom-spec:spec-expansion`. "Validated" means the change-folder is **`validate_spec_output.py`-clean** (the validator ran and exited 0). The change-folder's `specs/<capability>/spec.md` delta is the structure `validate_spec_output.py` enforces: `### Requirement:` blocks each containing one or more `#### Scenario:` (GIVEN / WHEN / THEN) acceptance criteria.

**Detecting which change-folder to consume.** A layered cascade, evaluated in order — stop at the first layer that resolves. Grounded in `docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md` §Resolved decisions (industry precedent: spec-kit, OpenSpec, Jira smart commits — every shipped answer shrinks the candidate pool structurally, none guesses from content).

**All detection layers anchor at the TARGET repo's root, not the ambient working directory.** Before evaluating layer (i) or layer (ii), resolve the target repo's root via `git rev-parse --show-toplevel` run **in the repo being planned for** — never in whatever directory the dispatch happened to start in. Branch name (layer i) and the `docs/loom/` folder count (layer ii) are both evaluated **against that resolved root**, not a relative guess from cwd. This mirrors `code-reviewer.md`'s D8 "Activation is self-derived" anchor pattern, which fixed the identical bug class (a relative check from cwd false-N/A's from a worktree or nested cwd — here it makes a weak operator run detection against the wrong repo entirely).

- **Layer 0 — explicit handoff wins.** If the caller (a conductor, an orchestrator, the user) hands writing-plans a change-folder path directly, bind to it immediately. Detection never runs — layers (i) and (ii) below exist only for when no path was named.
- **Layer (i) — branch-slug match, opportunistic only.** Exact match between the current branch name and a `docs/loom/<change-id>` slug. This layer is **opportunistic**, not authoritative: a miss falls through **silently** to layer (ii) — no error, no note. When this layer DOES decide the binding, **surface it explicitly** ("bound to `<change-id>` via branch name") — never bind silently. Any **ambiguity** (the branch name could plausibly match more than one folder) skips straight to the ask sub-step of layer (ii) below — never guess.
- **Layer (ii) — non-archived folder count.** List non-archived `docs/loom/<change-id>/` folders:
  - **0 → N/A, loudly.** State that no change-folder was found and proceed on the brainstorming-brief input instead — never a silent skip.
  - **1 → auto-bind, and state it.** Bind to the single folder and say so ("bound to `<change-id>`, the only non-archived change-folder found").
  - **>1 → ask**, listing candidates sorted by **recency** (most-recent first), with the most recent as the **recommended default** — never pick without asking.
  - **Never content-similarity.** No layer matches on spec-content similarity to the target repo — that guesswork is what every shipped precedent avoids.

**Mandatory once bound.** Once a change-folder is bound by any layer (including Layer 0), consuming it is **not optional** — writing-plans MUST derive the plan from it (scenario → task mapping below), not treat it as an FYI alongside a separately-authored brief.

**Wrong-bind reversal trigger.** If a real wrong-bind incident occurs (writing-plans bound to the wrong change-folder and produced a plan against it), layer (i) downgrades from opportunistic-auto to **confirm-before-use** — surface this to the user/orchestrator immediately rather than silently continuing to trust layer (i) unconfirmed.

**Who runs the validator.** In Continuous mode the FREEZE step already gated this change-folder — it ran `validate_spec_output.py` and got exit 0 — so writing-plans **trusts that exit-0** and does not re-run it. For a direct, non-freeze invocation (consuming a change-folder outside Continuous mode), run `validate_spec_output.py` once on the change-folder before consuming it, and proceed only on exit 0.

**Scenario → task mapping.** Map each `#### Scenario:` (its GIVEN / WHEN / THEN) → **one task's `Acceptance: RED/GREEN`**. The THEN is the GREEN observable; the GIVEN/WHEN set up the RED. One `### Requirement:` may **fan to N tasks** — split per §The splitting framework (a multi-Scenario Requirement is N candidate tasks, grouped by assertion boundary).

**Point-don't-copy / link back.** **NEVER** copy the spec body into the plan — loom-spec is SSOT, and a copied delta silently goes stale the moment loom-spec re-edits the change-folder, so the plan then drives implementers off a spec that no longer exists. Reference the source `### Requirement:` / `#### Scenario:` names via the stable join key `<change-id> / Requirement: <name> / Scenario: <name>` (the `Brief item covered:` field accepts this referent — see [`references/plan-format.md`](references/plan-format.md)). The plan **links back** to the spec; it does not duplicate it.

**Verbatim-copy carve-out (fact vs interpretation).** One exception to point-don't-copy: the THEN **observable**, **magic values**, and **signatures** are *facts* — copy them **verbatim** into the RED/GREEN assertion (a paraphrased magic value or signature is a defect). The surrounding **narrative** and **design rationale** are *interpretation* — link to them, do not copy. Facts in, prose linked.

**WHAT not WHERE — populate code-target fields by target-repo recon.** The change-folder supplies the **WHAT** (behavior / acceptance) but carries **no file / module / path info** — yet `references/plan-format.md` makes `Module` and `Files touched` (the parallelism disjointness oracle) required per task. Do **not** guess placeholder paths. Populate each task's `Module` / `Files touched` / `Context paths` by **reconnaissance of the TARGET repo** — grep / Read / Explore over the codebase the change lands in, the same Current-State-Evidence recon brainstorming does — seeded by the proposal's `## OOUX object model` (OOUX = the proposal's object/relationship model) where present (object → likely module / file). The spec names the behavior; the target repo tells you where it lives.

- **MODIFIED / REMOVED deltas.** When the spec carries a `## MODIFIED Requirements` or `## REMOVED Requirements` block (not just `## ADDED Requirements`), map them to change / removal tasks **plus the corresponding test update** — same `#### Scenario:` → RED/GREEN discipline (the RED is the failing test that encodes the changed / removed behavior; the GREEN is the updated test passing).

**Consumer read-only.** **NEVER edit the producer's change-folder** — loom-spec is SSOT, so a consumer edit makes sibling consumers read a different spec than the one the freeze validated, and races the freeze's `validate_spec_output.py` re-run. writing-plans reads `docs/loom/<change-id>/` and writes only its own plan at `docs/loom/plans/<date>-<topic>.md` (the canonical plan path from the §Output contract; for a change-folder input the `<change-id>` fills the `<topic>` slot).

**Coverage self-check (change-folder input only).** After producing the plan, run `python3 loom-code/scripts/check_scenario_coverage.py <change-folder> <plan>`. It compares the change-folder's `#### Scenario:` set against the plan's `Brief item covered` join keys. Exit 0 means every scenario maps to a task. **Exit 1 blocks the plan from PASS** — self-review may not declare PASS until either every scenario maps to a task, or the drop is **explicitly user-approved** and recorded in the plan's `Notes` section (name the dropped join key + the approval). This check applies only to the change-folder input path; a brainstorming-brief-only plan has no change-folder to check coverage against. **Gate order**: run this coverage check BEFORE dispatching the plan-document-reviewer — a coverage failure blocks the dispatch (a cheap deterministic script runs before an evaluator subagent, same economics as §Self-review's pre-patch habit; the two gates check different things — the reviewer's Check 3 verifies field presence per task, this script verifies full scenario coverage — so neither subsumes the other).

## Cross-skill contract

| Direction | Skill | Contract |
|---|---|---|
| **Upstream** | `brainstorming` | Produces brief at `docs/loom/specs/<topic>.md`. writing-plans reads it via Read tool. |
| **Upstream** | `loom-spec:spec-expansion` | Produces the validated change-folder consumed per §Consuming a loom-spec change-folder. |
| **Downstream** | `subagent-driven-development` | Consumes plan at `docs/loom/plans/<topic>.md`. SDD reads plan + dispatches per-task triad. |
| **Downstream (opt-in)** | `dispatching-parallel-agents` | Consumes tasks marked `Independent: true` with disjoint `Files touched`. Dispatches their implementers in one assistant message for concurrent execution. Fall back to SDD's sequential dispatch if either condition fails. |
| **Self-review** | `plan-document-reviewer` (evaluator subagent) | writing-plans dispatches it after producing the plan. Returns PASS / NEEDS_REVISION. |
| **Recursive (BLOCKED fallback)** | `writing-plans` (self) | When SDD's implementer returns BLOCKED with decomposition signal, orchestrator re-invokes this skill on the failing task. |
| **Optional delegation** | `dev-workflow:complexity-critique` | If the plan produces >3 tasks and you suspect Axis 3 (smallest end state) was too generous, optionally invoke complexity-critique before falling back to brainstorming. |

Delegation contract per CLAUDE.md: pass **paths + structured seed context**, not file content. The target skill loads its own resources via Read.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Just skip planning, the brief is enough."* | The brief is the *what*; the plan is the *how-cut-into-atomic-pieces*. SDD needs atomicity, not just scope. | Refuse. Produce the plan even if it's only 1-2 tasks. If 1 task, the brief was an exemption candidate (§When NOT to Use). |
| *"This task is roughly an hour but I don't know how to split it."* | "I don't know how to split" is a discovery failure, not a planning failure. The brief did not articulate Axis 3 (smallest end state) tightly enough. | Surface back to brainstorming for Axis 3 re-cut, do not produce a 1-hour task that resolves to a single assertion and calls itself done — split by criterion 1 (one failing test), not by the clock. |
| *"This chain is 8 tasks deep, that's fine."* | No — see §Plan size ceiling. Critical-path depth >5 = brief too big. (A wide-but-shallow 8-task plan is fine; a deep 8-link chain is not.) | Refuse the deep chain. Route back to brainstorming OR split into N briefs each with depth ≤5. |
| *"Skip the plan-document-reviewer, it's overkill."* | The reviewer catches the failure modes the splitting framework misses (orphan tasks, cycle dependencies, brief-task coverage gaps). | Refuse. Self-review is non-negotiable. If you genuinely produced a perfect plan, the reviewer takes 30 seconds to confirm. |
| *"Implementer returned BLOCKED, just retry."* | Beck Child Test pattern says split smaller, not retry. Silent retry burns SDD's 3-round cap. | Re-invoke writing-plans on the failing task per §BLOCKED fallback. |
| *"This task depends on Task 1, Task 3, AND a thing not in the plan."* | The "thing not in the plan" is a missing task. Declare it. | Add the missing task to the plan. Re-run plan-document-reviewer. |
| 「先跳過 plan 直接派 SDD 吧 / プランは飛ばして」 | Same rationalization, localized. | Same refusal — produce the plan. |

## What this skill does NOT do

- Does **not** write code. Atomic-task production is metadata about future work, not the work.
- Does **not** dispatch SDD subagents. That's SDD's job. writing-plans hands off the plan; SDD picks it up.
- Does **not** invoke the implementer / spec-reviewer / code-quality-reviewer prompts directly. Only plan-document-reviewer (a different evaluator scope).
- Does **not** estimate dev-time at all. The split-trigger is criterion 1 (one failing test) — see §The splitting framework, and §No time-box criterion for why a completion-time estimate isn't part of the schema.
- Does **not** decide priority or sequencing beyond what the dependency graph requires. The user (or SDD) decides which independent tasks run first.

## See also

- [`references/plan-format.md`](references/plan-format.md) — full plan schema.
- [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) — evaluator subagent prompt.
- [`../brainstorming/SKILL.md`](../brainstorming/SKILL.md) — upstream brief producer.
- [`../brainstorming/references/handoff-brief-format.md`](../brainstorming/references/handoff-brief-format.md) — input contract.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — downstream plan consumer.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — discipline that fires inside each implementer subagent.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 2 (Planning).
