# Clarify Loom authorization boundaries — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-27
> **Author**: Codex, approved by kouko

## Design-side on-ramp

not fired — this is a bounded correction to existing workflow contracts, not product-shaped work

## Queue relation

unqueued — the user directly authorized this correction after two live workflow failures

## Problem

When an authorized change enters review or close-out, the user needs Loom to continue ordinary in-scope repair without repeated permission requests while preserving the hard boundary that agents never merge main.

## Users

- Loom users running change tasks — need review findings resolved without authorization arriving in small batches.
- Loom maintainers — need each owning skill to state its own boundary without a new shared synchronization subsystem.

## Smallest End State

The docs-review workflow distinguishes review-only requests from authorized change tasks and does not repeatedly ask for deterministic in-scope fixes. The branch-finishing workflow distinguishes forbidden main-changing actions from allowed synchronization after a human merge. Four regression scenarios demonstrate both boundaries; no shared SSOT, generator, or CI workflow is added.

- BI-1 — Authorized change tasks continue through deterministic in-scope documentation findings without repeated permission requests.
- BI-2 — Review-only tasks report findings without modifying artifacts.
- BI-3 — Standard PR close-out reaches ready-to-merge but never changes main or enables merge on the user's behalf.
- BI-4 — After a user-completed PR merge, local main synchronization is allowed and is not classified as an agent merge.

## Current State Evidence

- **Forward**: `loom-code/skills/requesting-docs-review/SKILL.md` §Process sends gating findings to the user and forbids auto-fix; `loom-code/skills/finishing-a-development-branch/SKILL.md` §Default flow drives publication.
- **Reverse**: `loom-code/skills/finishing-a-development-branch/SKILL.md` §Cross-skill contract delegates its docs arm to requesting-docs-review.
- **Error**: `requesting-docs-review/SKILL.md` Directive 2 treats a still-blocking confirmation as a new authorization stop; `finishing-a-development-branch/references/delegation-boundaries.md` says merge stays with the user.
- **Data**: Inputs are the initiating request, review findings, confirmation verdict, PR state, and Git branch state; outputs are act/report/stop decisions.
- **Boundary**: `[SECURITY]` GitHub publication and main-branch mutation are external, shared-state boundaries owned by finishing-a-development-branch.
- **Evidence paths**: `loom-code/skills/requesting-docs-review/SKILL.md` §Process; `loom-code/skills/finishing-a-development-branch/SKILL.md` §Default flow; `loom-code/skills/finishing-a-development-branch/references/delegation-boundaries.md` §What this skill does NOT do; `~/.claude/rules/judgment-rubrics.md` §3.

## Decision

Modify only the two owning skills and their behavioral contracts. Do not add a canonical authorization file, generated references, synchronization code, or a new CI workflow. Preserve review convergence limits as quality stops rather than permission batches, and make every main-changing action agent-forbidden while allowing post-merge local synchronization.

- BI-5 — The two owning skills contain the complete minimal correction, protected by focused regression tests rather than a new authorization framework.

## Out of Scope

- A repository-wide authorization taxonomy or autonomy-level configuration.
- Changes to host sandbox or approval policy.
- Allowing an agent to merge main after conversational authorization.
- The separate reference-prose compaction arc.

## Alternatives Considered

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| Canonical YAML with generated role slices | Proposed during this session | Adds a rule generator, consumer registry, and cross-plugin CI for two distinct failures. |
| Canonical Markdown copied into every skill | Existing family-contract pattern | Better than YAML but still couples unrelated review-remediation and Git-merge policies. |
| Direct owning-skill corrections | Current decision | Smallest change that fixes the two observed failures and preserves skill independence. |

## What Becomes Obsolete

- BI-6 — The docs-review blanket prohibition on auto-fixing every instruction finding becomes obsolete.
- BI-7 — Ambiguous wording that lets an agent treat “merge” as permission to change local main becomes obsolete.

## Open Questions

N/A — no unresolved question: the user approved the smallest direct-edit design and the permanent agent-never merge boundary

## Diagrams

N/A — no flow/state/architecture-shaped content: two local policy corrections and their regression cases are sufficient
