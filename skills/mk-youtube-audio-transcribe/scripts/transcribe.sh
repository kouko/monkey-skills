#!/bin/bash
# transcribe.sh - Transcribe audio to text using whisper.cpp
#
# Usage:
#   ./scripts/transcribe.sh "<audio_file>" [model] [language]
#
# Parameters:
#   audio_file - Path to audio file (required)
#   model      - Model name: auto, tiny, base, small, medium, large-v3, belle-zh, kotoba-ja (default: auto)
#   language   - Language code: en, ja, zh, auto (default: auto)
#
# Auto-selection (model=auto):
#   - zh → belle-zh (Chinese-specialized)
#   - ja → kotoba-ja (Japanese-specialized)
#   - others → medium (general purpose)
#
# Output: JSON with transcription result

set -e

# Load dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load jq first (needed for JSON error output)
if ! source "$SCRIPT_DIR/_utility__ensure_jq.sh"; then
    echo '{"status":"error","message":"Failed to load jq dependency script"}' >&2
    exit 1
fi
if [ -n "$JQ_ERROR_JSON" ]; then
    echo "$JQ_ERROR_JSON"
    exit 1
fi
if [ -z "$JQ" ]; then
    echo '{"status":"error","message":"JQ not set after sourcing _utility__ensure_jq.sh"}' >&2
    exit 1
fi

# Load ffmpeg
if ! source "$SCRIPT_DIR/_utility__ensure_ffmpeg.sh"; then
    "$JQ" -n '{status:"error",message:"Failed to load ffmpeg dependency script"}'
    exit 1
fi
if [ -n "$FFMPEG_ERROR_JSON" ]; then
    echo "$FFMPEG_ERROR_JSON"
    exit 1
fi
if [ -z "$FFMPEG" ]; then
    "$JQ" -n '{status:"error",message:"FFMPEG not set after sourcing _utility__ensure_ffmpeg.sh"}'
    exit 1
fi

# Load whisper
if ! source "$SCRIPT_DIR/_ensure_whisper.sh"; then
    "$JQ" -n '{status:"error",message:"Failed to load whisper dependency script"}'
    exit 1
fi
if [ -n "$WHISPER_ERROR_JSON" ]; then
    echo "$WHISPER_ERROR_JSON"
    exit 1
fi
if [ -z "$WHISPER" ]; then
    "$JQ" -n '{status:"error",message:"WHISPER not set after sourcing _ensure_whisper.sh"}'
    exit 1
fi

source "$SCRIPT_DIR/_utility__naming.sh"

# --- Parse --force flag from any position ---
FORCE_REFRESH=false
ARGS=()
for arg in "$@"; do
    case "$arg" in
        --force|-f) FORCE_REFRESH=true ;;
        *) ARGS+=("$arg") ;;
    esac
done
set -- "${ARGS[@]}"

AUDIO_FILE="$1"
MODEL="${2:-auto}"
LANGUAGE="${3:-auto}"

# Auto-select model based on language when model=auto
if [ "$MODEL" = "auto" ]; then
    case "$LANGUAGE" in
        zh)
            MODEL="belle-zh"
            echo "[INFO] Auto-selected Chinese-specialized model: belle-zh" >&2
            ;;
        ja)
            MODEL="kotoba-ja"
            echo "[INFO] Auto-selected Japanese-specialized model: kotoba-ja" >&2
            ;;
        *)
            MODEL="medium"
            echo "[INFO] Auto-selected general model: medium" >&2
            ;;
    esac
fi

if [ -z "$AUDIO_FILE" ]; then
    "$JQ" -n '{status: "error", message: "Usage: transcribe.sh <audio_file> [model] [language]"}'
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    "$JQ" -n --arg file "$AUDIO_FILE" '{status: "error", message: ("File not found: " + $file)}'
    exit 1
fi

# Ensure model is available (does NOT auto-download)
set +e
source "$SCRIPT_DIR/_ensure_model.sh" "$MODEL"
MODEL_EXIT_CODE=$?
set -e

if [ $MODEL_EXIT_CODE -eq 2 ]; then
    # Model not found - output structured error with download info
    echo "$MODEL_ERROR_JSON" | "$JQ" '{
        status: "error",
        error_code: .error_code,
        message: .message,
        model: .model,
        model_size: .model_size,
        download_url: .download_url,
        download_command: .download_command,
        hint: "Execute download_command using Bash tool with timeout: 1800000 (30 minutes)"
    }'
    exit 1
elif [ $MODEL_EXIT_CODE -eq 3 ]; then
    # Model corrupted - output structured error with re-download info
    echo "$MODEL_ERROR_JSON" | "$JQ" '{
        status: "error",
        error_code: .error_code,
        message: .message,
        model: .model,
        model_size: .model_size,
        expected_sha256: .expected_sha256,
        actual_sha256: .actual_sha256,
        model_path: .model_path,
        download_command: .download_command,
        hint: "Execute download_command using Bash tool with timeout: 1800000 (30 minutes)"
    }'
    exit 1
elif [ $MODEL_EXIT_CODE -ne 0 ]; then
    # Other error (unknown model, etc.)
    if [ -n "$MODEL_ERROR_JSON" ]; then
        echo "$MODEL_ERROR_JSON" | "$JQ" '{status: "error"} + .'
    else
        "$JQ" -n --arg model "$MODEL" '{status: "error", message: ("Failed to load model: " + $model)}'
    fi
    exit 1
fi

# Create temp directory for processing
TEMP_DIR="$MONKEY_KNOWLEDGE_TMP/build/whisper-transcribe-$$"
mkdir -p "$TEMP_DIR"

# Output directory (skill-local)
OUTPUT_DIR="$SCRIPT_DIR/../data"
mkdir -p "$OUTPUT_DIR"

# Generate output filename from audio file (preserving unified naming)
BASENAME=$(LC_ALL=en_US.UTF-8 basename "$AUDIO_FILE" | LC_ALL=en_US.UTF-8 sed 's/\.[^.]*$//')
JSON_OUTPUT="$OUTPUT_DIR/${BASENAME}.json"
TEXT_OUTPUT="$OUTPUT_DIR/${BASENAME}.txt"

# Extract video ID from filename (format: {YYYYMMDD}__{id}__{title}.{ext})
# Video ID is extracted from position 10-20 (after the date prefix)
VIDEO_ID=""
if [[ "$BASENAME" == *"__"* ]]; then
    VIDEO_ID=$(extract_video_id_from_basename "$BASENAME")
fi

# Read metadata from centralized store (if available)
EXISTING_META=""
if [ -n "$VIDEO_ID" ]; then
    EXISTING_META=$(read_meta "$VIDEO_ID")
fi

# Extract metadata fields (empty if not found)
META_VIDEO_ID=""
META_TITLE=""
META_CHANNEL=""
META_URL=""
if [ -n "$EXISTING_META" ]; then
    META_VIDEO_ID=$(echo "$EXISTING_META" | "$JQ" -r '.video_id // empty')
    META_TITLE=$(echo "$EXISTING_META" | "$JQ" -r '.title // empty')
    META_CHANNEL=$(echo "$EXISTING_META" | "$JQ" -r '.channel // empty')
    META_URL=$(echo "$EXISTING_META" | "$JQ" -r '.url // empty')
fi

# --- Cache check (unless --force) ---
if [ "$FORCE_REFRESH" != "true" ] && [ -n "$VIDEO_ID" ]; then
    EXISTING_JSON=$(find_file_by_id "$OUTPUT_DIR" "$VIDEO_ID" "*.json")
    if [ -n "$EXISTING_JSON" ] && [ -f "$EXISTING_JSON" ]; then
        EXISTING_TXT="${EXISTING_JSON%.json}.txt"
        echo "[INFO] Using cached transcription: $EXISTING_JSON" >&2

        # Get file statistics
        CHAR_COUNT=$(wc -c < "$EXISTING_JSON" | tr -d ' ')
        LINE_COUNT=$(wc -l < "$EXISTING_JSON" | tr -d ' ')
        TEXT_CHAR_COUNT=0
        TEXT_LINE_COUNT=0
        if [ -f "$EXISTING_TXT" ]; then
            TEXT_CHAR_COUNT=$(wc -c < "$EXISTING_TXT" | tr -d ' ')
            TEXT_LINE_COUNT=$(wc -l < "$EXISTING_TXT" | tr -d ' ')
        fi

        # Extract language and model from cached JSON
        CACHED_LANG=$("$JQ" -r '.language // "unknown"' "$EXISTING_JSON")
        CACHED_DURATION=$("$JQ" -r '.duration // ""' "$EXISTING_JSON")
        CACHED_MODEL=$("$JQ" -r '.model // ""' "$EXISTING_JSON")

        "$JQ" -n \
            --arg file_path "$EXISTING_JSON" \
            --arg text_file_path "$EXISTING_TXT" \
            --arg language "$CACHED_LANG" \
            --arg duration "$CACHED_DURATION" \
            --arg model "$CACHED_MODEL" \
            --argjson char_count "$CHAR_COUNT" \
            --argjson line_count "$LINE_COUNT" \
            --argjson text_char_count "$TEXT_CHAR_COUNT" \
            --argjson text_line_count "$TEXT_LINE_COUNT" \
            --argjson cached true \
            --arg video_id "$META_VIDEO_ID" \
            --arg title "$META_TITLE" \
            --arg channel "$META_CHANNEL" \
            --arg url "$META_URL" \
            '{
                status: "success",
                file_path: $file_path,
                text_file_path: $text_file_path,
                language: $language,
                duration: $duration,
                model: $model,
                char_count: $char_count,
                line_count: $line_count,
                text_char_count: $text_char_count,
                text_line_count: $text_line_count,
                cached: $cached,
                video_id: $video_id,
                title: $title,
                channel: $channel,
                url: $url
            }'
        exit 0
    fi
fi

# --- Force refresh: delete existing files ---
if [ "$FORCE_REFRESH" = "true" ] && [ -n "$VIDEO_ID" ]; then
    echo "[INFO] Force refresh enabled, removing existing files..." >&2
    rm -f "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.json "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.txt 2>/dev/null || true
fi

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Convert audio to 16kHz mono WAV (required by whisper)
WAV_FILE="$TEMP_DIR/audio.wav"
echo "[INFO] Converting audio to WAV..." >&2
"$FFMPEG" -i "$AUDIO_FILE" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV_FILE" -y 2>/dev/null

# Get audio duration
DURATION=$("$FFMPEG" -i "$AUDIO_FILE" 2>&1 | grep "Duration" | cut -d ' ' -f 4 | sed 's/,//' | cut -d '.' -f 1)

# Detect CPU cores for optimal threading
CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null)
if [ -z "$CPU_CORES" ]; then
    CPU_CORES=$(nproc 2>/dev/null || echo 4)
fi
THREADS=$(( (CPU_CORES + 1) / 2 ))  # 使用一半核心數
echo "[INFO] Using $THREADS threads (half of $CPU_CORES cores)" >&2

# Build whisper command
WHISPER_ARGS=("-f" "$WAV_FILE" "-m" "$MODEL_PATH" "-oj" "-t" "$THREADS" "--print-progress" "--beam-size" "2" "--max-context" "512")

# Add language option (auto = don't specify, let whisper detect)
if [ "$LANGUAGE" != "auto" ]; then
    WHISPER_ARGS+=("-l" "$LANGUAGE")
fi

# Run whisper
echo "[INFO] Transcribing with model: $MODEL..." >&2
OUTPUT_FILE="$TEMP_DIR/output"
"$WHISPER" "${WHISPER_ARGS[@]}" -of "$OUTPUT_FILE" >/dev/null

# Check if output exists
JSON_FILE="$OUTPUT_FILE.json"
if [ ! -f "$JSON_FILE" ]; then
    "$JQ" -n '{status: "error", message: "Transcription failed"}'
    exit 1
fi

# Extract language from whisper output
DETECTED_LANG=$("$JQ" -r '.result.language // "unknown"' "$JSON_FILE")

# Save full JSON to file
"$JQ" --arg model "$MODEL" --arg duration "$DURATION" '
{
    text: .transcription | map(.text) | join(""),
    language: .result.language,
    duration: $duration,
    model: $model,
    segments: [.transcription[] | {
        start: .timestamps.from,
        end: .timestamps.to,
        text: .text
    }]
}
' "$JSON_FILE" > "$JSON_OUTPUT"

# Save plain text to file
"$JQ" -r '.transcription | map(.text) | join("")' "$JSON_FILE" > "$TEXT_OUTPUT"

# Get file statistics
CHAR_COUNT=$(wc -c < "$JSON_OUTPUT" | tr -d ' ')
LINE_COUNT=$(wc -l < "$JSON_OUTPUT" | tr -d ' ')
TEXT_CHAR_COUNT=$(wc -c < "$TEXT_OUTPUT" | tr -d ' ')
TEXT_LINE_COUNT=$(wc -l < "$TEXT_OUTPUT" | tr -d ' ')

# Output file paths and metadata
"$JQ" -n \
    --arg file_path "$JSON_OUTPUT" \
    --arg text_file_path "$TEXT_OUTPUT" \
    --arg language "$DETECTED_LANG" \
    --arg duration "$DURATION" \
    --arg model "$MODEL" \
    --argjson char_count "$CHAR_COUNT" \
    --argjson line_count "$LINE_COUNT" \
    --argjson text_char_count "$TEXT_CHAR_COUNT" \
    --argjson text_line_count "$TEXT_LINE_COUNT" \
    --argjson cached false \
    --arg video_id "$META_VIDEO_ID" \
    --arg title "$META_TITLE" \
    --arg channel "$META_CHANNEL" \
    --arg url "$META_URL" \
    '{
        status: "success",
        file_path: $file_path,
        text_file_path: $text_file_path,
        language: $language,
        duration: $duration,
        model: $model,
        char_count: $char_count,
        line_count: $line_count,
        text_char_count: $text_char_count,
        text_line_count: $text_line_count,
        cached: $cached,
        video_id: $video_id,
        title: $title,
        channel: $channel,
        url: $url
    }'
