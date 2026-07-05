# Claude Code — tool name reference for `dbt-wiki`

> Phase B parallel orchestration (`init/SKILL.md` §"Phase B parallel
> orchestration", inherited by reference in `redistill/SKILL.md` §Step 3)
> phrases subagent dispatch in host-neutral prose ("fans out one
> subagent per domain"). This file is the concrete Claude Code call
> shape that prose resolves to.

## Per-domain fan-out dispatch

```
Agent({
  subagent_type: "general-purpose",
  description: "distill <domain> domain",
  prompt: "<domain's evidence unique_ids + reserved_entities map +
            domains map + has_metricflow flag + write-direct or
            return-and-materialize instructions>"
})
```

One call per domain, all issued in the **same assistant message** so
Claude Code runs them concurrently — Claude Code only parallelizes
`Agent` calls that appear together in one message; sequential calls
across separate messages block on each other.

- **Do not add `name:`** to any of these calls — see
  `loom-code/skills/using-loom-code/references/environment-gotchas.md`
  §A1: naming turns a one-shot blocking dispatch into a persistent
  mailbox-semantics teammate whose output is never delivered as this
  turn's tool result.
- **Write-direct vs return-and-materialize** (per `init/SKILL.md`'s own
  §"Deliverable contract"): if domain agents reliably call `Write`
  themselves, use write-direct. If Step 6.6's persistence-verification
  gate shows zero files written despite the agent claiming success,
  switch to return-and-materialize — force a structured
  `{folder, slug, content}` output via a schema and have the
  orchestrator (not the subagent) call `Write`.
