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

**Verified 2026-07-05 (autonomy claim re-verified live 2026-07-06), mixed evidence grain (see breakdown)**: Codex's real subagent primitive is the `multi_agent` feature — not the previously-guessed `Agent(subagent_type, prompt)`-shaped call.

- ✓ **live-exercised**: `codex features list` on a local Codex 0.139.0 install shows `multi_agent  stable  true` — the feature itself is confirmed on and stable, not merely documented.
- **doc-confirmed, verb names only — spawning-authorization is now session-exercised**: the exact verb names (`spawn_agent`, `wait_agent`, `close_agent`), the config toggle shape below, and the `~/.codex/agents/*.toml` shape come from OpenAI's official Codex manual (§Subagents) and a direct `WebFetch` re-fetch/quote-match of `obra/superpowers`'s own `codex-tools.md` (which documents the identical mechanism) — not from actually invoking `spawn_agent`/`wait_agent`/`close_agent` by name in a live Codex session. Treat the verb names as doc-sourced until session-exercised. The **behavioral claim** those same docs made about *when* Codex spawns — previously stated here as "explicit-trigger only" — is corrected below: live probes on 2026-07-06 showed model-initiated spawning with no per-spawn approval (see "Explicit-trigger claim corrected" below).

If a Codex install has `multi_agent` disabled, enable it explicitly:

```toml
# ~/.codex/config.toml
[features]
multi_agent = true
```

Architectural differences from Claude Code's `Agent()` tool that matter for re-binding loom-code's skills onto Codex:

- **Explicit-trigger claim corrected (live-verified 2026-07-06).** The manual/superpowers-sourced claim that Codex spawns subagents "only on explicit user instruction" does **not** hold as stated. Live probes on codex-cli 0.139.0 (`multi_agent` stable + on, via `codex exec`) showed **model-initiated spawning** — the model itself decided to spawn, with no per-spawn user approval — from two setups: (a) a plain prompt instruction telling the model to delegate a sub-task, and (b) an AGENTS.md standing delegation instruction paired with a delegation-free prompt (the prompt itself never mentioned spawning; the model spawned off the standing instruction alone). Probe recipe (dated provenance, reproducible) — setup (a): `codex exec` a prompt that instructs delegation; setup (b): write an AGENTS.md delegation directive + send a delegation-free prompt; both: observe `collab:`-prefixed events in the transcript confirming a spawn occurred. **Not yet exercised**: interactive mode — only `codex exec` (non-interactive) was probed; do not assume the same holds there without a fresh probe. A loom-code skill that instructs an autonomous dispatch now has a live-verified Codex path via a standing AGENTS.md directive; framing the request as an explicit per-dispatch spawn instruction (the old workaround) still works too, but is no longer the only route.
- **No blocking/non-blocking toggle.** Codex's own runtime automatically waits for and consolidates all subagent results — there is no per-call parameter that flips a dispatch between blocking and mailbox-style async. This is why [environment-gotchas §A1](environment-gotchas.md) (Claude Code's `name:`-triggers-mailbox-semantics pitfall) is scoped Claude-Code-only: three explicit verbs (spawn/wait/close), not one overloaded call with an easy-to-miss extra parameter, structurally rules out that specific failure mode on Codex.
- **`name` means something different.** Custom agent *identity* in Codex lives in TOML files under `~/.codex/agents/` (`name` / `description` / `developer_instructions` required fields) — a reusable, session-level profile roughly analogous to Claude Code's `subagent_type`, not a per-dispatch ephemeral tracking label.
- **No plugin-bundled agent definitions.** Codex's plugin manifest schema has no field for shipping reusable custom-agent definitions alongside a plugin (only `skills`). loom-code's `agents/*.md` role-prompt files (`implementer.md`, `spec-reviewer.md`, `code-quality-reviewer.md`, `code-reviewer.md`) still have **no confirmed Codex-native equivalent** — this remains an open gap. See [`loom-code/research/2026-07-05-claude-code-codex-dual-compat-patterns.md`](../../../research/2026-07-05-claude-code-codex-dual-compat-patterns.md) for the full survey.

The agent prompts in `loom-code/agents/*.md` are plain Markdown specifically so they re-bind cleanly to whatever the actual Codex dispatch surface is — that design intent holds, but the target primitive is now known to be `spawn_agent`/`wait_agent`/`close_agent`, not a guessed `Agent(subagent_type, prompt)`-shaped call. (Path corrected 2026-07-05: these role-prompt files live at `loom-code/agents/*.md`, not the pre-P15-12 `skills/subagent-driven-development/agents/*.md` path this section previously named.)

### Re-binding loom-code's dispatch points onto Codex (doc-sourced, not session-exercised)

Where a loom-code SKILL.md says "dispatch a `<role>` subagent" (e.g. `subagent-driven-development`'s implementer / spec-reviewer / code-quality-reviewer, or `requesting-code-review`'s code-reviewer panel), the Codex-side equivalent is: `spawn_agent` with the corresponding `loom-code/agents/<role>.md` content as the agent's instructions, then `wait_agent` for its result, then `close_agent` when done (per `subagent-driven-development`'s own guidance to close implementer/reviewer subagents once finished). Live probes now show Codex can spawn autonomously off a standing AGENTS.md directive (see "Explicit-trigger claim corrected" above), so the orchestrator has two live-verified routes: an explicit per-dispatch spawn instruction ("spawn an implementer agent for task N using `loom-code/agents/implementer.md`'s instructions") — the more session-exercised of the two, still the safer default — or a standing AGENTS.md delegation directive that lets the model decide to spawn without restating the instruction each time. Either way, `wait_agent` + `close_agent` follow the same as before.

### Panel dispatch mapping — `requesting-code-review`'s 2-reviewer panel (v0.26.0+) (shape derived from the 2026-07-06 probes; not yet session-exercised as a panel)

`requesting-code-review` dispatches a **panel of two** `code-reviewer` agents per its SKILL.md §Process Steps 2-3 (evidence: `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`). On Codex, the natural mapping is **one spawn instruction naming both agents**: "spawn two code-reviewer agents using `loom-code/agents/code-reviewer.md`'s instructions, byte-identical prompts, review branch diff `<range>`" — this is exactly `multi_agent`'s own "spawn one agent per point, wait for all" pattern (§Parallel fan-out below), which natively covers the 2-agent case. `wait_agent` for both results; unioning the findings and re-running the aggregation rule (per the SKILL.md) is orchestrator-side logic, identical on both hosts.

### Parallel fan-out (`dispatching-parallel-agents`) (doc-sourced, not session-exercised)

Codex's `multi_agent` feature natively supports the same "spawn N, wait for all, consolidate" shape `dispatching-parallel-agents` calls for — this is literally the manual's own worked example: *"Spawn one agent per point, wait for all of them, and summarize the result for each point."* Unlike Claude Code (where concurrency depends on issuing multiple `Agent` calls in the same assistant message), Codex's own runtime handles the waiting and consolidation automatically once the spawn instruction names multiple agents/points.

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
