#!/bin/bash
# _download_ytdlp.sh - Download yt-dlp binary
#
# Downloads platform-specific yt-dlp binary from GitHub releases.
# Supports macOS, Linux, and Windows.
#
# Usage:
#   ./scripts/_download_ytdlp.sh
#
# Output:
#   Downloads yt-dlp to bin/ directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/../bin"

# yt-dlp release URL (latest)
YT_DLP_RELEASE_URL="https://github.com/yt-dlp/yt-dlp/releases/latest/download"

# Detect platform and get download URL
get_download_info() {
    local os binary_name download_url

    os="$(uname -s)"

    case "$os" in
        Darwin)
            binary_name="yt-dlp-macos"
            download_url="$YT_DLP_RELEASE_URL/yt-dlp_macos"
            ;;
        Linux)
            binary_name="yt-dlp-linux"
            download_url="$YT_DLP_RELEASE_URL/yt-dlp_linux"
            ;;
        MINGW*|CYGWIN*|MSYS*)
            binary_name="yt-dlp.exe"
            download_url="$YT_DLP_RELEASE_URL/yt-dlp.exe"
            ;;
        *)
            echo "ERROR: Unsupported platform: $os" >&2
            exit 1
            ;;
    esac

    echo "$binary_name $download_url"
}

download_ytdlp() {
    local info binary_name download_url binary_path

    info=$(get_download_info)
    binary_name=$(echo "$info" | cut -d' ' -f1)
    download_url=$(echo "$info" | cut -d' ' -f2)
    binary_path="$BIN_DIR/$binary_name"

    # Check if already exists
    if [ -x "$binary_path" ]; then
        echo "[INFO] yt-dlp already exists: $binary_path" >&2
        echo "[INFO] Version: $("$binary_path" --version 2>&1 || true)" >&2
        return 0
    fi

    echo "[INFO] Downloading yt-dlp (latest)..." >&2
    echo "[INFO] Platform: $(uname -s)" >&2
    echo "[INFO] URL: $download_url" >&2

    mkdir -p "$BIN_DIR"

    if command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$binary_path" "$download_url"
    elif command -v wget &> /dev/null; then
        wget --show-progress -O "$binary_path" "$download_url"
    else
        echo "ERROR: curl or wget required to download yt-dlp" >&2
        exit 1
    fi

    chmod +x "$binary_path"

    echo "[SUCCESS] yt-dlp installed: $binary_path" >&2
    echo "[INFO] Version: $("$binary_path" --version 2>&1 || true)" >&2
}

download_ytdlp
