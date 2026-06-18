#!/usr/bin/env bash
# validate.sh — render Mermaid through the real parser and report what the
# static "Quality Checklist" in SKILL.md cannot: syntax errors (mermaid-cli
# does NOT signal these via exit code — it writes an error SVG and exits 0)
# and likely literal-quote mistakes (quoting a free-form title/label).
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
      /^[[:space:]]*```mermaid[[:space:]]*$/ { inblk=1; n++; fn=sprintf("%s/%03d.mmd", dir, n); next }
      /^[[:space:]]*```[[:space:]]*$/        { inblk=0; next }
      inblk                                  { print > fn }
    ' "$src"
    ;;
  -) cat > "$work/001.mmd" ;;
  *) cat "$src" > "$work/001.mmd" ;;
esac

shopt -s nullglob
blocks=( "$work"/*.mmd )
[ ${#blocks[@]} -gt 0 ] || { echo "no mermaid diagrams found in: $src"; exit 0; }

fail=0
for f in "${blocks[@]}"; do
  name="$(basename "$f" .mmd)"
  svg="$f.svg"
  npx -y "@mermaid-js/mermaid-cli@$MERMAID_VER" -i "$f" -o "$svg" >/dev/null 2>&1 || true

  if [ ! -s "$svg" ] || grep -q "Syntax error" "$svg" 2>/dev/null; then
    why="$(grep -m1 -oE '(Lexical|Syntax|Parse) error[^<]*' "$svg" 2>/dev/null || true)"
    echo "FAIL  $name  ${why:-render produced no output}"
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
