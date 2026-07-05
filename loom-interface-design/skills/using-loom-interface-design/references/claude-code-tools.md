# Claude Code — subagent dispatch reference

This plugin's skills (`design-critic`'s multi-lens panel) phrase subagent
dispatch in host-neutral prose ("dispatch one subagent per lens, fresh
context, general reasoning agent"). This file is the concrete Claude Code
call shape that prose resolves to.

## Subagent dispatch

```
Agent(
  subagent_type: "general-purpose",
  description: "<3-5 word lens task>",
  prompt: "<self-contained lens-critic task — agent has no prior context>"
)
```

- **`subagent_type: "general-purpose"`** — the host's general reasoning
  agent type. Do **not** use a read-only / search / explore-restricted
  subagent type for a lens-critic: a search-restricted subagent's system
  prompt can refuse the reasoning role outright, silently dropping that
  lens (a false negative the panel has no way to detect from the outside).
  On a host whose *default* subagent is a search/explore type, override it
  explicitly for every lens dispatch.
- **Do not add `name:`.** Adding `name:` to this call turns a one-shot
  blocking dispatch into a persistent, addressable "teammate" running on
  mailbox semantics — its output is never delivered as this turn's tool
  result; only an explicit `SendMessage` call retrieves it, and the
  panel's loop-until-dry logic has no step that does this. `description:`
  is unrelated and always required regardless (it does not trigger this
  behavior).
- Each lens-critic's prompt carries: the artifact paths, the
  `references/design-heuristics.md` path, its persona string, and its one
  lens row — per the skill's own "Lens-critic input contract."

## Parallel fan-out (one round = N lens dispatches)

Claude Code runs `Agent` calls concurrently **only when they appear in the
same assistant message**. A loop-until-dry round dispatches all N
lens-critics for that round together:

```
# ✅ Concurrent — one message, N Agent calls (one per lens)
Agent({subagent_type: "general-purpose", description: "...", prompt: "<lens 1>"})
Agent({subagent_type: "general-purpose", description: "...", prompt: "<lens 2>"})
Agent({subagent_type: "general-purpose", description: "...", prompt: "<lens N>"})

# ❌ Sequential — each call in its own message, blocks on the prior
Agent({...lens 1...})    # message 1
# (wait for lens 1 to return)
Agent({...lens 2...})    # message 2
```

A **targeted re-seed** round (re-dispatching only the lens(es) whose
re-seeded gap changed) issues fewer `Agent` calls, but the same
same-message-concurrency rule applies when more than one lens is
re-dispatched together. A full panel round re-dispatches all 5 fixed
lenses (plus the conditional `docs/loom/PRINCIPLES.md` lens, when
present) in one message.
