# Codex CLI — tool name mapping

> **Status**: Verified on Codex 0.139.0, 2026-06-14 (live install + session test).
>
> **Authoritative reference**: this file records `loom-code`'s plugin / tool surface as confirmed against a real Codex 0.139.0 install. The verified command surface, hook contract, and the Codex-specific `description` length constraint are live-tested facts. A small number of items remain marked **assumed** where the live test did not exercise them; those are called out inline.

## Codex constraint — skill `description` ≤ 1024 chars

Codex 0.139.0 **refuses to load** any skill whose `description` frontmatter exceeds 1024 characters, failing with:

```
invalid description: exceeds maximum length of 1024 characters
```

Claude Code has **no such limit**. This is why 2 of `loom-code`'s skills had their `description` trimmed to load under Codex — keep every skill's `description` ≤ 1024 chars to stay dual-harness portable. After the trim, all skills of the set verified at the time (11; `ui-verification` added later, unverified live on Codex) load under Codex 0.139.0.

## Installing the plugin in Codex 0.139.0

Codex uses a **marketplace → plugin** two-step. The command surface below is from `codex plugin --help` / each subcommand's `--help` on 0.139.0; the **exercised-live** subset (✓) was run during the 2026-06-14 ritual, the rest is help-documented but not exercised:

```
# 1. Register a marketplace (local path, owner/repo, or git URL)
codex plugin marketplace add <path|owner/repo|git-url>   # ✓ exercised: `marketplace add .`
codex plugin marketplace list                            # ✓ exercised
codex plugin marketplace remove <name>                   # from --help, not exercised

# 2. Install a plugin from a registered marketplace
codex plugin add <PLUGIN>@<MARKETPLACE>                  # ✓ exercised: `add loom-code@monkey-skills`
codex plugin add <PLUGIN> --marketplace <name>           # equivalent (from `plugin add --help`, not exercised)
codex plugin list                                        # ✓ exercised
codex plugin remove <PLUGIN>                             # ✓ exercised: `remove loom-code@monkey-skills`
```

Codex 0.139.0 has no `install` subcommand under `codex plugin` (use `add`), no `details` subcommand (use `list`), and no scope flag — do not reference any of those. Use `codex plugin list` to confirm an install and `codex plugin marketplace list` to confirm a registered source.

## Skill invocation in Codex 0.139.0

Codex uses **slash-command syntax** for skill invocation:

```
/skill-name
/plugin:skill-name    # plugin-scoped (when same skill name exists in multiple plugins)
```

For `loom-code`'s skills (11 at verification time):

| Skill | Codex invocation |
|---|---|
| using-loom-code | `/using-loom-code` (also injected via SessionStart hook) |
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
| ui-verification | `/ui-verification` (added v0.21.0 — **unverified live on Codex**) |

If a skill name conflicts with another installed plugin (e.g. `obra/superpowers` ships `/brainstorming` too), use the plugin-scoped form: `/loom-code:brainstorming`.

**Verified**: all 11 then-existing skills load from the installed plugin under Codex 0.139.0 (after the `description` trim above). The SessionStart hook injects the router — confirmed, a live session quoted the router banner verbatim.

**Assumed (not exercised in this test)**: auto-discovery via description-text classification (the prompt-match mechanism Claude Code uses). The hook injection covers the router (always-on context) regardless of whether prompt-match works identically; specialist skills load via slash command for certain.

## Hook output shape — Codex 0.139.0 consumes the nested key

**Verified**: Codex 0.139.0 consumes the **nested** `hookSpecificOutput.additionalContext` key — the **same** key Claude Code consumes. A plugin-bundled `hooks/hooks.json` SessionStart hook is honored by Codex 0.139.0.

The hook script emits:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<router content>"
  }
}
```

Both Claude Code and Codex 0.139.0 read `hookSpecificOutput.additionalContext`, so a single emitted shape covers both harnesses — no Codex-specific adapter or alternate key is needed. (Earlier drafts of this doc speculated a top-level `additional_context` snake_case key; that is **not** what Codex 0.139.0 consumes — the nested key is correct.)

## Subagent dispatch

Per TECH-SPEC §3.3-3.4, loom-code's `subagent-driven-development` skill dispatches three subagents per atomic task (implementer / spec-reviewer / code-quality-reviewer).

**Assumed (not exercised in this test)**: Codex's exact agent-dispatch surface. Candidate shapes:

| Option | Pattern | Status |
|---|---|---|
| (a) Codex `Task` / `Agent` tool | Equivalent to Claude Code's `Agent(subagent_type: ..., prompt: ...)` | most likely shape |
| (b) Slash-command shell | `/dispatch <prompt-file>` | possible |
| (c) Direct subprocess | Spawn Codex with a prompt arg | fallback if no native dispatch |

The agent prompts in `skills/subagent-driven-development/agents/*.md` are plain Markdown specifically so they re-bind cleanly to whatever the actual Codex dispatch surface is. The orchestrator (parent agent) reads the prompt, substitutes `{…}` placeholders, and invokes Codex's dispatch primitive.

## File operations

**Assumed (not exercised in this test)**: exact tool names. Codex likely exposes Read / Write / Edit primitives with names similar to but possibly different from Claude Code's:

| Operation | Claude Code | Codex (expected) |
|---|---|---|
| Read file | `Read(file_path)` | `Read(path)` or `read_file(path)` — assumed |
| Create / overwrite | `Write(file_path, content)` | `Write(path, contents)` or `write_file(...)` — assumed |
| Edit in place | `Edit(file_path, old, new)` | `Edit(path, old_str, new_str)` or `edit_file(...)` — assumed |
| List directory | `ls` via Bash | likely a `list_dir` or Bash — assumed |
| Find files | `Glob(pattern)` / `Grep` via Bash | assumed |

The skill prompts in `skills/subagent-driven-development/agents/*.md` use the abstract phrasing *"Read the file"* / *"Write to the file"* — not the literal Claude Code tool names — so they transcribe to whatever Codex's primitives are without modification.

## Shell

Codex exposes a shell-equivalent (Codex's whole pitch is "agent that runs commands"). **Assumed** exact name:

- `bash(cmd)` / `Bash(cmd)` — most likely
- `shell(cmd)` — possible alternative
- `exec(cmd)` — less likely

## CLAUDE.md ≡ AGENTS.md

Claude Code reads `CLAUDE.md` for project conventions; Codex reads `AGENTS.md`. The skill bodies in loom-code reference `CLAUDE.md` (the original target); Codex users should mirror their `CLAUDE.md` to `AGENTS.md` for the rules to apply. Some plugins ship both, symlinked or duplicated. (Exact mirroring requirement **assumed** — not exercised in this test.)

## What the hook injection covers (harness-independent)

The SessionStart hook injection IS the load-bearing mechanism for the router-charter pattern. The hook's JSON output is consumed by the host harness BEFORE any tool surface is exposed to the agent:

- Claude Code consumes `hookSpecificOutput.additionalContext` → the router rules + Skill Priority table land in agent system prompt
- Codex 0.139.0 consumes the **same** `hookSpecificOutput.additionalContext` → same content lands in agent system prompt (verified)
- Either way: the agent boots with the 4 router rules (Brainstorm / TDD / SDD / Never push without review) + Skill Priority table loaded

So the hook is the safety net even if specialist skill invocation tool names differ — the router self-describes its own behavior + skill names, so the agent can adapt.

## See also

- [`../../../tests/codex-cli/README.md`](../../../tests/codex-cli/README.md) — verification procedure.
- [`../../../.codex-plugin/plugin.json`](../../../.codex-plugin/plugin.json) — Codex manifest.
- [`../../../hooks/session-start`](../../../hooks/session-start) — bash; emits the nested `hookSpecificOutput.additionalContext` shape both Claude Code + Codex 0.139.0 consume.
- [`claude-code-tools.md`](claude-code-tools.md) — Claude Code canonical tool names (verified; v0.1.0+).
- [`../../../TECH-SPEC.md`](../../../TECH-SPEC.md) §2.3 — hook mechanism design that drives the portable JSON output.
- `obra/superpowers` v5.1.0 — Codex plugin reference implementation (this plugin's `interface` block schema mirrors it).
