#!/bin/bash
# download-model.sh - Download whisper model
#
# Downloads model from Hugging Face with progress bar.
# Run this in terminal to see download progress.
#
# Usage:
#   ./scripts/download-model.sh <model_name>
#   ./scripts/download-model.sh --list
#
# Examples:
#   ./scripts/download-model.sh medium      # Download medium model (1.5GB)
#   ./scripts/download-model.sh belle-zh    # Download Chinese model
#   ./scripts/download-model.sh kotoba-ja   # Download Japanese model
#   ./scripts/download-model.sh --list      # List available models

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/../models"

# Source common functions
source "$SCRIPT_DIR/_model_common.sh"

# Show available models
show_models() {
    echo "Available models:"
    echo ""
    echo "Standard Models:"
    printf "  %-16s %-10s %s\n" "MODEL" "SIZE" "DESCRIPTION"
    printf "  %-16s %-10s %s\n" "-----" "----" "-----------"
    for model in tiny base small medium large-v3 large-v3-turbo; do
        printf "  %-16s %-10s %s\n" "$model" "$(get_model_size_human "$model")" "$(get_model_description "$model")"
    done
    echo ""
    echo "Language-Specialized Models:"
    printf "  %-16s %-10s %s\n" "MODEL" "SIZE" "DESCRIPTION"
    printf "  %-16s %-10s %s\n" "-----" "----" "-----------"
    for model in belle-zh kotoba-ja kotoba-ja-q5; do
        printf "  %-16s %-10s %s\n" "$model" "$(get_model_size_human "$model")" "$(get_model_description "$model")"
    done
    echo ""
    echo "Usage: $0 <model_name>"
}

# Download model (calls internal _download_model.sh)
download_model() {
    local model_name="$1"
    local filename
    filename=$(get_model_filename "$model_name")

    if [ -z "$filename" ]; then
        echo "ERROR: Unknown model: $model_name" >&2
        echo "" >&2
        show_models >&2
        exit 1
    fi

    local model_path="$MODELS_DIR/$filename"
    local download_url
    download_url=$(get_model_url "$model_name")
    local model_size
    model_size=$(get_model_size_human "$model_name")

    # Check if already downloaded
    if [ -f "$model_path" ]; then
        echo "[INFO] Model already exists: $model_path"
        echo "[INFO] Size: $(du -h "$model_path" | cut -f1)"
        exit 0
    fi

    echo "┌────────────────────────────────────────────────────┐"
    echo "│  Downloading Whisper Model                        │"
    echo "├────────────────────────────────────────────────────┤"
    echo "│  Model: $model_name"
    echo "│  Size:  $model_size"
    echo "│  URL:   $download_url"
    echo "└────────────────────────────────────────────────────┘"
    echo ""

    # Call internal download script
    bash "$SCRIPT_DIR/_download_model.sh" "$model_name"
}

# Main
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_models
    exit 0
fi

if [ "$1" = "--list" ] || [ "$1" = "-l" ]; then
    show_models
    exit 0
fi

download_model "$1"
