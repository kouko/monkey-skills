# book-extract

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Convert an EPUB into chunked-by-chapter Markdown for LLM ingestion.
> Format-agnostic — works on any EPUB, not just Kobo-sourced.

Part of the [tsundoku](../..) plugin. Skill spec Claude loads is
[`SKILL.md`](SKILL.md); this README is for humans.

## Why a custom converter (vs plain pandoc)?

Many EPUBs use Kobo-specific markup (`<span class="koboSpan">`) instead of
semantic `<h1>` for chapters. Running pandoc directly produces **zero
markdown headings**, which kills downstream chunking.

This skill drives chapter splitting from the EPUB's `toc.ncx` (or EPUB3
nav) instead — works on books that don't use semantic chapter markup.
Validated end-to-end on Kobo / 角川 / 時報 / O'Reilly EPUBs.

## Pipeline

```
EPUB
  ↓
unzip + parse OPF/NCX        ← spine items (XHTML files in order)
                              + chapter labels mapped from NCX
  ↓ per spine item
pre-clean XHTML              ← strip kobo spans, SVG, scripts, empty divs
  ↓
pandoc XHTML → GFM Markdown
  ↓
post-clean MD                ← strip leading 全形 indents, hard-break `\`
                              artifacts, raw <img> tags
  ↓
NN-<slugified-label>.md      ← H1 = chapter label from NCX
+ index.md (TOC + token estimates)
+ metadata.json (title / authors / publisher / ISBN / chapters)
```

## Quick start

```bash
# One-time: ensure pandoc is installed (brew → standalone fallback)
bash scripts/install_pandoc.sh

# Source paths
source scripts/tsundoku_paths.sh
EPUB=~/Books/kobo/"<author> - <title> b9152ffe.epub"

# Convert (uses $TSUNDOKU_MARKDOWN_DIR by default — no --out-dir needed)
python3 scripts/epub_to_markdown.py --epub "$EPUB" \
    --strip-images --strip-frontmatter

# → writes to ~/.tsundoku/cache/markdown/<title-slug>-<id8>/
#       index.md + metadata.json + NN-chapter.md files
```

## Conversion options

| Flag | Effect |
|---|---|
| `--out-dir DIR` | output ROOT (auto per-book subdir inside; default `$TSUNDOKU_MARKDOWN_DIR`) |
| `--no-subdir` | disable per-book subdir; write straight into `--out-dir` |
| `--strip-images` | drop image references — recommended for text-heavy books |
| `--strip-frontmatter` | skip 書封 / 目錄 / 版權 / cover / contents etc. |
| `--strip-backmatter` | skip 索引 / 致謝 / index / acknowledg (附錄 / 譯後記 retained) |
| `--merge-small N` | merge sub-N-token chapters into previous |
| `--pandoc PATH` | override pandoc binary |
| `--quiet` | suppress per-chapter progress |

## Output structure

```
~/.tsundoku/cache/markdown/<title-slug>-<id8>/
├── index.md                      ← TOC + per-chapter token estimate
├── metadata.json                 ← title / authors / publisher / ISBN / chapters[]
├── 01-cover.md                   ← (skipped if --strip-frontmatter)
├── 02-序.md
├── 03-chapter-01.md              ← H1 = chapter label from NCX
├── 04-chapter-02.md
...
```

Chapter filenames: `NN-<slugified-label>.md` (CJK preserved). Subdir name:
`<slug-of-title>` or `<slug-of-title>-<id8>` if input filename matches the
kobodl pattern.

## Token budget reference

| Book size | Total tokens (CJK estimate) | Strategy |
|---|---|---|
| ≤80K | one-shot context | full book in one Claude call |
| 80-150K | chapter-by-chapter | iterate per file |
| 150K+ | outline-first | summarize first, then targeted re-read |

## Cache management

```bash
# Wipe everything (markdown + library.json), keep auth + EPUBs
bash scripts/cache_clear.sh

# Wipe one book's markdown
bash scripts/cache_clear.sh --book 一九八四-b9152ffe

# Preview
bash scripts/cache_clear.sh --dry-run

# Wipe only library.json (force fresh re-export)
bash scripts/cache_clear.sh --library-only
```

Auth (`~/.tsundoku/kobo/auth/`), binary, and downloaded EPUBs are **never**
touched.

## Files in this folder

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | Skill spec Claude loads (full conversion + chunking reference) |
| [`scripts/install_pandoc.sh`](scripts/install_pandoc.sh) | Brew → GitHub-release standalone fallback |
| [`scripts/epub_to_markdown.py`](scripts/epub_to_markdown.py) | NCX-driven chapter split + pandoc + clean. ~620 lines, stdlib only |
| [`scripts/cache_clear.sh`](scripts/cache_clear.sh) | Wipe extracted markdown / library cache (4 modes) |

## Sources accepted

- ✅ Kobo-sourced EPUBs (via [`kobo-library`](../kobo-library))
- ✅ Project Gutenberg
- ✅ BookWalker / 角川 / 講談社 download exports
- ✅ Apple Books exports
- ✅ Hand-prepared EPUBs
- ⚠️ EPUBs with no NCX and no EPUB3 nav fall back to filename-stem chapters
- ❌ PDF (different format, would need a separate `pdf-extract` skill)

## See also

- [`book-distill`](../book-distill) — natural next step: turn the chunked
  Markdown into a coherent set of agent skills
- [`tsundoku` README](../..) — full pipeline overview
