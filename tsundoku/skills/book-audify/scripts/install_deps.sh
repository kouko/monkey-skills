#!/usr/bin/env bash
# install_deps.sh — ensure book-audify's two external legs are available:
# edge-tts (CLI) and ffmpeg/ffprobe.
#
# Mirrors install_pandoc.sh's three-stage shape for ffmpeg/ffprobe:
#   1. already on PATH? done.
#   2. brew install ffmpeg (if Homebrew is available)
#   3. Download the publisher's latest release static builds into
#      $TSUNDOKU_ROOT/bin (SHA256-checked against the sidecar published
#      alongside — an integrity check, not a supply-chain pin)
#
# edge-tts has no brew formula and is used purely as a CLI here, so it is
# installed as an isolated console-script tool — `uv tool install` or
# `pipx install`, never bare pip into whatever environment is active.
#
# If installed via #3, binaries land at $TSUNDOKU_ROOT/bin/{ffmpeg,ffprobe}
# and are printed at the end so callers can capture them via
# `eval "$(install_deps.sh)"`.
#
# License note: the static builds from ffmpeg.martin-riedl.de are GPLv3.
# Downloading them onto the user's machine at install time keeps the source
# obligation with the build publisher — do NOT "optimize" this into a binary
# vendored in the repo or a release artifact; that would make this project a
# distributor owing corresponding source.
#
# Usage:
#   install_deps.sh [--force-standalone]
#
# Options:
#   --force-standalone    skip brew, download static ffmpeg/ffprobe builds
#
# Exit codes:
#   0  all dependencies available (paths printed)
#   1  install failed
#   2  argument error
#   3  unsupported platform

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATHS_SCRIPT="$SCRIPT_DIR/tsundoku_paths.sh"
[[ -f "$PATHS_SCRIPT" ]] && source "$PATHS_SCRIPT" || {
    TSUNDOKU_ROOT="${TSUNDOKU_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/tsundoku}"
}

# See tools already installed by a previous run even when the user's shell
# setup doesn't include these dirs (uv/pipx put console scripts in
# ~/.local/bin; stage 3 installs into $TSUNDOKU_ROOT/bin)
PATH="$TSUNDOKU_ROOT/bin:$HOME/.local/bin:$PATH"

FORCE_STANDALONE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force-standalone) FORCE_STANDALONE=true; shift ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "install_deps: unknown arg: $1" >&2; exit 2 ;;
    esac
done

# ---------------------------------------------------------------- edge-tts
if command -v edge-tts >/dev/null 2>&1; then
    echo "[edge-tts] already installed: $(command -v edge-tts)" >&2
elif command -v uv >/dev/null 2>&1; then
    echo "[edge-tts] installing via uv tool" >&2
    uv tool install edge-tts >&2
elif command -v pipx >/dev/null 2>&1; then
    echo "[edge-tts] installing via pipx" >&2
    pipx install edge-tts >&2
else
    echo "[edge-tts] neither uv nor pipx found — install one, then re-run:" >&2
    echo "           brew install uv     (then: uv tool install edge-tts)" >&2
    echo "           brew install pipx   (then: pipx install edge-tts)" >&2
    exit 1
fi
command -v edge-tts >/dev/null 2>&1 || {
    echo "[edge-tts] installed but not on PATH — run 'uv tool update-shell' or 'pipx ensurepath', then reopen the shell" >&2
    exit 1
}
echo "EDGE_TTS=$(command -v edge-tts)"

# ------------------------------------------------------------------ ffmpeg
# 1. Already installed?
if [[ "$FORCE_STANDALONE" != true ]] \
   && command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
    echo "[ffmpeg] already installed: $(command -v ffmpeg)" >&2
    echo "FFMPEG=$(command -v ffmpeg)"
    echo "FFPROBE=$(command -v ffprobe)"
    exit 0
fi

# 2. Try brew (mac/linux)
if [[ "$FORCE_STANDALONE" != true ]] && command -v brew >/dev/null 2>&1; then
    echo "[ffmpeg] installing via Homebrew" >&2
    if brew install ffmpeg >&2; then
        echo "[ffmpeg] installed via brew: $(command -v ffmpeg)" >&2
        echo "FFMPEG=$(command -v ffmpeg)"
        echo "FFPROBE=$(command -v ffprobe)"
        exit 0
    fi
    echo "[ffmpeg] brew install failed; falling back to static builds" >&2
fi

# 3. Static builds (ffmpeg.martin-riedl.de — GPLv3, SHA256 alongside, macOS
# builds are arm64-native, Developer ID-signed and notarized)
echo "[ffmpeg] downloading static builds" >&2

uname_s=$(uname -s)
uname_m=$(uname -m)
case "$uname_s" in
    Darwin)
        os="macos"
        case "$uname_m" in
            arm64) arch="arm64" ;;
            *) echo "[ffmpeg] no static build for macOS $uname_m — use brew" >&2; exit 3 ;;
        esac
        ;;
    Linux)
        os="linux"
        case "$uname_m" in
            x86_64) arch="amd64" ;;
            aarch64|arm64) arch="arm64" ;;
            *) echo "[ffmpeg] unsupported Linux arch: $uname_m" >&2; exit 3 ;;
        esac
        ;;
    *)
        echo "[ffmpeg] unsupported OS: $uname_s — install ffmpeg manually" >&2
        exit 3
        ;;
esac

dl_dir="$TSUNDOKU_ROOT/bin"
mkdir -p "$dl_dir"

sha256_of() {
    if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
    else sha256sum "$1" | awk '{print $1}'; fi
}

for tool in ffmpeg ffprobe; do
    redirect_url="https://ffmpeg.martin-riedl.de/redirect/latest/$os/$arch/release/$tool.zip"
    tmp_zip="$dl_dir/$tool.zip.partial"
    echo "[ffmpeg] $redirect_url" >&2
    final_url="$(curl --fail --location --silent --show-error \
        --output "$tmp_zip" --write-out '%{url_effective}' "$redirect_url")" || {
        echo "[ffmpeg] download failed: $redirect_url" >&2
        rm -f "$tmp_zip"
        exit 1
    }
    # Sanity-check size — a tiny file usually means we caught an error page
    size_bytes=$(stat -f%z "$tmp_zip" 2>/dev/null || stat -c%s "$tmp_zip" 2>/dev/null || echo 0)
    if [[ "$size_bytes" -lt 1000000 ]]; then
        echo "[ffmpeg] downloaded $tool.zip is suspiciously small ($size_bytes bytes); aborting" >&2
        rm -f "$tmp_zip"
        exit 1
    fi
    # Verify against the published SHA256 sidecar
    expected="$(curl --fail --location --silent "$final_url.sha256" | awk '{print $1}')"
    actual="$(sha256_of "$tmp_zip")"
    if [[ -z "$expected" || "$expected" != "$actual" ]]; then
        echo "[ffmpeg] SHA256 mismatch for $tool.zip (expected ${expected:-<none>}, got $actual); aborting" >&2
        rm -f "$tmp_zip"
        exit 1
    fi
    (cd "$dl_dir" && unzip -oq "$tmp_zip" "$tool")
    rm -f "$tmp_zip"
    chmod +x "$dl_dir/$tool"
    # curl doesn't set com.apple.quarantine, but a stray attribute is fatal on
    # arm64; clearing it costs nothing. Never strip/mutate the binary — that
    # invalidates the notarized signature (silent "Killed: 9").
    xattr -d com.apple.quarantine "$dl_dir/$tool" 2>/dev/null || true
    echo "[ffmpeg] installed: $dl_dir/$tool" >&2
done

"$dl_dir/ffmpeg" -version 2>/dev/null | head -n 1 >&2 || true
echo "FFMPEG=$dl_dir/ffmpeg"
echo "FFPROBE=$dl_dir/ffprobe"
