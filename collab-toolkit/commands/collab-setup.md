---
name: collab-setup
description: Bootstrap collab-toolkit. Installs agent-browser, Chrome for Testing, abx wrapper, writes ~/.config/collab-toolkit/config.json. v0.1.2 default = dedicated mode (unified per-toolkit profile, Claude-orchestrated 2-3-login flow via AskUserQuestion — Google SSO cascade). Shared mode (reuse your daily Chrome login state) is opt-in via --shared (⚠️ failure-prone in multi-profile / multi-account / SSO-refresh setups). Sub-commands: --reauth <service>, --switch-mode (bidirectional toggle), --verify.
---

# /collab-setup

Bootstrap and configure collab-toolkit. This command is **Claude-orchestrated** — Claude reads the instructions below and drives the flow with `Bash` + `AskUserQuestion` tools. No `!` prefix needed.

`$ARGUMENTS` may contain: `--dedicated`, `--shared`, `--switch-mode`, `--reauth <service>`, `--verify`, or nothing.

The plugin directory containing this command file is `${CLAUDE_PLUGIN_ROOT}` (or, in older runtimes, resolve via `$(dirname this-file)/..`). The setup script lives at `<plugin-root>/scripts/setup.sh`.

---

## ⚠️ MUST NOT — anti-pattern guards for this orchestration

> 1. **DO NOT use `AskUserQuestion` to ask the user which mode (shared vs dedicated) to use.** The mode is determined unambiguously by `$ARGUMENTS` per the Step 1 dispatch table. Empty args = dedicated, period. Showing a mode picker is a regression — the user explicitly opted for "no-flag default" UX (see v0.1.3 release notes).
> 2. **DO NOT prompt the user for shared/dedicated confirmation when no config exists.** "No config + no args = dedicated" is the explicit v0.1.3 default. Just proceed.
> 3. **`AskUserQuestion` is reserved for the orchestrated login flow** (per-service "Logged in to X?" prompts in Section 3b) and for `--reauth` Done/Retry confirmation. **Mode selection is never an `AskUserQuestion`.**
> 4. Sections 3a / 3b / 3c / 3d / 3e are **dispatch targets** (determined by Step 1), **not** menu options shown to the user.

## Step 1: Parse `$ARGUMENTS` and dispatch (no picker)

Parse `$ARGUMENTS` and JUMP DIRECTLY to the corresponding Section 3 subsection. Do not surface the choice to the user.

| `$ARGUMENTS` | Action | Jump to |
|---|---|---|
| empty | Default = dedicated mode | Section 3b |
| `--dedicated` | Explicit dedicated mode | Section 3b |
| `--shared` | Opt-in shared mode (⚠️ caveat) | Section 3a |
| `--switch-mode` | Toggle mode (no-config → dedicated) | Section 3c |
| `--reauth <service>` | Re-login one service | Section 3d |
| `--verify` | Verify 5 services headless | Section 3e |

Read current mode if config exists:

```bash
bash -c 'jq -r .mode ~/.config/collab-toolkit/config.json 2>/dev/null || echo "(none)"'
```

For `--switch-mode`: if current mode is `shared` → target = dedicated. If `dedicated` → target = shared. If empty → target = shared.

## Step 2: Install (idempotent — runs fast if already installed)

For all actions except `--verify` and `--reauth`, run install phases first:

```bash
bash "<plugin-root>/scripts/setup.sh" --install-only
```

This installs agent-browser (Homebrew preferred on macOS, npm fallback), downloads Chrome for Testing if missing, installs `~/.local/bin/abx` wrapper. Already-installed steps are no-ops.

## Step 3: Dispatch targets (executed per Step 1 — NOT menu options)

> **Reminder**: subsections 3a–3e are jump targets selected by Step 1's args parsing. **Never** present them as options to the user via `AskUserQuestion`. The user already chose by passing (or omitting) flags.

### 3a. Setup shared mode (opt-in via `--shared`)

> ⚠️ **Shared mode has known failure modes** in real-world setups: cookies may not transfer from daily Chrome (especially when Chrome is running with profile-lock active or macOS Keychain prompts dismissed); multi-Chrome-profile users have to pick the "right" profile; services using SSO refresh may not work headless; verify is brittle for marketing-redirect cases. **Dedicated mode (default) is recommended for office-collaboration use.** Use shared only if you specifically know your setup is simple (one Chrome profile, all 5 services in one Google account, no SSO refresh).

Goal: pick a Chrome profile + write shared-mode config + verify.

1. List Chrome profiles + Google account emails:
   ```bash
   bash "<plugin-root>/scripts/setup.sh" --list-profiles-meta 2>/dev/null || true
   # OR equivalently:
   bash -c '
     agent-browser profiles || true
     source "<plugin-root>/scripts/setup.sh" --source-only
     list_profiles_with_email 2>/dev/null || true
   '
   ```

2. Parse the output. Profile names appear as either directory names (e.g., `Default`, `Profile 1`, `Profile 2`) from `agent-browser profiles` OR as `<dir>: <email> — <display>` lines from `list_profiles_with_email`.

3. Show the user a summary of profile→email mapping and use **AskUserQuestion** to let them pick:
   - Header: `Chrome profile`
   - Question: `Which Chrome profile to use for collab-toolkit?`
   - Options: each profile directory name (e.g., `Default`, `Profile 1`, `Profile 2`). For each option, include the Google account email in the description if known. If you can't determine the list, default options should at minimum include `Default` and `Profile 1`.

4. Write config:
   ```bash
   bash "<plugin-root>/scripts/setup.sh" --setup-shared "<chosen_profile_name>"
   ```

5. Verify all 5 services:
   ```bash
   bash -c 'agent-browser close 2>/dev/null; bash "<plugin-root>/scripts/setup.sh" --verify'
   ```
   (Daemon close ensures fresh profile snapshot.)

6. Report results to user. For each `⚠️ NOT logged in` service, instruct user to log in via their daily Chrome under the chosen profile, then re-run `/collab-setup --verify`.

### 3b. Setup dedicated mode (orchestrated login flow)

Goal: write dedicated-mode config + open headed Chrome + walk user through 5 service logins via AskUserQuestion + verify.

1. Write config + create dedicated profile dir (does NOT open Chrome yet):
   ```bash
   bash "<plugin-root>/scripts/setup.sh" --setup-dedicated-config
   ```

2. Clear daemon so the new profile takes effect:
   ```bash
   agent-browser close 2>/dev/null || true
   ```

3. Walk user through 5 service logins **sequentially**. For each service in this order: `asana, slack, notion, gcal, gmail`:

   a. Open the service in headed Chrome (first call launches Chrome; subsequent calls navigate the existing window):
      ```bash
      bash "<plugin-root>/scripts/setup.sh" --open-headed <service>
      ```

   b. Use **AskUserQuestion** to confirm login:
      - Header: e.g., `Asana login`
      - Question: e.g., `Logged into Asana in the popup Chrome window?`
      - Options:
        - `Done — logged in` (proceed to next service)
        - `Skip this service` (skip and continue; service will show ⚠️ in verify)
        - `I had to retry login` (re-run --open-headed for this service, then ask again)

   c. Based on answer, advance to next service or retry/skip.

   **Important: Google SSO cascade.** After the user logs into the first Google-account-related service (e.g., GCal or Gmail), subsequent Google-SSO services may auto-complete with no visible login form. User should still click "Done — logged in" once they see the service UI loaded.

4. Close daemon to ensure verify uses fresh cookies:
   ```bash
   agent-browser close 2>/dev/null || true
   ```

5. Verify all 5 services (headless):
   ```bash
   bash "<plugin-root>/scripts/setup.sh" --verify
   ```

6. Report results. For any `⚠️ NOT logged in`, use **AskUserQuestion** to offer:
   - `Retry this service` (re-runs `--reauth <service>` flow)
   - `Skip — fix manually later`

### 3c. `--switch-mode`

1. Read current mode (Step 1).
2. If current = `shared` → run 3b (Setup dedicated mode).
3. If current = `dedicated` → run 3a (Setup shared mode).
4. If empty → run 3b (no prior config → v0.1.2 default = dedicated).

After completion, mention to the user that the mode has been toggled.

### 3d. `--reauth <service>`

1. Confirm current mode is dedicated:
   ```bash
   bash -c 'jq -r .mode ~/.config/collab-toolkit/config.json'
   ```
   If `shared`: tell user `--reauth` only applies in dedicated mode; suggest they log into the service via their daily Chrome under the configured profile instead.

2. Open Chrome at the service URL:
   ```bash
   bash "<plugin-root>/scripts/setup.sh" --open-headed <service>
   ```

3. **AskUserQuestion**:
   - Question: `<Service> re-login complete?`
   - Options: `Done`, `Retry`, `Cancel`

4. On Done: close daemon + run verify for confirmation:
   ```bash
   agent-browser close 2>/dev/null
   bash "<plugin-root>/scripts/setup.sh" --verify
   ```

5. Show results.

### 3e. `--verify`

```bash
agent-browser close 2>/dev/null
bash "<plugin-root>/scripts/setup.sh" --verify
```

Show the 5 ✓/⚠️ lines verbatim to the user.

---

## Concrete defaults (use these when in doubt)

- Plugin root: the directory containing this file's parent (`commands/..`).
- Setup script: `<plugin-root>/scripts/setup.sh`.
- Config: `${XDG_CONFIG_HOME:-$HOME/.config}/collab-toolkit/config.json`.
- Dedicated profile (v0.1.2 unified): `${XDG_DATA_HOME:-$HOME/.local/share}/collab-toolkit/profiles/dedicated`.

## Error handling

- If any `bash setup.sh ...` invocation exits non-zero, capture stderr and surface it to the user. Suggest re-running with a fresh state by clearing `~/.config/collab-toolkit/` + `~/.local/share/collab-toolkit/` (and optionally `~/.local/bin/abx`).
- If `agent-browser` is not on PATH after `--install-only`, instruct the user to ensure Homebrew is installed (macOS) or npm globally accessible.
- If `~/.local/bin` is not on `PATH`, `--install-only` prints a warning with the `export` line — relay this to the user verbatim.

## See also

- Plugin README: `<plugin-root>/README.md`
- v0.1.0 design spec: `docs/superpowers/specs/2026-05-15-collab-toolkit-v0.1.0-design.md`
- Skills consuming this setup: asana-automate, slack-automate, notion-automate, gcal-automate, gmail-automate
