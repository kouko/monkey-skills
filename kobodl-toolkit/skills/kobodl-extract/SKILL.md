---
name: kobodl-extract
description: >-
  Convert a downloaded EPUB into chunked-by-chapter Markdown for LLM
  ingestion. Designed for 400+ page expository books where chapter-level
  chunking matters for two-pass distillation (full book → outline → skill).
  Uses pandoc as the conversion engine, drives chapter splitting from the
  EPUB's NCX (table of contents) so it works on books that don't use semantic
  H1 markup. CJK-safe (繁中 / 簡中 / 日文). Use when the user wants to read
  a book they own into Claude's context, build a skill from a book's
  knowledge, or generate Obsidian / RAG-friendly chapter notes from EPUB.
  電子書EPUB分章Markdown化。書籍知識のskill化に向けた変換。
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

- An EPUB file (typically from `kobodl-library` `kobodl_get.sh`)
- pandoc installed — run `install_pandoc.sh` once

## Components

| Path | Role |
|---|---|
| `scripts/install_pandoc.sh` | brew → standalone fallback installer |
| `scripts/kobodl_to_markdown.py` | the converter (Python stdlib only + pandoc subprocess) |
| `pandoc` | external dependency, ~50 MB |

## One-time Setup

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/install_pandoc.sh
# prints PANDOC=<path>; already on $PATH after brew install
```

The installer tries Homebrew first, falls back to GitHub-release standalone
binary download into `$KOBODL_DATA/bin/pandoc`. No-op if pandoc is already
on PATH.

## Conversion

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/kobodl_to_markdown.py \
    --epub  path/to/book.epub \
    --out-dir path/to/output \
    [options]
```

| Option | Effect |
|---|---|
| `--strip-images` | drop image references (Markdown + raw `<img>`) — recommended for text-heavy books |
| `--strip-frontmatter` | skip 書封 / 目錄 / 版權 / cover / contents / colophon / etc. |
| `--strip-backmatter` | skip 索引 / 致謝 / index / acknowledg / about-the-author. **Note**: 附錄 / 譯後記 are kept by default — they're often essential to non-fiction |
| `--merge-small N` | merge chapters with fewer than N tokens into the previous (default 0 = off) |
| `--pandoc PATH` | override pandoc binary (default: `$PANDOC` env or `pandoc` on PATH) |
| `--quiet` | suppress per-chapter progress to stderr |

### Output layout

```
out-dir/
├── index.md              ← TOC + per-chapter token estimate
├── metadata.json         ← title, authors, publisher, ISBN, chapters[]
├── 01-cover.md           ← (skipped if --strip-frontmatter)
├── 02-序.md
├── 03-chapter-01.md      ← H1 = chapter label from NCX
├── 04-chapter-02.md
...
```

Filenames are `NN-<slugified-label>.md`, padded to 2-digit prefix. Slugs keep
CJK characters intact, replace path-unsafe punctuation with `-`.

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
source ${CLAUDE_PLUGIN_ROOT}/skills/kobodl-auth/scripts/kobodl_paths.sh
EPUB="$KOBODL_DOWNLOADS/<author> - <title> <id8>.epub"
OUT="$KOBODL_DATA/markdown/<title>"

bash ${CLAUDE_SKILL_DIR}/scripts/install_pandoc.sh >/dev/null
python3 ${CLAUDE_SKILL_DIR}/scripts/kobodl_to_markdown.py \
    --epub "$EPUB" --out-dir "$OUT" \
    --strip-images --strip-frontmatter --quiet
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

## Known Quirks

- **NCX-less EPUBs**: rare in modern Kobo books, but if the EPUB has no
  toc.ncx and no EPUB3 nav, chapter labels fall back to filename stems
  (e.g. `p-002`). The content is still split per spine item, just unlabeled.
- **Mid-chapter NCX entries**: if NCX points to `chapter.xhtml#section-3` for
  a sub-section, the converter only matches at the file level — sub-section
  labels are lost. Workaround: edit `index.md` post-hoc or split by H2/H3
  manually after conversion.
- **Image-only chapters**: some EPUBs have a "chapter" that's just a cover
  illustration. With `--strip-images` these become empty (5-20 tokens) and
  may merge with `--merge-small`.
- **Description ≤ 500 chars**: comes from `kobodl-library`, not this skill —
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
| `kobodl-library:kobodl_get.sh` (EPUB) | converts | `dev-workflow:skill-creator-advance` (skill creation) |
| Manual EPUB drop | converts | `obsidian:obsidian-markdown` (vault notes) |
| Manual EPUB drop | converts | direct LLM context |

## Reference

- pandoc docs: <https://pandoc.org/MANUAL.html>
- pandoc EPUB notes: <https://pandoc.org/epub.html>
- EPUB OPF spec: <https://www.w3.org/TR/epub-33/>
- Book-to-knowledge two-pass pattern: outline first, distill second
