#!/bin/bash
# _utility__ensure_ffmpeg.sh - Ensure ffmpeg is available
#
# Checks for ffmpeg in:
#   1. System PATH
#   1b. Well-known install paths (for plugin environments with incomplete PATH)
#   2. bin/ directory (platform-specific binary)
#   3. Auto-downloads if not found
#
# Usage:
#   source "$(dirname "$0")/_utility__ensure_ffmpeg.sh"
#   if [ -n "$FFMPEG_ERROR_JSON" ]; then
#       echo "$FFMPEG_ERROR_JSON"
#       exit 1
#   fi
#   "$FFMPEG" -version
#
# Exports:
#   FFMPEG           - Full path to ffmpeg binary
#   FFMPEG_DIR       - Directory containing ffmpeg (for --ffmpeg-location)
#   FFMPEG_ERROR_JSON - Error details if ffmpeg not found
#
# Exit codes:
#   0 - ffmpeg found (FFMPEG variable is set)
#   1 - ffmpeg not found and download failed (FFMPEG_ERROR_JSON is set)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/../bin"

# Initialize
FFMPEG=""
FFMPEG_DIR=""
FFMPEG_ERROR_JSON=""
_FFMPEG_EXIT_CODE=0

# --- Platform Detection ---

get_ffmpeg_binary_name() {
    local os arch
    os="$(uname -s | tr '[:upper:]' '[:lower:]')"
    arch="$(uname -m)"

    # Normalize arch names
    case "$arch" in
        x86_64)        arch="amd64" ;;
        arm64|aarch64) arch="arm64" ;;
        *)             echo ""; return 1 ;;
    esac

    echo "ffmpeg-${os}-${arch}"
}

# --- Main Logic ---

find_ffmpeg() {
    # 1. Prefer system-installed ffmpeg
    if command -v ffmpeg &> /dev/null; then
        command -v ffmpeg
        return 0
    fi

    # 1b. Check well-known install paths (PATH may be incomplete in plugin environments)
    local known_path
    for known_path in /opt/homebrew/bin/ffmpeg /usr/local/bin/ffmpeg; do
        if [ -x "$known_path" ]; then
            echo "$known_path"
            return 0
        fi
    done

    # 2. Check pre-built binary in bin/ (with platform suffix)
    local binary_name="$(get_ffmpeg_binary_name)"
    if [ -n "$binary_name" ]; then
        local binary_path="$BIN_DIR/$binary_name"
        if [ -x "$binary_path" ]; then
            echo "$binary_path"
            return 0
        fi
    fi

    # 3. Not available
    return 1
}

# Try to find ffmpeg
if FFMPEG=$(find_ffmpeg); then
    _FFMPEG_EXIT_CODE=0
else
    # ffmpeg not found - try auto-download
    echo "[INFO] ffmpeg not found, downloading..." >&2
    if "$SCRIPT_DIR/_utility__download_ffmpeg.sh" >&2; then
        # Re-check after download
        if FFMPEG=$(find_ffmpeg); then
            _FFMPEG_EXIT_CODE=0
        else
            FFMPEG_ERROR_JSON=$(cat <<EOF
{
    "error_code": "FFMPEG_NOT_FOUND",
    "message": "ffmpeg download succeeded but binary not found. Check platform support.",
    "download_command": "$SCRIPT_DIR/_utility__download_ffmpeg.sh",
    "build_command": "$SCRIPT_DIR/_utility__build_ffmpeg.sh"
}
EOF
)
            _FFMPEG_EXIT_CODE=1
        fi
    else
        FFMPEG_ERROR_JSON=$(cat <<EOF
{
    "error_code": "FFMPEG_DOWNLOAD_FAILED",
    "message": "ffmpeg not found and download failed. Please install manually.",
    "download_command": "$SCRIPT_DIR/_utility__download_ffmpeg.sh",
    "build_command": "$SCRIPT_DIR/_utility__build_ffmpeg.sh"
}
EOF
)
        _FFMPEG_EXIT_CODE=1
    fi
fi

# Derive FFMPEG_DIR for --ffmpeg-location usage
if [ -n "$FFMPEG" ]; then
    FFMPEG_DIR="$(dirname "$FFMPEG")"
fi

# Export results
export FFMPEG
export FFMPEG_DIR
export FFMPEG_ERROR_JSON

# Return/exit with appropriate code
if [ $_FFMPEG_EXIT_CODE -ne 0 ]; then
    return $_FFMPEG_EXIT_CODE 2>/dev/null || exit $_FFMPEG_EXIT_CODE
fi
