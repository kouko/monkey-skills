# Claude Code — tool name reference for `daily-brief`

> The per-platform fan-out step in `SKILL.md` §"平行 fan-out" phrases
> dispatch in host-neutral prose ("一次性平行發出全部就緒平台的
> sub-agent"). This file is the concrete Claude Code call shape that
> prose resolves to.

## Per-platform parallel fan-out

One `Agent` call per ready platform (Slack / Asana / Notion / Gmail /
Calendar / GitHub / whichever passed the 0-A Gate), all issued in the
**same assistant message** so Claude Code runs them concurrently —
Claude Code only parallelizes `Agent` calls that appear together in
one message; sequential calls across separate messages block on each
other.

```
Agent({subagent_type: "general-purpose", description: "<platform> search", prompt: "<identity token + time window + search angles for this platform>"})
Agent({subagent_type: "general-purpose", description: "<platform> search", prompt: "..."})
... one per ready platform, same message ...
```

- **Do not add `name:`** to any of these calls — see
  `loom-code/skills/using-loom-code/references/environment-gotchas.md`
  §A1: naming turns a one-shot blocking dispatch into a persistent
  mailbox-semantics teammate whose output is never delivered as this
  turn's tool result.
- **Pass the identity token in the prompt**, not as a separate lookup —
  per `platform-search-playbook.md` §2, the subagent should never need
  to re-derive Slack user ID / Asana GID / Notion self id / email /
  GitHub login itself.
- **Each subagent must `ToolSearch` its own platform's MCP tools before
  calling them** — these tools are deferred; calling them without a
  prior `ToolSearch` fails with `InputValidationError`.
