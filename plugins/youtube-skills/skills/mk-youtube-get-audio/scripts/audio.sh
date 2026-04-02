#!/bin/bash
set -e

# Load dependency scripts
source "$(dirname "$0")/_utility__ensure_ytdlp.sh"
source "$(dirname "$0")/_utility__ensure_jq.sh"
source "$(dirname "$0")/_utility__ensure_ffmpeg.sh" 2>/dev/null || true
source "$(dirname "$0")/_utility__naming.sh"

# Build --ffmpeg-location args if ffmpeg is available
FFMPEG_ARGS=()
if [ -n "$FFMPEG_DIR" ]; then
    FFMPEG_ARGS=(--ffmpeg-location "$FFMPEG_DIR")
fi

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

URL="$1"
OUTPUT_DIR="${2:-$MONKEY_KNOWLEDGE_TMP/youtube/audio}"
BROWSER="${3:-}"  # Optional: specify browser (chrome, firefox, safari, etc.)

if [ -z "$URL" ]; then
    "$JQ" -n '{status: "error", message: "Usage: audio.sh <url> [output_dir] [browser]"}'
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Get Chrome profiles directory based on OS
get_chrome_dir() {
    case "$(uname)" in
        Darwin) echo "$HOME/Library/Application Support/Google/Chrome" ;;
        Linux)  echo "$HOME/.config/google-chrome" ;;
        *)      echo "" ;;  # Windows needs different handling
    esac
}

# Try browser cookies and return the working browser string
try_browser_cookies() {
    local browser="$1"

    # For Chrome without specific profile, try all profiles
    if [[ "$browser" == "chrome" ]]; then
        local chrome_dir
        chrome_dir=$(get_chrome_dir)
        if [ -d "$chrome_dir" ]; then
            # Try Default profile first
            if "$YT_DLP" --cookies-from-browser "chrome:Default" --simulate "$URL" >/dev/null 2>&1; then
                echo "chrome:Default"
                return 0
            fi
            # Try other profiles
            for profile_dir in "$chrome_dir"/Profile*/; do
                if [ -d "$profile_dir" ]; then
                    local profile_name
                    profile_name=$(basename "$profile_dir")
                    if "$YT_DLP" --cookies-from-browser "chrome:$profile_name" --simulate "$URL" >/dev/null 2>&1; then
                        echo "chrome:$profile_name"
                        return 0
                    fi
                fi
            done
        fi
    fi

    # Non-Chrome or all Chrome profiles failed
    if "$YT_DLP" --cookies-from-browser "$browser" --simulate "$URL" >/dev/null 2>&1; then
        echo "$browser"
        return 0
    fi
    return 1
}

# Fetch metadata with optional cookie authentication
fetch_metadata() {
    local use_cookies="$1"
    local field="$2"
    local cookie_args=()

    if [ "$use_cookies" = "true" ] && [ -n "$BROWSER" ]; then
        cookie_args=(--cookies-from-browser "$BROWSER")
    elif [ "$use_cookies" = "true" ]; then
        for browser in chrome firefox safari edge brave; do
            local found_browser
            if found_browser=$(try_browser_cookies "$browser"); then
                cookie_args=(--cookies-from-browser "$found_browser")
                break
            fi
        done
    fi

    "$YT_DLP" --print "$field" "${cookie_args[@]}" "$URL" 2>/dev/null
}

# Pre-check: determine if we should use cookies first based on existing metadata
USE_COOKIES_FIRST="false"
VIDEO_ID_FROM_URL=$(extract_video_id_from_url "$URL")
if [ -n "$VIDEO_ID_FROM_URL" ] && check_needs_auth "$VIDEO_ID_FROM_URL"; then
    echo "[INFO] Known restricted video, using cookies directly..." >&2
    USE_COOKIES_FIRST="true"
fi

# Get video ID, title, and upload_date for unified naming (with fallback)
if [ "$USE_COOKIES_FIRST" = "true" ]; then
    VIDEO_ID=$(fetch_metadata "true" "id") || VIDEO_ID=""
    NEED_COOKIES="true"
else
    VIDEO_ID=$(fetch_metadata "false" "id") || VIDEO_ID=""
    if [ -z "$VIDEO_ID" ]; then
        echo "[INFO] First metadata attempt failed, retrying with browser cookies..." >&2
        VIDEO_ID=$(fetch_metadata "true" "id") || VIDEO_ID=""
        NEED_COOKIES="true"
    else
        NEED_COOKIES="false"
    fi
fi

if [ -z "$VIDEO_ID" ]; then
    "$JQ" -n '{status: "error", message: "Could not extract video ID (tried with and without cookies)"}'
    exit 1
fi

# Get remaining metadata using the determined cookie strategy
TITLE=$(fetch_metadata "$NEED_COOKIES" "title") || TITLE=""
if [ -z "$TITLE" ] && [ "$NEED_COOKIES" = "false" ]; then
    NEED_COOKIES="true"
    TITLE=$(fetch_metadata "true" "title") || TITLE=""
fi
UPLOAD_DATE=$(fetch_metadata "$NEED_COOKIES" "upload_date") || UPLOAD_DATE=""

BASENAME=$(make_basename "$UPLOAD_DATE" "$VIDEO_ID")

# Read existing metadata or create entry
EXISTING_META=$(read_meta "$VIDEO_ID")
if [ -z "$EXISTING_META" ]; then
    # Fetch metadata for centralized store
    CHANNEL=$(fetch_metadata "$NEED_COOKIES" "channel") || CHANNEL=""
    DURATION=$(fetch_metadata "$NEED_COOKIES" "duration_string") || DURATION=""
    WEBPAGE_URL=$(fetch_metadata "$NEED_COOKIES" "webpage_url") || WEBPAGE_URL="$URL"

    META_JSON=$("$JQ" -n \
        --arg video_id "$VIDEO_ID" \
        --arg title "$TITLE" \
        --arg channel "$CHANNEL" \
        --arg url "$WEBPAGE_URL" \
        --arg upload_date "$UPLOAD_DATE" \
        --arg duration_string "$DURATION" \
        --arg source "audio" \
        '{
            video_id: $video_id,
            title: $title,
            channel: $channel,
            url: $url,
            upload_date: $upload_date,
            duration_string: $duration_string,
            source: $source,
            partial: true,
            fetched_at: (now | todate)
        }')

    write_or_merge_meta "$META_DIR/$BASENAME.meta.json" "$META_JSON" "true"
    EXISTING_META="$META_JSON"
fi

# --- Cache check (unless --force) ---
if [ "$FORCE_REFRESH" != "true" ]; then
    EXISTING_AUDIO=$(find_file_by_id "$OUTPUT_DIR" "$VIDEO_ID" "*.{m4a,webm,opus,ogg,mp3,aac,wav}")
    if [ -z "$EXISTING_AUDIO" ]; then
        # Try each extension individually (brace expansion doesn't work in find_file_by_id)
        for ext in m4a webm opus ogg mp3 aac wav; do
            EXISTING_AUDIO=$(find_file_by_id "$OUTPUT_DIR" "$VIDEO_ID" "*.$ext")
            [ -n "$EXISTING_AUDIO" ] && break
        done
    fi
    if [ -n "$EXISTING_AUDIO" ] && [ -f "$EXISTING_AUDIO" ]; then
        echo "[INFO] Using cached audio: $EXISTING_AUDIO" >&2
        FILE_SIZE=$(ls -lh "$EXISTING_AUDIO" | awk '{print $5}')

        # Extract metadata fields for output
        META_VIDEO_ID=$(echo "$EXISTING_META" | "$JQ" -r '.video_id // empty')
        META_TITLE=$(echo "$EXISTING_META" | "$JQ" -r '.title // empty')
        META_CHANNEL=$(echo "$EXISTING_META" | "$JQ" -r '.channel // empty')
        META_URL=$(echo "$EXISTING_META" | "$JQ" -r '.url // empty')
        META_DURATION=$(echo "$EXISTING_META" | "$JQ" -r '.duration_string // empty')

        "$JQ" -n \
            --arg status "success" \
            --arg file_path "$EXISTING_AUDIO" \
            --arg file_size "$FILE_SIZE" \
            --argjson cached true \
            --arg video_id "$META_VIDEO_ID" \
            --arg title "$META_TITLE" \
            --arg channel "$META_CHANNEL" \
            --arg url "$META_URL" \
            --arg duration_string "$META_DURATION" \
            '{
                status: $status,
                file_path: $file_path,
                file_size: $file_size,
                cached: $cached,
                video_id: $video_id,
                title: $title,
                channel: $channel,
                url: $url,
                duration_string: $duration_string
            }'
        exit 0
    fi
fi

# --- Force refresh: delete existing files ---
if [ "$FORCE_REFRESH" = "true" ]; then
    echo "[INFO] Force refresh enabled, removing existing files..." >&2
    rm -f "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.m4a "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.webm 2>/dev/null || true
    rm -f "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.opus "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.ogg 2>/dev/null || true
    rm -f "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.mp3 "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.aac 2>/dev/null || true
    rm -f "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.wav 2>/dev/null || true
fi

# Create temp directory for download
TEMP_DIR=$(mktemp -d)
cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT

# Download audio with optional cookie authentication
download_audio() {
    local use_cookies="$1"
    local cookie_args=()

    if [ "$use_cookies" = "true" ] && [ -n "$BROWSER" ]; then
        cookie_args=(--cookies-from-browser "$BROWSER")
    elif [ "$use_cookies" = "true" ]; then
        # Auto-detect available browser (Chrome tries all profiles)
        for browser in chrome firefox safari edge brave; do
            local found_browser
            if found_browser=$(try_browser_cookies "$browser"); then
                cookie_args=(--cookies-from-browser "$found_browser")
                echo "[INFO] Using cookies from: $found_browser" >&2
                break
            fi
        done
    fi

    # Download to temp directory first, then rename
    "$YT_DLP" -x -o "$TEMP_DIR/%(id)s.%(ext)s" "${cookie_args[@]}" "${FFMPEG_ARGS[@]}" "$URL" 2>&1
}

# First attempt: without authentication
if ! download_audio "false" >&2; then
    echo "[INFO] First attempt failed, retrying with browser cookies..." >&2

    # Second attempt: with browser cookies
    if ! download_audio "true" >&2; then
        "$JQ" -n '{status: "error", message: "Download failed (tried with and without cookies)"}'
        exit 1
    fi
fi

# Find the downloaded file in temp directory (any audio format)
TEMP_FILE=""
for ext in m4a webm opus ogg mp3 aac wav; do
    TEMP_FILE=$(ls -t "$TEMP_DIR"/*."$ext" 2>/dev/null | head -1)
    [ -n "$TEMP_FILE" ] && break
done

if [ -n "$TEMP_FILE" ] && [ -f "$TEMP_FILE" ]; then
    # Get the extension from the downloaded file
    EXT="${TEMP_FILE##*.}"

    # Rename to unified format: {id}__{title}.{ext}
    AUDIO_FILE="$OUTPUT_DIR/${BASENAME}.${EXT}"
    mv "$TEMP_FILE" "$AUDIO_FILE"

    # Extract metadata fields for output
    META_VIDEO_ID=$(echo "$EXISTING_META" | "$JQ" -r '.video_id // empty')
    META_TITLE=$(echo "$EXISTING_META" | "$JQ" -r '.title // empty')
    META_CHANNEL=$(echo "$EXISTING_META" | "$JQ" -r '.channel // empty')
    META_URL=$(echo "$EXISTING_META" | "$JQ" -r '.url // empty')
    META_DURATION=$(echo "$EXISTING_META" | "$JQ" -r '.duration_string // empty')

    "$JQ" -n \
        --arg status "success" \
        --arg file_path "$AUDIO_FILE" \
        --arg file_size "$(ls -lh "$AUDIO_FILE" | awk '{print $5}')" \
        --argjson cached false \
        --arg video_id "$META_VIDEO_ID" \
        --arg title "$META_TITLE" \
        --arg channel "$META_CHANNEL" \
        --arg url "$META_URL" \
        --arg duration_string "$META_DURATION" \
        '{
            status: $status,
            file_path: $file_path,
            file_size: $file_size,
            cached: $cached,
            video_id: $video_id,
            title: $title,
            channel: $channel,
            url: $url,
            duration_string: $duration_string
        }'
else
    "$JQ" -n '{status: "error", message: "Download completed but file not found"}'
    exit 1
fi
