# book-audify

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Turn an owned e-book into a personal audiobook — `.m4b` with chapter
> bookmarks, synthesized with free Microsoft neural voices (edge-tts).

Takes `book-extract`'s per-chapter Markdown and runs:
clean → **validated hard gate** → per-chapter TTS → ffmpeg m4b merge.

- Cleaning strips everything a TTS engine would mispronounce (markup,
  footnote anchors, translator notes, decorative chapter frames) and skips
  front/back matter; `validate_tts.py` refuses to synthesize a dirty folder.
- Voice/rate are user choices — the skill A/B samples a short chapter
  instead of arguing taste. Sped-up listeners (1.5x) get a slower base rate
  so prosody survives.
- Foreign-language books: full-text translate-for-listening (per-book
  glossary, no English parentheticals) with a one-chapter listen gate before
  committing to the whole book.

`scripts/install_deps.sh` installs both dependencies: `edge-tts` as an
isolated CLI tool (`uv tool install edge-tts` / `pipx install edge-tts` —
never bare `pip`) and `ffmpeg`/`ffprobe` (brew, or a SHA256-verified
static build).

Note on data flow: edge-tts is a client for Microsoft's online read-aloud
service, so the book's full text is uploaded to Microsoft, chapter by
chapter, at synthesis time. Personal use of books you own; do not
distribute the audio.
