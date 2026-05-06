# Source-Scope Contract — Whole-Vault Scan + Blacklist

`wiki-ingest` reads the **entire vault** recursively for `.md` files, then applies two parallel blacklists: a **DIR blacklist** (top-level only) and a **FILE blacklist** (any depth).

Each blacklist has two layers: hardcoded system defaults + user-configurable from `.obsidian-wiki.config`.

## DIR blacklist (top-level match)

### Layer 1: System hardcoded DIR excludes (NOT user-configurable)

| Pattern | Why excluded |
|---|---|
| `wiki/` | The output itself; ingesting it would loop forever |
| `.*` | Any top-level dir starting with `.` — by Unix / Obsidian convention these are hidden / system. Catches `.obsidian`, `.trash`, `.git`, `.github`, `.vscode`, `.idea`, `.claude`, `.cursor`, `.codex`, `.windsurf`, `.devcontainer`, `.husky`, `.changeset`, etc. — current and future tool config dirs |
| `node_modules/` | JS dependency directory (vault may include scripts) |
| `_raw/` | Convention for raw / unprocessed dumps (literal name; the `OBSIDIAN_WIKI_RAW_DIR` config key is advisory-only, not currently consumed) |

These are baked into [`scripts/scan-vault.sh`](../scripts/scan-vault.sh). Adding more system-level exclusions requires editing this file and the script.

**Why `.*` is hardcoded (not user-configurable)**: dot-prefix is a universal "hidden / system / not-for-users" marker. If a user deliberately created a `.foo/` directory, they signaled "this is not part of normal workflow" — by definition, it shouldn't be wiki-distilled. The override-flexibility argument is theoretical; in practice, no legitimate vault content lives in dot-prefixed directories. If exception is genuinely needed, user can rename the directory to remove the dot prefix.

### Layer 2: User-configured DIR excludes

From `<vault-root>/.obsidian-wiki.config`, key `OBSIDIAN_WIKI_EXCLUDE_DIRS` (multi-line, one shell-glob pattern per line within a quoted string).

Default after `/wiki-setup`: `daily`, `inbox` (skip flow notes and capture-only zones).

Common additions:
- `personal` — private notes
- `projects` — in-progress work
- `archive` — frozen old notes
- `_*` — any top-level dir starting with underscore (system / draft / asset folders)
- `temp?` — `temp1`, `temp2`, ...
- `[Aa]rchive` — case-variant `Archive` or `archive` (only meaningful on case-sensitive filesystems)

## FILE blacklist (any-depth match) — NEW in v3.9.0

Files are filtered by **basename**, applied at **any depth** in the vault tree. This is intentionally asymmetric from the DIR rule (top-level only) because filename conventions are location-independent (e.g., `CLAUDE.md` is agent config wherever it lives), whereas directory semantics are location-sensitive.

### Layer 1: System hardcoded FILE excludes (NOT user-configurable)

| Pattern | Why excluded |
|---|---|
| `CLAUDE.md` | Claude Code project instructions — agent config, not knowledge |
| `AGENT.md` | Generic agent instructions (various tools) |
| `AGENTS.md` | Codex / Cursor agent instructions variant |
| `MEMORY.md` | Agent memory dump |

Universal agent-config filenames. Even when nested (e.g., `projects/myapp/CLAUDE.md`), they're agent config, not user knowledge.

### Layer 2: User-configured FILE excludes

From `<vault-root>/.obsidian-wiki.config`, key `OBSIDIAN_WIKI_EXCLUDE_FILES` (same multi-line glob format as DIR list).

Default: empty.

Common additions:
- `README.md` — repo metadata (border case: some Obsidian users use it as vault landing page; opt-in)
- `TODO.md` — task lists, not knowledge
- `CHANGELOG.md` — release notes, not knowledge
- `LICENSE.md` — legal text, not knowledge
- `*.draft.md` — draft files (glob)
- `[A-Z]*.md` (broad — exclude all uppercase-prefix at root; aggressive)

### Root-level hidden files

`.notes.md` and any other root-level `.md` file starting with `.` are auto-excluded (parallels the `.*` DIR rule). This is hardcoded; not user-configurable.

## Match rule asymmetry summary

| Rule | Match scope | Why |
|---|---|---|
| DIR exclude | Top-level only | Directory semantics are location-sensitive (`projects/old/daily/` is unrelated to top-level `daily/`) |
| FILE exclude | Any depth | Filename conventions are location-independent (`CLAUDE.md` is agent config wherever it lives) |

## Why a custom config file (NOT `.env`)

`.obsidian-wiki.config` (introduced in v3.8.0) replaced the old `.env` to avoid:

- Claude Code permission rules that block `**/*.env` reads
- Anti-secret tooling false positives (gitleaks / trufflehog default-scan `.env`)
- `.gitignore` default templates including `.env`
- Naming collision with vault-local dev workspace `.env` files

The `.obsidian-wiki.config` filename matches none of these patterns. It's still shell-sourceable (`set -a; . .obsidian-wiki.config; set +a`) so zero new dependencies.

## Multi-line value format

`OBSIDIAN_WIKI_EXCLUDE_DIRS` uses one pattern per line within a quoted multi-line string. This means patterns may contain commas, spaces, or CJK characters without escaping — only literal newlines are forbidden (filesystems disallow them anyway).

```bash
OBSIDIAN_WIKI_EXCLUDE_DIRS="daily
inbox
_*
notes, with comma
資料夾 with spaces
[Aa]rchive"
```

## Match rule (top-level only, glob-aware, special-char safe)

A file is excluded if its **vault-relative path's first segment matches any excluded glob pattern**.

- Only the **first path segment** is compared
- Nested directories with the same name are **NOT** excluded
- Match is **case-sensitive** in pattern interpretation (use `[Aa]` patterns or rely on FS case-insensitivity)
- Special characters (commas, spaces, CJK) in pattern values are safe because of the multi-line storage format
- Each entry is a shell glob:
  - `daily` — literal exact match (no wildcards = exact)
  - `_*` — any name starting with `_`
  - `*-archive` — any name ending in `-archive`
  - `temp?` — single-char wildcard
  - `[Aa]rchive` — char class

## Example scope resolution

Given `OBSIDIAN_WIKI_EXCLUDE_DIRS="daily\ninbox"`:

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

Given `OBSIDIAN_WIKI_EXCLUDE_DIRS="daily\ninbox\n_*"` (glob — exclude all `_`-prefixed top-level dirs):

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

Given `OBSIDIAN_WIKI_EXCLUDE_DIRS="notes, with comma\n資料夾 with spaces"` (special chars):

```
vault/
├── notes, with comma/x.md             ← EXCLUDED (special chars handled — no escape needed)
├── 資料夾 with spaces/y.md             ← EXCLUDED (CJK + spaces handled)
└── references/paper.md                ← INCLUDED
```

This is intentional: a sub-folder named `daily/` or `_temp/` deep inside `projects/old/` is unrelated to the top-level folders. Top-level-only matching avoids accidental over-exclusion.

## Implementation: invoke the bundled scan script

Don't hand-roll a `find` command — use the bundled portable script:

```bash
bash <skill-root>/scripts/scan-vault.sh "$VAULT_ROOT"
```

The script **auto-sources** `<vault-root>/.obsidian-wiki.config` to read `OBSIDIAN_WIKI_EXCLUDE_DIRS` — no need to source it manually. It normalizes input (trims whitespace + trailing slashes), handles multi-line values, and emits one absolute file path per line.

If the config file is missing, the script falls back to the env var directly (useful for testing).

See [`scripts/scan-vault.sh`](../scripts/scan-vault.sh) for the full implementation. Pure POSIX `sh` — works on macOS / Linux / BSD without bash 4 features.

## Boundary cases

| Scenario | Behavior |
|---|---|
| Vault root has loose `.md` files | Included (depth-1 files at vault root scan) |
| `.md` file inside `.obsidian/plugins/some-plugin/README.md` | EXCLUDED (under `.obsidian/`) |
| Hidden file at vault root like `.notes.md` | EXCLUDED (v3.9.0+) — root-level hidden files are auto-filtered to mirror the `.*` DIR rule |
| File `CLAUDE.md` / `AGENT.md` / `AGENTS.md` / `MEMORY.md` at any depth | EXCLUDED (v3.9.0+) — system FILE blacklist, applies at any depth |
| Custom user-defined excluded files (e.g. `README.md`, `TODO.md`) | EXCLUDED if listed in `OBSIDIAN_WIKI_EXCLUDE_FILES` (v3.9.0+) |
| Symlink pointing into excluded dir | Behavior depends on `find` — by default symlinks are NOT followed, so the linked content is not scanned. If user needs symlink-following, add `-L` to `find` invocation in scan-vault.sh. |
| Empty `OBSIDIAN_WIKI_EXCLUDE_DIRS=""` | Only system exclusions apply; user has explicitly opted in to whole-vault scan |
| Directory name with literal commas / spaces / CJK | Handled — multi-line value format keeps each pattern intact |
| Legacy `.env` config still present (v3.7.0 or earlier) | scan-vault.sh ignores it; user should run `/wiki-setup` to migrate to `.obsidian-wiki.config` |
