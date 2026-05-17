# Claude Code — tool name canonical reference

> Sourced from Claude Code v2 tool surface. Used by `using-code-toolkit` to keep skill prompts portable across versions.

## Skill invocation

```
Skill(skill: "<skill-name>")          # e.g. Skill(skill: "tdd-iron-law")
Skill(skill: "<plugin>:<skill-name>") # plugin-scoped — Skill(skill: "dev-workflow:git-memory")
```

Plugin-scoped form is required when invoking skills from a different plugin (e.g. delegations to `dev-workflow:*` from `code-toolkit:*`).

## Subagent dispatch

```
Agent(
  subagent_type: "<type>",
  description: "<3-5 word task>",
  prompt: "<self-contained task — agent has no prior context>"
)
```

Available `subagent_type` values vary by host configuration; common ones surface in the system prompt at startup. code-toolkit ships 4 plugin-level agents (v0.6.0+) — dispatch via `subagent_type: "code-toolkit:<role>"`:

- `code-toolkit:implementer` — SDD worker
- `code-toolkit:spec-reviewer` — SDD per-task spec evaluator
- `code-toolkit:code-quality-reviewer` — SDD per-task quality evaluator
- `code-toolkit:code-reviewer` — whole-branch evaluator (requesting-code-review)

Role contracts live at `code-toolkit/agents/<role>.md`. Each agent carries the 12-rule engineering baseline ([`code-toolkit/scripts/_baseline.md`](../../../scripts/_baseline.md)) baked into its system prompt.

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
