#!/bin/bash
set -e

# Load dependencies
source "$(dirname "$0")/_utility__ensure_ytdlp.sh"
source "$(dirname "$0")/_utility__ensure_jq.sh"
source "$(dirname "$0")/_utility__ensure_ffmpeg.sh" 2>/dev/null || true
source "$(dirname "$0")/_utility__naming.sh"

# Build --ffmpeg-location args if ffmpeg is available
FFMPEG_ARGS=()
if [ -n "$FFMPEG_DIR" ]; then
    FFMPEG_ARGS=(--ffmpeg-location "$FFMPEG_DIR")
fi

CHANNEL="$1"
LIMIT="${2:-10}"
TYPE="${3:-all}"

if [ -z "$CHANNEL" ]; then
    "$JQ" -n --arg status "error" \
        --arg message "Usage: channel-latest.sh <channel_url|@handle> [limit] [type]" \
        '{status: $status, message: $message}'
    exit 1
fi

# Detect if input is a video URL and extract channel URL
if [[ "$CHANNEL" == *"youtube.com/watch"* ]] || \
   [[ "$CHANNEL" == *"youtube.com/shorts/"* ]] || \
   [[ "$CHANNEL" == *"youtu.be/"* ]]; then
    # Extract channel URL from video
    CHANNEL_BASE=$("$YT_DLP" "${FFMPEG_ARGS[@]}" --print channel_url "$CHANNEL" 2>/dev/null)
    if [ -z "$CHANNEL_BASE" ]; then
        "$JQ" -n --arg status "error" \
            --arg message "Could not extract channel from video URL" \
            '{status: $status, message: $message}'
        exit 1
    fi
# Normalize channel base URL (without tab)
elif [[ "$CHANNEL" == @* ]]; then
    CHANNEL_BASE="https://www.youtube.com/$CHANNEL"
elif [[ "$CHANNEL" != http* ]]; then
    CHANNEL_BASE="https://www.youtube.com/@$CHANNEL"
else
    # Remove any trailing tab path
    CHANNEL_BASE="${CHANNEL%/videos}"
    CHANNEL_BASE="${CHANNEL_BASE%/shorts}"
    CHANNEL_BASE="${CHANNEL_BASE%/streams}"
    CHANNEL_BASE="${CHANNEL_BASE%/podcasts}"
fi

# Fetch channel info (name and URL) from the first video
# This is needed because --flat-playlist on channel tabs doesn't include channel info
CHANNEL_INFO=$("$YT_DLP" "${FFMPEG_ARGS[@]}" --print channel --print channel_url --playlist-items 1 "$CHANNEL_BASE/videos" 2>/dev/null || echo "")
CHANNEL_NAME=$(echo "$CHANNEL_INFO" | head -1)
CHANNEL_URL=$(echo "$CHANNEL_INFO" | tail -1)

# Function to fetch from a single tab
fetch_tab() {
    local tab_url="$1"
    local limit="$2"
    local filter="$3"

    if [ -n "$filter" ]; then
        "$YT_DLP" --dump-json --flat-playlist \
            --playlist-items "1:$limit" \
            --match-filters "$filter" \
            "${FFMPEG_ARGS[@]}" \
            "$tab_url" 2>/dev/null || echo ""
    else
        "$YT_DLP" --dump-json --flat-playlist \
            --playlist-items "1:$limit" \
            "${FFMPEG_ARGS[@]}" \
            "$tab_url" 2>/dev/null || echo ""
    fi
}

# Handle different types
case "$TYPE" in
    videos)
        # Regular videos from /videos tab
        RESULT=$(fetch_tab "$CHANNEL_BASE/videos" "$LIMIT" "")
        ;;
    live)
        # Livestreams: use /streams tab (official YouTube classification)
        RESULT=$(fetch_tab "$CHANNEL_BASE/streams" "$LIMIT" "")
        ;;
    shorts)
        # Shorts: use /shorts tab (official YouTube classification)
        RESULT=$(fetch_tab "$CHANNEL_BASE/shorts" "$LIMIT" "")
        ;;
    podcasts)
        # Podcasts: use /podcasts tab
        RESULT=$(fetch_tab "$CHANNEL_BASE/podcasts" "$LIMIT" "")
        ;;
    all|*)
        # Fetch from all 4 tabs and merge
        # Fetch more items per tab to ensure we have enough after dedup
        FETCH_LIMIT=$((LIMIT * 2))

        VIDEOS=$(fetch_tab "$CHANNEL_BASE/videos" "$FETCH_LIMIT" "")
        SHORTS=$(fetch_tab "$CHANNEL_BASE/shorts" "$FETCH_LIMIT" "")
        STREAMS=$(fetch_tab "$CHANNEL_BASE/streams" "$FETCH_LIMIT" "")
        PODCASTS=$(fetch_tab "$CHANNEL_BASE/podcasts" "$FETCH_LIMIT" "")

        # Merge all results
        RESULT=""
        [ -n "$VIDEOS" ] && RESULT="$RESULT$VIDEOS"$'\n'
        [ -n "$SHORTS" ] && RESULT="$RESULT$SHORTS"$'\n'
        [ -n "$STREAMS" ] && RESULT="$RESULT$STREAMS"$'\n'
        [ -n "$PODCASTS" ] && RESULT="$RESULT$PODCASTS"$'\n'

        # Remove trailing newline
        RESULT="${RESULT%$'\n'}"
        ;;
esac

if [ -z "$RESULT" ]; then
    "$JQ" -n --arg status "error" \
        --arg message "No content found for this channel" \
        '{status: $status, message: $message}'
    exit 1
fi

# Parse, deduplicate, sort, and limit results
# Inject channel info since --flat-playlist on channel tabs doesn't include it
FINAL_OUTPUT=$(echo "$RESULT" | "$JQ" -s --argjson limit "$LIMIT" \
    --arg channel_name "$CHANNEL_NAME" --arg channel_url "$CHANNEL_URL" '
    map({
        video_id: .id,
        title,
        url: .webpage_url,
        channel: $channel_name,
        channel_url: $channel_url,
        duration_string,
        view_count,
        upload_date,
        live_status,
        availability,
        description: (.description // "" | .[0:200])
    })
    | unique_by(.video_id)
    | sort_by(.upload_date) | reverse
    | .[:$limit]
')

# Write metadata for each video to centralized store (partial data, won't overwrite complete)
mkdir -p "$META_DIR"
echo "$FINAL_OUTPUT" | "$JQ" -c '.[]' | while read -r line; do
    VIDEO_ID=$(echo "$line" | "$JQ" -r '.video_id')
    TITLE=$(echo "$line" | "$JQ" -r '.title')
    UPLOAD_DATE=$(echo "$line" | "$JQ" -r '.upload_date')
    BASENAME=$(make_basename "$UPLOAD_DATE" "$VIDEO_ID")

    META_JSON=$(echo "$line" | "$JQ" '{
        video_id,
        title,
        url,
        channel,
        channel_url,
        duration_string,
        view_count,
        upload_date,
        live_status,
        availability,
        description,
        source: "channel-latest",
        partial: true,
        fetched_at: (now | todate)
    }')

    # partial data won't overwrite complete data
    write_or_merge_meta "$META_DIR/$BASENAME.meta.json" "$META_JSON" "true"
done

# Output the final JSON array
echo "$FINAL_OUTPUT"
