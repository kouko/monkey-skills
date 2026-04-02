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

QUERY="$1"
COUNT="${2:-10}"
MODE="${3:-fast}"  # fast (default) or full

if [ -z "$QUERY" ]; then
    echo "Usage: search.sh <query> [count] [mode]"
    echo "  mode: fast (default, quick but limited metadata)"
    echo "        full (slower but includes upload_date, description, live_status)"
    exit 1
fi

# Build yt-dlp options based on mode
if [ "$MODE" = "full" ]; then
    # Full mode: no --flat-playlist, slower but complete metadata
    YT_OPTS="--dump-json"
else
    # Fast mode: use --flat-playlist, faster but missing some fields
    YT_OPTS="--dump-json --flat-playlist"
fi

# Search and format results (aligned with channel-latest output format)
RESULT=$("$YT_DLP" "ytsearch${COUNT}:${QUERY}" \
    $YT_OPTS "${FFMPEG_ARGS[@]}" 2>/dev/null | \
    "$JQ" -s 'map({
        video_id: .id,
        title,
        url: .webpage_url,
        channel,
        channel_url,
        duration_string,
        view_count,
        upload_date,
        live_status,
        availability,
        description: (.description // "" | .[0:200])
    })')

# Write metadata for each video to centralized store
mkdir -p "$META_DIR"
echo "$RESULT" | "$JQ" -c '.[]' | while read -r line; do
    VIDEO_ID=$(echo "$line" | "$JQ" -r '.video_id')
    TITLE=$(echo "$line" | "$JQ" -r '.title')
    UPLOAD_DATE=$(echo "$line" | "$JQ" -r '.upload_date // empty')

    # Skip if no upload_date (fast mode results lack it)
    if [ -z "$UPLOAD_DATE" ]; then
        continue
    fi

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
        source: "search",
        partial: true,
        fetched_at: (now | todate)
    }')

    write_or_merge_meta "$META_DIR/$BASENAME.meta.json" "$META_JSON" "true"
done

# Output the result wrapped in status object (consistent with other skills)
"$JQ" -n --argjson videos "$RESULT" '{status: "success", videos: $videos}'
