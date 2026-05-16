#!/usr/bin/env bash
# setup.sh — back-end for /collab-setup slash command.
# Installs agent-browser, downloads Chrome for Testing, installs abx wrapper,
# writes ~/.config/collab-toolkit/config.json.
#
# v0.1.2 changes:
# - `dedicated` mode now uses a SINGLE unified profile (was: 5 per-service dirs).
#   Google SSO cascades across services in one profile → 2-3 logins typical
#   instead of 5.
# - Setup is Claude-orchestrated for dedicated mode (no `read -rp`, no `!`
#   prefix needed). See commands/collab-setup.md.
# - `--switch-mode` is now bidirectional (shared ↔ dedicated).
# - Subcommands added for Claude orchestration: --setup-dedicated-config,
#   --open-headed, --reauth.

set -euo pipefail

# ============================================================================
# XDG path helpers
# ============================================================================

xdg_config_home() { echo "${XDG_CONFIG_HOME:-$HOME/.config}"; }
xdg_data_home()   { echo "${XDG_DATA_HOME:-$HOME/.local/share}"; }
xdg_bin_home()    { echo "$HOME/.local/bin"; }

# Globals (computed at top of main)
# NOTE: CONFIG_DIR / DATA_DIR / BIN_DIR / CONFIG / DEDICATED_PROFILE are set
# by main() before any function uses them. Functions called outside main()
# (e.g., from bats) use lazy-fallback computation: ${VAR:-$(helper)/...}.
CONFIG_DIR=""; DATA_DIR=""; BIN_DIR=""; CONFIG=""; DEDICATED_PROFILE=""
DEDICATED=false; SHARED=false; REAUTH=""; SWITCH=false; VERIFY_ONLY=false; MODE=""
ACTION=""; SHARED_PROFILE_ARG=""; OPEN_SERVICE=""

# ============================================================================
# Argument parsing
# ============================================================================

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      # User-facing flags (backward compat with v0.1.0+)
      --dedicated)    DEDICATED=true ;;
      --shared)       SHARED=true ;;
      --reauth)       REAUTH="$2"; shift ;;
      --switch-mode)  SWITCH=true ;;
      --verify)       VERIFY_ONLY=true ;;

      # Orchestrator subcommands (Claude calls these from commands/collab-setup.md)
      --install-only)               ACTION=install_only ;;
      --list-profiles-meta)         ACTION=list_profiles_meta ;;
      --setup-shared)               ACTION=setup_shared_noninteractive; SHARED_PROFILE_ARG="$2"; shift ;;
      --setup-dedicated-config)     ACTION=setup_dedicated_config_only ;;
      --open-headed)                ACTION=open_headed_service; OPEN_SERVICE="$2"; shift ;;

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

# Convenience: run all install phases
install_only() {
  install_agent_browser
  install_chrome
  install_abx
}

# ============================================================================
# Phase 4a: shared mode setup
# ============================================================================

write_config_shared() {
  local name="$1"
  local config_dir config
  config_dir="${CONFIG_DIR:-$(xdg_config_home)/collab-toolkit}"
  config="${CONFIG:-$config_dir/config.json}"
  mkdir -p "$config_dir"
  jq -n --arg name "$name" \
    '{mode:"shared", chrome_profile:$name, dedicated_profile:"~/.local/share/collab-toolkit/profiles/dedicated"}' \
    > "$config"
}

list_profiles_with_email() {
  # Reads Chrome's Local State JSON and emits one line per profile:
  #   "  <dir_name>: <user_name|(no Google account)> — <display_name|dir_name>"
  # Tries macOS / Linux Chrome / Linux Chromium paths. Returns non-zero if none found.
  local local_state=""
  for candidate in \
    "$HOME/Library/Application Support/Google/Chrome/Local State" \
    "$HOME/.config/google-chrome/Local State" \
    "$HOME/.config/chromium/Local State"
  do
    if [ -f "$candidate" ]; then
      local_state="$candidate"
      break
    fi
  done
  [ -z "$local_state" ] && return 1
  jq -r '
    .profile.info_cache
    | to_entries[]
    | "  \(.key): \(.value.user_name // "(no Google account)") — \(.value.name // .key)"
  ' "$local_state" 2>/dev/null
}

list_profiles_meta() {
  # Convenience for Claude orchestrator: print agent-browser profile list +
  # Local State email map in one call.
  echo "## agent-browser profiles"
  agent-browser profiles 2>&1 || true
  echo ""
  echo "## Google account info per profile (from Local State)"
  list_profiles_with_email 2>/dev/null || echo "  (Local State not found — non-Chrome browser or no Chrome installed)"
}

setup_shared() {
  # Interactive path (backward compat — used when setup.sh invoked directly
  # without orchestration).
  echo "Available Chrome profiles:"
  agent-browser profiles || true
  if list_profiles_with_email > /tmp/collab-profile-emails.$$ 2>/dev/null \
     && [ -s /tmp/collab-profile-emails.$$ ]; then
    echo ""
    echo "Google account info per profile:"
    cat /tmp/collab-profile-emails.$$
  fi
  rm -f /tmp/collab-profile-emails.$$
  local name
  read -rp "Profile name to use [Default]: " name
  name="${name:-Default}"
  write_config_shared "$name"
  MODE=shared
  verify_all_services
}

setup_shared_noninteractive() {
  # Non-interactive path for Claude orchestrator. Caller supplies the
  # profile name via --setup-shared <name>.
  local name="${SHARED_PROFILE_ARG:-Default}"
  write_config_shared "$name"
  MODE=shared
  echo "✓ Shared mode configured (chrome_profile: $name)"
}

# ============================================================================
# Phase 4b: dedicated mode setup (UNIFIED profile, v0.1.2)
# ============================================================================

write_config_dedicated_unified() {
  local profile_path="$1"
  local config_dir config
  config_dir="${CONFIG_DIR:-$(xdg_config_home)/collab-toolkit}"
  config="${CONFIG:-$config_dir/config.json}"
  mkdir -p "$config_dir"
  jq -n --arg dp "$profile_path" \
    '{mode:"dedicated", chrome_profile:"Default", dedicated_profile:$dp}' \
    > "$config"
}

setup_dedicated_config_only() {
  # Claude-orchestrator entry point. Writes config + creates dedicated profile
  # dir. Does NOT open Chrome and does NOT verify — orchestrator handles those
  # via separate --open-headed calls + AskUserQuestion + --verify.
  local dedicated_profile
  dedicated_profile="${DEDICATED_PROFILE:-$(xdg_data_home)/collab-toolkit/profiles/dedicated}"
  mkdir -p "$dedicated_profile"
  write_config_dedicated_unified "$dedicated_profile"
  MODE=dedicated
  echo "✓ Dedicated mode config written (profile dir: $dedicated_profile)"
}

setup_dedicated_direct() {
  # Direct CLI path (no Claude orchestrator). Writes config + opens Chrome
  # at the first service. Prints user instructions for completing the flow
  # manually. Subsequent navigations + verify are user's job here.
  setup_dedicated_config_only
  echo ""
  echo "→ Opening Chrome at Asana (headed). Log in to ALL 5 services in this"
  echo "  Chrome window (open tabs as needed: Slack / Notion / GCal / Gmail)."
  echo "  Google SSO will likely cascade across services."
  local dedicated_profile
  dedicated_profile=$(jq -r .dedicated_profile "$CONFIG")
  dedicated_profile="${dedicated_profile/#\~/$HOME}"
  agent-browser --headed --profile "$dedicated_profile" open "$(service_url asana)"
  echo ""
  echo "→ After all 5 services logged in, run: /collab-setup --verify"
}

open_headed_service() {
  # Claude-orchestrator entry point. Opens (or navigates to) one service in
  # the dedicated headed Chrome session. Caller asks user for login
  # confirmation via AskUserQuestion afterward.
  local service="${OPEN_SERVICE:-$1}"
  local url
  url=$(service_url "$service")
  local config
  config="${CONFIG:-$(xdg_config_home)/collab-toolkit/config.json}"
  local dedicated_profile
  dedicated_profile=$(jq -r .dedicated_profile "$config" 2>/dev/null || echo "")
  if [ -z "$dedicated_profile" ] || [ "$dedicated_profile" = "null" ]; then
    echo "ERR: dedicated_profile not set in config; run --setup-dedicated-config first" >&2
    exit 1
  fi
  dedicated_profile="${dedicated_profile/#\~/$HOME}"
  # First headed call launches Chrome; subsequent open calls navigate the
  # existing daemon's Chrome instance.
  agent-browser --headed --profile "$dedicated_profile" open "$url"
}

reauth_dedicated() {
  # User-facing: /collab-setup --reauth <service> in dedicated mode.
  # Opens Chrome at the service URL for re-login. User completes login;
  # subsequent skill invocations use the refreshed cookies.
  local service="$1"
  if [ -z "$service" ]; then
    echo "ERR: --reauth requires a service name" >&2
    exit 2
  fi
  echo "→ Opening $service in headed Chrome for re-login..."
  OPEN_SERVICE="$service" open_headed_service
  echo ""
  echo "→ Log in to $service. After that, run: /collab-setup --verify"
}

# ============================================================================
# Verification
# ============================================================================

verify_all_services() {
  for service in asana slack notion gcal gmail; do
    verify_one "$service" || true
  done
}

verify_one() {
  # v0.1.2: URL-based check (primary) + title-based check (fallback).
  # Title alone was unreliable — services often redirect not-logged-in users
  # to marketing landing pages whose titles don't contain "Sign in" / "Log in"
  # (observed: Slack "AI Work Platform...", Notion "The AI workspace...",
  # Gmail just "Gmail"). URL-based hostname mismatch catches these.
  local service="$1"
  local url current_url title expected_host current_host
  url=$(service_url "$service")
  abx open "$url" >/dev/null
  current_url=$(abx get url 2>/dev/null || echo "")
  title=$(abx get title 2>/dev/null || echo "")

  # Extract hostnames for comparison
  expected_host=$(echo "$url"         | sed -E 's#^https?://([^/]+).*#\1#')
  current_host=$(echo "$current_url"  | sed -E 's#^https?://([^/]+).*#\1#')

  local not_logged_in=false reason=""

  # Check 1: hostname mismatch → service redirected away from its app host
  # (e.g., app.slack.com → slack.com marketing, mail.google.com → google.com/gmail/about,
  #  www.notion.so → notion.so/product, anything → accounts.google.com)
  if [ -n "$current_host" ] && [ "$current_host" != "$expected_host" ]; then
    not_logged_in=true
    reason="hostname redirected: $expected_host → $current_host"
  fi

  # Check 2: same host but URL path indicates login page
  # (e.g., app.asana.com/-/login)
  if ! $not_logged_in; then
    case "$current_url" in
      *"/login"*|*"/signin"*|*"/sign-in"*|*"/sign_in"*|*accounts.google.com*)
        not_logged_in=true
        reason="URL is login page: $current_url"
        ;;
    esac
  fi

  # Check 3: title fallback (catches edge cases the URL checks miss)
  if ! $not_logged_in; then
    case "$title" in
      *"Sign in"*|*"Log in"*|*"Login"*|*"sign in"*|*"log in"*)
        not_logged_in=true
        reason="title indicates login page: $title"
        ;;
    esac
  fi

  if $not_logged_in; then
    echo "⚠️ $service: NOT logged in ($reason)"
    [ "$MODE" = "shared" ]    && echo "   → Log into $service in your daily Chrome under the configured profile, then re-run /collab-setup --verify"
    [ "$MODE" = "dedicated" ] && echo "   → Run: /collab-setup --reauth $service"
  else
    echo "✓ $service ready (URL: $current_url, title: $title)"
  fi
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
  [ -f "$CONFIG" ] && jq -r .mode "$CONFIG" 2>/dev/null || echo ""
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
  DEDICATED_PROFILE="$DATA_DIR/profiles/dedicated"
  mkdir -p "$CONFIG_DIR" "$DATA_DIR" "$BIN_DIR"

  parse_args "$@"

  # Orchestrator-only subcommands take priority. ACTION is set only when
  # one of --install-only / --setup-shared / --setup-dedicated-config /
  # --open-headed was provided.
  if [ -n "$ACTION" ]; then
    "$ACTION"
    return
  fi

  if $VERIFY_ONLY; then
    MODE="$(current_mode)"
    verify_all_services
    return
  fi

  if [ -n "$REAUTH" ]; then
    MODE="$(current_mode)"
    if [ "$MODE" = "dedicated" ]; then
      reauth_dedicated "$REAUTH"
    else
      echo "ERR: --reauth only meaningful in dedicated mode (current mode: $MODE)." >&2
      exit 2
    fi
    return
  fi

  install_agent_browser
  install_chrome
  install_abx

  # v0.1.2 default = dedicated (more reliable than shared for office-
  # collaboration use cases; see Profile modes section in README). Shared
  # remains opt-in via --shared.
  #
  # --switch-mode is bidirectional: toggle between shared and dedicated
  # based on current config. --dedicated forces dedicated, --shared forces
  # shared, regardless of current state.
  if $SWITCH; then
    case "$(current_mode)" in
      shared)    setup_dedicated_direct ;;
      dedicated) setup_shared ;;
      *)         setup_dedicated_direct ;;   # no prior config → default to dedicated
    esac
  elif $SHARED; then
    setup_shared
  elif $DEDICATED; then
    setup_dedicated_direct
  else
    # No mode flag → v0.1.2 default = dedicated
    setup_dedicated_direct
  fi
}

# Skip main() if sourced (for bats)
(return 0 2>/dev/null) && return 0
main "$@"
