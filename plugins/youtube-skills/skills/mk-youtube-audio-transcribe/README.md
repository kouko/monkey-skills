# YouTube Audio Transcribe Skill

Transcribe audio files to text using local whisper.cpp with Metal acceleration.

## Overview

This skill converts audio files to text using OpenAI's Whisper model (via whisper.cpp). It supports:
- **Local processing**: No cloud API required
- **Metal acceleration**: Fast processing on macOS
- **Auto language detection**: Supports multiple languages
- **Multiple models**: From tiny (fast) to large (accurate)

## File Structure

```
mk-youtube-audio-transcribe/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── bin/                  # Pre-built binaries (macOS)
│   ├── ffmpeg            # Audio converter
│   ├── whisper-cli       # Whisper CLI with Metal
│   └── .gitkeep
├── models/               # Downloaded Whisper models
│   └── .gitkeep
└── scripts/
    ├── _ensure_ffmpeg.sh    # Ensures ffmpeg is available
    ├── _ensure_whisper.sh   # Ensures whisper-cli is available
    ├── _ensure_model.sh     # Auto-downloads models if missing
    ├── _utility__ensure_jq.sh        # Ensures jq is available
    ├── _utility__naming.sh          # Unified naming and metadata functions
    ├── _build_whisper.sh    # Build script for updates
    ├── _download_ffmpeg.sh  # Download script for updates
    ├── download-model.sh    # Download whisper models
    └── transcribe.sh        # Main transcription script
```

## Dependencies

| Dependency | Purpose | Location |
|------------|---------|----------|
| ffmpeg | Audio conversion | System or auto-download |
| whisper-cli | Speech-to-text | System or auto-build |
| jq | JSON formatting | System or auto-download |

## Script: `transcribe.sh`

### Usage

```bash
./scripts/transcribe.sh "<audio_file>" [model] [language]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| audio_file | Yes | - | Path to audio file |
| model | No | auto | Model name (auto = automatic selection) |
| language | No | auto | Language code |

### Available Models

#### Standard Models

| Model | Size | RAM | Description |
|-------|------|-----|-------------|
| auto | - | - | Automatic selection based on language (default) |
| tiny | 74MB | ~273MB | Fastest, lowest accuracy |
| base | 141MB | ~388MB | Fast, moderate accuracy |
| small | 465MB | ~852MB | Balanced |
| medium | 1.4GB | ~2.1GB | High accuracy |
| large-v3 | 2.9GB | ~3.9GB | Best accuracy |
| large-v3-turbo | 1.5GB | ~2.1GB | Large model optimized for speed |

#### Language-Specialized Models

| Model | Language | Size | Source |
|-------|----------|------|--------|
| belle-zh | Chinese | 1.5GB | [BELLE-2](https://huggingface.co/BELLE-2/Belle-whisper-large-v3-turbo-zh-ggml) |
| kotoba-ja | Japanese | 1.4GB | [kotoba-tech](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0-ggml) |
| kotoba-ja-q5 | Japanese | 513MB | Quantized version (faster) |

#### Auto-Selection (model=auto)

When model is `auto` (default), the script automatically selects the best model based on language:

| Language | Auto-Selected Model |
|----------|---------------------|
| zh | belle-zh (Chinese-specialized) |
| ja | kotoba-ja (Japanese-specialized) |
| others | medium (general purpose) |

```bash
# Auto-selection examples:
./scripts/transcribe.sh video.m4a auto zh   # → uses belle-zh
./scripts/transcribe.sh video.m4a auto ja   # → uses kotoba-ja
./scripts/transcribe.sh video.m4a auto en   # → uses medium
./scripts/transcribe.sh video.m4a           # → uses medium (default)
```

### Supported Languages

- `auto` - Auto-detect (default)
- `en` - English
- `ja` - Japanese
- `zh` - Chinese
- `ko` - Korean
- And many more (Whisper supports 99 languages)

### Output Format

**Success:**
```json
{
  "status": "success",
  "file_path": "{baseDir}/data/20240101__VIDEO_ID.json",
  "text_file_path": "{baseDir}/data/20240101__VIDEO_ID.txt",
  "language": "en",
  "duration": "3:32",
  "model": "medium",
  "char_count": 12345,
  "line_count": 100,
  "text_char_count": 10000,
  "text_line_count": 50,
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Note:** Output filename is derived from input audio filename. Metadata fields (video_id, title, channel, url) are populated from centralized metadata store if available.

**Error:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

### Output Fields

| Field | Description |
|-------|-------------|
| `file_path` | Absolute path to JSON file (with segments) |
| `text_file_path` | Absolute path to plain text file |
| `language` | Detected language code |
| `duration` | Audio duration |
| `model` | Model used for transcription |
| `char_count` | Character count of JSON file |
| `line_count` | Line count of JSON file |
| `text_char_count` | Character count of plain text file |
| `text_line_count` | Line count of plain text file |
| `video_id` | YouTube video ID (from metadata store) |
| `title` | Video title (from metadata store) |
| `channel` | Channel name (from metadata store) |
| `url` | Video URL (from metadata store) |

### JSON File Format

The JSON file at `file_path` contains:
```json
{
  "text": "Full transcription text...",
  "language": "en",
  "duration": "3:32",
  "model": "medium",
  "segments": [
    {
      "start": "00:00:00.000",
      "end": "00:00:05.000",
      "text": "First segment..."
    }
  ]
}
```

## Model Download

Models are **auto-downloaded** on first use. The script will:
1. Check if model exists in `models/` directory
2. If not found, automatically download from Hugging Face
3. Verify SHA256 checksum after download

For manual download (to see progress bar):

```bash
# Download a model manually
./scripts/download-model.sh medium      # 1.4GB, general purpose
./scripts/download-model.sh belle-zh    # 1.5GB, Chinese-specialized
./scripts/download-model.sh kotoba-ja   # 1.4GB, Japanese-specialized
./scripts/download-model.sh tiny        # 74MB, fastest

# List all available models
./scripts/download-model.sh --list
```

Models are saved to `models/` directory.

## Examples

```bash
# Transcribe with default settings (medium model, auto language)
./scripts/transcribe.sh /path/to/audio/video.m4a

# Use smaller model for faster processing
./scripts/transcribe.sh audio.mp3 small

# Force English language
./scripts/transcribe.sh podcast.wav medium en

# Use tiny model for quick preview
./scripts/transcribe.sh long-video.m4a tiny auto

# Use Chinese-specialized model for better Chinese transcription
./scripts/transcribe.sh chinese-video.m4a belle-zh zh

# Use Japanese-specialized model for better Japanese transcription
./scripts/transcribe.sh japanese-video.m4a kotoba-ja ja

# Use quantized Japanese model for faster processing
./scripts/transcribe.sh japanese-video.m4a kotoba-ja-q5 ja
```

## How It Works

```
┌─────────────────────────────┐
│      transcribe.sh          │
│  audio_file, [model], [lang]│
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Load dependencies         │
│   _ensure_ffmpeg.sh         │
│   _ensure_whisper.sh        │
│   _ensure_model.sh          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Convert audio to WAV      │
│   ffmpeg -i input           │
│   -ar 16000 -ac 1           │
│   -c:a pcm_s16le out.wav    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Run whisper-cli           │
│   -f audio.wav              │
│   -m model -oj              │
│   (Metal acceleration)      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Save to files             │
│   .json (full) + .txt       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Return file paths         │
│   {file_path, text_file_path}│
└─────────────────────────────┘
```

## Building Binaries

### whisper-cli (macOS with Metal)

```bash
./scripts/_build_whisper.sh
```

This will:
1. Clone whisper.cpp repository
2. Build with Metal acceleration enabled
3. Copy binary to bin/
4. Clean up source code

### ffmpeg

```bash
./scripts/_download_ffmpeg.sh
```

This will download a pre-built ffmpeg binary from martin-riedl.de (signed & notarized).
Automatically detects architecture (Apple Silicon or Intel) and downloads the appropriate version.

## Use Cases

1. **No subtitles**: Transcribe videos that don't have captions
2. **Podcast transcription**: Convert podcasts to searchable text
3. **Meeting notes**: Transcribe recorded meetings
4. **Content analysis**: Extract text for summarization

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `UNKNOWN_MODEL` | Invalid model name | Use a valid model name from available list |
| `DOWNLOAD_FAILED` | Model download failed | Check network connection, retry |
| `MODEL_CORRUPTED` | Model file corrupted or incomplete | Re-download with `download_command` |
| `File not found` | Invalid path | Check file path |
| `Transcription failed` | whisper error | Check audio format |
| `ffmpeg not found` | Missing ffmpeg | Run _download_ffmpeg.sh |
| `whisper-cli not found` | Missing whisper | Run _build_whisper.sh |

### Unknown Model Error

When an invalid model name is specified:

```json
{
  "status": "error",
  "error_code": "UNKNOWN_MODEL",
  "message": "Unknown model: invalid-name",
  "available_models": ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo", "belle-zh", "kotoba-ja", "kotoba-ja-q5"]
}
```

### Download Failed Error

When model auto-download fails:

```json
{
  "status": "error",
  "error_code": "DOWNLOAD_FAILED",
  "message": "Failed to download model 'medium'",
  "model": "medium",
  "download_url": "https://huggingface.co/..."
}
```

Check network connection and retry, or run `./scripts/download-model.sh <model>` in terminal to see detailed progress.

### Model Corrupted Error

When a model file is corrupted or incomplete (SHA256 mismatch), the script returns:

```json
{
  "status": "error",
  "error_code": "MODEL_CORRUPTED",
  "message": "Model 'medium' is corrupted or incomplete. Please re-download.",
  "model": "medium",
  "model_size": "1.4GB",
  "expected_sha256": "6c14d5adee5f86394037b4e4e8b59f1673b6cee10e3cf0b11bbdbee79c156208",
  "actual_sha256": "abc123...",
  "model_path": "/path/to/models/ggml-medium.bin",
  "download_command": "rm '/path/to/models/ggml-medium.bin' && curl -L --progress-bar -o '/path/to/models/ggml-medium.bin' 'https://...' 2>&1"
}
```

The `download_command` will remove the corrupted file and re-download it.

## Performance Tips

1. **Specify language**: Enables auto-selection of specialized models (zh→belle-zh, ja→kotoba-ja) for best accuracy
2. **Model selection**: Use `auto` (default) for optimal results, or `small` for faster processing
3. **Audio quality**: Better source audio = better transcription
4. **Memory**: Ensure enough RAM for chosen model

### Hardware Optimization

The script automatically optimizes for your hardware:

| Feature | Behavior |
|---------|----------|
| **CPU Threads** | Auto-detects CPU cores and uses all available threads |
| **GPU (Metal)** | Enabled by default on macOS |
| **Flash Attention** | Enabled by default for faster inference |

On Apple Silicon Macs, this typically provides 2-3x speedup compared to the default 4-thread setting.

## Security

See [MACOS_SECURITY.md](../../../../docs/MACOS_SECURITY.md) for details on macOS Gatekeeper and quarantine behavior.

## License

MIT
