#!/usr/bin/env bash
# test-privacy-scan.sh
#
# CI is bash-only for dev-workflow (dev-workflow/tests/test-*.sh); there is
# no pytest job that runs dev-workflow/skills/git-memory/scripts/test_privacy_scan.py
# in CI, so that pytest suite has zero regression protection there. This
# test exercises the REAL privacy-scan.py CLI (not the pytest internals) so
# the layer-1 secrets scanner's observable contract is pinned in the bash
# lane CI actually runs.
#
# Usage:
#   bash dev-workflow/tests/test-privacy-scan.sh

set -u

DEV_WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCANNER="$DEV_WORKFLOW_DIR/skills/git-memory/scripts/privacy-scan.py"

PASS_COUNT=0
FAIL_COUNT=0
pass() { echo "PASS — $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL — $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

TMPDIR_LOCAL="$(mktemp -d "${TMPDIR:-/tmp}/privacy-scan-test.XXXXXX")"
cleanup() { rm -rf "$TMPDIR_LOCAL"; }
trap cleanup EXIT

# -------------------------------------------------------------------------
# Check 0 — the scanner script exists at all.

if [ ! -f "$SCANNER" ]; then
  fail "privacy-scan.py does not exist at $SCANNER"
  echo ""
  echo "================================================================"
  echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
  echo "================================================================"
  exit 1
else
  pass "privacy-scan.py exists"
fi

# -------------------------------------------------------------------------
# Check 1 — clean text (ordinary commit prose, no secret) → exit 0 and
# empty JSON list.

CLEAN_FILE="$TMPDIR_LOCAL/clean.txt"
cat >"$CLEAN_FILE" <<'EOF'
Refactored the login flow to handle empty usernames gracefully.
Added a regression test for the redirect-loop bug reported last week.
EOF

CLEAN_OUT="$(python3 "$SCANNER" --text-file "$CLEAN_FILE")"
CLEAN_EXIT=$?

if [ "$CLEAN_EXIT" -ne 0 ]; then
  fail "clean text: expected exit 0, got $CLEAN_EXIT"
elif [ "$CLEAN_OUT" != "[]" ]; then
  fail "clean text: expected empty JSON list '[]', got: $CLEAN_OUT"
else
  pass "clean text → exit 0, empty JSON list"
fi

# -------------------------------------------------------------------------
# Check 2 — planted AWS key (AKIA + 16 upper-alnum) → exit 3 and a JSON
# finding naming the aws pattern.

AWS_KEY="AKIAABCDEFGHIJ1234KL"
AWS_FILE="$TMPDIR_LOCAL/aws.txt"
cat >"$AWS_FILE" <<EOF
Rotated old credentials, one of which was $AWS_KEY, during the cleanup.
EOF

AWS_OUT="$(python3 "$SCANNER" --text-file "$AWS_FILE")"
AWS_EXIT=$?

if [ "$AWS_EXIT" -ne 3 ]; then
  fail "AWS key: expected exit 3, got $AWS_EXIT"
elif ! echo "$AWS_OUT" | grep -qF "aws_access_key"; then
  fail "AWS key: JSON output missing 'aws_access_key' pattern name: $AWS_OUT"
else
  pass "planted AWS key → exit 3, finding names aws_access_key"
fi

# -------------------------------------------------------------------------
# Check 3 — planted PEM private-key header → exit 3.

PEM_FILE="$TMPDIR_LOCAL/pem.txt"
cat >"$PEM_FILE" <<'EOF'
-----BEGIN RSA PRIVATE KEY-----
EOF

PEM_OUT="$(python3 "$SCANNER" --text-file "$PEM_FILE")"
PEM_EXIT=$?

if [ "$PEM_EXIT" -ne 3 ]; then
  fail "PEM header: expected exit 3, got $PEM_EXIT"
elif ! echo "$PEM_OUT" | grep -qF "pem_private_key"; then
  fail "PEM header: JSON output missing 'pem_private_key' pattern name: $PEM_OUT"
else
  pass "planted PEM private-key header → exit 3, finding names pem_private_key"
fi

# -------------------------------------------------------------------------
# Check 3b — planted Slack bot token → exit 3, finding names slack_token.

SLACK_FILE="$TMPDIR_LOCAL/slack.txt"
cat >"$SLACK_FILE" <<'EOF'
token: xoxb-1234567890-1234567890123-abcdefghijklmnopqrstuvwx
EOF

SLACK_OUT="$(python3 "$SCANNER" --text-file "$SLACK_FILE")"
SLACK_EXIT=$?

if [ "$SLACK_EXIT" -ne 3 ]; then
  fail "Slack token: expected exit 3, got $SLACK_EXIT"
elif ! echo "$SLACK_OUT" | grep -qF "slack_token"; then
  fail "Slack token: JSON output missing 'slack_token' pattern name: $SLACK_OUT"
else
  pass "planted Slack bot token → exit 3, finding names slack_token"
fi

# -------------------------------------------------------------------------
# Check 3c — planted generic secret assignment → exit 3, finding names
# generic_secret_assignment.

GENERIC_FILE="$TMPDIR_LOCAL/generic.txt"
cat >"$GENERIC_FILE" <<'EOF'
SECRET=abcdefghijklmnopqrstuvwxyz
EOF

GENERIC_OUT="$(python3 "$SCANNER" --text-file "$GENERIC_FILE")"
GENERIC_EXIT=$?

if [ "$GENERIC_EXIT" -ne 3 ]; then
  fail "generic secret assignment: expected exit 3, got $GENERIC_EXIT"
elif ! echo "$GENERIC_OUT" | grep -qF "generic_secret_assignment"; then
  fail "generic secret assignment: JSON output missing 'generic_secret_assignment' pattern name: $GENERIC_OUT"
else
  pass "planted generic secret assignment → exit 3, finding names generic_secret_assignment"
fi

# -------------------------------------------------------------------------
# Check 4 — redaction: the full planted secret literal must NOT appear
# anywhere in stdout (only a short redacted prefix may).

if echo "$AWS_OUT" | grep -qF "$AWS_KEY"; then
  fail "redaction: full AWS key literal '$AWS_KEY' leaked into stdout: $AWS_OUT"
else
  pass "redaction: full AWS key literal absent from stdout"
fi

# -------------------------------------------------------------------------
# Check 5 — stdin path works (pipe text in, no --text-file).

STDIN_OUT="$(printf 'Just an ordinary line of commit prose.\n' | python3 "$SCANNER")"
STDIN_EXIT=$?

if [ "$STDIN_EXIT" -ne 0 ]; then
  fail "stdin path: expected exit 0, got $STDIN_EXIT"
elif [ "$STDIN_OUT" != "[]" ]; then
  fail "stdin path: expected empty JSON list '[]', got: $STDIN_OUT"
else
  pass "stdin path (no --text-file) → exit 0, empty JSON list"
fi

# -------------------------------------------------------------------------
# Summary

echo ""
echo "================================================================"
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "================================================================"

if [ "${FAIL_COUNT}" -gt 0 ]; then
  exit 1
fi
exit 0
