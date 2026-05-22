#!/usr/bin/env bats
#
# Verifies salesforce-toolkit/scripts/sf/alias-infer.sh:
#   - exposes an `infer_alias` function when sourced
#   - implements 3-layer alias inference per spec Decision Q3:
#       Layer 1: explicit user_alias override wins
#       Layer 2: regex parse of *.my.salesforce.com / *.lightning.force.com /
#                *.sandbox.my.salesforce.com → lowercased subdomain, `--` → `-`
#       Layer 3: well-known endpoint fallback
#                  login.salesforce.com or empty → `prod`
#                  test.salesforce.com → `sandbox`
#                  otherwise → empty (caller falls back to sf username)
#
# Each test sources the library in a fresh `bash -c` subshell so failures in
# one assertion do not contaminate the next. Output is captured via `run`.

ALIAS_INFER="${BATS_TEST_DIRNAME}/../scripts/sf/alias-infer.sh"

@test "alias-infer.sh exists" {
  [ -f "$ALIAS_INFER" ]
}

@test "alias-infer.sh is sourceable and exposes infer_alias function" {
  # shellcheck source=/dev/null
  run bash -c "source '$ALIAS_INFER'; declare -F infer_alias"
  [ "$status" -eq 0 ]
  [[ "$output" == *"infer_alias"* ]]
}

# ---------------------------------------------------------------------------
# Layer 1 — explicit override wins regardless of URL
# ---------------------------------------------------------------------------

@test "(a) explicit user_alias overrides everything else" {
  run bash -c "source '$ALIAS_INFER'; infer_alias '' 'myorg'"
  [ "$status" -eq 0 ]
  [ "$output" = "myorg" ]
}

# ---------------------------------------------------------------------------
# Layer 2 — subdomain inference from *.my.salesforce.com family
# ---------------------------------------------------------------------------

@test "(b) acme.my.salesforce.com → acme" {
  run bash -c "source '$ALIAS_INFER'; infer_alias 'https://acme.my.salesforce.com' ''"
  [ "$status" -eq 0 ]
  [ "$output" = "acme" ]
}

@test "(c) acme--devsbx.sandbox.my.salesforce.com → acme-devsbx (collapse --)" {
  run bash -c "source '$ALIAS_INFER'; infer_alias 'https://acme--devsbx.sandbox.my.salesforce.com' ''"
  [ "$status" -eq 0 ]
  [ "$output" = "acme-devsbx" ]
}

@test "(d) MIXED-Case.my.salesforce.com → mixed-case (lowercase)" {
  run bash -c "source '$ALIAS_INFER'; infer_alias 'https://MIXED-Case.my.salesforce.com' ''"
  [ "$status" -eq 0 ]
  [ "$output" = "mixed-case" ]
}

# ---------------------------------------------------------------------------
# Layer 3 — well-known endpoint fallback
# ---------------------------------------------------------------------------

@test "(e) login.salesforce.com → prod" {
  run bash -c "source '$ALIAS_INFER'; infer_alias 'https://login.salesforce.com' ''"
  [ "$status" -eq 0 ]
  [ "$output" = "prod" ]
}

@test "(f) test.salesforce.com → sandbox" {
  run bash -c "source '$ALIAS_INFER'; infer_alias 'https://test.salesforce.com' ''"
  [ "$status" -eq 0 ]
  [ "$output" = "sandbox" ]
}

@test "(g) empty URL → prod (default)" {
  run bash -c "source '$ALIAS_INFER'; infer_alias '' ''"
  [ "$status" -eq 0 ]
  [ "$output" = "prod" ]
}

@test "(h) unrelated URL → empty string (let sf use username)" {
  run bash -c "source '$ALIAS_INFER'; infer_alias 'https://random.example.com' ''"
  [ "$status" -eq 0 ]
  [ "$output" = "" ]
}

# ---------------------------------------------------------------------------
# Direct-invocation entry point — enables `bash alias-infer.sh URL [ALIAS]`
# for Claude-orchestrated /sf-setup (Step 5) without a `source ...` wrapper.
# ---------------------------------------------------------------------------

@test "(i) direct invocation: acme URL prints acme" {
  run bash "$ALIAS_INFER" "https://acme.my.salesforce.com" ""
  [ "$status" -eq 0 ]
  [ "$output" = "acme" ]
}

@test "(j) direct invocation: explicit alias override wins" {
  run bash "$ALIAS_INFER" "https://acme.my.salesforce.com" "myorg"
  [ "$status" -eq 0 ]
  [ "$output" = "myorg" ]
}

@test "(k) direct invocation: login.salesforce.com prints prod" {
  run bash "$ALIAS_INFER" "https://login.salesforce.com" ""
  [ "$status" -eq 0 ]
  [ "$output" = "prod" ]
}

@test "(l) direct invocation: no args → prod (empty URL defaults to prod)" {
  run bash "$ALIAS_INFER"
  [ "$status" -eq 0 ]
  [ "$output" = "prod" ]
}
