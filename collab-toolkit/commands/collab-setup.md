---
name: collab-setup
description: One-time bootstrap for collab-toolkit. Installs agent-browser, downloads Chrome for Testing, installs abx wrapper, writes ~/.config/collab-toolkit/config.json. Default mode: shared (reuses your Chrome profile login state). Opt-in: --dedicated mode (5 per-service profile dirs, manual login). Sub-commands: --reauth <service>, --switch-mode, --verify.
---

# /collab-setup

Bootstrap collab-toolkit. Runs `scripts/setup.sh` from the plugin directory.

## Usage

```bash
/collab-setup                       # default: shared mode (read user's Chrome profile)
/collab-setup --dedicated           # opt-in: dedicated per-service profile dirs (5x manual login)
/collab-setup --reauth <service>    # re-login a single service (dedicated mode)
/collab-setup --switch-mode         # toggle between shared and dedicated
/collab-setup --verify              # re-verify all 5 services are logged in
```

## What it does

1. **Install agent-browser**: macOS prefers `brew install agent-browser`; falls back to `npm i -g agent-browser`. Linux/Windows use npm directly.
2. **Install Chrome for Testing**: runs `agent-browser install` (downloads ~200MB Chromium).
3. **Install abx wrapper**: copies `scripts/abx` to `$HOME/.local/bin/abx`. Warns if `$HOME/.local/bin` is not on PATH.
4. **Write config**: `$XDG_CONFIG_HOME/collab-toolkit/config.json` (defaults to `~/.config/collab-toolkit/config.json`).
5. **Verify services**: opens each of {Asana, Slack, Notion, Google Calendar, Gmail} and checks the page title is not a sign-in page.

## Implementation

Executes:

```bash
bash "$(dirname "$(readlink -f "$0")")/../scripts/setup.sh" "$@"
```

Where `$(dirname ...)` resolves to the plugin's `commands/` directory at runtime; we step up one and into `scripts/setup.sh`.

## See also

- Spec: `docs/superpowers/specs/2026-05-15-collab-toolkit-v0.1.0-design.md`
- Skills that depend on this: asana-automate, slack-automate, notion-automate, gcal-automate, gmail-automate
