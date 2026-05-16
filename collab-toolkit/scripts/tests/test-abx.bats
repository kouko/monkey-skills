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
{ "mode": "shared", "chrome_profile": "Default", "dedicated_profile": "~/.local/share/collab-toolkit/profiles/dedicated" }
JSON
  run abx open https://example.com
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile Default"* ]]
  [[ "$output" == *"open https://example.com"* ]]
}

@test "abx with shared mode picks user-chosen profile name" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "shared", "chrome_profile": "Work", "dedicated_profile": "~/.local/share/collab-toolkit/profiles/dedicated" }
JSON
  run abx snapshot -i
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile Work"* ]]
  [[ "$output" == *"snapshot -i"* ]]
}

@test "abx with dedicated mode uses dedicated_profile path (unified, v0.1.2)" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<JSON
{ "mode": "dedicated", "chrome_profile": "Default", "dedicated_profile": "$TEST_TMPDIR/.local/share/collab-toolkit/profiles/dedicated" }
JSON
  run abx open https://app.asana.com
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile $TEST_TMPDIR/.local/share/collab-toolkit/profiles/dedicated"* ]]
}

@test "abx with dedicated mode expands tilde in dedicated_profile" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "dedicated", "chrome_profile": "Default", "dedicated_profile": "~/myprofile" }
JSON
  run abx get title
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile $HOME/myprofile"* ]]
}

@test "abx with dedicated mode ignores ABX_SERVICE env var (v0.1.2 — unified profile, no per-service routing)" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<JSON
{ "mode": "dedicated", "chrome_profile": "Default", "dedicated_profile": "$TEST_TMPDIR/dedicated" }
JSON
  ABX_SERVICE=asana run abx open https://app.asana.com
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile $TEST_TMPDIR/dedicated"* ]]
  # Should NOT route to a per-service subdir
  [[ "$output" != *"$TEST_TMPDIR/dedicated/asana"* ]]
}

@test "abx with dedicated mode errors when dedicated_profile missing (v0.1.0/v0.1.1 migration)" {
  cat > "$XDG_CONFIG_HOME/collab-toolkit/config.json" <<'JSON'
{ "mode": "dedicated", "chrome_profile": "Default", "profiles_root": "~/.local/share/collab-toolkit/profiles" }
JSON
  run abx open https://example.com
  [ "$status" -ne 0 ]
  [[ "$output" == *"dedicated_profile"* ]]
  [[ "$output" == *"--switch-mode"* ]] || [[ "$output" == *"--dedicated"* ]]
}
