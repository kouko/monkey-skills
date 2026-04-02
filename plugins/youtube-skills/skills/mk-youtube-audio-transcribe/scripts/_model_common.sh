#!/bin/bash
# _model_common.sh - Common model functions
#
# Shared functions for model management.
# This file is sourced by _ensure_model.sh, _download_model.sh, and download-model.sh
#
# Usage:
#   source "$(dirname "$0")/_model_common.sh"

# Get model SHA256 hash (from Hugging Face X-Linked-ETag header)
# Used for integrity verification
get_model_sha256() {
    local name="$1"
    case "$name" in
        tiny)           echo "be07e048e1e599ad46341c8d2a135645097a538221678b7acdd1b1919c6e1b21" ;;
        base)           echo "60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe" ;;
        small)          echo "1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b" ;;
        medium)         echo "6c14d5adee5f86394037b4e4e8b59f1673b6cee10e3cf0b11bbdbee79c156208" ;;
        large-v3)       echo "64d182b440b98d5203c4f9bd541544d84c605196c4f7b845dfa11fb23594d1e2" ;;
        large-v3-turbo) echo "1fc70f774d38eb169993ac391eea357ef47c88757ef72ee5943879b7e8e2bc69" ;;
        belle-zh)       echo "2a3bba5bfdb4d4da3d9949a83b405711727ca1941d4d5810895e077eb3cb4d99" ;;
        kotoba-ja)      echo "eff70a8a236e731abba774ba71e1f6d0fce53302137208c32207e694e0bf4546" ;;
        kotoba-ja-q5)   echo "4a3b92192b5d3578ff854a5876213e2e27af0c2d357492c2d14271e82c303658" ;;
        *)              echo "" ;;
    esac
}

# Get model size human readable
get_model_size_human() {
    local name="$1"
    case "$name" in
        tiny)           echo "74MB" ;;
        base)           echo "141MB" ;;
        small)          echo "465MB" ;;
        medium)         echo "1.4GB" ;;
        large-v3)       echo "2.9GB" ;;
        large-v3-turbo) echo "1.5GB" ;;
        belle-zh)       echo "1.5GB" ;;
        kotoba-ja)      echo "1.4GB" ;;
        kotoba-ja-q5)   echo "513MB" ;;
        *)              echo "unknown" ;;
    esac
}

# Get model description (for user-facing output)
get_model_description() {
    local name="$1"
    case "$name" in
        tiny)           echo "Fastest, lowest accuracy" ;;
        base)           echo "Fast, moderate accuracy" ;;
        small)          echo "Balanced speed/accuracy" ;;
        medium)         echo "High accuracy (recommended for general use)" ;;
        large-v3)       echo "Best accuracy, slowest" ;;
        large-v3-turbo) echo "Large model optimized for speed" ;;
        belle-zh)       echo "Chinese-specialized (recommended for zh)" ;;
        kotoba-ja)      echo "Japanese-specialized (recommended for ja)" ;;
        kotoba-ja-q5)   echo "Japanese-specialized, quantized (faster)" ;;
        *)              echo "" ;;
    esac
}

# Map model name to local filename
get_model_filename() {
    local name="$1"
    case "$name" in
        # Standard whisper.cpp models
        tiny)           echo "ggml-tiny.bin" ;;
        base)           echo "ggml-base.bin" ;;
        small)          echo "ggml-small.bin" ;;
        medium)         echo "ggml-medium.bin" ;;
        large-v3)       echo "ggml-large-v3.bin" ;;
        large-v3-turbo) echo "ggml-large-v3-turbo.bin" ;;
        # Language-specialized models
        belle-zh)       echo "ggml-belle-zh.bin" ;;
        kotoba-ja)      echo "ggml-kotoba-ja.bin" ;;
        kotoba-ja-q5)   echo "ggml-kotoba-ja-q5.bin" ;;
        *)              echo "" ;;
    esac
}

# Get download URL for model
get_model_url() {
    local name="$1"
    case "$name" in
        # Standard whisper.cpp models (ggerganov/whisper.cpp)
        tiny)           echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin" ;;
        base)           echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin" ;;
        small)          echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin" ;;
        medium)         echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin" ;;
        large-v3)       echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin" ;;
        large-v3-turbo) echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin" ;;
        # Chinese-specialized model (BELLE-2)
        belle-zh)       echo "https://huggingface.co/BELLE-2/Belle-whisper-large-v3-turbo-zh-ggml/resolve/main/ggml-model.bin" ;;
        # Japanese-specialized model (kotoba-tech)
        kotoba-ja)      echo "https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0-ggml/resolve/main/ggml-kotoba-whisper-v2.0.bin" ;;
        kotoba-ja-q5)   echo "https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0-ggml/resolve/main/ggml-kotoba-whisper-v2.0-q5_0.bin" ;;
        *)              echo "" ;;
    esac
}
