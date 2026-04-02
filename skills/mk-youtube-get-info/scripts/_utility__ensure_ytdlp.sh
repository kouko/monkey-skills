#!/bin/bash
# _utility__ensure_ytdlp.sh - Ensure yt-dlp is available
#
# Checks for yt-dlp in:
#   1. System PATH
#   2. bin/ directory (universal or platform-specific binary)
#   3. Auto-downloads if not found
#
# Usage:
#   source "$(dirname "$0")/_utility__ensure_ytdlp.sh"
#   if [ -n "$YTDLP_ERROR_JSON" ]; then
#       echo "$YTDLP_ERROR_JSON"
#       exit 1
#   fi
#   "$YT_DLP" --version
#
# Exit codes:
#   0 - yt-dlp found (YT_DLP variable is set)
#   1 - yt-dlp not found and download failed (YTDLP_ERROR_JSON is set)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/../bin"

# Initialize
YT_DLP=""
YTDLP_ERROR_JSON=""
_YTDLP_EXIT_CODE=0

# --- Platform Detection ---

# Get platform-specific binary name (local build)
get_ytdlp_platform_binary_name() {
    local os arch
    os="$(uname -s)"
    arch="$(uname -m)"

    # Normalize OS names
    case "$os" in
        Darwin)               os="darwin" ;;
        Linux)                os="linux" ;;
        MINGW*|CYGWIN*|MSYS*) os="windows" ;;
        *)                    echo ""; return 1 ;;
    esac

    # Normalize arch names
    case "$arch" in
        x86_64)        arch="amd64" ;;
        arm64|aarch64) arch="arm64" ;;
        i686|i386)     arch="386" ;;
        *)             echo ""; return 1 ;;
    esac

    echo "yt-dlp-${os}-${arch}"
}

# Get universal binary name (official release)
get_ytdlp_binary_name() {
    local os
    os="$(uname -s)"

    case "$os" in
        Darwin)
            echo "yt-dlp-macos"
            ;;
        Linux)
            echo "yt-dlp-linux"
            ;;
        MINGW*|CYGWIN*|MSYS*)
            echo "yt-dlp.exe"
            ;;
        *)
            echo ""
            ;;
    esac
}

find_ytdlp() {
    # 1. Check system yt-dlp
    if command -v yt-dlp &> /dev/null; then
        echo "$(command -v yt-dlp)"
        return 0
    fi

    # 1b. Check well-known install paths (PATH may be incomplete in plugin environments)
    local known_path
    for known_path in /opt/homebrew/bin/yt-dlp /usr/local/bin/yt-dlp; do
        if [ -x "$known_path" ]; then
            echo "$known_path"
            return 0
        fi
    done

    # 2. Check bin/ directory - universal binary (official release, preferred)
    local binary_name
    binary_name=$(get_ytdlp_binary_name)
    if [ -n "$binary_name" ] && [ -x "$BIN_DIR/$binary_name" ]; then
        echo "$BIN_DIR/$binary_name"
        return 0
    fi

    # 3. Check bin/ directory - platform-specific binary (local build fallback)
    local platform_binary_name
    platform_binary_name=$(get_ytdlp_platform_binary_name)
    if [ -n "$platform_binary_name" ] && [ -x "$BIN_DIR/$platform_binary_name" ]; then
        echo "$BIN_DIR/$platform_binary_name"
        return 0
    fi

    # Not found
    return 1
}

# Try to find yt-dlp
if YT_DLP=$(find_ytdlp); then
    _YTDLP_EXIT_CODE=0
else
    # yt-dlp not found - try auto-download
    echo "[INFO] yt-dlp not found, downloading..." >&2
    if "$SCRIPT_DIR/_utility__download_ytdlp.sh" >&2; then
        # Re-check after download
        if YT_DLP=$(find_ytdlp); then
            _YTDLP_EXIT_CODE=0
        else
            YTDLP_ERROR_JSON=$(cat <<EOF
{
    "error_code": "YTDLP_NOT_FOUND",
    "message": "yt-dlp download succeeded but binary not found. Check platform support.",
    "download_command": "$SCRIPT_DIR/_utility__download_ytdlp.sh",
    "build_command": "$SCRIPT_DIR/_utility__build_ytdlp.sh"
}
EOF
)
            _YTDLP_EXIT_CODE=1
        fi
    else
        YTDLP_ERROR_JSON=$(cat <<EOF
{
    "error_code": "YTDLP_DOWNLOAD_FAILED",
    "message": "yt-dlp not found and download failed. Please install manually.",
    "download_command": "$SCRIPT_DIR/_utility__download_ytdlp.sh",
    "build_command": "$SCRIPT_DIR/_utility__build_ytdlp.sh"
}
EOF
)
        _YTDLP_EXIT_CODE=1
    fi
fi

# Export results
export YT_DLP
export YTDLP_ERROR_JSON

# Return/exit with appropriate code
if [ $_YTDLP_EXIT_CODE -ne 0 ]; then
    return $_YTDLP_EXIT_CODE 2>/dev/null || exit $_YTDLP_EXIT_CODE
fi
