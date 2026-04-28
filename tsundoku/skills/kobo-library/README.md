# kobo-library

> Search a Kobo e-book library by 10+ filter axes, present matches as cards,
> download the chosen books as DRM-free EPUBs.

Part of the [tsundoku](../..) plugin. Skill spec Claude loads is
[`SKILL.md`](SKILL.md); this README is for humans.

## What it does

The user-facing flow:

```
"Find a behavioral economics book from the last 5 years that I haven't read"
                              ↓
                kobo_query.py filters local library JSON
                              ↓
                cards (markdown / table / summary / ids)
                              ↓
                "Looks good — download #2 and #5"
                              ↓
                kobo_get.sh downloads chosen RevisionIds
                              ↓
                DRM-free .epub files in ~/Books/kobo/
```

## Pre-condition

[`kobo-auth`](../kobo-auth) must have run successfully. If
`bash ../kobo-auth/scripts/kobo_login.sh status` doesn't return 0, do that
first.

## Quick start

```bash
# Source paths (gets TSUNDOKU_KOBO_BINARY / _CONFIG / _LIBRARY_JSON / etc.)
source scripts/tsundoku_paths.sh
mkdir -p "$TSUNDOKU_DOWNLOADS"

# Refresh the library index (export Kobo's metadata to local JSON)
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"

# Search — preview as cards
python3 scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "行為經濟,Behavioral" \
    --pub-after 2020 --status ReadyToRead \
    --format markdown

# Download chosen RevisionIds
bash scripts/kobo_get.sh "$REVISION_ID"

# Or batch via pipe
python3 scripts/kobo_query.py --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --series "Silent Witch" --format ids \
  | bash scripts/kobo_get.sh
```

## Filters supported by `kobo_query.py`

| Filter | Effect |
|---|---|
| `--title PATTERN` | substring match on Title |
| `--author PATTERN` | substring match on any contributor |
| `--series PATTERN` | substring match on series name |
| `--description PATTERN` | full-text on cleaned description (comma = OR) |
| `--description-all PATTERN` | comma keywords; ALL must match |
| `--status` | `Finished` / `Reading` / `ReadyToRead` |
| `--language CODE` | `zh` / `ja` / `en` ... |
| `--country CODE` | `tw` / `jp` / `us` ... |
| `--publisher PATTERN` | substring on publisher name |
| `--isbn ISBN` | exact ISBN |
| `--pub-after YYYY[-MM[-DD]]` | publication date >= |
| `--pub-before YYYY[-MM[-DD]]` | publication date <= |
| `--genre UUID` / `--category UUID` | UUID match (advanced) |
| `--min-progress N` / `--max-progress N` | reading progress 0-100 |

Output formats: `table` / `json` / `ids` / `markdown` / `summary`.
All filters AND-combined.

## Files in this folder

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | Skill spec Claude loads (full filter / output reference) |
| [`scripts/kobo_query.py`](scripts/kobo_query.py) | Filter library JSON, 5 output formats. Pure stdlib |
| [`scripts/kobo_get.sh`](scripts/kobo_get.sh) | Download by RevisionId (args or stdin pipe), idempotent skip |

## Output destinations

```
~/Books/kobo/
└── <author> - <title> <id8>.epub      ← user-visible, DRM-free
```

EPUBs are DRM-free out of the box (kobodl decrypts on download).

## See also

- [`kobo-auth`](../kobo-auth) — login first
- [`book-extract`](../book-extract) — natural next step: turn the EPUB into
  chunked Markdown for LLM ingestion
- [`tsundoku` README](../..) — full pipeline overview
