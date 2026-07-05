# Claude Code — tool name reference for `domain-teams`

> Every team's worker/evaluator launch instructions (`skill-team/standards/agent-interface.md`,
> echoed in all 9 team `SKILL.md` files) are written as host-neutral
> prose — a Resource Paths block, not a literal tool call. This file is
> the concrete Claude Code call shape that prose resolves to.

## Worker / evaluator dispatch

```
Agent({
  subagent_type: "domain-teams:worker",     # or "domain-teams:evaluator"
  description: "<3-5 word task>",
  prompt: "<Resource Paths block + Task/Artifact/Requirements per
            agent-interface.md's Worker/Evaluator Input Contract>"
})
```

- **Do not add `name:`.** Naming this call turns a one-shot blocking
  dispatch into a persistent mailbox-semantics teammate whose output is
  never delivered as this turn's tool result — only an explicit
  `SendMessage` retrieves it, and no team workflow in this plugin has a
  step that does that. `description:` is unrelated and always required
  regardless.
- `domain-teams/agents/worker.md` and `evaluator.md` are plain Markdown
  role prompts (no Claude-Code-specific syntax inside them) — they
  transcribe unchanged into whichever host's dispatch call this file
  documents.

## Parallel fan-out (e.g. `research-team/protocols/hook-parallel-fanout.md`, `copywriting-team/protocols/copy-ideation-advanced.md`)

Claude Code runs `Agent` calls concurrently **only when they appear in
the same assistant message**:

```
# ✅ Concurrent — one message, N Agent calls (one per sub-worker)
Agent({subagent_type: "domain-teams:worker", description: "...", prompt: "<sub-question 1>"})
Agent({subagent_type: "domain-teams:worker", description: "...", prompt: "<sub-question 2>"})
Agent({subagent_type: "domain-teams:worker", description: "...", prompt: "<sub-question N>"})

# ❌ Sequential — each call in its own message, blocks on the prior
Agent({...sub-question 1...})    # message 1
# (wait for it to return)
Agent({...sub-question 2...})    # message 2
```

## Detecting "no subagent-spawning capability" (for the fan-out degradation path)

`hook-parallel-fanout.md`'s degraded-mode check ("no subagent-spawning
capability in the worker's tool set") resolves on Claude Code to: no
`Agent` tool is present in the current agent's tool list (a plain
in-context worker invoked without tool access, or a restricted
subagent type). When `Agent` is absent, fall back to the degraded
single-agent parallel-I/O path per that hook's own rules.
