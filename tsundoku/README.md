# tsundoku 積読

**Version**: 0.6.0
**Part of**: [monkey-skills](../)

> *tsundoku (積読)* — Japanese for the books you've bought but haven't read yet.
> This plugin turns that pile into actionable knowledge.

Search a Kobo e-book library by **title / author / series / publication date /
category / description text / reading status / language**, present matches as
cards, download the chosen books as DRM-free EPUBs, then convert downloaded
EPUBs into chunked-by-chapter Markdown for LLM ingestion (book → skill
workflow). Wraps [`subdavis/kobo-book-downloader`][kobodl] and uses
[pandoc][pandoc] for the EPUB→Markdown stage.

[kobodl]: https://github.com/subdavis/kobo-book-downloader
[pandoc]: https://pandoc.org

## Skills

| Skill | When to use |
|---|---|
| [`kobodl-auth`](skills/kobodl-auth/SKILL.md) | First-time setup, login, account migration, credential rotation |
| [`kobodl-library`](skills/kobodl-library/SKILL.md) | Daily use — search, list, batch-download EPUBs |
| [`kobodl-extract`](skills/kobodl-extract/SKILL.md) | Convert EPUB → chunked-by-chapter Markdown (for book→skill, RAG, Obsidian notes) |

Skills are named after the upstream tool they wrap (`kobodl`). The plugin
itself is the brand umbrella, ready to grow toward other sources (Kindle,
Apple Books) later.

## Quick Start

### A. Brand-new setup (interactive activation)

```bash
# install binary + run device-flow login (opens kobo.com/activate code)
bash tsundoku/skills/kobodl-auth/scripts/kobodl_install.sh
bash tsundoku/skills/kobodl-auth/scripts/kobodl_login.sh add
```

Follow the prompts: open `https://www.kobo.com/activate` in a browser, sign in,
enter the 6-digit code shown by kobodl. The command auto-completes once the
activation registers.

### B. Migrate from existing kobodl install

If you already have credentials elsewhere (e.g. legacy `~/KobodlLibrarySync/`
shell script, or upstream's `~/.config/kobodl/`), skip the activation flow:

```bash
bash tsundoku/skills/kobodl-auth/scripts/kobodl_install.sh
bash tsundoku/skills/kobodl-auth/scripts/kobodl_login.sh \
    import-from ~/KobodlLibrarySync/config/kobodl.json
```

### C. Search and download

```bash
source tsundoku/lib/tsundoku_paths.sh
export TMPDIR="$TSUNDOKU_TMPDIR"
mkdir -p "$TSUNDOKU_DOWNLOADS"

# refresh library index
"$TSUNDOKU_BINARY" --config "$TSUNDOKU_CONFIG" \
    book list --export-library "$TSUNDOKU_LIBRARY_JSON"

# search (e.g. "books that mention behavioral economics, published since 2020,
# not yet read") — preview as rich cards
python3 tsundoku/skills/kobodl-library/scripts/kobodl_query.py \
    --library "$TSUNDOKU_LIBRARY_JSON" \
    --description "行為經濟,行為金融,Behavioral" \
    --pub-after 2020 --status ReadyToRead --format markdown

# download chosen RevisionIds (idempotent — skips books already on disk)
bash tsundoku/skills/kobodl-library/scripts/kobodl_get.sh "$REVISION_ID"

# or pipe a filtered set
python3 tsundoku/skills/kobodl-library/scripts/kobodl_query.py \
    --library "$TSUNDOKU_LIBRARY_JSON" --series "Silent Witch" --format ids \
  | bash tsundoku/skills/kobodl-library/scripts/kobodl_get.sh --convert-pdf
```

### D. EPUB → chunked Markdown (for book→skill)

```bash
# one-time: ensure pandoc is installed
bash tsundoku/skills/kobodl-extract/scripts/install_pandoc.sh

# convert (uses $TSUNDOKU_MARKDOWN_DIR by default — no --out-dir needed)
python3 tsundoku/skills/kobodl-extract/scripts/kobodl_to_markdown.py \
    --epub "$EPUB_PATH" --strip-images --strip-frontmatter
# → writes to ~/.tsundoku/cache/markdown/<title-slug>-<id8>/index.md + chapters

# clear the cache when finished with a book→skill task
bash tsundoku/skills/kobodl-extract/scripts/kobodl_cache_clear.sh
```

Then read `index.md` first (TOC + token estimates), distill into an outline,
and finally hand off to `dev-workflow:skill-creator-advance` to produce the
new skill.

## Storage Layout (single root)

```
~/.tsundoku/                  ← TSUNDOKU_ROOT
├── auth/                       chmod 700
│   └── kobodl.json             chmod 600  (Kobo session credentials)
├── bin/kobodl-macos
├── tmp/                        TMPDIR override (PYI-1270 fix)
└── cache/                      regenerable, wipe-able as a unit
    ├── library.json
    └── markdown/<book>/...

~/Books/kobo/                 ← TSUNDOKU_DOWNLOADS (user-visible EPUBs)
```

**Two decision-point env vars** — set these to relocate things:

| Var | Default | Purpose |
|---|---|---|
| `TSUNDOKU_ROOT` | `~/.tsundoku` | All toolkit state (auth + binary + cache) |
| `TSUNDOKU_DOWNLOADS` | `~/Books/kobo` | User-visible EPUB downloads |

**Five derived paths** computed from the two above (don't set directly):
`TSUNDOKU_CONFIG`, `TSUNDOKU_BINARY`, `TSUNDOKU_LIBRARY_JSON`,
`TSUNDOKU_MARKDOWN_DIR`, `TSUNDOKU_TMPDIR`. They're exported for convenience
when sourcing `lib/tsundoku_paths.sh`.

The `auth/` subdirectory is `chmod 700`, the `kobodl.json` file is `chmod 600`.
The `cache/` subtree is regenerable — wipe at any time via
`kobodl-extract/scripts/kobodl_cache_clear.sh`.

## Repository Structure

```
tsundoku/
├── .claude-plugin/plugin.json
├── README.md
├── lib/
│   └── tsundoku_paths.sh        # plugin-wide path resolver (source-able)
└── skills/
    ├── kobodl-auth/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobodl_install.sh    # binary download (idempotent)
    │       └── kobodl_login.sh      # add / status / remove / import-from / path
    ├── kobodl-library/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobodl_query.py      # filter --export-library JSON, 5 formats
    │       └── kobodl_get.sh        # download by RevisionId (args or stdin)
    └── kobodl-extract/
        ├── SKILL.md
        └── scripts/
            ├── install_pandoc.sh     # brew → standalone fallback
            ├── kobodl_to_markdown.py # NCX-driven chapter split + pandoc + clean
            └── kobodl_cache_clear.sh # wipe extracted markdown / library cache
```

## Requirements

- macOS or Linux (kobodl ships macOS binary auto-installed; Linux users
  can `pipx install kobodl` and override `TSUNDOKU_BINARY`)
- Python 3.9+ (query / extract scripts use stdlib only)
- A Kobo account with at least one purchased book
- Optional: pandoc (for `kobodl-extract` — auto-installed via brew or
  standalone GitHub release; no-op if already installed)
- Optional: [Calibre][calibre] for EPUB → PDF conversion

[calibre]: https://calibre-ebook.com/download_osx

## Security

- `kobodl.json` contains your **Kobo session credentials** — equivalent to a
  password. Never commit, paste into chat, or upload
- `kobodl_login.sh` enforces `chmod 600` after every operation that touches
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
  install kobodl via `pipx install kobodl` and override `TSUNDOKU_BINARY`
  after sourcing `tsundoku_paths.sh`

## Lineage

Generalizes the [`kobodl-library-sync.sh`][ancestor] single-file shell script
into a search-first toolkit with proper separation of auth, runtime, and
extraction; metadata-rich queries; chunked Markdown for LLM ingestion; and
a single-root storage layout under `~/.tsundoku/`.

[ancestor]: https://github.com/kouko/kobodl-library-sync
