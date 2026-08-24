# Review binding remediation — brief

> **Phase**: whole-branch review remediation
> **Date**: 2026-08-24
> **Authority**: user explicitly authorized repairs after review findings

## Design-side on-ramp

not fired — this corrects internal review and plugin-install contracts.

## Queue relation

unqueued — it repairs the active cross-host review-gate branch before release.

## Problem

Some review instructions claim to judge an immutable commit but still read files from the editable worktree, use a whole-branch file list for one task, or describe incompatible Claude and Codex confirmation paths. A reviewer can therefore inspect A and produce a marker that permits B.

## Users

- A maintainer running loom-code from Claude Code or Codex.
- A reviewer agent that must receive one internally consistent evidence packet.
- A release gate that must refuse an unbound or contradictory review route.

## Smallest End State

Every review artifact path is converted to a target-repository-relative path and read from the reviewed SHA; each SDD reviewer sees only its task's declared files; Claude and Codex documentation describe executable, non-conflicting confirmation routes; and stale sandbox/path instructions are removed.

- BI-1 — Immutable reviewer reads cannot fall back to mutable worktree artifacts.
- BI-2 — Per-task review scope cannot expand to unrelated branch files.
- BI-3 — Post-fix confirmation has one executable contract per host.
- BI-4 — The marker and documentation agree on accepting valid simplification records and named test profiles.

## Current State Evidence

- **Forward**: `loom-code/agents/code-reviewer.md` — headings `D8 — Principles Conformance` and `D9 — Deliberate-Simplification Marker Harvest` still name mutable-worktree operations.
- **Reverse**: `loom-code/scripts/_reviewer-discipline.md` — immutable snapshot rule is the shared contract agent files must follow.
- **Error**: `loom-code/skills/requesting-docs-review/SKILL.md` — `Directive 2` conflicts with its binding convergence contract.
- **Data**: `loom-code/skills/subagent-driven-development/SKILL.md` — its reviewer packet names `review_scope.py` as the only artifact scope despite per-task review.
- **Boundary**: `loom-code/scripts/loom_gate_markers.py` — marker minting validates a terminal reviewed SHA.

## Decision

Repair the contracts and their structural tests in four atomic slices. Use repository-relative packet paths for every SHA snapshot read; derive an SDD review scope from the active task; specify Codex fresh confirmation with its original findings and terminal-output mapping; and align marker/document prose with the durable test-profile route. Keep the existing real-host gate and its exact receipt validation.

## Out of Scope

- Changing reviewer model selection or the privacy judge.
- Relaxing any exact receipt, reviewed-SHA, or marker validation.
- Replacing the named `claude-test` profile with a temporary profile.

## Alternatives Considered

| Alternative | Why not selected |
|---|---|
| Permit reviewers to resolve absolute paths from the worktree | Reintroduces the A-versus-B evidence gap.
| Treat Codex as an exception to the docs convergence contract without an explicit adapter contract | Leaves an executor with incompatible instructions.
| Suppress valid simplification ledgers before marker minting | Rejects documented, bounded trade-offs rather than validating them.

## What Becomes Obsolete

- BI-5 — Mutable-worktree evidence reads inside reviewer contracts.
- BI-6 — Mutable Claude sandbox flags and paths in Part 4 records.

## Open Questions

N/A — no unresolved question: the review findings and user authorization fix the required direction.

## Diagrams

N/A — the packet/data boundary is described by the existing cross-host gate artifacts.
