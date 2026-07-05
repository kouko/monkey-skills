# Claude Code — subagent dispatch reference

This plugin's skills (`completeness-critic`'s multi-lens panel) phrase
subagent dispatch in host-neutral prose ("dispatch one subagent per lens,
fresh context, general reasoning agent — not bound to any one
harness/tool"). This file is the concrete Claude Code call shape that
prose resolves to.

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
  subagent type for a lens-critic: lens-critique is pure design reasoning
  (reading the draft and reasoning about omissions), and a
  search-restricted subagent's system prompt ("I only locate code, I
  don't reason") can refuse the lens role outright — the panel silently
  loses that lens, which reads as "no gaps in that lens," a false
  negative. On a host whose *default* subagent is a search/explore type,
  override it explicitly for every lens dispatch.
- **Do not add `name:`.** Adding `name:` to this call turns a one-shot
  blocking dispatch into a persistent, addressable "teammate" running on
  mailbox semantics — its output is never delivered as this turn's tool
  result; only an explicit `SendMessage` call retrieves it, and this
  skill's loop-until-dry logic has no step that does this. `description:`
  is unrelated and always required regardless.
- Each lens-critic's prompt carries a distinct adversarial persona and,
  for at least one critic, the original-requirements-only view (not the
  draft) — per the skill's own "multi-lens critic panel" contract.

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
re-dispatched together. A full second panel round re-dispatches all five
fixed lenses (plus the conditional `docs/loom/PRINCIPLES.md` lens, when
present) in one message.
