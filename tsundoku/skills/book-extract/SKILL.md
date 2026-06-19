---
name: book-extract
description: |
  Convert a downloaded EPUB into chunked-by-chapter Markdown — NCX-driven chapter splitting, pandoc engine, CJK-safe (繁中/簡中/日文). Use to read an owned book into context or build a skill from it. Then → book-distill.
---

# Kobo Extract

Converts an EPUB → one Markdown file per chapter, ready for LLM ingestion.

The downstream goal is **knowledge → skill**: feed the chunked Markdown to
Claude, distill into an outline, then refine into a reusable skill (typically
via `dev-workflow:skill-creator-advance`).

## Why a custom converter?

Many CJK EPUBs use Kobo-specific markup (`<span class="koboSpan">`) instead of
semantic `<h1>` for chapters. Running pandoc directly produces zero markdown
headings, which kills downstream chunking. This skill:

1. Parses the EPUB's `toc.ncx` (or EPUB3 nav) to get the canonical chapter list
2. Maps each chapter to its XHTML spine item
3. Pre-cleans XHTML noise (kobo spans, SVG blocks, scripts, empty divs)
4. Runs pandoc per-chapter to produce GFM Markdown
5. Post-cleans (collapses whitespace, strips pandoc hard-break artifacts)
6. Writes per-chapter MD files + index.md + metadata.json

## Pre-conditions

- An EPUB file (typically from `kobo-library` `kobo_get.sh`)
- pandoc installed — run `install_pandoc.sh` once

## Components

| Path | Role |
|---|---|
| `scripts/install_pandoc.sh` | brew → standalone fallback installer |
| `scripts/epub_to_markdown.py` | the converter (Python stdlib only + pandoc subprocess) |
| `scripts/cache_clear.sh` | wipe extracted markdown / library cache |
| `pandoc` | external dependency, ~50 MB |

## One-time Setup

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/install_pandoc.sh
# prints PANDOC=<path>; already on $PATH after brew install
```

The installer tries Homebrew first, falls back to GitHub-release standalone
binary download into `$TSUNDOKU_ROOT/bin/pandoc`. No-op if pandoc is already
on PATH.

## Conversion

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/epub_to_markdown.py \
    --epub  path/to/book.epub \
    [--out-dir path/to/library-root] \
    [options]
```

`--out-dir` is **optional** — defaults to `$TSUNDOKU_MARKDOWN_DIR`
(= `$TSUNDOKU_ROOT/cache/markdown` = `~/.cache/tsundoku/markdown`). It's
treated as a **library root**: the script auto-creates a per-book
subdirectory inside it so you can convert many books into the same root
without overwrites. The subdir name uses the EPUB's title; if the input
filename matches the kobodl pattern (`... <8-hex>.epub`), the 8-char id is
appended for dedupe.

**Why cache?** Extracted markdown is regenerable from the EPUB at any time,
so it lives under XDG cache (not config, not data). Safe to wipe between
projects. See `scripts/cache_clear.sh`.

| Option | Effect |
|---|---|
| `--no-subdir` | disable per-book subdir; write straight into `--out-dir` |
| `--strip-images` | skip image extraction + drop all `![]()` and raw `<img>` references — for pure-text shipping (LLM distillation, plain-text vault) |
| `--strip-frontmatter` | skip 書封 / 目錄 / 版權 / cover / contents / colophon / etc. |
| `--strip-backmatter` | skip 索引 / 致謝 / index / acknowledg / about-the-author. **Note**: 附錄 / 譯後記 are kept by default — they're often essential to non-fiction |
| `--merge-small N` | merge chapters with fewer than N tokens into the previous (default 0 = off) |
| `--pandoc PATH` | override pandoc binary (default: `$PANDOC` env or `pandoc` on PATH) |
| `--quiet` | suppress per-chapter progress to stderr |

### Images

By default, image files referenced by the EPUB are extracted alongside the
chapter Markdown:

```
out-dir/<book>/
├── images/
│   ├── cover.jpg
│   ├── ch03-fig1.png        ← basename preserved when unique
│   └── cover-9f1c2a3b.svg   ← SHA-1 suffix on basename collision
├── 01-cover.md              ← contains `![](images/cover.jpg)`
├── 03-chapter-01.md         ← contains `![Fig 1](images/ch03-fig1.png)`
...
```

All image references in chapter Markdown use inline GFM syntax
`![alt](images/<file>)`, relative to each chapter file. External URLs
(`http(s)://`) and `data:` URIs are passed through untouched (not extracted,
not rewritten). Inline `<svg>` blocks are stripped (covers and decorative
SVG); SVG referenced via `<img src="cover.svg">` is extracted normally.

**Disk cost**: typically +5 MB per book; image-heavy design / business
books may reach 50 MB. To opt out for LLM-only distillation use
`--strip-images`.

### Output layout

```
out-dir/                            ← --out-dir (library root)
└── 一九八四-b9152ffe/               ← auto-created per-book subdir
    ├── index.md                    ← TOC + per-chapter token estimate
    ├── metadata.json               ← title, authors, publisher, ISBN, chapters[]
    ├── 01-cover.md                 ← (skipped if --strip-frontmatter)
    ├── 02-序.md
    ├── 03-chapter-01.md            ← H1 = chapter label from NCX
    ├── 04-chapter-02.md
    ...
```

Subdir naming:
- **Default**: `<slug-of-title>` from EPUB metadata
- **kobodl-sourced files** (filename ends in 8-hex): `<slug-of-title>-<id8>`,
  giving deterministic dirs that dedupe re-purchased editions
- **No title in metadata**: falls back to slugified EPUB filename stem
- **Re-running on the same EPUB**: same subdir name → idempotent overwrite

Chapter filenames inside: `NN-<slugified-label>.md`, padded to 2-digit prefix.
Slugs keep CJK characters intact, replace path-unsafe punctuation with `-`.

## Token Budget Reference

Per `metadata.json.total_tokens` (CJK-aware estimate, ~0.6 tok/char):

| Book | Chapters | Total tokens | Largest chapter | Strategy |
|---|---|---|---|---|
| 一九八四 (sample) | 9 | ~95K | 第二章 35K | One-shot context (47% window) |
| 400-page expository | ~12-20 | ~120-180K | ~15-25K | Per-chapter or chapter-group |
| 600-page tome | ~30 | ~150-220K | ~10-15K | Always per-chapter |

**Rule of thumb**: if `total_tokens > 80,000`, prefer chapter-by-chapter
distillation. If a single chapter > 30K, ask Claude to summarize that chapter
first before extracting frameworks.

## Standard Workflow — EPUB → Skill

### Step 1 — Convert

```bash
source ${CLAUDE_SKILL_DIR}/scripts/tsundoku_paths.sh
EPUB="$TSUNDOKU_DOWNLOADS/<author> - <title> <id8>.epub"

bash ${CLAUDE_SKILL_DIR}/scripts/install_pandoc.sh >/dev/null
python3 ${CLAUDE_SKILL_DIR}/scripts/epub_to_markdown.py \
    --epub "$EPUB" --strip-frontmatter --quiet
# → creates $TSUNDOKU_MARKDOWN_DIR/<title-slug>-<id8>/index.md + chapter files
# + images/ subdirectory (image references rewritten inline)
# (= ~/.cache/tsundoku/markdown/<title-slug>-<id8>/...)
#
# Pure-text shipping (LLM distillation only): add --strip-images
```

For a permanent home (e.g. checking into a vault), pass `--out-dir`:

```bash
python3 ... --epub "$EPUB" --out-dir ~/Documents/vault/books/
```

### Step 2 — Pass 1: build outline

Read `index.md` first to see the chapter map and token totals. Then read the
chapters in sequence (smallest first or in TOC order) and produce a concise
outline:

```
output/outline.md
├── Book metadata (title, author, central thesis in 1 sentence)
├── Per-chapter
│   ├── Title
│   ├── 1-line summary
│   ├── Key concepts named
│   ├── Frameworks / models introduced
│   └── Decision rules / heuristics distilled
└── Cross-chapter themes
```

Keep outline ≤ 5K tokens. This compresses ~95K of book into ~5K of structured
notes — **the actionable knowledge density is in the outline, not the prose**.

### Step 3 — Pass 2: build the skill

Hand the outline + a few re-read chapters to **`dev-workflow:skill-creator-advance`**
or write directly:

```
new-skill/
├── SKILL.md              # frontmatter (name, description, when-to-use)
│                         # core methodology — distilled frameworks
│                         # decision rules — when to apply X vs Y
│                         # examples — book-grounded micro-cases
└── references/
    └── source-book.md    # outline, with citation back to chapters
```

**Crucial**: cite source chapters in the SKILL.md so future-you can re-read
context if the skill behaves wrong. Example footer:

```markdown
## Source

Based on *<title>* by <author>, chapters X / Y / Z.
See [`references/source-book.md`](references/source-book.md) for outline.
```

## Cache Management

Extracted markdown is regenerable, so it lives in `$TSUNDOKU_ROOT/cache/markdown/`.
After finishing a book→skill task, wipe to reclaim disk:

```bash
# wipe everything (markdown + library.json), keep auth and EPUBs
bash ${CLAUDE_SKILL_DIR}/scripts/cache_clear.sh

# wipe only one book's markdown
bash ${CLAUDE_SKILL_DIR}/scripts/cache_clear.sh --book 一九八四-b9152ffe

# preview what would be removed
bash ${CLAUDE_SKILL_DIR}/scripts/cache_clear.sh --dry-run

# wipe only library.json (force fresh re-export next time)
bash ${CLAUDE_SKILL_DIR}/scripts/cache_clear.sh --library-only
```

Auth (`$TSUNDOKU_ROOT`), binary (`$TSUNDOKU_ROOT/bin/`), and EPUB downloads
(`$TSUNDOKU_DOWNLOADS`) are **never** touched.

## Known Quirks

- **NCX-less EPUBs**: rare in modern Kobo books, but if the EPUB has no
  toc.ncx and no EPUB3 nav, chapter labels fall back to filename stems
  (e.g. `p-002`). The content is still split per spine item, just unlabeled.
- **Mid-chapter NCX entries**: if NCX points to `chapter.xhtml#section-3` for
  a sub-section, the converter only matches at the file level — sub-section
  labels are lost. Workaround: edit `index.md` post-hoc or split by H2/H3
  manually after conversion.
- **Image-only chapters**: some EPUBs have a "chapter" that's just a cover
  illustration. By default the image is extracted to `images/` and a short
  `![](images/cover.jpg)` line remains. With `--strip-images` these
  chapters become empty (5-20 tokens) and may merge with `--merge-small`.
- **Description ≤ 500 chars**: comes from `kobo-library`, not this skill —
  not relevant here, but a reminder that book metadata from Kobo is summary,
  not synopsis.
- **Front-matter heuristic**: pattern-matches on common labels (書封 / 目錄 /
  版權 / cover / contents / dedication / colophon / publication / 出版資訊).
  Misses publisher-specific labels like "推薦序" or "導讀" — those are
  retained, which is usually correct for expository books.

## CJK / Multi-language Notes

- **Traditional Chinese / Simplified Chinese**: clean output, no special
  handling needed
- **Japanese with ruby (振り仮名)**: pandoc drops `<rt>` content by default.
  The converter doesn't add a furigana filter. If you need it preserved,
  add `--lua-filter` via the `--pandoc` option pointing to a wrapped pandoc
  invocation; see [waldeir/pandoc-filter-furigana](https://github.com/waldeir/pandoc-filter-furigana)
- **Vertical-text books**: irrelevant in Markdown (pure text once converted)

## Cross-Skill Handoff

| Input from | This skill | Output to |
|---|---|---|
| `kobo-library:kobo_get.sh` (EPUB) | converts | `dev-workflow:skill-creator-advance` (skill creation) |
| Manual EPUB drop | converts | `obsidian:obsidian-markdown` (vault notes) |
| Manual EPUB drop | converts | direct LLM context |

## Reference

- pandoc docs: <https://pandoc.org/MANUAL.html>
- pandoc EPUB notes: <https://pandoc.org/epub.html>
- EPUB OPF spec: <https://www.w3.org/TR/epub-33/>
- Book-to-knowledge two-pass pattern: outline first, distill second
