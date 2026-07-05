# Codex CLI — tool name mapping for `domain-teams`

> Every team's worker/evaluator launch instructions are host-neutral
> prose. For the verified detail on Codex's `multi_agent` primitive
> (`spawn_agent`/`wait_agent`/`close_agent`) see
> `loom-code/skills/using-loom-code/references/codex-tools.md`. This
> file only maps `domain-teams`' worker/evaluator + parallel-fan-out
> dispatch points onto it and is **doc-sourced, not session-exercised**
> against this specific plugin.

## Worker / evaluator dispatch

`spawn_agent` with `domain-teams/agents/worker.md` (or `evaluator.md`)
content as the agent's instructions, plus the Resource Paths block +
Task/Artifact/Requirements (per `agent-interface.md`'s Input Contract)
as its input, then `wait_agent` for the result, then `close_agent`.
Codex has no naming pitfall equivalent to Claude Code's `name:` —
its explicit three-verb model has no overloaded call for an extra
parameter to silently hijack.

## Parallel fan-out (e.g. `research-team/protocols/hook-parallel-fanout.md`'s nested sub-worker dispatch)

Codex's `multi_agent` feature natively supports "spawn N, wait for all,
consolidate" in one combined explicit instruction — frame the fan-out
as: "spawn one worker agent per sub-question (list them), each with its
own Resource Paths + sub-question; wait for all; integrate." Codex's own
runtime handles the waiting and consolidation once the spawn
instruction names all N sub-workers — no separate concurrency rule is
needed the way Claude Code's same-message rule is.

## Detecting "no subagent-spawning capability" (for the fan-out degradation path)

On Codex, this resolves to: the `multi_agent` feature is disabled
(`codex features list` shows `multi_agent  stable  false`, or the
current agent's own `~/.codex/agents/*.toml` profile forbids nested
spawns). When disabled, `hook-parallel-fanout.md`'s degraded-mode path
applies — issue N parallel tool calls in one round instead of spawning
N sub-workers.
