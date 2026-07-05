# Claude Code — tool name reference for `translation-toolkit`

> All 5 active specialist skills (`translation-i18n`, `translation-doc`,
> `translation-creative`, `translation-novel`, `translation-audit`)
> phrase subagent dispatch in host-neutral prose ("subagent dispatches
> a blind v2 → source retranslation", "dispatches one fresh-context
> EXTRACTOR subagent", "no isolation capability"). This file is the
> concrete Claude Code call shape that prose resolves to.

## S1 back-translation gate (all 5 skills)

```
Agent({
  subagent_type: "general-purpose",
  description: "back-translation check",
  prompt: "<BACK-TRANSLATOR role prompt: blind v2 → source-language
            retranslation, no access to the original source>"
})
```

- **Blind** means the subagent's prompt must NOT include the original
  source text — only the v2 target-language output to retranslate.
  Leaking the source defeats the gate's purpose (it becomes a
  round-trip check, not an independent-retranslation check).
- **Detecting "no isolation capability"** (the condition that makes S1
  skip with the `S1: SKIPPED (no isolation capability)` audit-trail
  flag): on Claude Code this means no `Agent` tool is available to the
  current agent (a plain in-context worker with no subagent access).
- **Do not add `name:`** to this dispatch — see
  `loom-code/skills/using-loom-code/references/environment-gotchas.md`
  §A1: naming turns the one-shot blocking call into a persistent
  mailbox-semantics teammate whose output is never delivered.

## `translation-novel`'s per-chapter EXTRACTOR dispatch

```
Agent({
  subagent_type: "general-purpose",
  model: <resolve_model_for_role(model, 'extractor')>,
  description: "extract chapter glossary",
  prompt: "<canonical extractor prompt + intake-spec + accumulated
            state from prior chapters + current chapter text>"
})
```

One dispatch per chapter, fresh context each time — no cross-chapter
conversation memory; the accumulated state JSON is the only carry-over
channel between dispatches.

**Model-string caution**: `references/orthogonal-axes.md` §Model
routing documents literal ids like `claude-haiku-4-5` in the toolkit's
own `model:` config field. Whether Claude Code's `Agent()` call needs
that literal id or the harness-level alias (`"haiku"`) is a per-harness
detail — `dev-workflow:distill-sessions` hit exactly this gap
(`references/claude-code-tools.md` there: the literal model id fails
`Agent()`'s enum validation; only the alias works). Verify which form
`resolve_model_for_role` ultimately hands to the dispatch call before
relying on it un-inspected.
