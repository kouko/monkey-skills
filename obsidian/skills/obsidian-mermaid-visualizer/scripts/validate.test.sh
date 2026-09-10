#!/usr/bin/env bash
# Characterization test for validate.sh — proves the checker fires when it
# should and stays quiet when it should not. Run: bash scripts/validate.test.sh
#
# Assertions match verdicts anchored to line start (^PASS / ^FAIL / ^WARN).
# An unanchored search is vacuous here: validate.sh's own trailing banner
# contains the word "FAIL", so a bare grep for it passes even when the
# checker does nothing.
set -uo pipefail
V="$(cd "$(dirname "$0")" && pwd)/validate.sh"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0
expect() { # desc  expected_regex  actual
  if printf '%s' "$3" | grep -qE -- "$2"; then echo "ok   - $1"; pass=$((pass+1))
  else echo "FAIL - $1"; echo "       wanted /$2/ in: $3"; fail=$((fail+1)); fi
}

# --- quiet when it should be -------------------------------------------------

# 1) valid quoted-CJK quadrant -> PASS, exit 0
good="$(printf 'quadrantChart\n  title 定位\n  x-axis "低" --> "高"\n  y-axis "低" --> "高"\n  "甲": [0.3,0.7]\n')"
out="$(printf '%s' "$good" | bash "$V" - 2>&1)"; rc=$?
expect "valid CJK quadrant -> PASS" "^PASS" "$out"
expect "valid CJK quadrant -> exit 0" "^0$" "$rc"

# 2) a markdown file with no mermaid at all -> clean exit, no verdict
printf '# note\n\nprose only\n' > "$TMP/none.md"
out="$(bash "$V" "$TMP/none.md" 2>&1)"; rc=$?
expect "no diagrams -> no FAIL verdict" "^no mermaid diagrams found" "$out"
expect "no diagrams -> exit 0" "^0$" "$rc"

# --- fires when it should ----------------------------------------------------

# 3) malformed arrow -> FAIL, exit 1, and the reason names the parser error
bad="$(printf 'graph TD\n  A --> \n')"
out="$(printf '%s' "$bad" | bash "$V" - 2>&1)"; rc=$?
expect "malformed arrow -> FAIL" "^FAIL" "$out"
expect "malformed arrow -> exit 1" "^1$" "$rc"
expect "malformed arrow -> reason names the parse error" "(Lexical|Syntax|Parse) error" "$out"

# 4) empty mermaid block -> FAIL (regression: awk used to create no file at all,
#    so an empty block was silently skipped and a lone empty block exited 0)
printf '# note\n\n```mermaid\n```\n' > "$TMP/empty.md"
out="$(bash "$V" "$TMP/empty.md" 2>&1)"; rc=$?
expect "empty block -> FAIL" "^FAIL" "$out"
expect "empty block -> exit 1" "^1$" "$rc"

# 5) attributed fence -> extracted, not skipped (regression: the opener regex
#    required a bare ```mermaid line, so ```mermaid {theme} yielded "no
#    diagrams found" and a vacuous green exit)
printf '# note\n\n```mermaid {theme: dark}\ngraph TD\n  A --> B\n```\n' > "$TMP/attr.md"
out="$(bash "$V" "$TMP/attr.md" 2>&1)"; rc=$?
expect "attributed fence -> extracted and PASSes" "^PASS" "$out"
if printf '%s' "$out" | grep -q '^no mermaid diagrams found'; then
  echo "FAIL - attributed fence -> must not report 'no diagrams'"; fail=$((fail+1))
else
  echo "ok   - attributed fence -> must not report 'no diagrams'"; pass=$((pass+1))
fi

# --- advisory ----------------------------------------------------------------

# 6) quoted pie title -> WARN (literal quotes reach the rendered text)
warn="$(printf 'pie title "市場佔有率"\n  "甲" : 60\n  "乙" : 40\n')"
out="$(printf '%s' "$warn" | bash "$V" - 2>&1)"
expect "quoted pie title -> WARN" "^WARN" "$out"

echo "--- $pass passed, $fail failed"
[ "$fail" -eq 0 ]
