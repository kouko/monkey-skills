# YouTube Caption Skill

Download and extract subtitles/captions from YouTube videos.

## Overview

This skill downloads subtitles from YouTube videos using `yt-dlp` and outputs JSON with file path and metadata. Use the Read tool to get the actual content. It supports:

- **Auto language detection**: Automatically detects video's original language
- **Subtitle type distinction**: Prioritizes manual subtitles over auto-generated
- **Multiple languages**: Supports language priority lists

## File Structure

```
mk-youtube-get-caption/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── bin/                  # Auto-downloaded binaries (initially empty)
│   └── .gitkeep
└── scripts/
    ├── _utility__ensure_ytdlp.sh  # Ensures yt-dlp is available
    ├── _utility__ensure_jq.sh     # Ensures jq is available
    ├── _utility__naming.sh        # Unified naming and metadata functions
    └── caption.sh        # Main caption script
```

## Dependencies

| Dependency | Purpose | Auto-download |
|------------|---------|---------------|
| yt-dlp | Subtitle download | Yes |
| jq | JSON output formatting | Yes |
| sed | Text processing | Pre-installed |
| curl/wget | Download binaries | Required (pre-installed) |

## Script: `caption.sh`

### Usage

```bash
./scripts/caption.sh "<URL>" [language|auto]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| URL | Yes | - | YouTube video URL |
| language | No | auto | Language code, priority list, or "auto" |

### Language Options

| Value | Behavior |
|-------|----------|
| (empty) | Auto-detect video's original language |
| `auto` | Same as empty - detect original language |
| `en`, `ja`, etc. | Specific language code |
| `"en,ja,zh-TW"` | Comma-separated priority list |

### Language Codes

| Code | Language |
|------|----------|
| en | English |
| ja | Japanese |
| zh-TW | Traditional Chinese (Taiwan) |
| zh-Hant | Traditional Chinese |
| zh-CN | Simplified Chinese |
| ko | Korean |
| es | Spanish |
| fr | French |
| de | German |

### Output Format (JSON)

**Success:**
```json
{
  "status": "success",
  "file_path": "{baseDir}/data/20240101__VIDEO_ID.en.srt",
  "text_file_path": "{baseDir}/data/20240101__VIDEO_ID.en.txt",
  "language": "en",
  "subtitle_type": "manual",
  "char_count": 30287,
  "line_count": 1555,
  "text_char_count": 25000,
  "text_line_count": 800,
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Error:**
```json
{
  "status": "error",
  "message": "No subtitles found (this video may not have subtitles)"
}
```

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" or "error" |
| file_path | string | Absolute path to SRT file |
| text_file_path | string | Absolute path to plain text file (no timestamps) |
| language | string | Detected language code |
| subtitle_type | string | "manual" (author-uploaded) or "auto-generated" (YouTube AI) |
| char_count | number | Number of characters in the SRT file |
| line_count | number | Number of lines in the SRT file |
| text_char_count | number | Number of characters in the plain text file |
| text_line_count | number | Number of lines in the plain text file |
| video_id | string | YouTube video ID |
| title | string | Video title |
| channel | string | Channel name |
| url | string | Video URL |
| message | string | Error message (only on failure) |

## Examples

```bash
# Auto-detect original language (recommended)
./scripts/caption.sh "https://www.youtube.com/watch?v=xxx"

# Explicitly use auto-detection
./scripts/caption.sh "https://www.youtube.com/watch?v=xxx" auto

# Download Japanese subtitles
./scripts/caption.sh "https://www.youtube.com/watch?v=xxx" ja

# Download with language priority
./scripts/caption.sh "https://www.youtube.com/watch?v=xxx" "zh-TW,zh-Hant,en"
```

## How It Works

```
┌─────────────────────┐
│     caption.sh      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Load dependencies  │
│  _ensure_ytdlp.sh   │
│  _ensure_jq.sh      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Language check     │
│  Empty/auto? → Get  │
│  original language  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Try manual subs    │
│  --write-subs       │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
  Found?      Not Found
     │           │
     ▼           ▼
┌─────────┐  ┌─────────────────┐
│ Manual  │  │ Try auto-subs   │
│ success │  │ --write-auto-   │
│         │  │ subs            │
└────┬────┘  └────────┬────────┘
     │                │
     └───────┬────────┘
             │
             ▼
┌─────────────────────┐
│  Generate .txt      │
│  (remove timestamps)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Output JSON with   │
│  both file paths    │
└─────────────────────┘
```

## Subtitle Priority

The script downloads subtitles in this order:

1. **Manual subtitles** (`--write-subs`): Human-created captions uploaded by video author
2. **Auto-generated** (`--write-auto-subs`): YouTube's AI-generated captions

The `subtitle_type` field in the output indicates which type was downloaded.

## Output Files

| Location | Purpose |
|----------|---------|
| `{baseDir}/data/{YYYYMMDD}__{video_id}.{lang}.srt` | Downloaded SRT subtitle files |
| `{baseDir}/data/{YYYYMMDD}__{video_id}.{lang}.txt` | Plain text version (no timestamps) |

Files are stored in the skill-local `data/` directory and persist across sessions.

## Use Cases

1. **Content summarization**: Extract text for AI summarization
2. **Translation**: Get subtitles in original language for translation
3. **Accessibility**: Create text versions of video content
4. **Research**: Extract quotes and content from videos
5. **Quality check**: Verify if manual or auto-generated subtitles are available

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `ERROR: No subtitles found` | Video has no captions | Use `/mk-youtube-get-audio` for speech-to-text |
| Empty output | Subtitle download failed | Check video URL and language |
| Wrong language | Requested language unavailable | Try different language code or use `auto` |

## Fallback Strategy

If a video has no subtitles:

1. Use `/mk-youtube-get-audio` to download audio
2. Use external speech-to-text service
3. Manually transcribe content

## License

MIT
