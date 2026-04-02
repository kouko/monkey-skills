# YouTube Info Skill

Get detailed information about a YouTube video.

## Overview

This skill extracts metadata from a YouTube video URL using `yt-dlp` and formats it as JSON. It's useful for getting video details before downloading or summarizing content.

## File Structure

```
mk-youtube-get-info/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── bin/                  # Auto-downloaded binaries (initially empty)
│   └── .gitkeep
└── scripts/
    ├── _utility__ensure_ytdlp.sh  # Ensures yt-dlp is available
    ├── _utility__ensure_jq.sh     # Ensures jq is available
    ├── _utility__naming.sh        # Unified naming and metadata functions
    └── info.sh           # Main info script
```

## Dependencies

| Dependency | Purpose | Auto-download |
|------------|---------|---------------|
| yt-dlp | Video metadata extraction | Yes |
| jq | JSON formatting | Yes |
| curl/wget | Download binaries | Required (pre-installed) |

## Dependency Management

### `_ensure_ytdlp.sh`

```
Priority:
1. System-installed yt-dlp (command -v yt-dlp)
2. Previously downloaded binary in bin/
3. Auto-download from GitHub releases
```

### `_ensure_jq.sh`

```
Priority:
1. System-installed jq (command -v jq)
2. Previously downloaded binary in bin/
3. Auto-download based on OS + CPU architecture
```

## Script: `info.sh`

### Usage

```bash
./scripts/info.sh "<URL>"
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| URL | Yes | YouTube video URL |

### Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

### Output Format

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "channel": "Channel Name",
  "channel_url": "https://www.youtube.com/channel/UC...",
  "duration_string": "10:23",
  "view_count": 1234567,
  "upload_date": "20240101",
  "language": "en",
  "description": "Video description (truncated to 1000 chars)...",
  "has_subtitles": true,
  "subtitle_languages": ["en", "ja", "zh-TW"],
  "has_auto_captions": true,
  "auto_caption_count": 15
}
```

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| video_id | string | YouTube video ID |
| title | string | Video title |
| url | string | Full video URL |
| channel | string | Channel name |
| channel_url | string | Channel URL |
| duration_string | string | Duration in HH:MM:SS or MM:SS format |
| view_count | number | Total view count |
| upload_date | string | Upload date in YYYYMMDD format |
| language | string | Video's original language (ISO 639-1 code, e.g., en, ja, ko) |
| description | string | Description (max 1000 characters) |
| has_subtitles | boolean | Whether manual subtitles are available |
| subtitle_languages | array | List of available subtitle language codes |
| has_auto_captions | boolean | Whether auto-generated captions are available |
| auto_caption_count | number | Number of auto-caption languages available |

## Examples

```bash
# Get info for a video
./scripts/info.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Using short URL
./scripts/info.sh "https://youtu.be/dQw4w9WgXcQ"
```

## How It Works

```
┌─────────────────┐
│    info.sh      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Load dependencies│
│ _ensure_ytdlp   │
│ _ensure_jq      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ yt-dlp -j       │
│ --no-download   │
│ Extract JSON    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ jq transform    │
│ Select fields   │
│ Truncate desc   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ JSON output     │
└─────────────────┘
```

## Use Cases

1. **Pre-download check**: Verify video metadata before downloading
2. **Content summarization**: Get description for AI summarization
3. **Analytics**: Extract view counts and upload dates
4. **Playlist building**: Gather video info for curation

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Empty output | Invalid URL | Check URL format |
| `ERROR: Video unavailable` | Private/deleted video | Try different video |
| Network error | Connection issue | Check internet connection |

## License

MIT
