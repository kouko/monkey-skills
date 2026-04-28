---
name: kobo-auth
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

Owns the **authentication lifecycle** for `tsundoku`. Separated from the
runtime `kobo-library` skill because login is a once-per-account event,
while search/download is daily use.

This skill is **stateful** — its outcome is a credentials file on disk that
other skills depend on.

## When to Use

- Very first time using the toolkit (no credentials yet)
- `kobo-library` reports "auth required"
- Switching to a different Kobo account
- Migrating from a previous kobodl install (e.g. the legacy
  `~/KobodlLibrarySync/` shell script)
- Auditing or rotating credentials

## Storage Layout (single root, per-platform subdirs)

```
~/.tsundoku/                     ← TSUNDOKU_ROOT
├── kobo/                          Kobo platform state
│   ├── auth/                       chmod 700
│   │   └── kobodl.json             chmod 600  (Kobo session credentials)
│   └── bin/kobodl-macos            14 MB upstream binary
├── tmp/                           shared TMPDIR override (PYI-1270 fix)
└── cache/                         regenerable, wipe-able as a unit
    ├── kobo/library.json           cached library export
    └── markdown/<book>/...         EPUB → MD (platform-agnostic)

~/Books/kobo/                    ← TSUNDOKU_DOWNLOADS (user-visible EPUBs)
```

When sibling skills like `kindle-*` or `apple-books-*` land later, they'll
nest under `~/.tsundoku/kindle/`, `~/.tsundoku/cache/kindle/` etc.

**Two decision-point env vars** (set these to relocate things):
- `TSUNDOKU_ROOT` — default `~/.tsundoku`
- `TSUNDOKU_DOWNLOADS` — default `~/Books/kobo`

**Five derived paths** (computed from the two above; do not set directly):

| Var | Scope |
|---|---|
| `TSUNDOKU_TMPDIR` | shared |
| `TSUNDOKU_MARKDOWN_DIR` | shared (`cache/markdown`) |
| `TSUNDOKU_KOBO_CONFIG` | Kobo: kobodl.json |
| `TSUNDOKU_KOBO_BINARY` | Kobo: kobodl-macos |
| `TSUNDOKU_KOBO_LIBRARY_JSON` | Kobo: library export |

**Permissions enforced** by `kobo_login.sh`:
- `$TSUNDOKU_ROOT/kobo/auth/` directory: `chmod 700` (owner-only)
- `kobodl.json` file: `chmod 600` (owner read/write only)
- Other directories: default `755`; binary stays `755` for execution

**Cache wipe**: `cache/` is a single subtree of regenerable derived data
(see `book-extract:cache_clear.sh`). Auth, binary, and downloaded
EPUBs are never touched.

**Independence**: This layout is separate from any prior `kobodl` install.
The upstream tool's default `~/.config/kobodl/` and the legacy
`~/KobodlLibrarySync/` shell-script directory are left untouched.

## Helper Scripts

`tsundoku_paths.sh` lives at the plugin root (`tsundoku/lib/`) and is shared
by every skill. Source it once to populate path env vars, then invoke the
auth scripts.

| Path | Role |
|---|---|
| `scripts/tsundoku_paths.sh` (per skill — copied to each one) | Source-able OR runnable. Resolves and emits all path env vars |
| `scripts/kobo_install.sh` | Downloads `kobodl-macos` to `$TSUNDOKU_ROOT/bin/`. Idempotent |
| `scripts/kobo_login.sh`   | Subcommand router — see below |

`kobo_login.sh` subcommands:

| Subcommand | Effect |
|---|---|
| `status` (default) | Print `user list`; exit 0 if authed, 1 if not, 3 if binary missing |
| `add` | Run interactive `kobodl user add`; chmod 600 on success |
| `remove EMAIL` | Remove a user from the config |
| `import-from PATH` | Copy an existing `kobodl.json` into `$TSUNDOKU_KOBO_CONFIG` |
| `path` | Print the canonical config path and exit |

## Standard Flows

### Flow A — First-time setup (interactive activation)

> **Why this flow runs in the user's terminal, not via Bash tool**: kobodl's
> device-flow login prints a 6-digit code to stdout that the user must read
> and type into `https://www.kobo.com/activate`. When run via Claude Code's
> Bash tool, that output is buffered and truncated in the UI ("+N lines"
> indicator) while the process is mid-flight, so the user can't see the code
> as it appears. In Claude Desktop's Cowork tab, the same Bash subprocess is
> additionally blocked from reaching `kobo.com` by the sandbox URL allowlist
> — kobodl hangs forever on a network call that never resolves. Even on Code
> CLI, kobodl's polling loop expects a real TTY for clean cancellation. The
> reliable pattern is: print the command for the user to run in their own
> terminal, wait for them to confirm activation, then verify auth state from
> Claude. See `domain-teams:skill-team / standards/user-terminal-handoff.md`
> for the general convention.

#### Step 1 — Install binary (Bash-OK, no interaction)

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/kobo_install.sh
```

#### Step 2 — Skip if already authed (Bash-OK, no interaction)

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/kobo_login.sh status
```

If exit code 0 → already authed; print the user list and stop. Otherwise
proceed to Step 3.

#### Step 3 — Hand off device-flow to user's terminal (DO NOT Bash-run)

Print this block to the user verbatim — substitute `${CLAUDE_SKILL_DIR}`
with the actual resolved path so the user can copy-paste:

```
Please open a NEW terminal (outside Claude) and run:

    source <CLAUDE_SKILL_DIR>/scripts/tsundoku_paths.sh
    "$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" user add

kobodl will print a 6-digit code and a URL. Open the URL in your browser,
sign in to your Kobo account, enter the 6-digit code, and wait — kobodl
polls in the background and exits automatically when activation registers
(usually <60 seconds after you enter the code on the website).

Reply "done" once kobodl has exited successfully.
```

Do NOT wrap this in a Bash tool call. Claude must wait for the user's
"done" reply before proceeding.

#### Step 4 — Verify auth state from Claude (Bash-OK)

After the user replies "done":

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/kobo_login.sh status
```

- Exit 0 + email printed → ✓ auth complete; hand off to `kobo-library`
- Exit 1 → activation didn't register. Likely causes:
  - Code expired (10-minute window) — re-run Step 3 to get a fresh code
  - User cancelled before kobodl finished polling — same fix
  - Network issue between user's terminal and `kobo.com` — out of scope

### Flow B — Migrate from existing kobodl install

If the user already authenticated via the legacy shell script
(`kobodl-library-sync.sh`) or an earlier kobodl install, their credentials
live at `~/KobodlLibrarySync/config/kobodl.json` (or wherever they pointed
`--config`). Skip the activation flow entirely:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/kobo_install.sh
bash ${CLAUDE_SKILL_DIR}/scripts/kobo_login.sh \
    import-from ~/KobodlLibrarySync/config/kobodl.json
bash ${CLAUDE_SKILL_DIR}/scripts/kobo_login.sh status
```

`import-from`:
- Backs up any existing config to `kobodl.json.bak.<timestamp>` first
- Copies the source file into `$TSUNDOKU_KOBO_CONFIG`
- Sets `chmod 600`
- Verifies via `user list` if the binary is installed

### Flow C — Verify auth state (idempotent check)

Use this as a precondition check from other skills:

```bash
if bash ${CLAUDE_SKILL_DIR}/scripts/kobo_login.sh status >/dev/null; then
    echo "auth ready"
else
    echo "auth required — invoke kobo-auth Flow A or B"
fi
```

Exit codes:
- `0` — at least one user authed
- `1` — config missing or no user inside
- `3` — binary not installed yet (run `kobo_install.sh` first)

### Flow D — Re-authenticate / rotate / switch account

`add` is a device-flow command (same TTY constraints as Flow A) — hand
off to the user's terminal, do NOT run via Bash. `remove` is purely local
file mutation, so Bash is fine.

**Add another account** (kobodl supports multiple users in one config):
follow Flow A Steps 1–4. The new user appends to `kobodl.json`.

**Remove an old account** (Bash-OK):

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/kobo_login.sh remove old@example.com
```

**Nuclear option — wipe and start over**: combine both patterns —

```bash
# Step 1 (Bash-OK): remove the file
rm "$TSUNDOKU_KOBO_CONFIG"
```

Then run Flow A Steps 1–4 to re-authenticate.

After removing credentials locally, the user should also visit Kobo's
**Authorized Devices** page and revoke the device entry to fully invalidate
the session token.

## Multi-User Notes

`kobodl.json` stores an array of users. Most kobodl commands accept
`-u EMAIL` or `-u USERKEY` to scope to a specific user. The `kobo-library`
skill defaults to whichever user `book list` returns first — pass `-u` if
the user has multiple accounts and wants a specific one.

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `[login] activation did not complete` | User cancelled, code expired (10 min), or browser flow failed | Re-run `kobo_login.sh add` |
| `Traceback ... PermissionError ... /var/folders/.../tmp` | PYI-1270 (PyInstaller temp dir issue) | Already handled — `tsundoku_paths.sh` sets TMPDIR. If still failing, manually `export TMPDIR=$TSUNDOKU_TMPDIR` |
| `xattr: ... No such xattr` | macOS quarantine flag absent | Harmless; install script suppresses |
| `book list` returns auth error after weeks | Session token expired | Run `kobo_login.sh add` to refresh |
| `[install] downloaded file is suspiciously small` | GitHub returned 404 HTML | Check the release URL or pass `--url` to override |

## Security Reminders

- `kobodl.json` is equivalent to your Kobo session — treat as a password
- Never commit it, paste it into chat, or upload to a cloud service
- This skill enforces `chmod 600`, but you should also ensure your home
  directory isn't world-readable
- For shared machines, prefer using a unique macOS user account over relying
  on file permissions alone

## Cross-Skill Handoff

After successful auth, hand off to **`kobo-library`** for the actual
search/download work. That skill assumes:
- `tsundoku_paths.sh` is source-able (resolves paths)
- `kobo_login.sh status` returns 0 (auth ready)
- `TSUNDOKU_KOBO_BINARY` is executable

If any precondition fails, route the user back to this skill.

## Reference

- kobodl: <https://github.com/subdavis/kobo-book-downloader>
- Kobo activation: <https://www.kobo.com/activate>
- Kobo Authorized Devices (revocation): <https://www.kobo.com/account/devices>
- XDG Base Directory Spec: <https://specifications.freedesktop.org/basedir-spec/>
