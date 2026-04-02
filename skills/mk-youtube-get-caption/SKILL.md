---
name: mk-youtube-get-caption
description: Download YouTube video subtitles. Use when user wants to get captions or subtitles from a video.
license: MIT
metadata:
  version: 1.2.1
  author: kouko
  tags:
    - youtube
    - caption
    - subtitle
compatibility:
  claude-code: ">=1.0.0"
---

# YouTube Caption Download

Download video subtitles and display content. Automatically detects video's original language and distinguishes between manual and auto-generated subtitles.

## Quick Start

```
/mk-youtube-get-caption <URL> [language|auto] [--force]
```

## Examples

- `/mk-youtube-get-caption https://youtube.com/watch?v=xxx` - Auto-detect original language
- `/mk-youtube-get-caption https://youtube.com/watch?v=xxx auto` - Explicitly use original language
- `/mk-youtube-get-caption https://youtube.com/watch?v=xxx ja` - Download Japanese subtitles
- `/mk-youtube-get-caption https://youtube.com/watch?v=xxx "zh-TW,en"` - Language priority list

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| URL | Yes | - | YouTube video URL |
| language | No | auto | Language code or priority list |
| --force | No | false | Force re-download even if cached file exists |

## Language Options

| Value | Behavior |
|-------|----------|
| (empty) | Auto-detect video's original language |
| `auto` | Same as empty |
| `en`, `ja`, etc. | Specific language code |
| `"en,ja,zh-TW"` | Comma-separated priority list |

## How it Works

1. Execute: `{baseDir}/scripts/caption.sh "<URL>" "<language>"`
2. If no language specified, detect video's original language
3. Try to download manual (author-uploaded) subtitles first
4. If unavailable, fall back to auto-generated subtitles
5. Parse JSON output to get file path and metadata
6. Use Read tool to get subtitle content if needed

## Output Format

Success:
```json
{
  "status": "success",
  "file_path": "{baseDir}/data/20091025__VIDEO_ID.en.srt",
  "text_file_path": "{baseDir}/data/20091025__VIDEO_ID.en.txt",
  "language": "en",
  "subtitle_type": "manual",
  "char_count": 30287,
  "line_count": 1555,
  "text_char_count": 25000,
  "text_line_count": 800,
  "cached": false,
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Cache hit** (returns existing file):
```json
{
  "status": "success",
  "file_path": "{baseDir}/data/20091025__VIDEO_ID.en.srt",
  "subtitle_type": "cached",
  "cached": true,
  ...
}
```

Error:
```json
{
  "status": "error",
  "message": "No subtitles found (this video may not have subtitles)"
}
```

## Output Fields

| Field | Description |
|-------|-------------|
| `file_path` | Absolute path to the downloaded SRT file |
| `text_file_path` | Absolute path to plain text file (no timestamps) |
| `language` | Detected language code of the downloaded subtitle |
| `subtitle_type` | `manual` (author-uploaded) or `auto-generated` (YouTube AI) |
| `char_count` | Number of characters in the SRT file |
| `line_count` | Number of lines in the SRT file |
| `text_char_count` | Number of characters in the plain text file |
| `text_line_count` | Number of lines in the plain text file |
| `video_id` | YouTube video ID |
| `title` | Video title |
| `channel` | Channel name |
| `url` | Full video URL |

## Filename Format

Files use unified naming with date prefix: `{YYYYMMDD}__{video_id}.{lang}.{ext}`

Example: `20091025__dQw4w9WgXcQ.en.srt`

## Notes

- **File caching**: If caption file already exists for this video/language, it will be reused (returns `cached: true`)
- **Force refresh**: Use `--force` flag to re-download even if cached file exists
- Uses system yt-dlp/jq if available, otherwise auto-downloads on first run
- Some videos may not have subtitles
- Manual subtitles are prioritized over auto-generated ones
- Auto-generated subtitles may be less accurate

## Next Step

After downloading the caption, invoke `/mk-youtube-transcript-summarize` with the `text_file_path` from the output to generate a structured summary:

```
/mk-youtube-transcript-summarize <text_file_path>
```

**IMPORTANT**: Always use the Skill tool to invoke `/mk-youtube-transcript-summarize`. Do NOT generate summaries directly without loading the skill — it contains critical rules for compression ratio, section structure, data preservation, and language handling.
