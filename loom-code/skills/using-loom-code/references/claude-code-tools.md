# Claude Code — tool name canonical reference

> Sourced from Claude Code v2 tool surface. Used by `using-loom-code` to keep skill prompts portable across versions.

## Skill invocation

```
Skill(skill: "<skill-name>")          # e.g. Skill(skill: "tdd-iron-law")
Skill(skill: "<plugin>:<skill-name>") # plugin-scoped — Skill(skill: "dev-workflow:git-memory")
```

Plugin-scoped form is required when invoking skills from a different plugin (e.g. delegations to `dev-workflow:*` from `loom-code:*`).

## Subagent dispatch

```
Agent(
  subagent_type: "<type>",
  description: "<3-5 word task>",
  prompt: "<self-contained task — agent has no prior context>"
)
```

This is the concrete call shape every loom-code skill's host-neutral "dispatch a subagent" prose resolves to on Claude Code. **Do not add `name:`** to a loom-code dispatch — see [environment-gotchas](environment-gotchas.md) §A1: naming turns this one-shot blocking call into a persistent mailbox-semantics teammate whose output is never delivered (only `SendMessage` retrieves it). `description:` is unrelated and always required regardless.

**An UNNAMED dispatch is still addressable after it returns.** The `Agent` spawn result carries a handle/agent-id for the dispatched agent even when no `name:` was passed; `SendMessage` to that handle resumes the SAME agent from its own transcript — no `name:` needed. This is the mechanism `requesting-docs-review`'s delta-confirmation duty relies on: the orchestrator addresses the round-1 reviewer by the handle its dispatch returned, not by a teammate name. The no-`name:` rule and §A1's undelivered-reply caveat are scoped to NAMED teammate dispatches; they do not apply to `SendMessage`-driven resumption of an unnamed agent's handle.

Available `subagent_type` values vary by host configuration; common ones surface in the system prompt at startup. loom-code ships 5 plugin-level agents (four since v0.6.0; docs-reviewer since v0.42.0) — dispatch via `subagent_type: "loom-code:<role>"`:

- `loom-code:implementer` — SDD worker
- `loom-code:spec-reviewer` — SDD per-task spec evaluator
- `loom-code:code-quality-reviewer` — SDD per-task quality evaluator
- `loom-code:code-reviewer` — whole-branch evaluator (requesting-code-review)
- `loom-code:docs-reviewer` — whole-artifact prose evaluator (requesting-docs-review)

Role contracts live at `loom-code/agents/<role>.md`. Each agent carries the 12-rule engineering baseline ([`loom-code/scripts/_baseline.md`](../../../scripts/_baseline.md)) baked into its system prompt. Reviewer agents may also carry a `model:` frontmatter key that sets their host-native default; a dispatch-time `model` param on the `Agent` call takes precedence over the frontmatter default — by loom convention, used only to upgrade the tier.

### Parallel fan-out (`dispatching-parallel-agents`)

Claude Code runs `Agent` calls concurrently **only when they appear in the same assistant message**. Sequential calls across separate messages run sequentially:

```
# ✅ Concurrent — one message, multiple Agent calls
Agent({subagent_type: "loom-code:implementer", description: "...", prompt: "<domain A task body>"})
Agent({subagent_type: "loom-code:implementer", description: "...", prompt: "<domain B task body>"})
Agent({subagent_type: "loom-code:implementer", description: "...", prompt: "<domain C task body>"})

# ❌ Sequential — each Agent call in its own message, blocks on the prior
Agent({...A...})    # message 1
# (wait for A to return)
Agent({...B...})    # message 2
```

## File operations

| Operation | Tool | Notes |
|---|---|---|
| Read file | `Read(file_path: "<absolute>")` | Absolute paths only. |
| Create / overwrite | `Write(file_path, content)` | Read first if file exists. |
| Edit in place | `Edit(file_path, old_string, new_string)` | `old_string` must be unique unless `replace_all: true`. |

## Shell

```
Bash(command: "<cmd>", description: "<short description>")
```

Note that the bash environment persists working-directory state between calls but not shell state (env exports / aliases).

## Other surfaces (deferred / optional)

- `WebFetch` / `WebSearch` — for online lookups.
- `Glob` / `Grep` — for file/pattern search.
- `TaskCreate` / `TaskUpdate` / `TaskList` — for progress tracking when multi-step.

Refer to the host's deferred-tools list (surfaced in `<system-reminder>` blocks) for the full enumeration.
