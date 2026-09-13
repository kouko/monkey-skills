#!/bin/bash
# Merge per-chapter mp3s into a single .m4b audiobook with chapter bookmarks.
#
# Usage: build_m4b.sh <mp3_dir> <out.m4b> [title] [author]
#
# Chapter titles come from the filenames: "06-04-The Deal.mp3" → "04 The Deal"
# (leading play-order prefix stripped). Requires ffmpeg + ffprobe.
#
# ffmpeg's concat demuxer can fail on a bad list entry and still exit 0, so
# the output duration is checked against the sum of the inputs — a silently
# dropped chapter fails the build instead of shipping a corrupt audiobook.
set -euo pipefail
SRC="${1:?usage: build_m4b.sh <mp3_dir> <out.m4b> [title] [author]}"
OUT="${2:?usage: build_m4b.sh <mp3_dir> <out.m4b> [title] [author]}"
TITLE="${3:-$(basename "$OUT" .m4b)}"
AUTHOR="${4:-}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Tools installed by install_deps.sh land in $TSUNDOKU_ROOT/bin (static
# ffmpeg/ffprobe) and ~/.local/bin (uv/pipx console scripts); make them
# visible even when the user's shell setup doesn't include those dirs
TSUNDOKU_ROOT="${TSUNDOKU_ROOT:-$HOME/.tsundoku}"
PATH="$TSUNDOKU_ROOT/bin:$HOME/.local/bin:$PATH"

for tool in ffmpeg ffprobe; do
  command -v "$tool" >/dev/null || {
    echo "$tool not found — run $(dirname "$0")/install_deps.sh (or: brew install ffmpeg)"
    exit 1
  }
done
[ -d "$SRC" ] || { echo "mp3 folder not found: $SRC"; exit 1; }
# concat list entries resolve relative to the list file's directory, not CWD
SRC="$(cd "$SRC" && pwd)"

# One source of truth for chapter order: Python emits both the concat list
# (apostrophes escaped for the concat demuxer) and the FFMETADATA chapters.
python3 - "$SRC" "$TMP/list.txt" "$TMP/chapters.txt" "$TMP/expected_ms" "$TITLE" "$AUTHOR" <<'EOF'
import os, re, subprocess, sys
src, list_path, meta_path, dur_path, title, author = sys.argv[1:7]

def order(f):  # numeric play-order prefix first, so 99- sorts before 100-
    m = re.match(r'(\d+)', f)
    return (int(m.group(1)) if m else float('inf'), f)

def esc_meta(s):  # FFMETADATA special characters
    return re.sub(r'([=;#\\\n])', r'\\\1', s)

files = sorted((f for f in os.listdir(src) if f.endswith('.mp3')), key=order)
if not files:
    sys.exit(f'no mp3 files in {src}')
with open(list_path, 'w', encoding='utf-8') as lf:
    for f in files:
        p = os.path.join(src, f).replace("'", "'\\''")
        lf.write(f"file '{p}'\n")
lines = [";FFMETADATA1", f"title={esc_meta(title)}", f"album={esc_meta(title)}"]
if author:
    lines.append(f"artist={esc_meta(author)}")
t = 0
for f in files:
    probed = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", os.path.join(src, f)],
        capture_output=True, text=True).stdout.strip()
    if not probed:
        sys.exit(f"ffprobe could not read a duration from {f} — corrupt mp3? "
                 f"delete it and re-run batch_tts.sh")
    ms = int(float(probed) * 1000)
    chap = re.sub(r'^\d+-', '', f[:-4])   # strip play-order prefix
    lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={t}", f"END={t+ms}",
              f"title={esc_meta(chap)}"]
    t += ms
open(meta_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
open(dur_path, "w").write(f"{t} {len(files)}")
print(f"chapters: {len(files)}, total {t/1000/3600:.2f} hr")
EOF

ffmpeg -y -f concat -safe 0 -i "$TMP/list.txt" -i "$TMP/chapters.txt" \
  -map_metadata 1 -map_chapters 1 \
  -c:a aac -b:a 64k -movflags +faststart \
  "$OUT"

# Don't trust ffmpeg's exit code: verify muxed duration vs sum of inputs
actual_s="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
# shellcheck disable=SC2046
python3 - $(cat "$TMP/expected_ms") "$actual_s" <<'EOF' || { rm -f "$OUT"; exit 1; }
import sys
expected, nfiles = int(sys.argv[1]), int(sys.argv[2])
actual = float(sys.argv[3]) * 1000
tol = 100 * nfiles + 500   # AAC priming skews ~tens of ms per input file
if actual + tol < expected:
    sys.exit(f"output is {(expected-actual)/1000:.1f}s shorter than the sum of "
             f"the inputs — a chapter was dropped; build aborted")
EOF

echo "=== done ==="
ls -lh "$OUT"
