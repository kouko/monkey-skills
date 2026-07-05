# Codex CLI — tool name mapping for `distill-sessions`

> Scoped to this skill's own dispatch points. For the general loom-code
> dispatch surface see
> `loom-code/skills/using-loom-code/references/codex-tools.md` — that
> file carries the verified detail on Codex's `multi_agent` primitive
> (`spawn_agent`/`wait_agent`/`close_agent`); this file only maps
> `distill-sessions`' 2 dispatch points onto it.
>
> **Doc-sourced, not session-exercised** against this specific skill's
> prompts — inherits the same evidence grain as loom-code's own
> `codex-tools.md` §Subagent dispatch.

## Stage 3 parallel fan-out (`agents/prompt-failure-analysis.md` / `agents/prompt-success-analysis.md`)

Delegates to `loom-code:dispatching-parallel-agents` for the concrete
per-host call shape. On Codex this resolves to `spawn_agent` once per
`subagent_payload[]` entry (each carrying
`agents/prompt-failure-analysis.md` or `agents/prompt-success-analysis.md`
as the agent's instructions plus that entry's
`session_events`/`target_skill_path`/`target_skill_md_content` as its
input), then `wait_agent` for all, then `close_agent` once done — Codex's
own runtime handles the wait-for-all/consolidate step automatically once
the spawn instruction names multiple agents (see `using-loom-code`'s
`references/codex-tools.md`).

## Stage 5c single dispatch (`agents/prompt-advisory-analyst.md`)

`spawn_agent` with `agents/prompt-advisory-analyst.md`'s content as the
agent's instructions plus the `merged_data`/`lang`/`date_str` JSON as its
input, then `wait_agent` for the result, then `close_agent`.

### Model selection

Codex has no `model: "sonnet"`-style per-dispatch alias parameter — model
choice for a spawned agent is configured via the agent's own profile
under `~/.codex/agents/*.toml`, not passed inline per call. Point the
profile at the current Sonnet generation to match the Claude Code side's
model lock.
