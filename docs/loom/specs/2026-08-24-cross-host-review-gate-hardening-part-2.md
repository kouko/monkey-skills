# Brief: cross-host review-gate hardening — part 2

Date: 2026-08-24
Origin: implementation review of the approved cross-host review-gate hardening brief.

## Design-side on-ramp

fired: rows 1 — user chose direct

## Queue relation

unqueued — repairs the already approved cross-host review-gate hardening arc.

## Problem

The first implementation correctly made the marker refuse a stale reviewed
SHA, but it only wired the code-review station. The same shared reviewer rule
also serves the SDD and docs-review stations, whose dispatchers do not receive
the portable context. A partial fix would make ordinary review paths require
inputs that their callers never supply.

## Users

- Maintainers running code, docs, or per-task reviews from a consumer repo.
- Kouko, who needs one reliable review contract across Claude Code and Codex.

## Smallest End State

- BI-1 — Every reviewer role receives one complete context packet: target repo,
  reviewed SHA, plugin version, and only approved absolute plugin resources.
- BI-2 — Each caller passes that packet unchanged and names the reviewed SHA in
  its terminal verdict or marker route; no caller derives plugin paths from a
  consumer repository.
- BI-3 — Claude Code and Codex document equivalent adapter steps for resolving
  and passing that packet.
- BI-4 — A no-quota isolated-install dogfood test proves code, docs, and SDD
  routes work from a consumer repo without a `loom-code/` directory; stale SHA
  marker minting still refuses.

## Decision

Extend the existing plugin-local context resolver rather than creating host-
specific resolvers. Make the canonical reviewer discipline and every reviewer
caller consume its approved resource names. Keep local dogfood deterministic;
live host runs remain optional because they consume model quota.

## Alternatives Considered

- Give only code-review callers the new fields — rejected because shared Rule
  R1 would then break SDD and docs review.
- Copy the resolver into each host adapter — rejected because separate packet
  semantics would recreate host drift.

## Out of Scope

- Changing which review models are selected.
- Replacing the privacy judge; its public-name false positive is tracked
  separately from this correctness repair.
- Live Claude Code or Codex model-costing dogfood runs.
