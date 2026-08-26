# skill-refactor package-resource mode — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-26
> **Author**: Codex
> **Status**: FROZEN — user approved feeding the proven loom compaction controls back into `skill-refactor`

## Design-side on-ramp

not fired — this is a structural improvement to an existing developer skill with a user-approved direction

## Queue relation

unqueued — the user directly authorized this follow-up and there is no live bet entry

## Problem

When maintainers refactor a skill's bundled resources rather than only `SKILL.md`, they need `skill-refactor` to prove the candidate came from an immutable baseline, behaves consistently on supported hosts, passes gates at the right cost level, and reports honest package-wide savings.

## Users

- Skill maintainers — need one refactor workflow for entrypoint text and bundled resources without duplicating a reference-specific sibling skill.
- Claude Code and Codex users — need the same observable skill behavior after a package-resource refactor.
- Reviewers — need reproducible provenance, explicit ungradeable results, and net accounting that cannot report moved prose as savings.

## Smallest End State

`skill-refactor` gains a package-resource mode that reuses its existing Q1/Q2/Q3 model while generalizing the measured target beyond `SKILL.md`. A deterministic harness freezes a baseline tree, compares it with an isolated candidate, reports target-file and whole-package deltas, and rejects path or invariant drift. The workflow runs cheap per-file checks first, owning-skill behavior checks second, and optional family or plugin dual-host checks last; a host failure is ungradeable, never equivalent.

- BI-1 — Freeze and verify an immutable baseline for a target skill package before candidate generation.
- BI-2 — Compare baseline and candidate behavior on Claude Code and Codex with explicit ungradeable outcomes.
- BI-3 — Enforce per-resource, owning-skill, and package-or-family gate layers in increasing cost order.
- BI-4 — Report target-file and whole-package net word and byte deltas, counting every bundled-file addition and removal.

## Current State Evidence

- **Forward** — `skill-dev-toolkit/skills/skill-refactor/SKILL.md` at `## The Gate Function (per round)` defines Q1/Q2/Q3 around a post-edit `SKILL.md`, so bundled-resource edits cannot currently satisfy the documented reduction gate.
- **Forward** — `skill-dev-toolkit/skills/skill-refactor/scripts/equivalence_check.py` at `def run_layer_1` compares generated outputs, not the baseline and candidate skill packages that produced them.
- **Reverse** — `skill-dev-toolkit/skills/skill-refactor/scripts/multi_judge.py` at `actual judge calls are spawned` only aggregates three Claude-oriented judge results and has no host-normalized runner.
- **Reverse** — `scripts/skill_compaction_preflight.py` at `def export_baseline` and `loom-code/scripts/loom_firing_harness.py` at `def compare_hosts` already prove immutable Git-tree export, raw transcript retention, dual-host normalization, and at least two replicates.
- **Error** — `loom-code/scripts/loom_firing_harness.py` at `gradeable =` excludes non-gradeable host outcomes from equivalence, while current `skill-refactor` has no package-mode ungradeable vocabulary.
- **Data** — `docs/loom/dogfood/2026-08-26-loom-family-skill-compaction-summary.md` at `Counting the three pilot references back in` records extraction-adjusted package accounting rather than gross `SKILL.md` shrinkage.
- **Boundary** — `[API]` live Claude Code and Codex runs consume quota and vary by host; deterministic fixture tests must cover the harness logic, with live replay remaining an explicit final gate.
- **Evidence paths**:
  - `skill-dev-toolkit/skills/skill-refactor/SKILL.md` — `## The Gate Function (per round)`
  - `skill-dev-toolkit/skills/skill-refactor/scripts/equivalence_check.py` — `def run_layer_1`
  - `skill-dev-toolkit/skills/skill-refactor/scripts/multi_judge.py` — `actual judge calls are spawned`
  - `scripts/skill_compaction_preflight.py` — `def export_baseline`
  - `loom-code/scripts/loom_firing_harness.py` — `def compare_hosts`
  - `docs/loom/dogfood/2026-08-26-loom-family-skill-compaction-summary.md` — `Counting the three pilot references back in`

## Decision

Extend `skill-refactor` with one conditional package-resource protocol and deterministic package harness; do not create a new skill. Port the general lessons rather than importing loom-specific paths: immutable tree fingerprints, pluggable host observations, layered gates, and net package accounting. Keep the current output-equivalence scripts for generated artifacts, but make package validation a separate responsibility with a closed verdict schema. Candidate work happens in an isolated root and only passing changes are applied to the user's worktree.

- BI-5 — Add package-resource mode to the existing skill without duplicating its trigger or Q1/Q2/Q3 ownership.
- BI-6 — Keep package validation generic and host-adapter-driven rather than depending on loom-code at runtime.

## Out of Scope

- Refactoring loom reference prose in this change.
- Creating a `reference-refactor` sibling skill.
- Changing `skill-tuning`, `skill-judge`, or `dogfood-skill-testing` behavior.
- Requiring paid live-host evaluation in every CI run.
- Redesigning creative-output equivalence or replacing the existing judge ensemble.
- Supporting arbitrary non-skill repositories as package targets.

## Alternatives Considered

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| Keep the gate `SKILL.md`-only | [Anthropic Agent Skills overview, English](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | Skills include instructions, scripts, and resources; measuring only the entrypoint omits part of the shipped behavior and context cost. |
| Create a reference-only sibling skill | [OpenAI Skills guide, Japanese](https://openai.com/ja-JP/academy/skills/) | The user intent and workflow remain behavior-preserving skill refactoring, so a sibling would duplicate triggers, gates, and maintenance. |
| Generalize `skill-refactor` with layered package mode | [Anthropic skill authoring best practices, English](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); [Japanese](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices) | Chosen: evaluation-first development and progressive disclosure support one entrypoint with conditional package details. |

## What Becomes Obsolete

- BI-7 — Retire `SKILL.md`-only Q2 accounting as the universal reduction rule; retain it only for entrypoint mode.
- BI-8 — Retire ad hoc loom-only package-compaction setup as the only way to obtain immutable, dual-host, net-accounted evidence.
- BI-9 — Replace rollback-by-`git revert` guidance for uncommitted candidates with isolated-candidate discard and apply-after-pass.

## Open Questions

N/A — no unresolved question: the user explicitly approved the four capabilities and the existing-skill direction

## Diagrams

N/A — no user interaction or state model: the gate dependency order will be expressed in the implementation plan
