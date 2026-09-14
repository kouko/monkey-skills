# Codex CLI — tool name mapping for `daily-news-digest`

> This self-contained file maps this skill's heavy-day dispatch onto the
> current Codex concurrent-subagent tool shape and is **doc-sourced,
> not session-exercised** against this specific skill.

## Heavy-day parallel fan-out (STEP 6/7)

`spawn_agent` once per story-cluster (each carrying that cluster's note
paths + story angle as its instructions), plus optionally one more for
the STEP 7 knowledge tier, then `wait_agent` for all, then `close_agent`
once done. Codex's own runtime automatically waits for and consolidates
all subagent results before returning — there is no per-call toggle to
set, so the Claude-Code-only "never `run_in_background: true`" pitfall
(see `claude-code-tools.md`) and the `name:`-triggers-mailbox-semantics
pitfall both structurally cannot recur on Codex: three explicit verbs,
not one overloaded call with an easy-to-miss extra parameter.

Frame the dispatch as an explicit spawn instruction (Codex spawns
subagents only on explicit instruction, never autonomously mid-skill):
"spawn one agent per story-cluster with its note paths + story angle,
wait for all, then assemble."
