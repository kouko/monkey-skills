# YouTube Search Skill

Search YouTube videos by keyword and return structured results.

## Overview

This skill uses `yt-dlp` to search YouTube and returns video metadata in JSON format. It supports automatic dependency management - if `yt-dlp` or `jq` is not installed on the system, it will be downloaded automatically.

Search results are saved to the centralized metadata store (`/tmp/monkey_knowledge/youtube/meta/`) for use by other skills in the pipeline.

## File Structure

```
mk-youtube-search/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── bin/                  # Auto-downloaded binaries (initially empty)
│   └── .gitkeep
└── scripts/
    ├── _utility__ensure_ytdlp.sh  # Ensures yt-dlp is available
    ├── _utility__ensure_jq.sh     # Ensures jq is available
    ├── _utility__naming.sh        # Unified naming and metadata functions
    └── search.sh         # Main search script
```

## Dependencies

| Dependency | Purpose | Auto-download |
|------------|---------|---------------|
| yt-dlp | YouTube search | Yes |
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
3. Auto-download based on OS + CPU architecture:
   - macOS Intel: jq-macos-amd64
   - macOS ARM: jq-macos-arm64
   - Linux x64: jq-linux-amd64
   - Linux ARM: jq-linux-arm64
   - Windows: jq-win64.exe
```

## Script: `search.sh`

### Usage

```bash
./scripts/search.sh "<query>" [count] [mode]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| query | Yes | - | Search keywords |
| count | No | 10 | Number of results |
| mode | No | fast | `fast` or `full` (see Mode Selection) |

### Mode Selection

| Mode | Speed | Metadata | Use When |
|------|-------|----------|----------|
| `fast` | ~1-2s | Basic (no upload_date) | General searches, topic exploration |
| `full` | ~5-8s | Complete (includes upload_date, description) | Time-sensitive searches, recent content |

### Output Format

```json
[
  {
    "video_id": "dQw4w9WgXcQ",
    "title": "Video Title",
    "url": "https://www.youtube.com/watch?v=...",
    "channel": "Channel Name",
    "channel_url": "https://www.youtube.com/channel/UC...",
    "duration_string": "10:23",
    "view_count": 1234567,
    "upload_date": "20240115",
    "live_status": "not_live",
    "description": "First 200 chars..."
  }
]
```

### Output Fields

| Field | Type | Description | Fast Mode |
|-------|------|-------------|-----------|
| video_id | string | YouTube video ID | ✅ |
| title | string | Video title | ✅ |
| url | string | Full video URL | ✅ |
| channel | string | Channel name | ✅ |
| channel_url | string | Channel URL | ✅ |
| duration_string | string | Duration in HH:MM:SS or MM:SS format | ✅ |
| view_count | number | Total view count | ✅ |
| upload_date | string | Upload date in YYYYMMDD format | ❌ (null) |
| live_status | string | not_live, is_live, was_live, is_upcoming | ❌ (null) |
| description | string | First 200 characters of description | ❌ (empty) |

## Examples

```bash
# Search for AI tutorials (fast mode, default)
./scripts/search.sh "AI tutorial"

# Search with specific count
./scripts/search.sh "machine learning" 10

# Search with quoted phrase
./scripts/search.sh "\"deep learning\" beginner" 3

# Search with full metadata (slower but includes upload_date)
./scripts/search.sh "Claude AI news" 5 full

# Search for recent content (full mode recommended)
./scripts/search.sh "latest iPhone review" 10 full
```

## How It Works

```
┌─────────────────────────────────┐
│  search.sh <query> [count] [mode]│
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────┐     ┌─────────────────┐
│ _ensure_ytdlp   │────▶│ $YT_DLP         │
└─────────────────┘     └────────┬────────┘
                                 │
┌─────────────────┐              │
│ _ensure_jq      │────▶ $JQ    │
└─────────────────┘              │
                                 │
┌─────────────────┐              │
│ _naming.sh      │────▶ Metadata functions
└─────────────────┘              │
                                 ▼
                   ┌─────────────────────────────┐
                   │    Mode Selection           │
                   ├─────────────────────────────┤
                   │ fast: --flat-playlist       │
                   │       (quick, limited meta) │
                   │ full: no --flat-playlist    │
                   │       (slow, complete meta) │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │ yt-dlp search   │
                        │ ytsearchN:query │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ jq transform    │
                        │ JSON output     │
                        └────────┬────────┘
                                 │
                                 ▼
                   ┌─────────────────────────────┐
                   │ Write metadata (full only)  │
                   │ /tmp/monkey_knowledge/youtube/meta/    │
                   └─────────────────────────────┘
```

## Centralized Metadata Storage

Search results are saved to `/tmp/monkey_knowledge/youtube/meta/` with `partial: true` flag.

**Note:** Metadata is only written in `full` mode (since `fast` mode lacks `upload_date` required for filename).

| Scenario | Behavior |
|----------|----------|
| search (full) → get-info | search writes partial, get-info updates to complete |
| get-info → search | get-info already complete, search won't overwrite |
| search (fast) | No metadata written (missing upload_date) |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `ERROR: Unsupported platform` | OS not recognized | Check `uname -s` output |
| `ERROR: curl or wget required` | No download tool | Install curl or wget |
| Empty output | No search results | Try different keywords |

## License

MIT
