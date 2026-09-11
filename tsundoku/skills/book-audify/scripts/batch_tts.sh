#!/bin/bash
# Batch-synthesize TTS-ready chapter .txt files into per-chapter mp3s.
#
# Usage: batch_tts.sh <src_txt_dir> <dst_mp3_dir> [voice] [rate]
#   voice  edge-tts voice name        (default: zh-TW-HsiaoChenNeural)
#          list options: edge-tts --list-voices | grep <lang>
#   rate   base speaking rate offset  (default: +0%)
#          tip: if you listen at 1.5x, generate at -25% so pauses and
#          prosody survive the speed-up
#
# Idempotent: existing non-empty mp3s are skipped, so a killed run can be
# resumed by re-running the same command. Runs validate_tts.py first — a
# dirty source folder refuses to synthesize.
set -uo pipefail
SRC="${1:?usage: batch_tts.sh <src_txt_dir> <dst_mp3_dir> [voice] [rate]}"
DST="${2:?usage: batch_tts.sh <src_txt_dir> <dst_mp3_dir> [voice] [rate]}"
VOICE="${3:-zh-TW-HsiaoChenNeural}"
RATE="${4:-+0%}"

# Tools installed by install_deps.sh land in $TSUNDOKU_ROOT/bin (static
# ffmpeg/ffprobe) and ~/.local/bin (uv/pipx console scripts); make them
# visible even when the user's shell setup doesn't include those dirs
TSUNDOKU_ROOT="${TSUNDOKU_ROOT:-$HOME/.tsundoku}"
PATH="$TSUNDOKU_ROOT/bin:$HOME/.local/bin:$PATH"

command -v edge-tts >/dev/null || {
  echo "edge-tts not found — run $(dirname "$0")/install_deps.sh (or: uv tool install edge-tts / pipx install edge-tts)"
  exit 1
}
[ -d "$SRC" ] || { echo "source folder not found: $SRC"; exit 1; }
python3 "$(dirname "$0")/validate_tts.py" "$SRC" || { echo "not TTS-ready — fix violations first"; exit 1; }
mkdir -p "$DST"

fail=0
consec=0
for f in "$SRC"/*.txt; do
  base="$(basename "$f" .txt)"
  out="$DST/$base.mp3"
  if [ -s "$out" ]; then
    # a header-corrupt mp3 (hard kill early in the write) is caught here via
    # ffprobe; a cleanly truncated one still reports its header duration and
    # slips through — build_m4b.sh's duration gate is the backstop for those
    if ! command -v ffprobe >/dev/null 2>&1 || \
       ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" 2>/dev/null | grep -q '[0-9]'; then
      echo "skip(exists) $base"
      continue
    fi
    echo "redo(truncated) $base"
    rm -f "$out"
  fi
  echo "tts[$VOICE $RATE] $base ..."
  if ! edge-tts --voice "$VOICE" --rate="$RATE" --file "$f" --write-media "$out"; then
    echo "FAIL $base"
    fail=1
    rm -f "$out"
    consec=$((consec+1))
    if [ "$consec" -ge 3 ]; then
      echo "3 consecutive failures — this is not a transient blip. edge-tts talks to a"
      echo "non-public Microsoft endpoint that changes; check your edge-tts is current:"
      echo "  uv tool upgrade edge-tts   (or: pipx upgrade edge-tts)"
      exit 1
    fi
  else
    consec=0
  fi
done

echo "=== summary ==="
ls -lh "$DST" | tail -n +2
[ "$fail" -eq 0 ] && echo "ALL OK" || { echo "SOME FAILED — re-run to retry"; exit 1; }
