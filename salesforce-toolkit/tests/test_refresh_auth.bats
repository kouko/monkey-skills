#!/usr/bin/env bats
#
# Verifies salesforce-toolkit/scripts/sf/refresh-auth.sh — standalone
# re-auth helper that wraps `sf org login web --alias=<X> --set-default`.
# Per Plan T4 acceptance, bats exercises ONLY the `--dry-run` + arg-parse
# + TTY-guard paths; real OAuth is never invoked here. The user dogfoods
# the non-dry-run flow in finishing-a-branch.
#
# Cases (Plan T4 acceptance §GREEN):
#   (a) --dry-run                  → does NOT invoke `sf org login` (plan-only)
#   (b) --alias=foo --dry-run      → planned command includes `--alias=foo`
#   (c) no TTY (</dev/null) sans --dry-run → exit 10 + stderr "controlling terminal"
#
# Output contract reminder (from Task description):
#   - human-readable progress lines → stderr
#   - dry-run plan lines            → stderr
#   - final result JSON             → stdout (single object) — only on real
#                                     re-auth path, not exercised in bats

REFRESH_AUTH="${BATS_TEST_DIRNAME}/../scripts/sf/refresh-auth.sh"

# `run --separate-stderr` is bats 1.5+; declare the floor once.
bats_require_minimum_version 1.5.0

# ---------------------------------------------------------------------------
# Existence + executability
# ---------------------------------------------------------------------------

@test "refresh-auth.sh exists and is executable" {
  [ -f "$REFRESH_AUTH" ]
  [ -x "$REFRESH_AUTH" ]
}

# ---------------------------------------------------------------------------
# (a) --dry-run does NOT invoke `sf org login` (plan-only)
# ---------------------------------------------------------------------------
#
# Verification strategy: --dry-run runs MUST succeed even when `sf` is
# absent from PATH. We strip PATH down to a minimal set lacking `sf` and
# confirm exit 0 + a stderr plan line referencing `sf org login web`.
# If the script actually invoked `sf`, it would fail with exit 12.

@test "(a) --dry-run does not invoke sf; succeeds without sf in PATH" {
  # Bare PATH — /usr/bin + /bin cover coreutils (printf, tty, command);
  # `sf` lives in Homebrew prefix and is NOT in this set.
  run --separate-stderr env -i PATH=/usr/bin:/bin HOME="$HOME" \
      bash "$REFRESH_AUTH" --dry-run
  [ "$status" -eq 0 ]
  # Plan line MUST mention the command that would have run.
  [[ "$stderr" == *"sf org login web"* ]]
  # Sanity: dry-run marker present.
  [[ "$stderr" == *"dry-run"* ]]
}

# ---------------------------------------------------------------------------
# (b) --alias=foo --dry-run → planned command includes --alias=foo
# ---------------------------------------------------------------------------

@test "(b) --alias=foo --dry-run → plan output contains --alias=foo" {
  run --separate-stderr env -i PATH=/usr/bin:/bin HOME="$HOME" \
      bash "$REFRESH_AUTH" --alias=foo --dry-run
  [ "$status" -eq 0 ]
  [[ "$stderr" == *"--alias=foo"* ]]
}

# ---------------------------------------------------------------------------
# (c) no TTY (stdin /dev/null) without --dry-run → exit 10 + stderr
#     "controlling terminal"
# ---------------------------------------------------------------------------
#
# In bats the harness already has no TTY on stdin; redirecting from
# /dev/null makes it explicit and matches the contract require_tty
# enforces. We MUST NOT pass --dry-run here — that path skips the guard.

@test "(c) no TTY without --dry-run → exit 10 + 'controlling terminal' stderr" {
  # Invoke directly with stdin redirected from /dev/null; the script's
  # `exit 10` (from require_tty) propagates as the run's status.
  # Bats's default `run` merges stderr into $output, so the stderr
  # `controlling terminal` line is visible there.
  run "$REFRESH_AUTH" </dev/null
  [ "$status" -eq 10 ]
  [[ "$output" == *"controlling terminal"* ]]
}
