# Brief: loom-code skill text compaction

Date: 2026-08-26
Parent brief: docs/loom/specs/2026-08-25-loom-skill-text-compaction.md
Status: FROZEN — the design-family compaction established the method; this part applies it to the 13 remaining loom-code entrypoints.

## Design-side on-ramp

not fired — this is a behavior-preserving refactor of existing code-workflow contracts with regression coverage

## Problem

The 13 remaining loom-code entrypoints repeat examples, rationale, routing explanations, schemas, and delegated detail that do not all belong in the default load. Together they contain 33,409 words, so weak models spend substantial context before reaching the trigger, refusal, stage boundary, execution order, review gate, and stopping rule.

## Users

- Claude Code and Codex users who need unchanged coding-workflow decisions after the entrypoints become shorter.
- Loom maintainers who need per-skill essence oracles and exact word ranges rather than subjective prose review.
- Reviewers who need weak-model evidence for activation, routing, refusal, tools, user gates, side effects, and stopping behavior.

## Smallest End State

Before any refactor, every target skill has a same-directory `test-prompts.json` with at least three genuine prompts spanning happy-path, edge-case, and stress behavior. An independent preflight freezes the 13 current word counts, invariant snapshots, and dual-host weak-model baseline outputs. No round may modify a skill's `SKILL.md` and any bundled file together.

All 13 remaining loom-code `SKILL.md` entrypoints are then 20–30% shorter while retaining every always-needed behavior inline. Each skill receives a RED-first static essence and word-range test, valid references, focused and package tests, a privacy gate, an atomic commit, and immutable-input specification and quality reviews. The family then passes two baseline/candidate replicates per skill on Claude Code `haiku` and Codex `gpt-5.6-luna`, with stronger adjudication restricted to replicated surviving `INCONCLUSIVE` results.

- BI-0 — Before refactoring, validate the existing requesting-code-review and writing-plans corpora; create the other 11 same-directory `test-prompts.json` files with at least one happy-path, edge-case, and stress prompt; capture 13-skill `wc -w`, invariant snapshots, immutable baseline roots, and two baseline outputs per host and skill. Record that the user already acknowledged genuine prompts plus weak-model equivalence testing.
- BI-1 — Compact brainstorming while preserving subagent stop, hard gate and exemptions, Axis 0 reception/backlog/on-ramp behavior, Axes 1–5, one-axis questioning, research-grounded alternatives, brief schema and checks, sign-off, delegation, and visual/state boundaries.
- BI-2 — Compact dispatching-parallel-agents while preserving independence criteria, one-domain-per-agent prompts, one-message fan-out, TDD per branch, aggregation and integration verification, plan markup, concurrent-session worktrees, and shared-root-cause refusal.
- BI-3 — Compact finishing-a-development-branch while preserving trigger authorization, review/docs routing, verification and conditional UI gate, memory timing, privacy and attached-HEAD guards, explicit staging, commit-carrier and final-HEAD markers, branch-qualified push, PR/CI repair limits, no auto-merge, cleanup ask, archive/backlog/purpose checks, and close-out report.
- BI-4 — Compact loom-memory while preserving its conditional N/A-loud gate, charter-as-SSOT rule, record classification and contradiction handling, generated index and integrity checks, pull-based recall and freshness check, exhaustive prune verdicts, and approval-only deletion.
- BI-5 — Compact requesting-code-review while preserving live-gate receipt, triggers and exemptions, contract/record classification, push-as-trigger close-out routing, immutable review context and refusal, four-way file routing, docs-arm tier rule, two-reviewer code panel, grounded aggregation, stage/marker behavior, and user relay rules.
- BI-6 — Compact requesting-docs-review while preserving DOCS live receipt, docs-only and mixed-arm scope, mechanical exemptions, immutable scope pass-down, citation pre-pass, two-reviewer whole-artifact review across five dimensions, blocking-class aggregation, one full round plus one delta confirmation, append-only evidence correction, marker ownership, and STOP behavior.
- BI-7 — Compact systematic-debugging while preserving its reproduce-first gate and exemptions, the REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY sequence, one-variable experiments, evidence logging, root-cause-before-fix rule, TDD handoff, bounded escalation, and special lanes for intermittent, environment, and slow failures.
- BI-8 — Compact tdd-iron-law while preserving subagent behavior, iron law and enumerated exemptions, RED → GREEN → REFACTOR order, false-green diagnostic, test-quality requirements, legacy characterization, agent reporting, and refusal of test-after or production-first rationalizations.
- BI-9 — Compact ui-verification while preserving its UI-touch plus `ui-flows.md` conditional gate and N/A outcomes, real-app state coverage, tool-resolution order and degradation ladder, evidence capture, blocking failures, bounded repair, verdict format, and separation from package tests.
- BI-10 — Compact using-git-worktrees while preserving when worktrees do and do not apply, shared-git implications, `.worktrees/` ignore safety, branch/path collision checks, creation and removal commands, concurrent-session isolation, cleanup confirmation, and no-stash/no-clone boundaries.
- BI-11 — Compact using-loom-code while preserving parent-only routing, five load-bearing rules, instruction priority, host mapping, ordered stage table and auxiliary skills, independent-task suggestion, approved-scope autonomy with mandatory continuous-mode load, safety stops and no auto-merge, coexistence, and conditional reference loading.
- BI-12 — Compact verification-before-completion while preserving the package-level hard gate and exemptions, declared-first command resolution, project-root execution, nonzero-test/output inspection, failure routing, evidence verdict, final-HEAD marker minting, stale-evidence rule, plain relay, and UI/quality boundaries.
- BI-13 — Compact writing-plans while preserving upstream eligibility, three-part atomic splitting, depth ceiling, BLOCKED child-test fallback, all intake and self-review gates, reviewer retry/amendment rules, kickoff/progress surface, bilingual field policy, complete plan schema, change-folder binding and critic freshness, scenario/brief coverage, and consumer read-only behavior.
- BI-14 — Record per-skill and aggregate size deltas plus static, focused, package, reference, privacy, review, Claude, Codex, replicate, raw-evidence, and adjudication results with no confirmed regression or unexplained side effect.

## Current State Evidence

- **Data** — current `wc -w` baselines and exact allowed ranges are: brainstorming 3,645 → 2,552–2,916; dispatching-parallel-agents 1,827 → 1,279–1,461; finishing-a-development-branch 4,470 → 3,129–3,576; loom-memory 1,058 → 741–846; requesting-code-review 4,496 → 3,148–3,596; requesting-docs-review 4,063 → 2,845–3,250; systematic-debugging 2,200 → 1,540–1,760; tdd-iron-law 1,833 → 1,284–1,466; ui-verification 1,196 → 838–956; using-git-worktrees 1,298 → 909–1,038; using-loom-code 1,671 → 1,170–1,336; verification-before-completion 1,154 → 808–923; writing-plans 4,498 → 3,149–3,598. The 13-skill baseline total is 33,409 words.
- **Forward** — `loom-code/scripts/loom_firing_harness.py` provides dual-host baseline/candidate comparison, pinned models, retained raw JSONL, and replicate control; the prior family parts validated this runner.
- **Forward** — `loom-code/skills/requesting-code-review/test-prompts.json` and `loom-code/skills/writing-plans/test-prompts.json` each already contain four genuine prompts covering happy, edge, and stress behavior; the other 11 target directories currently have no `test-prompts.json`.
- **Forward** — the existing `loom-code/scripts/test_*.py` suite pins routing, live-gate, plan, review, verification, memory, UI, close-out, and cross-reference behavior that each focused task must preserve.
- **Reverse** — the 13 current `SKILL.md` files are the behavioral sources under test; `subagent-driven-development` is excluded from compaction because its completed compaction test and candidate are fixed family context.
- **Error** — static pins prove required contract text remains but cannot prove a weak model still activates, refuses, routes, asks, writes, verifies, or stops at the same point.
- **Boundary** — no new or expanded reference file may receive removed prose. The target is true deletion from `SKILL.md`, not default-load relocation; any incidental reference delta is reported and cannot count toward the reduction.
- **Evidence paths**:
  - `loom-code/skills/brainstorming/SKILL.md` — hard gate, axes, brief, and delegation contracts
  - `loom-code/skills/dispatching-parallel-agents/SKILL.md` — independence, fan-out, aggregation, and worktree contracts
  - `loom-code/skills/finishing-a-development-branch/SKILL.md` — delegated close-out, safety, PR, CI, and reporting contracts
  - `loom-code/skills/loom-memory/SKILL.md` — conditional store verbs and charter boundary
  - `loom-code/skills/requesting-code-review/SKILL.md` — scope, routing, panel, aggregation, and publish gate
  - `loom-code/skills/requesting-docs-review/SKILL.md` — whole-artifact review and bounded confirmation
  - `loom-code/skills/systematic-debugging/SKILL.md` — four-phase evidence loop
  - `loom-code/skills/tdd-iron-law/SKILL.md` — RED/GREEN/REFACTOR and false-green rules
  - `loom-code/skills/ui-verification/SKILL.md` — conditional UI state verification
  - `loom-code/skills/using-git-worktrees/SKILL.md` — safe parallel checkout lifecycle
  - `loom-code/skills/using-loom-code/SKILL.md` — router stages, autonomy, and boundaries
  - `loom-code/skills/verification-before-completion/SKILL.md` — package-level proof and marker
  - `loom-code/skills/writing-plans/SKILL.md` — atomic plan, gates, schema, and change-folder consumption

## Alternatives Considered

| Alternative | Evidence | Why rejected |
|---|---|---|
| Apply one final word ceiling to every skill | Baselines range from 1,058 to 4,498 words and operative density differs | A fixed ceiling would over-compress dense orchestrators and under-challenge smaller skills. |
| Move detailed contracts into references | The user fixed a no-extraction method for this family round | Relocation can preserve total complexity while making the apparent entrypoint delta look better. |
| Depend only on existing package tests | Existing tests pin many fragments but were not designed as per-skill compaction oracles | They do not jointly assert each entrypoint's essence and bounded word range. |
| Use per-skill 20–30% deletion plus dual-host replay | The design-family plan and completed SDD compaction established this method | Chosen: it combines a measurable reduction with observable behavior as the release gate. |

## Decision

Run an independent preflight before any refactor. Validate the two existing prompt corpora and author the other 11 same-directory `test-prompts.json` files, each with at least three genuine prompts spanning happy-path, edge-case, and stress behavior. Using immutable full-plugin baseline input, capture two Claude Code `haiku` and two Codex `gpt-5.6-luna` outputs per target skill, raw evidence paths, frozen `wc -w` counts, and an invariant snapshot tied to each prompt's expected behavior. The user previously acknowledged this genuine-prompt and weak-model equivalence method.

Then implement 13 RED-first tasks in ledger order, one per remaining skill. Each depends on the completed preflight. First add the named static test and demonstrate that the untouched file fails only its word ceiling; then compact only that skill's `SKILL.md`, deleting repetition without adding or expanding references. Run the named oracle, relevant focused tests, the entire loom-code script suite, cross-reference validation, and privacy review before one atomic commit.

Each committed task is reviewed from immutable commit inputs by a specification reviewer and a quality reviewer. A finding returns to the same owner for repair; the oracle, focused tests, package suite, cross-reference and privacy gates rerun, followed by fresh immutable reviews. Only one task is claimed at a time even though their file sets are disjoint, keeping baselines, commits, and review evidence attributable.

After all 13 tasks pass, compare immutable full-plugin baseline and candidate roots for all 14 family skills: the 13 newly compacted entrypoints plus the already-completed `subagent-driven-development`. Run Claude Code `haiku` and Codex `gpt-5.6-luna`, two replicates per skill, using grounded prompts that exercise each skill's load-bearing decisions while prohibiting outbound, destructive, or persistent effects.

Only replicated results still classified `INCONCLUSIVE` after mechanical comparison go to a stronger evidence adjudicator. A confirmed regression returns to its owning task for full repair and retest.

## What Becomes Obsolete

Repeated examples, historical rationale, duplicate stage descriptions, copied schemas, and restated delegate contracts become obsolete when their removal leaves every always-needed decision and stop condition inline. No new harness, reference extraction, or alternate artifact schema is introduced.

## Out of Scope

- Recompacting `subagent-driven-development`; it is a fixed family context and final A/B corpus member only.
- Modifying a target `SKILL.md` in the same round or commit as its `test-prompts.json` or another bundled file; preflight and refactor bytes remain separate.
- Changing any trigger, exemption, authorization boundary, stage order, verdict vocabulary, reviewer population, tool invocation, artifact schema, side effect, retry cap, human gate, or stopping behavior.
- Adding or expanding references to absorb removed entrypoint text.
- Editing loom-design or loom-workflow skills in this family part.
- Making paid live evaluation an unconditional CI job.

## Queue relation

unqueued — this is the next sequential family part of the user-authorized compaction arc

## Open Questions

N/A — no unresolved question: scope, reduction range, no-extraction rule, host matrix, model tiers, replicate count, and adjudication policy are fixed

## Diagrams

N/A — no flow/state/architecture-shaped content: the implementation plan carries the 13-task ledger and final join
