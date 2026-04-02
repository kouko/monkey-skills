---
name: mk-youtube-audio-transcribe
description: Transcribe audio to text using local whisper.cpp. Use when user wants to convert audio/video to text, get transcription, or speech-to-text.
license: MIT
metadata:
  version: 1.1.1
  author: kouko
  tags:
    - youtube
    - audio
    - transcribe
    - whisper
    - speech-to-text
compatibility:
  claude-code: ">=1.0.0"
---

# YouTube Audio Transcribe

Transcribe audio files to text using local whisper.cpp (no cloud API required).

## Quick Start

```
/mk-youtube-audio-transcribe <audio_file> [model] [language] [--force]
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| audio_file | Yes | - | Path to audio file |
| model | No | auto | Model: auto, tiny, base, small, medium, large-v3, belle-zh, kotoba-ja |
| language | No | auto | Language code: en, ja, zh, auto (auto-detect) |
| --force | No | false | Force re-transcribe even if cached file exists |

## Examples

- `/mk-youtube-audio-transcribe /path/to/audio/video.m4a` - Transcribe with auto model selection
- `/mk-youtube-audio-transcribe video.m4a auto zh` - Auto-select best model for Chinese → belle-zh
- `/mk-youtube-audio-transcribe video.m4a auto ja` - Auto-select best model for Japanese → kotoba-ja
- `/mk-youtube-audio-transcribe audio.mp3 small en` - Use small model, force English
- `/mk-youtube-audio-transcribe podcast.wav medium ja` - Use medium model (explicit), Japanese

## How it Works

1. Execute: `{baseDir}/scripts/transcribe.sh "<audio_file>" "<model>" "<language>"`
2. Auto-download model if not found (with progress)
3. Convert audio to 16kHz mono WAV using ffmpeg
4. Run whisper-cli for transcription
5. Save full JSON to `{baseDir}/data/<filename>.json`
6. Save plain text to `{baseDir}/data/<filename>.txt`
7. Return file paths and metadata

```
┌─────────────────────────────┐
│      transcribe.sh          │
│  audio_file, [model], [lang]│
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   ffmpeg: convert to WAV    │
│   16kHz, mono, pcm_s16le    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   whisper-cli: transcribe   │
│   with Metal acceleration   │
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

## Output Format

**Success:**
```json
{
  "status": "success",
  "file_path": "{baseDir}/data/20091025__VIDEO_ID.json",
  "text_file_path": "{baseDir}/data/20091025__VIDEO_ID.txt",
  "language": "en",
  "duration": "3:32",
  "model": "medium",
  "char_count": 12345,
  "line_count": 100,
  "text_char_count": 10000,
  "text_line_count": 50,
  "cached": false,
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Cache hit** (returns existing transcription):
```json
{
  "status": "success",
  "file_path": "{baseDir}/data/20091025__VIDEO_ID.json",
  "cached": true,
  ...
}
```

**Error (general):**
```json
{
  "status": "error",
  "message": "Error description"
}
```

**Error (unknown model):**
```json
{
  "status": "error",
  "error_code": "UNKNOWN_MODEL",
  "message": "Unknown model: invalid-name",
  "available_models": ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo", "belle-zh", "kotoba-ja", "kotoba-ja-q5"]
}
```

When you receive `UNKNOWN_MODEL` error: suggest a valid model from the `available_models` list.

**Error (model not found):**
```json
{
  "status": "error",
  "error_code": "MODEL_NOT_FOUND",
  "message": "Model 'medium' not found. Please download it first.",
  "model": "medium",
  "model_size": "1.4GB",
  "download_url": "https://huggingface.co/...",
  "download_command": "curl -L --progress-bar -o '/path/to/models/ggml-medium.bin' 'https://...' 2>&1"
}
```

When you receive `MODEL_NOT_FOUND` error:
1. Inform user: "Downloading model '{model}' ({model_size})..."
2. Execute `download_command` using Bash tool with `timeout: 1800000` (30 minutes)
3. After download completes: re-run the original transcribe command

**Error (model corrupted):**
```json
{
  "status": "error",
  "error_code": "MODEL_CORRUPTED",
  "message": "Model 'medium' is corrupted or incomplete. Please re-download.",
  "model": "medium",
  "model_size": "1.4GB",
  "expected_sha256": "6c14d5adee5f86394037b4e4e8b59f1673b6cee10e3cf0b11bbdbee79c156208",
  "actual_sha256": "def456...",
  "model_path": "/path/to/models/ggml-medium.bin",
  "download_command": "rm '/path/to/models/ggml-medium.bin' && curl -L --progress-bar -o '/path/to/models/ggml-medium.bin' 'https://...' 2>&1"
}
```

When you receive `MODEL_CORRUPTED` error:
1. Inform user: "Model '{model}' is corrupted. Re-downloading ({model_size})..."
2. Execute `download_command` (removes corrupted file and re-downloads) using Bash tool with `timeout: 1800000` (30 minutes)
3. After download completes: re-run the original transcribe command

## Output Fields

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
| `video_id` | YouTube video ID (from centralized metadata store) |
| `title` | Video title (from centralized metadata store) |
| `channel` | Channel name (from centralized metadata store) |
| `url` | Full video URL (from centralized metadata store) |

## Filename Format

Output files preserve the input audio filename's unified naming format with date prefix: `{YYYYMMDD}__{video_id}.{ext}`

Example: `20091025__dQw4w9WgXcQ.json`

## JSON File Format

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

## Models

### Standard Models

| Model | Size | RAM | Speed | Accuracy |
|-------|------|-----|-------|----------|
| auto | - | - | - | Auto-select based on language (default) |
| tiny | 74MB | ~273MB | Fastest | Low |
| base | 141MB | ~388MB | Fast | Medium |
| small | 465MB | ~852MB | Moderate | Good |
| medium | 1.4GB | ~2.1GB | Slow | High |
| large-v3 | 2.9GB | ~3.9GB | Slowest | Best |
| large-v3-turbo | 1.5GB | ~2.1GB | Moderate | High (optimized for speed) |

### Language-Specialized Models

| Model | Language | Size | Description |
|-------|----------|------|-------------|
| belle-zh | Chinese | 1.5GB | BELLE-2 Chinese-specialized model |
| kotoba-ja | Japanese | 1.4GB | kotoba-tech Japanese-specialized model |
| kotoba-ja-q5 | Japanese | 513MB | Quantized version (faster, smaller) |

### Auto-Selection (model=auto)

When model is `auto` (default), the system automatically selects the best model based on language:

| Language | Auto-Selected Model |
|----------|---------------------|
| zh | belle-zh (Chinese-specialized) |
| ja | kotoba-ja (Japanese-specialized) |
| others | medium (general purpose) |

Example: `/mk-youtube-audio-transcribe video.m4a auto zh` → uses `belle-zh`

## Notes

- **File caching**: If transcription already exists for this video, it will be reused (returns `cached: true`)
- **Force refresh**: Use `--force` flag to re-transcribe even if cached file exists
- **Specify language for best results** - enables auto-selection of specialized models (zh→belle-zh, ja→kotoba-ja)
- Use Read tool to get file content from `file_path` or `text_file_path`
- **Models must be downloaded before first use** - returns `MODEL_NOT_FOUND` error with download command
- Uses Metal acceleration on macOS for faster processing
- Supports auto language detection
- Audio is converted to 16kHz WAV for optimal results
- Requires ffmpeg and whisper-cli (pre-built in bin/)

## Model Download

Models must be downloaded before transcription. When you receive a `MODEL_NOT_FOUND` error, execute the `download_command` with `timeout: 1800000`.

```bash
# In terminal (to see progress bar)
./scripts/download-model.sh medium      # 1.4GB
./scripts/download-model.sh belle-zh    # 1.5GB (Chinese)
./scripts/download-model.sh kotoba-ja   # 1.4GB (Japanese)
./scripts/download-model.sh --list      # Show all available models
```

## Next Step

After transcription completes, invoke `/mk-youtube-transcript-summarize` with the `text_file_path` from the output to generate a structured summary:

```
/mk-youtube-transcript-summarize <text_file_path>
```

**IMPORTANT**: Always use the Skill tool to invoke `/mk-youtube-transcript-summarize`. Do NOT generate summaries directly without loading the skill — it contains critical rules for compression ratio, section structure, data preservation, and language handling.
