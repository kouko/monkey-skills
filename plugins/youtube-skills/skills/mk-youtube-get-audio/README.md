# YouTube Audio Skill

Download audio from YouTube videos with automatic cookie fallback for restricted content.

## Overview

This skill extracts audio from YouTube videos using `yt-dlp`. It supports:
- **Best available format**: m4a, webm, or opus (no conversion needed)
- **Cookie fallback**: Auto-retry with browser cookies when download fails
- **Chrome multi-profile**: Automatically tries all Chrome profiles

## File Structure

```
mk-youtube-get-audio/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── bin/                  # Auto-downloaded binaries (initially empty)
│   └── .gitkeep
└── scripts/
    ├── _utility__ensure_ytdlp.sh  # Ensures yt-dlp is available
    ├── _utility__ensure_jq.sh     # Ensures jq is available
    ├── _utility__naming.sh        # Unified naming and metadata functions
    └── audio.sh          # Main audio download script
```

## Dependencies

| Dependency | Purpose | Auto-download |
|------------|---------|---------------|
| yt-dlp | Video/audio download | Yes |
| jq | JSON output formatting | Yes |
| curl/wget | Download binaries | Required (pre-installed) |

**Note**: No ffmpeg required. Audio is downloaded in the best available format without conversion.

## Script: `audio.sh`

### Usage

```bash
./scripts/audio.sh "<URL>" [output_dir] [browser]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| URL | Yes | - | YouTube video URL |
| output_dir | No | /tmp/monkey_knowledge/youtube/audio/ | Output directory |
| browser | No | auto | Browser for cookies (chrome, firefox, safari, edge, brave) |

### Output Format (JSON)

**Success:**
```json
{
  "status": "success",
  "file_path": "/tmp/monkey_knowledge/youtube/audio/20240101__VIDEO_ID.m4a",
  "file_size": "5.2M",
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "duration_string": "3:32"
}
```

**Error:**
```json
{
  "status": "error",
  "message": "Download failed (tried with and without cookies)"
}
```

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" or "error" |
| file_path | string | Absolute path to audio file |
| file_size | string | Human-readable file size |
| video_id | string | YouTube video ID |
| title | string | Video title |
| channel | string | Channel name |
| url | string | Video URL |
| duration_string | string | Video duration (e.g., "3:32") |
| message | string | Error message (only on failure) |

## Examples

```bash
# Download to default location (auto cookie fallback)
./scripts/audio.sh "https://www.youtube.com/watch?v=xxx"

# Download to custom directory
./scripts/audio.sh "https://www.youtube.com/watch?v=xxx" ~/Music

# Force use Chrome cookies
./scripts/audio.sh "https://www.youtube.com/watch?v=xxx" /tmp chrome

# Force use Firefox cookies
./scripts/audio.sh "https://www.youtube.com/watch?v=xxx" /tmp firefox
```

## How It Works

```
┌─────────────────────────────┐
│         audio.sh            │
│  URL, [output_dir], [browser]│
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   First attempt (no auth)   │
└──────────────┬──────────────┘
               │
       ┌───────┴───────┐
       │               │
    Success         Failed
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────────────┐
│ Return JSON │  │ Auto-detect browser │
│ with path   │  │ + Chrome profiles   │
└─────────────┘  └──────────┬──────────┘
                            │
                            ▼
               ┌─────────────────────────────┐
               │ Try browsers in order:      │
               │ chrome → firefox → safari   │
               │ → edge → brave              │
               └──────────────┬──────────────┘
                              │
                              ▼
               ┌─────────────────────────────┐
               │ If Chrome, try profiles:    │
               │ Default → Profile 1 → ...   │
               └──────────────┬──────────────┘
                              │
                      ┌───────┴───────┐
                      │               │
                   Success         Failed
                      │               │
                      ▼               ▼
               ┌─────────────┐  ┌─────────────┐
               │ Return JSON │  │ Return error│
               │ with path   │  │ JSON        │
               └─────────────┘  └─────────────┘
```

## Browser Cookie Fallback

When initial download fails (e.g., member-only or age-restricted content), the script automatically retries with browser cookies.

### Supported Browsers

| Browser | Parameter | Platform | Profile Support |
|---------|-----------|----------|-----------------|
| Chrome | `chrome` | Windows, macOS, Linux | Auto-detect all profiles |
| Firefox | `firefox` | Windows, macOS, Linux | Default only |
| Safari | `safari` | macOS | Default only |
| Edge | `edge` | Windows, macOS | Default only |
| Brave | `brave` | Windows, macOS, Linux | Default only |

### Chrome Profile Detection

Chrome profile directories are automatically enumerated:

| Platform | Directory |
|----------|-----------|
| macOS | `~/Library/Application Support/Google/Chrome/` |
| Linux | `~/.config/google-chrome/` |

Profiles are tried in order:
1. `Default` (default profile)
2. `Profile 1`, `Profile 2`, ... (additional profiles)

Console output indicates which profile was used:
```
[INFO] Using cookies from: chrome:Profile 2
```

### Use Cases for Cookie Authentication

- **Member-only videos**: Channel membership content
- **Age-restricted videos**: Content requiring age verification
- **Region-restricted content**: Some geo-blocked videos
- **Private videos**: If your account has access

## Security Considerations

| Risk | Description | Mitigation |
|------|-------------|------------|
| Account suspension | YouTube may suspend accounts for automated access | Use secondary account |
| Cookie expiration | YouTube cookies expire in 3-5 days | Refresh browser session periodically |
| Privacy | Cookie files contain authentication data | Don't share or commit cookie files |

**Recommendation**: Use a secondary YouTube account for downloading restricted content.

## Audio Format

The script downloads audio in the best available format without conversion:

- **Format**: Typically m4a, webm, or opus (depends on source)
- **Quality**: Best available from YouTube
- **Channels**: Same as source (usually stereo)
- **No conversion**: No ffmpeg required

## Output Location

| Directory | Persistence | Notes |
|-----------|-------------|-------|
| `/tmp/monkey_knowledge/youtube/audio/` | Until reboot | Default location |
| `~/Music/` | Permanent | Recommended for keeping |
| Custom path | Permanent | User-specified |

## Use Cases

1. **Speech-to-text**: Download audio when video has no subtitles
2. **Podcast extraction**: Save podcast audio for offline listening
3. **Music download**: Extract music from music videos
4. **Member content**: Access membership content with browser cookies

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Download failed (tried with and without cookies)` | All attempts failed | Check URL, login to YouTube in browser |
| `File not found` | Download succeeded but file missing | Check disk space and permissions |

## Troubleshooting

### Cookie issues

```bash
# Check if browser is supported
yt-dlp --cookies-from-browser chrome --list-formats "URL"

# Test specific profile
yt-dlp --cookies-from-browser "chrome:Profile 1" --list-formats "URL"
```

### Permission errors

```bash
# Check output directory permissions
ls -la /tmp/monkey_knowledge/youtube/audio/

# Create directory if needed
mkdir -p /tmp/monkey_knowledge/youtube/audio/
```

### Disk space

```bash
# Check available space
df -h /tmp/
```

## License

MIT
