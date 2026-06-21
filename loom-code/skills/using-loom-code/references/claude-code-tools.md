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

Available `subagent_type` values vary by host configuration; common ones surface in the system prompt at startup. loom-code ships 4 plugin-level agents (v0.6.0+) — dispatch via `subagent_type: "loom-code:<role>"`:

- `loom-code:implementer` — SDD worker
- `loom-code:spec-reviewer` — SDD per-task spec evaluator
- `loom-code:code-quality-reviewer` — SDD per-task quality evaluator
- `loom-code:code-reviewer` — whole-branch evaluator (requesting-code-review)

Role contracts live at `loom-code/agents/<role>.md`. Each agent carries the 12-rule engineering baseline ([`loom-code/scripts/_baseline.md`](../../../scripts/_baseline.md)) baked into its system prompt.

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
