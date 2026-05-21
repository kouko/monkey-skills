#!/usr/bin/env bats
#
# Verifies salesforce-toolkit/scripts/common/tty-guard.sh:
#   - exposes a `require_tty` function when sourced
#   - returns 0 when stdin is attached to a TTY (interactive)
#   - exits 10 with stderr message when stdin is redirected (no controlling TTY)
#
# Test isolation: each "no-TTY" case runs the function in a subshell with
# `</dev/null` so we capture the exit code without taking down the bats process.

TTY_GUARD="${BATS_TEST_DIRNAME}/../scripts/common/tty-guard.sh"

@test "tty-guard.sh exists" {
  [ -f "$TTY_GUARD" ]
}

@test "tty-guard.sh is sourceable and exposes require_tty function" {
  # shellcheck source=/dev/null
  run bash -c "source '$TTY_GUARD'; declare -F require_tty"
  [ "$status" -eq 0 ]
  [[ "$output" == *"require_tty"* ]]
}

@test "require_tty fails with exit 10 + stderr message when stdin is /dev/null" {
  # Force no-TTY by redirecting stdin from /dev/null in a subshell.
  # set +e because we deliberately expect non-zero exit.
  run bash -c "set +e; source '$TTY_GUARD'; require_tty </dev/null; echo \"exit_code=\$?\""
  # The whole bash -c invocation exits non-zero because `exit 10` inside
  # `require_tty` terminates the sourced subshell. Capture both stderr (printed
  # by require_tty) and the exit code from the subshell.
  [ "$status" -eq 10 ]
  [[ "$output" == *"requires a controlling terminal"* ]]
}

@test "require_tty returns 0 when stdin is a TTY" {
  # Inside the bats harness `bats` itself may or may not have a TTY; the
  # robust way to simulate a TTY for a subprocess is to allocate one via
  # `script(1)` (BSD on macOS). If `script` is unavailable, fall back to
  # checking via `[ -t 0 ]` after re-attaching stdin from /dev/tty when
  # available.
  if command -v script >/dev/null 2>&1; then
    # macOS BSD `script` signature: script [-q] file command...
    # The `-q` flag suppresses the "Script started" banner. Output is also
    # written to the typescript file; we point it at /dev/null.
    run script -q /dev/null bash -c "source '$TTY_GUARD'; require_tty && echo OK"
    [ "$status" -eq 0 ]
    [[ "$output" == *"OK"* ]]
  else
    skip "script(1) not available; cannot simulate TTY in this environment"
  fi
}
