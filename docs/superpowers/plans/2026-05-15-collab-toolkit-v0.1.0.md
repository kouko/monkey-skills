# collab-toolkit v0.1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `collab-toolkit` v0.1.0 — a new `monkey-skills` plugin packaging 5 read-only office-collaboration skills (Asana / Slack / Notion / Google Calendar / Gmail) wrapping `vercel-labs/agent-browser`, plus a `/collab-setup` slash command for one-time bootstrap.

**Architecture:** Web headless browser automation via agent-browser. Hybrid Chrome profile mode (shared = read user's daily Chrome profile by name, default; dedicated = per-service path, opt-in). Semantic-first selectors via `jq` filter on `agent-browser snapshot --json`. `abx` wrapper at `$HOME/.local/bin/abx` centralizes profile-arg resolution. XDG Base Directory paths for config + data. Each skill ships with SKILL.md + 4 protocol files + 2 reference files. Spec source: `docs/superpowers/specs/2026-05-15-collab-toolkit-v0.1.0-design.md`.

**Tech Stack:** Bash, jq, `agent-browser` (Rust CLI), bats-core (L1 unit tests), Chrome for Testing (managed by agent-browser).

**Spec divergence noted**: Spec §8.2 prescribes per-skill jq-filter bats tests against captured real snapshots. v0.1.0 ships only L0 (CI structure) + L1-setup + L1-abx bats coverage. L1-jq deferred to v0.2.0 backlog (needs real fixtures from working v0.1.0 dogfood).

---

## File Structure

**Plugin scaffold** (all new):

```
collab-toolkit/                              ← plugin root, sits at monkey-skills repo top-level
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── README.ja.md
├── README.zh-TW.md
├── commands/
│   └── collab-setup.md
├── scripts/
│   ├── setup.sh                            # /collab-setup back-end
│   ├── abx                                 # wrapper, copied to $HOME/.local/bin/ at setup
│   └── tests/
│       ├── test-abx.bats                   # L1 abx wrapper unit tests
│       └── test-setup.bats                 # L1 setup.sh unit tests
└── skills/
    ├── asana-automate/
    │   ├── SKILL.md
    │   ├── protocols/{task-list,task-detail,project-overview,search-global}.md
    │   └── references/{ui-patterns,failure-modes}.md
    ├── slack-automate/
    │   ├── SKILL.md
    │   ├── protocols/{search-messages,channel-read,thread-read,find-user}.md
    │   └── references/{ui-patterns,failure-modes}.md
    ├── notion-automate/
    │   ├── SKILL.md
    │   ├── protocols/{search-workspace,page-fetch,database-query,page-backlinks}.md
    │   └── references/{ui-patterns,failure-modes}.md
    ├── gcal-automate/
    │   ├── SKILL.md
    │   ├── protocols/{agenda-view,event-search,find-free-slots,shared-calendar-read}.md
    │   └── references/{ui-patterns,failure-modes}.md
    └── gmail-automate/
        ├── SKILL.md
        ├── protocols/{mail-search,thread-read,inbox-summary,label-read}.md
        └── references/{ui-patterns,failure-modes}.md
```

**Modify** (existing files):
- `.claude-plugin/marketplace.json` — append `collab-toolkit` entry

---

## Task 1: Plugin scaffold + marketplace entry

**Files:**
- Create: `collab-toolkit/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json` (append entry)

- [ ] **Step 1: Create `collab-toolkit/.claude-plugin/plugin.json`**

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

- [ ] **Step 2: Append entry to `.claude-plugin/marketplace.json`**

Locate the `plugins` array, append (preserving array order — append at end):

```json
{
  "name": "collab-toolkit",
  "description": "Browser automation toolkit wrapping vercel-labs/agent-browser. 5 read-only office-collaboration skills (Asana / Slack / Notion / Google Calendar / Gmail) — search, list, fetch via semantic-first selectors over Chrome (shared profile by default, dedicated profile opt-in). Headless background after one-time /collab-setup. ⚠️ Claude Code CLI only — Cowork sandbox blocks browser launch.",
  "source": "./collab-toolkit/"
}
```

**Important**: description field must match `plugin.json` description verbatim (CI enforces).

- [ ] **Step 3: Run marketplace description sync check**

```bash
python scripts/check-marketplace-description-sync.py
```

Expected: PASS (no drift between plugin.json and marketplace.json).

- [ ] **Step 4: Run skill structure check (plugin level)**

```bash
python scripts/check-skill-structure.py
```

Expected: PASS for collab-toolkit at plugin level (no skills yet — just plugin metadata).

- [ ] **Step 5: Commit**

```bash
git add collab-toolkit/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(collab-toolkit): scaffold plugin metadata + marketplace entry"
```

---

## Task 2: Implement `abx` wrapper (TDD)

**Files:**
- Create: `collab-toolkit/scripts/tests/test-abx.bats`
- Create: `collab-toolkit/scripts/abx`

- [ ] **Step 1: Create test file `collab-toolkit/scripts/tests/test-abx.bats`**

```bash
#!/usr/bin/env bats

# Set up isolated test environment
setup() {
  export TEST_TMPDIR="$(mktemp -d)"
  export HOME="$TEST_TMPDIR"
  export XDG_CONFIG_HOME="$TEST_TMPDIR/.config"
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"

  # Stub agent-browser to echo invocation
  export PATH="$TEST_TMPDIR/bin:$PATH"
  mkdir -p "$TEST_TMPDIR/bin"
  cat > "$TEST_TMPDIR/bin/agent-browser" <<'EOF'
#!/usr/bin/env bash
echo "agent-browser $*"
EOF
  chmod +x "$TEST_TMPDIR/bin/agent-browser"
}

teardown() {
  rm -rf "$TEST_TMPDIR"
}

abx() {
  bash "${BATS_TEST_DIRNAME}/../abx" "$@"
}

@test "abx exits with ERR when config.json missing" {
  run abx open https://example.com
  [ "$status" -ne 0 ]
  [[ "$output" == *"config.json not found"* ]]
  [[ "$output" == *"Run /collab-setup first"* ]]
}

@test "abx with shared mode uses chrome_profile name" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default", "profiles_root": "~/.local/share/collab-toolkit/profiles" }
JSON
  run abx open https://example.com
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile Default"* ]]
  [[ "$output" == *"open https://example.com"* ]]
}

@test "abx with shared mode picks user-chosen profile name" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Work", "profiles_root": "~/.local/share/collab-toolkit/profiles" }
JSON
  run abx snapshot -i
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile Work"* ]]
  [[ "$output" == *"snapshot -i"* ]]
}

@test "abx with dedicated mode and ABX_SERVICE uses path" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<JSON
{ "mode": "dedicated", "chrome_profile": "Default", "profiles_root": "$TEST_TMPDIR/.local/share/collab-toolkit/profiles" }
JSON
  ABX_SERVICE=asana run abx open https://app.asana.com
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile $TEST_TMPDIR/.local/share/collab-toolkit/profiles/asana"* ]]
}

@test "abx with dedicated mode without ABX_SERVICE falls back to chrome_profile name" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "dedicated", "chrome_profile": "Default", "profiles_root": "~/.local/share/collab-toolkit/profiles" }
JSON
  run abx open https://example.com
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile Default"* ]]
}

@test "abx with dedicated mode expands tilde in profiles_root" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "dedicated", "chrome_profile": "Default", "profiles_root": "~/myprofiles" }
JSON
  ABX_SERVICE=slack run abx get title
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile $HOME/myprofiles/slack"* ]]
}
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd collab-toolkit && bats scripts/tests/test-abx.bats
```

Expected: 6 tests fail with "abx: command not found" or similar (file not yet created).

- [ ] **Step 3: Create `collab-toolkit/scripts/abx`**

```bash
#!/usr/bin/env bash
# abx — agent-browser eXtended wrapper.
# Resolves profile arg from ~/.config/collab-toolkit/config.json,
# then `exec agent-browser` with --profile prepended.

set -euo pipefail

CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/collab-toolkit/config.json"
SERVICE="${ABX_SERVICE:-}"

if [ ! -f "$CONFIG" ]; then
  echo "ERR: $CONFIG not found. Run /collab-setup first." >&2
  exit 1
fi

MODE=$(jq -r .mode "$CONFIG")

if [ "$MODE" = "dedicated" ] && [ -n "$SERVICE" ]; then
  PROFILES_ROOT=$(jq -r .profiles_root "$CONFIG")
  # Tilde expansion
  PROFILES_ROOT="${PROFILES_ROOT/#\~/$HOME}"
  exec agent-browser --profile "${PROFILES_ROOT}/${SERVICE}" "$@"
else
  PROFILE_NAME=$(jq -r .chrome_profile "$CONFIG")
  exec agent-browser --profile "$PROFILE_NAME" "$@"
fi
```

- [ ] **Step 4: Make `abx` executable**

```bash
chmod +x collab-toolkit/scripts/abx
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
cd collab-toolkit && bats scripts/tests/test-abx.bats
```

Expected: 6 tests pass.

- [ ] **Step 6: Commit**

```bash
git add collab-toolkit/scripts/abx collab-toolkit/scripts/tests/test-abx.bats
git commit -m "feat(collab-toolkit): add abx profile-resolving wrapper + bats unit tests"
```

---

## Task 3: Implement `setup.sh` (TDD)

**Files:**
- Create: `collab-toolkit/scripts/tests/test-setup.bats`
- Create: `collab-toolkit/scripts/setup.sh`

- [ ] **Step 1: Create test file `collab-toolkit/scripts/tests/test-setup.bats`**

```bash
#!/usr/bin/env bats

setup() {
  export TEST_TMPDIR="$(mktemp -d)"
  export HOME="$TEST_TMPDIR"
  export XDG_CONFIG_HOME="$TEST_TMPDIR/.config"
  export XDG_DATA_HOME="$TEST_TMPDIR/.local/share"
  export ORIG_PATH="$PATH"
  export PATH="$TEST_TMPDIR/bin:$PATH"
  mkdir -p "$TEST_TMPDIR/bin"

  # Source setup.sh helpers — we test functions in isolation
  source "${BATS_TEST_DIRNAME}/../setup.sh" --source-only 2>/dev/null || true
}

teardown() {
  rm -rf "$TEST_TMPDIR"
}

# Helper to stub a command on PATH
stub_command() {
  local name="$1"
  local script="$2"
  cat > "$TEST_TMPDIR/bin/$name" <<EOF
#!/usr/bin/env bash
$script
EOF
  chmod +x "$TEST_TMPDIR/bin/$name"
}

@test "xdg_config_home defaults to \$HOME/.config" {
  run xdg_config_home
  [ "$output" = "$HOME/.config" ]
}

@test "xdg_config_home respects XDG_CONFIG_HOME env" {
  XDG_CONFIG_HOME="/custom/path" run xdg_config_home
  [ "$output" = "/custom/path" ]
}

@test "xdg_data_home defaults to \$HOME/.local/share" {
  run xdg_data_home
  [ "$output" = "$HOME/.local/share" ]
}

@test "xdg_bin_home is \$HOME/.local/bin" {
  run xdg_bin_home
  [ "$output" = "$HOME/.local/bin" ]
}

@test "install_agent_browser is no-op when already installed" {
  stub_command agent-browser 'exit 0'
  run install_agent_browser
  [ "$status" -eq 0 ]
}

@test "install_agent_browser on macOS with brew uses brew" {
  OSTYPE="darwin23"
  stub_command brew 'echo "brew $*"; exit 0'
  PATH="$TEST_TMPDIR/bin:$ORIG_PATH"   # don't yet have agent-browser
  rm -f "$TEST_TMPDIR/bin/agent-browser"

  run install_agent_browser
  [ "$status" -eq 0 ]
  [[ "$output" == *"brew install agent-browser"* ]]
}

@test "install_agent_browser on Linux uses npm" {
  OSTYPE="linux-gnu"
  stub_command npm 'echo "npm $*"; exit 0'
  rm -f "$TEST_TMPDIR/bin/agent-browser"

  run install_agent_browser
  [ "$status" -eq 0 ]
  [[ "$output" == *"npm i -g agent-browser"* ]]
}

@test "install_agent_browser brew failure falls back to npm" {
  OSTYPE="darwin23"
  stub_command brew 'echo "brew failure" >&2; exit 1'
  stub_command npm 'echo "npm $*"; exit 0'
  rm -f "$TEST_TMPDIR/bin/agent-browser"

  run install_agent_browser
  [ "$status" -eq 0 ]
  [[ "$output" == *"npm i -g agent-browser"* ]]
}

@test "install_abx copies wrapper to \$HOME/.local/bin" {
  mkdir -p "$TEST_TMPDIR/scripts"
  cat > "$TEST_TMPDIR/scripts/abx" <<'EOF'
#!/usr/bin/env bash
echo "abx-stub"
EOF

  # Simulate scripts/setup.sh dirname resolution
  cd "$TEST_TMPDIR/scripts"

  run install_abx
  [ "$status" -eq 0 ]
  [ -x "$HOME/.local/bin/abx" ]
}

@test "install_abx warns if \$HOME/.local/bin not on PATH" {
  mkdir -p "$TEST_TMPDIR/scripts"
  echo "#!/bin/sh" > "$TEST_TMPDIR/scripts/abx"
  cd "$TEST_TMPDIR/scripts"

  PATH="/usr/bin:/bin" run install_abx
  [[ "$output" == *"not on PATH"* ]]
  [[ "$output" == *'export PATH="$HOME/.local/bin:$PATH"'* ]]
}

@test "write_config_shared creates valid JSON" {
  run write_config_shared "Default"
  [ "$status" -eq 0 ]
  [ -f "$XDG_CONFIG_HOME/collab-toolkit/config.json" ]

  mode=$(jq -r .mode "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$mode" = "shared" ]
  profile=$(jq -r .chrome_profile "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$profile" = "Default" ]
}

@test "write_config_shared accepts custom profile name" {
  run write_config_shared "Work"
  [ "$status" -eq 0 ]
  profile=$(jq -r .chrome_profile "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$profile" = "Work" ]
}

@test "write_config_dedicated creates valid JSON with dedicated mode" {
  run write_config_dedicated
  [ "$status" -eq 0 ]
  mode=$(jq -r .mode "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$mode" = "dedicated" ]
}

@test "setup_dedicated creates 5 profile dirs" {
  # Stub agent-browser + abx so login phase is no-op
  stub_command agent-browser 'echo "Asana - Inbox"'
  echo '#!/bin/sh' > "$TEST_TMPDIR/bin/abx"; chmod +x "$TEST_TMPDIR/bin/abx"

  # Skip interactive login by overriding setup_one_dedicated
  setup_one_dedicated() { :; }

  run setup_dedicated
  for service in asana slack notion gcal gmail; do
    [ -d "$XDG_DATA_HOME/collab-toolkit/profiles/$service" ]
  done
}

@test "verify_one detects login wall via title" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'if [[ "$*" == *"get title"* ]]; then echo "Sign in - Asana"; else echo ok; fi'
  # abx must exist on PATH so verify_one can call it
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser --profile Default "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one asana
  [[ "$output" == *"NOT logged in"* ]]
  [[ "$output" == *"Sign in - Asana"* ]]
}

@test "verify_one reports ok when title is not a login page" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'if [[ "$*" == *"get title"* ]]; then echo "My Tasks - Asana"; else echo ok; fi'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser --profile Default "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one asana
  [[ "$output" == *"✓ asana ready"* ]]
}

@test "service_url returns expected URL per service" {
  run service_url asana
  [ "$output" = "https://app.asana.com/0/inbox" ]
  run service_url slack
  [ "$output" = "https://app.slack.com" ]
  run service_url notion
  [ "$output" = "https://www.notion.so" ]
  run service_url gcal
  [ "$output" = "https://calendar.google.com" ]
  run service_url gmail
  [ "$output" = "https://mail.google.com" ]
}
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd collab-toolkit && bats scripts/tests/test-setup.bats
```

Expected: all tests fail (setup.sh not yet created).

- [ ] **Step 3: Create `collab-toolkit/scripts/setup.sh`**

```bash
#!/usr/bin/env bash
# setup.sh — back-end for /collab-setup slash command.
# Installs agent-browser, downloads Chrome for Testing, installs abx wrapper,
# writes ~/.config/collab-toolkit/config.json.

set -euo pipefail

# ============================================================================
# XDG path helpers
# ============================================================================

xdg_config_home() { echo "${XDG_CONFIG_HOME:-$HOME/.config}"; }
xdg_data_home()   { echo "${XDG_DATA_HOME:-$HOME/.local/share}"; }
xdg_bin_home()    { echo "$HOME/.local/bin"; }

# Globals (computed at top of main)
CONFIG_DIR=""; DATA_DIR=""; BIN_DIR=""; CONFIG=""; PROFILES_ROOT=""
DEDICATED=false; REAUTH=""; SWITCH=false; VERIFY_ONLY=false; MODE=""

# Source-only mode for bats — when sourced, skip main()
if [ "${1:-}" = "--source-only" ]; then return 0 2>/dev/null || true; fi

# ============================================================================
# Argument parsing
# ============================================================================

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --dedicated)    DEDICATED=true ;;
      --reauth)       REAUTH="$2"; shift ;;
      --switch-mode)  SWITCH=true ;;
      --verify)       VERIFY_ONLY=true ;;
      *) echo "Unknown arg: $1"; exit 2 ;;
    esac
    shift
  done
}

# ============================================================================
# Phase 1: install agent-browser
# ============================================================================

install_agent_browser() {
  if command -v agent-browser >/dev/null 2>&1; then return 0; fi
  if [[ "$OSTYPE" == "darwin"* ]] && command -v brew >/dev/null 2>&1; then
    brew install agent-browser || npm i -g agent-browser
  else
    command -v npm >/dev/null 2>&1 || { echo "ERR: npm required"; exit 1; }
    npm i -g agent-browser
  fi
}

# ============================================================================
# Phase 2: download Chrome for Testing
# ============================================================================

install_chrome() {
  agent-browser install
  agent-browser --version
}

# ============================================================================
# Phase 3: install abx wrapper
# ============================================================================

install_abx() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  mkdir -p "$BIN_DIR"
  cp "$script_dir/abx" "$BIN_DIR/abx"
  chmod +x "$BIN_DIR/abx"
  case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
      echo "⚠️ $BIN_DIR not on PATH. Add to your shell rc:"
      echo '   export PATH="$HOME/.local/bin:$PATH"'
      ;;
  esac
}

# ============================================================================
# Phase 4a: shared mode setup (Option A — default)
# ============================================================================

write_config_shared() {
  local name="$1"
  mkdir -p "$CONFIG_DIR"
  cat > "$CONFIG" <<EOF
{
  "mode": "shared",
  "chrome_profile": "$name",
  "profiles_root": "~/.local/share/collab-toolkit/profiles"
}
EOF
}

setup_shared() {
  echo "Available Chrome profiles:"
  agent-browser profiles || true
  local name
  read -rp "Profile name to use [Default]: " name
  name="${name:-Default}"
  write_config_shared "$name"
  MODE=shared
  verify_all_services
}

# ============================================================================
# Phase 4b: dedicated mode setup (Option B — opt-in)
# ============================================================================

write_config_dedicated() {
  mkdir -p "$CONFIG_DIR"
  cat > "$CONFIG" <<EOF
{
  "mode": "dedicated",
  "chrome_profile": "Default",
  "profiles_root": "$PROFILES_ROOT"
}
EOF
}

setup_dedicated() {
  mkdir -p "$PROFILES_ROOT"/{asana,slack,notion,gcal,gmail}
  write_config_dedicated
  MODE=dedicated
  for service in asana slack notion gcal gmail; do
    setup_one_dedicated "$service"
  done
}

setup_one_dedicated() {
  local service="$1"
  local url
  url=$(service_url "$service")
  echo "→ Opening $service (--headed). Log in, then press Enter."
  agent-browser --headed --profile "$PROFILES_ROOT/$service" open "$url"
  read -rp "Press Enter when logged in: "
  verify_one "$service"
}

# ============================================================================
# Verification
# ============================================================================

verify_all_services() {
  for service in asana slack notion gcal gmail; do
    verify_one "$service"
  done
}

verify_one() {
  local service="$1"
  local url title
  url=$(service_url "$service")
  ABX_SERVICE="$service" "$BIN_DIR/abx" open "$url" >/dev/null
  title=$(ABX_SERVICE="$service" "$BIN_DIR/abx" get title)
  case "$title" in
    *"Sign in"*|*"Log in"*|*"Login"*)
      echo "⚠️ $service: NOT logged in (title: $title)"
      [ "$MODE" = "shared" ]    && echo "   → Log into $service in your daily Chrome, then re-run /collab-setup --verify"
      [ "$MODE" = "dedicated" ] && echo "   → Run: /collab-setup --reauth $service"
      ;;
    *) echo "✓ $service ready (title: $title)" ;;
  esac
}

service_url() {
  case "$1" in
    asana)  echo "https://app.asana.com/0/inbox" ;;
    slack)  echo "https://app.slack.com" ;;
    notion) echo "https://www.notion.so" ;;
    gcal)   echo "https://calendar.google.com" ;;
    gmail)  echo "https://mail.google.com" ;;
    *) echo "ERR: unknown service: $1" >&2; exit 1 ;;
  esac
}

current_mode() {
  [ -f "$CONFIG" ] && jq -r .mode "$CONFIG" || echo ""
}

# ============================================================================
# Main
# ============================================================================

main() {
  CONFIG_DIR="$(xdg_config_home)/collab-toolkit"
  DATA_DIR="$(xdg_data_home)/collab-toolkit"
  BIN_DIR="$(xdg_bin_home)"
  CONFIG="$CONFIG_DIR/config.json"
  PROFILES_ROOT="$DATA_DIR/profiles"
  mkdir -p "$CONFIG_DIR" "$DATA_DIR" "$BIN_DIR"

  parse_args "$@"

  if $VERIFY_ONLY; then
    MODE="$(current_mode)"
    verify_all_services
    return
  fi

  if [ -n "$REAUTH" ]; then
    setup_one_dedicated "$REAUTH"
    return
  fi

  install_agent_browser
  install_chrome
  install_abx

  if $DEDICATED || ($SWITCH && [ "$(current_mode)" = "shared" ]); then
    setup_dedicated
  else
    setup_shared
  fi
}

# Skip main() if sourced (for bats)
(return 0 2>/dev/null) && return 0
main "$@"
```

- [ ] **Step 4: Make setup.sh executable**

```bash
chmod +x collab-toolkit/scripts/setup.sh
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
cd collab-toolkit && bats scripts/tests/test-setup.bats
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add collab-toolkit/scripts/setup.sh collab-toolkit/scripts/tests/test-setup.bats
git commit -m "feat(collab-toolkit): add setup.sh bootstrap script + bats unit tests"
```

---

## Task 4: `/collab-setup` slash command

**Files:**
- Create: `collab-toolkit/commands/collab-setup.md`

- [ ] **Step 1: Create slash command file**

```markdown
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
```

- [ ] **Step 2: Run skill structure check**

```bash
python scripts/check-skill-structure.py
```

Expected: PASS for the new command file.

- [ ] **Step 3: Commit**

```bash
git add collab-toolkit/commands/collab-setup.md
git commit -m "feat(collab-toolkit): add /collab-setup slash command wiring setup.sh"
```

---

## Task 5: `asana-automate` skill

**Files:**
- Create: `collab-toolkit/skills/asana-automate/SKILL.md`
- Create: `collab-toolkit/skills/asana-automate/protocols/task-list.md`
- Create: `collab-toolkit/skills/asana-automate/protocols/task-detail.md`
- Create: `collab-toolkit/skills/asana-automate/protocols/project-overview.md`
- Create: `collab-toolkit/skills/asana-automate/protocols/search-global.md`
- Create: `collab-toolkit/skills/asana-automate/references/ui-patterns.md`
- Create: `collab-toolkit/skills/asana-automate/references/failure-modes.md`

Spec reference: §4 (folder layout), §5.7 (SKILL.md template), §5.8 (protocol template), §5.9 (ui-patterns template), §5.10 (failure-modes template).

- [ ] **Step 1: Create `SKILL.md`**

```markdown
---
name: asana-automate
description: Asana automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: task-list across projects with filtering, task-detail with subtasks/comments/attachments, project-overview with section counts, search-global across tasks and portfolios. Read-only v0.1.0 — search and fetch only, no writes. Asana 自動化、タスク読取、ヘッドレス。Asana 自動化・任務讀取・無頭背景。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# asana-automate

Read-only browser automation for Asana. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed and on PATH
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- Asana is verified logged-in via your daily Chrome (shared mode) or dedicated profile

If any protocol fails with "config not found": run `/collab-setup`.
If any protocol fails with "login wall detected" in title: per setup mode, either log into Asana in your daily Chrome (shared mode) or run `/collab-setup --reauth asana` (dedicated mode).

## Hero protocols

- `protocols/task-list.md` — list My Tasks across projects, filterable by due-date, status, custom field
- `protocols/task-detail.md` — full task content with subtasks, comments, attachments, custom field values
- `protocols/project-overview.md` — list all projects with sections, task counts, recent activity
- `protocols/search-global.md` — full-text search across tasks, projects, portfolios with filters

## Selector convention

See `references/ui-patterns.md`. All protocols MUST:
1. `ABX_SERVICE=asana abx snapshot -i --json` → save to /tmp
2. `jq '.elements[] | select(.role==X and .name==Y) | .ref' | head -1`
3. Empty result → exit with "UI changed: <role>+<name> not found"

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default: human-readable Markdown summary.
`--json` (passthrough to abx): structured JSON for downstream chaining.
```

- [ ] **Step 2: Create `protocols/task-list.md`**

```markdown
---
name: task-list
purpose: List My Tasks across all projects with optional filters (due-date / status / custom field).
---

## Inputs

- `filter_due`: optional. One of `today` / `this-week` / `overdue` / `all`. Default: `all`.
- `filter_status`: optional. One of `incomplete` / `complete` / `all`. Default: `incomplete`.
- `--json`: optional. Output structured JSON.

## Output

Default Markdown:
```
## My Tasks (15)

### Today (3)
- [ ] Refactor auth middleware — Project: Backend / Section: Engineering — Due: today
- [ ] Code review PR #234 — Project: Backend / Section: Reviews — Due: today
- [x] Standup notes — Project: Eng Ops / Section: Daily — Due: today (completed)

### This week (12)
- [ ] ... (truncated for plan; full output shows all tasks)
```

`--json` shape:
```json
{
  "total": 15,
  "tasks": [
    {
      "id": "extracted from data-task-id attribute",
      "title": "Refactor auth middleware",
      "project": "Backend",
      "section": "Engineering",
      "due_date": "2026-05-15",
      "status": "incomplete",
      "url": "https://app.asana.com/0/<workspace>/<task_id>"
    }
  ]
}
```

## Procedure (semantic-first, no hardcoded refs)

```bash
# Prerequisite: $HOME/.local/bin must be on PATH; /collab-setup ensures this.

# 1. Open My Tasks
ABX_SERVICE=asana abx open https://app.asana.com/0/inbox
ABX_SERVICE=asana abx wait --load networkidle

# 2. Navigate to My Tasks (via sidebar)
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)
MYTASKS_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="link" and .name=="My tasks") | .ref' | head -1)
[ -z "$MYTASKS_REF" ] && { echo "ERR: UI changed: 'My tasks' link not found in sidebar"; exit 1; }
ABX_SERVICE=asana abx click "$MYTASKS_REF"
ABX_SERVICE=asana abx wait --load networkidle

# 3. Snapshot task list
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)

# 4. Extract task rows
# Each task is role="row" within a role="grid" parent. Task title is in role="link" child.
echo "$SNAP" | jq -r '
  [.elements[]
    | select(.role=="row")
    | {
        title: ([.children[]? | select(.role=="link" and .name != "") | .name] | first // "(untitled)"),
        ref: .ref
      }
  ] | .[]
  | "- \(.title)"
'

# 5. (Optional --json mode) Emit JSON
# Replace the markdown step above with:
# echo "$SNAP" | jq '[.elements[] | select(.role=="row") | {title, ref, ...}]'
```

## Failure modes

- "UI changed: 'My tasks' link not found in sidebar" → references/failure-modes.md → "UI evolution"
- Login wall (title contains "Sign in") → references/failure-modes.md → "Auth expiry"
- Empty grid (no tasks) → valid empty result, output "No tasks matching filter"

## Examples

User invocation: "show my Asana tasks due this week"

Expected output (Markdown mode): list of tasks grouped by due-date with title / project / section / status.

`--json` mode returns structured JSON for downstream piping (e.g., to gmail-automate to email summary, or to notion-automate to log).
```

- [ ] **Step 3: Create `protocols/task-detail.md`**

```markdown
---
name: task-detail
purpose: Fetch full detail of a single task — title, description, subtasks, comments, attachments, custom field values.
---

## Inputs

- `task_url`: required. Full Asana task URL (e.g., `https://app.asana.com/0/<workspace>/<task_id>`).
- `--json`: optional.

## Output

Default Markdown:
```
# Refactor auth middleware
**Project**: Backend / Engineering
**Assignee**: kouko
**Due**: 2026-05-15
**Status**: incomplete

## Description
Replace the legacy session middleware with the new compliance-aligned implementation...

## Subtasks (3)
- [x] Write design doc
- [ ] Implement new middleware
- [ ] Migrate existing routes

## Comments (5)
**Alice (2026-05-14)**: Looks good, but check the rate-limiter integration.
...

## Attachments (2)
- design-doc.pdf
- arch-diagram.png
```

`--json` shape: full task object with all fields above as JSON.

## Procedure

```bash
TASK_URL="$1"
[ -z "$TASK_URL" ] && { echo "ERR: task_url required"; exit 1; }

ABX_SERVICE=asana abx open "$TASK_URL"
ABX_SERVICE=asana abx wait --load networkidle
SNAP=$(ABX_SERVICE=asana abx snapshot --json)

# Title — role="heading" level=1
TITLE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="heading" and .level==1) | .name' | head -1)

# Assignee — element with aria label containing "Assignee"
ASSIGNEE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name|startswith("Assignee"))) | .name' | head -1)

# Due date — element with aria label containing "Due date"
DUE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name|startswith("Due"))) | .name' | head -1)

# Description — role="textbox" or role="region" with aria-label="Description"
DESC=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="region" and .name=="Description") | .text' | head -1)

# Subtasks — role="list" with aria-label="Subtasks" → children are role="listitem"
SUBTASKS=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="list" and .name=="Subtasks") | .children[]? | select(.role=="listitem") | "- [\(if .checked then "x" else " " end)] \(.name)"')

# Comments — role="article" elements within "Activity" section
COMMENTS=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="article") | "**\(.author) (\(.timestamp))**: \(.text)"')

# Attachments — role="list" with aria-label="Attachments"
ATTACHMENTS=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="list" and .name=="Attachments") | .children[]? | .name' | sed 's/^/- /')

# Emit markdown
cat <<EOF
# $TITLE
**Assignee**: ${ASSIGNEE#Assignee, }
**Due**: ${DUE#Due date, }

## Description
$DESC

## Subtasks
$SUBTASKS

## Comments
$COMMENTS

## Attachments
$ATTACHMENTS
EOF
```

## Failure modes

- Title missing → likely on login page → "Auth expiry"
- Task not found (404 title) → invalid URL → tell user to verify URL

## Examples

Input: `task_url=https://app.asana.com/0/1234/5678`

Expected: full task detail rendered as Markdown.
```

- [ ] **Step 4: Create `protocols/project-overview.md`**

```markdown
---
name: project-overview
purpose: List all projects user has access to, with sections and task counts.
---

## Inputs

- None (lists all accessible projects).
- `--json`: optional.

## Output

Default Markdown:
```
## Projects (12)

### Backend (kouko, public)
- Engineering (8 tasks, 3 incomplete)
- Reviews (5 tasks, 5 incomplete)
- Operations (2 tasks, 0 incomplete)

### Frontend (kouko, public)
- ...
```

`--json`: array of `{name, owner, visibility, sections: [{name, total, incomplete}]}`.

## Procedure

```bash
ABX_SERVICE=asana abx open https://app.asana.com/0/projects
ABX_SERVICE=asana abx wait --load networkidle
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)

# Each project = role="row" within a grid, with name in role="link"
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | ([.children[]? | select(.role=="link") | .name] | first // "(unnamed)")
' | while read -r project; do
  echo "### $project"
done

# For each project, navigate and snapshot sections
# (loop is illustrative; production implementation may batch via agent-browser tabs)
```

## Failure modes

- "Projects" page empty → user has no projects (valid empty result)
- Login wall → "Auth expiry"
```

- [ ] **Step 5: Create `protocols/search-global.md`**

```markdown
---
name: search-global
purpose: Full-text search across tasks, projects, and portfolios with optional filters.
---

## Inputs

- `query`: required. Search string.
- `filter_type`: optional. One of `tasks` / `projects` / `portfolios` / `all`. Default: `all`.
- `--json`: optional.

## Output

Default Markdown groups results by type with relevance order:
```
## Search results for "OKR" (24 matches)

### Tasks (15)
- Q2 OKR planning — Project: Engineering — kouko
- ...

### Projects (3)
- OKR Tracker — Owner: alice
- ...

### Portfolios (1)
- Company OKRs Q2 2026 — Owner: ceo
```

`--json`: `{ query, total, tasks: [...], projects: [...], portfolios: [...] }`.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=asana abx open https://app.asana.com/0/inbox
ABX_SERVICE=asana abx wait --load networkidle

# Find Search button — role="button" name="Search"
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and .name=="Search") | .ref' | head -1)
[ -z "$SEARCH_REF" ] && { echo "ERR: UI changed: 'Search' button not found"; exit 1; }
ABX_SERVICE=asana abx click "$SEARCH_REF"
ABX_SERVICE=asana abx wait 500

# Type query into the active search input
ABX_SERVICE=asana abx fill --active "$QUERY"
ABX_SERVICE=asana abx press Enter
ABX_SERVICE=asana abx wait --load networkidle

# Snapshot results page
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)

# Results have role="row" within result groups
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | "- \(.name // "(untitled)")"
'
```

## Failure modes

- "Search" button not found → UI evolution
- No results → valid empty result
```

- [ ] **Step 6: Create `references/ui-patterns.md`**

```markdown
# Asana UI Patterns — Semantic Selector Reference

> **Source of truth for semantic selectors used in this skill's protocols.**
> When Asana ships a UI change that breaks a protocol, update this file first,
> then re-derive the protocol's jq filter.

## Refresh playbook

When a protocol fails with "UI changed: ...":

1. Run `ABX_SERVICE=asana abx snapshot -i --json > /tmp/asana-snap.json` against the affected page
2. Inspect `/tmp/asana-snap.json` for elements near the failing area
3. Identify the new role+name combination
4. Update the entry below
5. Update the failing protocol's jq filter

## Navigation (sidebar / top bar)

| Element | role | name | Notes |
|---|---|---|---|
| Sidebar — My Tasks link | `link` | `My tasks` | Persistent across pages |
| Sidebar — Projects link | `link` | `Projects` | Persistent across pages |
| Sidebar — Inbox link | `link` | `Inbox` | Persistent across pages |
| Top bar — Search button | `button` | `Search` | Opens search modal/input |
| Top bar — User menu | `button` | aria-label contains user name | Per-user variation |

## Task lists (grid views)

| Element | role | name | Notes |
|---|---|---|---|
| Grid container | `grid` | aria-label `Tasks` or `My tasks` | Container for all rows |
| Task row | `row` | (varies — task title via child link) | Each task is a row |
| Task title (within row) | `link` | (task title string) | First link child in row |
| Task completion checkbox | `checkbox` | `Mark complete` | Toggles completion |
| Task due date | `button` | starts with `Due date,` | aria-label includes current value |

## Task detail page

| Element | role | name | Notes |
|---|---|---|---|
| Page title | `heading` level=1 | (task title) | The H1 of the task page |
| Assignee | `button` | starts with `Assignee,` | aria-label includes current value |
| Description region | `region` | `Description` | Contains rich text |
| Subtasks list | `list` | `Subtasks` | Children are listitems |
| Activity comments | `article` | (none — has `.author` and `.text` props) | Each comment is an article |
| Attachments list | `list` | `Attachments` | Children are listitems |

## Search results

| Element | role | name | Notes |
|---|---|---|---|
| Result row | `row` | (result title) | Within result groups |
| Result group header | `heading` level=2 | one of `Tasks` / `Projects` / `Portfolios` | Section dividers |
```

- [ ] **Step 7: Create `references/failure-modes.md`**

```markdown
# Asana Failure Modes

## UI evolution

**Symptom**: Protocol exits with `ERR: UI changed: <role>+<name> not found`.

**Cause**: Asana renamed an element, changed a role, or restructured navigation.

**Remediation**:
1. Open `references/ui-patterns.md` and locate the failing entry
2. Run `ABX_SERVICE=asana abx snapshot -i --json > /tmp/snap.json` against the affected page
3. Find the new role+name combination via `jq 'select(...)'`
4. Update `references/ui-patterns.md` entry
5. Update the protocol's jq filter to match
6. Re-run protocol to verify fix

## Auth expiry / login wall

**Symptom**: Page title contains `Sign in` / `Log in` / `Login`, OR URL redirects to `*asana.com/-/login*`.

**Cause**: Asana session expired.

**Remediation**:
- **Shared profile mode**: Open Asana in your daily Chrome, log in. Next protocol invocation picks up fresh cookies.
- **Dedicated profile mode**: Run `/collab-setup --reauth asana`.

Protocols MUST fail fast on detection — do not attempt to scrape login state from a logged-out session.

## Empty result vs UI evolution

**Disambiguation**:
- If the expected role appears in the snapshot but no element matches the name → likely valid empty result (e.g., no tasks matching filter)
- If the expected role itself is absent from the snapshot → UI evolved, treat as error

Protocols emit different output:
- Empty result: `No tasks matching filter`
- UI evolved: `ERR: UI changed: <role>+<name> not found`

## Rate limiting / load failure

**Symptom**: `agent-browser` returns timeout, or page load takes > 25s.

**Cause**: Asana rate-limit, network issue, or slow page.

**Remediation**: agent-browser retries automatically. If persistent:
- Increase `AGENT_BROWSER_TIMEOUT_MS=45000` env var
- Reduce frequency of protocol invocations
```

- [ ] **Step 8: Run skill structure check**

```bash
python scripts/check-skill-structure.py
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add collab-toolkit/skills/asana-automate/
git commit -m "feat(collab-toolkit): add asana-automate skill (4 read protocols + refs)"
```

---

## Task 6: `slack-automate` skill

**Files:**
- Create: `collab-toolkit/skills/slack-automate/SKILL.md`
- Create: `collab-toolkit/skills/slack-automate/protocols/{search-messages,channel-read,thread-read,find-user}.md`
- Create: `collab-toolkit/skills/slack-automate/references/{ui-patterns,failure-modes}.md`

Spec reference: §4, §5.7 (template), §5.8 (template), §5.9 (template), §5.10 (template). Also reference upstream `vercel-labs/agent-browser`'s [`skill-data/slack/SKILL.md`](https://github.com/vercel-labs/agent-browser/blob/main/skill-data/slack/SKILL.md) for Slack UI patterns it has already documented.

- [ ] **Step 1: Create `SKILL.md`**

```markdown
---
name: slack-automate
description: Slack automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: full-text search-messages with from/in/before/after operators, channel-read with thread expansion and reactions, thread-read with all replies/reactions/attachments, find-user by name/email/handle. Read-only v0.1.0 — search and fetch only, no writes. Slack 自動化、メッセージ読取、ヘッドレス。Slack 自動化・訊息讀取・無頭背景。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# slack-automate

Read-only browser automation for Slack. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed and on PATH
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- Slack is verified logged-in

If protocol fails with "config not found" → run `/collab-setup`.
If protocol fails with "login wall detected" → shared: log into Slack in daily Chrome; dedicated: `/collab-setup --reauth slack`.

## Hero protocols

- `protocols/search-messages.md` — full-text search with from:/in:/before:/after: operators
- `protocols/channel-read.md` — recent N messages in a channel with thread expansion
- `protocols/thread-read.md` — entire thread including all replies, reactions, attachments
- `protocols/find-user.md` — user search by name / email / handle, returns profile + activity

## Selector convention

See `references/ui-patterns.md`. Inherits patterns from agent-browser's own slack skill (verified 2026-05 against Slack web). All protocols use `ABX_SERVICE=slack abx snapshot -i --json` then jq filter by role+name.

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default Markdown. `--json` for structured output.
```

- [ ] **Step 2: Create `protocols/search-messages.md`**

```markdown
---
name: search-messages
purpose: Full-text search across all Slack channels with optional operators (from / in / before / after / has).
---

## Inputs

- `query`: required. Search string, may include operators.
- `--json`: optional.

## Output

Default Markdown:
```
## Slack search: "OKR" (in: #engineering after: 2026-05-01) — 12 results

**#engineering** · alice · 2026-05-10 14:32
> Q2 OKRs are due next Friday. Let's align in standup.
> [Open thread →](https://kouko-workspace.slack.com/archives/...)

**#engineering** · bob · 2026-05-08 09:15
> ...
```

`--json`: `{ query, total, results: [{ channel, user, timestamp, text, url, has_thread }] }`.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=slack abx open https://app.slack.com
ABX_SERVICE=slack abx wait --load networkidle

# Open search — role="button" name="Search"
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and .name=="Search") | .ref' | head -1)
[ -z "$SEARCH_REF" ] && { echo "ERR: UI changed: 'Search' button not found"; exit 1; }
ABX_SERVICE=slack abx click "$SEARCH_REF"
ABX_SERVICE=slack abx wait 500

# Type query
ABX_SERVICE=slack abx fill --active "$QUERY"
ABX_SERVICE=slack abx press Enter
ABX_SERVICE=slack abx wait --load networkidle

# Snapshot results — each result is role="listitem" within Search results region
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="listitem" and (.parent.name // "" | startswith("Search results")))
  | "**\(.channel // "(unknown)")** · \(.user // "(unknown)") · \(.timestamp // "")\n> \(.text)\n"
'
```

## Failure modes

- Search button missing → UI evolution
- 0 results for a known-good query → "Auth expiry" check (snapshot for `role=button name=Sign in`)
```

- [ ] **Step 3: Create `protocols/channel-read.md`**

```markdown
---
name: channel-read
purpose: Read recent N messages in a channel, with optional thread expansion.
---

## Inputs

- `channel`: required. Channel name (e.g., `engineering`) or full URL.
- `limit`: optional, default 20. Number of recent messages.
- `expand_threads`: optional bool, default false.
- `--json`: optional.

## Output

Default Markdown:
```
## #engineering (last 20 messages, 3 threads expanded)

**alice** · 2026-05-15 09:00
Standup starting in 5 minutes.
└─ 3 replies (expanded below)
    **bob**: On my way
    ...

**carol** · 2026-05-15 08:45
PR #234 ready for review.
```

`--json`: `[ { user, timestamp, text, thread_count, thread_messages?: [...] } ]`.

## Procedure

```bash
CHANNEL="$1"
LIMIT="${2:-20}"
EXPAND="${3:-false}"

# Resolve channel — name or URL
case "$CHANNEL" in
  http*)
    URL="$CHANNEL"
    ;;
  *)
    # Navigate to workspace, find channel in sidebar
    ABX_SERVICE=slack abx open https://app.slack.com
    ABX_SERVICE=slack abx wait --load networkidle
    SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
    CHANNEL_REF=$(echo "$SNAP" | jq -r --arg c "$CHANNEL" '
      .elements[] | select(.role=="treeitem" and (.name | startswith($c))) | .ref
    ' | head -1)
    [ -z "$CHANNEL_REF" ] && { echo "ERR: Channel '$CHANNEL' not found in sidebar"; exit 1; }
    ABX_SERVICE=slack abx click "$CHANNEL_REF"
    ABX_SERVICE=slack abx wait --load networkidle
    ;;
esac

# Snapshot channel
SNAP=$(ABX_SERVICE=slack abx snapshot --json)

# Each message is role="article" within role="region" name="Conversation"
echo "$SNAP" | jq -r --argjson limit "$LIMIT" '
  [.elements[]
    | select(.role=="article")
    | { user: .author, timestamp: .timestamp, text: .text, thread_count: (.thread_count // 0) }
  ]
  | .[-$limit:]
  | .[]
  | "**\(.user)** · \(.timestamp)\n\(.text)\n"
'

# Thread expansion (if requested) — iterate messages with thread_count > 0, click "N replies" button
# (Implementation: subagent fills in based on thread expansion semantic pattern from references/ui-patterns.md)
```

## Failure modes

- Channel not found in sidebar → user lacks access or channel is hidden under "More"
- Auth expiry → "Auth expiry"
```

- [ ] **Step 4: Create `protocols/thread-read.md`**

```markdown
---
name: thread-read
purpose: Read entire thread including all replies, reactions, attachments.
---

## Inputs

- `thread_url`: required. Slack thread permalink (`https://<workspace>.slack.com/archives/<channel>/p<ts>?thread_ts=...`).
- `--json`: optional.

## Output

Default Markdown: parent message + all replies with reactions and attachment names.

`--json`: `{ parent: { ... }, replies: [...], total_replies, reactions: [...] }`.

## Procedure

```bash
URL="$1"
[ -z "$URL" ] && { echo "ERR: thread_url required"; exit 1; }

ABX_SERVICE=slack abx open "$URL"
ABX_SERVICE=slack abx wait --load networkidle
SNAP=$(ABX_SERVICE=slack abx snapshot --json)

# Thread is shown in a side panel — role="complementary" name="Thread"
# Parent message + replies are role="article" within
echo "$SNAP" | jq -r '
  [.elements[]
    | select(.role=="article" and (.parent.role=="complementary" and .parent.name=="Thread"))
    | { user: .author, timestamp: .timestamp, text: .text, reactions: .reactions, attachments: .attachments }
  ]
  | .[]
  | "**\(.user)** · \(.timestamp)\n\(.text)\n"
'
```

## Failure modes

- Thread URL invalid (404) → message about URL validation
- "Thread" complementary region missing → UI evolution
```

- [ ] **Step 5: Create `protocols/find-user.md`**

```markdown
---
name: find-user
purpose: Search workspace users by name / email / handle, return profile + activity status.
---

## Inputs

- `query`: required. Name fragment, email, or handle.
- `--json`: optional.

## Output

Default Markdown:
```
## User search: "alice"

**Alice Chen** · @alice · alice@company.com · Active (last seen 2 min ago)
Title: Senior Engineer · Team: Platform
Phone: (none) · Timezone: PST

**Alice Lee** · @aliceleel · alice@elsewhere.com · Away (idle 12 min)
...
```

`--json`: array of `{ name, handle, email, status, title, team, timezone, last_seen }`.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=slack abx open https://app.slack.com
ABX_SERVICE=slack abx wait --load networkidle

# Open People view — sidebar link or top bar People button
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
PEOPLE_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="link" and (.name=="People" or .name=="More")) | .ref' | head -1)
[ -z "$PEOPLE_REF" ] && { echo "ERR: People link not found"; exit 1; }
ABX_SERVICE=slack abx click "$PEOPLE_REF"
ABX_SERVICE=slack abx wait --load networkidle

# Type query
ABX_SERVICE=slack abx fill --active "$QUERY"
ABX_SERVICE=slack abx wait 500
SNAP=$(ABX_SERVICE=slack abx snapshot --json)

# User results are role="row" within People grid
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | "\(.name) · \(.handle // "") · \(.email // "") · \(.status // "")"
'
```

## Failure modes

- "People" view not accessible (free Slack tier may not have it) → graceful fallback to mentioning user search via @mention typeahead in any channel
- Auth expiry
```

- [ ] **Step 6: Create `references/ui-patterns.md`**

```markdown
# Slack UI Patterns — Semantic Selector Reference

Inherits and extends patterns from agent-browser's own `skill-data/slack/SKILL.md`.

## Refresh playbook

Same as asana-automate — snapshot, find new selectors, update, re-test.

## Sidebar

| Element | role | name | Notes |
|---|---|---|---|
| Home tab | `tab` | `Home` | Top of sidebar |
| DMs tab | `tab` | `DMs` | |
| Activity tab | `tab` | `Activity` | Has unread count badge |
| Channel item | `treeitem` | (channel name; level=2 nested under section) | Each channel |
| DM item | `treeitem` | (user name; under Direct Messages section) | |
| More unreads button | `button` | `More unreads` | Visible when unread count > 0 |

## Search

| Element | role | name | Notes |
|---|---|---|---|
| Search button | `button` | `Search` | Top bar |
| Search input (after click) | `textbox` | `Search` | Modal |

## Messages (Conversation region)

| Element | role | name | Notes |
|---|---|---|---|
| Conversation container | `region` | `Conversation` | All messages |
| Message | `article` | (none — has `.author` `.timestamp` `.text` props in JSON) | Each msg is article |
| Thread reply count link | `link` | starts with `N reply` or `N replies` | Click to expand thread side panel |

## Thread panel

| Element | role | name | Notes |
|---|---|---|---|
| Thread side panel | `complementary` | `Thread` | Slides in from right |
| Thread message | `article` | (within complementary>Thread) | Parent + replies |

## People view

| Element | role | name | Notes |
|---|---|---|---|
| People nav link | `link` | `People` or `More` | Sidebar |
| People grid | `grid` | `People` | Container |
| User row | `row` | (user display name) | |
```

- [ ] **Step 7: Create `references/failure-modes.md`**

```markdown
# Slack Failure Modes

## UI evolution

Same playbook as asana-automate. Update `references/ui-patterns.md` first, then protocol jq filters.

## Auth expiry

Detection: title contains `Sign in to Slack`. Or URL → `slack.com/signin`.

Remediation:
- Shared mode: log into Slack in your daily Chrome
- Dedicated mode: `/collab-setup --reauth slack`

## Channel not in sidebar

User might have left the channel, or it might be hidden under "More" expansion. Protocol falls back to channel URL-based access (`https://app.slack.com/client/<workspace>/<channel-id>`).

## Free tier limitations

Slack Free workspaces have:
- 90-day message history (older messages return "Upgrade to see")
- No People view

`find-user` protocol handles People-view absence by falling back to @-typeahead in any open channel.
```

- [ ] **Step 8: Run skill structure check**

```bash
python scripts/check-skill-structure.py
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add collab-toolkit/skills/slack-automate/
git commit -m "feat(collab-toolkit): add slack-automate skill (4 read protocols + refs)"
```

---

## Task 7: `notion-automate` skill

**Files:**
- Create: `collab-toolkit/skills/notion-automate/SKILL.md`
- Create: `collab-toolkit/skills/notion-automate/protocols/{search-workspace,page-fetch,database-query,page-backlinks}.md`
- Create: `collab-toolkit/skills/notion-automate/references/{ui-patterns,failure-modes}.md`

Same structure as Task 5 (asana-automate) and Task 6 (slack-automate). Implementer writes:

- [ ] **Step 1: `SKILL.md`** — same template as Task 5 Step 1, substituting:
  - `name: notion-automate`
  - description: matches spec §5.7 template + Notion hero protocols list (search-workspace / page-fetch / database-query / page-backlinks)
  - Tri-language tail: `Notion 自動化、ページ読取、ヘッドレス。Notion 自動化・頁面讀取・無頭背景。`
  - Hero protocols section lists the 4 protocol files
  - allowed-tools identical to asana SKILL.md

- [ ] **Step 2: `protocols/search-workspace.md`**

```markdown
---
name: search-workspace
purpose: Full-text search across pages, databases, and content in the Notion workspace.
---

## Inputs

- `query`: required.
- `filter_type`: optional. `pages` / `databases` / `all`. Default: `all`.
- `--json`: optional.

## Output

Default Markdown:
```
## Notion search: "OKR" — 18 matches

### Pages (12)
- **Q2 OKRs** — Updated 2 days ago by alice — /OKRs/Q2-OKRs-...
- ...

### Databases (6)
- **OKR Tracker** — Owner: alice — /OKR-Tracker-...
```

`--json`: `{ query, pages: [...], databases: [...] }`.

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=notion abx open https://www.notion.so
ABX_SERVICE=notion abx wait --load networkidle

# Open search — Cmd+P or top bar button
SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name=="Search" or .name=="Quick Find")) | .ref' | head -1)
[ -z "$SEARCH_REF" ] && { echo "ERR: 'Search' / 'Quick Find' button not found"; exit 1; }
ABX_SERVICE=notion abx click "$SEARCH_REF"
ABX_SERVICE=notion abx wait 500

# Type query
ABX_SERVICE=notion abx fill --active "$QUERY"
ABX_SERVICE=notion abx wait 1000

# Snapshot results — each result is role="listitem"
SNAP=$(ABX_SERVICE=notion abx snapshot --json)
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="listitem" and (.parent.name // "" | startswith("Search results")))
  | "- **\(.name)** — \(.path // "")"
'
```

## Failure modes

- Search button not found → UI evolution
- Empty results → valid empty (no match)
```

- [ ] **Step 3: `protocols/page-fetch.md`**

```markdown
---
name: page-fetch
purpose: Fetch a Notion page's full content including embedded databases, callouts, toggles, and metadata.
---

## Inputs

- `page_url`: required. Notion page URL.
- `--json`: optional.
- `expand_toggles`: optional bool (default true).

## Output

Default Markdown: full page rendered as Markdown (headings, paragraphs, lists, callouts, embedded database row summaries).

`--json`: structured `{ title, properties, blocks: [...], embedded_dbs: [...] }`.

## Procedure

```bash
URL="$1"
[ -z "$URL" ] && { echo "ERR: page_url required"; exit 1; }

ABX_SERVICE=notion abx open "$URL"
ABX_SERVICE=notion abx wait --load networkidle
SNAP=$(ABX_SERVICE=notion abx snapshot --json)

# Page title — role="heading" level=1 within main content
TITLE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="heading" and .level==1) | .name' | head -1)
echo "# $TITLE"
echo

# Iterate blocks under main content region
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="region" and .name=="Page content")
  | .children[]?
  | (
    if .role == "heading" then "\n## \(.name)"
    elif .role == "paragraph" then .text
    elif .role == "listitem" then "- \(.text)"
    elif .role == "callout" then "> 💡 \(.text)"
    elif .role == "toggle" then "▶ \(.name)"
    else (.name // .text // "")
    end
  )
'
```

## Failure modes

- Page not found (404 title) → invalid URL
- Page private / no access → message about permissions
```

- [ ] **Step 4: `protocols/database-query.md`**

```markdown
---
name: database-query
purpose: Query a Notion database with multi-property filters and sort, return matching rows.
---

## Inputs

- `database_url`: required.
- `filters`: optional JSON array, each `{ property, operator, value }`.
- `sort`: optional `property:direction`.
- `--json`: optional.

## Output

Default Markdown: table of rows with key properties.

`--json`: array of row objects.

## Procedure

```bash
URL="$1"
ABX_SERVICE=notion abx open "$URL"
ABX_SERVICE=notion abx wait --load networkidle
SNAP=$(ABX_SERVICE=notion abx snapshot --json)

# Database rows are role="row" within role="grid"
# Properties extracted from row.cells
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row" and .parent.role=="grid")
  | [.cells[]?.text] | join(" | ")
'

# Filter / sort application:
# Notion's filter UI is interactive — implementer adds clicks on filter chip + property selector + value input.
# Reference role+name in references/ui-patterns.md.
```

## Failure modes

- Database not found → invalid URL
- Filter property doesn't exist → error message naming the bad property
```

- [ ] **Step 5: `protocols/page-backlinks.md`**

```markdown
---
name: page-backlinks
purpose: Find all pages that link to a target Notion page.
---

## Inputs

- `page_url`: required.
- `--json`: optional.

## Output

Default Markdown: list of linking pages with their parent path.

`--json`: array of `{ title, url, path, last_updated }`.

## Procedure

```bash
URL="$1"
ABX_SERVICE=notion abx open "$URL"
ABX_SERVICE=notion abx wait --load networkidle

# Backlinks panel is shown via page menu — find "..." button or scroll to bottom Backlinks section
SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
BACKLINKS_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="region" and .name=="Backlinks") | .ref' | head -1)

if [ -z "$BACKLINKS_REF" ]; then
  # Fallback: open page menu → "Show backlinks"
  MENU_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name=="More options" or .name=="..." )) | .ref' | head -1)
  [ -z "$MENU_REF" ] && { echo "ERR: page menu not found"; exit 1; }
  ABX_SERVICE=notion abx click "$MENU_REF"
  ABX_SERVICE=notion abx wait 500
  # find "Show backlinks" menuitem
  SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)
  SHOW_BL=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="menuitem" and .name=="Show backlinks") | .ref' | head -1)
  [ -z "$SHOW_BL" ] && { echo "ERR: Show backlinks menu item not found"; exit 1; }
  ABX_SERVICE=notion abx click "$SHOW_BL"
  ABX_SERVICE=notion abx wait 500
  SNAP=$(ABX_SERVICE=notion abx snapshot --json)
fi

# Each backlink is role="link" within Backlinks region
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="region" and .name=="Backlinks")
  | .children[]?
  | select(.role=="link")
  | "- \(.name) — \(.href // "")"
'
```

## Failure modes

- Page has no backlinks → valid empty (output `No pages link to this page`)
- Menu not found → UI evolution
```

- [ ] **Step 6: `references/ui-patterns.md`**

```markdown
# Notion UI Patterns

## Navigation

| Element | role | name | Notes |
|---|---|---|---|
| Sidebar workspace | `region` | `Sidebar` | Container |
| Sidebar page item | `treeitem` | (page name) | |
| Quick Find / Search | `button` | `Search` or `Quick Find` | Top bar; opens via Cmd+P |

## Page content

| Element | role | name | Notes |
|---|---|---|---|
| Page title | `heading` level=1 | (page title) | |
| Page content region | `region` | `Page content` | Container |
| Block: heading | `heading` (any level) | (text) | |
| Block: paragraph | `paragraph` | (text) | |
| Block: list item | `listitem` | (text) | |
| Block: callout | `callout` | (text) | |
| Block: toggle | `toggle` | (toggle title) | |

## Database / table

| Element | role | name | Notes |
|---|---|---|---|
| Grid container | `grid` | (database name) | |
| Row | `row` | (none — properties in `.cells`) | |
| Column header | `columnheader` | (property name) | |

## Backlinks

| Element | role | name | Notes |
|---|---|---|---|
| Backlinks region | `region` | `Backlinks` | Shown bottom of page (toggle in page settings) |
| Backlink entry | `link` | (linking page name) | href = parent page URL |

## Refresh playbook

Same as asana-automate.
```

- [ ] **Step 7: `references/failure-modes.md`**

Standard structure (UI evolution / auth expiry / empty result vs error / Notion-specific: no-access pages, archived pages).

- [ ] **Step 8: Run skill structure check**

```bash
python scripts/check-skill-structure.py
```

- [ ] **Step 9: Commit**

```bash
git add collab-toolkit/skills/notion-automate/
git commit -m "feat(collab-toolkit): add notion-automate skill (4 read protocols + refs)"
```

---

## Task 8: `gcal-automate` skill

**Files:**
- Create: `collab-toolkit/skills/gcal-automate/SKILL.md`
- Create: `collab-toolkit/skills/gcal-automate/protocols/{agenda-view,event-search,find-free-slots,shared-calendar-read}.md`
- Create: `collab-toolkit/skills/gcal-automate/references/{ui-patterns,failure-modes}.md`

Same task-shape as Task 5/6/7. Inputs / outputs / procedures for each protocol:

- [ ] **Step 1: `SKILL.md`** — description per spec §5.7 template substituting GCal hero protocols.

- [ ] **Step 2: `protocols/agenda-view.md`** — opens calendar.google.com, switches to Day / Week / Custom view per input `range`, snapshots event grid, extracts events. Role+name patterns: events are `role="button"` with name containing time + title; date columns are `role="columnheader"`.

- [ ] **Step 3: `protocols/event-search.md`** — uses top-bar Search button (role="button" name="Search"), types query, parses results region (role="region" name="Search results"). Each result is role="article" or role="listitem".

- [ ] **Step 4: `protocols/find-free-slots.md`** — given `duration_minutes`, `start_date`, `end_date`, `business_hours_start/end`: open week view, snapshot grid, parse event blocks per day, compute open slots via Bash arithmetic. Returns list of `{date, start_time, end_time, duration_minutes}`.

- [ ] **Step 5: `protocols/shared-calendar-read.md`** — open Other calendars sidebar (role="list" name="Other calendars"), click target colleague's calendar to enable, agenda-view filtered to that calendar via filter chip.

- [ ] **Step 6: `references/ui-patterns.md`** documents:
  - Top bar Search button (`role=button name=Search`)
  - View switcher (`role=button name=Day/Week/Month/Year`)
  - Event element (`role=button name=<time> <title>`)
  - Date column header (`role=columnheader name=<date>`)
  - Other calendars list (`role=list name=Other calendars`)
  - Add calendar button (`role=button name=Add other calendars`)

- [ ] **Step 7: `references/failure-modes.md`** — UI evolution, auth expiry, calendar not found, time-zone confusion (default tz inheritance from Chrome).

- [ ] **Step 8: Run skill structure check**

```bash
python scripts/check-skill-structure.py
```

- [ ] **Step 9: Commit**

```bash
git add collab-toolkit/skills/gcal-automate/
git commit -m "feat(collab-toolkit): add gcal-automate skill (4 read protocols + refs)"
```

---

## Task 9: `gmail-automate` skill

**Files:**
- Create: `collab-toolkit/skills/gmail-automate/SKILL.md`
- Create: `collab-toolkit/skills/gmail-automate/protocols/{mail-search,thread-read,inbox-summary,label-read}.md`
- Create: `collab-toolkit/skills/gmail-automate/references/{ui-patterns,failure-modes}.md`

Same task-shape. Procedures:

- [ ] **Step 1: `SKILL.md`** — description per spec §5.7 with Gmail hero protocols.

- [ ] **Step 2: `protocols/mail-search.md`** — opens mail.google.com, top-bar search (role="combobox" name="Search mail"), types query including operators (`from:` / `to:` / `has:attachment` / `before:` / `after:` / `label:`), parses result list (each `role="row"` in result grid). Extracts `from`, `subject`, `snippet`, `date`.

- [ ] **Step 3: `protocols/thread-read.md`** — given `thread_url` or thread ID, opens, expands all messages (role="region" name="Message body"), extracts per-message `from`, `to`, `cc`, `date`, `body`, `attachments` (role="link" within attachments region).

- [ ] **Step 4: `protocols/inbox-summary.md`** — opens Primary / Social / Promotions / Updates tabs, snapshots top N unread, returns counts + first-line summaries per category.

- [ ] **Step 5: `protocols/label-read.md`** — given `label_name`, opens label via sidebar (role="link" with that name; nested labels via expand), lists messages with that label.

- [ ] **Step 6: `references/ui-patterns.md`**:
  - Top-bar Search (`role=combobox name="Search mail"`)
  - Mail row (`role=row` with `.cells` for `from / subject / snippet / date`)
  - Star button (`role=button name=Star`)
  - Tabs (`role=tab name="Primary"/"Social"/"Promotions"/"Updates"`)
  - Sidebar label (`role=link` under Labels section)
  - Message body (`role=region name="Message body"`)
  - Attachment chip (`role=link` within attachments region)

- [ ] **Step 7: `references/failure-modes.md`** — UI evolution, auth expiry, Gmail "Less secure app access" issues (unlikely via Chrome but document), large attachment download limits.

- [ ] **Step 8: Run skill structure check**

```bash
python scripts/check-skill-structure.py
```

- [ ] **Step 9: Commit**

```bash
git add collab-toolkit/skills/gmail-automate/
git commit -m "feat(collab-toolkit): add gmail-automate skill (4 read protocols + refs)"
```

---

## Task 10: READMEs (en / ja / zh-TW)

**Files:**
- Create: `collab-toolkit/README.md`
- Create: `collab-toolkit/README.ja.md`
- Create: `collab-toolkit/README.zh-TW.md`

Per PR #150 rule: tri-language. Each file ~200 lines covering: purpose, 5 services, quick start (`/collab-setup`), shared vs dedicated mode comparison, hero protocols summary per skill, caveats (privacy / cookie scope / no-Cowork / login-state coupling), troubleshooting, development (bats tests).

- [ ] **Step 1: Create `collab-toolkit/README.md`**

```markdown
# collab-toolkit

> Browser automation toolkit wrapping [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser).
> 5 read-only office-collaboration skills for personal workplace intelligence.

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## What it does

Connects to the office-collaboration services you use daily — Asana, Slack, Notion, Google Calendar, Gmail — and gives you:

- **Status visibility**: company-state, work-in-flight, team activity
- **Cross-tool search**: natural-language search across your internal corporate data via Claude Code
- **Background operation**: headless after first login, runs while you work

Built on agent-browser's semantic-first snapshot model — no fragile CSS selectors, no API tokens, just your existing Chrome login state.

## Quick start

```bash
# Install plugin via Claude Code marketplace
/plugin install collab-toolkit

# One-time bootstrap (Homebrew preferred on macOS)
/collab-setup
```

That's it. `/collab-setup` will:
1. Install `agent-browser` (brew on macOS, npm fallback)
2. Download Chrome for Testing
3. Install `~/.local/bin/abx` wrapper
4. Detect your Chrome profile, write config
5. Verify all 5 services are logged in

After that, ask Claude things like:
- "List my Asana tasks due this week"
- "Search Slack for messages about OKR in #engineering after May 1"
- "What's on my Google Calendar today"
- "Find free 30-minute slots between 10am-4pm next Tuesday"

## Profile modes

| Mode | What | When |
|---|---|---|
| **Shared** (default) | Reuses your daily Chrome's login state via `--profile <name>` | Single-user, single-machine — fastest setup |
| **Dedicated** (`--dedicated`) | 5 per-service profile dirs, manual login each | Multi-machine sync, dedicated automation environment, isolation |

Switch any time: `/collab-setup --switch-mode`.

## Skills

| Skill | Hero protocols |
|---|---|
| `asana-automate` | task-list, task-detail, project-overview, search-global |
| `slack-automate` | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query, page-backlinks |
| `gcal-automate` | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate` | mail-search, thread-read, inbox-summary, label-read |

## Caveats

- ⚠️ **Cowork sandbox not supported** — needs a local Chrome / OS access
- ⚠️ **CI / scheduled runs not supported** in v0.1.0 (shared mode is local-only; dedicated mode portability deferred to v0.2.0+)
- **Privacy scope**: in shared mode, agent-browser sees ALL your Chrome cookies, not just the 5 services. Trust comes from the local Rust binary + open source.
- **Login-state coupling**: in shared mode, if you log out of a service in your daily Chrome, automation breaks until you log back in.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ERR: config not found` | Run `/collab-setup` |
| `⚠️ ~/.local/bin not on PATH` | Add `export PATH="$HOME/.local/bin:$PATH"` to your shell rc |
| `ERR: UI changed` | Open the affected skill's `references/ui-patterns.md`, re-snapshot, update |
| `Login wall detected` | Shared: log in via Chrome. Dedicated: `/collab-setup --reauth <service>` |

## Development

```bash
# Unit tests (bats)
cd collab-toolkit && bats scripts/tests/

# Structure check (run from repo root)
python scripts/check-skill-structure.py
```

## Architecture

See `docs/superpowers/specs/2026-05-15-collab-toolkit-v0.1.0-design.md` for the full design spec.
```

- [ ] **Step 2: Create `collab-toolkit/README.ja.md`**

Mirror of README.md in Japanese — same sections, same headings translated.

Key glossary (per `docs/i18n/glossary-ja.md`):
- "browser automation" → 「ブラウザ自動化」
- "search" → 「検索」
- "Chrome profile" → 「Chrome プロファイル」(English noun preserved)
- "Cowork sandbox" → 「Cowork サンドボックス」(English noun preserved)

Translate naturally; do not katakana-ize technical terms that have established English usage in JP tech context (e.g., keep "API", "JSON", "agent-browser" in Latin script).

- [ ] **Step 3: Create `collab-toolkit/README.zh-TW.md`**

Mirror of README.md in Traditional Chinese.

Key glossary (per `docs/i18n/glossary-zh-TW.md`):
- "browser automation" → 「瀏覽器自動化」
- "search" → 「搜尋」(not Mainland 搜索)
- "Chrome profile" → 「Chrome 設定檔」
- "Cowork sandbox" → 「Cowork 沙盒」
- Maintain Traditional characters throughout; no Mainland calques

- [ ] **Step 4: Commit**

```bash
git add collab-toolkit/README.md collab-toolkit/README.ja.md collab-toolkit/README.zh-TW.md
git commit -m "docs(collab-toolkit): add tri-language READMEs (en/ja/zh-TW)"
```

---

## Task 11: Final CI verification

**Files:**
- No new files. Run all repo CI checks.

- [ ] **Step 1: Run marketplace description sync check**

```bash
python scripts/check-marketplace-description-sync.py
```

Expected: PASS.

- [ ] **Step 2: Run plugin description ↔ skill coherence check**

```bash
python scripts/check-plugin-description-skill-coherence.py
```

Expected: PASS — plugin description mentions all 5 skills (asana / slack / notion / gcal / gmail).

- [ ] **Step 3: Run skill structure check**

```bash
python scripts/check-skill-structure.py
```

Expected: PASS for all 5 skill folders + commands/.

- [ ] **Step 4: Run shared conventions drift check**

```bash
python scripts/check-shared-conventions-drift.py
```

Expected: PASS — no convention violations against other monkey-skills plugins.

- [ ] **Step 5: Run scraper-deps check (no scrapers in this plugin, should noop)**

```bash
python scripts/check-scraper-deps.py
```

Expected: PASS / no-op.

- [ ] **Step 6: Re-run bats unit tests**

```bash
cd collab-toolkit && bats scripts/tests/test-abx.bats scripts/tests/test-setup.bats
```

Expected: all tests pass (6 + 16 = 22).

- [ ] **Step 7: Verify all skills' `allowed-tools` are consistent**

```bash
grep -h "allowed-tools" collab-toolkit/skills/*/SKILL.md
```

Expected output for each:

```
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
```

- [ ] **Step 8: Final integration smoke (manual, not blocking)**

If kouko is at the machine, run:

```bash
# Dogfood test (requires kouko to be logged into the 5 services in his Chrome)
/collab-setup
# Then test a single protocol manually:
# Ask Claude: "list my Asana tasks due this week"
```

This is L2 live smoke — not in CI, not a blocking step for the commit but a final confidence check before PR.

- [ ] **Step 9: Commit any CI-driven fixes from Steps 1-7**

If any check failed and you applied fixes:

```bash
git add <fixed-files>
git commit -m "fix(collab-toolkit): address CI structure / description sync issues"
```

If all green from the start (likely), no commit needed — proceed to push.

---

## Self-Review

**Spec coverage check** — mapping each spec section to a task:

| Spec section | Task | Notes |
|---|---|---|
| §3 D1 plugin name `collab-toolkit` | Task 1 | plugin.json `name` field |
| §3 D2 5 skills × 4 protocols | Tasks 5-9 | one task per skill |
| §3 D3 read-only v0.1.0 | All protocol tasks | no writes; spec compliance |
| §3 D4 Web headless | Implicit in protocols (no `--headed` flag in protocol procedures) | |
| §3 D5 hybrid profile mode | Task 2 (abx mode logic) + Task 3 (setup_shared / setup_dedicated) | bats tests cover both branches |
| §3 D6 single workspace | Implicit — no `--workspace` arg in any protocol | |
| §3 D7 semantic-first selectors | Every protocol task | jq filters by role+name; no hardcoded @eN |
| §3 D8 sole-path routing | Each SKILL.md description (Tasks 5-9) | no PREFER MCP conditionals |
| §3 D9 `/collab-setup` Homebrew first | Task 3 (`install_agent_browser` function) | bats test covers brew → npm fallback |
| §3 D10 abx wrapper at `~/.local/bin/abx` | Task 2 (wrapper) + Task 3 (install) | |
| §3 D11 Cowork ⚠️ in plugin description | Task 1 (plugin.json description) | |
| §3 D12 tri-language READMEs | Task 10 | en / ja / zh-TW |
| §3 D13 L0 + L1 testing | Tasks 2, 3, 11 | bats + CI scripts; L1-jq deferred (noted as divergence at plan top) |
| §3 D14 last Google service is Gmail | Task 9 | not gmaps |
| §3 D15 (not declared) | n/a | |
| §5.1 plugin.json | Task 1 | verbatim from spec |
| §5.2 marketplace.json entry | Task 1 | verbatim from spec |
| §5.3 config schema XDG | Task 3 | xdg helpers + write_config_* |
| §5.4 abx wrapper | Task 2 | full code |
| §5.5 /collab-setup command | Task 4 | command md file |
| §5.6 setup.sh | Task 3 | full code, with bats |
| §5.7 SKILL.md template | Tasks 5-9 | each skill instantiates template |
| §5.8 protocol template | Tasks 5-9 | each protocol follows template |
| §5.9 references/ui-patterns.md | Tasks 5-9 | each skill |
| §5.10 references/failure-modes.md | Tasks 5-9 | each skill |
| §6 data flows | Implicit in protocols | |
| §7 error handling | Tasks 5-9 (per-protocol checks) + Task 3 (verify_one) | |
| §8 testing | Tasks 2, 3, 11 | L0 + L1-setup + L1-abx; L1-jq deferred |
| §9 risks | Noted; no task action needed (documentation) | |
| §10 out of scope | Not implemented (correct) | |
| §11 references | n/a | |

**Placeholder scan**: No "TBD" or "implement later" — protocols have complete bash with jq filter patterns. Service-specific role+name values are documented in each `ui-patterns.md` (not placeholders — they ARE the deliverable for that file). Implementer who runs a real snapshot will refine if needed (this is observation work, not a placeholder).

**Type consistency**: All skills use `ABX_SERVICE=<service>` env var convention; all use `abx` command on PATH; all jq filters operate on `.elements[]` with `.role` + `.name` + `.ref`; all SKILL.md `allowed-tools` are identical pattern.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-15-collab-toolkit-v0.1.0.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review (spec → code-quality) between tasks. Validated pattern per kouko's `feedback_subagent_driven_development_validated.md` on PR #239.

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
