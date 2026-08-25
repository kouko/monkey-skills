# Brief: loom skill text compaction with cross-host behavioral equivalence

Date: 2026-08-25
Source: user-approved plan to shorten every loom skill while preserving behavior on Claude Code and Codex.
Status: FROZEN — the user approved the staged weak-model A/B approach in this thread.

## Design-side on-ramp

not fired — this is an incremental refactor of existing skill contracts with regression coverage

## Problem

The 33 loom skill entrypoints repeat rationale, examples, sibling-owned contracts, and host mechanics, so routine invocations pay context cost that does not always change decisions. Maintainers need a smaller default load without weakening activation, authorization, refusal, sequencing, output, or verification behavior.

## Users

- Loom users running skills through Claude Code or Codex, especially on weaker models where redundant prose competes with task context.
- Loom maintainers editing skill contracts who need objective regression evidence instead of judging equivalence from prose alone.
- Reviewers who need a clear distinction between behavior-preserving compaction and an unreviewed behavior change.

## Smallest End State

A shared replay harness runs the same behavior corpus against baseline and candidate plugin roots on Claude Code and Codex, normalizes host-specific events, and grades observable invariants rather than wording. Three representative high-yield skills prove the compaction recipe before the remaining 30 skills are changed in family-scoped waves. Every skill becomes shorter only when its static contract checks, existing tests, weak-model A/B probes, and required package tests remain green; aggregate before/after size is recorded honestly.

- BI-1 — Run one baseline-versus-candidate behavioral corpus through both Claude Code and Codex with normalized observable outcomes and retained raw transcripts.
- BI-2 — Compact distill-sessions, spec-expansion, and subagent-driven-development as representative workflow, design, and code-orchestration pilots without behavioral regression.
- BI-3 — Apply the validated compaction recipe to all remaining loom-code, loom-design, and loom-workflow SKILL.md entrypoints.
- BI-4 — Publish per-skill and aggregate before/after measurements plus all structural, behavioral, and package-test evidence.

## Current State Evidence

- **Forward** — `loom-code/scripts/loom_firing_harness.py` at `def run_one` and `def run_corpus` already runs a prompt corpus and grades firing, but its execution path is Claude-only.
- **Forward** — `loom-code/scripts/live_host_review_gate.py` at `HOSTS = ("claude", "codex")` already owns dual-host argv construction, isolated workspaces, event parsing, and observable gate validation.
- **Reverse** — `loom-code/tests/skill-triggering/` and the `*-pressure/prompts/` directories supply existing firing and refusal inputs consumed by the firing harness and manual dogfood runs.
- **Reverse** — `loom-code/scripts/test_loom_firing_harness.py` and `loom-code/scripts/test_live_host_review_gate.py` pin the two harness contracts that the shared replay path must preserve.
- **Error** — `loom-code/tests/codex-cli/test-hook-injection.sh` and `test-skill-loading.sh` cover Codex startup/load failures, but do not compare baseline and candidate behavior.
- **Data** — Claude emits stream JSON and Codex emits JSON events; the shared grader must normalize these into host-neutral markers while retaining the original JSONL as evidence.
- **Boundary** — `[API]` live weak-model runs consume Claude Code and Codex quota; deterministic unit tests must stub transcripts, while live A/B remains an explicit evaluation command rather than an always-on CI requirement.
- **Evidence paths**:
  - `loom-code/scripts/loom_firing_harness.py` — `def run_one`, `def run_corpus`
  - `loom-code/scripts/live_host_review_gate.py` — `HOSTS = ("claude", "codex")`, `host_argv_for_case`, `validate_host_result`
  - `loom-code/scripts/test_loom_firing_harness.py` — firing-harness unit tests
  - `loom-code/scripts/test_live_host_review_gate.py` — host-adapter and event-oracle tests
  - `loom-code/tests/skill-triggering/` — shared prompt corpus seed
  - `loom-code/tests/codex-cli/test-hook-injection.sh` — Codex hook smoke test
  - `docs/loom/backlog/2026-07-23-loom-code-replay-matrix-per-change-objective-regression-measurement.md` — replay-matrix start condition and n≥2 rule

## Alternatives Considered

| Alternative | Evidence | Why rejected |
|---|---|---|
| Compare the old and new Markdown with a strong-model reviewer | Existing cold-read dogfood records | A prose-equivalence opinion cannot prove tool order, refusal, disk effects, or host-specific loading behavior. |
| Move large sections to references and rely on static tests | `skill-creator` progressive-disclosure guidance | This can reduce entry size while leaving total runtime tokens unchanged, and static pins cannot detect decision regressions. |
| Run weak-model A/B on Claude Code only | Existing `loom_firing_harness.py` | Codex has different skill loading and event shapes; a Claude-only pass cannot establish cross-host behavior. |
| Add a shared dual-host behavior replay layer, then compact in measured waves | `live_host_review_gate.py` plus the replay-matrix backlog entry | Chosen: it reuses current machinery and produces comparable observable evidence before broad edits. |

## Decision

Build the smallest shared adapter that adds Codex execution and host-neutral event grading to the existing firing/review-gate machinery, with unit tests written RED first. Run live evaluation with economy models, at least two replicates for a divergence, and use a stronger model only to adjudicate surviving differences.

Compact each skill by deleting repetition first, extracting only genuinely conditional detail, and retaining triggers, safety boundaries, required sequences, output schemas, and final checks inline. Complete the work in sequential family-scoped parts so the full 33-skill objective remains explicit while each implementation plan stays reviewable.

- BI-5 — Treat observable behavior as the equivalence contract; wording similarity and model self-report are never pass criteria.
- BI-6 — Use deletion and true conditional loading before reference extraction, preserving every always-needed rule inline.

## What Becomes Obsolete

- BI-7 — Retire Claude-only replay execution once the shared runner covers both hosts without removing backward-compatible Claude invocation.
- BI-8 — Replace ad hoc one-off cold-read records for compaction with a reusable baseline/candidate evaluation command and structured result artifact.

## Out of Scope

- Changing the product behavior, authority boundaries, verdict vocabularies, or required tool sequences of any skill.
- Making live paid model evaluation an unconditional CI job.
- Rewriting non-loom plugins.
- Comparing natural-language wording for exact equality.
- Claiming that reference extraction saves runtime tokens when the reference is mandatory on every path.

## Queue relation

unqueued — the user directly authorized this arc while no backlog entry has status bet

## Open Questions

N/A — no unresolved question: the user approved the weak-model dual-host A/B approach and full 33-skill scope

## Diagrams

N/A — no flow/state/architecture-shaped content: the dependency order is captured in the implementation plans
