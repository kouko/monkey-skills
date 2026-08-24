# Claude Code — tool name canonical reference

> Sourced from Claude Code v2 tool surface. Used by `using-loom-code` to keep skill prompts portable across versions.

## Skill invocation

```
Skill(skill: "<skill-name>")          # e.g. Skill(skill: "tdd-iron-law")
Skill(skill: "<plugin>:<skill-name>") # plugin-scoped — Skill(skill: "loom-workflow:git-memory")
```

Plugin-scoped form is required when invoking skills from a different plugin (e.g. delegations to `loom-workflow:*` from `loom-code:*`).

## Review-context adapter

Before a Claude Code review station dispatches a panel, resolve the common
review context from this **installed plugin root**, once per review attempt.
The root derives from the absolute path of the loaded reference file:

1. Start from that absolute path and walk upward until the directory named
   `loom-code`; assign it to `derived_plugin_root`. If no such directory is
   found, REFUSE the review attempt. Resolve `derived_plugin_root` to its
   canonical absolute path before any comparison.
2. `CLAUDE_PLUGIN_ROOT` is a cross-check only, never a path source. If
   `CLAUDE_PLUGIN_ROOT` is missing or differs from `derived_plugin_root`,
   REFUSE the review attempt. Canonicalize `CLAUDE_PLUGIN_ROOT` to an absolute
   path, then compare the two canonical absolute paths.
3. Use only `derived_plugin_root` for every plugin-local command:

```
python3 "${derived_plugin_root}/scripts/review_context.py" --repo <target_repo>
```

Do not infer it from a cache layout, the working directory, or the consumer
repository. The script emits one
unchanged immutable context packet containing `target_repo`, `reviewed_sha`,
`plugin_version`, and `resources`. Do not derive plugin paths from
`target_repo`, the working directory, or an assumed source checkout.

Copy the packet verbatim into every downstream station and reviewer prompt.
When an upstream station already handed down the complete packet, consume it
verbatim rather than resolving another packet; a station must not silently
replace the reviewed SHA or any approved resource path.

### Claude post-fix confirmation

Claude Code's `SendMessage` continuation may be used only for the same
reviewer that raised a docs finding. After a fix, first resolve or receive a
fresh immutable context packet for the fresh post-fix SHA, not the pre-fix
`reviewed_sha`. Send that same reviewer the complete post-fix confirmation
packet — immutable context, original gating findings, and delta evidence —
tied to the fresh packet. The reviewer returns only its ordinary three-valued
verdict and echoes the fresh packet `reviewed_sha`; the orchestrator maps that
ordinary verdict to `CONFIRMED_RESOLVED` or `STILL_BLOCKING` under the binding
convergence contract.

Record the initial round `reviewed_sha` before dispatching the first reviewer.
If the post-fix packet `reviewed_sha` equals the initial round `reviewed_sha`,
REFUSE confirmation: do not create a wrapper verdict and do not mint a marker.
Commit the fix, resolve a genuinely new packet, then restart the confirmation
sequence.

The confirmation is terminal evidence only when its echoed SHA equals the
fresh packet SHA. It is never a pass for the original packet and must not
mint a marker by itself; the calling docs station constructs and validates the
current-packet terminal verdict before any marker operation.

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

Before every spawn, **resolve the dispatch profile** in
[`dispatch-profile.md`](dispatch-profile.md). Translate its semantic tier to
Claude's current family alias, leave per-agent `effort` unset, and record
`requested_effort=<low|medium|high>; effective_effort=inherited` in the
packet. The resolved profile is loom's source of truth for model selection;
Claude applies the main session's effort. If
Claude's policy rejects a `frontier` model request, follow the profile's
fail-loud rule rather than inheriting the parent model.

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
