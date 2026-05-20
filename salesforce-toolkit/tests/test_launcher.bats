#!/usr/bin/env bats
#
# Verifies salesforce-toolkit/bin/sf-mcp-launcher.sh dispatch logic
# (Decision Q1 Path D + Q7 brew fallback):
#
#   1. sf-mcp-server on PATH → exec sf-mcp-server "$@"
#      (brew formula `salesforce-mcp` installs binary named
#      `sf-mcp-server`; verified dogfood 2026-05-20)
#   2. else npx on PATH       → exec npx -y @salesforce/mcp "$@"
#   3. else                   → stderr 指向 /salesforce-toolkit:sf-setup + exit 127
#
# Mock strategy: write tiny shell stubs to a per-test tmpdir, prepend that
# tmpdir to PATH, run launcher, assert stdout (stubs echo what argv they
# received) and exit code. No real sf-mcp-server / npx invocation.

LAUNCHER="${BATS_TEST_DIRNAME}/../bin/sf-mcp-launcher.sh"

setup() {
  TMPDIR_TEST="$(mktemp -d -t sf-launcher-test.XXXXXX)"
  export TMPDIR_TEST
}

teardown() {
  [ -n "${TMPDIR_TEST:-}" ] && rm -rf "$TMPDIR_TEST"
}

# Helper: write an executable stub at $1 that echoes "STUB <basename> $@".
make_stub() {
  local path="$1"
  cat >"$path" <<'STUB'
#!/usr/bin/env bash
printf 'STUB %s %s\n' "$(basename "$0")" "$*"
STUB
  chmod +x "$path"
}

@test "launcher file exists and is executable" {
  [ -f "$LAUNCHER" ]
  [ -x "$LAUNCHER" ]
}

# PATH note: we prepend the mock dir to a *minimal* system PATH (/bin:/usr/bin)
# so that the launcher's `#!/usr/bin/env bash` shebang can still resolve `env`
# and `bash`, but `sf-mcp-server` / `npx` resolve only when the test placed
# a stub for them in $TMPDIR_TEST. A fully empty PATH would also strip bash
# itself and make the test exit 127 for the wrong reason.

@test "(a) sf-mcp-server on PATH → exec sf-mcp-server with forwarded args" {
  make_stub "$TMPDIR_TEST/sf-mcp-server"
  # No npx stub in $TMPDIR_TEST → proves selection is sf-mcp-server first.
  # /bin:/usr/bin on macOS does not normally have npx either.
  run env -i PATH="$TMPDIR_TEST:/bin:/usr/bin" HOME="$HOME" "$LAUNCHER" \
    --orgs DEFAULT_TARGET_ORG --toolsets data
  [ "$status" -eq 0 ]
  [[ "$output" == *"STUB sf-mcp-server --orgs DEFAULT_TARGET_ORG --toolsets data"* ]]
}

@test "(b) only npx on PATH → exec npx -y @salesforce/mcp with forwarded args" {
  make_stub "$TMPDIR_TEST/npx"
  run env -i PATH="$TMPDIR_TEST:/bin:/usr/bin" HOME="$HOME" "$LAUNCHER" \
    --orgs DEFAULT_TARGET_ORG --toolsets data
  [ "$status" -eq 0 ]
  # npx must be invoked with `-y @salesforce/mcp` then user args.
  [[ "$output" == *"STUB npx -y @salesforce/mcp --orgs DEFAULT_TARGET_ORG --toolsets data"* ]]
}

@test "(c) neither sf-mcp-server nor npx → exit 127 + stderr mentions sf-setup" {
  # No stubs placed in $TMPDIR_TEST; /bin:/usr/bin lets bash/env resolve.
  # --separate-stderr puts the stderr stream in $stderr; run -127 declares
  # the expected exit code inline (bats 1.5+).
  bats_require_minimum_version 1.5.0
  run -127 --separate-stderr env -i PATH="$TMPDIR_TEST:/bin:/usr/bin" HOME="$HOME" "$LAUNCHER" \
    --orgs DEFAULT_TARGET_ORG
  [[ "$stderr" == *"sf-setup"* ]]
}
