---
name: using-youtube-skills
description: Entry point for the youtube-skills plugin. Explains when to use it and what skills are available. Load this skill for YouTube video processing tasks.
---

# Using YouTube Skills

This plugin provides tools for searching, downloading, transcribing, and summarizing YouTube content.

## When to Use

- Searching for YouTube videos
- Getting video metadata and info
- Downloading audio or captions
- Transcribing video audio
- Summarizing video content
- Getting latest videos from a channel

## Available Skills

| Skill | Purpose |
|-------|---------|
| `youtube-skills:mk-youtube-search` | Search YouTube videos by keyword |
| `youtube-skills:mk-youtube-get-info` | Get video metadata (title, duration, views) |
| `youtube-skills:mk-youtube-get-caption` | Download video subtitles |
| `youtube-skills:mk-youtube-get-audio` | Download video audio |
| `youtube-skills:mk-youtube-audio-transcribe` | Transcribe audio to text via whisper.cpp |
| `youtube-skills:mk-youtube-summarize` | Summarize video or channel content |
| `youtube-skills:mk-youtube-transcript-summarize` | Summarize from transcript file |
| `youtube-skills:mk-youtube-get-channel-latest` | Get latest videos from a channel |

## Quick Start

- Summarize a video: invoke `youtube-skills:mk-youtube-summarize` with the URL
- Search and explore: invoke `youtube-skills:mk-youtube-search`
