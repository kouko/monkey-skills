#!/bin/bash
# _ensure_model.sh - Ensure whisper model is available
#
# Checks if model exists locally. Returns error if not found.
# Does NOT auto-download - returns structured error with download command.
#
# Usage:
#   source "$(dirname "$0")/_ensure_model.sh" [model_name]
#   echo "Model path: $MODEL_PATH"
#
# Exit codes:
#   0 - Model found and verified (MODEL_PATH is set)
#   1 - Unknown model (MODEL_ERROR_JSON is set)
#   2 - Model not found (MODEL_ERROR_JSON is set with download_command)
#   3 - Model corrupted (MODEL_ERROR_JSON is set)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/../models"

# Source common functions
source "$SCRIPT_DIR/_model_common.sh"

# Model name (default: medium)
MODEL_NAME="${1:-medium}"

# Initialize result variables
MODEL_PATH=""
MODEL_ERROR_JSON=""
_MODEL_EXIT_CODE=0

# Get filename
_MODEL_FILENAME=$(get_model_filename "$MODEL_NAME")

# Check for unknown model
if [ -z "$_MODEL_FILENAME" ]; then
    MODEL_ERROR_JSON=$(cat <<EOF
{
    "error_code": "UNKNOWN_MODEL",
    "message": "Unknown model: $MODEL_NAME",
    "available_models": ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo", "belle-zh", "kotoba-ja", "kotoba-ja-q5"]
}
EOF
)
    _MODEL_EXIT_CODE=1
else
    _MODEL_PATH_CHECK="$MODELS_DIR/$_MODEL_FILENAME"
    _DOWNLOAD_URL=$(get_model_url "$MODEL_NAME")
    _MODEL_SIZE_HUMAN=$(get_model_size_human "$MODEL_NAME")

    # Check if model exists - do NOT auto-download
    if [ ! -f "$_MODEL_PATH_CHECK" ]; then
        MODEL_ERROR_JSON=$(cat <<EOF
{
    "error_code": "MODEL_NOT_FOUND",
    "message": "Model '$MODEL_NAME' not found. Please download it first.",
    "model": "$MODEL_NAME",
    "model_size": "$_MODEL_SIZE_HUMAN",
    "download_url": "$_DOWNLOAD_URL",
    "download_command": "curl -L --progress-bar -o '$_MODEL_PATH_CHECK' '$_DOWNLOAD_URL' 2>&1"
}
EOF
)
        _MODEL_EXIT_CODE=2
    fi

    # Verify model if no error yet
    if [ $_MODEL_EXIT_CODE -eq 0 ] && [ -f "$_MODEL_PATH_CHECK" ]; then
        _EXPECTED_SHA256=$(get_model_sha256 "$MODEL_NAME")

        if [ -z "$_EXPECTED_SHA256" ]; then
            # No SHA256 defined for this model - skip verification
            MODEL_PATH="$_MODEL_PATH_CHECK"
            _MODEL_EXIT_CODE=0
        else
            # Calculate local SHA256
            echo "[INFO] Verifying model integrity..." >&2
            _ACTUAL_SHA256=$(shasum -a 256 "$_MODEL_PATH_CHECK" 2>/dev/null | awk '{print $1}')

            if [ "$_ACTUAL_SHA256" = "$_EXPECTED_SHA256" ]; then
                # SHA256 verified
                MODEL_PATH="$_MODEL_PATH_CHECK"
                _MODEL_EXIT_CODE=0
                echo "[INFO] Model verified: $MODEL_NAME" >&2
            else
                # SHA256 mismatch - model corrupted or incomplete
                MODEL_ERROR_JSON=$(cat <<EOF
{
    "error_code": "MODEL_CORRUPTED",
    "message": "Model '$MODEL_NAME' is corrupted or incomplete. Please re-download.",
    "model": "$MODEL_NAME",
    "model_size": "$_MODEL_SIZE_HUMAN",
    "expected_sha256": "$_EXPECTED_SHA256",
    "actual_sha256": "$_ACTUAL_SHA256",
    "model_path": "$_MODEL_PATH_CHECK",
    "download_command": "rm '$_MODEL_PATH_CHECK' && curl -L --progress-bar -o '$_MODEL_PATH_CHECK' '$_DOWNLOAD_URL' 2>&1"
}
EOF
)
                _MODEL_EXIT_CODE=3
            fi
        fi
    fi
fi

# Export results
export MODEL_PATH
export MODEL_NAME
export MODEL_ERROR_JSON

# Return/exit with appropriate code
if [ $_MODEL_EXIT_CODE -ne 0 ]; then
    return $_MODEL_EXIT_CODE 2>/dev/null || exit $_MODEL_EXIT_CODE
fi
