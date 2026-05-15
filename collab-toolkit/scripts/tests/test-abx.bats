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
