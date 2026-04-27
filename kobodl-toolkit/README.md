# kobodl-toolkit

**Version**: 0.3.0
**Part of**: [monkey-skills](../)

Search a Kobo e-book library by **title / author / series / publication date /
category / description text / reading status / language**, present matches as
cards, then download the chosen books as DRM-free EPUBs. Wraps
[`subdavis/kobo-book-downloader`][kobodl] and exposes the rich library JSON
(Title / Authors / Publisher / Series / Description / Genre / Categories /
ReadingState / CoverImageUrl).

[kobodl]: https://github.com/subdavis/kobo-book-downloader

## Skills

| Skill | When to use |
|---|---|
| [`kobodl-auth`](skills/kobodl-auth/SKILL.md) | First-time setup, login, account migration, credential rotation |
| [`kobodl-library`](skills/kobodl-library/SKILL.md) | Daily use — search, list, batch-download EPUBs |

Auth is a separate skill because login is a one-time-per-account event while
search/download is daily.

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

## Storage Layout (XDG-respecting, owner-only)

| What | Default path | Override |
|---|---|---|
| Credentials (mode 600) | `~/.config/claude-kobodl/kobodl.json` | `KOBODL_HOME` |
| Binary | `~/.local/share/claude-kobodl/bin/kobodl-macos` | `KOBODL_DATA` |
| Library index | `~/.local/share/claude-kobodl/library.json` | `KOBODL_DATA` |
| Tmp | `~/.local/share/claude-kobodl/tmp/` | `KOBODL_DATA` |
| Downloads | `~/Books/kobo/` | `KOBODL_DOWNLOADS` |

`XDG_CONFIG_HOME` and `XDG_DATA_HOME` are honored. The toolkit-specific
overrides win when both are set.

The credentials directory is `chmod 700`, the file is `chmod 600`.
**Independent** of any prior install — the legacy `~/KobodlLibrarySync/`
directory is left untouched.

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
    └── kobodl-library/
        ├── SKILL.md
        └── scripts/
            ├── kobodl_query.py      # filter --export-library JSON, 5 formats
            └── kobodl_get.sh        # download by RevisionId (args or stdin)
```

## Requirements

- macOS (kobodl ships a macOS binary; auto-installed on first run)
- Python 3.9+ (query script uses stdlib only)
- A Kobo account with at least one purchased book
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
