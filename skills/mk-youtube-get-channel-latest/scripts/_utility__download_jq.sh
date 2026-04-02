#!/bin/bash
# _download_jq.sh - Download jq binary
#
# Downloads platform-specific jq binary from GitHub releases.
# Supports macOS (x86_64/arm64), Linux (x86_64/aarch64), and Windows.
#
# Usage:
#   ./scripts/_download_jq.sh
#
# Output:
#   Downloads jq to bin/ directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/../bin"

# jq 1.7.1 release URL
JQ_VERSION="1.7.1"
JQ_RELEASE_URL="https://github.com/jqlang/jq/releases/download/jq-$JQ_VERSION"

# Detect platform and get download URL
get_download_info() {
    local os arch binary_name download_url

    os="$(uname -s)"
    arch="$(uname -m)"

    case "$os" in
        Darwin)
            case "$arch" in
                x86_64)
                    binary_name="jq-macos-amd64"
                    ;;
                arm64)
                    binary_name="jq-macos-arm64"
                    ;;
                *)
                    echo "ERROR: Unsupported macOS architecture: $arch" >&2
                    exit 1
                    ;;
            esac
            ;;
        Linux)
            case "$arch" in
                x86_64)
                    binary_name="jq-linux-amd64"
                    ;;
                aarch64|arm64)
                    binary_name="jq-linux-arm64"
                    ;;
                *)
                    echo "ERROR: Unsupported Linux architecture: $arch" >&2
                    exit 1
                    ;;
            esac
            ;;
        MINGW*|CYGWIN*|MSYS*)
            binary_name="jq-win64.exe"
            ;;
        *)
            echo "ERROR: Unsupported platform: $os" >&2
            exit 1
            ;;
    esac

    download_url="$JQ_RELEASE_URL/$binary_name"
    echo "$binary_name $download_url"
}

download_jq() {
    local info binary_name download_url binary_path

    info=$(get_download_info)
    binary_name=$(echo "$info" | cut -d' ' -f1)
    download_url=$(echo "$info" | cut -d' ' -f2)
    binary_path="$BIN_DIR/$binary_name"

    # Check if already exists
    if [ -x "$binary_path" ]; then
        echo "[INFO] jq already exists: $binary_path" >&2
        echo "[INFO] Version: $("$binary_path" --version 2>&1 || true)" >&2
        return 0
    fi

    echo "[INFO] Downloading jq $JQ_VERSION..." >&2
    echo "[INFO] Platform: $(uname -s)/$(uname -m)" >&2
    echo "[INFO] URL: $download_url" >&2

    mkdir -p "$BIN_DIR"

    if command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$binary_path" "$download_url"
    elif command -v wget &> /dev/null; then
        wget --show-progress -O "$binary_path" "$download_url"
    else
        echo "ERROR: curl or wget required to download jq" >&2
        exit 1
    fi

    chmod +x "$binary_path"

    echo "[SUCCESS] jq installed: $binary_path" >&2
    echo "[INFO] Version: $("$binary_path" --version 2>&1 || true)" >&2
}

download_jq
