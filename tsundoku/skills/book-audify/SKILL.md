---
name: book-audify
description: >-
  Turn an owned e-book into a personal audiobook (.m4b with chapter
  bookmarks). Takes book-extract's chunked-by-chapter Markdown, cleans it
  into TTS-ready plain text (a validated hard gate, not best-effort regex),
  batch-synthesizes per-chapter audio with edge-tts (free Microsoft neural
  voices, CJK-safe), and merges into a single m4b via ffmpeg. Optionally
  translates a foreign-language book chapter-by-chapter before synthesis
  (translate-for-listening rules + per-book glossary + one-chapter listen
  gate). Use when the user wants to listen to a book they own, convert
  EPUB/Markdown to audio/speech/audiobook, or asks for TTS narration of a
  book. 電子書轉個人有聲書。所有EPUBをオーディオブック化。
---

# Book Audify

Converts a book into a `.m4b` audiobook with chapter bookmarks, using free
neural TTS. Personal use of books the user owns — do not distribute the
produced audio. Note the input text is sent to a third party: edge-tts is a
client for Microsoft's online read-aloud endpoint, so **the full text of the
book is uploaded, chapter by chapter, to Microsoft at synthesis time** —
tell the user if they haven't clearly assumed it.

**Routing: this skill's input is per-chapter Markdown (`NN-title.md`).** If
the user starts from an EPUB (or any e-book file), run
`tsundoku:book-extract` on it first, then return here with its output
folder.

## Pipeline

```
Step 0: scripts/install_deps.sh              ← edge-tts + ffmpeg/ffprobe
book-extract output (NN-chapter.md ...)
  → scripts/clean_for_tts.py   src_dir dst_dir [--lang zh|en|ja]
  → REVIEW the printed skip list against the book's chapter list
  → scripts/validate_tts.py    dst_dir            ← HARD GATE
  → scripts/batch_tts.sh       dst_dir mp3_dir [voice] [rate]
  → scripts/build_m4b.sh       mp3_dir out.m4b [title] [author]
```

The skip-list review is a mandatory human/agent step, not a formality: the
cleaner drops front/back matter by filename, and a body chapter wrongly
matched there is silent data loss — the validator only inspects files that
exist, so no automated gate can catch it. Compare the `SKIPPED` list against
the book's actual chapter list before synthesizing.

Roughly 1 hour of synthesis per full-length book; the m4b plays in Apple
Books (macOS), BookPlayer (iOS — iOS Books does not accept sideloaded
audiobooks), or any audiobook player.

## Why a cleaning step + hard gate?

TTS engines read everything: markdown `#`/`**`, footnote anchors, circled
translator-note numbers (❶ ➊), decorative chapter frames, image tags, URLs.
Publisher markup varies too much to trust one regex pass, so the contract is
enforced by `validate_tts.py`: **if it fails, fix the flagged violations
semantically (or extend the cleaner) — never synthesize a folder that
doesn't PASS.** An hour of TTS on a dirty file is the failure mode the gate
exists to prevent.

`clean_for_tts.py` also:
- skips front/back matter (dedication, acknowledgments, copyright, index)
- converts digit chapter headings ("01 Title") to spoken form (第一章 /
  Chapter 1) so they aren't read digit-by-digit
- drops end-of-chapter translator notes whose inline anchors were removed

## Voice and rate

- List voices: `edge-tts --list-voices | grep zh-TW` (or `en-`, `ja-`)
- Defaults: `zh-TW-HsiaoChenNeural`, rate `+0%`
- **Ask the user two things before a full run: which voice (offer one male +
  one female sample of a short chapter), and whether they listen sped-up.**
  If they play audiobooks at 1.5x, synthesize at rate `-25%` — playback
  speed-up compresses pauses hardest, so a slower base preserves prosody and
  sentence boundaries.
- Re-synthesis is free: never argue taste, generate A/B samples of the same
  excerpt and let the user's ear decide.

## Foreign-language books (translate, then audify)

Translation is semantic work — done by Claude chapter-by-chapter, full-text
(never summarized). Rules that differ from print translation:

- Translate **for the ear**: split long sentences, flatten inversions
- Proper nouns: use target-language renderings only — never "賈伯斯 (Steve
  Jobs)" parentheticals, which get read aloud as English
- Numbers/units converted to natural spoken forms in the target language
- Keep a per-book glossary at `<dst_dir>/_glossary.md` (leading `_` is
  ignored by the validator); every chapter's translation carries it so names
  stay consistent, including across parallel per-chapter subagents

**Hard gate: translate ONE chapter → clean → synthesize → user listens and
approves — only then translate the rest.** "LLM translation is acceptable to
listen to" is an assumption that must be verified per book/user before
spending a full-book translation.

## Pre-conditions

- `scripts/install_deps.sh` installs both external legs: `edge-tts` as an
  isolated CLI tool (`uv tool install` / `pipx install` — never bare `pip`)
  and `ffmpeg`/`ffprobe` (PATH → brew → SHA256-verified static build;
  tools it installs are found by the scripts via `$TSUNDOKU_ROOT/bin` and
  `~/.local/bin` PATH fallbacks). Synthesis
  needs network access — chapter text goes to Microsoft's TTS endpoint.
- Chapters from `book-extract` (or any `NN-title.md` folder)

## Verify before declaring done

- `build_m4b.sh` already checks output duration against the sum of the
  inputs (ffmpeg's concat can drop a chapter and still exit 0); still
  confirm chapter count in the m4b == chapter files, and spot-decode two
  offsets (`ffmpeg -v error -ss <t> -i out.m4b -t 20 -f null -`)
- Listen to 30 seconds of one chapter (or have the user do it)
- Large m4b files (300MB+) usually exceed chat upload limits — hand the user
  a local path instead
