#!/bin/bash
set -e

# Load dependencies
source "$(dirname "$0")/_utility__ensure_jq.sh"
source "$(dirname "$0")/_utility__naming.sh"

# --- Parse flags from any position ---
FORCE_REFRESH=false
CHECK_MODE=false
ARGS=()
for arg in "$@"; do
    case "$arg" in
        --force|-f) FORCE_REFRESH=true ;;
        --check|-c) CHECK_MODE=true ;;
        *) ARGS+=("$arg") ;;
    esac
done
set -- "${ARGS[@]}"

# Summaries directory (skill-local) — defined early for both --check and normal mode
SUMMARY_DIR="$(cd "$(dirname "$0")/.." && pwd)/data"
mkdir -p "$SUMMARY_DIR"

# --- Helper: read metadata fields from centralized store ---
read_meta_fields() {
    local vid="$1"
    META_VIDEO_ID=""
    META_TITLE=""
    META_CHANNEL=""
    META_URL=""
    if [ -n "$vid" ]; then
        local meta
        meta=$(read_meta "$vid")
        if [ -n "$meta" ]; then
            META_VIDEO_ID=$(echo "$meta" | "$JQ" -r '.video_id // empty')
            META_TITLE=$(echo "$meta" | "$JQ" -r '.title // empty')
            META_CHANNEL=$(echo "$meta" | "$JQ" -r '.channel // empty')
            META_URL=$(echo "$meta" | "$JQ" -r '.url // empty')
        fi
    fi
}

# --- Check mode: lookup only, no transcript file needed ---
if [ "$CHECK_MODE" = "true" ]; then
    INPUT="$1"
    if [ -z "$INPUT" ]; then
        "$JQ" -n --arg status "error" \
            --arg message "Usage: summary.sh --check <URL_or_video_id>" \
            '{status: $status, message: $message}'
        exit 1
    fi

    # Extract video_id: try URL first, then treat as raw 11-char video_id
    VIDEO_ID=$(extract_video_id_from_url "$INPUT")
    if [ -z "$VIDEO_ID" ]; then
        if [[ "$INPUT" =~ ^[a-zA-Z0-9_-]{11}$ ]]; then
            VIDEO_ID="$INPUT"
        else
            "$JQ" -n --arg status "error" \
                --arg message "Could not extract video_id from: $INPUT" \
                '{status: $status, message: $message}'
            exit 1
        fi
    fi

    # Search for existing summary in data/
    EXISTING_SUMMARY=""
    if [ -d "$SUMMARY_DIR" ]; then
        EXISTING_SUMMARY=$(find_file_by_id "$SUMMARY_DIR" "$VIDEO_ID" "*.md")
    fi

    # Read metadata from centralized store
    read_meta_fields "$VIDEO_ID"

    if [ -n "$EXISTING_SUMMARY" ] && [ -f "$EXISTING_SUMMARY" ]; then
        SUMMARY_CHAR_COUNT=$(wc -c < "$EXISTING_SUMMARY" | tr -d ' ')
        SUMMARY_LINE_COUNT=$(wc -l < "$EXISTING_SUMMARY" | tr -d ' ')

        echo "[INFO] Found cached summary: $EXISTING_SUMMARY" >&2

        "$JQ" -n \
            --arg status "success" \
            --argjson exists true \
            --arg output_summary "$EXISTING_SUMMARY" \
            --argjson summary_char_count "$SUMMARY_CHAR_COUNT" \
            --argjson summary_line_count "$SUMMARY_LINE_COUNT" \
            --arg video_id "${META_VIDEO_ID:-$VIDEO_ID}" \
            --arg title "$META_TITLE" \
            --arg channel "$META_CHANNEL" \
            --arg url "$META_URL" \
            '{
                status: $status,
                exists: $exists,
                output_summary: $output_summary,
                summary_char_count: $summary_char_count,
                summary_line_count: $summary_line_count,
                video_id: $video_id,
                title: $title,
                channel: $channel,
                url: $url
            }'
    else
        echo "[INFO] No cached summary found for: $VIDEO_ID" >&2

        "$JQ" -n \
            --arg status "success" \
            --argjson exists false \
            --arg video_id "${META_VIDEO_ID:-$VIDEO_ID}" \
            --arg title "$META_TITLE" \
            --arg channel "$META_CHANNEL" \
            --arg url "$META_URL" \
            '{
                status: $status,
                exists: $exists,
                video_id: $video_id,
                title: $title,
                channel: $channel,
                url: $url
            }'
    fi
    exit 0
fi

# --- Normal mode: requires transcript file path ---
FILE_PATH="$1"

if [ -z "$FILE_PATH" ]; then
    "$JQ" -n --arg status "error" \
        --arg message "Usage: summary.sh <transcript_file_path> [--force] | summary.sh --check <URL_or_video_id>" \
        '{status: $status, message: $message}'
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    "$JQ" -n --arg status "error" \
        --arg message "File not found: $FILE_PATH" \
        '{status: $status, message: $message}'
    exit 1
fi

# Resolve absolute path
ABS_PATH="$(cd "$(dirname "$FILE_PATH")" && pwd)/$(basename "$FILE_PATH")"
CHAR_COUNT=$(wc -c < "$FILE_PATH" | tr -d ' ')
LINE_COUNT=$(wc -l < "$FILE_PATH" | tr -d ' ')

# Determine processing strategy based on content size
if [ "$CHAR_COUNT" -lt 80000 ]; then
    STRATEGY="standard"
elif [ "$CHAR_COUNT" -lt 200000 ]; then
    STRATEGY="sectioned"
else
    STRATEGY="chunked"
fi

# Calculate output summary path (skill-local data/)
BASENAME=$(basename "$ABS_PATH")
BASENAME_NO_EXT="${BASENAME%.*}"
OUTPUT_SUMMARY="$SUMMARY_DIR/${BASENAME_NO_EXT}.md"

# Extract video ID from filename (format: {YYYYMMDD}__{video_id}.{lang}.{ext})
VIDEO_ID=""
if [[ "$BASENAME_NO_EXT" == *"__"* ]]; then
    VIDEO_ID=$(extract_video_id_from_basename "$BASENAME_NO_EXT")
fi

# Read metadata from centralized store (if available)
read_meta_fields "$VIDEO_ID"

# --- Cache check (unless --force) ---
if [ "$FORCE_REFRESH" != "true" ] && [ -n "$VIDEO_ID" ]; then
    EXISTING_SUMMARY=$(find_file_by_id "$SUMMARY_DIR" "$VIDEO_ID" "*.md")
    if [ -n "$EXISTING_SUMMARY" ] && [ -f "$EXISTING_SUMMARY" ]; then
        echo "[INFO] Using cached summary: $EXISTING_SUMMARY" >&2

        # Get file statistics
        SUMMARY_CHAR_COUNT=$(wc -c < "$EXISTING_SUMMARY" | tr -d ' ')
        SUMMARY_LINE_COUNT=$(wc -l < "$EXISTING_SUMMARY" | tr -d ' ')

        "$JQ" -n \
            --arg status "success" \
            --arg source_transcript "$ABS_PATH" \
            --arg output_summary "$EXISTING_SUMMARY" \
            --argjson char_count "$CHAR_COUNT" \
            --argjson line_count "$LINE_COUNT" \
            --arg strategy "$STRATEGY" \
            --argjson cached true \
            --argjson summary_char_count "$SUMMARY_CHAR_COUNT" \
            --argjson summary_line_count "$SUMMARY_LINE_COUNT" \
            --arg video_id "$META_VIDEO_ID" \
            --arg title "$META_TITLE" \
            --arg channel "$META_CHANNEL" \
            --arg url "$META_URL" \
            '{
                status: $status,
                source_transcript: $source_transcript,
                output_summary: $output_summary,
                char_count: $char_count,
                line_count: $line_count,
                strategy: $strategy,
                cached: $cached,
                summary_char_count: $summary_char_count,
                summary_line_count: $summary_line_count,
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
    rm -f "$SUMMARY_DIR/"*"__${VIDEO_ID}."*.md 2>/dev/null || true
fi

"$JQ" -n \
    --arg status "success" \
    --arg source_transcript "$ABS_PATH" \
    --arg output_summary "$OUTPUT_SUMMARY" \
    --argjson char_count "$CHAR_COUNT" \
    --argjson line_count "$LINE_COUNT" \
    --arg strategy "$STRATEGY" \
    --argjson cached false \
    --arg video_id "$META_VIDEO_ID" \
    --arg title "$META_TITLE" \
    --arg channel "$META_CHANNEL" \
    --arg url "$META_URL" \
    '{
        status: $status,
        source_transcript: $source_transcript,
        output_summary: $output_summary,
        char_count: $char_count,
        line_count: $line_count,
        strategy: $strategy,
        cached: $cached,
        video_id: $video_id,
        title: $title,
        channel: $channel,
        url: $url
    }'
