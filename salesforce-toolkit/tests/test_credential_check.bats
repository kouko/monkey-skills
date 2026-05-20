#!/usr/bin/env bats
#
# Verifies salesforce-toolkit/scripts/sf/credential-check.sh — pure
# read-only diagnostic that emits a JSON status to stdout and always
# exits 0. Per Plan T2 acceptance:
#
#   (a) full PATH (mocked binaries present) → JSON shows all "installed"
#   (b) brew absent                          → .brew == "missing"
#   (c) sf absent                            → .sf_cli == "missing" AND .sf_version == null
#   (d) JSON always valid (`jq .` parse exits 0) regardless of state
#
# Exit code: ALWAYS 0 (diagnostic; never errors out).
#
# Mock strategy (mirrors test_launcher.bats T4 PATH-mock):
#   - mktemp -d per test → $TMPDIR_TEST
#   - write executable stubs (brew / sf / salesforce-mcp / node / npx) into
#     $TMPDIR_TEST that print canned `--version` output and canned `sf
#     org display --json` / `sf config get target-org --json` payloads
#   - run credential-check.sh with PATH set to $TMPDIR_TEST:/bin:/usr/bin
#   - `env -i` to scrub the inherited PATH so /opt/homebrew/bin etc.
#     cannot leak a real `brew` / `sf` into the mocked test
#   - jq must remain resolvable for the script's own JSON emission, so
#     we re-export the jq path via PATH augmentation when the system jq
#     lives outside /bin:/usr/bin (macOS ships jq in /usr/local/bin or
#     /opt/homebrew/bin).

CHECK="${BATS_TEST_DIRNAME}/../scripts/sf/credential-check.sh"

setup() {
  TMPDIR_TEST="$(mktemp -d -t sf-credcheck-test.XXXXXX)"
  export TMPDIR_TEST
  # Locate jq on the host. credential-check.sh shells out to jq for its
  # JSON emitter, so jq must be reachable inside the sandboxed PATH.
  # We CANNOT just add `dirname jq` to PATH — on macOS Homebrew, jq
  # lives in /opt/homebrew/bin alongside `brew` and `node`, which would
  # leak those binaries into the sandboxed test and defeat the (b)/(d)
  # "absent" cases. Instead we create an isolated `$JQ_SANDBOX` dir
  # holding only a symlink to jq.
  JQ_BIN="$(command -v jq || true)"
  if [ -z "${JQ_BIN}" ]; then
    skip "jq not available on host"
  fi
  JQ_SANDBOX="${TMPDIR_TEST}.jq"
  mkdir -p "$JQ_SANDBOX"
  ln -sf "$JQ_BIN" "$JQ_SANDBOX/jq"
  export JQ_BIN JQ_SANDBOX
}

teardown_jq_sandbox() {
  [ -n "${JQ_SANDBOX:-}" ] && rm -rf "$JQ_SANDBOX"
}

teardown() {
  [ -n "${TMPDIR_TEST:-}" ] && rm -rf "$TMPDIR_TEST"
  teardown_jq_sandbox
}

# Helper: write an executable stub at $1 with the body in $2.
make_stub() {
  local path="$1"
  local body="$2"
  cat >"$path" <<STUB
#!/usr/bin/env bash
${body}
STUB
  chmod +x "$path"
}

# Helper: stub `sf` that responds to multiple subcommands.
# - `sf --version`                                 → prints fake version
# - `sf config get target-org --json`              → prints alias JSON
# - `sf org display --target-org=<alias> --json`   → prints connectedStatus
make_sf_stub() {
  local path="$1"
  local version="${2:-@salesforce/cli/2.50.0 darwin-arm64 node-v20.0.0}"
  local alias="${3:-prod}"
  local connected_status="${4:-Connected}"
  cat >"$path" <<SF
#!/usr/bin/env bash
# Tiny sf-CLI mock that fans out by first arg.
case "\$1" in
  --version)
    printf '%s\n' "${version}"
    ;;
  config)
    # Expected: sf config get target-org --json
    if [ "\$2" = "get" ] && [ "\$3" = "target-org" ]; then
      cat <<JSON
{
  "status": 0,
  "result": [
    {"name": "target-org", "value": "${alias}", "success": true, "location": "Global"}
  ]
}
JSON
    else
      printf '{}\n'
    fi
    ;;
  org)
    # Expected: sf org display --target-org=<alias> --json
    if [ "\$2" = "display" ]; then
      cat <<JSON
{
  "status": 0,
  "result": {
    "alias": "${alias}",
    "username": "user@example.com",
    "instanceUrl": "https://example.my.salesforce.com",
    "connectedStatus": "${connected_status}"
  }
}
JSON
    else
      printf '{}\n'
    fi
    ;;
  *)
    printf '{}\n'
    ;;
esac
SF
  chmod +x "$path"
}

# ---------------------------------------------------------------------------
# Existence + executability + shape sanity
# ---------------------------------------------------------------------------

@test "credential-check.sh exists and is executable" {
  [ -f "$CHECK" ]
  [ -x "$CHECK" ]
}

# ---------------------------------------------------------------------------
# (a) all tools present → every field "installed", versions non-null
# ---------------------------------------------------------------------------

@test "(a) full PATH → all fields installed and versions present" {
  make_stub        "$TMPDIR_TEST/brew"           'printf "Homebrew 4.5.0\n"'
  make_sf_stub     "$TMPDIR_TEST/sf"
  make_stub        "$TMPDIR_TEST/salesforce-mcp" 'printf "@salesforce/mcp/1.2.3\n"'
  make_stub        "$TMPDIR_TEST/node"           'printf "v20.10.0\n"'

  run env -i PATH="$TMPDIR_TEST:$JQ_SANDBOX:/bin:/usr/bin" HOME="$HOME" "$CHECK"
  [ "$status" -eq 0 ]

  # JSON must parse cleanly.
  echo "$output" | jq -e '.' >/dev/null

  # Each tool field marked "installed".
  echo "$output" | jq -e '.brew == "installed"'           >/dev/null
  echo "$output" | jq -e '.sf_cli == "installed"'         >/dev/null
  echo "$output" | jq -e '.salesforce_mcp == "installed"' >/dev/null
  echo "$output" | jq -e '.node == "installed"'           >/dev/null

  # Versions resolved (non-null strings).
  echo "$output" | jq -e '.sf_version  != null and (.sf_version  | type == "string")' >/dev/null
  echo "$output" | jq -e '.mcp_version != null and (.mcp_version | type == "string")' >/dev/null

  # Default org parsed from stubbed `sf config get target-org`.
  echo "$output" | jq -e '.default_org == "prod"'               >/dev/null
  echo "$output" | jq -e '.default_org_status == "active"'      >/dev/null
}

# ---------------------------------------------------------------------------
# (b) brew absent → .brew == "missing", other fields untouched
# ---------------------------------------------------------------------------

@test "(b) brew absent → .brew == \"missing\" but sf still detected" {
  # No brew stub.
  make_sf_stub     "$TMPDIR_TEST/sf"
  make_stub        "$TMPDIR_TEST/salesforce-mcp" 'printf "@salesforce/mcp/1.2.3\n"'
  make_stub        "$TMPDIR_TEST/node"           'printf "v20.10.0\n"'

  run env -i PATH="$TMPDIR_TEST:$JQ_SANDBOX:/bin:/usr/bin" HOME="$HOME" "$CHECK"
  [ "$status" -eq 0 ]

  echo "$output" | jq -e '.' >/dev/null
  echo "$output" | jq -e '.brew == "missing"'             >/dev/null
  echo "$output" | jq -e '.sf_cli == "installed"'         >/dev/null
  echo "$output" | jq -e '.salesforce_mcp == "installed"' >/dev/null
}

# ---------------------------------------------------------------------------
# (c) sf absent → .sf_cli "missing" AND .sf_version null
# ---------------------------------------------------------------------------

@test "(c) sf absent → .sf_cli missing AND .sf_version null AND default_org null" {
  make_stub        "$TMPDIR_TEST/brew"           'printf "Homebrew 4.5.0\n"'
  # No sf stub.
  make_stub        "$TMPDIR_TEST/salesforce-mcp" 'printf "@salesforce/mcp/1.2.3\n"'
  make_stub        "$TMPDIR_TEST/node"           'printf "v20.10.0\n"'

  run env -i PATH="$TMPDIR_TEST:$JQ_SANDBOX:/bin:/usr/bin" HOME="$HOME" "$CHECK"
  [ "$status" -eq 0 ]

  echo "$output" | jq -e '.' >/dev/null
  echo "$output" | jq -e '.sf_cli == "missing"'         >/dev/null
  echo "$output" | jq -e '.sf_version == null'          >/dev/null
  echo "$output" | jq -e '.default_org == null'         >/dev/null
  echo "$output" | jq -e '.default_org_status == null'  >/dev/null
}

# ---------------------------------------------------------------------------
# (d) JSON always valid regardless of state (nothing on PATH)
# ---------------------------------------------------------------------------

@test "(d) nothing on PATH → valid JSON, all tools missing, exit 0" {
  # Empty $TMPDIR_TEST — no tool stubs at all.
  run env -i PATH="$TMPDIR_TEST:$JQ_SANDBOX:/bin:/usr/bin" HOME="$HOME" "$CHECK"
  [ "$status" -eq 0 ]

  echo "$output" | jq -e '.' >/dev/null
  echo "$output" | jq -e '.brew == "missing"'             >/dev/null
  echo "$output" | jq -e '.sf_cli == "missing"'           >/dev/null
  echo "$output" | jq -e '.salesforce_mcp == "missing"'   >/dev/null
  echo "$output" | jq -e '.node == "missing"'             >/dev/null
  echo "$output" | jq -e '.sf_version  == null'           >/dev/null
  echo "$output" | jq -e '.mcp_version == null'           >/dev/null
  echo "$output" | jq -e '.default_org == null'           >/dev/null
  echo "$output" | jq -e '.default_org_status == null'    >/dev/null
}
