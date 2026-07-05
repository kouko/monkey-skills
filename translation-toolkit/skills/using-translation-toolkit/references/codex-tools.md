# Codex CLI — tool name mapping for `translation-toolkit`

> All 5 active specialist skills phrase subagent dispatch in
> host-neutral prose. For the verified detail on Codex's `multi_agent`
> primitive (`spawn_agent`/`wait_agent`/`close_agent`) see
> `loom-code/skills/using-loom-code/references/codex-tools.md`. This
> file only maps `translation-toolkit`'s 2 dispatch points onto it and
> is **doc-sourced, not session-exercised** against this plugin.

## S1 back-translation gate (all 5 skills)

`spawn_agent` with the BACK-TRANSLATOR role prompt (blind v2 → source
retranslation, no access to the original source) as the agent's
instructions, then `wait_agent` for the result, then `close_agent`.

**Detecting "no isolation capability"** on Codex: the `multi_agent`
feature is disabled (`codex features list` shows `multi_agent  stable
false`), or the current agent's own `~/.codex/agents/*.toml` profile
forbids nested spawns. When disabled, S1 skips with the
`S1: SKIPPED (no isolation capability)` audit-trail flag, same as the
Claude-Code-side condition.

## `translation-novel`'s per-chapter EXTRACTOR dispatch

`spawn_agent` once per chapter (fresh context each time — no
cross-chapter conversation memory carries over except the accumulated
state JSON passed as input), with the canonical extractor prompt as
the agent's instructions, then `wait_agent`, then `close_agent`. Model
selection for the `extractor` role lives in the spawned agent's own
`~/.codex/agents/*.toml` profile — Codex has no per-call `model:`
parameter equivalent to Claude Code's `Agent()` call.
