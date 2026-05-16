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
  PATH="$TEST_TMPDIR/bin:/usr/bin:/bin"   # isolate from real agent-browser on host PATH
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
  PATH="$TEST_TMPDIR/bin:/usr/bin:/bin"   # isolate from real agent-browser on host PATH
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

@test "write_config_dedicated_unified writes mode=dedicated with dedicated_profile path" {
  run write_config_dedicated_unified "/some/path/dedicated"
  [ "$status" -eq 0 ]
  mode=$(jq -r .mode "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$mode" = "dedicated" ]
  dp=$(jq -r .dedicated_profile "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$dp" = "/some/path/dedicated" ]
}

@test "setup_dedicated_config_only creates unified profile dir + writes config" {
  run setup_dedicated_config_only
  [ "$status" -eq 0 ]
  # Profile dir created
  [ -d "$XDG_DATA_HOME/collab-toolkit/profiles/dedicated" ]
  # Config has mode=dedicated and dedicated_profile pointing to that dir
  mode=$(jq -r .mode "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$mode" = "dedicated" ]
  dp=$(jq -r .dedicated_profile "$XDG_CONFIG_HOME/collab-toolkit/config.json")
  [ "$dp" = "$XDG_DATA_HOME/collab-toolkit/profiles/dedicated" ]
}

@test "setup_dedicated_config_only does NOT create per-service dirs (v0.1.0/v0.1.1 schema removed)" {
  run setup_dedicated_config_only
  [ "$status" -eq 0 ]
  for service in asana slack notion gcal gmail; do
    [ ! -d "$XDG_DATA_HOME/collab-toolkit/profiles/$service" ]
  done
}

@test "open_headed_service errors when config missing" {
  rm -f "$XDG_CONFIG_HOME/collab-toolkit/config.json"
  OPEN_SERVICE=asana run open_headed_service
  [ "$status" -ne 0 ]
  [[ "$output" == *"dedicated_profile not set"* ]]
}

@test "open_headed_service launches agent-browser headed with dedicated profile" {
  setup_dedicated_config_only >/dev/null
  stub_command agent-browser 'echo "agent-browser $*"'
  OPEN_SERVICE=slack run open_headed_service
  [ "$status" -eq 0 ]
  [[ "$output" == *"--headed"* ]]
  [[ "$output" == *"--profile $XDG_DATA_HOME/collab-toolkit/profiles/dedicated"* ]]
  [[ "$output" == *"open https://app.slack.com"* ]]
}

@test "verify_one detects login wall via URL path (same-host /login redirect, e.g. Asana)" {
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'case "$*" in
    *"get url"*)   echo "https://app.asana.com/-/login?u=app" ;;
    *"get title"*) echo "Log in - Asana" ;;
    *)             echo "ok" ;;
  esac'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one asana
  [[ "$output" == *"NOT logged in"* ]]
  [[ "$output" == *"login page"* || "$output" == *"/-/login"* ]]
}

@test "verify_one detects hostname redirect (marketing landing page, e.g. Slack)" {
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  # Slack redirects unauthenticated users to marketing page on slack.com
  stub_command agent-browser 'case "$*" in
    *"get url"*)   echo "https://slack.com/get-started" ;;
    *"get title"*) echo "Slack | AI Work Platform & Productivity Tools" ;;
    *)             echo "ok" ;;
  esac'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one slack
  [[ "$output" == *"NOT logged in"* ]]
  [[ "$output" == *"hostname redirected"* ]]
  [[ "$output" == *"app.slack.com"* ]]
}

@test "verify_one detects Google SSO redirect (accounts.google.com) for GCal/Gmail" {
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'case "$*" in
    *"get url"*)   echo "https://accounts.google.com/ServiceLogin?service=cl" ;;
    *"get title"*) echo "Google Calendar - Sign in to Access..." ;;
    *)             echo "ok" ;;
  esac'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one gcal
  [[ "$output" == *"NOT logged in"* ]]
  # Could be caught by hostname mismatch OR URL pattern — either is correct
  [[ "$output" == *"accounts.google.com"* ]]
}

@test "verify_one reports ready when URL stays at expected host AND title not login" {
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'case "$*" in
    *"get url"*)   echo "https://app.asana.com/0/inbox" ;;
    *"get title"*) echo "My Tasks - Asana" ;;
    *)             echo "ok" ;;
  esac'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one asana
  [[ "$output" == *"✓ asana ready"* ]]
  [[ "$output" == *"My Tasks - Asana"* ]]
}

@test "verify_one falls back to title check when URL fetch is empty (abx daemon error)" {
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'case "$*" in
    *"get url"*)   echo "" ;;
    *"get title"*) echo "Sign in - Notion" ;;
    *)             echo "ok" ;;
  esac'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one notion
  [[ "$output" == *"NOT logged in"* ]]
  [[ "$output" == *"Sign in - Notion"* ]]
}

@test "verify_one detects zh-TW login title (登入)" {
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'case "$*" in
    *"get url"*)   echo "https://app.asana.com/0/inbox" ;;
    *"get title"*) echo "登入 - Asana" ;;
    *)             echo "ok" ;;
  esac'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one asana
  [[ "$output" == *"NOT logged in"* ]]
  [[ "$output" == *"登入 - Asana"* ]]
}

@test "verify_one detects ja login title (ログイン)" {
  mkdir -p "$XDG_CONFIG_HOME/collab-toolkit"
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Default" }
JSON
  stub_command agent-browser 'case "$*" in
    *"get url"*)   echo "https://www.notion.so" ;;
    *"get title"*) echo "Notion へログイン" ;;
    *)             echo "ok" ;;
  esac'
  cat > "$TEST_TMPDIR/bin/abx" <<'EOF'
#!/usr/bin/env bash
exec agent-browser "$@"
EOF
  chmod +x "$TEST_TMPDIR/bin/abx"

  MODE=shared run verify_one notion
  [[ "$output" == *"NOT logged in"* ]]
  [[ "$output" == *"ログイン"* ]]
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

@test "list_profiles_with_email reads macOS Chrome Local State and emits profile:email lines" {
  mkdir -p "$HOME/Library/Application Support/Google/Chrome"
  cat > "$HOME/Library/Application Support/Google/Chrome/Local State" <<'JSON'
{
  "profile": {
    "info_cache": {
      "Default":   { "user_name": "alice@example.com",      "name": "Personal" },
      "Profile 1": { "user_name": "alice.work@example.com", "name": "Work" },
      "Profile 2": { "name": "No signin" }
    }
  }
}
JSON
  run list_profiles_with_email
  [ "$status" -eq 0 ]
  [[ "$output" == *"Default: alice@example.com"* ]]
  [[ "$output" == *"Profile 1: alice.work@example.com"* ]]
  [[ "$output" == *"Profile 2: (no Google account)"* ]]
  [[ "$output" == *"— Personal"* ]]
  [[ "$output" == *"— Work"* ]]
}

@test "list_profiles_with_email returns non-zero when no Local State found in any candidate path" {
  run list_profiles_with_email
  [ "$status" -ne 0 ]
}

@test "list_profiles_with_email falls back to Linux Chrome path when macOS path absent" {
  mkdir -p "$HOME/.config/google-chrome"
  cat > "$HOME/.config/google-chrome/Local State" <<'JSON'
{ "profile": { "info_cache": { "Default": { "user_name": "linux@example.com", "name": "Linux Profile" } } } }
JSON
  run list_profiles_with_email
  [ "$status" -eq 0 ]
  [[ "$output" == *"Default: linux@example.com"* ]]
  [[ "$output" == *"— Linux Profile"* ]]
}
