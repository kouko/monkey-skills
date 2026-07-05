# Claude Code — tool name reference for `domain-teams`

> Every team's worker/evaluator launch instructions
> (`domain-teams/skills/skill-team/standards/agent-interface.md`,
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

## Parallel fan-out (e.g. `research-team/protocols/hook-parallel-fanout.md`'s nested sub-worker dispatch)

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
capability in the worker's tool set") is a two-part check on Claude
Code, not a single tool-presence lookup:

1. **Tool present?** Is `Agent` absent from the current agent's tool
   list (a plain in-context worker invoked without tool access, or a
   restricted subagent type)? If absent, degrade — this part alone is
   sound: a tool the agent cannot invoke guarantees the spawn fails.
2. **Recursion actually permitted?** Tool presence does **not** by
   itself guarantee a *nested* spawn is allowed — a host can hand a
   worker the `Agent` tool while still capping recursion depth or
   forbidding worker-spawns-worker via session/sandbox policy. There is
   no single introspectable flag for this on Claude Code today.
   **When you cannot positively confirm recursion is permitted, default
   to the degraded path and emit the disclosure line** — the same
   fail-safe Codex gets for free from its explicit
   feature-flag-plus-profile check below. Treating "tool present" as
   equivalent to "may recurse" is the asymmetry to avoid: it risks a
   silent, undetected degradation where the worker believes it achieved
   true fan-out (and skips the disclosure) but the nested spawn actually
   no-oped.

Symmetric Codex check: the `multi_agent` feature is disabled
(`codex features list` shows `multi_agent stable false`), **or** the
current agent's own `~/.codex/agents/*.toml` profile forbids nested
spawns — either condition alone is sufficient to degrade.
