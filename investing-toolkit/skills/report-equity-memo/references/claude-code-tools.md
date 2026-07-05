# Claude Code — tool name reference for `report-equity-memo`

> Phase 2.5's peer-discovery step names the `general-purpose` subagent
> type directly in `SKILL.md` — a real Claude-Code built-in agent-type
> name, but without literal `Agent(...)` call syntax. This file gives
> the concrete call shape + the Codex agent-type mapping.

## Peer-discovery dispatch

```
Agent({
  subagent_type: "general-purpose",
  description: "peer discovery",
  prompt: "<the Phase 2.5 prompt template — anchor_ticker + company_name>"
})
```

- **`general-purpose`** — Claude Code's built-in general-reasoning agent
  type. Do **not** substitute a read-only / search-restricted subagent
  type here — peer selection requires judgment (business-line
  comparability, scale-tier fit), not just retrieval.
- **Do not add `name:`** — see
  `loom-code/skills/using-loom-code/references/environment-gotchas.md`
  §A1: naming turns a one-shot blocking dispatch into a persistent
  mailbox-semantics teammate whose output is never delivered.
- One-shot, blocking: the orchestrator waits for the JSON peer list
  before proceeding to Phase 2.5's mode-switch step.
