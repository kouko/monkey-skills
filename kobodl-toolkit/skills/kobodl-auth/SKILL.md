---
name: kobodl-auth
description: >-
  First-time setup and credential management for the Kobo library toolkit.
  Installs the kobodl binary, runs the device-flow activation (kobo.com/activate
  + 6-digit code), stores credentials in XDG-style locations with mode 600, and
  supports importing existing kobodl.json from other tools. Use when the user
  needs to log into Kobo, re-authenticate after expiry, change Kobo accounts,
  or migrate credentials from a prior kobodl install. macOS only. Kobo 帳號登入
  と認証管理。Kobo帳號驗證・登入流程。
---

# Kobo Auth

Owns the **authentication lifecycle** for `kobodl-toolkit`. Separated from the
runtime `kobodl-library` skill because login is a once-per-account event,
while search/download is daily use.

This skill is **stateful** — its outcome is a credentials file on disk that
other skills depend on.

## When to Use

- Very first time using the toolkit (no credentials yet)
- `kobodl-library` reports "auth required"
- Switching to a different Kobo account
- Migrating from a previous kobodl install (e.g. the legacy
  `~/KobodlLibrarySync/` shell script)
- Auditing or rotating credentials

## Storage Layout (XDG-respecting, four-tier)

| Tier | What | Default path | Override env var |
|---|---|---|---|
| **Config** | Credentials | `~/.config/claude-kobodl/kobodl.json` | `KOBODL_HOME` |
| **Data** | Binary | `~/.local/share/claude-kobodl/bin/kobodl-macos` | `KOBODL_DATA` |
| **Data** | Tmp (PYI-1270 fix) | `~/.local/share/claude-kobodl/tmp/` | `KOBODL_DATA` |
| **Cache** | Library index (regenerable) | `~/.cache/claude-kobodl/library.json` | `KOBODL_CACHE` |
| **Cache** | Extracted markdown | `~/.cache/claude-kobodl/markdown/` | `KOBODL_CACHE` |
| **Visible** | EPUB downloads | `~/Books/kobo/` | `KOBODL_DOWNLOADS` |

`XDG_CONFIG_HOME` / `XDG_DATA_HOME` / `XDG_CACHE_HOME` are honored as
fallbacks; toolkit-specific `KOBODL_*` overrides win when both are set.

The cache tier holds **regenerable derived data** — safe to wipe at any time
(see `kobodl-extract:kobodl_cache_clear.sh`). It is intentionally NOT in the
config dir so dotfile-sync tools (chezmoi / dotdrop) won't accidentally
backup hundreds of megabytes of book content alongside settings.

**Permissions enforced:**
- `KOBODL_HOME` directory: `chmod 700` (owner-only)
- `kobodl.json` file: `chmod 600` (owner read/write only)
- All other locations: default permissions (binary is `755`)

**Independence**: This layout is intentionally separate from any prior install.
The legacy `~/KobodlLibrarySync/` directory is left untouched — see the
**Migration** section below for how to import from it.

## Helper Scripts

All in `scripts/`. Source `kobodl_paths.sh` first to populate path variables,
or invoke individual scripts directly (they source `kobodl_paths.sh`
internally).

| Script | Role |
|---|---|
| `kobodl_paths.sh` | Source-able OR runnable. Resolves and emits all path env vars |
| `kobodl_install.sh` | Downloads `kobodl-macos` to `KOBODL_DATA/bin/`. Idempotent |
| `kobodl_login.sh`   | Subcommand router — see below |

`kobodl_login.sh` subcommands:

| Subcommand | Effect |
|---|---|
| `status` (default) | Print `user list`; exit 0 if authed, 1 if not, 3 if binary missing |
| `add` | Run interactive `kobodl user add`; chmod 600 on success |
| `remove EMAIL` | Remove a user from the config |
| `import-from PATH` | Copy an existing `kobodl.json` into `$KOBODL_CONFIG` |
| `path` | Print the canonical config path and exit |

## Standard Flows

### Flow A — First-time setup (interactive activation)

```bash
# 1. Resolve paths into shell
source ${CLAUDE_SKILL_DIR}/scripts/kobodl_paths.sh

# 2. Install binary (no-op if already present)
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_install.sh

# 3. Start activation
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_login.sh add
```

When `kobodl_login.sh add` runs, kobodl prints something like:
```
Open https://www.kobo.com/activate and enter 123456.
```

**Claude must relay this code to the user clearly**, then wait for the command
to return. The user's job is:
1. Open `https://www.kobo.com/activate` in a browser
2. Sign in to their Kobo account
3. Enter the 6-digit code shown above
4. Wait — kobodl polls in the background and exits when activation completes

Do **not** cancel the command early. Polling can take up to ~60 seconds after
the user enters the code on the website.

On success:
- The script prints `[login] success — auth saved to <path> (mode 600)`
- `kobodl_login.sh status` returns exit 0 with the user's email

### Flow B — Migrate from existing kobodl install

If the user already authenticated via the legacy shell script
(`kobodl-library-sync.sh`) or an earlier kobodl install, their credentials
live at `~/KobodlLibrarySync/config/kobodl.json` (or wherever they pointed
`--config`). Skip the activation flow entirely:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_install.sh
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_login.sh \
    import-from ~/KobodlLibrarySync/config/kobodl.json
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_login.sh status
```

`import-from`:
- Backs up any existing config to `kobodl.json.bak.<timestamp>` first
- Copies the source file into `$KOBODL_CONFIG`
- Sets `chmod 600`
- Verifies via `user list` if the binary is installed

### Flow C — Verify auth state (idempotent check)

Use this as a precondition check from other skills:

```bash
if bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_login.sh status >/dev/null; then
    echo "auth ready"
else
    echo "auth required — invoke kobodl-auth Flow A or B"
fi
```

Exit codes:
- `0` — at least one user authed
- `1` — config missing or no user inside
- `3` — binary not installed yet (run `kobodl_install.sh` first)

### Flow D — Re-authenticate / rotate / switch account

```bash
# Add another account (kobodl supports multiple users in one config)
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_login.sh add

# Remove an old account
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_login.sh remove old@example.com

# Nuclear option — wipe and start over
rm "$KOBODL_CONFIG"
bash ${CLAUDE_SKILL_DIR}/scripts/kobodl_login.sh add
```

After removing credentials locally, the user should also visit Kobo's
**Authorized Devices** page and revoke the device entry to fully invalidate
the session token.

## Multi-User Notes

`kobodl.json` stores an array of users. Most kobodl commands accept
`-u EMAIL` or `-u USERKEY` to scope to a specific user. The `kobodl-library`
skill defaults to whichever user `book list` returns first — pass `-u` if
the user has multiple accounts and wants a specific one.

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `[login] activation did not complete` | User cancelled, code expired (10 min), or browser flow failed | Re-run `kobodl_login.sh add` |
| `Traceback ... PermissionError ... /var/folders/.../tmp` | PYI-1270 (PyInstaller temp dir issue) | Already handled — `kobodl_paths.sh` sets TMPDIR. If still failing, manually `export TMPDIR=$KOBODL_TMPDIR` |
| `xattr: ... No such xattr` | macOS quarantine flag absent | Harmless; install script suppresses |
| `book list` returns auth error after weeks | Session token expired | Run `kobodl_login.sh add` to refresh |
| `[install] downloaded file is suspiciously small` | GitHub returned 404 HTML | Check the release URL or pass `--url` to override |

## Security Reminders

- `kobodl.json` is equivalent to your Kobo session — treat as a password
- Never commit it, paste it into chat, or upload to a cloud service
- This skill enforces `chmod 600`, but you should also ensure your home
  directory isn't world-readable
- For shared machines, prefer using a unique macOS user account over relying
  on file permissions alone

## Cross-Skill Handoff

After successful auth, hand off to **`kobodl-library`** for the actual
search/download work. That skill assumes:
- `kobodl_paths.sh` is source-able (resolves paths)
- `kobodl_login.sh status` returns 0 (auth ready)
- `KOBODL_BINARY` is executable

If any precondition fails, route the user back to this skill.

## Reference

- kobodl: <https://github.com/subdavis/kobo-book-downloader>
- Kobo activation: <https://www.kobo.com/activate>
- Kobo Authorized Devices (revocation): <https://www.kobo.com/account/devices>
- XDG Base Directory Spec: <https://specifications.freedesktop.org/basedir-spec/>
