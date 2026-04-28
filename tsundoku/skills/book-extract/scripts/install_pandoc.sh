#!/usr/bin/env bash
# install_pandoc.sh — ensure pandoc is available.
#
# Tries in order:
#   1. `pandoc --version` — already on PATH? done.
#   2. brew install pandoc (if Homebrew is available)
#   3. Download standalone binary tarball from GitHub releases into TSUNDOKU_ROOT
#
# If installed via #3, the binary is at $TSUNDOKU_ROOT/bin/pandoc and printed at
# the end so callers can capture it via `eval "$(install_pandoc.sh)"`.
#
# Usage:
#   install_pandoc.sh [--force-standalone] [--version VER]
#
# Options:
#   --force-standalone    skip brew, download standalone binary
#   --version VER         pin a specific pandoc version (default: latest)
#
# Exit codes:
#   0  pandoc available (path printed)
#   1  install failed
#   2  argument error
#   3  unsupported platform

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATHS_SCRIPT="$SCRIPT_DIR/tsundoku_paths.sh"
[[ -f "$PATHS_SCRIPT" ]] && source "$PATHS_SCRIPT" || {
    TSUNDOKU_ROOT="${TSUNDOKU_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/tsundoku}"
}

FORCE_STANDALONE=false
VERSION="latest"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force-standalone) FORCE_STANDALONE=true; shift ;;
        --version) VERSION="$2"; shift 2 ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "install_pandoc: unknown arg: $1" >&2; exit 2 ;;
    esac
done

# 1. Already installed?
if [[ "$FORCE_STANDALONE" != true ]] && command -v pandoc >/dev/null 2>&1; then
    pandoc_path="$(command -v pandoc)"
    pandoc_ver="$(pandoc --version | head -n 1)"
    echo "[pandoc] already installed: $pandoc_path ($pandoc_ver)" >&2
    echo "PANDOC=$pandoc_path"
    exit 0
fi

# 2. Try brew (mac/linux)
if [[ "$FORCE_STANDALONE" != true ]] && command -v brew >/dev/null 2>&1; then
    echo "[pandoc] installing via Homebrew" >&2
    if brew install pandoc >&2; then
        pandoc_path="$(command -v pandoc || echo /opt/homebrew/bin/pandoc)"
        echo "[pandoc] installed via brew: $pandoc_path" >&2
        echo "PANDOC=$pandoc_path"
        exit 0
    fi
    echo "[pandoc] brew install failed; falling back to standalone download" >&2
fi

# 3. Standalone binary
echo "[pandoc] downloading standalone binary" >&2

uname_s=$(uname -s)
uname_m=$(uname -m)
case "$uname_s" in
    Darwin)
        platform="macOS"
        ext="zip"
        case "$uname_m" in
            arm64) arch="arm64" ;;
            x86_64) arch="x86_64" ;;
            *) echo "[pandoc] unsupported macOS arch: $uname_m" >&2; exit 3 ;;
        esac
        ;;
    Linux)
        platform="linux"
        ext="tar.gz"
        case "$uname_m" in
            x86_64) arch="amd64" ;;
            aarch64|arm64) arch="arm64" ;;
            *) echo "[pandoc] unsupported Linux arch: $uname_m" >&2; exit 3 ;;
        esac
        ;;
    *)
        echo "[pandoc] unsupported OS: $uname_s — install pandoc manually from" >&2
        echo "         https://github.com/jgm/pandoc/releases/latest" >&2
        exit 3
        ;;
esac

# Resolve version
if [[ "$VERSION" == "latest" ]]; then
    api_url="https://api.github.com/repos/jgm/pandoc/releases/latest"
    tag=$(curl -sL "$api_url" | grep -o '"tag_name": *"[^"]*"' | head -n 1 | sed 's/.*"\([^"]*\)"/\1/')
    if [[ -z "$tag" ]]; then
        echo "[pandoc] failed to resolve latest version from GitHub API" >&2
        exit 1
    fi
    VERSION="$tag"
fi

dl_dir="$TSUNDOKU_ROOT/bin"
mkdir -p "$dl_dir"
fname="pandoc-${VERSION}-${arch}-${platform}.${ext}"
url="https://github.com/jgm/pandoc/releases/download/${VERSION}/${fname}"
tmp="$dl_dir/${fname}.partial"

echo "[pandoc] $url" >&2
if ! curl --fail --location --output "$tmp" "$url"; then
    echo "[pandoc] download failed: $url" >&2
    exit 1
fi

# Extract
extract_dir="$dl_dir/pandoc-${VERSION}"
rm -rf "$extract_dir"
mkdir -p "$extract_dir"
case "$ext" in
    zip) (cd "$extract_dir" && unzip -q "$tmp") ;;
    tar.gz) tar -xzf "$tmp" -C "$extract_dir" ;;
esac
rm -f "$tmp"

# Find the binary inside the extracted tree
pandoc_bin=$(find "$extract_dir" -type f -name pandoc -perm -u+x | head -n 1)
if [[ -z "$pandoc_bin" ]]; then
    echo "[pandoc] could not find pandoc binary in extracted tree" >&2
    exit 1
fi

# Symlink to a stable path
target="$dl_dir/pandoc"
ln -sf "$pandoc_bin" "$target"
echo "[pandoc] installed: $target" >&2
"$target" --version | head -n 1 >&2 || true
echo "PANDOC=$target"
