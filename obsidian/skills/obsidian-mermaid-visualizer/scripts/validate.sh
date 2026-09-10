#!/usr/bin/env bash
# validate.sh — render Mermaid through the real parser and report what the
# static "Quality Checklist" in SKILL.md cannot: syntax errors and likely
# literal-quote mistakes (quoting a free-form title/label).
#
# On the pinned mermaid-cli (11.4.2) and on 11.16.0, a malformed diagram exits
# non-zero and writes no SVG — probed 2026-09-11. An earlier comment here
# claimed the opposite (error SVG, exit 0) and the script discarded the exit
# code because of it. Both signals are now checked: exit code first, artifact
# inspection as a fallback in case a future build reverts to the error-SVG
# behaviour.
#
# Usage:
#   scripts/validate.sh path/to/note.md      # checks every ```mermaid block
#   scripts/validate.sh diagram.mmd          # a single diagram file
#   cat diagram.mmd | scripts/validate.sh -  # stdin
#
# Exit: 0 = all blocks parsed, 1 = at least one FAIL, 2 = bad usage.
#
# CAVEAT: mermaid-cli is MORE lenient than Obsidian's bundled Mermaid. A PASS
# means "parses in mermaid-cli@$MERMAID_VER"; it does NOT guarantee the diagram
# renders in your Obsidian. A FAIL is a real bug. Pinned near Obsidian's bundle
# to catch as much as the static checklist misses.
set -euo pipefail

MERMAID_VER="11.4.2"   # ~ Obsidian's bundled Mermaid; newer cli is too lenient

[ $# -eq 1 ] || { grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
src="$1"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# Gather diagrams into $work/NNN.mmd
case "$src" in
  *.md)
    awk -v dir="$work" '
      /^[[:space:]]*```mermaid([[:space:]].*)?$/ { inblk=1; n++; fn=sprintf("%s/%03d.mmd", dir, n); printf "" > fn; next }
      /^[[:space:]]*```[[:space:]]*$/            { inblk=0; next }
      inblk                                      { print > fn }
    ' "$src"
    ;;
  -) cat > "$work/001.mmd" ;;
  *) cat "$src" > "$work/001.mmd" ;;
esac

shopt -s nullglob
blocks=( "$work"/*.mmd )

# Fail-closed on extraction misses: if the source declares mermaid fences we
# did not extract, a green exit would be vacuous.
opened=0
case "$src" in
  *.md) opened=$(grep -cE '^[[:space:]]*```mermaid' "$src" 2>/dev/null || true) ;;
esac
if [ "${opened:-0}" -gt "${#blocks[@]}" ]; then
  echo "FAIL  extraction  $src declares $opened mermaid fence(s) but only ${#blocks[@]} were extracted"
  exit 1
fi
[ ${#blocks[@]} -gt 0 ] || { echo "no mermaid diagrams found in: $src"; exit 0; }

fail=0
for f in "${blocks[@]}"; do
  name="$(basename "$f" .mmd)"
  svg="$f.svg"
  # The renderer's exit code is the primary signal: on mermaid-cli 11.4.2 and
  # 11.16.0 a malformed diagram exits non-zero and writes no SVG (probed
  # 2026-09-11). The artifact checks below stay as a second line of defence in
  # case a future version writes an error image and exits 0 instead.
  rc=0
  npx -y "@mermaid-js/mermaid-cli@$MERMAID_VER" -i "$f" -o "$svg" >"$f.log" 2>&1 || rc=$?

  svg_err="$(grep -m1 -oE '(Lexical|Syntax|Parse) error[^<]*' "$svg" 2>/dev/null || true)"
  if [ "$rc" -ne 0 ] || [ ! -s "$svg" ] || [ -n "$svg_err" ]; then
    why="$svg_err"
    [ -n "$why" ] || why="$(grep -m1 -oE '(Lexical|Syntax|Parse) error.*' "$f.log" 2>/dev/null || true)"
    [ -n "$why" ] || why="renderer exited $rc with no usable output"
    echo "FAIL  $name  $why"
    fail=1
    continue
  fi

  # Heuristic: a literal " inside a rendered <text> node usually means a
  # free-form title/label was wrongly quoted (pie/quadrant/gantt title bug).
  if grep -qE '<text[^>]*>[^<]*"[^<]*</text>' "$svg" 2>/dev/null; then
    echo "WARN  $name  rendered text contains a literal \" — a title/label may be wrongly quoted"
  else
    echo "PASS  $name"
  fi
done

echo "---"
echo "mermaid-cli@$MERMAID_VER is more lenient than Obsidian: PASS != guaranteed Obsidian render; FAIL is a real bug."
exit $fail
