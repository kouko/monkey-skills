# Codex CLI — tool name mapping for `dbt-wiki`

> This self-contained file maps `dbt-wiki`'s per-domain fan-out onto the
> host's current Codex concurrent-subagent tool shape and is
> **doc-sourced, not session-exercised** against this plugin.

## Per-domain fan-out dispatch

`spawn_agent` once per domain (each carrying that domain's evidence
`unique_id`s + the `reserved_entities`/`domains` maps + the
`has_metricflow` flag as its instructions), then `wait_agent` for all,
then `close_agent` once done. Codex's own runtime handles the
wait-for-all/consolidate step automatically once the spawn instruction
names all domains — no "same assistant message" rule to follow the way
Claude Code requires.

- **Write-direct vs return-and-materialize** applies identically on
  Codex: if a spawned domain agent doesn't reliably persist files
  (Step 6.6's persistence-verification gate shows zero files written),
  switch to having the agent return `{folder, slug, content}` and have
  the orchestrator write the files itself.
