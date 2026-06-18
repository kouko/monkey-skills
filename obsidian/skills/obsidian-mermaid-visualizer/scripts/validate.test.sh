#!/usr/bin/env bash
# Characterization test for validate.sh — proves it flags the exact bug class
# this skill's quoting fixes were about. Run: bash scripts/validate.test.sh
set -uo pipefail
V="$(cd "$(dirname "$0")" && pwd)/validate.sh"
pass=0; fail=0
expect() { # desc  expected_substr  actual
  if printf '%s' "$3" | grep -q -- "$2"; then echo "ok   - $1"; pass=$((pass+1))
  else echo "FAIL - $1"; echo "       wanted /$2/ in: $3"; fail=$((fail+1)); fi
}

# 1) valid quoted-CJK quadrant -> PASS, exit 0
good="$(printf 'quadrantChart\n  title 定位\n  x-axis "低" --> "高"\n  y-axis "低" --> "高"\n  "甲": [0.3,0.7]\n')"
out="$(printf '%s' "$good" | bash "$V" - 2>&1)"; rc=$?
expect "valid CJK quadrant -> PASS" "PASS" "$out"
expect "valid CJK quadrant -> exit 0" "^0$" "$rc"

# 2) unquoted-CJK architecture -> FAIL, exit 1
bad="$(printf 'architecture-beta\n  service a(server)[應用伺服器]\n')"
out="$(printf '%s' "$bad" | bash "$V" - 2>&1)"; rc=$?
expect "unquoted CJK arch -> FAIL" "FAIL" "$out"
expect "unquoted CJK arch -> exit 1" "^1$" "$rc"

# 3) quoted pie title -> WARN (literal quotes)
warn="$(printf 'pie title "市場佔有率"\n  "甲" : 60\n  "乙" : 40\n')"
out="$(printf '%s' "$warn" | bash "$V" - 2>&1)"
expect "quoted pie title -> WARN" "WARN" "$out"

echo "--- $pass passed, $fail failed"
[ "$fail" -eq 0 ]
