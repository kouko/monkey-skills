# Codex CLI — tool name mapping

> **Phase**: v0.4.0 — Codex CLI build complete; verification ritual pending Codex CLI install (see [`../../tests/codex-cli/README.md`](../../tests/codex-cli/README.md)).
>
> **Authoritative reference**: this file mirrors what we know about Codex CLI's plugin / tool surface as of the v0.4.0 build. Items marked **⚠️ TBD verify** require Codex CLI install + live test to confirm; until then they are best-effort based on the Codex CLI plugin spec, observed Superpowers v5.1.0 dual-harness layout, and the schema in this plugin's `.codex-plugin/plugin.json` `interface` block.

## Skill invocation in Codex CLI

Codex CLI plugin spec uses **slash-command syntax** for skill invocation (one-to-one with Codex CLI's built-in skill resolution):

```
/skill-name
/plugin:skill-name    # plugin-scoped (when same skill name exists in multiple plugins)
```

For `code-toolkit`'s 11 skills:

| Skill | Codex CLI invocation |
|---|---|
| using-code-toolkit | `/using-code-toolkit` (also auto-injected via SessionStart hook) |
| brainstorming | `/brainstorming` |
| writing-plans | `/writing-plans` |
| subagent-driven-development | `/subagent-driven-development` |
| tdd-iron-law | `/tdd-iron-law` |
| systematic-debugging | `/systematic-debugging` |
| requesting-code-review | `/requesting-code-review` |
| verification-before-completion | `/verification-before-completion` |
| finishing-a-development-branch | `/finishing-a-development-branch` |
| using-git-worktrees | `/using-git-worktrees` |
| dispatching-parallel-agents | `/dispatching-parallel-agents` |

If skill-name conflicts with another installed plugin (e.g. `obra/superpowers` ships `/brainstorming` too), use plugin-scoped form: `/code-toolkit:brainstorming`.

**⚠️ TBD verify**: slash-form is the standard plugin-skill invocation; auto-discovery via description-text classification (the mechanism Claude Code uses) **may or may not** work identically in Codex CLI. The hook injection covers the router (always-on context) regardless; specialist skills load via either slash command OR description-match-on-prompt.

## Hook output shape — already Codex-compatible

`hooks/session-start` (Claude Code spec was the original target) emits a JSON object with three top-level keys for portability:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<router content>"
  },
  "additional_context": "<same router content>",  // ← Codex CLI consumes this
  "additionalContext": "<same router content>"    // ← legacy / mixed shape fallback
}
```

The Codex CLI key is `additional_context` (snake_case, top-level). Already emitted by the existing hook script — no Codex-specific adapter needed.

**⚠️ TBD verify**: the exact key name + nesting Codex CLI expects. The triple-key shape is a "shotgun" pattern that should hit ANY of the plausible Codex CLI shapes; verify by running `test-hook-injection.sh` after install.

## Subagent dispatch

Per TECH-SPEC §3.3-3.4, code-toolkit's `subagent-driven-development` skill dispatches three subagents per atomic task (implementer / spec-reviewer / code-quality-reviewer). The dispatch mechanism in Codex CLI:

**⚠️ TBD verify**: Codex CLI's agent-dispatch surface. Options based on Codex CLI architecture:

| Option | Pattern | Status |
|---|---|---|
| (a) Codex CLI's `Task` / `Agent` tool | Equivalent to Claude Code's `Agent(subagent_type: ..., prompt: ...)` | most likely shape |
| (b) Slash-command shell | `/dispatch <prompt-file>` | possible if Codex uses slash for everything |
| (c) Direct subprocess | Spawn Codex CLI with prompt arg | fallback if no native dispatch |

The agent prompts in `skills/subagent-driven-development/agents/*.md` are written in plain Markdown specifically so they re-bind cleanly to whatever the actual Codex CLI dispatch surface is. The orchestrator (parent agent) reads the prompt + substitutes `{…}` placeholders + invokes Codex's dispatch primitive.

## File operations

**⚠️ TBD verify**: exact tool names. Codex CLI likely exposes Read / Write / Edit primitives with names similar to but possibly different from Claude Code's:

| Operation | Claude Code | Codex CLI (expected) |
|---|---|---|
| Read file | `Read(file_path)` | `Read(path)` or `read_file(path)` — **TBD** |
| Create / overwrite | `Write(file_path, content)` | `Write(path, contents)` or `write_file(...)` — **TBD** |
| Edit in place | `Edit(file_path, old, new)` | `Edit(path, old_str, new_str)` or `edit_file(...)` — **TBD** |
| List directory | `ls` via Bash | likely Codex has a `list_dir` or uses Bash too — **TBD** |
| Find files | `Glob(pattern)` / `Grep` via Bash | **TBD** |

The skill prompts in `skills/subagent-driven-development/agents/*.md` use the abstract phrasing *"Read the file"* / *"Write to the file"* — not the literal Claude Code tool names — so they transcribe to whatever Codex CLI's primitives are without modification.

## Shell

Codex CLI almost certainly exposes a shell-equivalent (Codex's whole pitch is "agent that runs commands"). Likely named:

- `bash(cmd)` / `Bash(cmd)` — most likely
- `shell(cmd)` — possible alternative
- `exec(cmd)` — less likely

**⚠️ TBD verify** at install time.

## CLAUDE.md ≡ AGENTS.md (or similar)

Claude Code reads `CLAUDE.md` for project conventions. Codex CLI reads its own equivalent — typically `AGENTS.md` or similar. The skill bodies in code-toolkit reference `CLAUDE.md` (because it's the original target); Codex CLI users should mirror their `CLAUDE.md` to `AGENTS.md` (or whatever the Codex convention is) for the rules to apply.

**⚠️ TBD verify**: the exact filename Codex CLI looks for. Some plugins ship both `CLAUDE.md` + `AGENTS.md` symlinked / duplicated.

## What the hook injection covers (harness-independent)

Regardless of which Codex CLI surface details turn out to be — the SessionStart hook injection IS the load-bearing mechanism for the router-charter pattern. The hook's JSON output is consumed by the host harness BEFORE any tool surface is exposed to the agent:

- Claude Code consumes `hookSpecificOutput.additionalContext` → the router rules + Skill Priority table land in agent system prompt
- Codex CLI consumes `additional_context` → same content lands in agent system prompt
- Either way: the agent boots with the 4 router rules (Brainstorm / TDD / SDD / Never push without review) + Skill Priority table loaded

So the hook is the safety net even if specialist skill invocation tool names differ — the router self-describes its own behavior + skill names, so the agent can adapt.

## Verification — what to test when Codex CLI installs

Run `tests/codex-cli/test-skill-loading.sh` + `tests/codex-cli/test-hook-injection.sh` (see `tests/codex-cli/README.md` for full procedure). Expected:

1. Plugin installs cleanly via Codex CLI plugin install command (TBD exact syntax)
2. `codex plugin details code-toolkit` (TBD command) lists 11 skills
3. SessionStart hook fires on fresh session; router context appears in agent's first prompt
4. `/tdd-iron-law` (or however Codex CLI invokes skills) loads the skill body
5. Run one TDD-pressure prompt (e.g. `tests/tdd-iron-law-pressure/prompts/skip-just-this-once.txt`) → agent refuses + cites Beck 2002

Any TBD-marked item that fails verification → update this file with the actual Codex CLI surface name + fix the affected skill body / agent prompt.

## See also

- [`../../tests/codex-cli/README.md`](../../tests/codex-cli/README.md) — verification procedure for when Codex CLI installs.
- [`../../.codex-plugin/plugin.json`](../../.codex-plugin/plugin.json) — Codex CLI manifest.
- [`../../hooks/session-start`](../../hooks/session-start) — bash; portable JSON output covers both Claude Code + Codex CLI key conventions.
- [`claude-code-tools.md`](claude-code-tools.md) — Claude Code canonical tool names (verified; v0.1.0+).
- [`../../TECH-SPEC.md`](../../TECH-SPEC.md) §2.3 — hook mechanism design that drives the portable JSON output.
- `obra/superpowers` v5.1.0 — Codex CLI plugin reference implementation (this plugin's `interface` block schema mirrors it).
