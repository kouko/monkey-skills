# OpenCode v2 Plugin Compatibility

This document describes the compatibility of monkey-skills plugins with OpenCode v2, focusing on the handling of `CLAUDE_SKILL_DIR` and `CLAUDE_PLUGIN_ROOT` placeholders.

## What Works

- Skills load correctly in OpenCode v2
- Scripts referenced by relative paths from the skill directory work as-is
- The OpenCode loader passes the skill directory path, enabling relative path resolution

## What Breaks

In OpenCode v2, the `CLAUDE_SKILL_DIR` and `CLAUDE_PLUGIN_ROOT` placeholders **are NOT substituted** in SKILL.md files or scripts. When these tokens appear in instructions, the literal string is passed to the agent, which will fail to resolve the paths.

Specifically affected:
- SKILL.md prose that instructs users to run `$CLAUDE_SKILL_DIR/...` or `$CLAUDE_PLUGIN_ROOT/...`
- Any baked-in paths in scripts that rely on these tokens

## Documented Fallback

In Claude Code, `CLAUDE_SKILL_DIR` is the **current skill's own directory** (`<plugin>/skills/<skill-name>`) and `CLAUDE_PLUGIN_ROOT` is the **plugin root** (`<plugin>`). OpenCode does not substitute either token, so replace them per the install layout:

- **Install path** (OpenCode v2 git install): `~/.cache/opencode/npm/git-<hash>/<n>/node_modules/monkey-skills-<plugin>/`
  - `CLAUDE_PLUGIN_ROOT` → that plugin directory
  - `CLAUDE_SKILL_DIR` → `<plugin dir>/skills/<current-skill-name>` (NOT the plugin root — scripts under `${CLAUDE_SKILL_DIR}/scripts/` live inside the individual skill)
- **Relative paths (recommended)**: scripts referenced from the skill directory work as-is when resolved relative to the skill's own folder; prefer editing the command to a relative path over hard-coding the cache path (cache hashes change between versions)

Per plugin:
- **investing-toolkit** (uses both tokens): `CLAUDE_PLUGIN_ROOT` → plugin dir; `CLAUDE_SKILL_DIR` → `<plugin dir>/skills/<skill-name>` (e.g. `report-stock-snapshot/scripts/snapshot_format.py` lives inside that skill's directory)
- **tsundoku** (uses both tokens): same substitutions as investing-toolkit
- **think-orbit** (`CLAUDE_PLUGIN_ROOT` only): → plugin dir
- **obsidian** (`CLAUDE_SKILL_DIR` only): → `<plugin dir>/skills/<skill-name>`
- **salesforce-toolkit** (`CLAUDE_PLUGIN_ROOT` only): → plugin dir

## Tested With

Tested with opencode v2.0.18