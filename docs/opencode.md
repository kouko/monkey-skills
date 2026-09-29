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

For each affected skill family, use the following approach in OpenCode:

- **investing-toolkit**: Replace `CLAUDE_SKILL_DIR` with the plugin's install path (typically `~/.cache/opencode/npm/@kouko/investing-toolkit/version/`) or use relative paths from the skill directory
- **tsundoku**: Replace `CLAUDE_SKILL_DIR` with the plugin's install path or use relative paths from the skill directory
- **think-orbit**: Replace `CLAUDE_PLUGIN_ROOT` with the plugin's install path or use relative paths from the skill directory
- **obsidian**: Replace `CLAUDE_SKILL_DIR` with the plugin's install path or use relative paths from the skill directory
- **salesforce-toolkit**: Replace `CLAUDE_PLUGIN_ROOT` with the plugin's install path or use relative paths from the skill directory

## Tested With

Tested with opencode v2.0.18