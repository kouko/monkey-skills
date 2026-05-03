# Source-Scope Contract — Whole-Vault Scan + Blacklist

`wiki-ingest` reads the **entire vault** recursively for `.md` files, then filters out two layers of exclusions: hardcoded system paths + user-configured directories from `.env`.

## Layer 1: Hardcoded always-excluded paths (NOT user-configurable)

| Path | Why excluded |
|---|---|
| `wiki/` | The output itself; ingesting it would loop forever |
| `.obsidian/` | Obsidian's config / plugin / cache directory — never user knowledge |
| `.trash/` | Obsidian's deleted-notes recycle bin |
| `.git/` | Version control internals |
| `node_modules/` | JS dependency directory (vault may include scripts) |
| `_raw/` | Convention for raw / unprocessed dumps (per `OBSIDIAN_RAW_DIR`) |

These are baked into [`scripts/scan-vault.sh`](../scripts/scan-vault.sh) and cannot be overridden via `.env`. Adding more system-level exclusions requires editing this file and the script.

## Layer 2: User-configured exclusions

From `.env` `OBSIDIAN_EXCLUDE_DIRS` (comma-separated, vault-relative; entries are **shell-glob patterns**, not just literal names).

Default after `/wiki-setup`: `daily,inbox` (skip flow notes and capture-only zones).

Common additions:
- `personal` — private notes
- `projects` — in-progress work
- `archive` — frozen old notes
- `_*` — any top-level dir starting with `_` (Obsidian convention for system / draft / asset folders)
- `temp?` — `temp1`, `temp2`, ...
- `[Aa]rchive` — case-variant `Archive` or `archive` (only meaningful on case-sensitive filesystems)

## Match rule (top-level only, glob-aware)

A file is excluded if its **vault-relative path's first segment matches any excluded glob pattern**.

- Only the **first path segment** is compared against the blacklist
- Nested directories with the same name are **NOT** excluded
- Match is **case-sensitive** in pattern interpretation (use `[Aa]` patterns or rely on FS case-insensitivity)
- Each entry in `OBSIDIAN_EXCLUDE_DIRS` is a shell glob:
  - `daily` — literal exact match (no wildcards = exact)
  - `_*` — any name starting with `_`
  - `*-archive` — any name ending in `-archive`
  - `temp?` — single-char wildcard
  - `[Aa]rchive` — char class

## Example scope resolution

Given `OBSIDIAN_EXCLUDE_DIRS=daily,inbox`:

```
vault/
├── daily/2026-05-03.md                ← EXCLUDED (top-level daily/, in user blacklist)
├── inbox/random-thought.md            ← EXCLUDED (top-level inbox/, in user blacklist)
├── wiki/entities/qlib.md              ← EXCLUDED (top-level wiki/, system)
├── .obsidian/workspace.json           ← EXCLUDED (top-level .obsidian/, system)
├── projects/old/daily/notes.md        ← INCLUDED (top-level is projects/, not daily/)
├── archive/inbox-2025/scratch.md      ← INCLUDED (top-level is archive/, not inbox/)
├── Daily/x.md                         ← INCLUDED (case-sensitive: Daily ≠ daily)
├── references/2026-04-20-paper.md     ← INCLUDED
├── research/MAB-survey.md             ← INCLUDED
├── lab/notebook.md                    ← INCLUDED
└── projects/billing-redesign.md       ← INCLUDED
```

Given `OBSIDIAN_EXCLUDE_DIRS=daily,inbox,_*` (glob — exclude all `_`-prefixed top-level dirs):

```
vault/
├── daily/note.md                      ← EXCLUDED (literal `daily`)
├── inbox/idea.md                      ← EXCLUDED (literal `inbox`)
├── _archive/old.md                    ← EXCLUDED (glob `_*` matches)
├── _drafts/wip.md                     ← EXCLUDED (glob `_*` matches)
├── _attachments/img.md                ← EXCLUDED (glob `_*` matches)
├── projects/old/_temp/note.md         ← INCLUDED (top-level is projects/, not _temp)
├── references/paper.md                ← INCLUDED
└── temp1/file.md                      ← INCLUDED (no `_` prefix)
```

This is intentional: a sub-folder named `daily/` or `_temp/` deep inside `projects/old/` is unrelated to the top-level folders. Top-level-only matching avoids accidental over-exclusion.

## Implementation: invoke the bundled scan script

Don't hand-roll a `find` command — use the bundled portable script:

```bash
bash <skill-root>/scripts/scan-vault.sh "$VAULT_ROOT"
```

The script reads `OBSIDIAN_EXCLUDE_DIRS` from the environment (or from `.env` if `set -a; . .env; set +a` is run first), normalizes input (trims whitespace + trailing slashes), and emits one absolute file path per line.

See [`scripts/scan-vault.sh`](../scripts/scan-vault.sh) for the full implementation. It works in `sh`, `bash`, `zsh` on macOS / Linux / BSD without bash 4 features.

## Boundary cases

| Scenario | Behavior |
|---|---|
| Vault root has loose `.md` files | Included (depth-1 files at vault root scan) |
| `.md` file inside `.obsidian/plugins/some-plugin/README.md` | EXCLUDED (under `.obsidian/`) |
| Hidden file at vault root like `.notes.md` | INCLUDED (only excluded dirs are filtered, not hidden files at root) |
| Symlink pointing into excluded dir | Behavior depends on `find` — by default symlinks are NOT followed, so the linked content is not scanned. If user needs symlink-following, add `-L` to `find` invocation in scan-vault.sh. |
| Empty `OBSIDIAN_EXCLUDE_DIRS=` in .env | Only system exclusions apply; user has explicitly opted in to whole-vault scan |
