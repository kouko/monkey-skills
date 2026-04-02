---
name: mk-youtube-get-info
description: Get YouTube video metadata (title, channel, duration, views, subtitle availability). Use when user wants video details or needs to check subtitle availability before summarization.
license: MIT
metadata:
  version: 1.0.2
  author: kouko
  tags:
    - youtube
    - info
    - summary
compatibility:
  claude-code: ">=1.0.0"
---

# YouTube Video Info

Get video details and generate content summary.

## Quick Start

```
/mk-youtube-get-info <URL> [browser]
```

## Examples

```bash
# Basic usage (auto-detects cookies if needed)
/mk-youtube-get-info https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Specify browser for cookie authentication
/mk-youtube-get-info https://www.youtube.com/watch?v=dQw4w9WgXcQ chrome
```

## How it Works

1. Execute: `{baseDir}/scripts/info.sh "<URL>"`
2. Parse JSON to get video metadata
3. Try to get subtitles for summarization
4. Generate summary based on subtitle content
5. If no subtitles, display video info only

## Output Format

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "channel": "Channel Name",
  "channel_url": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
  "duration_string": "10:30",
  "view_count": 1234567,
  "upload_date": "20240101",
  "language": "en",
  "availability": "public",
  "description": "Video description (first 500 chars)",
  "has_subtitles": true,
  "subtitle_languages": ["en", "ja", "zh-Hant"],
  "has_auto_captions": true,
  "auto_caption_count": 157
}
```

### Fields

| Field | Description |
|-------|-------------|
| `video_id` | YouTube video ID |
| `title` | Video title |
| `url` | Full video URL |
| `channel` | Channel name |
| `channel_url` | Channel URL |
| `duration_string` | Duration (e.g., "10:30") |
| `view_count` | Number of views |
| `upload_date` | Upload date (YYYYMMDD) |
| `language` | Primary language (ISO 639-1 code) |
| `availability` | Access level: `public`, `unlisted`, `members_only`, `subscriber_only`, `needs_auth`, `premium_only`, `private` |
| `description` | Video description (truncated to 500 chars) |
| `has_subtitles` | Whether manual subtitles exist |
| `subtitle_languages` | Array of available subtitle language codes |
| `has_auto_captions` | Whether auto-generated captions exist |
| `auto_caption_count` | Number of auto-generated caption languages |

### Centralized Metadata Store

This skill automatically saves video metadata to `/tmp/monkey_knowledge/youtube/meta/{YYYYMMDD}__{video_id}.meta.json`. This metadata can be accessed by downstream skills (caption, audio, transcribe, summary) to include video information in their outputs.

### Content Summary
(Generated from subtitle analysis)
- Key point 1
- Key point 2
- ...

## Notes

- Uses system yt-dlp/jq if available, otherwise auto-downloads on first run
- **Cookie Fallback**: If initial request fails, automatically retries with browser cookies (auto-detects Chrome, Firefox, Safari, Edge, Brave)
- **Browser Parameter**: Optionally specify `chrome`, `firefox`, `safari`, `edge`, or `brave` to use specific browser cookies

## Next Step

After obtaining video info, determine the summarization path based on subtitle availability:

- **If `has_subtitles: true` or `has_auto_captions: true`**: Invoke `/mk-youtube-get-caption` to download subtitles
- **If both are `false`**: Invoke `/mk-youtube-get-audio` to download audio for transcription

To generate a complete summary, always follow the full pipeline — do NOT skip directly to summarization without first obtaining a transcript through one of the above paths.
