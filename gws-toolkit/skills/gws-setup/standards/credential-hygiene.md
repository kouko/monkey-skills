# Credential Hygiene — gws-setup

> Applies to: the `gws-toolkit` plugin, specifically the OAuth
> Client Secret, refresh tokens, and BYO-client env vars that the
> Google Workspace backend handles.
> Baseline: OWASP ASVS v5.0.0 L1 (`app-security-standard.md`). This
> document specializes that baseline for gws-toolkit; it does not
> replace the upstream standard.

## Five hard rules (non-negotiable)

### Rule 1 — The skill repo never stores any credential

**The repo holds code + docs + test fixtures only (no real values).**

The following must never enter any commit:

- `client_secret.json` (contains OAuth Client ID + Client Secret)
- `token.json` / `keyring-file.json` (refresh token)
- `env.sh` (contains `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET` in
  plaintext)
- Any file under `~/.config/gws/` other than `SHA256SUMS`
- Real Drive IDs or real account emails (PII) mixed into
  `tests/fixtures/`

**Because**: ASVS V13 (Configuration) + V14 (Data Protection) —
secrets must not live in source code, build artifacts, or logs.
Even a private repo leaks via backups, CI runners, mirrors, and
clones.

### Rule 2 — All user credentials live in `~/.config/gws/`

All end-user credentials **must** live in `~/.config/gws/` and
nowhere else:

```
~/.config/gws/
├── config.yaml             # non-secret; account + client_id reference
├── client_secret.json      # OAuth Client Secret (600)
├── env.sh                  # BYO-client env vars (600)
└── keyring-file.json       # refresh token, only when explicit file-backend opt-in (600)
```

Permission requirements:

- Directory `~/.config/gws/`: `700`
- All files: `600`

**Because**: (a) centralization makes incident response scopes
unambiguous (see [Incident response](#incident-response)); (b) it
aligns with the gws CLI's own conventions; (c) home-directory scope
matches macOS's single-user assumption and satisfies ASVS V14
secrets-at-rest.

### Rule 3 — `.claude/settings.json` deny rule

Add the following to Claude Code's `settings.json` to prevent
Claude from accidentally reading credentials into its context —
once anything enters context it can flow to model-provider logs,
get summarized, or land in a commit:

```json
{
  "permissions": {
    "deny": [
      "Read(~/.config/gws/**)",
      "Read(~/.cache/gws-toolkit/bin/.version)",
      "Bash(cat ~/.config/gws/*)",
      "Bash(cat ~/.config/gws/**)",
      "Bash(cp ~/.config/gws/* *)",
      "Bash(git add ~/.config/gws/*)",
      "Write(~/.config/gws/**)"
    ]
  }
}
```

What the 7 patterns cover:

1. `Read(~/.config/gws/**)` — blocks Claude's Read tool from
   reading credentials directly.
2. `Read(~/.cache/gws-toolkit/bin/.version)` — the version file
   gets treated as harmless metadata. It holds no secret (the file
   stores the resolved release tag, not credentials), but narrowing
   reads keeps the attack surface small.
3. `Bash(cat ~/.config/gws/*)` — blocks `cat` from reading the
   credential files.
4. `Bash(cat ~/.config/gws/**)` — `**` covers subdirectories.
5. `Bash(cp ~/.config/gws/* *)` — blocks `cp` from moving
   credentials out of `~/.config/gws/`.
6. `Bash(git add ~/.config/gws/*)` — last line of defense: even if
   the file ends up inside a repo, `git add` itself is blocked.
7. `Write(~/.config/gws/**)` — blocks Claude's Write tool from
   overwriting. gws itself writes credentials via its own shell
   scripts (not Claude's Write), so it's unaffected.

**Because**: ASVS V14 (secrets-at-rest) + V16 (logs must not
contain secrets). In practice Claude Code's context is one of those
log surfaces; a deny rule is a cheap and effective preventive
measure.

### Rule 4 — `.gitignore` patterns

The plugin root `.gitignore` must contain:

```gitignore
# credentials — never commit (repo-relative patterns only)
.config/gws/
*/keyring-file.json
*/env.sh
# Note: home-dir credential files (~/.config/gws/**) cannot be
# protected by .gitignore (git uses repo-relative paths only and
# does not expand ~). Home-dir credential read access is blocked by
# the settings.json deny rule in Rule 3.

# binary cache
.cache/slides-toolkit/

# runtime artifacts (test fixtures with real IDs/paths)
tests/fixtures/*.drive_id.txt
tests/fixtures/*.local

# macOS
.DS_Store
```

**Important**: `.gitignore` uses repo-relative patterns and **does
not expand `~`**. The home-directory credentials (which in practice
are all under `~/.config/gws/`) are **not protected by .gitignore**
— they are protected by **Rule 3's settings.json deny rule**.

**Because**: this splits responsibility cleanly — repo-relative
goes through `.gitignore`, home-dir goes through `settings.json`.
No one confuses "it's in .gitignore so it's safe". Aligns with
TECH-SPEC §8.2.

### Rule 5 — Prefer Keychain on macOS; only opt into file backend explicitly

Keychain is macOS's native encrypted credential store, and it's
more secure than a plaintext file. **Since gws v0.22.3 (2026-01), macOS and
Windows use strict Keychain — there is no silent file-backend fallback.**
The wrapper scripts honour that contract.

- **Personal macOS machine**: **do not** set
  `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file` on your own. Keep
  Keychain as the default.
- **If Keychain genuinely fails** (no graphical session / strict
  no-keyring CI / etc.): **explicitly** opt into the file backend
  via `export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`. The token
  then lives in `~/.config/gws/keyring-file.json` (chmod 600,
  `.gitignore`-covered). On macOS this is rarely needed.
- **Linux / CI** (Phase 2+): Keychain doesn't exist; the file
  backend is acceptable. Re-evaluate ASVS requirements when Phase
  2+ begins (you may need to level up to L2).

**Because**: the ASVS V14 gap between Keychain and file backend is
"hardware/OS-level crypto vs filesystem permissions" — a plaintext
file (even at chmod 600) is easier to extract if the machine is
physically compromised. The MVP targets macOS only, so use
Keychain by default and opt into file explicitly when you have a
reason.

## Sensitivity tiers

Aligned with TECH-SPEC §2.4 (external dependencies) and §4.8
(credential flow):

| Asset | Sensitivity | If it leaks | Priority |
|---|---|---|---|
| OAuth Client Secret (`installed.client_secret` in `client_secret.json`) | 🔴 High | Attacker can masquerade as your OAuth client to pop a consent screen for Test users. The consent screen still restricts to Test users, but the incident-scope blast radius grows noticeably. | Revoke + rotate immediately |
| Refresh token (Keychain or `keyring-file.json`) | 🔴 High | Attacker has consent-free access to your Slides / Drive.file for up to 7 days | `gws auth logout` immediately + wipe Keychain/file |
| `env.sh` (Client ID + Secret in plaintext) | 🔴 High | Equivalent to a Client Secret leak | Delete + rotate immediately |
| `installed.client_id` inside `client_secret.json` | 🟡 Medium | The Client ID alone doesn't authenticate; it's dangerous only when paired with the Secret | Handle based on Secret status |
| `gws` binary + its URL pin | ⚪ Low | Public resource; the URL pin + HTTPS + official GitHub org is the integrity boundary (SHA-256 verification retired v0.4.0; TECH-SPEC §2.3) | No action |
| Drive IDs in `registry.md` (only if the template itself is non-sensitive) | ⚪ Low | A Drive ID still requires scoped access; leaking the ID alone doesn't authorize anything | No action |
| Google-account email | 🟡 Medium | PII + phishing surface; don't commit it | Replace with a placeholder |

Mapping: 🔴 = trigger incident response immediately; 🟡 = judge by
context; ⚪ = no special handling, but avoid unnecessary exposure.

## Incident response

When a credential has been committed / pushed / otherwise exposed:

### Step 1 — Revoke immediately

Open https://console.cloud.google.com → APIs & Services →
Credentials → **delete** the affected OAuth Client ID. **Do not
just "suspend" it** — delete it, so the old Client Secret can never
exchange another refresh token.

### Step 2 — Create a new OAuth client

Return to `protocols/gcp-console-walkthrough.md` §4–§5 to create a
new Desktop app OAuth client and download a fresh
`client_secret.json`.

### Step 3 — Wipe the old tokens

```bash
gws auth logout
# Clear Keychain (if used):
security delete-generic-password -s gws-cli 2>/dev/null
# Clear file backend (if used):
rm -f ~/.config/gws/keyring-file.json ~/.config/gws/env.sh
```

### Step 4 — Re-auth

Rerun `protocols/gcp-console-walkthrough.md` §7–§10.

### Step 5 — If it was committed to git

**Rewrite git history** (destructive operations — require explicit
confirmation before running):

```bash
# Use git-filter-repo (the recommended modern tool);
# git filter-branch is deprecated.
git filter-repo --path <leaked-file> --invert-paths

# If already pushed to the remote:
git push --force-with-lease origin <branch>
```

**Do not** rely on `git rm --cached <file>` alone — that only
clears the current HEAD, while history still carries the secret.

**Notify every collaborator who has cloned or forked** so they
rebase or re-clone.

### Step 6 — Rotate downstream resources

Check the Google Cloud audit log (Console → Logging) for any
suspicious access against Google resources during the 7-day token
TTL window. Even though the MVP scope is minimal (only
`presentations` + `drive` + `documents` + `spreadsheets`), you should still check.

### Step 7 — Write an incident log

Create `slides-toolkit/incidents/YYYY-MM-DD-<short-description>.md`
(the directory is created on demand, per TECH-SPEC §2.1, §8.4).
Contents:

- Discovery time and how it was found (grep? GitHub secret-scanning
  alert?)
- Leak vector (e.g. `client_secret.json` accidentally committed)
- Affected time window (token TTL within which it could have been
  abused)
- Revoke + rotate timestamps
- Root cause (e.g. Rule 3's settings.json deny rule was not applied)
- Prevention (e.g. add a `gitleaks protect --staged` pre-commit hook)

**Do not** include the actual secret in the incident log — the log
itself is an ASVS V16 audit surface, so we don't want to re-leak.

## OWASP ASVS v5.0.0 L1 mapping

The ASVS L1 verification items this standard touches (aligned with
`app-security-standard.md` and TECH-SPEC §8.6):

| ASVS chapter | How this standard maps |
|---|---|
| **V1** Encoding & Sanitization | Minimal OAuth scopes (least-privilege: `presentations` + `drive` + `documents` + `spreadsheets`, never `drive` full or `userinfo.email`); UTF-8-only pipeline to avoid mojibake creating an injection surface |
| **V13** Configuration | Rule 5 (Keychain preferred, explicit file-backend opt-in via `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`); binary URL pin + HTTPS as secure-default + dependency-integrity control |
| **V14** Data Protection | Rule 1 (no secret in repo) + Rule 2 (centralized `~/.config/gws/`, chmod 600) + Rule 4 (.gitignore) + Rule 3 (settings.json deny rule blocking Claude reads) — a multi-layer secrets-at-rest defense |
| **V16** Security Logging & Error Handling | Incident response writes `incidents/` without secrets; the exit-code table (TECH-SPEC §4.2) never prints token values to stderr |

**Because**: ASVS L1 is the reasonable baseline for personal /
internal tools (see `app-security-standard.md` §Default Tier).
slides-toolkit handles a personal OAuth credential — not PCI,
HIPAA, or financial data — so L1 suffices. If Phase 2+ publishes
this to external multi-user audiences, re-evaluate whether to move
to L2.

## Related files

- `app-security-standard.md` (code-team standards — the upstream
  ASVS anchor)
- TECH-SPEC §4.8 — detailed credential flow diagram
- TECH-SPEC §8.1 — full settings.json deny-rule list
- TECH-SPEC §8.2 — full `.gitignore` patterns
- TECH-SPEC §8.4 — incident response playbook (this standard is the
  detailed version)
- TECH-SPEC §8.6 — ASVS L1 mapping (this standard extends it)
- `protocols/gcp-console-walkthrough.md` §5 — `client_secret.json`
  chmod 600
- `protocols/issue-119-workaround.md` — env var workaround and
  `env.sh` chmod
