# Codex CLI — subagent dispatch reference

This plugin's skills (`design-critic`'s multi-lens panel) phrase subagent
dispatch in host-neutral prose. This file is the concrete Codex re-binding.

**Verified 2026-07-05, mixed evidence grain**: the `multi_agent` feature
flag itself is live-confirmed (`codex features list` on a local Codex
0.139.0 install showed `multi_agent  stable  true`). The verb names and
behavioral claims below are doc-confirmed (OpenAI's official Codex
manual §Subagents) — not exercised in a live Codex session against this
specific plugin's skills.

## Subagent dispatch

Codex's real subagent primitive is `multi_agent` — three explicit verbs
(`spawn_agent`, `wait_agent`, `close_agent`), not a single overloaded call.
If disabled:

```toml
# ~/.codex/config.toml
[features]
multi_agent = true
```

- **Explicit-trigger only.** Codex spawns subagents only on explicit
  instruction — never autonomously mid-skill. Frame the dispatch as an
  explicit spawn request: "spawn N lens-critic agents, one per lens, each
  with the artifact paths + heuristics reference + its persona + its lens
  row; wait for all; consolidate."
- **No naming pitfall.** Codex's own runtime automatically waits for and
  consolidates all subagent results — there is no per-call parameter that
  silently flips a dispatch into async/mailbox semantics the way Claude
  Code's `name:` does. This class of failure structurally cannot recur on
  Codex (three explicit verbs, not one overloaded call).
- **Agent-type equivalent to "general-purpose, never read-only/search"**
  (this mapping is this file's own inference, not a manual-stated fact —
  the manual documents the three built-in agents generically, it does not
  discuss lens-critics). Codex ships built-in agents `default`
  (general-purpose fallback), `worker` (execution-focused), and `explorer`
  (read-heavy codebase exploration). A lens-critic is pure reasoning over
  an artifact, not codebase exploration — spawn with `default` (or a
  custom general agent), **not** `explorer`; `explorer`'s narrower framing
  risks the same refuse-the-reasoning-role failure mode the Claude Code
  side warns about.

## Parallel fan-out (one round = N lens dispatches)

Codex's `multi_agent` feature natively supports "spawn N, wait for all,
consolidate" in **one combined explicit instruction** — this is literally
the manual's own worked example ("spawn one agent per point, wait for all
of them, and summarize the result for each point"). Unlike Claude Code
(where concurrency depends on issuing N separate `Agent` calls in the same
assistant message), Codex's own runtime handles the waiting and
consolidation once the spawn instruction names all N lenses:

```
Spawn N lens-critic agents, one per lens (list personas + lens rows),
each reading the artifact paths + references/design-heuristics.md.
Wait for all N. Consolidate findings into the panel union.
```

A targeted re-seed round names only the re-dispatched lens(es); a full
panel round names all 5 fixed lenses (plus the conditional
`docs/loom/PRINCIPLES.md` lens, when present).
