# OpenCode v2 plugin compatibility
originator: kouko
kind: engineering
needs-design: no — additive plugin packaging only; skill/command/hook behavior unchanged, and no new user-facing interface surface in this repo
status: confirmed 2026-09-29
publication: automatic — authorized 2026-09-29 by kouko

## Problem
OpenCode v2 users cannot install monkey-skills plugins. The repo ships each plugin as a Claude Code plugin directory (`.claude-plugin/plugin.json` plus `skills/`), which OpenCode v2 does not consume: it expects a plugin to be a package with a `package.json` and a TypeScript entrypoint that registers capabilities programmatically, and SKILL.md folders are not auto-discovered from an installed plugin. The repo already covers four hosts (Claude, Codex, Gemini, Cursor) but not OpenCode, so its 169 skills are unavailable to OpenCode v2 users.

## Proposed outcome
Each of the 21 marketplace plugin directories ships an OpenCode v2 plugin package — a `package.json` plus a thin loader that registers the directory's bundled skills through the OpenCode plugin API — installable from the repo URL with the repository-subdirectory selector, so any plugin can be added to OpenCode and its skills load through the skill tool.

## Acceptance
1. For each of the three pilot plugins (investing-toolkit, obsidian, ascii-graph-toolkit), `opencode plugin add 'github:kouko/monkey-skills#main::path:<plugin>'` succeeds and `opencode plugin list` shows the plugin.
2. In a clean OpenCode session, the pilot plugins' skills are advertised with name and description and load their full body through the skill tool.
3. The remaining 18 marketplace plugins install the same way, and each loads at least one representative skill.
4. A skill whose scripts reference `CLAUDE_SKILL_DIR` or `CLAUDE_PLUGIN_ROOT` either works in OpenCode as written or ships a documented OpenCode-compatible fallback; a clean OpenCode session exercising one such skill produces the expected artifact.
5. Existing host packaging is untouched: `.claude-plugin/`, `.codex-plugin/`, marketplace.json, skill bodies, commands, agents, and hook scripts are unchanged, and the repo package suite passes.

## Constraints
- Additive only: new files (package manifest, loader entrypoint, docs) beside existing plugin content; no rework of existing directories or files.
- OpenCode v2 only; no v1 support.
- Loader code must not violate the repo's flat skill-folder rule.
- Test-first changes; no unrelated cleanup.

## Out of scope
- An OpenCode marketplace or registry (OpenCode has none; installation is per-plugin).
- Porting hooks, agents, commands, or MCP servers to OpenCode (including the ascii-graph-toolkit SessionStart hook).
- Rewriting or improving any existing skill content.
- Changing the Claude, Codex, Gemini, or Cursor packaging.

## Open questions
- none
