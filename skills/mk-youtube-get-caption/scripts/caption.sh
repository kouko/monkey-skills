#!/bin/bash
set -e

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
LANG="${2:-}"  # Empty means auto-detect original language
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="$SKILL_DIR/data"

if [ -z "$URL" ]; then
    "$JQ" -n --arg status "error" \
        --arg message "Usage: caption.sh <url> [lang|auto]" \
        '{status: $status, message: $message}'
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Browser argument (optional, can be specified after lang)
BROWSER="${3:-}"

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
    "$JQ" -n --arg status "error" \
        --arg message "Could not extract video ID (tried with and without cookies)" \
        '{status: $status, message: $message}'
    exit 1
fi

# Get remaining metadata using the determined cookie strategy
TITLE=$(fetch_metadata "$NEED_COOKIES" "title") || TITLE=""
UPLOAD_DATE=$(fetch_metadata "$NEED_COOKIES" "upload_date") || UPLOAD_DATE=""

BASENAME=$(make_basename "$UPLOAD_DATE" "$VIDEO_ID")

# Read existing metadata or create minimal entry
EXISTING_META=$(read_meta "$VIDEO_ID")
if [ -z "$EXISTING_META" ]; then
    # Fetch minimal metadata for centralized store
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
        --arg source "caption" \
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

# --- Detect primary language (once) ---
if [ -z "$LANG" ] || [ "$LANG" = "auto" ]; then
    PRIMARY_LANG=$(fetch_metadata "$NEED_COOKIES" "language") || PRIMARY_LANG=""
    if [ -z "$PRIMARY_LANG" ] || [ "$PRIMARY_LANG" = "NA" ] || [ "$PRIMARY_LANG" = "null" ]; then
        PRIMARY_LANG=""
        # Tier 1: First subtitle language from centralized metadata
        if [ -n "$EXISTING_META" ]; then
            PRIMARY_LANG=$(echo "$EXISTING_META" | "$JQ" -r '
                (.subtitle_languages // []) | if length > 0 then .[0] else empty end
            ' 2>/dev/null) || PRIMARY_LANG=""
        fi
        # Tier 2: First manual subtitle language from yt-dlp
        if [ -z "$PRIMARY_LANG" ]; then
            PRIMARY_LANG=$(fetch_metadata "$NEED_COOKIES" '%(subtitles)#j' | "$JQ" -r '
                keys | if length > 0 then .[0] else empty end
            ' 2>/dev/null) || PRIMARY_LANG=""
        fi
        # No Tier 3 — fallback handled by download strategy
    fi
else
    PRIMARY_LANG="$LANG"
fi

# --- Cache check (unless --force) ---
if [ "$FORCE_REFRESH" != "true" ]; then
    # If specific language detected, check for that language
    if [ -n "$PRIMARY_LANG" ]; then
        EXISTING_SRT=$(find_file_by_id "$OUTPUT_DIR" "$VIDEO_ID" "*.${PRIMARY_LANG}.srt")
    else
        # Otherwise check for any srt file for this video
        EXISTING_SRT=$(find_file_by_id "$OUTPUT_DIR" "$VIDEO_ID" "*.srt")
    fi
    if [ -n "$EXISTING_SRT" ] && [ -f "$EXISTING_SRT" ]; then
        EXISTING_TXT="${EXISTING_SRT%.srt}.txt"
        echo "[INFO] Using cached caption: $EXISTING_SRT" >&2

        # Extract language from filename (e.g., *__.en.srt -> en)
        DETECTED_LANG=$(LC_ALL=en_US.UTF-8 basename "$EXISTING_SRT" | LC_ALL=en_US.UTF-8 sed 's/.*\.\([^.]*\)\.srt$/\1/')

        # Get SRT file statistics
        CHAR_COUNT=$(wc -c < "$EXISTING_SRT" | tr -d ' ')
        LINE_COUNT=$(wc -l < "$EXISTING_SRT" | tr -d ' ')

        # Get text file statistics (if exists)
        TEXT_CHAR_COUNT=0
        TEXT_LINE_COUNT=0
        if [ -f "$EXISTING_TXT" ]; then
            TEXT_CHAR_COUNT=$(wc -c < "$EXISTING_TXT" | tr -d ' ')
            TEXT_LINE_COUNT=$(wc -l < "$EXISTING_TXT" | tr -d ' ')
        fi

        # Extract metadata fields for output
        META_VIDEO_ID=$(echo "$EXISTING_META" | "$JQ" -r '.video_id // empty')
        META_TITLE=$(echo "$EXISTING_META" | "$JQ" -r '.title // empty')
        META_CHANNEL=$(echo "$EXISTING_META" | "$JQ" -r '.channel // empty')
        META_URL=$(echo "$EXISTING_META" | "$JQ" -r '.url // empty')

        "$JQ" -n \
            --arg status "success" \
            --arg file_path "$EXISTING_SRT" \
            --arg text_file_path "$EXISTING_TXT" \
            --arg language "$DETECTED_LANG" \
            --arg subtitle_type "cached" \
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
                status: $status,
                file_path: $file_path,
                text_file_path: $text_file_path,
                language: $language,
                subtitle_type: $subtitle_type,
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
if [ "$FORCE_REFRESH" = "true" ]; then
    echo "[INFO] Force refresh enabled, removing existing files..." >&2
    rm -f "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.srt "$OUTPUT_DIR/"*"__${VIDEO_ID}."*.txt 2>/dev/null || true
fi

# Download subtitles with optional cookie authentication
download_subtitles() {
    local sub_type="$1"    # "manual" or "auto"
    local lang="$2"        # language code or "" for yt-dlp fallback
    local cookie_args=()
    local sub_lang_args=()

    if [ "$NEED_COOKIES" = "true" ] && [ -n "$BROWSER" ]; then
        cookie_args=(--cookies-from-browser "$BROWSER")
    elif [ "$NEED_COOKIES" = "true" ]; then
        for browser in chrome firefox safari edge brave; do
            local found_browser
            if found_browser=$(try_browser_cookies "$browser"); then
                cookie_args=(--cookies-from-browser "$found_browser")
                echo "[INFO] Using cookies from: $found_browser" >&2
                break
            fi
        done
    fi

    if [ -n "$lang" ]; then
        sub_lang_args=(--sub-lang "$lang")
    fi

    if [ "$sub_type" = "auto" ]; then
        "$YT_DLP" --write-auto-subs \
                  "${sub_lang_args[@]}" \
                  --skip-download --convert-subs srt \
                  "${cookie_args[@]}" \
                  "${FFMPEG_ARGS[@]}" \
                  -o "$TEMP_DIR/%(id)s" "$URL" >&2 || true
    else
        "$YT_DLP" --write-subs \
                  "${sub_lang_args[@]}" \
                  --skip-download --convert-subs srt \
                  "${cookie_args[@]}" \
                  "${FFMPEG_ARGS[@]}" \
                  -o "$TEMP_DIR/%(id)s" "$URL" >&2 || true
    fi
}

# Download to temp location first, then rename
TEMP_DIR=$(mktemp -d)
cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT

TEMP_SRT=""
SUBTITLE_TYPE=""

# Step 1-2: Primary language (if detected)
if [ -n "$PRIMARY_LANG" ]; then
    # Step 1: Manual subs in primary language
    echo "[INFO] Step 1: Trying manual subtitles for '$PRIMARY_LANG'..." >&2
    download_subtitles "manual" "$PRIMARY_LANG"
    TEMP_SRT=$(ls -t "$TEMP_DIR"/*.srt 2>/dev/null | head -1)
    SUBTITLE_TYPE="manual"

    # Step 2: Auto subs in primary language
    if [ -z "$TEMP_SRT" ] || [ ! -f "$TEMP_SRT" ]; then
        echo "[INFO] Step 2: Trying auto-generated subtitles for '$PRIMARY_LANG'..." >&2
        download_subtitles "auto" "$PRIMARY_LANG"
        TEMP_SRT=$(ls -t "$TEMP_DIR"/*.srt 2>/dev/null | head -1)
        SUBTITLE_TYPE="auto-generated"
    fi
fi

# Step 3: yt-dlp built-in fallback (no --sub-lang)
if [ -z "$TEMP_SRT" ] || [ ! -f "$TEMP_SRT" ]; then
    # 3a: Manual fallback
    echo "[INFO] Step 3a: Trying manual subtitles (yt-dlp fallback)..." >&2
    download_subtitles "manual" ""
    TEMP_SRT=$(ls -t "$TEMP_DIR"/*.srt 2>/dev/null | head -1)
    SUBTITLE_TYPE="manual"

    # 3b: Auto fallback
    if [ -z "$TEMP_SRT" ] || [ ! -f "$TEMP_SRT" ]; then
        echo "[INFO] Step 3b: Trying auto-generated subtitles (yt-dlp fallback)..." >&2
        download_subtitles "auto" ""
        TEMP_SRT=$(ls -t "$TEMP_DIR"/*.srt 2>/dev/null | head -1)
        SUBTITLE_TYPE="auto-generated"
    fi
fi

if [ -n "$TEMP_SRT" ] && [ -f "$TEMP_SRT" ]; then
    # Extract language from filename (e.g., VIDEO_ID.en.srt -> en)
    DETECTED_LANG=$(LC_ALL=en_US.UTF-8 basename "$TEMP_SRT" | LC_ALL=en_US.UTF-8 sed 's/.*\.\([^.]*\)\.srt$/\1/')

    # Rename to unified format: {id}__{title}.{lang}.srt
    SRT_FILE="$OUTPUT_DIR/${BASENAME}.${DETECTED_LANG}.srt"
    mv "$TEMP_SRT" "$SRT_FILE"

    # Generate plain text version (remove sequence numbers, timestamps, empty lines)
    TEXT_FILE="${SRT_FILE%.srt}.txt"
    LC_ALL=en_US.UTF-8 sed '/^[0-9]*$/d; /-->/d; /^[[:space:]]*$/d' "$SRT_FILE" | uniq > "$TEXT_FILE"

    # Get SRT file statistics
    CHAR_COUNT=$(wc -c < "$SRT_FILE" | tr -d ' ')
    LINE_COUNT=$(wc -l < "$SRT_FILE" | tr -d ' ')

    # Get text file statistics
    TEXT_CHAR_COUNT=$(wc -c < "$TEXT_FILE" | tr -d ' ')
    TEXT_LINE_COUNT=$(wc -l < "$TEXT_FILE" | tr -d ' ')

    # Extract metadata fields for output
    META_VIDEO_ID=$(echo "$EXISTING_META" | "$JQ" -r '.video_id // empty')
    META_TITLE=$(echo "$EXISTING_META" | "$JQ" -r '.title // empty')
    META_CHANNEL=$(echo "$EXISTING_META" | "$JQ" -r '.channel // empty')
    META_URL=$(echo "$EXISTING_META" | "$JQ" -r '.url // empty')

    # Output JSON with both file paths and metadata
    "$JQ" -n \
        --arg status "success" \
        --arg file_path "$SRT_FILE" \
        --arg text_file_path "$TEXT_FILE" \
        --arg language "$DETECTED_LANG" \
        --arg subtitle_type "$SUBTITLE_TYPE" \
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
            status: $status,
            file_path: $file_path,
            text_file_path: $text_file_path,
            language: $language,
            subtitle_type: $subtitle_type,
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
else
    "$JQ" -n \
        --arg status "error" \
        --arg message "No subtitles found (this video may not have subtitles)" \
        '{status: $status, message: $message}'
    exit 1
fi
