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

## Immutable review-context adapter

Before any loom review station dispatches reviewers, set
`loaded_reference_path` to the loaded `codex-tools.md` absolute path and derive
the installed `loom-code` plugin root from that path alone:

```sh
case "$loaded_reference_path" in
  /*) ;;
  *)
    echo "loaded_reference_path must be absolute" >&2
    exit 1
    ;;
esac
if [ -L "$loaded_reference_path" ] || [ ! -f "$loaded_reference_path" ] || \
   [ "$(basename "$loaded_reference_path")" != "codex-tools.md" ]; then
  echo "loaded reference must be the codex-tools.md regular file" >&2
  exit 1
fi
canonical_reference="$(cd "$(dirname "$loaded_reference_path")" && pwd -P)/$(basename "$loaded_reference_path")"
plugin_root="$(cd "$(dirname "$canonical_reference")/../../.." && pwd -P)"
expected_reference="$plugin_root/skills/using-loom-code/references/codex-tools.md"
if [ "$canonical_reference" != "$expected_reference" ]; then
  echo "loaded reference must match the installed loom-code reference layout" >&2
  exit 1
fi
test -f "$plugin_root/scripts/review_context.py" || {
  echo "review_context.py is absent from the loaded plugin" >&2
  exit 1
}
```

The adapter validates that source before deriving `plugin_root`: it must be an
absolute, non-symlink regular `codex-tools.md` file whose canonical location
is exactly `skills/using-loom-code/references/codex-tools.md` under the
derived root. A same-named foreign file is not an installed loom-code
reference. The adapter must not infer the root from a cache, marketplace, or
consumer path. It must not use the current working directory as a fallback.
The loaded reference is the authority; the derived root is not the target
repository or working directory. If the layout or script is absent, refuse the
review. It then runs the common resolver once:

```
python3 <installed-plugin-root>/scripts/review_context.py --repo <target_repo>
```

The adapter must forward the resulting JSON packet verbatim to every downstream
station and reviewer. A downstream consumer must not derive, replace, or merge
packet fields: `target_repo`, `reviewed_sha`, `plugin_version`, and the
approved absolute `resources` paths remain exactly the resolver's output. The
same command is used for every direct review entry; an upstream station hands
its already-resolved packet to a delegate unchanged instead of resolving a
replacement packet.

After a docs fix, assemble the post-fix confirmation packet specified by the
binding [`convergence contract`](../../requesting-docs-review/references/convergence-contract.md):
the complete immutable context, original gating findings, and delta evidence.
Resolve its post-fix SHA, then dispatch a labelled `fresh whole-artifact review
(Codex)` using that complete packet. This is a new review of the entire changed
artifact set; do not represent this as a `SendMessage` continuation. The fresh reviewer returns its
ordinary verdict under that packet and echoes that fresh packet's `reviewed_sha`, which must
differ from the initial packet's `reviewed_sha`; otherwise reject the result.
The orchestrator, not the fresh reviewer, maps that ordinary verdict to
`CONFIRMED_RESOLVED` or `STILL_BLOCKING` under the convergence contract. Only
that mapped result may feed the current-SHA terminal verdict or marker path.

## Subagent dispatch

Per TECH-SPEC §3.3-3.4, loom-code's `subagent-driven-development` skill dispatches three subagents per atomic task (implementer / spec-reviewer / code-quality-reviewer).

**Verified 2026-07-05 (autonomy claim re-verified live 2026-07-06), mixed evidence grain (see breakdown)**: Codex's real subagent primitive is the `multi_agent` feature — not the previously-guessed `Agent(subagent_type, prompt)`-shaped call.

- ✓ **live-exercised**: `codex features list` on a local Codex 0.139.0 install shows `multi_agent  stable  true` — the feature itself is confirmed on and stable, not merely documented.
- **doc-confirmed, verb names only — spawning authorization is now session-exercised**: the exact `spawn_agent` and `wait_agent` verb names, the config toggle shape below, and the `~/.codex/agents/*.toml` shape come from OpenAI's official Codex manual (§Subagents) and a direct `WebFetch` re-fetch/quote-match of `obra/superpowers`'s own `codex-tools.md` — not from actually invoking those verbs by name in a live Codex session. Treat the verb names as doc-sourced until session-exercised. The **behavioral claim** those same docs made about *when* Codex spawns — previously stated here as "explicit-trigger only" — is corrected below: live probes on 2026-07-06 showed model-initiated spawning with no per-spawn approval (see "Explicit-trigger claim corrected" below).

If a Codex install has `multi_agent` disabled, enable it explicitly:

```toml
# ~/.codex/config.toml
[features]
multi_agent = true
```

Architectural differences from Claude Code's `Agent()` tool that matter for re-binding loom-code's skills onto Codex:

- **Explicit-trigger claim corrected (live-verified 2026-07-06).** The manual/superpowers-sourced claim that Codex spawns subagents "only on explicit user instruction" does **not** hold as stated. Live probes on codex-cli 0.139.0 (`multi_agent` stable + on, via `codex exec`) showed **model-initiated spawning** — the model itself decided to spawn, with no per-spawn user approval — from two setups: (a) a plain prompt instruction telling the model to delegate a sub-task, and (b) an AGENTS.md standing delegation instruction paired with a delegation-free prompt (the prompt itself never mentioned spawning; the model spawned off the standing instruction alone). Probe recipe (dated provenance, reproducible) — setup (a): `codex exec` a prompt that instructs delegation; setup (b): write an AGENTS.md delegation directive + send a delegation-free prompt; both: observe `collab:`-prefixed events in the transcript confirming a spawn occurred. **Not yet exercised**: interactive mode — only `codex exec` (non-interactive) was probed; do not assume the same holds there without a fresh probe. A loom-code skill that instructs an autonomous dispatch now has a live-verified Codex path via a standing AGENTS.md directive; framing the request as an explicit per-dispatch spawn instruction (the old workaround) still works too, but is no longer the only route.
- **Explicit lifecycle.** Each `spawn_agent` call creates one child. The
  orchestrator collects its result with `wait_agent`; it does not assume that
  a multi-agent instruction is automatically expanded, waited on, or
  consolidated. Codex exposes no `close_agent` operation in this surface, so
  no loom procedure may require one.
- **`name` means something different.** Custom agent *identity* in Codex lives in TOML files under `~/.codex/agents/` (`name` / `description` / `developer_instructions` required fields) — a reusable, session-level profile roughly analogous to Claude Code's `subagent_type`, not a per-dispatch ephemeral tracking label.
- **No plugin-bundled agent definitions.** Codex's plugin manifest schema has no field for shipping reusable custom-agent definitions alongside a plugin (only `skills`). loom-code's `agents/*.md` role-prompt files (`implementer.md`, `spec-reviewer.md`, `code-quality-reviewer.md`, `code-reviewer.md`, `docs-reviewer.md` — five files) still have **no confirmed Codex-native equivalent** — this remains an open gap. See [`loom-code/research/2026-07-05-claude-code-codex-dual-compat-patterns.md`](../../../research/2026-07-05-claude-code-codex-dual-compat-patterns.md) for the full survey.
- **No mailbox/SendMessage confirmation primitive.** Claude Code's delta-confirmation mechanism (`requesting-docs-review` Directive 2) addresses an unnamed agent's dispatch handle via `SendMessage` to resume it in-session — Codex has no equivalent primitive. On Codex, give the labelled fresh whole-artifact reviewer the complete post-fix confirmation packet, then let the orchestrator normalize its ordinary verdict under the [convergence contract](../../requesting-docs-review/references/convergence-contract.md).

The public role prompts are `loom-code/agents/implementer.md`,
`loom-code/agents/spec-reviewer.md`, `loom-code/agents/code-quality-reviewer.md`,
`loom-code/agents/code-reviewer.md`, and `loom-code/agents/docs-reviewer.md`.
They are plain Markdown so they re-bind cleanly to the actual Codex dispatch
surface. The target primitives are `spawn_agent` and `wait_agent`, not a guessed
`Agent(subagent_type, prompt)`-shaped call.

### Re-binding loom-code's dispatch points onto Codex (doc-sourced, not session-exercised)

Where a loom-code SKILL.md says "dispatch a `<role>` subagent" (e.g.
`subagent-driven-development`'s implementer / spec-reviewer /
code-quality-reviewer, or `requesting-code-review`'s code-reviewer panel),
resolve the portable profile first. The public logical identities are
`loom-code/agents/<role>.md`; their runtime files must come from the installed
root derived above, never a consumer checkout or the current working directory:

```sh
implementer_prompt="$plugin_root/agents/implementer.md"
spec_reviewer_prompt="$plugin_root/agents/spec-reviewer.md"
code_quality_reviewer_prompt="$plugin_root/agents/code-quality-reviewer.md"
code_reviewer_prompt="$plugin_root/agents/code-reviewer.md"
docs_reviewer_prompt="$plugin_root/agents/docs-reviewer.md"
for role_prompt in "$implementer_prompt" "$spec_reviewer_prompt" \
  "$code_quality_reviewer_prompt" "$code_reviewer_prompt" "$docs_reviewer_prompt"; do
  test -f "$role_prompt" || {
    echo "reviewer prompt is absent from the installed plugin: $role_prompt" >&2
    exit 1
  }
done
```

The Codex-side equivalent is one `spawn_agent` call per role with the matching
runtime prompt above as its instructions and the profile's translated `model`
and `reasoning_effort`; then use `wait_agent` to collect every child result and
consolidate in the orchestrator. Live probes now show Codex can spawn
autonomously off a standing AGENTS.md directive (see "Explicit-trigger claim
corrected" above), so the orchestrator has two live-verified routes: an
explicit per-dispatch spawn instruction — the safer default — or a standing
AGENTS.md delegation directive that lets the model decide to spawn without
restating the instruction each time.

### Portable per-subagent model selection

**Current loom path.** Resolve [`dispatch-profile.md`](dispatch-profile.md)
before every `spawn_agent` call, then pass its host-translated `model` and
`reasoning_effort` directly to that call. The profile is shared with Claude
Code and carries the tier floor plus bounded-fallback rule. Use the current
tool schema's advertised model enum at dispatch time; do not copy a product
name into a loom skill.

`.codex/agents/*.toml` role files are **not the loom dispatch mechanism**.
They may remain as a user's independent Codex configuration, but a loom
dispatch must use the generic role-prompt path when such a role could override
the requested model or effort. A conflict is reported, never silently
resolved by inheriting the parent model.

### Existing Codex role files

An existing `.codex/agents/*.toml` role file is user configuration, not a
loom dispatch input. Detect a conflict with its requested model or effort and
report it; do not inherit, override, or document a TOML fallback here.

### Panel dispatch mapping — `requesting-code-review`'s 2-reviewer panel (v0.26.0+) (shape derived from the 2026-07-06 probes; not yet session-exercised as a panel)

`requesting-code-review` dispatches a **panel of two** `code-reviewer` agents per its SKILL.md §Process Steps 2-3 (evidence: `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`). On Codex, resolve the profile once, issue **two separate** `spawn_agent` calls with byte-identical prompts, then `wait_agent` for both results. Unioning the findings and re-running the aggregation rule (per the SKILL.md) is orchestrator-side logic, identical on both hosts.

### Parallel fan-out (`dispatching-parallel-agents`) (doc-sourced, not session-exercised)

Codex's `multi_agent` feature supports the same "spawn N, wait for all,
consolidate" shape `dispatching-parallel-agents` calls for. Issue one
`spawn_agent` call per independent point, wait explicitly for every result,
and summarize the set in the orchestrator.

## File operations

**Assumed (not exercised in this test)**: exact tool names. Codex likely exposes Read / Write / Edit primitives with names similar to but possibly different from Claude Code's:

| Operation | Claude Code | Codex (expected) |
|---|---|---|
| Read file | `Read(file_path)` | `Read(path)` or `read_file(path)` — assumed |
| Create / overwrite | `Write(file_path, content)` | `Write(path, contents)` or `write_file(...)` — assumed |
| Edit in place | `Edit(file_path, old, new)` | `Edit(path, old_str, new_str)` or `edit_file(...)` — assumed |
| List directory | `ls` via Bash | likely a `list_dir` or Bash — assumed |
| Find files | `Glob(pattern)` / `Grep` via Bash | assumed |

The public role prompts in `loom-code/agents/*.md` use the abstract phrasing
*"Read the file"* / *"Write to the file"* — not literal Claude Code tool
names — so they transcribe to whatever Codex primitives are available.

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
