#!/bin/bash
# _download_model.sh - Download whisper model (internal script)
#
# Downloads model from Hugging Face.
# For interactive use with --list, use: download-model.sh
#
# Usage:
#   ./_download_model.sh <model_name>
#
# Exit codes:
#   0 - Success
#   1 - Unknown model
#   2 - Download failed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/../models"

# Source common functions
source "$SCRIPT_DIR/_model_common.sh"

download_model() {
    local model_name="$1"
    local filename download_url model_path

    filename=$(get_model_filename "$model_name")
    if [ -z "$filename" ]; then
        echo "ERROR: Unknown model: $model_name" >&2
        echo "Available: tiny, base, small, medium, large-v3, large-v3-turbo, belle-zh, kotoba-ja, kotoba-ja-q5" >&2
        exit 1
    fi

    model_path="$MODELS_DIR/$filename"
    download_url=$(get_model_url "$model_name")

    # Check if already exists
    if [ -f "$model_path" ]; then
        echo "[INFO] Model already exists: $model_path" >&2
        echo "[INFO] Size: $(du -h "$model_path" | cut -f1)" >&2
        exit 0
    fi

    echo "[INFO] Downloading model: $model_name" >&2
    echo "[INFO] URL: $download_url" >&2

    mkdir -p "$MODELS_DIR"

    # Prefer wget (better progress in non-TTY), fallback to curl
    if command -v wget &> /dev/null; then
        wget --show-progress -O "$model_path" "$download_url" 2>&1
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$model_path" "$download_url" 2>&1
    else
        echo "ERROR: curl or wget required" >&2
        exit 2
    fi

    echo "[SUCCESS] Model downloaded: $model_path" >&2
    echo "[INFO] Size: $(du -h "$model_path" | cut -f1)" >&2
}

# Main
if [ $# -eq 0 ]; then
    echo "Usage: $0 <model_name>" >&2
    echo "Available: tiny, base, small, medium, large-v3, large-v3-turbo, belle-zh, kotoba-ja, kotoba-ja-q5" >&2
    exit 1
fi

download_model "$1"
