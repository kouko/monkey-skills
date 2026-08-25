# Brief: loom-workflow skill text compaction

Date: 2026-08-25
Parent brief: docs/loom/specs/2026-08-25-loom-skill-text-compaction.md
Status: FROZEN — Part 1's dual-host pilot gate passed and the user authorized continuing the staged compaction.

## Design-side on-ramp

not fired — this is a behavior-preserving refactor of existing workflow contracts with regression coverage

## Problem

The eight remaining loom-workflow entrypoints repeat examples, historical rationale, anti-pattern explanations, and schemas already owned by focused references. Their 19,725-word default load makes weaker models spend context on teaching prose even when the current path needs only the activation rule, hard gates, output contract, and final check.

## Users

- Claude Code and Codex users who need unchanged workflow decisions after the entrypoints become shorter.
- Loom maintainers who need a per-skill essence oracle and reproducible size target rather than subjective prose review.
- Reviewers who need real weak-model evidence for activation, refusal, sequencing, output, and stop behavior.

## Smallest End State

All eight remaining loom-workflow `SKILL.md` entrypoints are measurably shorter while retaining their always-needed behavior inline. Each skill has a RED-first static contract test, valid conditional references, existing tests green, and at least two baseline/candidate replicates on Claude Code `haiku` and Codex `gpt-5.6-luna`; surviving divergence is reviewed by a stronger model before classification.

- BI-1 — Compact brief-before-asking while preserving four-mode routing, the repeated-confusion guard, turn ordering, the six-block contract, escape hatches, and pre-send check.
- BI-2 — Compact complexity-critique while preserving mandatory mindset loading, the three ordered questions, greenfield handling, verdict vocabulary, and single-change routing boundary.
- BI-3 — Compact cot-explain while preserving source resolution, chain extraction and early exit, Mermaid layout rules, Markdown/HTML authority, render-verify-render, fidelity review, and publishing consent.
- BI-4 — Compact dbt-model-style while preserving bounded enforcement, style-versus-logic scope, CTE roles, zero-logic `final`, passthrough, naming/comments, header, Redshift syntax, config, and self-check.
- BI-5 — Compact git-memory while preserving mandatory invocation, internal trailer classification, durable-store hierarchy, privacy gate, commit/PR/merge capture and verification, and on-demand recall.
- BI-6 — Compact handoff while preserving prepare/resume routing, ten-block schema, verbatim state capture, Resume Launcher, T1/T2 verification policy, conversation language, and synthesis stop.
- BI-7 — Compact proposal-critique while preserving enumerate/decompose, grounding and necessity axes, the triage matrix, DEFER fall-through, three-bucket output, and routing boundaries.
- BI-8 — Compact recap-state while preserving in-session scope, six rendered L3 blocks, verbatim critical phrases, two-mode separation, visual limits, and the synthesis soft gate.
- BI-9 — Record per-skill and aggregate size deltas plus static, package, Claude Code, Codex, replicate, raw-evidence, and stronger-adjudication results with no unexplained regression.

## Current State Evidence

- **Data** — current `wc -w` baselines are 3,072 brief-before-asking, 2,150 complexity-critique, 4,350 cot-explain, 3,573 dbt-model-style, 2,341 git-memory, 1,448 handoff, 1,366 proposal-critique, and 1,425 recap-state; total 19,725 words.
- **Forward** — `loom-code/scripts/loom_firing_harness.py` exposes `compare` with separate `--claude-model`, `--codex-model`, baseline/candidate roots, raw directory, output path, and `--replicates`; Part 1 already validated this capability.
- **Forward** — `docs/loom/dogfood/2026-08-25-loom-skill-compaction-dual-host-ab.md` records successful Claude `haiku` and Codex `gpt-5.6-luna` pilot runs with two replicates and stronger adjudication.
- **Boundary** — references may hold examples, rationale, schemas, or phase-conditional detail, but triggers, authorization, hard stops, required order, output shape, and final verification remain inline.
- **Boundary** — live host runs consume configured local quota and remain an explicit evaluation step, not an unconditional CI job.
- **Evidence paths**:
  - `loom-workflow/skills/brief-before-asking/SKILL.md` — `## Four Trigger Modes`, `## The 6-Block Briefing Structure`, `## Pre-send check`
  - `loom-workflow/skills/complexity-critique/SKILL.md` — `## Before You Begin — Load a Mindset`, `## The Gate Function`, `## Verdict`
  - `loom-workflow/skills/cot-explain/SKILL.md` — `## Step 1` through `## Step 6`, `## Failure modes to refuse`
  - `loom-workflow/skills/dbt-model-style/SKILL.md` — `## Scope of enforcement`, `## 1. CTE structure`, `## After writing / editing`
  - `loom-workflow/skills/git-memory/SKILL.md` — `## Invocation policy`, `## Three pillars`, `## When not to use`
  - `loom-workflow/skills/handoff/SKILL.md` — `## Prepare mode`, `## Resume mode`, `## Apply all 5 共通核心原則`
  - `loom-workflow/skills/proposal-critique/SKILL.md` — `## The Gate Function`, `## The Triage Matrix`, `## When To Apply`
  - `loom-workflow/skills/recap-state/SKILL.md` — `## What to do`, `## Soft-gate Synthesis-check`, `## What NOT to do`

## Alternatives Considered

| Alternative | Evidence | Why rejected |
|---|---|---|
| Apply one uniform percentage to all eight skills | Current baselines and structures differ substantially | A dense operative contract such as cot-explain or dbt-model-style has less safe deletion headroom than example-heavy critique skills. |
| Move every long section to a mandatory reference | Progressive-disclosure rule and Part 1 findings | Mandatory references preserve total runtime load and can hide always-needed gates from weak models. |
| Trust static string pins alone | Part 1 dual-host dogfood | Static pins prove words remain, not that weak models still activate, stop, sequence tools, or write the same artifacts. |
| Use per-skill conservative ranges plus dual-host replay | Current skill reconnaissance and successful Part 1 harness | Chosen: it allows different safe ceilings while keeping observable behavior as the release gate. |

## Decision

Implement eight independent RED-first compaction tasks, one per skill directory. Delete repetition before extracting content; when extraction is needed, use one focused reference with an explicit conditional read trigger. Keep the essence listed in BI-1 through BI-8 inline and enforce it with a named static test.

Use conservative reductions grounded in each entrypoint's current redundancy: brief-before-asking 22–30%, complexity-critique 25–35%, cot-explain 18–25%, dbt-model-style 18–25%, git-memory 22–30%, handoff 18–25%, proposal-critique 25–35%, and recap-state 20–28%. A task may exceed its lower bound only after its essence oracle and existing tests pass; no upper target authorizes deleting behavior.

After all eight tasks pass review, run the established Part 1 comparator with Claude Code `haiku` and Codex `gpt-5.6-luna`, at least two replicates per skill. Retain raw JSONL outside the repo, record redacted paths and normalized observables, and route every replicated surviving divergence to stronger-model evidence review; a confirmed regression returns to the owning skill task.

## What Becomes Obsolete

Repeated inline worked examples, historical incident narratives, duplicated schema prose, and repeated rationale become obsolete where a focused reference already owns them or a new conditional reference is introduced. The Part 1 harness remains the only comparison abstraction; this part adds no second runner.

## Out of Scope

- Changing any workflow's trigger, authorization, verdict vocabulary, required order, output schema, file effect, privacy rule, or stop behavior.
- Compacting `distill-sessions`, which was completed and validated in Part 1.
- Editing loom-code or loom-design skills in this family-scoped part.
- Updating translated READMEs or unrelated documentation merely to mirror internal prose movement.
- Making paid live evaluation an unconditional CI job.

## Queue relation

unqueued — this is the next sequential family part of the user-authorized compaction arc

## Open Questions

N/A — no unresolved question: Part 1 fixed the host matrix, model tiers, replicate count, and adjudication policy

## Diagrams

N/A — no flow/state/architecture-shaped content: the implementation plan carries the wide fan-out and final join
