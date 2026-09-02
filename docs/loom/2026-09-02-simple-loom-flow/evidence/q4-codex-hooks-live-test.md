# Codex CLI hooks — live test (2026-09-02, codex-cli 0.151.0, macOS)

Test repo: scratchpad/codex-hook-test — `.codex/hooks.json` PreToolUse → `.codex/hooks/guard.sh`
(logs raw stdin payload to hook-log.jsonl; exit 2 + stderr when command contains BLOCKME).
Driver: `codex exec -s workspace-write "<prompt>" < /dev/null` (stdin MUST be closed or exec hangs).

| # | config | trust flag | hook ran? | blocked? | note |
|---|---|---|---|---|---|
| A | no matcher | --dangerously-bypass-hook-trust | yes | yes | payload captured |
| B | matcher "Bash" | --dangerously-bypass-hook-trust | yes | yes | stderr surfaced to model: "Command blocked by PreToolUse hook: loom-guard: …" |
| C | matcher "Bash" | (none) | **no** | no | **silent skip — no warning anywhere in exec output** |
| D | matcher "Bash", linked git worktree | --dangerously-bypass-hook-trust | yes | yes | payload cwd = worktree path; no core.hooksPath involvement |

## Payload (PreToolUse) — same shape as Claude Code
session_id, turn_id, transcript_path, cwd, hook_event_name="PreToolUse", model, permission_mode,
tool_name="Bash", tool_input={"command": "..."}, tool_use_id

## Trust persistence
`~/.codex/config.toml`:
```
[hooks.state."<source>:<event_snake>:<i>:<j>"]
trusted_hash = "sha256:<64hex>"
```
Observed keys: `/Users/kouko/.codex/hooks.json:pre_tool_use:0:0`, `code-toolkit@monkey-skills:hooks/hooks.json:session_start:0:0`.
Hash input NOT reverse-engineered (tried hook object / entry / command string / script bytes in several
serializations — no match). Docs: trust is per current hash, re-review on change; `/hooks` (interactive TUI)
is the only documented way to trust; plugin-bundled hooks also require review; managed hooks
(requirements.toml / MDM) are "trusted by policy" — requirements.toml location not documented.

## Side effects
codex exec appended `[projects."<test repo path>"] trust_level = "trusted"` to ~/.codex/config.toml (project trust, unrelated to hook trust).
Test worktree `scratchpad/codex-hook-wt` (branch `wt`) left in place — removal command was denied.

## Implications for loom
1. Deterministic layer on Codex works by construction and in worktrees — once the hook is trusted.
2. Untrusted repo/plugin hooks fail OPEN **silently** in exec mode → a fresh clone / fresh machine has no gate until the user runs `/hooks` once per hook-definition hash. Any change to the hook command line re-triggers review.
3. Zero-init is therefore NOT achievable on Codex for non-managed hooks; the residual user action is one `/hooks` trust per repo per hook version. CI/branch protection remains the only non-bypassable layer.
4. Open question (needs a test that writes global config → ask user): whether a user-authored `~/.codex/requirements.toml` is honored as "managed" (would make loom hooks trusted by policy without /hooks).

## Addendum (2026-09-02, run E) — does trust survive a content-only change to the hook script?

Subject: the already-trusted plugin hook `code-toolkit@monkey-skills:hooks/hooks.json:session_start:0:0`
(`~/.codex/plugins/cache/monkey-skills/code-toolkit/0.16.0/hooks/session-start`).
Method: appended `touch <marker>` to the script (hooks.json definition untouched), ran
`codex exec` WITHOUT `--dangerously-bypass-hook-trust`, checked the marker, restored the script (cmp-verified).

| check | result |
|---|---|
| sha256(script bytes) == trusted_hash? | no (437b6d… vs f8fd55…) |
| sha256(hooks.json bytes) == trusted_hash? | no |
| modified script executed without re-trust? | **YES — marker file created** |

Conclusion: `trusted_hash` covers the hook *definition*, not the script content. Once a hook is trusted, anyone who
can write the script file (an agent on a working branch, if the checker lives in the repo) can change what it does
and it still runs as trusted. Mitigation must come from outside Codex: CI verifies the checker's digest against
main (or the checker lives where the working tree cannot edit it).
