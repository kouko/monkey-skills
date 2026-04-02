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

URL="$1"
BROWSER="${2:-}"  # Optional: specify browser (chrome, firefox, safari, etc.)

if [ -z "$URL" ]; then
    "$JQ" -n '{status: "error", message: "Usage: info.sh <url> [browser]"}'
    exit 1
fi

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

# Fetch info with optional cookie authentication
fetch_info() {
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

    "$YT_DLP" -j --no-download "${cookie_args[@]}" "${FFMPEG_ARGS[@]}" "$URL" 2>/dev/null
}

# Pre-check: determine if we should use cookies first based on existing metadata
USE_COOKIES_FIRST="false"
VIDEO_ID_FROM_URL=$(extract_video_id_from_url "$URL")
if [ -n "$VIDEO_ID_FROM_URL" ] && check_needs_auth "$VIDEO_ID_FROM_URL"; then
    echo "[INFO] Known restricted video, using cookies directly..." >&2
    USE_COOKIES_FIRST="true"
fi

# Fetch info based on pre-check result
if [ "$USE_COOKIES_FIRST" = "true" ]; then
    RAW_META=$(fetch_info "true") || RAW_META=""
else
    # First attempt: without authentication
    RAW_META=$(fetch_info "false") || RAW_META=""
    if [ -z "$RAW_META" ]; then
        echo "[INFO] First attempt failed, retrying with browser cookies..." >&2
        # Second attempt: with browser cookies
        RAW_META=$(fetch_info "true") || RAW_META=""
    fi
fi

if [ -z "$RAW_META" ]; then
    "$JQ" -n '{status: "error", message: "Failed to fetch video info (tried with and without cookies)"}'
    exit 1
fi

# Extract video ID, title, and upload_date for basename
VIDEO_ID=$(echo "$RAW_META" | "$JQ" -r '.id')
TITLE=$(echo "$RAW_META" | "$JQ" -r '.title')
UPLOAD_DATE=$(echo "$RAW_META" | "$JQ" -r '.upload_date')
BASENAME=$(make_basename "$UPLOAD_DATE" "$VIDEO_ID")

# Build metadata JSON for storage (complete data)
META_JSON=$(echo "$RAW_META" | "$JQ" '{
    video_id: .id,
    title,
    url: .webpage_url,
    channel,
    channel_url,
    duration_string,
    view_count,
    upload_date,
    description: .description[0:500],
    language,
    availability,
    has_subtitles: ((.subtitles | keys | length) > 0),
    subtitle_languages: (.subtitles | keys // []),
    has_auto_captions: ((.automatic_captions | keys | length) > 0),
    auto_caption_count: (.automatic_captions | keys | length // 0),
    source: "get-info",
    partial: false,
    fetched_at: (now | todate)
}')

# Write or merge metadata (complete data always updates)
write_or_merge_meta "$META_DIR/$BASENAME.meta.json" "$META_JSON" "false"

# Output JSON
echo "$RAW_META" | "$JQ" '{
    video_id: .id,
    title,
    url: .webpage_url,
    channel,
    channel_url,
    duration_string,
    view_count,
    upload_date,
    language,
    availability,
    description: .description[0:1000],
    has_subtitles: ((.subtitles | keys | length) > 0),
    subtitle_languages: (.subtitles | keys // []),
    has_auto_captions: ((.automatic_captions | keys | length) > 0),
    auto_caption_count: (.automatic_captions | keys | length // 0)
}'
