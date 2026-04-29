# tsundoku 積読

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Turn your owned-but-unread e-book pile into actionable agent skills — login, search, download, extract, distill.

> ⚠️ **Claude Code CLI only.** Cowork sandbox blocks `kobo.com` device-flow auth + EPUB downloads. See [Cowork compatibility](#cowork-compatibility) below.

**Version**: 0.11.0 · **License**: MIT · **Part of**: [monkey-skills](../README.md)

## Cowork compatibility

This plugin is **incompatible with Claude Desktop's Cowork tab**. Two of the four skills (`kobo-auth`, `kobo-library`) make outbound calls to `kobo.com` and `kobodl`'s download CDN, both of which sit outside Cowork's URL allowlist. The remaining skills (`book-extract`, `book-distill`) operate purely on local files and would work in Cowork, but the pipeline is only useful end-to-end.

Run this plugin from **Claude Code CLI** (or the Code tab embedded in Claude Desktop). The same sandbox finding documented for [`investing-toolkit`](../investing-toolkit/docs/mcp-setup.md) applies here.

## Background

積読 (tsundoku) is the Japanese word for the pile of books you bought, meant to read, and never opened. The pile compounds: each new purchase adds knowledge you owned but never extracted. This plugin treats that pile as the source — take an e-book you already paid for, surface it on demand, and convert it into reusable methodology your agent can invoke.

The pipeline is four stages, separated by stable on-disk artifacts so any stage can re-run independently:

```
kobo-auth ──▶ kobo-library ──▶ book-extract ──▶ book-distill
 (once)        (daily)           (per book)       (per book)

   login  ──▶  EPUB on disk ──▶ chunked .md  ──▶ atomic SKILL.md set
```

The split between `kobo-*` (Kobo-platform-specific) and `book-*` (format-agnostic) is deliberate: future siblings like `kindle-*` or `apple-books-*` would slot in alongside the `kobo-*` peers, while `book-extract` / `book-distill` accept any EPUB / Markdown directory regardless of source.

## Skills

| Skill | Layer | Role |
|---|---|---|
| [`tsundoku`](commands/tsundoku.md) | router | Routes to the right skill based on intent (login / search / convert / distill) |
| [`kobo-auth`](skills/kobo-auth/SKILL.md) | source-platform (`kobo-*`) | First-time setup, device-flow activation, credential rotation, multi-account |
| [`kobo-library`](skills/kobo-library/SKILL.md) | source-platform (`kobo-*`) | Search the Kobo library by title / author / series / publication date / category / description text / reading status / language; download chosen books as DRM-free EPUBs |
| [`book-extract`](skills/book-extract/SKILL.md) | format-agnostic (`book-*`) | EPUB → chunked-by-chapter Markdown via NCX-driven splitting; CJK-safe |
| [`book-distill`](skills/book-distill/SKILL.md) | format-agnostic (`book-*`) | Markdown → atomic SKILL.md set via RIA-TV++ (Adler analytical read → 5 parallel extractors → triple verification → RIA++ render → Zettelkasten linking → adversarial pressure test) |

**Naming convention**: `kobo-*` skills are bound to the Kobo platform (auth, library API, kobodl binary). `book-*` skills work on any EPUB or chunked Markdown, with no Kobo dependency. This means `book-extract` and `book-distill` are reusable on books you obtained any other way (manual EPUB drop, library loan, public domain).

## Quick start

Five common scenarios. The router skill picks for you if you describe the intent in natural language.

### A. Router — "I want to use tsundoku"

```
/tsundoku
```

Describes the four stages and asks which step to start with. First-time users should run B → C → D → E in sequence.

### B. First-time login (`kobo-auth`)

```
/tsundoku-kobo-auth
```

The skill installs the kobodl binary into `~/.tsundoku/kobo/bin/`, then **hands off the device-flow activation to your terminal** — kobodl prints a 6-digit code that you enter at `https://www.kobo.com/activate`, and running this through Claude's Bash tool buffers and truncates the code mid-flight. Claude waits for you to reply "done", then verifies via `kobo_login.sh status`.

If you already have a `kobodl.json` from a prior install:

```
"Import my existing kobodl credentials from ~/KobodlLibrarySync/config/kobodl.json"
```

### C. Search and download (`kobo-library`)

```
/tsundoku-kobo-library
```

Then describe what you want in natural language. Examples:

```
"Find books on behavioral economics published in the last five years that I haven't read"
"Show me everything in the Silent Witch series and download all of them"
"Books I bought more than two years ago and never started"
```

The skill maps your intent to `kobo_query.py` filters (title / author / series / publisher / `--description` keyword search across title + description text / `--pub-after` / `--purchased-after` / `--status` / `--language` / ...), presents matches as table / markdown cards / summary, asks you to confirm, then downloads via `kobodl book get` into `~/Books/kobo/`.

### D. Convert (`book-extract`)

```
/tsundoku-book-extract
```

Pass an EPUB path (it does not have to be from Kobo). The skill installs pandoc on first run, parses the EPUB's NCX (table of contents) for canonical chapter boundaries, pre-cleans Kobo-specific markup (`<span class="koboSpan">`), runs pandoc per chapter, and writes per-chapter Markdown into `~/.tsundoku/cache/markdown/<title-slug>-<id8>/`.

Output: `index.md` (TOC + per-chapter token estimates) + `metadata.json` + `NN-<chapter>.md` files.

### E. Distill (`book-distill`)

```
/tsundoku-book-distill
```

Distills the chunked Markdown into an atomic skill set via the **RIA-TV++** pipeline:

```
Stage 0: Adler analytical read           → BOOK_OVERVIEW.md
Stage 1: 5 parallel sub-agent extractors → frameworks / principles / cases /
                                            counter-examples / glossary
Stage 1.5: Triple verification filter    → ~30-50% pass for methodology-dense books
Stage 2: RIA++ render per skill          → SKILL.md per unit (R / I / A1 / A2 / E / B)
Stage 3: Zettelkasten linking            → INDEX.md + cross-refs
Stage 4: Adversarial pressure test       → test-prompts.json (lures non-negotiable)
```

Output is **language-adaptive**: if the source book is in Japanese, the resulting SKILL.md description and trigger signals are in Japanese, so Claude's activation matches natural user queries. R-field quotes are always verbatim source language.

## Under the hood

All four skills are thin wrappers over shell + Python scripts. You can invoke them directly without going through the skill if you prefer:

```bash
# Source path env vars (works from any skill's scripts/ directory)
source ~/.claude/plugins/cache/monkey-skills/tsundoku/0.11.0/skills/kobo-library/scripts/tsundoku_paths.sh

# Auth lifecycle
bash <skill-dir>/kobo-auth/scripts/kobo_install.sh           # install kobodl
bash <skill-dir>/kobo-auth/scripts/kobo_login.sh status      # 0=authed, 1=missing, 3=binary missing
bash <skill-dir>/kobo-auth/scripts/kobo_login.sh import-from PATH

# Search + download
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"
python3 <skill-dir>/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "behavioral economics,行為經濟" --pub-after 2020 --status ReadyToRead \
    --format markdown
bash <skill-dir>/kobo-library/scripts/kobo_get.sh "$REVISION_ID"

# Extract
bash <skill-dir>/book-extract/scripts/install_pandoc.sh
python3 <skill-dir>/book-extract/scripts/epub_to_markdown.py \
    --epub "$EPUB" --strip-images --strip-frontmatter

# Distill bootstrap
bash <skill-dir>/book-distill/scripts/book_distill_init.sh <book-slug-id8>
```

This keeps the skills auditable — nothing happens that you cannot reproduce by reading a script.

## Storage layout

Single root, per-platform subdirs. Future `kindle-*` / `apple-books-*` siblings would mirror the `kobo/` branch.

```
~/.tsundoku/                       ← TSUNDOKU_ROOT (default)
├── kobo/                            Kobo platform state
│   ├── auth/                         chmod 700
│   │   └── kobodl.json               chmod 600  (Kobo session credentials)
│   └── bin/kobodl-macos              ~14 MB upstream binary
├── tmp/                             shared TMPDIR override (PYI-1270 fix)
└── cache/                           regenerable, wipe-able as a unit
    ├── kobo/library.json             cached library export
    ├── markdown/<book>/...           EPUB → chunked Markdown (platform-agnostic)
    └── distilled/<book>/...          book-distill output

~/Books/kobo/                       ← TSUNDOKU_DOWNLOADS (user-visible EPUBs)
├── <author> - <title> <id8>.epub
└── ...
```

The `cache/` subtree is regenerable (re-export the library, re-extract the EPUBs); `auth/`, `bin/`, and `~/Books/kobo/` are not.

## Environment variables

Two decision-point variables you set; five derived paths the scripts compute. Override the two roots before sourcing `tsundoku_paths.sh`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `TSUNDOKU_ROOT` | No | `~/.tsundoku` | Root for auth, binary, cache, tmp |
| `TSUNDOKU_DOWNLOADS` | No | `~/Books/kobo` | User-visible EPUB downloads |
| `TSUNDOKU_TMPDIR` | derived | `$TSUNDOKU_ROOT/tmp` | TMPDIR override (PyInstaller PYI-1270 fix) |
| `TSUNDOKU_MARKDOWN_DIR` | derived | `$TSUNDOKU_ROOT/cache/markdown` | EPUB → Markdown output root |
| `TSUNDOKU_KOBO_CONFIG` | derived | `$TSUNDOKU_ROOT/kobo/auth/kobodl.json` | Kobo session credentials |
| `TSUNDOKU_KOBO_BINARY` | derived | `$TSUNDOKU_ROOT/kobo/bin/kobodl-macos` | kobodl CLI binary |
| `TSUNDOKU_KOBO_LIBRARY_JSON` | derived | `$TSUNDOKU_ROOT/cache/kobo/library.json` | Cached `book list --export-library` output |

Do not set the derived variables directly — change `TSUNDOKU_ROOT` instead.

## Repository structure

```
tsundoku/
├── .claude-plugin/
│   └── plugin.json
├── commands/                          slash-command surfaces
│   ├── tsundoku.md                     router
│   ├── kobo-auth.md
│   ├── kobo-library.md
│   ├── book-extract.md
│   └── book-distill.md
├── skills/
│   ├── kobo-auth/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── tsundoku_paths.sh       shared path resolver (copy)
│   │       ├── kobo_install.sh         download kobodl binary
│   │       └── kobo_login.sh           subcommand router (status / add / remove / import-from / path)
│   ├── kobo-library/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── tsundoku_paths.sh       shared path resolver (copy)
│   │       ├── kobo_query.py           filter + format library JSON
│   │       └── kobo_get.sh             download by RevisionId, idempotent
│   ├── book-extract/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── install_pandoc.sh       brew → standalone fallback
│   │       ├── epub_to_markdown.py     NCX-driven chapter splitter + pandoc
│   │       └── cache_clear.sh          wipe markdown / library cache
│   └── book-distill/
│       ├── SKILL.md
│       ├── ATTRIBUTION.md              cangjie-skill / nuwa-skill / Adler / RIA / Munger
│       ├── methodology/                  per-stage design rationale
│       │   ├── 00-overview.md
│       │   ├── 01-stage0-adler.md
│       │   ├── 02-stage1-parallel-extract.md
│       │   ├── 03-stage1.5-triple-verify.md
│       │   ├── 04-stage2-ria-plus.md
│       │   ├── 05-stage3-zettelkasten.md
│       │   └── 06-stage4-pressure-test.md
│       ├── extractors/                   5 parallel sub-agent prompts
│       │   ├── framework-extractor.md
│       │   ├── principle-extractor.md
│       │   ├── case-extractor.md
│       │   ├── counter-example-extractor.md
│       │   └── glossary-extractor.md
│       ├── templates/
│       └── scripts/
│           └── book_distill_init.sh
├── README.md
├── README.ja.md
└── README.zh-TW.md
```

## Requirements

| Requirement | Notes |
|---|---|
| **macOS** or **Linux** | `kobo-*` skills ship a macOS kobodl binary; Linux users `pipx install kobodl` and override `TSUNDOKU_KOBO_BINARY`. `book-*` skills are platform-agnostic. |
| **Python 3.9+** | stdlib only; no extra packages |
| **Kobo account** with purchased books | Required for `kobo-auth` / `kobo-library`. Trial / KoboPlus titles work too. |
| **pandoc** | Installed automatically by `book-extract/scripts/install_pandoc.sh` (Homebrew first, GitHub-release standalone fallback) |
| **Calibre** (optional) | Only needed for `kobo_get.sh --convert-pdf`. Install separately if you want PDF output alongside EPUB. |

Claude Code CLI is required for end-to-end use. Cowork tab will not work — see [Cowork compatibility](#cowork-compatibility).

## Security

`kobodl.json` holds your Kobo session token. **Treat it as a password.**

| Control | Enforced by | Notes |
|---|---|---|
| `chmod 700` on `~/.tsundoku/kobo/auth/` | `kobo_login.sh` on every write | Owner-only directory |
| `chmod 600` on `kobodl.json` | `kobo_login.sh` after `add` and `import-from` | Owner read/write only |
| Backup before overwrite (`import-from`) | `kobo_login.sh` | Writes `kobodl.json.bak.<timestamp>` |
| Multi-user scoping | `-u EMAIL` flag on every command | If `kobodl.json` holds multiple accounts |

**Do not** commit `kobodl.json`, paste it into chat, or upload it. To revoke a leaked or rotated session, sign in to Kobo and remove the device entry at <https://www.kobo.com/account/devices> — local file deletion alone does not invalidate the upstream token.

## Notes

- **kobodl bugs**: `book wishlist` is broken in kobodl 0.10.x and is not used. Removed books (`IsRemoved=True`) often fail to download and are excluded from query results by default.
- **Description cap**: Kobo's API truncates `Description` at 500 chars and serves it as HTML; `kobo_query.py` strips the HTML for matching and output. Treat descriptions as ONIX marketing copy, not synopses.
- **OS support**: macOS is the tested path. Linux works with `pipx install kobodl` plus a manual `TSUNDOKU_KOBO_BINARY` override. Windows is untested — accept PRs.
- **Furigana**: pandoc drops `<rt>` content by default, so Japanese ruby text is lost during EPUB → Markdown conversion. See [`waldeir/pandoc-filter-furigana`](https://github.com/waldeir/pandoc-filter-furigana) if you need it preserved.

## Lineage

- `kobo-auth` + `kobo-library` are forked from an earlier shell-script sync tool (`kobodl-library-sync.sh`, the `~/KobodlLibrarySync/` legacy directory). The `import-from` subcommand exists specifically to migrate users from that tool.
- `book-distill` is a fork of [`kangarooking/cangjie-skill` (蒼頡-skill)](https://github.com/kangarooking/cangjie-skill) (MIT, 2026), with full English translation, language-adaptive output, and an entry contract that auto-feeds from `book-extract`. The Triple Verification filter is itself adapted from [`alchaincyf/nuwa-skill`](https://github.com/alchaincyf/nuwa-skill). See [`skills/book-distill/ATTRIBUTION.md`](skills/book-distill/ATTRIBUTION.md) for the full credit chain (Adler / Luhmann / 趙周 RIA / Forte / Munger).
- `kobodl` itself is [`subdavis/kobo-book-downloader`](https://github.com/subdavis/kobo-book-downloader). This plugin only orchestrates it.

## Install

In Claude Code CLI:

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install tsundoku
```

Verify by invoking the router:

```
/tsundoku
```

Then run `/tsundoku-kobo-auth` to set up Kobo login.

## Contributing

- **Questions / bug reports**: open an issue at <https://github.com/kouko/monkey-skills/issues>.
- **PRs**: target `main`. Conventional Commits required. New skill content (especially `book-distill` methodology changes) needs primary-source citation in the commit body.
- **Cowork-related issues**: read the [Cowork compatibility](#cowork-compatibility) section first; it is almost certainly the documented sandbox limitation, not a plugin bug.

## License

MIT — see [LICENSE](../LICENSE) at the repository root.

`book-distill` carries an additional `Copyright (c) 2026 kangarooking` for the upstream cangjie-skill architecture; see [`skills/book-distill/ATTRIBUTION.md`](skills/book-distill/ATTRIBUTION.md).
