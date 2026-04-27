# kobodl-toolkit

**Version**: 0.5.0
**Part of**: [monkey-skills](../)

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

Auth is a one-time event; library is daily search+download; extract is opt-in
post-processing for "I want Claude to read this book".

## Quick Start

### A. Brand-new setup (interactive activation)

```bash
# install binary + run device-flow login (opens kobo.com/activate code)
bash kobodl-toolkit/skills/kobodl-auth/scripts/kobodl_install.sh
bash kobodl-toolkit/skills/kobodl-auth/scripts/kobodl_login.sh add
```

Follow the prompts: open `https://www.kobo.com/activate` in a browser, sign in,
enter the 6-digit code shown by kobodl. The command auto-completes once the
activation registers.

### B. Migrate from existing kobodl install

If you already have credentials at `~/KobodlLibrarySync/config/kobodl.json`
(or another location), skip the activation flow:

```bash
bash kobodl-toolkit/skills/kobodl-auth/scripts/kobodl_install.sh
bash kobodl-toolkit/skills/kobodl-auth/scripts/kobodl_login.sh \
    import-from ~/KobodlLibrarySync/config/kobodl.json
```

### C. Search and download

```bash
source kobodl-toolkit/skills/kobodl-auth/scripts/kobodl_paths.sh
export TMPDIR="$KOBODL_TMPDIR"
mkdir -p "$KOBODL_DOWNLOADS"

# refresh library index
"$KOBODL_BINARY" --config "$KOBODL_CONFIG" \
    book list --export-library "$KOBODL_LIBRARY_JSON"

# search (e.g. "books that mention behavioral economics, published since 2020,
# not yet read") — preview as rich cards
python3 kobodl-toolkit/skills/kobodl-library/scripts/kobodl_query.py \
    --library "$KOBODL_LIBRARY_JSON" \
    --description "行為經濟,行為金融,Behavioral" \
    --pub-after 2020 --status ReadyToRead --format markdown

# download chosen RevisionIds (idempotent — skips books already on disk)
bash kobodl-toolkit/skills/kobodl-library/scripts/kobodl_get.sh "$REVISION_ID"

# or pipe a filtered set
python3 kobodl-toolkit/skills/kobodl-library/scripts/kobodl_query.py \
    --library "$KOBODL_LIBRARY_JSON" --series "Silent Witch" --format ids \
  | bash kobodl-toolkit/skills/kobodl-library/scripts/kobodl_get.sh --convert-pdf
```

### D. EPUB → chunked Markdown (for book→skill)

```bash
# one-time: ensure pandoc is installed
bash kobodl-toolkit/skills/kobodl-extract/scripts/install_pandoc.sh

# convert (uses $KOBODL_MARKDOWN_DIR by default — no --out-dir needed)
python3 kobodl-toolkit/skills/kobodl-extract/scripts/kobodl_to_markdown.py \
    --epub "$EPUB_PATH" --strip-images --strip-frontmatter
# → writes to ~/.cache/claude-kobodl/markdown/<title-slug>-<id8>/index.md + chapters

# clear the cache when finished with a book→skill task
bash kobodl-toolkit/skills/kobodl-extract/scripts/kobodl_cache_clear.sh
```

Then read `index.md` first (TOC + token estimates), distill into an outline,
and finally hand off to `dev-workflow:skill-creator-advance` to produce the
new skill.

## Storage Layout (XDG four-tier)

| Tier | What | Default path | Override |
|---|---|---|---|
| **Config** (chmod 700) | Credentials | `~/.config/claude-kobodl/kobodl.json` | `KOBODL_HOME` |
| **Data** | Binary | `~/.local/share/claude-kobodl/bin/kobodl-macos` | `KOBODL_DATA` |
| **Data** | Tmp (PYI-1270 fix) | `~/.local/share/claude-kobodl/tmp/` | `KOBODL_DATA` |
| **Cache** | Library index | `~/.cache/claude-kobodl/library.json` | `KOBODL_CACHE` |
| **Cache** | Extracted markdown | `~/.cache/claude-kobodl/markdown/<book>/` | `KOBODL_CACHE` |
| **Visible** | EPUB downloads | `~/Books/kobo/` | `KOBODL_DOWNLOADS` |

Three categories are intentionally separated:
- **Config**: secrets, owner-only, do not back up to dotfiles
- **Data**: binaries + persistent state
- **Cache**: regenerable derived data — safe to wipe, won't get pulled into
  dotfile syncs (chezmoi / dotdrop default-exclude `~/.cache/`)

`XDG_CONFIG_HOME` / `XDG_DATA_HOME` / `XDG_CACHE_HOME` are honored as
fallbacks. The legacy `~/KobodlLibrarySync/` directory is left untouched.

## Repository Structure

```
kobodl-toolkit/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    ├── kobodl-auth/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobodl_paths.sh      # source-able path resolver (shared)
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
  can `pipx install kobodl` and override `KOBODL_BINARY`)
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
- This toolkit is macOS-only by default. Linux/Windows users can install
  kobodl via `pipx install kobodl` and override `KOBODL_BINARY` after sourcing
  `kobodl_paths.sh`

## Lineage

Generalizes the [`kobodl-library-sync.sh`][ancestor] single-file shell script
into a search-first toolkit with proper separation of auth and runtime,
metadata-rich queries, and XDG-compliant credential storage.

[ancestor]: https://github.com/kouko/kobodl-library-sync
