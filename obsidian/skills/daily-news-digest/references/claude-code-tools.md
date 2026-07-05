# Claude Code — tool name reference for `daily-news-digest`

> Scoped to this skill's own heavy-day dispatch point
> (`heavy-day-dispatch.md`). For the general dual-host dispatch pattern
> this file follows, see `loom-code/skills/using-loom-code/references/claude-code-tools.md`.

## Heavy-day parallel fan-out (STEP 6/7)

One subagent per story-cluster (plus optionally one more for the STEP 7
knowledge tier), all dispatched **blocking**, in one round:

```
Agent({subagent_type: "general-purpose", description: "...", prompt: "<cluster note paths + story angle>"})
Agent({subagent_type: "general-purpose", description: "...", prompt: "<cluster note paths + story angle>"})
...
```

- **Same-assistant-message concurrency**: Claude Code runs `Agent` calls
  concurrently only when they appear in the same assistant message —
  issue one call per cluster, all in one message.
- **Never set `run_in_background: true`.** STEP 8 assembly can't start
  until every subagent returns, so background dispatch buys no
  parallelism and only creates end-of-turn stop-hook contention — a
  real 2026-07-02 failure produced eight consecutive blocked turns
  after the digest was already written, because a background dispatch
  left the turn "waiting" on results nothing was polling for.
- **Do not add `name:`** to any of these calls — see
  `loom-code/skills/using-loom-code/references/environment-gotchas.md`
  §A1: naming turns a one-shot blocking call into a persistent
  mailbox-semantics teammate whose output is never delivered as this
  turn's tool result.
- If a `ScheduleWakeup`/cron was set to wait on results, cancel it as
  soon as the subagent results are collected — it has no further
  purpose once STEP 8 assembly starts.
