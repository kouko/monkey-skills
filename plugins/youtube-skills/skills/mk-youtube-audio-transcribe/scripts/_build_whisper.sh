#!/bin/bash
# _build_whisper.sh - Build whisper.cpp with CoreML + Metal (macOS)
#
# This script:
#   1. Clones whisper.cpp repository
#   2. Builds with CoreML and Metal acceleration
#   3. Copies binary to bin/
#   4. Cleans up source code
#
# Usage:
#   ./scripts/_build_whisper.sh

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
BUILD_DIR="$MONKEY_KNOWLEDGE_TMP/build/whisper-cpp-$$"

# Platform suffix for binary naming
get_platform_suffix() {
    local os arch
    os="$(uname -s | tr '[:upper:]' '[:lower:]')"
    arch="$(uname -m)"

    case "$arch" in
        x86_64)        arch="amd64" ;;
        arm64|aarch64) arch="arm64" ;;
    esac

    echo "${os}-${arch}"
}

PLATFORM_SUFFIX="$(get_platform_suffix)"

# Only support macOS
if [ "$(uname -s)" != "Darwin" ]; then
    echo "ERROR: This script is for macOS only" >&2
    exit 1
fi

# Check prerequisites
check_prerequisites() {
    if ! xcode-select -p &>/dev/null; then
        echo "ERROR: Xcode CLI tools required" >&2
        echo "Run: xcode-select --install" >&2
        exit 1
    fi

    if ! command -v cmake &>/dev/null; then
        echo "ERROR: cmake required" >&2
        echo "Run: brew install cmake" >&2
        exit 1
    fi

    if ! command -v git &>/dev/null; then
        echo "ERROR: git required" >&2
        exit 1
    fi
}

build_whisper() {
    echo "[INFO] Cloning whisper.cpp..." >&2
    git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git "$BUILD_DIR"
    cd "$BUILD_DIR"

    echo "[INFO] Building with Metal (static linking)..." >&2
    cmake -B build \
        -DCMAKE_BUILD_TYPE=Release \
        -DGGML_METAL=ON \
        -DBUILD_SHARED_LIBS=OFF

    cmake --build build -j"$(sysctl -n hw.ncpu)"

    echo "[INFO] Installing binary..." >&2
    mkdir -p "$BIN_DIR"
    local output_name="whisper-cli-${PLATFORM_SUFFIX}"
    cp build/bin/whisper-cli "$BIN_DIR/$output_name"
    chmod +x "$BIN_DIR/$output_name"

    echo "[INFO] Cleaning up..." >&2
    cd /
    rm -rf "$BUILD_DIR"

    echo "[INFO] whisper-cli installed: $BIN_DIR/$output_name" >&2
    echo "[INFO] Build options: Metal=ON, Static=ON" >&2
}

check_prerequisites
build_whisper

echo "[SUCCESS] Build complete!" >&2
"$BIN_DIR/whisper-cli-${PLATFORM_SUFFIX}" --version 2>&1 || true
