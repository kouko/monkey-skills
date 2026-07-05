# Claude Code — tool name reference for `distill-sessions`

> Scoped to this skill's own dispatch points. For the general loom-code
> dispatch surface (subagent-driven-development, requesting-code-review,
> parallel fan-out mechanics) see
> `loom-code/skills/using-loom-code/references/claude-code-tools.md` —
> this file only maps `distill-sessions`' 2 dispatch points onto it.

## Stage 3 parallel fan-out (`agents/prompt-failure-analysis.md` / `agents/prompt-success-analysis.md`)

Delegates to `loom-code:dispatching-parallel-agents` for the concrete
per-host call shape — see `using-loom-code`'s
`references/claude-code-tools.md`. On Claude Code this resolves to N
`Agent()` calls issued in a single assistant message so the harness
runs them concurrently:

```
Agent({
  subagent_type: "general-purpose",
  description: "<3-5 word task>",
  prompt: "<agents/prompt-failure-analysis.md or
            agents/prompt-success-analysis.md content +
            session_events / target_skill_path /
            target_skill_md_content JSON>"
})
```

One such call per `subagent_payload[]` entry, all issued in the same
assistant message per `dispatching-parallel-agents`'s concurrency rule.
**Do not add `name:`** — see
`loom-code/skills/using-loom-code/references/environment-gotchas.md`
§A1: it turns the one-shot blocking call into a persistent
mailbox-semantics teammate whose output is never delivered.

## Stage 5c single dispatch (`agents/prompt-advisory-analyst.md`)

```
Agent({
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "distill-sessions advisory report",
  prompt: "<agents/prompt-advisory-analyst.md content +
            merged_data / lang / date_str JSON>"
})
```

### Model alias

`model: "sonnet"` is Claude Code's harness-level alias for the current
Sonnet generation (Sonnet 4.6 at time of writing). Passing the literal
model id `"claude-sonnet-4-6"` (the id the prompt's own YAML frontmatter
documents) fails `Agent()`'s enum validation — always dispatch with the
alias, not the literal id.
