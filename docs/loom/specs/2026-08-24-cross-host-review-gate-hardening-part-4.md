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
  an isolated consumer dogfood proves the primitives, while live hosts prove
  the station dispatches consume that same flow.
- BI-5 — A reproducible live-host gate proves that both real CLIs load the
  candidate copy, preserve its packet SHA, and refuse unsafe adapter inputs
  without changing a user installation. A live station means a host-native
  slash invocation plus a candidate-root `review_context.py` subprocess event
  and a packet-consumption trace; echoed prose alone is not evidence. A
  gate-only nonce receipt makes that consumption observable without changing
  normal station behavior when no token is supplied.

## Decision

Build the executable primitives first, then connect callers in data-flow
order. A station cannot substitute a prose promise for a missing scope,
citation, marker, or adapter invariant.

For the live-host gate, resolve exactly one schema-valid packet per host attempt
before its four station sessions. That runner-owned candidate-root resolver
event is the sole packet source: stations must not re-resolve it. Each station
instead proves real loaded-skill consumption through a structured host Read/tool
event plus an exact packet trace, never final-answer echo alone. The copied
plugin and consumer worktree remain read-only, except `consumer/.git/loom`; the sessions prove routing and packet
consumption, not an artifact-writing whole review.

Each live session is therefore a gate-only two-tool protocol, not the station's
downstream reviewer workflow: first read the exact candidate station SKILL,
then execute the exact receipt or refusal-probe command, with no exploration or
reviewer dispatch. Claude exposes only those two case-specific tool patterns
through `--allowedTools`; the dedicated noninteractive profile uses
`bypassPermissions`, while the validator rejects any tool call beyond the exact
Read/Bash pair and broad Read/Bash approval
is forbidden.

The live gate may supply a nonce, packet path, and marker directory only to its
temporary fixture. In that mode a station writes one schema-validated receipt
only under `.git/loom`; without all gate inputs it performs no receipt action.
Negative routes receive no usable token and must produce neither receipt nor
downstream resolver/citation/scope/marker command.

Before launching either host, the runner removes every inherited
`LOOM_LIVE_GATE_*` variable and injects the five valid-case values only for a
valid station. Negative routes execute the candidate copy's deterministic
adapter probe and must expose its exact typed refusal through the host's
command-result event; prompt prose or a final `REFUSE:` line alone is not
evidence. The native negative slash command must also match its station.

Claude runs through the fixed `~/.claude-test` profile. Its configuration
sets `bypassPermissions`, and the runner invokes Claude with
`--permission-mode bypassPermissions`; the protected daily state must remain
unchanged. Command evidence accepts a wrapper only when Codex records its
host transport as exact `/bin/zsh -lc`; Claude and every other wrapper shape
are rejected.

## Out of Scope

- Model-cost research beyond the mandatory, recorded Claude Code and Codex
  live-host release gate.
- Privacy judge redesign and reviewer-model selection.
