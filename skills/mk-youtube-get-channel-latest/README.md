# YouTube Get Channel Latest Skill

Get the latest videos, livestreams, shorts, or podcasts from a YouTube channel.

## Overview

This skill retrieves the most recent content from a YouTube channel using `yt-dlp`. It supports:
- **Multiple input formats**: @handle, username, channel URL, or **video URL**
- **Content type filtering**: videos, live, shorts, podcasts
- **Configurable result limits**

When given a video URL, it automatically extracts the channel and fetches the latest content from that creator.

## File Structure

```
mk-youtube-get-channel-latest/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── bin/                  # Auto-downloaded binaries (initially empty)
│   └── .gitkeep
└── scripts/
    ├── _utility__ensure_ytdlp.sh  # Ensures yt-dlp is available
    ├── _utility__ensure_jq.sh     # Ensures jq is available
    ├── _utility__naming.sh        # Unified naming and metadata functions
    └── channel-latest.sh # Main script
```

## Dependencies

| Dependency | Purpose | Auto-download |
|------------|---------|---------------|
| yt-dlp | Channel data extraction | Yes |
| jq | JSON output formatting | Yes |
| curl/wget | Download binaries | Required (pre-installed) |

## Script: `channel-latest.sh`

### Usage

```bash
./scripts/channel-latest.sh "<channel>" [limit] [type]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| channel | Yes | - | Channel URL, @handle, username, or **video URL** |
| limit | No | 10 | Number of items to retrieve (1-50) |
| type | No | all | Content type filter |

### Type Options

| Type | Tab URL | Description |
|------|---------|-------------|
| `all` | All 4 tabs | Fetches from all tabs, deduplicates, sorts by date |
| `videos` | `/videos` | Regular videos |
| `live` | `/streams` | Livestreams (current, past, upcoming) |
| `shorts` | `/shorts` | YouTube Shorts |
| `podcasts` | `/podcasts` | Podcast episodes |

### Channel Input Formats

| Input | Behavior |
|-------|----------|
| `@handle` | → `https://www.youtube.com/@handle` |
| `username` | → `https://www.youtube.com/@username` |
| Channel URL | Trailing tab path removed |
| **Video URL** | Extract channel URL via yt-dlp |
| **Shorts URL** | Extract channel URL via yt-dlp |
| **youtu.be URL** | Extract channel URL via yt-dlp |

### Output Format (JSON)

**Success:**
```json
[
  {
    "video_id": "dQw4w9WgXcQ",
    "title": "Video Title",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "channel": "Channel Name",
    "channel_url": "https://www.youtube.com/channel/UC...",
    "duration_string": "3:32",
    "view_count": 1500000000,
    "upload_date": "20091025",
    "live_status": "not_live",
    "description": "First 200 chars..."
  }
]
```

**Error:**
```json
{
  "status": "error",
  "message": "No content found for this channel"
}
```

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| video_id | string | YouTube video ID |
| title | string | Video title |
| url | string | Full YouTube URL |
| channel | string | Channel name |
| channel_url | string | Channel URL |
| duration_string | string | Human-readable duration (e.g., "10:23") |
| view_count | number | View count (may be null for upcoming) |
| upload_date | string | Upload date in YYYYMMDD format |
| live_status | string | not_live, is_live, was_live, is_upcoming |
| description | string | First 200 characters of description |

## Examples

```bash
# Get latest 10 items from a channel (all types)
./scripts/channel-latest.sh "@GoogleDevelopers"

# Get latest 5 regular videos
./scripts/channel-latest.sh "@MKBHD" 5 videos

# Get latest 10 livestreams
./scripts/channel-latest.sh "@NASA" 10 live

# Get latest 20 shorts
./scripts/channel-latest.sh "@shorts" 20 shorts

# Get latest podcasts
./scripts/channel-latest.sh "https://www.youtube.com/@TED" 5 podcasts

# From a video URL - get latest from that video's channel
./scripts/channel-latest.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 5 videos

# From a short URL
./scripts/channel-latest.sh "https://youtu.be/dQw4w9WgXcQ" 5 all
```

## How It Works

```
┌─────────────────────────────┐
│     channel-latest.sh       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Load dependencies         │
│   _ensure_ytdlp.sh          │
│   _ensure_jq.sh             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Check input type          │
└──────────────┬──────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────────────┐
│ Video URL   │  │ Channel input       │
│ /watch?v=   │  │ @handle, username,  │
│ /shorts/    │  │ or channel URL      │
│ youtu.be/   │  │                     │
└──────┬──────┘  └──────────┬──────────┘
       │                    │
       ▼                    │
┌─────────────┐             │
│ yt-dlp      │             │
│ --print     │             │
│ channel_url │             │
└──────┬──────┘             │
       │                    │
       └────────┬───────────┘
                │
                ▼
┌─────────────────────────────┐
│   Normalize to base URL     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Check type parameter      │
└──────────────┬──────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────────────┐
│ Specific    │  │ type=all            │
│ type        │  │ Fetch all 4 tabs:   │
│             │  │ /videos, /shorts,   │
│ Fetch from  │  │ /streams, /podcasts │
│ single tab  │  └──────────┬──────────┘
└──────┬──────┘             │
       │                    ▼
       │         ┌─────────────────────┐
       │         │ Merge & deduplicate │
       │         │ Sort by upload_date │
       │         │ Take top N items    │
       │         └──────────┬──────────┘
       │                    │
       └────────┬───────────┘
                │
                ▼
┌─────────────────────────────┐
│   Format JSON output        │
│   Extract relevant fields   │
│   Truncate description      │
└─────────────────────────────┘
```

## Type Classification Logic

```
                         Type Parameter
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
  all                    Specific Type            (invalid)
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────┐     ┌─────────────┴─────────────┐        → all
│ Fetch   │     │             │             │
│ 4 tabs  │     ▼             ▼             ▼
│ /videos │  videos        shorts         live       podcasts
│ /shorts │     │             │             │           │
│/streams │     ▼             ▼             ▼           ▼
│/podcasts│  /videos      /shorts      /streams    /podcasts
│         │  (YouTube's   (YouTube's   (YouTube's  (YouTube's
│ Merge & │  official     official     official    official
│ Sort    │  Videos tab)  Shorts tab)  Live tab)   Podcasts)
└─────────┘
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `No content found` | Invalid channel or no matching content | Verify channel URL/handle |
| Empty result | Channel has no content of requested type | Try different type filter |
| Network error | Connection issues | Check internet connection |

## Use Cases

1. **Content monitoring**: Track new uploads from favorite channels
2. **Research**: Gather recent content from multiple channels
3. **Live tracking**: Find current and upcoming livestreams
4. **Shorts discovery**: Find short-form content from creators
5. **Podcast updates**: Get latest podcast episodes

## License

MIT
