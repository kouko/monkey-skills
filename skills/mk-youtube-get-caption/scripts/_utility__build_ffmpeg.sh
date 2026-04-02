#!/bin/bash
# _build_ffmpeg.sh - Build ffmpeg from source (LGPL, minimal)
#
# This script:
#   1. Downloads ffmpeg source code
#   2. Builds with LGPL license (no GPL components)
#   3. Minimal build for audio conversion only
#   4. Copies binary to bin/
#   5. Cleans up source code
#
# Build time: ~10-15 minutes
#
# Usage:
#   ./scripts/_build_ffmpeg.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/../bin"

# FFmpeg version to build
FFMPEG_VERSION="7.1"

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
BUILD_DIR="$MONKEY_KNOWLEDGE_TMP/build/ffmpeg-$$"

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

# Check prerequisites
check_prerequisites() {
    local missing=()

    if ! xcode-select -p &>/dev/null; then
        echo "ERROR: Xcode CLI tools required" >&2
        echo "Run: xcode-select --install" >&2
        exit 1
    fi

    # Check for required tools
    for tool in make curl tar; do
        if ! command -v "$tool" &>/dev/null; then
            missing+=("$tool")
        fi
    done

    # Optional but recommended: nasm/yasm for assembly optimizations
    if ! command -v nasm &>/dev/null && ! command -v yasm &>/dev/null; then
        echo "[WARN] nasm/yasm not found - building without assembly optimizations" >&2
        echo "[HINT] Install with: brew install nasm" >&2
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        echo "ERROR: Missing required tools: ${missing[*]}" >&2
        exit 1
    fi
}

build_ffmpeg() {
    echo "[INFO] Creating build directory..." >&2
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"

    echo "[INFO] Downloading ffmpeg ${FFMPEG_VERSION} source..." >&2
    curl -L -o ffmpeg.tar.xz "https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.xz"

    echo "[INFO] Extracting..." >&2
    tar xf ffmpeg.tar.xz
    cd "ffmpeg-${FFMPEG_VERSION}"

    echo "[INFO] Configuring (LGPL, minimal audio build)..." >&2
    # LGPL build - no --enable-gpl flag
    # Minimal build for audio conversion
    ./configure \
        --prefix="$BUILD_DIR/install" \
        --disable-doc \
        --disable-htmlpages \
        --disable-manpages \
        --disable-podpages \
        --disable-txtpages \
        --disable-network \
        --disable-autodetect \
        --disable-programs \
        --enable-ffmpeg \
        --disable-ffplay \
        --disable-ffprobe \
        --disable-avdevice \
        --disable-swscale \
        --disable-postproc \
        --enable-swresample \
        --disable-encoders \
        --enable-encoder=pcm_s16le \
        --enable-encoder=pcm_s16be \
        --disable-decoders \
        --enable-decoder=aac \
        --enable-decoder=mp3 \
        --enable-decoder=mp3float \
        --enable-decoder=flac \
        --enable-decoder=opus \
        --enable-decoder=vorbis \
        --enable-decoder=pcm_s16le \
        --enable-decoder=pcm_s16be \
        --enable-decoder=pcm_f32le \
        --disable-muxers \
        --enable-muxer=wav \
        --disable-demuxers \
        --enable-demuxer=aac \
        --enable-demuxer=mp3 \
        --enable-demuxer=flac \
        --enable-demuxer=ogg \
        --enable-demuxer=mov \
        --enable-demuxer=matroska \
        --enable-demuxer=wav \
        --disable-parsers \
        --enable-parser=aac \
        --enable-parser=mpegaudio \
        --enable-parser=flac \
        --enable-parser=opus \
        --enable-parser=vorbis \
        --disable-bsfs \
        --disable-protocols \
        --enable-protocol=file \
        --disable-indevs \
        --disable-outdevs \
        --extra-cflags="-O3" \
        --extra-ldflags="" \
        --enable-pthreads \
        --disable-debug \
        --disable-stripping

    echo "[INFO] Building (this may take 10-15 minutes)..." >&2
    make -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)"

    echo "[INFO] Installing binary..." >&2
    mkdir -p "$BIN_DIR"
    local output_name="ffmpeg-${PLATFORM_SUFFIX}"
    cp ffmpeg "$BIN_DIR/$output_name"
    chmod +x "$BIN_DIR/$output_name"

    # Strip binary to reduce size
    strip "$BIN_DIR/$output_name" 2>/dev/null || true

    echo "[INFO] Cleaning up..." >&2
    cd /
    rm -rf "$BUILD_DIR"

    # Get binary size
    local size
    size=$(du -h "$BIN_DIR/$output_name" | cut -f1)

    echo "[INFO] ffmpeg installed: $BIN_DIR/$output_name" >&2
    echo "[INFO] Binary size: $size" >&2
    echo "[INFO] License: LGPL (no GPL components)" >&2
    echo "[INFO] Features: Audio decoding (AAC, MP3, FLAC, Opus, Vorbis) + WAV output" >&2
}

check_prerequisites
build_ffmpeg

echo "[SUCCESS] Build complete!" >&2
"$BIN_DIR/ffmpeg-${PLATFORM_SUFFIX}" -version 2>&1 | head -3
