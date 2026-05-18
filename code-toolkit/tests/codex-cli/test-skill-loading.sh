#!/usr/bin/env bash
# test-skill-loading.sh — verify Codex CLI plugin install + skill discovery
#
# Phase 2.5 v0.4.0 build deliverable. Runs the install + details probe;
# verifies all 11 expected skills are discoverable (v0.9.0+).
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
  codex plugin marketplace add /path/to/monkey-skills/.worktrees/code-toolkit-design --scope local
  codex plugin install code-toolkit@monkey-skills --scope local

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
  codex plugin marketplace add . --scope local
  codex plugin install code-toolkit@monkey-skills --scope local
EOF
  exit 1
fi

echo "OK: code-toolkit installed"

# -------------------------------------------------------------------------
# Step 2 — fetch skill list

# ⚠️ TBD verify exact Codex CLI command for skill enumeration. The
# Claude Code analogue is `claude plugin details <name>` which lists
# skills. Codex CLI's command name might differ.

DETAILS_OUTPUT=$(codex plugin details code-toolkit 2>&1)
if [ -z "${DETAILS_OUTPUT}" ]; then
  echo "FAIL: 'codex plugin details code-toolkit' returned empty output"
  echo "      (⚠️ verify Codex CLI's plugin-details command name)"
  exit 1
fi

# -------------------------------------------------------------------------
# Step 3 — verify each expected skill appears in the details output

missing=()
for skill in "${EXPECTED_SKILLS[@]}"; do
  if ! echo "${DETAILS_OUTPUT}" | grep -q "${skill}"; then
    missing+=("${skill}")
  fi
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "FAIL: ${#missing[@]} of ${#EXPECTED_SKILLS[@]} expected skills missing from Codex CLI plugin details:"
  for s in "${missing[@]}"; do
    echo "  - ${s}"
  done
  exit 1
fi

echo "OK: all ${#EXPECTED_SKILLS[@]} expected skills discoverable in Codex CLI"
echo "PASS — Codex CLI plugin install + skill enumeration verified"
exit 0
