---
name: writing-plans
description: |
  Use AFTER brainstorming produces a brief, BEFORE subagent-driven-development dispatches implementers. Splits it into atomic tasks — each with one RED/GREEN test and a single module boundary — into a dependency graph.
version: 0.12.2
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / plan-document-reviewer — the last is a prompt-file role, not a registered agent type; see §Self-review), the parent orchestrator already finished planning. **Do not** re-route through this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Turns a `brainstorming` brief or validated `loom-design` change-folder into a reviewed plan for `subagent-driven-development` (SDD). Each task must be:

- **Independently verifiable** — one RED test or diagnostic goes GREEN when done.
- **One module** of touch surface (consistent with SDD's per-task scope).

The plan is a **paths-not-content handoff**; review it before DONE.

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

**runnable capability note.** For a new test/build/lint/e2e/migration or similar verb, `Acceptance` must require both declaration in the command surface (`AGENTS.md`, `make`/`just`, or `package.json`) and a successful run.

**No time-box criterion.** Never size by duration; re-check the assertion and module boundary.

**Post-split parallel-marking pass.** At the **same dependency level**, mark both tasks `Independent: true` only when `Files touched` are disjoint and no semantic dependency exists.

**Guard — disjoint files ≠ independent.** Shared data/symbols, doc-mirrors-code, or producer/consumer relationships remain sequential. Declare every semantic edge in `Dependencies`, keep `Independent: false`, and describe its contract in `Seam` (`payload: none` when nothing crosses); see [`references/plan-format.md`](references/plan-format.md) `#### Seam`.

## Plan size ceiling — critical-path depth ≤5

Critical-path depth is the longest `Dependencies` chain. Parallel tasks at one level count once; total task count is irrelevant.

**No hard width cap.** Mark eligible tasks `Independent: true`; only **depth >5** triggers a hard split.

If the critical-path **depth** exceeds 5, the brief is too big. **Do not silently produce a deep chain.** Two options:

1. **Route back to brainstorming**: the Smallest End State (Axis 3) was not actually smallest — it baked in a long sequential dependency chain. Surface this and ask the user to re-cut.
2. **Split into multiple sequential briefs**: if the work genuinely needs a chain deeper than 5 and the user agrees, write *N* separate brief files (each with depth ≤5), explicitly labeled `<topic>-part-{1..N}.md`. Each brief is a standalone input to its own `writing-plans` run and its own SDD run. **Split = N brief files, not N plans from one brief.** A plan is 1-to-1 with one brief — `## Part 1 / ## Part 2` sections inside a single plan file are not valid splitting.

For an initial depth>5 brief, the two options are a closed list: there is no depth-limit exception, structural-split escape hatch, or “record the risk and continue” path.

Deep chains reveal discovery failure; wide plans are valid.

**Why depth `5` is a heuristic, not a law** — the compounding-error rationale and worked example: [`references/design-evidence.md`](references/design-evidence.md).

**Structural-split escape hatch (round-2 NEEDS_REVISION only):** If the plan-document-reviewer returns NEEDS_REVISION for a second round and the *sole* failure is a structural-size violation (a task structurally cannot resolve to one failing test within one module boundary — Check 6 keeps failing no matter how the description is reworded — and cannot be shrunk further without a brief change), split that oversized task into a fresh sibling part (a new `<topic>-part-N.md` brief → new plan) and treat it as a round-1 input to a fresh `writing-plans` run. The original plan's 2-round cap applies to the original tasks only; the new sibling part starts its own clean round count.

## BLOCKED fallback — Beck 2002 Child Test pattern

When SDD dispatches an implementer subagent and the implementer returns `BLOCKED` with `unblock_step: "this task needs to be split smaller"`, the orchestrator re-invokes writing-plans on the failing task. writing-plans then:

1. Reads the failing task description + the implementer's `unblock_step`.
2. Applies the splitting framework to produce **child tasks** that ladder up to the original.
3. The original task becomes a "parent" — when all children are DONE, the parent is DONE.
4. Self-reviews the child decomposition via plan-document-reviewer.
5. Returns the child plan to SDD.

This is Beck's Child Test pattern: split an oversized test into smaller green steps, then retry the parent; evidence: [`references/design-evidence.md`](references/design-evidence.md).

**Anti-pattern**: never retry the same decomposition BLOCKED task unchanged; re-invoke writing-plans.

## Self-review — plan-document-reviewer

`plan-document-reviewer` is a **PROMPT FILE** ([prompt](references/plan-document-reviewer-prompt.md)) dispatched via a generic subagent — NEVER an agent-registry lookup; no other reviewer agent (docs-reviewer included) may substitute. Tier: profile.

**Resolve the dispatch profile** in [`dispatch-profile.md`](../using-loom-code/references/dispatch-profile.md) before spawn; it owns translation and escalation.

Dispatch [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) as an evaluator in a one-shot blocking call. Its checklist is authoritative; host details are in the tool mapping and Claude's naming pitfall in [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §A1. Pre-screen:

- **one-failing-test acceptance** — each task names a specific RED test (criterion 1, primary);
- **every brief item covered** — every Smallest End State / Decision item maps to ≥1 task, no orphan tasks;
- **DAG, no cycles** — `Dependencies` form an acyclic graph with critical-path depth ≤5.

The prompt also enforces parallel-dispatch checks — see it for the complete list.

**Pre-patch before dispatch:** Read reviewer Checks 1 and 3; add missing top-level `Plan-document-reviewer verdict: PENDING` and per-task `Brief item covered:` fields.

**Coverage gate:** before dispatching the reviewer, run §Consuming a loom-design change-folder — Coverage self-check; brief mode (`--brief`) applies to every brief declaring `BI-` ids.

**Open-questions gate (unconditional):** on every plan run `python3 loom-code/scripts/check_open_questions.py <plan-path>` before review. A non-zero exit blocks the plan from PASS; fix and rerun.

**On-ramp choice gate (unconditional, intake):** before Task 1 run `python3 loom-code/scripts/check_onramp_choice.py <brief-path>`. Exit 2 → STOP: do not draft; relay the printed question to the user, wait, update the brief's `## Design-side on-ramp` line, re-run. Exit 1 → STOP (brief missing). `git-guard.py` repeats this at commit; grammar: [`../brainstorming/references/handoff-brief-format.md`](../brainstorming/references/handoff-brief-format.md).

**Queue-relation gate (unconditional):** at intake, before drafting Task 1, run `python3 loom-code/scripts/check_queue_relation.py <brief-path>`. Exit 0 resolves `unqueued` unconditionally, resolves `in-queue`/`displaces` with a matching live bet, or reports N/A when the store is absent. Exit 1 means the brief path was not found (fix the path), the brief/store is unreadable (NOT the store-absent case; fix permissions), or an entry status is outside the closed vocabulary (fix its frontmatter), then re-run. Exit 2 means unresolved: STOP, do not draft, relay the printed question, wait, write it into the brief's `## Queue relation`, and re-run. Grammar: [`../brainstorming/references/handoff-brief-format.md`](../brainstorming/references/handoff-brief-format.md).

**Field-microstructure gate (unconditional):** brief mode fires at intake, before drafting Task 1: run `python3 loom-code/scripts/check_field_microstructure.py --brief <brief-path>`; a non-zero exit blocks drafting. Before review run `python3 loom-code/scripts/check_field_microstructure.py <plan-path>`; a non-zero exit blocks the plan-document-reviewer dispatch. Exit 1: fix the flagged field or paragraph, re-run. Exit 2: structurally empty (no `## Task` headings, or no `## ` sections) — supply the missing structure, not a field fix.

**Seam-coverage gate (unconditional):** before review run `python3 loom-code/scripts/check_seam_coverage.py <plan-path>`; non-zero blocks. Fix and rerun; the script owns seam-edge coverage.

If reviewer returns `NEEDS_REVISION`, writing-plans **fixes the plan** and re-runs the reviewer. Before that re-dispatch, re-run the **Pre-patch before dispatch** self-screen on the revision delta itself — every line the fix added or changed — because three consecutive arcs' round-2 findings were defects the round-2 revision itself introduced. Up to 2 rounds; if still NEEDS_REVISION after round 2, escalate to user (likely the brief itself needs revisiting).

**Amending a PASS plan:** After PASS, any change re-reviews unless it is one of these three kinds — a **closed list**; an amendment that does not clearly match one of the three is outside the list:

1. **Stamping the verdict** — writing the reviewer's already-returned verdict, round, or timestamp into the header (`PENDING` → `PASS (2026-07-27, round 3)`). No technical content changes.
2. **Fixing a typo** — spelling, punctuation, or formatting (a mis-rendered heading, a stray character), with no change to what any field asserts.
3. **Filling a schema field** — writing a required-but-blank field (an empty `Brief item covered:`) with text **byte-identical** to wording already in the brief, the loom-design change-folder, or the plan — a verbatim copy of a quote, citation, or join key, never a paraphrase or any wording the author composed.

Anything else re-reviews — in particular a change to a task's Acceptance RED or GREEN, to a cited fact (a `file:line`, a number, a claim about existing behaviour), to a Dependencies edge, or to a task's scope (Description, Module, Files touched).

A qualifying amendment records a one-line skip note in the plan's `Notes` naming which kind (e.g. "Task 2's `Brief item covered` filled — filling a schema field, no re-review"). A stale PASS without a skip note is a silent gap.

## Kickoff briefing

After PASS and before SDD, kickoff is mandatory even for a small or obvious plan. Never skip it. Follow [`references/kickoff-briefing.md`](references/kickoff-briefing.md): batch-brief 1–3 one-way-door decisions and forks; route others to the Decision Log. Show the plan through [`adjudication-view`](../using-loom-code/protocols/adjudication-view.md) doc mode per its firing conditions.

**Progress surface.** From birth, the plan carries `Goal:`, `Stage:`, per-task `Status:`, an optional `Steps:` title block, and per-task `Gloss:` lines. Steps titles and Gloss lines are written at plan time in the user's conversation language per §Language policy. After PASS, run repo-root `scripts/plan_card.py` as `python3 scripts/plan_card.py <plan-path>`,
otherwise `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" <plan-path>`. Relay it — fire-and-continue, not a new pause — per `loom-code/hooks/family-relay.md §(a2) Progress card`; if family-relay or both scripts are absent, render the four fields inline: goal, task table, stage, next. Apply [`../using-loom-code/protocols/adjudication-view.md`](../using-loom-code/protocols/adjudication-view.md) doc mode per its firing conditions.

## Language policy

The plan document is written in two layers, split by field. Task
**Description** bodies and **Acceptance** (RED/GREEN) are written in
English — the machine-checkable contract implementers and reviewers
read. **Steps** titles, **Gloss**, **Goal**, task titles, and
**Notes** stay in the session's conversation language — the
human-facing surface the user reads. For careful reading of the
English precision content in zh-Hant/ja, produce the plan's document
view per the adjudication-view protocol's own firing conditions (doc
mode) — see
[`../using-loom-code/protocols/adjudication-view.md`](../using-loom-code/protocols/adjudication-view.md).

## Output contract — the plan

Schema in [`references/plan-format.md`](references/plan-format.md). Plan lives at `docs/loom/plans/<date>-<topic>.md` (sibling to the brief). Minimum structure:

```markdown
# Plan: <topic>

Source brief: docs/loom/specs/<date>-<topic>.md
Goal: <one sentence transcribed from the brief's Smallest End State at
    plan time — frozen with the plan; never edited afterward>
Stage: planning   ← at emit; enum planning | sdd:wave-N | review:round-N |
    blocked:user-decision | finishing — orchestrator updates it at each
    transition
Total tasks: <N>   ← uncapped
Critical-path depth: <D> (≤5)   ← longest Dependencies chain; this is the ceiling
Execution order: sequential | parallel-where-possible
Plan-document-reviewer verdict: PENDING   ← required; reviewer will flip to PASS (timestamp)

## Task-flow diagram

<!-- mermaid flowchart LR of the task dependency DAG (or the pinned N/A line) -->

## Open Questions

N/A — no unresolved question: <one-line reason>

## Task 1 — <short name>
- Description: <imperative voice, first line only — overflow routes to a nested bullet or table per §Field-value grammar>
- Module: <path or module name; one only>
- Files touched: <comma-separated paths the implementer will Write / Edit>
- Context paths:
  - <path to existing code the implementer reads>
- Acceptance:
  - RED: <failing test name / diagnostic>
  - GREEN: <observable condition when done>
- External surfaces: <required when the task touches a non-stdlib external surface —
    five categories + stdlib-preference rule in `references/plan-format.md` §External surfaces.
    Omit if pure internal logic. Per-task field, not a Notes catch-all.>
- Dependencies: <"none" | "Task N completes first" | "Tasks N, M complete first" |
    "Tasks N, M parallel" — semantics in `references/plan-format.md`; cross-part ordering
    uses "none" + a plan-level Notes entry (the field is within-plan only).>
- Seam: <required when Dependencies ≠ "none"; grammar: `references/plan-format.md` §Seam>
- Independent: <true | false>  # opt-in marker for dispatching-parallel-agents
- Brief item covered: <quote or close paraphrase from brief's Smallest End State /
    Decision section — required; plan-document-reviewer Check 3 blocks on this field>
- Status: pending   ← default-on ledger field; SDD maintains it —
    semantics in `references/plan-format.md` §Progress ledger
- Gloss: <one line, user's conversation language — effect + goal relation>

## Task 2 — ...
```

Worked examples — including an `Independent: true` pair (disjoint files, no semantic dependency) and a wide-but-shallow 8-task depth-2 plan — live in [`references/plan-format.md`](references/plan-format.md) §Worked example.

### Parallel-dispatch markup (v0.8.0+)

Two per-task fields — `Independent` and `Files touched` — signal parallel-dispatch eligibility for [`../dispatching-parallel-agents/SKILL.md`](../dispatching-parallel-agents/SKILL.md); full field semantics and the gating rule live in [`references/plan-format.md`](references/plan-format.md) §`Files touched` and `Independent`; the overlapping-`Files touched` plan error lives in that file's §Anti-patterns.

## Consuming a loom-design change-folder

Writing-plans consumes `docs/loom/<change-id>/` emitted by `loom-design:spec-expansion`. Validated means `validate_spec_output.py` exited 0 on its `specs/<capability>/spec.md` `### Requirement:` blocks and `#### Scenario:` criteria.

**Detecting which change-folder to consume.** Evaluate layers in order; stop on resolution. Evidence: `docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md` and [`references/design-evidence.md`](references/design-evidence.md).

First resolve the target repo's root: run `git rev-parse --show-toplevel` there. Anchor all layers at that TARGET repo's root, never ambient cwd.

- **Layer 0 — explicit handoff wins.** If the caller (a conductor, an orchestrator, the user) hands writing-plans a change-folder path directly, bind to it immediately. Detection never runs — layers (i) and (ii) below exist only for when no path was named.
- **Layer (i) — branch-slug match, opportunistic only.** Exact branch/`docs/loom/<change-id>` match binds and must be announced. A miss silently falls through; ambiguity goes to layer (ii)'s ask—never guess.
- **Layer (ii) — non-archived folder count.** List non-archived `docs/loom/<change-id>/` folders:
  - **0 → N/A, loudly.** State that no change-folder was found and proceed on the brainstorming-brief input instead — never a silent skip.
  - **1 → auto-bind, and state it.** Bind to the single folder and say so ("bound to `<change-id>`, the only non-archived change-folder found").
  - **>1 → ask**, listing candidates sorted by **recency** (most-recent first), with the most recent as the **recommended default** — never pick without asking.
  - **Never content-similarity.** No layer matches on spec-content similarity to the target repo — that guesswork is what every shipped precedent avoids.

**Mandatory once bound.** Once a change-folder is bound by any layer (including Layer 0), consuming it is **not optional** — writing-plans MUST derive the plan from it (scenario → task mapping below), not treat it as an FYI alongside a separately-authored brief.

**Wrong-bind reversal trigger.** A confirmed wrong-bind incident is surfaced immediately and downgrades layer (i) to confirm-before-use — restore the full protocol from git history.

**Who runs the validator.** In Continuous mode the FREEZE step already gated this change-folder — it ran `validate_spec_output.py` and got exit 0 — so writing-plans **trusts that exit-0** and does not re-run it. For a direct, non-freeze invocation (consuming a change-folder outside Continuous mode), run `validate_spec_output.py` once on the change-folder before consuming it, and proceed only on exit 0.

**Structural-clean is not enough — the critic verdict gate.** `validate_spec_output.py` exit 0 only proves the change-folder is **structurally clean** (schema-valid `### Requirement:` / `#### Scenario:` shape). It says nothing about whether `loom-design:completeness-critic` actually reviewed and approved this content — **structural-clean ≠ critic-fresh-and-passed**, two different gates, neither subsumes the other. Additionally invoke that public skill's verdict-validation command ([source](https://github.com/kouko/monkey-skills/blob/main/loom-design/scripts/spec/mint_critic_verdict.py)); resolve it through the installed skill, never a sibling layout:

```
<verdict-validation command from loom-design:completeness-critic> validate --change-folder <path> --critic completeness-critic --files proposal.md,specs/<capability>/spec.md
```

The `--files` list must be **concrete file paths**, not a directory or a placeholder — `mint_critic_verdict.py` resolves each entry with `Path.read_bytes()` (files only; a directory or a literal `...` raises `OSError`, which surfaces as an unreadable-file exit 4, easily misread as staleness). Point-don't-copy applies here too: don't copy the example verbatim — enumerate the change-folder's **actual** covered spec files (e.g. `proposal.md,specs/<capability>/spec.md`), and this list must **match** the list `completeness-critic` minted — `mint_critic_verdict.py` records that list at mint time and compares it at validate time.

Proceed only on **exit 0** (fresh `PASS_WITH_NOTES`). Route on the non-zero exits, same reporting discipline as the structural validator above:

- **Exit 2 (no verdict file, completeness-critic never ran)** — route TO `completeness-critic`: dispatch it against the change-folder before proceeding.
- **Exit 3 (fresh verdict is NEEDS_REVISION, critic blocked)** — route BACK to the spec-expansion writer: the critic already found problems writing-plans cannot resolve itself.
- **Exit 4 (three distinct causes, same remediation)** — a `--files` list that diverges from what was recorded at mint, a covered file edited since mint (stale), or a covered file that's unreadable since mint — re-run `completeness-critic` so it reviews the current bytes before writing-plans trusts the verdict again.

**Task-shape and code-target detail** (scenario → task mapping, point-don't-copy, verbatim-copy carve-out, target-repo recon, MODIFIED/REMOVED deltas). Map each `#### Scenario:` to one task's `Acceptance: RED/GREEN` — never copy the spec body into the plan, link via the join key `<change-id> / Requirement: <name> / Scenario: <name>` (id-mode: `<change-id> / REQ-<n> / Scenario: <name>`); THEN observables / magic values / signatures are facts, copied verbatim, narrative and rationale are interpretation, linked not copied; populate `Module` / `Files touched` / `Context paths` by reconnaissance of the TARGET repo, seeded by the proposal's `OOUX` object model where present; `MODIFIED` / `REMOVED` requirement deltas map to change/removal tasks plus a test update, same discipline. Full detail in [`references/consuming-a-change-folder.md`](references/consuming-a-change-folder.md).

**Consumer read-only.** **NEVER edit the producer's change-folder** — loom-design is SSOT, so a consumer edit makes sibling consumers read a different spec than the one the freeze validated, and races the freeze's `validate_spec_output.py` re-run. writing-plans reads `docs/loom/<change-id>/` and writes only its own plan at `docs/loom/plans/<date>-<topic>.md` (the canonical plan path from the §Output contract; for a change-folder input the `<change-id>` fills the `<topic>` slot).

**Coverage self-check.** After producing the plan, run `python3 loom-code/scripts/check_scenario_coverage.py <change-folder> <plan>`. It compares the change-folder's `#### Scenario:` set against the plan's `Brief item covered` join keys. Exit 0 means every scenario maps to a task. **Exit 1 blocks the plan from PASS** — self-review may not declare PASS until either every scenario maps to a task, or the drop is **explicitly user-approved** and recorded in the plan's `Notes` section (name the dropped join key + the approval). An undeclared bare `REQ-<n>` citation also exits 1, with no approval path — fix the citation. When the source brief declares `BI-` ids, the same script runs in **brief mode** — `python3 loom-code/scripts/check_scenario_coverage.py --brief <brief> <plan>` — before the plan-document-reviewer dispatch, blocking on an unresolvable citation; an uncovered id only warns. **Gate order**: run this coverage check BEFORE dispatching the plan-document-reviewer — a coverage failure blocks the dispatch (same cheap-script-before-evaluator economics as §Self-review's pre-patch habit). The two gates differ: the reviewer's Check 3 verifies field presence per task; this script verifies full scenario coverage — neither subsumes the other.

Cross-skill delegation (upstream / downstream / self-review / recursive contracts) passes paths + structured seed context per CLAUDE.md, never file content — full table: [`references/cross-skill-map.md`](references/cross-skill-map.md).

## Red Flags — refuse these rationalizations

Planning-skip shortcuts to refuse — *"just skip planning, the brief is enough," "this chain is 8 tasks deep, that's fine," "skip the plan-document-reviewer, it's overkill," "implementer returned BLOCKED, just retry"* (and localized 「先跳過 plan 直接派 SDD 吧 / プランは飛ばして」). Default posture: refuse the silent skip; produce the plan — even a 1-2 task plan beats no plan, and self-review costs 30 seconds against a discovery failure it would otherwise miss. Full table (rationalization → reality → correct response) in [`references/red-flags.md`](references/red-flags.md).

What this skill does NOT do (write code, dispatch SDD subagents, invoke implementer/reviewer prompts directly, estimate dev-time, or decide task priority) — full list: [`references/cross-skill-map.md`](references/cross-skill-map.md) §What this skill does NOT do.

## Links

- [`references/plan-format.md`](references/plan-format.md) — schema.
- [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) — reviewer.
- [`references/consuming-a-change-folder.md`](references/consuming-a-change-folder.md) — change-folder details.
- [`../brainstorming/SKILL.md`](../brainstorming/SKILL.md) — upstream brief producer.
- [`../brainstorming/references/handoff-brief-format.md`](../brainstorming/references/handoff-brief-format.md) — input contract.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — downstream plan consumer.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — discipline that fires inside each implementer subagent.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 2 (Planning).
