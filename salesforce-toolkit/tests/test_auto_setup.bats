#!/usr/bin/env bats
#
# Verifies salesforce-toolkit/scripts/sf/auto-setup.sh —— 6-step idempotent
# orchestrator. Per Plan T3 acceptance, bats exercises ONLY the `--dry-run`
# code path; real brew install / OAuth login are never invoked here. The
# user dogfoods the non-dry-run flow in finishing-a-branch.
#
# Cases:
#   (a) pure `--dry-run`                            → 6-step plan printed
#   (b) `--dry-run --alias=foo`                     → final alias = foo
#   (c) `--dry-run --instance-url=https://acme...`  → inferred alias = acme
#   (d) `--alias=bar --instance-url=https://acme...`→ explicit wins (bar)
#   (e) `--no-alias`                                → alias omitted
#   (f) final stdout JSON `.dry_run == true`        → jq -e exit 0
#
# Output contract reminder:
#   - human-readable progress lines → stderr (`[auto-setup] step N/6: ...`)
#   - dry-run plan lines            → stderr (`[auto-setup] [dry-run] ...`)
#   - final result JSON             → stdout (single object)

AUTO_SETUP="${BATS_TEST_DIRNAME}/../scripts/sf/auto-setup.sh"

# `run --separate-stderr` is bats 1.5+; declare the floor once so every
# @test inherits it (matches the pattern in test_launcher.bats).
bats_require_minimum_version 1.5.0

# ---------------------------------------------------------------------------
# Existence + executability + shellcheck
# ---------------------------------------------------------------------------

@test "auto-setup.sh exists and is executable" {
  [ -f "$AUTO_SETUP" ]
  [ -x "$AUTO_SETUP" ]
}

# ---------------------------------------------------------------------------
# (a) pure --dry-run → 6 step plan printed (stderr) + stdout JSON valid
# ---------------------------------------------------------------------------
#
# Bats 1.x's plain `run` merges stderr into $output, which prevents jq
# parsing the result JSON cleanly. Use `--separate-stderr` so the JSON
# lands in $output and the [auto-setup] progress lines in $stderr —
# same pattern used by test_launcher.bats T4.

@test "(a) pure --dry-run prints 6-step plan and emits valid JSON" {
  run --separate-stderr "$AUTO_SETUP" --dry-run
  [ "$status" -eq 0 ]

  # stdout should be parseable JSON.
  echo "$output" | jq -e '.' >/dev/null

  # stderr should reference each of the 6 steps.
  [[ "$stderr" == *"step 1/6"* ]]
  [[ "$stderr" == *"step 2/6"* ]]
  [[ "$stderr" == *"step 3/6"* ]]
  [[ "$stderr" == *"step 4/6"* ]]
  [[ "$stderr" == *"step 5/6"* ]]
  [[ "$stderr" == *"step 6/6"* ]]
}

# ---------------------------------------------------------------------------
# (b) --alias=foo wins → final JSON .org_alias == "foo"
# ---------------------------------------------------------------------------

@test "(b) --dry-run --alias=foo → final org_alias is foo" {
  run --separate-stderr "$AUTO_SETUP" --dry-run --alias=foo
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.org_alias == "foo"' >/dev/null
}

# ---------------------------------------------------------------------------
# (c) --instance-url=https://acme.my.salesforce.com → inferred alias acme
# ---------------------------------------------------------------------------

@test "(c) --dry-run --instance-url=acme.my.salesforce.com → inferred alias acme" {
  run --separate-stderr "$AUTO_SETUP" --dry-run --instance-url=https://acme.my.salesforce.com
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.org_alias == "acme"' >/dev/null
  echo "$output" | jq -e '.instance_url == "https://acme.my.salesforce.com"' >/dev/null
}

# ---------------------------------------------------------------------------
# (d) explicit --alias beats --instance-url infer
# ---------------------------------------------------------------------------

@test "(d) --alias=bar --instance-url=acme.my.salesforce.com → bar wins" {
  run --separate-stderr "$AUTO_SETUP" --dry-run --alias=bar --instance-url=https://acme.my.salesforce.com
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.org_alias == "bar"' >/dev/null
}

# ---------------------------------------------------------------------------
# (e) --no-alias → alias omitted (final JSON .org_alias null)
# ---------------------------------------------------------------------------

@test "(e) --dry-run --no-alias → final org_alias is null" {
  run --separate-stderr "$AUTO_SETUP" --dry-run --no-alias --instance-url=https://acme.my.salesforce.com
  [ "$status" -eq 0 ]
  # --no-alias forces alias to be omitted, regardless of --instance-url.
  echo "$output" | jq -e '.org_alias == null' >/dev/null
}

# ---------------------------------------------------------------------------
# (f) final stdout JSON .dry_run == true
# ---------------------------------------------------------------------------

@test "(f) --dry-run → final JSON .dry_run == true" {
  run --separate-stderr "$AUTO_SETUP" --dry-run
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.dry_run == true' >/dev/null
}
