# Brief: loom skill text compaction — Part 1 dual-host harness and pilots

Date: 2026-08-25
Parent brief: docs/loom/specs/2026-08-25-loom-skill-text-compaction.md
Status: FROZEN — the user approved the staged weak-model A/B approach in this thread.

## Design-side on-ramp

not fired — this is an incremental refactor of existing skill contracts with regression coverage

## Problem

The full 33-skill compaction cannot proceed safely until the repository can compare observable baseline and candidate behavior on both supported hosts. The first part must prove both the test method and the writing method on representative high-density skills.

## Users

- Loom maintainers who need a reusable regression signal before editing the remaining skill entrypoints.
- Claude Code and Codex users who need the same activation, refusal, sequencing, and output behavior after compaction.

## Smallest End State

The existing firing harness can run baseline and candidate plugin roots through Claude Code and Codex, normalize observable outcomes, retain raw transcripts, and require repeated evidence before declaring a divergence. The three representative skills are measurably shorter with static contract tests, current package tests, and live weak-model A/B probes green.

- BI-1 — Run one baseline-versus-candidate behavioral corpus through both Claude Code and Codex with normalized observable outcomes and retained raw transcripts.
- BI-2 — Compact distill-sessions, spec-expansion, and subagent-driven-development without behavioral regression.
- BI-3 — Record per-pilot size deltas and all static, package, and live A/B evidence needed to decide whether the remaining 30 skills may proceed.

## Current State Evidence

- **Forward** — `loom-code/scripts/loom_firing_harness.py` at `def run_one` and `def run_corpus` already runs a prompt corpus and grades firing, but its execution path is Claude-only.
- **Forward** — `loom-code/scripts/live_host_review_gate.py` at `HOSTS = ("claude", "codex")` already owns dual-host argv construction, isolated workspaces, event parsing, and observable gate validation.
- **Reverse** — `loom-code/tests/skill-triggering/` and the `*-pressure/prompts/` directories supply existing firing and refusal inputs.
- **Error** — `loom-code/tests/codex-cli/test-hook-injection.sh` and `test-skill-loading.sh` cover startup/load failures but not baseline/candidate equivalence.
- **Data** — Claude stream JSON and Codex JSON events need one host-neutral observable record while the original JSONL remains evidence.
- **Boundary** — `[API]` live economy-model runs consume configured Claude Code and Codex quota and therefore remain an explicit evaluation command rather than unconditional CI.
- **Evidence paths**:
  - `loom-code/scripts/loom_firing_harness.py` — `def run_one`, `def run_corpus`
  - `loom-code/scripts/live_host_review_gate.py` — `HOSTS = ("claude", "codex")`, `host_argv_for_case`, `validate_host_result`
  - `loom-code/scripts/test_loom_firing_harness.py` — current firing-harness unit tests
  - `loom-code/scripts/test_live_host_review_gate.py` — current dual-host parser and oracle tests
  - `docs/loom/backlog/2026-07-23-loom-code-replay-matrix-per-change-objective-regression-measurement.md` — n>=2 replay rule

## Alternatives Considered

| Alternative | Evidence | Why rejected |
|---|---|---|
| Strong-model prose-equivalence review | Existing cold-read records | Cannot prove tool order, refusal, disk effects, or host-specific loading. |
| Static pins only | Existing skill structure and pin tests | Cannot observe decisions made by a weak model. |
| Claude-only replay | Current firing harness | Cannot establish Codex behavior. |
| Shared dual-host replay followed by three pilots | Current live host gate plus replay backlog | Chosen because it reuses proven host adapters and gates broad edits on measured behavior. |

## Decision

Extend the existing firing harness with the smallest shared host adapter and comparison record, writing failing unit tests first. Use economy models for live baseline/candidate replay, repeat any divergence at least twice, and route only surviving differences to stronger review.

Compact the three pilots by deleting repetition first and extracting only genuinely conditional material. Keep triggers, authority boundaries, hard stops, required sequences, output contracts, and final verification inline.

- BI-4 — Treat observable behavior as the equivalence contract; wording similarity and model self-report are never pass criteria.
- BI-5 — Use deletion and true conditional loading before reference extraction, preserving every always-needed rule inline.

## What Becomes Obsolete

- BI-6 — Retire Claude-only replay execution once the shared runner covers both hosts without removing the backward-compatible Claude invocation.

## Out of Scope

- Compacting the remaining 30 skills in this part; the parent brief keeps that required next stage explicit.
- Changing any skill's product behavior, authority boundary, verdict vocabulary, or required tool sequence.
- Making paid live evaluation an unconditional CI job.
- Comparing natural-language wording for exact equality.

## Queue relation

unqueued — this is the first sequential part of the user-authorized parent arc

## Open Questions

N/A — no unresolved question: the user approved the host matrix, weak-model probes, and staged rollout

## Diagrams

N/A — no flow/state/architecture-shaped content: the dependency graph is carried by the implementation plan
