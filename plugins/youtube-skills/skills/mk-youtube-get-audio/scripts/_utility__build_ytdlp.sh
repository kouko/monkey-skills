#!/bin/bash
# _build_ytdlp.sh - Build yt-dlp standalone binary (platform-specific, smaller)
#
# This script:
#   1. Creates a temporary virtual environment
#   2. Installs yt-dlp and PyInstaller
#   3. Builds platform-specific standalone executable (~18MB vs 35MB universal)
#   4. Copies binary to bin/
#   5. Cleans up build environment
#
# Prerequisites:
#   - Python 3.8+ with pip
#   - Build tools (Xcode CLT on macOS, build-essential on Linux, VS Build Tools on Windows)
#
# Usage:
#   ./scripts/_build_ytdlp.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/../bin"

# Portable temp directory handling
get_base_tmp() {
    if [ -n "$TMPDIR" ]; then
        echo "$TMPDIR"
    elif [ -n "$TEMP" ]; then
        echo "$TEMP"
    elif [ -n "$TMP" ]; then
        echo "$TMP"
    else
        echo "/tmp"
    fi
}

MONKEY_KNOWLEDGE_TMP="$(get_base_tmp)/monkey_knowledge"
BUILD_DIR="$MONKEY_KNOWLEDGE_TMP/build/yt-dlp-$$"

# Platform suffix for binary naming
get_platform_suffix() {
    local os arch
    os="$(uname -s)"
    arch="$(uname -m)"

    # Normalize OS names
    case "$os" in
        Darwin)               os="darwin" ;;
        Linux)                os="linux" ;;
        MINGW*|CYGWIN*|MSYS*) os="windows" ;;
        *)                    os="$(echo "$os" | tr '[:upper:]' '[:lower:]')" ;;
    esac

    # Normalize arch names
    case "$arch" in
        x86_64)        arch="amd64" ;;
        arm64|aarch64) arch="arm64" ;;
        i686|i386)     arch="386" ;;
    esac

    echo "${os}-${arch}"
}

PLATFORM_SUFFIX="$(get_platform_suffix)"

# Check if running on macOS (for --target-arch support)
is_macos() {
    [ "$(uname -s)" = "Darwin" ]
}

# Check prerequisites
check_prerequisites() {
    # Check for Python 3
    if ! command -v python3 &>/dev/null; then
        echo "ERROR: Python 3 required" >&2
        echo "Install with: brew install python3" >&2
        exit 1
    fi

    # Check Python version (need 3.8+)
    local py_version
    py_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local py_major py_minor
    py_major=$(echo "$py_version" | cut -d. -f1)
    py_minor=$(echo "$py_version" | cut -d. -f2)

    if [ "$py_major" -lt 3 ] || { [ "$py_major" -eq 3 ] && [ "$py_minor" -lt 8 ]; }; then
        echo "ERROR: Python 3.8+ required (found $py_version)" >&2
        exit 1
    fi

    echo "[INFO] Python version: $py_version" >&2
}

build_ytdlp() {
    echo "[INFO] Creating build directory..." >&2
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"

    echo "[INFO] Creating virtual environment..." >&2
    python3 -m venv venv
    source venv/bin/activate

    echo "[INFO] Installing yt-dlp and PyInstaller..." >&2
    pip install --upgrade pip >&2
    pip install yt-dlp pyinstaller >&2

    # Get yt-dlp version
    local ytdlp_version
    ytdlp_version=$(pip show yt-dlp | grep "^Version:" | cut -d' ' -f2)
    echo "[INFO] yt-dlp version: $ytdlp_version" >&2

    # Get yt-dlp entry point
    local ytdlp_main
    ytdlp_main=$(python3 -c "import yt_dlp; print(yt_dlp.__path__[0])")/__main__.py

    echo "[INFO] Building standalone binary for ${PLATFORM_SUFFIX}..." >&2
    local output_name="yt-dlp-${PLATFORM_SUFFIX}"

    # PyInstaller options:
    # --onefile: Single executable
    # --strip: Strip debug symbols (not available on Windows)
    # --target-arch: Build for specific architecture (macOS only)
    # --noconfirm: Overwrite without asking
    # --clean: Clean cache before building
    local pyinstaller_args=(
        --onefile
        --noconfirm
        --clean
        --name "$output_name"
    )

    # --strip is not available on Windows
    case "$(uname -s)" in
        MINGW*|CYGWIN*|MSYS*)
            # Skip --strip on Windows
            ;;
        *)
            pyinstaller_args+=(--strip)
            ;;
    esac

    # --target-arch is macOS only
    if is_macos; then
        pyinstaller_args+=(--target-arch "$(uname -m)")
    fi

    pyinstaller "${pyinstaller_args[@]}" "$ytdlp_main" >&2

    echo "[INFO] Installing binary..." >&2
    mkdir -p "$BIN_DIR"
    cp "dist/$output_name" "$BIN_DIR/$output_name"
    chmod +x "$BIN_DIR/$output_name"

    # Deactivate virtual environment
    deactivate

    echo "[INFO] Cleaning up..." >&2
    cd /
    rm -rf "$BUILD_DIR"

    # Get binary size
    local size
    size=$(du -h "$BIN_DIR/$output_name" | cut -f1)

    echo "[INFO] yt-dlp installed: $BIN_DIR/$output_name" >&2
    echo "[INFO] Binary size: $size (${PLATFORM_SUFFIX})" >&2
    echo "[INFO] Version: $ytdlp_version" >&2
}

check_prerequisites
build_ytdlp

echo "[SUCCESS] Build complete!" >&2
"$BIN_DIR/yt-dlp-${PLATFORM_SUFFIX}" --version
