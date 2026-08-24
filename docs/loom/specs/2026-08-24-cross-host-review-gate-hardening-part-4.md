# Brief: cross-host review-gate hardening — part 4

Date: 2026-08-24
Origin: complete reviewed-SHA data-flow census.

## Design-side on-ramp

fired: rows 1 — user chose direct

## Queue relation

unqueued — completes the already approved cross-host review-gate hardening arc.

## Problem

The packet and reviewer contracts now name a reviewed SHA, but several
executables still read mutable HEAD or accept an unbound verdict: scope
resolution, document citation pre-pass, and marker validation. Host adapters
also need an executable installed-root rule before stations can rely on them.
Every edge from context creation through marker minting must carry one SHA and
must consume plugin resources through the packet.

## Smallest End State

- BI-1 — Scope and citation checks operate on the packet SHA, never mutable
  HEAD or working-tree files.
- BI-2 — A marker requires a schema-valid verdict whose `reviewed_sha` exactly
  matches its `--expected-head`, in addition to checking repository HEAD.
- BI-3 — Claude Code and Codex adapters have tested installed-root resolution
  rules and hand the same packet to their stations.
- BI-4 — Code, docs, and SDD stations consume only the completed primitives;
  an isolated consumer dogfood test proves the complete SHA-bound flow.
- BI-5 — A reproducible live-host gate proves that both real CLIs load the
  candidate copy, preserve its packet SHA, and refuse unsafe adapter inputs
  without changing a user installation.

## Decision

Build the executable primitives first, then connect callers in data-flow
order. A station cannot substitute a prose promise for a missing scope,
citation, marker, or adapter invariant.

## Out of Scope

- Model-cost research beyond the mandatory, recorded Claude Code and Codex
  live-host release gate.
- Privacy judge redesign and reviewer-model selection.
