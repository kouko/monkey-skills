---
name: sf-setup
description: Walks you through Salesforce DX backend setup entirely in this conversation — installs sf CLI + salesforce-mcp via brew, then opens browser for one OAuth click. No terminal switching.
allowed-tools: Bash(brew:*), Bash(sf:*), Bash(command:*), Bash(bash:*), Bash(jq:*)
---

# /sf-setup

**End-to-end Salesforce DX onboarding without leaving Claude Code.** Claude orchestrates every step — installs binaries via brew, infers your org alias, opens browser for OAuth, polls for completion, then tells you to `/reload-plugins`.

## Prerequisite (one-time, outside this command)

**Homebrew must already be installed.** This command does not install brew itself because the brew installer is interactive and runs `sudo` — which cannot work from a Claude Code Bash tool (no controlling terminal).

If `command -v brew` fails when this command runs, Claude will halt and show you the one-liner to paste into Terminal.app:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Run that once, restart Claude Code (so brew is in `PATH`), then re-invoke `/sf-setup`.

## $ARGUMENTS

| Flag | Effect |
|---|---|
| `--instance-url=<url>` | Salesforce instance URL (e.g. `https://ichef.my.salesforce.com`). If omitted, Claude asks via `AskUserQuestion`. |
| `--alias=<name>` | Explicit alias override. If omitted, Claude infers from instance URL subdomain and asks you to confirm. |
| `--force-reauth` | Re-run `sf org login web` even when an active default org already exists. |
| `--skip-mcp-brew` | Skip `brew install salesforce-mcp`; the launcher shim falls back to `npx -y @salesforce/mcp` at runtime. |
| `--no-prompt` | Use inferred alias directly; skip the AskUserQuestion confirmation step. |

## Procedure (Claude follows these steps)

### Step 1 — Probe current state

Run via Bash tool:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/credential-check.sh"
```

Parse the JSON output: `{brew, sf_cli, sf_version, salesforce_mcp, mcp_version, node, default_org, default_org_status}`.

**Halt if `.brew == "missing"`** — show the Prerequisite section above and stop. User must install brew in Terminal.app, restart Claude Code, then re-run.

### Step 2 — Install missing binaries (non-interactive)

If `.sf_cli == "missing"`:
```bash
brew install sf
```

If `.salesforce_mcp == "missing"` and `--skip-mcp-brew` was NOT passed:
```bash
brew install salesforce-mcp
```

Both `brew install` calls are non-interactive (no TTY needed) on modern Homebrew. Report progress to user; expect 1-3 min per install on a clean system.

### Step 3 — Resolve org instance URL + alias

If `--instance-url=<url>` was passed in `$ARGUMENTS`, use it directly. Otherwise ask user via `AskUserQuestion`:

> **Question**: Which Salesforce instance? (4 options)
> 1. **Production** (`https://login.salesforce.com`) — default for production orgs
> 2. **Sandbox** (`https://test.salesforce.com`) — for sandbox / test orgs
> 3. **My Domain** (e.g. `https://ichef.my.salesforce.com`) — for company-specific Domain instance
> 4. Other (custom URL)

Then infer alias from URL via `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/alias-infer.sh"` (sourced) — pass the URL and any explicit `--alias=` value. If `--alias=` was given, that wins. Otherwise the inference result is the proposed alias.

If `--no-prompt` was passed, use the inferred alias directly. Otherwise ask user via `AskUserQuestion`:

> **Question**: Use alias `<inferred>` for this org?
> - Yes (accept inferred)
> - Use a different name (then prompt for custom)
> - Don't set alias (sf uses username-derived default)

### Step 4 — OAuth via background bash

Check if a default org is already active (and `--force-reauth` was NOT passed):
```bash
sf org display --json
```

If exit 0 + `.result.connectedStatus == "Connected"`, skip Step 4 — the user is already logged in. Report "already authenticated" + skip to Step 5.

Otherwise, start `sf org login web` in background (use `Bash` tool with `run_in_background: true`):
```bash
sf org login web --alias=<resolved-alias> --set-default --instance-url=<resolved-url>
```

**Tell the user**: "Your browser will open in a moment — please complete the Salesforce OAuth flow. I'll detect when you're done."

Then poll every 5-10 seconds (use `Bash` tool foreground; wait between polls):
```bash
sf org display --target-org=<resolved-alias> --json 2>/dev/null | jq -e '.result.connectedStatus == "Connected"'
```

Poll loop: max 5 minutes (60 polls × 5 sec). If still not connected after 5 min, ask user:
- "OAuth not detected yet — still in progress, or want to abort?"

When `connectedStatus == "Connected"` returns true, OAuth is complete. Move to Step 5.

### Step 5 — Verify + emit summary

Final check:
```bash
sf org display --target-org=<resolved-alias> --json
```

Extract: `instanceUrl`, `username`, `accessTokenExpirationDate`. Report to user as a short summary:

> ✅ Salesforce setup complete
> - Alias: `<alias>`
> - Instance: `<instanceUrl>`
> - Account: `<username>`
> - Token expires: `<accessTokenExpirationDate>`

### Step 6 — Activate MCP server

Tell user:

> Run `/reload-plugins` to activate the salesforce MCP server. After reload you can ask things like:
> - "List the 10 most-recent Opportunities over $50K"
> - "Pull the Weekly Revenue dashboard"

That's the end of the procedure.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `brew: command not found` halt | Homebrew not installed | Run the brew installer one-liner in Terminal.app (see Prerequisite section), restart Claude Code |
| `brew install sf` fails | Network / tap drift / Homebrew API outage | Re-run `/sf-setup`; if persistent, run `brew install sf` in Terminal.app to see the real error |
| OAuth poll times out | User didn't complete consent in browser | Re-run `/sf-setup --force-reauth` |
| `sf org login web` immediately errors | Wrong instance URL for org type (e.g. sandbox URL on Production login) | Re-run `/sf-setup --instance-url=<correct-url> --force-reauth` |
| MCP server still failing after `/reload-plugins` | Launcher couldn't find binary | Run `command -v salesforce-mcp` — if missing, re-run `/sf-setup` (Step 2 will install it) |
| `--no-alias` was passed but Claude still asks alias | Bug — file an issue | Workaround: pass `--no-prompt --alias=-` (literal dash to omit) |

## Alternative — terminal power-user path

If you prefer to run setup in your own terminal (one-shot, TTY-bound):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/auto-setup.sh"
```

This invokes the same 6-step idempotent installer with TTY prompts (no Claude orchestration). Use when you want full control over the brew install confirmation or are debugging step-by-step. Both paths converge on the same end state — `sf` CLI authenticated + `salesforce-mcp` installed + default org set.

## See also

- `docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` — PRODUCT-SPEC (setup steps, JSON contract)
- `scripts/sf/credential-check.sh` — state probe (Step 1 source)
- `scripts/sf/alias-infer.sh` — 3-layer alias inference (Step 3 source)
- `scripts/sf/auto-setup.sh` — TTY-bound terminal-mode installer (alternative path)
- `scripts/sf/refresh-auth.sh` — standalone re-auth helper for token expiry
