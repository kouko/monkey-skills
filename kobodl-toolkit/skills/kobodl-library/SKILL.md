---
name: kobodl-library
description: >-
  Search a user's Kobo e-book library by title / author / series / publication
  date / category / description text / reading status / language, present
  matches to the user, and download the chosen books as DRM-free EPUBs via
  kobodl. Wraps subdavis/kobo-book-downloader and exposes the rich library
  JSON (Title / Authors / Publisher / Series / ISBN / Description / Genre /
  Categories / ReadingState / CoverImageUrl). macOS only. Requires
  `kobodl-auth` to have run first. Use when the user wants to find a specific
  book or a set of books from their Kobo library and download them. 電子書庫
  搜尋・下載・條件絞り込み。
---

# Kobo Library

Runtime skill for **search-then-download** over the user's Kobo library.
Authentication is owned by **`kobodl-auth`** — this skill assumes auth is
ready and exits with a hint if it isn't.

The intended user-facing flow:
1. User describes what they're looking for (title / author / topic / year)
2. Skill resolves filters, queries the library, presents matches as cards
3. User confirms which books to download
4. Skill downloads the chosen RevisionIds (idempotent, DRM-free EPUBs)

## Pre-conditions

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/kobodl-auth/scripts/kobodl_login.sh status \
    >/dev/null || { echo "auth required — see kobodl-auth skill"; exit 1; }
```

If status fails, route the user to the `kobodl-auth` skill (Flow A for new
login, Flow B for migration).

## Path Resolution

All paths come from `kobodl-auth/scripts/kobodl_paths.sh`. Source it once:

```bash
source ${CLAUDE_PLUGIN_ROOT}/skills/kobodl-auth/scripts/kobodl_paths.sh
export TMPDIR="$KOBODL_TMPDIR"
mkdir -p "$KOBODL_DOWNLOADS" "$KOBODL_TMPDIR"
```

Override with `KOBODL_HOME` / `KOBODL_DATA` / `KOBODL_DOWNLOADS` env vars
before sourcing.

## Components

| Path | Role |
|---|---|
| `scripts/kobodl_query.py` | Filter `--export-library` JSON, multiple output formats |
| `scripts/kobodl_get.sh` | Download books by RevisionId (args or stdin), idempotent |
| `$KOBODL_BINARY` | The kobodl CLI itself |
| `$KOBODL_LIBRARY_JSON` | Local cache of the user's library |

## Workflow — Search → Confirm → Download

### Step 1 — Refresh the library index (once per session)

```bash
"$KOBODL_BINARY" --config "$KOBODL_CONFIG" \
    book list --export-library "$KOBODL_LIBRARY_JSON"
```

Run this whenever the user mentions newly-purchased books, or if it has been
days since the last query. The export call is the only authoritative source —
table output drops 95% of the metadata.

### Step 2 — Translate user intent into query filters

Map the user's natural-language request to `kobodl_query.py` filters:

| User says | Filter |
|---|---|
| "找書名有 X 的" | `--title X` |
| "X 寫的" / "X 翻譯的" | `--author X` |
| "X 系列的" / "X 全部" | `--series X` |
| "X 出版社" / "X 文化" | `--publisher X` |
| "簡介提到 X" / "關於 X 的書" | `--description X` (multi-keyword OR: `X,Y,Z`) |
| "簡介同時提到 X 和 Y" | `--description-all X,Y` |
| "2020 年以後的書" | `--pub-after 2020` |
| "2024 年出版的" | `--pub-after 2024 --pub-before 2024` |
| "已讀完的" / "讀過的" | `--status Finished` |
| "在讀的" | `--status Reading` |
| "還沒讀過的" | `--status ReadyToRead` |
| "日文 / 中文書" | `--language ja` / `--language zh` |
| "讀超過一半的" | `--min-progress 50` |
| "ISBN 是 X" | `--isbn X` |
| "RevisionId 是 X" | `--revision-id X` |

Multiple filters AND-combine. Run `kobodl_query.py --help` for the full list.

**`--description` is the killer feature** — it greps the cleaned description
text. Use it for topic / theme / subject queries that don't appear in the
title:

```bash
# Books with "AI" / "人工智慧" / "機器學習" anywhere in title or description
python3 ${CLAUDE_SKILL_DIR}/scripts/kobodl_query.py \
    --library "$KOBODL_LIBRARY_JSON" \
    --description "AI,人工智慧,機器學習,大數據"
```

### Step 3 — Present matches to the user

Three presentation styles depending on context:

```bash
# Compact list (use when many matches, user just wants to scan)
python3 kobodl_query.py --library "$KOBODL_LIBRARY_JSON" [filters] \
    --format table --sort pub_date

# Rich card with cover + description (use when a few matches)
python3 kobodl_query.py --library "$KOBODL_LIBRARY_JSON" [filters] \
    --format markdown --limit 5

# Aggregate stats (use when user wants overview before deciding)
python3 kobodl_query.py --library "$KOBODL_LIBRARY_JSON" [filters] \
    --format summary
```

After showing results, **ask the user which to download** — by number, title,
or "all of them". Translate their choice into a list of RevisionIds.

### Step 4 — Download the chosen books

`kobodl_get.sh` accepts RevisionIds via positional args OR stdin.
Skips books whose `<id8>.epub` already exists in `$KOBODL_DOWNLOADS`.

```bash
# Single book (positional)
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_get.sh "$REVISION_ID"

# Multiple books (positional, space-separated)
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_get.sh "$ID1" "$ID2" "$ID3"

# Pipe from query (most common — filtered set)
python3 ${CLAUDE_SKILL_DIR}/scripts/kobodl_query.py \
    --library "$KOBODL_LIBRARY_JSON" --series "Silent Witch" --format ids \
  | bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_get.sh

# Preview before committing (show what would download)
python3 ${CLAUDE_SKILL_DIR}/scripts/kobodl_query.py [...] --format ids \
  | bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_get.sh --dry-run

# Convert each to PDF after download (requires Calibre)
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_get.sh --convert-pdf "$REVISION_ID"

# Custom output directory for this run
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_get.sh --output-dir ~/Books/research "$ID"
```

Output:
- **stdout**: one line per book — the absolute EPUB path (so callers can chain)
- **stderr**: progress, skip messages, and a summary footer

Exit codes: `0` = all attempted books succeeded or were already present;
`1` = at least one download failed.

## Filter Reference

`kobodl_query.py` filters (all optional, AND-combined):

| Filter | Notes |
|---|---|
| `--title PATTERN` | substring on Title (case-insensitive) |
| `--author PATTERN` | substring on any contributor name |
| `--series PATTERN` | substring on series name |
| `--description PATTERN` | comma-separated keywords; **ANY** match (haystack = title + subtitle + description) |
| `--description-all PATTERN` | comma-separated keywords; **ALL** must match |
| `--status Finished\|Reading\|ReadyToRead` | reading state |
| `--language CODE` | metadata language (`zh` / `ja` / `en` ...) |
| `--country CODE` | locale country (`tw` / `jp` / `us` ...) |
| `--publisher PATTERN` | publisher name |
| `--isbn ISBN` | exact ISBN |
| `--pub-after YYYY[-MM[-DD]]` | publication date >= |
| `--pub-before YYYY[-MM[-DD]]` | publication date <= |
| `--genre UUID` | exact UUID match on `BookMetadata.Genre` |
| `--category UUID` | UUID present in `BookMetadata.Categories` |
| `--revision-id UUID` | exact RevisionId (for resolving a single book) |
| `--min-progress N` / `--max-progress N` | progress 0-100 |
| `--include-removed` | include archived books (default: excluded) |

Output formats:
- `table` (default) — CJK-aware columns
- `json` — full structured data, description HTML stripped
- `ids` — one RevisionId per line, pipe to `kobodl_get.sh`
- `markdown` — Obsidian-friendly card with cover + description
- `summary` — count / status / language / top series / total reading minutes

Sort keys (ascending): `title` / `author` / `series` / `pub_date`, or
descending for `progress` / `spent`.

## Library JSON Reference

`kobodl --export-library` produces an array of `{NewEntitlement: {...}}`.
Three subobjects per entry:

```
NewEntitlement
├─ BookEntitlement   { RevisionId, IsRemoved, IsHidden, OriginCategory, ... }
├─ BookMetadata      { Title, Subtitle, Description (HTML, ≤500 chars),
│                      Contributors, Publisher.Name, Series {Name, Number},
│                      Isbn, Language, Locale, PublicationDate,
│                      Genre, Categories, CoverImageUrl, ... }
└─ ReadingState      { StatusInfo.Status, ProgressPercent, SpentReadingMinutes,
                       LastTimeFinished, ... }
```

**Caveats**:
- `Description` is HTML; `kobodl_query.py` strips it for matching/output.
  Cap is 500 chars (Kobo API truncation).
- `CoverImageUrl` is protocol-relative (`//cdn...`); query script prepends
  `https:` automatically.
- `RevisionId` is what `book get` accepts. `CrossRevisionId` is stable across
  re-purchased editions.
- `Genre` / `Categories` are UUIDs without resolved human names — pass through
  if the user has a known UUID, otherwise prefer description / title search.
- `book wishlist` subcommand has an upstream bug (kobodl 0.10.x) — not used.

## Worked Example

User: "找一本講行為經濟學的，最近五年內出版的，我還沒讀過的"

```bash
# Step 1: refresh
"$KOBODL_BINARY" --config "$KOBODL_CONFIG" \
    book list --export-library "$KOBODL_LIBRARY_JSON"

# Step 2: query
python3 ${CLAUDE_SKILL_DIR}/scripts/kobodl_query.py \
    --library "$KOBODL_LIBRARY_JSON" \
    --description "行為經濟,行為金融,經濟學家,Behavioral" \
    --pub-after 2020 \
    --status ReadyToRead \
    --format markdown

# Step 3: present cards to user; user picks book #2

# Step 4: download
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_get.sh "$picked_id"
```

## Multi-User

If `kobodl.json` holds multiple Kobo accounts, scope every command:

```bash
"$KOBODL_BINARY" --config "$KOBODL_CONFIG" book list \
    -u alice@example.com --export-library "$KOBODL_LIBRARY_JSON"

bash kobodl_get.sh --user alice@example.com "$REVISION_ID"
```

## Warnings

- `Description` is **publisher ONIX copy**, not a true synopsis — marketing
  flavored, may contain spoilers, max 500 chars
- Removed books (`IsRemoved=True`) often fail to download — excluded by default
- This skill is macOS-specific. Linux/Windows users install kobodl via
  `pipx install kobodl` and override `KOBODL_BINARY` after sourcing
  `kobodl_paths.sh`

## Cross-Skill Handoff

This skill is **data layer only**. For analysis or note generation:

- `obsidian:obsidian-markdown` — turn `--format markdown` output into vault notes
- `obsidian:obsidian-file-intel` — process downloaded EPUBs into summaries
- A custom LLM prompt — feed `--format json` (descriptions are pre-cleaned)

## Reference

- kobodl upstream: <https://github.com/subdavis/kobo-book-downloader>
- Calibre: <https://calibre-ebook.com/download_osx>
