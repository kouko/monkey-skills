# collab-toolkit v0.1.0 — Design Spec

**Date**: 2026-05-15
**Branch**: `feat/collab-toolkit-v0.1.0`
**Source**: New plugin wrapping [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) for office-collaboration browser automation across 5 services with no functional MCP coverage (Asana, Slack, Notion, Google Calendar, Gmail) in the user's current and future environments.

## Status

| Section | State |
|---|---|
| Brainstorm | ✅ approved (sections 1-7) |
| Spec | drafted, awaiting user review |
| Plan | pending (`superpowers:writing-plans`) |
| Implementation | pending |

## 1. Background

### 1.1 Why agent-browser

`vercel-labs/agent-browser` is a native Rust CLI shipping its own Claude Code plugin (`.claude-plugin/marketplace.json` + per-purpose runtime-loaded skills). It exposes browser automation as a daemon over Chrome DevTools Protocol with three properties that matter for this design:

1. **Semantic snapshot model** — `agent-browser snapshot -i --json` returns the accessibility tree with `@eN` refs assigned freshly per snapshot. Lets selectors live at the role+name semantic layer instead of CSS / XPath, dramatically slowing UI-breakage decay.
2. **Persistent profile reuse** — `--profile <name|path>` operates in two modes: by-name copies an existing Chrome profile to a read-only temp snapshot (with the macOS Keychain `--use-real-keychain` fix applied automatically), by-path uses a dedicated long-lived directory. Both modes preserve cookies / localStorage / SSO tokens.
3. **Headless default** — Chrome launches headless by default; `--headed` opt-in only.

### 1.2 Gap analysis vs existing MCP

| Service | MCP available in current env | Functional coverage |
|---|---|---|
| Asana | None | 0% — no MCP exists |
| Slack | `mcp__claude_ai_Slack__*` | ~90% (search / read / send / canvas / reactions) |
| Notion | `mcp__plugin_Notion_notion__*` | ~85% (fetch / pages / database / views / comments) |
| Google Calendar | `mcp__claude_ai_Google_Calendar__authenticate` only | ~0% (auth-only stubs) |
| Gmail | `mcp__claude_ai_Gmail__authenticate` only | ~0% (auth-only stubs) |

User's stated requirement: **future execution in MCP-less environments (CI / cron / new machines)**. Therefore design must not assume MCP availability — full surface coverage per app via agent-browser, with routing that lets MCP tools (when present) compete naturally on tool-call specificity.

### 1.3 Why this is a new plugin, not extension of an existing one

monkey-skills convention: per-domain plugin. None of the existing plugins (`obsidian`, `investing-toolkit`, `dev-workflow`, `gws-toolkit`, etc.) own office-collaboration browser automation. `gws-toolkit` is the nearest neighbor but is API-based (official Google Workspace CLI) and explicitly scoped to Google Workspace, not cross-vendor.

## 2. Goal

Ship `collab-toolkit` v0.1.0 as a Claude Code plugin packaging **5 read-only skills** for office-collaboration browser automation:

| Skill | Service | Hero protocols |
|---|---|---|
| `asana-automate` | Asana | task-list, task-detail, project-overview, search-global |
| `slack-automate` | Slack | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | Notion | search-workspace, page-fetch, database-query, page-backlinks |
| `gcal-automate` | Google Calendar | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate` | Gmail | mail-search, thread-read, inbox-summary, label-read |

Plus a `/collab-setup` slash command that bootstraps agent-browser, Chrome for Testing, and a profile configuration (shared with the user's Chrome by default; opt-in dedicated per-service profile).

Read-only scope: **service-side** read operations only (search, list, fetch). The skills make no mutating calls against Asana / Slack / Notion / Google Calendar / Gmail. Local filesystem writes (`/tmp` snapshots, `~/.config/collab-toolkit/config.json`, profile dirs) are normal. Service-side writes (send message, create task, update event) deferred to v0.2.0+.

## 3. Locked decisions

| # | Decision | Source |
|---|---|---|
| D1 | Plugin name: `collab-toolkit`, new independent plugin | brainstorm Q (plugin-name) |
| D2 | 5 skills, all read-only, 4 hero protocols per skill (20 total) | brainstorm Q3 |
| D3 | Browser mode: Web headless background (not Electron desktop) | brainstorm Q1 |
| D4 | Profile mode: Hybrid — default `shared` (Chrome profile by name) + opt-in `dedicated` (per-service path), switchable via config | brainstorm Q (profile-mode-final) |
| D5 | Single workspace per service (no `--workspace` flag in v0.1.0) | brainstorm Q4 |
| D6 | UI brittleness: Semantic-first selectors (role+name via jq filter on JSON snapshot), no hardcoded `@eN` refs in protocols | brainstorm Q5 |
| D7 | Routing description: sole-path wording, no conditional "PREFER MCP" language; tool-call specificity handles natural routing | user follow-up after Section 2 |
| D8 | Bootstrap: `/collab-setup` slash command; `scripts/setup.sh` does Homebrew first → npm fallback → `agent-browser install` → verify | brainstorm Q (setup-flow) |
| D9 | `abx` wrapper at `~/.local/bin/abx` centralizes profile-arg resolution; all protocols call `abx`, never `agent-browser` directly | brainstorm Q (profile-mode-final, abx wrapper) |
| D10 | Cowork incompatibility marked with ⚠️ in plugin description (per PR #154 convention) | brainstorm Q (cowork) |
| D11 | i18n READMEs: `README.md` / `README.ja.md` / `README.zh-TW.md` (per PR #150 rule) | brainstorm Q (i18n) |
| D12 | Testing: L0 (CI structure check via existing `scripts/check-*.py`) + L1 (bats unit tests for `setup.sh` and jq filters); L2 live smoke deferred to v0.2.0+ | brainstorm Q6 |
| D13 | Per-protocol output: Markdown summary by default; `--json` mode passes through agent-browser's structured output for downstream chaining | implicit from agent-browser convention |
| D14 | Last Google service is Gmail (not Maps) | user correction |

## 4. Plugin architecture

```
collab-toolkit/
├── .claude-plugin/
│   └── plugin.json
├── README.md / README.ja.md / README.zh-TW.md
├── commands/
│   └── collab-setup.md
├── scripts/
│   ├── setup.sh                    # /collab-setup back-end
│   ├── abx                         # wrapper, copied to ~/.local/bin/ at setup time
│   └── tests/
│       ├── test-setup.bats
│       ├── test-jq-filters.bats
│       └── fixtures/
│           ├── asana-snapshot.json
│           ├── slack-snapshot.json
│           ├── notion-snapshot.json
│           ├── gcal-snapshot.json
│           └── gmail-snapshot.json
└── skills/
    ├── asana-automate/
    │   ├── SKILL.md
    │   ├── protocols/
    │   │   ├── task-list.md
    │   │   ├── task-detail.md
    │   │   ├── project-overview.md
    │   │   └── search-global.md
    │   └── references/
    │       ├── ui-patterns.md       # role+name selector convention for this service
    │       └── failure-modes.md     # error handling specific to this service
    │
    ├── slack-automate/
    │   ├── SKILL.md
    │   ├── protocols/
    │   │   ├── search-messages.md
    │   │   ├── channel-read.md
    │   │   ├── thread-read.md
    │   │   └── find-user.md
    │   └── references/{ui-patterns,failure-modes}.md
    │
    ├── notion-automate/
    │   ├── SKILL.md
    │   ├── protocols/
    │   │   ├── search-workspace.md
    │   │   ├── page-fetch.md
    │   │   ├── database-query.md
    │   │   └── page-backlinks.md
    │   └── references/{ui-patterns,failure-modes}.md
    │
    ├── gcal-automate/
    │   ├── SKILL.md
    │   ├── protocols/
    │   │   ├── agenda-view.md
    │   │   ├── event-search.md
    │   │   ├── find-free-slots.md
    │   │   └── shared-calendar-read.md
    │   └── references/{ui-patterns,failure-modes}.md
    │
    └── gmail-automate/
        ├── SKILL.md
        ├── protocols/
        │   ├── mail-search.md
        │   ├── thread-read.md
        │   ├── inbox-summary.md
        │   └── label-read.md
        └── references/{ui-patterns,failure-modes}.md
```

Folder structure complies with monkey-skills CLAUDE.md "subfolder is single level only" rule.

## 5. Components

### 5.1 `plugin.json`

```json
{
  "name": "collab-toolkit",
  "version": "0.1.0",
  "description": "Browser automation toolkit wrapping vercel-labs/agent-browser. 5 read-only office-collaboration skills (Asana / Slack / Notion / Google Calendar / Gmail) — search, list, fetch via semantic-first selectors over Chrome (shared profile by default, dedicated profile opt-in). Headless background after one-time /collab-setup. ⚠️ Claude Code CLI only — Cowork sandbox blocks browser launch.",
  "author": { "name": "kouko", "url": "https://github.com/kouko" },
  "homepage": "https://github.com/kouko/monkey-skills/tree/main/collab-toolkit",
  "repository": "https://github.com/kouko/monkey-skills",
  "license": "MIT",
  "keywords": [
    "agent-browser", "browser-automation", "office-collaboration",
    "asana", "slack", "notion", "google-calendar", "gmail",
    "headless", "read-only", "semantic-selector"
  ]
}
```

### 5.2 `marketplace.json` entry

Append to top-level `monkey-skills/.claude-plugin/marketplace.json`:

```json
{
  "name": "collab-toolkit",
  "description": "<verbatim match of plugin.json description above — CI scripts/check-marketplace-description-sync.py enforces>",
  "source": "./collab-toolkit/"
}
```

### 5.3 Runtime config — XDG-compliant paths

Follows [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) for cross-environment consistency with modern CLIs (gh, rclone, mise, starship, direnv):

| Resource | Path | Override env |
|---|---|---|
| Config (settings) | `$XDG_CONFIG_HOME/collab-toolkit/config.json` → default `~/.config/collab-toolkit/config.json` | `XDG_CONFIG_HOME` |
| Data (auth profiles) | `$XDG_DATA_HOME/collab-toolkit/profiles/` → default `~/.local/share/collab-toolkit/profiles/` | `XDG_DATA_HOME` |
| Wrapper binary | `$HOME/.local/bin/abx` (de-facto standard, no XDG counterpart) | — |

`config.json` schema written by `/collab-setup`:

```json
{
  "mode": "shared",                                                // "shared" | "dedicated"
  "chrome_profile": "Default",                                     // used when mode=shared
  "profiles_root": "~/.local/share/collab-toolkit/profiles"        // used when mode=dedicated; tilde-expanded at read time
}
```

Default: `mode=shared`, `chrome_profile=Default` (user pickable from `agent-browser profiles` enumeration).

### 5.4 `abx` wrapper — `$HOME/.local/bin/abx`

Installed by `setup.sh` to a directory that is on `PATH` by default for most modern setups (macOS Homebrew shellenv, most Linux distros, manjaro/arch defaults). This solves the `allowed-tools` allowlist problem — SKILL.md can whitelist `Bash(abx:*)` directly. If `$HOME/.local/bin` is not yet on PATH, `setup.sh` prints the export line for the user's shell rc.

Resolves profile arg from config, then `exec agent-browser` with `--profile` prepended:

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/collab-toolkit/config.json"
SERVICE="${ABX_SERVICE:-}"

if [ ! -f "$CONFIG" ]; then
  echo "ERR: ~/.config/collab-toolkit/config.json not found. Run /collab-setup first." >&2
  exit 1
fi

MODE=$(jq -r .mode "$CONFIG")

if [ "$MODE" = "dedicated" ] && [ -n "$SERVICE" ]; then
  PROFILES_ROOT=$(jq -r .profiles_root "$CONFIG")
  PROFILES_ROOT="${PROFILES_ROOT/#\~/$HOME}"
  exec agent-browser --profile "${PROFILES_ROOT}/${SERVICE}" "$@"
else
  PROFILE_NAME=$(jq -r .chrome_profile "$CONFIG")
  exec agent-browser --profile "$PROFILE_NAME" "$@"
fi
```

Protocols set `ABX_SERVICE=<service>` before each `abx` call to hint dedicated-mode routing.

### 5.5 `/collab-setup` slash command

`commands/collab-setup.md`:

```markdown
---
name: collab-setup
description: One-time bootstrap for collab-toolkit. Installs agent-browser, downloads Chrome for Testing, installs abx wrapper, writes ~/.config/collab-toolkit/config.json. Default mode: shared (reuses your Chrome profile login state). Opt-in: --dedicated mode (5 per-service profile dirs, manual login). Sub-commands: --reauth <service>, --switch-mode, --verify.
---

# /collab-setup

Runs scripts/setup.sh with the chosen mode. See SKILL body for sub-command details.
```

### 5.6 `scripts/setup.sh`

Pseudocode (full implementation in `scripts/setup.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail

xdg_config_home() { echo "${XDG_CONFIG_HOME:-$HOME/.config}"; }
xdg_data_home()   { echo "${XDG_DATA_HOME:-$HOME/.local/share}"; }
xdg_bin_home()    { echo "$HOME/.local/bin"; }     # no XDG counterpart; de-facto standard

CONFIG_DIR="$(xdg_config_home)/collab-toolkit"
DATA_DIR="$(xdg_data_home)/collab-toolkit"
BIN_DIR="$(xdg_bin_home)"
CONFIG="$CONFIG_DIR/config.json"
PROFILES_ROOT="$DATA_DIR/profiles"
DEDICATED=false; REAUTH=""; SWITCH=false; VERIFY_ONLY=false
parse_args "$@"  # populates flags above

mkdir -p "$CONFIG_DIR" "$DATA_DIR" "$BIN_DIR"

install_agent_browser() {
  command -v agent-browser >/dev/null && return 0
  if [[ "$OSTYPE" == "darwin"* ]] && command -v brew >/dev/null; then
    brew install agent-browser || npm i -g agent-browser
  else
    command -v npm >/dev/null || { echo "ERR: npm required"; exit 1; }
    npm i -g agent-browser
  fi
}

install_chrome() { agent-browser install && agent-browser --version; }

install_abx() {
  cp "$(dirname "$0")/abx" "$BIN_DIR/abx"
  chmod +x "$BIN_DIR/abx"
  # PATH check — warn if $HOME/.local/bin not on PATH
  case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "⚠️ $BIN_DIR not on PATH. Add to your shell rc:"
       echo '   export PATH="$HOME/.local/bin:$PATH"' ;;
  esac
}

setup_shared() {
  echo "Available Chrome profiles:"
  agent-browser profiles
  read -rp "Profile name to use [Default]: " name
  name="${name:-Default}"
  write_config_shared "$name"
  verify_all_services
}

setup_dedicated() {
  mkdir -p "$PROFILES_ROOT"/{asana,slack,notion,gcal,gmail}
  write_config_dedicated
  for service in asana slack notion gcal gmail; do
    setup_one_dedicated "$service"
  done
}

setup_one_dedicated() {
  local service="$1"
  local url=$(service_url "$service")
  echo "→ Opening ${service} (--headed). Log in, then press Enter."
  agent-browser --headed --profile "$PROFILES_ROOT/$service" open "$url"
  read -rp "Press Enter when logged in: "
  verify_one "$service"
}

verify_all_services() {
  for service in asana slack notion gcal gmail; do verify_one "$service"; done
}

verify_one() {
  local service="$1"
  local url=$(service_url "$service")
  ABX_SERVICE="$service" "$BIN_DIR/abx" open "$url" >/dev/null
  local title=$(ABX_SERVICE="$service" "$BIN_DIR/abx" get title)
  case "$title" in
    *"Sign in"*|*"Log in"*|*"Login"*)
      echo "⚠️ $service: NOT logged in (title: $title)"
      [ "$MODE" = "shared" ] && echo "   → Log into $service in your daily Chrome, then re-run /collab-setup --verify"
      [ "$MODE" = "dedicated" ] && echo "   → Run: /collab-setup --reauth $service"
      ;;
    *) echo "✓ $service ready" ;;
  esac
}

service_url() {
  case "$1" in
    asana)  echo "https://app.asana.com/0/inbox" ;;
    slack)  echo "https://app.slack.com" ;;
    notion) echo "https://www.notion.so" ;;
    gcal)   echo "https://calendar.google.com" ;;
    gmail)  echo "https://mail.google.com" ;;
  esac
}

main() {
  $VERIFY_ONLY && { verify_all_services; exit 0; }
  [ -n "$REAUTH" ] && { setup_one_dedicated "$REAUTH"; exit 0; }
  install_agent_browser
  install_chrome
  install_abx
  if $DEDICATED || ($SWITCH && [ "$(current_mode)" = "shared" ]); then setup_dedicated; else setup_shared; fi
}
main
```

### 5.7 SKILL.md template (each of 5 skills)

```yaml
---
name: <service>-automate
description: <service capitalized> automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: <comma-separated list of 4 hero protocols with one-line each>. Read-only v0.1.0 — search and fetch only, no writes. <ja tail>。<zh-TW tail>。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# <service> automate

Read-only browser automation for <service>. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- This service is verified logged-in

If any protocol fails with "config not found": run `/collab-setup`.
If any protocol fails with "login wall detected" in title: per setup mode, either log into <service> in your daily Chrome (shared mode) or run `/collab-setup --reauth <service>` (dedicated mode).

## Hero protocols

- `protocols/<protocol-1>.md` — <one-line description>
- `protocols/<protocol-2>.md` — <one-line description>
- `protocols/<protocol-3>.md` — <one-line description>
- `protocols/<protocol-4>.md` — <one-line description>

## Selector convention

See `references/ui-patterns.md` — all protocols MUST find refs via:
1. `abx snapshot -i --json` → save to /tmp
2. `jq '.elements[] | select(.role==X and .name==Y) | .ref' | head -1`
3. Empty result → exit with "UI changed: <role>+<name> not found"

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default: human-readable Markdown summary.
`--json` (passthrough to abx): structured JSON for downstream chaining.
```

### 5.8 Protocol template

Every protocol file follows the same structure:

```markdown
---
name: <protocol-name>
purpose: one-sentence use case
---

## Inputs
- arg1: description, type, required/optional
- arg2: ...

## Output
- Default Markdown shape: ...
- `--json` JSON shape: ...

## Procedure (semantic-first, no hardcoded refs)

# Prerequisite: $HOME/.local/bin must be on PATH; /collab-setup ensures this.
# If `abx` is not found, run /collab-setup or check PATH per setup output.

# 1. Open + wait
ABX_SERVICE=<service> abx open "<url>"
ABX_SERVICE=<service> abx wait --load networkidle

# 2. Snapshot JSON
SNAP=$(ABX_SERVICE=<service> abx snapshot -i --json)

# 3. Locate elements by role+name (NEVER @eN literal)
TARGET_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="<R>" and .name=="<N>") | .ref' | head -1)
[ -z "$TARGET_REF" ] && { echo "ERR: UI changed: '<N>' (role=<R>) not found"; exit 1; }

# 4. Act
ABX_SERVICE=<service> abx click "$TARGET_REF"
# ... continues

## Failure modes (cross-reference)
- "UI changed: ..." → references/failure-modes.md → "UI evolution" section
- "Login wall" → references/failure-modes.md → "Auth expiry" section

## Examples

Example invocation, expected outputs (both Markdown and --json modes).
```

### 5.9 `references/ui-patterns.md` (per skill)

Documents the role+name conventions for this specific service. Example for Asana:

- `My tasks` link → `role="link"` `name="My tasks"`, nested under top-level navigation
- Task list rows → `role="row"` `name="<task title>"`
- Project name in header → `role="heading"` `level=1`

Includes a "Refresh playbook" section: how to re-derive these patterns when UI changes — run `abx snapshot -i --json`, inspect, update this file.

### 5.10 `references/failure-modes.md` (per skill)

Cross-reference target for protocol error branches. Sections:
- UI evolution (detection + remediation)
- Auth expiry / login wall (per profile mode)
- Network timeout / rate limit
- Empty result vs. error (disambiguation)

## 6. Data flows

### 6.1 First-run setup (default = shared mode)

```
User: /collab-setup
  ▼
Phase 1: install agent-browser (brew → npm fallback)
  ▼
Phase 2: agent-browser install (downloads Chrome for Testing, ~200MB)
  ▼
Phase 3: install_abx writes ~/.local/bin/abx
  ▼
Phase 4 (shared): enumerate Chrome profiles, user picks → write config.json → verify each of 5 services
  ▼
Done. Subsequent skill invocations use cookies from user's daily Chrome.

Total time on warm Mac: ~1 minute (download dominates).
```

### 6.2 First-run setup (opt-in dedicated mode)

```
User: /collab-setup --dedicated
  ▼
Phases 1-3 same as 6.1
  ▼
Phase 4: mkdir 5 profile dirs, write config (mode=dedicated)
  ▼
Phase 5: for each of 5 services:
  agent-browser --headed --profile <dir> open <url>
  User logs in manually in popup Chrome
  User presses Enter
  verify_one (check title not "Sign in")
  ▼
Done. Cookies persist in dedicated dirs, independent of daily Chrome.

Total time: ~5 minutes (5 login flows).
```

### 6.3 Per-protocol invocation (typical, shared mode)

```
User: "list my Asana tasks due this week"
  ▼
Claude routes to asana-automate (description match)
  ▼
SKILL.md body → dispatches to protocols/task-list.md
  ▼
[protocols/task-list.md procedure executes]
  ABX_SERVICE=asana abx open https://app.asana.com/0/inbox       # headless
  ↓ daemon spawned (first call) + Chrome launched in temp dir
  ↓ cookies copied from ~/Library/Application Support/Google/Chrome/Default/
  ↓ Keychain unlock via --use-real-keychain (handled by agent-browser)
  ABX_SERVICE=asana abx wait --load networkidle
  ABX_SERVICE=asana abx snapshot -i --json > /tmp/snap.json
  jq → TASKS_NAV_REF
  ABX_SERVICE=asana abx click "$TASKS_NAV_REF"
  ↓ ... iterate snapshot + extract task elements
  ↓ filter by due-date
  ↓ format output
  ▼
Markdown summary or JSON returned to user

Daemon persists in background (AGENT_BROWSER_IDLE_TIMEOUT_MS controls auto-shutdown).
Subsequent protocol calls within idle window reuse Chrome (fast).
```

### 6.4 Auth expiry / login wall

```
abx open <url>
abx get title
  ↓
Title matches "*Sign in*" | "*Log in*" | "*Login*"
  ↓
shared mode: surface message "Log into <service> in your daily Chrome, then retry"
dedicated mode: surface message "Run /collab-setup --reauth <service>"
  ↓
Protocol fails fast — does NOT attempt to scrape login state from logged-out session
```

## 7. Error handling

| Error class | Detection | Surface |
|---|---|---|
| agent-browser binary missing | `command -v agent-browser` in abx first line | `ERR: Run /collab-setup first.` |
| `~/.config/collab-toolkit/config.json` missing | abx file check | Same as above |
| `~/.local/bin/abx` missing or not executable | protocol uses `${HOME}/.local/bin/abx` directly, fails on exec | `ERR: abx wrapper not found. Run /collab-setup first.` |
| UI changed (semantic selector empty) | jq filter empty AND role does not exist in snapshot at all | `ERR: UI changed: <role>+<name> not found. Update <skill>/references/ui-patterns.md and re-snapshot.` |
| Login wall (auth expired) | Title contains Sign in/Log in/Login, or URL redirects to /login | Mode-specific remediation message (see 6.4) |
| Chrome profile lock conflict (shared mode + Chrome busy) | agent-browser launch returns lock error | Retry after 2s sleep once; on second failure: `Close heavy Chrome tabs, or switch to dedicated mode: /collab-setup --switch-mode` |
| Network timeout / page load failure | agent-browser internal timeout (default 25s; configurable via AGENT_BROWSER_TIMEOUT_MS) | Pass-through to protocol output, suggest retry |
| Empty result vs. UI changed | Disambiguate: if expected role exists in snapshot but name search returns 0 → may be valid empty result; if role itself is absent → UI changed | Protocol-specific messaging per case |
| jq missing | Pre-flight check in abx (if used in shared decode path) | `ERR: jq required. brew install jq.` |

## 8. Testing

### 8.1 L0 — structure / metadata (CI, existing)

The repo-level CI already runs:
- `scripts/check-skill-structure.py` — SKILL.md frontmatter, folder convention, allowed-tools whitelist
- `scripts/check-marketplace-description-sync.py` — plugin.json ↔ marketplace.json description verbatim match
- `scripts/check-plugin-description-skill-coherence.py` — plugin description references actual skills
- `scripts/check-shared-conventions-drift.py` — cross-plugin drift detection

collab-toolkit gets L0 for free once plugin.json and SKILL.md frontmatters are correct.

### 8.2 L1 — shell unit tests (bats, scripts/tests/)

`test-setup.bats` covers `scripts/setup.sh` logic:
- macOS prefers Homebrew (`OSTYPE=darwin*` + `brew` available)
- Homebrew failure falls back to npm
- Linux uses npm directly
- abx wrapper installed at correct path with correct permissions
- `setup_shared` writes config.json with `mode=shared`, picked profile name
- `setup_dedicated` writes config.json with `mode=dedicated`, mkdir's 5 profile dirs
- `verify_one` correctly detects "Sign in" / "Log in" / "Login" in title

`test-jq-filters.bats` covers per-protocol jq selectors against captured snapshot fixtures:
- `fixtures/asana-snapshot.json` (real `abx snapshot -i --json` output, anonymized cookies stripped)
- Same for slack / notion / gcal / gmail
- For each hero protocol, verify the jq filter returns non-empty ref of expected format

bats invocation: `cd collab-toolkit && bats scripts/tests/`. Documented in README "Development" section. Not in CI for v0.1.0 (bats is an extra dependency); revisit in v0.2.0.

### 8.3 L2 — live smoke (deferred)

Real agent-browser launches against real services, validates snapshot structure. Requires logged-in profile + careful flake handling. Deferred to v0.2.0+; v0.1.0 relies on user dogfood.

## 9. Risks and known unimplemented points

1. **Chrome SQLite cookie database lock contention (shared mode)** — agent-browser already handles macOS Keychain (verified via source code in `cli/src/native/cdp/chrome.rs`: `use_real_keychain` auto-set when profile is a name). SQLite lock contention during heavy Chrome write activity is theoretically possible but not observed in agent-browser docs. Mitigation: single retry-after-2s in abx wrapper; user message to switch to dedicated mode.
2. **UI evolution every 6-12 months** — semantic-first selectors significantly extend the meantime-to-break, but each service will eventually rename a button or restructure navigation. Each skill's `references/failure-modes.md` documents the playbook for updating `references/ui-patterns.md`.
3. **Slack search operator fidelity through UI search box** — Slack web supports `from:` / `in:` / `before:` / `after:` operators in the search input. ARIA label fallback path needed if the role+name lookup is brittle. Implementation note for `slack-automate/protocols/search-messages.md`.
4. **Gmail UI density** — Gmail has multiple list-density modes and Categories tabs; protocols must handle both Default and Comfortable view, and explicit Category navigation. `gmail-automate/references/ui-patterns.md` captures the conventions.
5. **Notion dynamic loading** — Notion lazy-loads database rows on scroll; `notion-automate/protocols/database-query.md` may need `abx wait` between scrolls. Pagination handling deferred to implementation.
6. **GCal find-free-slots algorithm correctness** — depends on parsing event blocks across multiple days; brittle if Google changes calendar grid markup. Worth a unit test on a fixture.
7. **First-run idempotency** — running `/collab-setup` twice should be safe (re-detect, re-write config, re-verify). Implementation must guard against double-install of brew/npm.
8. **No CI for live smoke** — v0.1.0 ships without L2 coverage. User dogfood is the validation gate.
9. **`allowed-tools` allowlist for `abx`** — Resolved by XDG path choice: abx installs at `$HOME/.local/bin/abx`, which is on PATH by default for most modern macOS / Linux setups (Homebrew shellenv, most Linux distros). SKILL.md whitelists `Bash(abx:*)` and Claude Code resolves it via PATH. Remaining edge case: users whose PATH does not include `$HOME/.local/bin` get a printed warning from `setup.sh` with the export-line they need to add to their shell rc; the verify step fails until PATH is fixed.

## 10. Out of scope (v0.2.0+)

- **Write operations** per service (send message, create task, update event, append page) — deferred for safety + UX (write protocols need confirmation flows)
- **Cross-skill orchestration** — `productivity-orchestrate` skill chaining e.g. Slack search → Asana task-list → GCal agenda-view → Notion page-fetch
- **Multi-workspace per app** — `--workspace` argument and per-workspace profiles
- **Live smoke (L2)** testing infrastructure
- **State save / restore for CI environments** — `agent-browser state save` flow for `mode=dedicated` portability across machines
- **Additional services** — Linear, Todoist, GitHub Projects, Figma (each adds a `<service>-automate` skill following the same template)
- **Notion AI / Slack Workflow Builder / Gmail Smart Compose UI flows** — interactive UI features beyond pure read

## 11. References

- agent-browser source: <https://github.com/vercel-labs/agent-browser>
- agent-browser core skill: `https://github.com/vercel-labs/agent-browser/tree/main/skill-data/core`
- agent-browser slack skill (companion for ours): `https://github.com/vercel-labs/agent-browser/tree/main/skill-data/slack`
- agent-browser electron skill (background for design choice): `https://github.com/vercel-labs/agent-browser/tree/main/skill-data/electron`
- agent-browser Chrome launch source (Keychain handling): `cli/src/native/cdp/chrome.rs`
- monkey-skills CLAUDE.md "Skill Structure" rule: project root
- monkey-skills `feedback_plugin_metadata_conventions.md` (memory): plugin.json location + Cowork marking + TTY handoff
- monkey-skills `feedback_subagent_driven_development_validated.md` (memory): 10-task plan pattern
- Industry context on Playwright Chrome profile reuse + macOS Keychain issue: <https://dev.to/zoetaka38/persisting-your-real-chrome-login-across-playwright-restarts-on-macos-126a>
- Brainstorming session (this design): user dialogue from 2026-05-15, captured in commit history
