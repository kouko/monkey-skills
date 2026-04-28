# tsundoku 積読

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 0.11.0
**Part of**: [monkey-skills](../)

> *tsundoku (積読)* — Japanese for the books you've bought but haven't read yet.
> This plugin turns that pile into actionable knowledge.

Search a Kobo e-book library by **title / author / series / publication date /
category / description text / reading status / language**, present matches as
cards, download the chosen books as DRM-free EPUBs, convert downloaded EPUBs
into chunked-by-chapter Markdown, and **distill the book into atomic agent
skills** via the RIA-TV++ pipeline (Adler analytical read → 5 parallel
extractors → triple verification → RIA++ render → Zettelkasten linking →
adversarial pressure test). Language-adaptive output (EN / 日本語 / 繁體中文).
Wraps [`subdavis/kobo-book-downloader`][kobodl] and uses [pandoc][pandoc]
for the EPUB→Markdown stage. Distillation methodology adapted from
[`kangarooking/cangjie-skill`][cangjie] (MIT).

[kobodl]: https://github.com/subdavis/kobo-book-downloader
[pandoc]: https://pandoc.org
[cangjie]: https://github.com/kangarooking/cangjie-skill

## Skills

| Skill | Slash command | When to use |
|---|---|---|
| [`kobo-auth`](skills/kobo-auth/SKILL.md) | `/kobo-auth` | First-time setup, login, account migration, credential rotation |
| [`kobo-library`](skills/kobo-library/SKILL.md) | `/kobo-library` | Daily use — search, list, batch-download EPUBs |
| [`book-extract`](skills/book-extract/SKILL.md) | `/book-extract` | Convert EPUB → chunked-by-chapter Markdown |
| [`book-distill`](skills/book-distill/SKILL.md) | `/book-distill` | Markdown → atomic agent skills via RIA-TV++ |
| (router) | `/tsundoku` | Auto-route based on intent; ambiguous request → asks which step |

Naming convention:
- **`kobo-*`** — source-platform layer (auth + library): bound to Kobo /
  kobodl. Future `kindle-*` / `apple-books-*` siblings would mirror this.
- **`book-*`** — format-agnostic processing layer (extract + distill): works
  on any EPUB / any chunked Markdown regardless of source. Future
  `paper-distill` (academic papers) or `transcript-distill` (podcasts) would
  join here.

## Quick Start

All flows start by invoking a slash command in Claude Code. The skill
handles binary install, prompts, credential storage, and pipeline
orchestration — you do not run shell scripts directly.

### A. Brand-new setup (first-time login)

```
/kobo-auth
```

Or in natural language: *"Set up Kobo login for me."*

The skill installs the kobodl binary, walks you through device-flow
activation (opens `kobo.com/activate`, asks for the 6-digit code), and
stores credentials with `chmod 600` under `~/.tsundoku/kobo/auth/`.

### B. Migrate from existing kobodl install

```
/kobo-auth
```

Then tell it: *"I already have a `kobodl.json` at `~/KobodlLibrarySync/config/kobodl.json` — please import."* The skill imports the credentials instead of running the activation flow.

### C. Search and download

```
/kobo-library
```

Or: *"Search my Kobo library for books that mention behavioral economics, published since 2020, that I haven't read yet."*

The skill refreshes the library index, runs the multi-criteria filter,
previews matches as rich cards, and downloads chosen books as DRM-free
EPUBs to `~/Books/kobo/`. Idempotent — books already on disk are skipped.

### D. EPUB → chunked Markdown

```
/book-extract
```

Or: *"Convert this EPUB to chapter-split Markdown."*

The skill auto-installs pandoc if missing, splits on the EPUB's NCX
table-of-contents, strips images / frontmatter, and writes to
`~/.tsundoku/cache/markdown/<title-slug>-<id8>/`.

### E. Markdown → atomic agent skill set

```
/book-distill
```

Or: *"Distill this book into reusable agent skills."*

The skill bootstraps the working directory and runs the 6-stage
RIA-TV++ pipeline:

| Stage | Action | Output |
|---|---|---|
| 0 | Adler analytical read | `BOOK_OVERVIEW.md` |
| 1 | 5 parallel extractors | `candidates/` |
| 1.5 | Triple verification | `verified.md` (~30-50% pass) |
| 2 | RIA++ skill render | `<skill-slug>/SKILL.md` |
| 3 | Zettelkasten linking | `INDEX.md` |
| 4 | Adversarial pressure test | `test-prompts.json` |

Output prose stays in the source language; YAML metadata + slugs are English.

### Not sure which step?

```
/tsundoku
```

Router skill — describe your intent and it dispatches to the right
sub-skill. Ambiguous requests get a "which step?" clarifying question.

## Under the Hood (direct script invocation)

The slash commands above are the recommended interface. For debugging,
CI scripting, or power-user flows, every skill's underlying scripts can
be invoked directly. The skills delegate to these:

### Auth (kobo-auth)

```bash
# install binary + device-flow activation
bash tsundoku/skills/kobo-auth/scripts/kobo_install.sh
bash tsundoku/skills/kobo-auth/scripts/kobo_login.sh add

# or import existing credentials
bash tsundoku/skills/kobo-auth/scripts/kobo_login.sh \
    import-from ~/KobodlLibrarySync/config/kobodl.json
```

### Library (kobo-library)

```bash
source tsundoku/skills/kobo-library/scripts/tsundoku_paths.sh
export TMPDIR="$TSUNDOKU_TMPDIR"
mkdir -p "$TSUNDOKU_DOWNLOADS"

# refresh library index
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"

# search (5 output formats: markdown / json / table / ids / paths)
python3 tsundoku/skills/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "behavioral,economics,行為經濟" \
    --pub-after 2020 --status ReadyToRead --format markdown

# download chosen RevisionIds (idempotent)
bash tsundoku/skills/kobo-library/scripts/kobo_get.sh "$REVISION_ID"

# pipe filtered set
python3 tsundoku/skills/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" --series "Silent Witch" --format ids \
  | bash tsundoku/skills/kobo-library/scripts/kobo_get.sh --convert-pdf
```

### Extract (book-extract)

```bash
# one-time pandoc check
bash tsundoku/skills/book-extract/scripts/install_pandoc.sh

# convert (uses $TSUNDOKU_MARKDOWN_DIR by default)
python3 tsundoku/skills/book-extract/scripts/epub_to_markdown.py \
    --epub "$EPUB_PATH" --strip-images --strip-frontmatter

# clear cache when done
bash tsundoku/skills/book-extract/scripts/cache_clear.sh
```

### Distill (book-distill)

```bash
# bootstrap working dir from extracted markdown
bash tsundoku/skills/book-distill/scripts/book_distill_init.sh \
    一九八四-b9152ffe
# Claude then reads book-distill/SKILL.md and runs the 6-stage pipeline
```

## Storage Layout (single root, per-platform subdirs)

```
~/.tsundoku/                  ← TSUNDOKU_ROOT
├── kobo/                       Kobo platform state
│   ├── auth/                    chmod 700
│   │   └── kobodl.json          chmod 600 (Kobo session credentials)
│   └── bin/kobodl-macos         14 MB upstream binary
├── tmp/                        shared TMPDIR override (PYI-1270 fix)
└── cache/                      regenerable, wipe-able as a unit
    ├── kobo/library.json        cached library export
    └── markdown/<book>/...      EPUB → MD (platform-agnostic)

~/Books/kobo/                 ← TSUNDOKU_DOWNLOADS (user-visible EPUBs)
```

When `kindle-*` / `apple-books-*` skills land later, they'll mirror under
`~/.tsundoku/kindle/`, `~/.tsundoku/cache/kindle/`, etc.

**Two decision-point env vars** — set these to relocate things:

| Var | Default | Purpose |
|---|---|---|
| `TSUNDOKU_ROOT` | `~/.tsundoku` | All toolkit state (auth + binary + cache) |
| `TSUNDOKU_DOWNLOADS` | `~/Books/kobo` | User-visible EPUB downloads |

**Five derived paths** computed from the two above (don't set directly):

| Var | Scope |
|---|---|
| `TSUNDOKU_TMPDIR` | shared |
| `TSUNDOKU_MARKDOWN_DIR` | shared (cache/markdown) |
| `TSUNDOKU_KOBO_CONFIG` | Kobo: kobodl.json |
| `TSUNDOKU_KOBO_BINARY` | Kobo: kobodl-macos |
| `TSUNDOKU_KOBO_LIBRARY_JSON` | Kobo: library export |

All exported when sourcing `each skill's `scripts/tsundoku_paths.sh``.

The `kobo/auth/` subdirectory is `chmod 700`, the `kobodl.json` file is
`chmod 600`. The `cache/` subtree is regenerable — wipe at any time via
`book-extract/scripts/cache_clear.sh`.

## Repository Structure

```
tsundoku/
├── .claude-plugin/plugin.json
├── README.md
├── commands/                    # slash commands (1:1 with skills + 1 router)
│   ├── tsundoku.md              #   /tsundoku (router)
│   ├── kobo-auth.md             #   /kobo-auth
│   ├── kobo-library.md          #   /kobo-library
│   ├── book-extract.md          #   /book-extract
│   └── book-distill.md          #   /book-distill
└── skills/
    ├── kobo-auth/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobo_install.sh    # binary download (idempotent)
    │       └── kobo_login.sh      # add / status / remove / import-from / path
    ├── kobo-library/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobo_query.py      # filter --export-library JSON, 5 formats
    │       └── kobo_get.sh        # download by RevisionId (args or stdin)
    ├── book-extract/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── install_pandoc.sh     # brew → standalone fallback
    │       ├── epub_to_markdown.py   # NCX-driven chapter split + pandoc + clean
    │       └── cache_clear.sh   # wipe extracted markdown / library cache
    └── book-distill/                 # RIA-TV++ pipeline (forked from cangjie-skill, MIT)
        ├── SKILL.md                  # top-level orchestrator
        ├── ATTRIBUTION.md             # upstream credits + license
        ├── methodology/              # 7 files: 00-overview + 01-06 stage details
        ├── extractors/               # 5 parallel sub-agent prompts
        │   ├── framework-extractor.md
        │   ├── principle-extractor.md
        │   ├── case-extractor.md
        │   ├── counter-example-extractor.md
        │   └── glossary-extractor.md
        ├── templates/                # BOOK_OVERVIEW / SKILL / INDEX / test-prompts
        └── scripts/
            └── book_distill_init.sh  # bootstrap distill dir from book-extract output
```

## Requirements

- macOS or Linux (kobodl ships macOS binary auto-installed; Linux users
  can `pipx install kobodl` and override `TSUNDOKU_KOBO_BINARY`)
- Python 3.9+ (query / extract scripts use stdlib only)
- A Kobo account with at least one purchased book
- Optional: pandoc (for `book-extract` — auto-installed via brew or
  standalone GitHub release; no-op if already installed)
- Optional: [Calibre][calibre] for EPUB → PDF conversion

[calibre]: https://calibre-ebook.com/download_osx

## Security

- `kobodl.json` contains your **Kobo session credentials** — equivalent to a
  password. Never commit, paste into chat, or upload
- `kobo_login.sh` enforces `chmod 600` after every operation that touches
  the file
- Revoke a session by deleting `kobodl.json` AND visiting Kobo's
  [Authorized Devices](https://www.kobo.com/account/devices) page
- For shared machines, use a dedicated macOS user account

## Notes

- `book wishlist` subcommand currently broken upstream (kobodl 0.10.x); only
  `book list` is supported
- `Description` field is capped at 500 chars by Kobo's API (publisher ONIX
  copy, not a synopsis)
- macOS gets a pre-built kobodl binary auto-installed; Linux/Windows users
  install kobodl via `pipx install kobodl` and override `TSUNDOKU_KOBO_BINARY`
  after sourcing `tsundoku_paths.sh`

## Lineage

Generalizes the [`kobodl-library-sync.sh`][ancestor] single-file shell script
into a search-first toolkit with proper separation of auth, runtime, and
extraction; metadata-rich queries; chunked Markdown for LLM ingestion; and
a single-root storage layout under `~/.tsundoku/`.

[ancestor]: https://github.com/kouko/kobodl-library-sync
