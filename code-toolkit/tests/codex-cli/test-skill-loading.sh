#!/usr/bin/env bash
# test-skill-loading.sh — verify Codex CLI plugin install + discovery
#
# Phase 2.5 v0.4.0 build deliverable. Confirms code-toolkit is
# installed + enabled via `codex plugin list` (the real Codex 0.139.0
# enumeration command). Codex 0.139.0 has no per-plugin skill-listing
# command (no `plugin details` analogue), so per-skill assertion is
# documented as a limitation, not faked against plugin-level output.
#
# Real Codex 0.139.0 `codex plugin` surface (probed from
# `codex plugin --help`): add / list / marketplace {add,list,upgrade,
# remove} / remove. There is NO `install`, NO `details`, NO `--scope`.
#
# Prerequisite: Codex CLI installed (https://github.com/openai/codex
# or equivalent). Script gracefully skips with install instructions if
# not present.
#
# Usage:
#   bash code-toolkit/tests/codex-cli/test-skill-loading.sh

set -u

EXPECTED_SKILLS=(
  using-code-toolkit
  brainstorming
  writing-plans
  subagent-driven-development
  tdd-iron-law
  systematic-debugging
  requesting-code-review
  verification-before-completion
  finishing-a-development-branch
  using-git-worktrees
  dispatching-parallel-agents
)

# -------------------------------------------------------------------------
# Step 0 — detect Codex CLI

if ! command -v codex >/dev/null 2>&1; then
  cat <<'EOF'
SKIP: Codex CLI not installed.

To install + run this test:

  # Option 1 — npm (if Codex CLI ships via npm)
  npm install -g codex-cli   # ⚠️ TBD verify exact package name

  # Option 2 — from source (https://github.com/openai/codex or similar)
  # follow upstream README

  # Then add this plugin as a local marketplace (mirrors the Claude
  # Code workflow per CHANGELOG [0.1.0]):
  codex plugin marketplace add /path/to/monkey-skills/.worktrees/code-toolkit-design
  codex plugin add code-toolkit@monkey-skills

  # Re-run this script:
  bash code-toolkit/tests/codex-cli/test-skill-loading.sh

Exit code 0 (SKIP, not FAIL) — Phase 2.5 verification deferred until
Codex CLI install. The Phase 2.5 BUILD (manifest + hook + scripts +
docs) is complete; only the verification ritual remains.
EOF
  exit 0
fi

echo "OK: codex found at $(command -v codex)"

# -------------------------------------------------------------------------
# Step 1 — verify code-toolkit is installed

if ! codex plugin list 2>&1 | grep -q "code-toolkit"; then
  cat <<'EOF'
FAIL: code-toolkit not installed in Codex CLI.

Install it first:

  cd /path/to/monkey-skills/.worktrees/code-toolkit-design
  codex plugin marketplace add .
  codex plugin add code-toolkit@monkey-skills
EOF
  exit 1
fi

echo "OK: code-toolkit installed"

# -------------------------------------------------------------------------
# Step 2 — confirm code-toolkit is installed AND enabled

# Codex 0.139.0 `codex plugin list` enumerates PLUGINS (not the skills
# inside a plugin) as a table: "PLUGIN  STATUS  VERSION  PATH" where
# STATUS reads "installed, enabled" for an active plugin. There is no
# `plugin details` / per-plugin skill-listing command in this surface,
# so we assert on the plugin row, not on individual skill names.

LIST_OUTPUT=$(codex plugin list 2>&1)
if ! echo "${LIST_OUTPUT}" | grep -E 'code-toolkit' | grep -qi 'enabled'; then
  echo "FAIL: code-toolkit not shown as enabled in 'codex plugin list':"
  echo "${LIST_OUTPUT}" | grep -E 'code-toolkit' || echo "  (no code-toolkit row found)"
  exit 1
fi

echo "OK: code-toolkit installed + enabled"

# -------------------------------------------------------------------------
# Step 3 — per-skill enumeration: NOT available in Codex 0.139.0
#
# Codex 0.139.0 exposes no command that lists the skills bundled inside
# an installed plugin (no `plugin details` analogue). The EXPECTED_SKILLS
# array above is retained as the authoritative manifest of what
# code-toolkit ships; verifying each is loadable requires opening a
# Codex session and invoking the skill, which is the live ritual in
# tests/codex-cli/README.md (not a non-interactive `plugin` subcommand).
#
# If a future Codex release adds a skill-enumeration command, re-add an
# assertion loop over EXPECTED_SKILLS here.

echo "NOTE: skipped per-skill enumeration — Codex 0.139.0 has no"
echo "      skill-listing command; ${#EXPECTED_SKILLS[@]} expected skills tracked in this script."
echo "PASS — Codex CLI plugin install + enabled-state verified"
exit 0
