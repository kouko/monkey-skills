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
# NOTE: PROFILES_ROOT, CONFIG_DIR, BIN_DIR, CONFIG are set by main() before
# any function uses them. Functions called outside main() (e.g., from bats)
# use lazy-fallback computation: ${VAR:-$(helper)/...}.
CONFIG_DIR=""; DATA_DIR=""; BIN_DIR=""; CONFIG=""; PROFILES_ROOT=""
DEDICATED=false; REAUTH=""; SWITCH=false; VERIFY_ONLY=false; MODE=""

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
  local script_dir bin_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  bin_dir="${BIN_DIR:-$(xdg_bin_home)}"
  mkdir -p "$bin_dir"
  cp "$script_dir/abx" "$bin_dir/abx"
  chmod +x "$bin_dir/abx"
  case ":$PATH:" in
    *":$bin_dir:"*) ;;
    *)
      echo "⚠️ $bin_dir not on PATH. Add to your shell rc:"
      echo '   export PATH="$HOME/.local/bin:$PATH"'
      ;;
  esac
}

# ============================================================================
# Phase 4a: shared mode setup (Option A — default)
# ============================================================================

write_config_shared() {
  local name="$1"
  local config_dir config
  config_dir="${CONFIG_DIR:-$(xdg_config_home)/collab-toolkit}"
  config="${CONFIG:-$config_dir/config.json}"
  mkdir -p "$config_dir"
  jq -n --arg name "$name" \
    '{mode:"shared", chrome_profile:$name, profiles_root:"~/.local/share/collab-toolkit/profiles"}' \
    > "$config"
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
  local config_dir config profiles_root
  config_dir="${CONFIG_DIR:-$(xdg_config_home)/collab-toolkit}"
  config="${CONFIG:-$config_dir/config.json}"
  profiles_root="${PROFILES_ROOT:-$(xdg_data_home)/collab-toolkit/profiles}"
  mkdir -p "$config_dir"
  jq -n --arg pr "$profiles_root" \
    '{mode:"dedicated", chrome_profile:"Default", profiles_root:$pr}' \
    > "$config"
}

setup_dedicated() {
  local profiles_root
  profiles_root="${PROFILES_ROOT:-$(xdg_data_home)/collab-toolkit/profiles}"
  mkdir -p "$profiles_root"/{asana,slack,notion,gcal,gmail}
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
  ABX_SERVICE="$service" abx open "$url" >/dev/null
  title=$(ABX_SERVICE="$service" abx get title)
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
# Source-only mode for bats — return after all functions are defined
# ============================================================================

# Source-only mode for bats — when sourced, skip main()
if [ "${1:-}" = "--source-only" ]; then return 0 2>/dev/null || true; fi

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
