---
name: gws-setup
description: First-time Google Workspace backend onboarding for gws-toolkit — GCP Console OAuth setup (Slides + Drive + Docs + Sheets + Gmail + Calendar API), gws CLI bootstrap, issue #119 workaround, credential hygiene, and upstream gws-* skill installation. 使用時機：第一次用 gws / 看到 401 403 auth / invalid_scope / invalid_client / 重新跑 setup / state detection 判斷要補哪一步 / OAuth scope 升級。v0.6.0: Workspace accounts auto-detected by gcloud active-account email domain (Internal app, no 7-day refresh limit); personal @gmail.com still supported via External + Testing path with 7-day refresh. macOS only.
---

# gws-setup

One-time machine setup so that `slides-builder` can call the gws
CLI against Google Slides. Supports both personal `@gmail.com` accounts
(External + Testing, 7-day refresh) and Google Workspace org accounts
(Internal, no 7-day limit) on macOS. Account type is auto-detected from
the active gcloud account's email domain. Linux and CI are out of scope.

## When to use

Invoke this skill in any of these four situations:

1. **First-time setup** — brand-new machine or brand-new Google
   account, no `~/.config/gws/` yet.
2. **Expired credentials** — more than 7 days since the last
   `gws auth` on a personal `@gmail.com` account (Google's hard limit
   for External + Testing; Workspace accounts do not hit this — see
   [Every 7 days maintenance](#every-7-days-maintenance-personal-account-only)).
3. **Auth error** — `slides-builder` returns exit code 10 / 16 /
   18, or stderr shows `401` / `403` / `invalid_scope` /
   `invalid_client`.
4. **State detection** — you're unsure where things stand (is the
   binary installed? is the token still valid?). Run
   `scripts/gws/credential-check.sh` first and branch on the
   JSON it returns.

## Prerequisites

| Item | Requirement | Notes |
|---|---|---|
| OS | macOS (darwin-arm64 or darwin-x86_64) | The only supported platform. Linux / WSL are out of scope. |
| Shell | zsh or bash | The default macOS zsh is fine. |
| Network tool | `curl` | Preinstalled on macOS. |
| Browser | Chrome or Safari | Needed once for the GCP Console steps. |
| Google account | Personal `@gmail.com` OR Google Workspace org account | Auto-detected by gcloud active-account email domain; `--audience` flag overrides if needed. Workspace accounts skip the 7-day refresh limit. |
| Credential store | macOS Keychain available (default) | If Keychain silently fails, the tooling falls back to a file backend. See [Workarounds](#workarounds). |

**Not required**: Python, uv, gcloud, brew, npm. The `gws` and `jq`
binaries are fetched by `scripts/gws/bootstrap.sh` into
`~/.cache/slides-toolkit/bin/` and verified by SHA-256 (TECH-SPEC §2.3).

## Workflow overview

```
  [Start]
     │
     ▼
┌─────────────────────────────┐
│ State detection             │   ← always run this first
│ credential-check.sh         │
└──────────┬──────────────────┘
           │ JSON: {backend, token_valid, expires_in_days, account_type}
           ▼
 ┌─────────┴──────────────┬──────────────────────┬─────────────────┐
 │ binary missing          │ binary present / not  │ token expired    │ all green
 │                         │ yet authed            │                  │
 ▼                         ▼                      ▼                  ▼
 [Setup flow, 10 steps]    [Resume at step 8]     [Re-auth only]     [Done]
 ├─ 6 Console steps        ├─ apply env workaround ├─ gws auth login
 └─ 4 local steps          └─ gws auth login       └─ 10-second job
```

Full branch table: `checklists/setup-state.md`.

## State detection

**Run state detection first. Don't charge straight into the setup
flow.**

```bash
bash scripts/gws/credential-check.sh
```

Expected JSON output:

```json
{"backend":"keychain","token_valid":true,"expires_in_days":6,"account_type":"personal"}
```

The `account_type` field is one of `personal` | `workspace` | `unknown`
— derived from the active gcloud account's email domain (`unknown` is a
defensive fallback when gcloud is missing or no active account is set).

Branch on the result:

| Result | Branch | Entry point |
|---|---|---|
| `credential-check.sh` not found, or `~/.cache/slides-toolkit/bin/` empty | Fresh machine | Setup flow step 1 |
| `backend=keychain`, `token_valid=true`, `expires_in_days > 0` | All green | Run `slides-builder` directly |
| `backend=keychain`, `token_valid=false` or `expires_in_days <= 0`, `account_type=personal` | Expired (personal) | [Every 7 days maintenance](#every-7-days-maintenance-personal-account-only) |
| `backend=keychain`, `token_valid=false` or `expires_in_days <= 0`, `account_type=workspace` | Expired (workspace — rare; no 7-day policy applies) | `bash scripts/gws/refresh-auth.sh` |
| `account_type=unknown` | gcloud missing or no active account | Run `gcloud auth login`, then rerun state detection |
| `backend=file` | Keychain silently failed, fell back to file | Continue, but read the Keychain note in [Workarounds](#workarounds) |
| exit 18 | Keychain unreadable and file backend also failed | Rerun setup step 3 (download the Client Secret) and steps 8–9 |

Full checklist: `checklists/setup-state.md`.

## Setup flow — pick a path

Two paths, **same end state**. Pick one:

| Path | What it is | When to pick |
|---|---|---|
| **Path A (recommended)** — `/gws-setup` slash command | Runs `scripts/gws/auto-setup.sh` end-to-end: install gcloud → `gcloud auth login` → create GCP project → enable 6 APIs → guided OAuth Consent + Client → install credentials → bootstrap binaries → `gws auth login`. Idempotent. | Default for first-time setup; ~6-8 min first run, ~30 sec when re-run on a set-up machine. |
| **Path B (manual fallback)** — 10-step browser walkthrough | Do everything yourself in the GCP Console; SKILL surfaces the table below. | Debugging, partial state recovery, or environments where the script can't run (no TTY, custom GCP setup, ...). |

### Path A — `/gws-setup` (recommended)

In Claude Code:

```
/gws-setup
```

(Or run the underlying script directly: `bash scripts/gws/auto-setup.sh`. Supports `--dry-run` and `--force-reinstall`.)

The slash command's full contract — `$ARGUMENTS`, the 8 codified steps, troubleshooting, when it doesn't apply — lives in `commands/gws-setup.md`. Read that for the per-step detail before running on a constrained environment (no TTY / behind a proxy / non-default `~/Downloads/` path).

### Path B — manual 10-step walkthrough

**10 steps total**, split into two segments: 6 browser steps in the
Console, then 4 local steps.

**Full walkthrough**: `protocols/gcp-console-walkthrough.md`
(estimate: 10–15 minutes).

| # | Where | What to do | On failure, return to |
|---|---|---|---|
| 1 | Browser | Create a GCP project | walkthrough §1 |
| 2 | Browser | Google Auth Platform → Branding → External + Testing | walkthrough §2 |
| 3 | Browser | Audience → add yourself as a Test user (**skipping this = 403 later**) | walkthrough §3 |
| 4 | Browser | Clients → Create client → **Desktop app** (not Web) | walkthrough §4 |
| 5 | Browser | Download `client_secret.json` → `~/.config/gws/` | walkthrough §5 |
| 6 | Browser | Enable APIs: Google Slides API + Google Drive API | walkthrough §6 |
| 7 | Terminal | `bash scripts/gws/bootstrap.sh` (installs gws + jq) | walkthrough §7 |
| 8 | Terminal | Export the issue #119 env vars (see below) | `protocols/issue-119-workaround.md` |
| 9 | Terminal | `gws auth login --scopes=presentations,drive,documents,spreadsheets,gmail,calendar` (**never use the `recommended` preset**) | walkthrough §9 |
| 10 | Browser | Consent screen → Advanced → Go to app (unsafe) → Allow | walkthrough §10 |

**Done when**:

```bash
gws auth whoami
# Expected: your_email@gmail.com
```

## Workarounds

### Issue #119 — `invalid_scope` / `invalid_client` on personal Gmail

The gws CLI ships with a built-in OAuth client that trips
`invalid_scope` or `invalid_client` on personal `@gmail.com`
accounts. The fix is to export your own OAuth Client ID + Secret as
env vars; gws picks them up and uses yours instead.

Quick command (full version plus shell-profile setup is in
`protocols/issue-119-workaround.md`):

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
```

Or delegate to `scripts/gws/env-guard.sh`:

```bash
bash scripts/gws/env-guard.sh check   # detect whether the workaround is needed
bash scripts/gws/env-guard.sh apply   # write ~/.config/gws/env.sh (chmod 600)
```

Upstream fix tracking: `googleworkspace/cli` issue #119 (TODO:
fill in upstream discussion link).

### macOS Keychain silent fail (fallback to file backend)

gws writes the refresh token to the macOS Keychain by default, but
under certain profile states the write appears to succeed while the
token can't be read back. When `credential-check.sh` detects this,
it falls back automatically:

```bash
export KEYRING_BACKEND=file
```

The token is then stored in `~/.config/gws/keyring-file.json`
(chmod 600, already covered by `.gitignore`). The trade-off versus
Keychain is a small drop in security (plaintext-at-rest versus
OS-level encryption), but on a personal machine with correct home
directory permissions this stays within ASVS V14 L1.

**Do not set `KEYRING_BACKEND=file` by default on a personal
machine** — that violates rule 5 of `standards/credential-hygiene.md`.

## Credential hygiene

Everything this skill touches is sensitive credential material.
**Required reading**: `standards/credential-hygiene.md`.

Five hard rules (summarized):

1. The skill repo never stores credentials of any kind (repo holds
   code + docs only).
2. User credentials live exclusively in `~/.config/gws/` (managed by
   gws).
3. A `.claude/settings.json` deny rule prevents Claude from reading
   credentials into context.
4. `.gitignore` patterns prevent accidental commits.
5. Prefer Keychain on macOS; only drop to the file backend on Linux/CI.

The same file contains the incident response playbook and the
ASVS v5.0.0 L1 mapping (V1 / V13 / V14 / V16).

## Every 7 days maintenance (personal-account only)

**Workspace accounts: no 7-day refresh limit applies; this section does
not apply.** Internal apps issued by Workspace orgs are not subject to
External + Testing's 7-day policy, so Workspace refresh tokens persist
until explicitly revoked. Skip this section if `credential-check.sh`
reports `account_type=workspace`.

**Refresh tokens issued under External + Testing last 7 days** — this
is a Google OAuth policy that applies to personal `@gmail.com` accounts.
Since the personal-account path intentionally does not pursue
production verification, there's no way around it.

Every 7 days (or whenever you see exit 10 `token expired`):

**Agent directive**: Claude — invoke this directly via the Bash tool.
**Do NOT** print the command as a paste-it `!` invocation for the user
to run manually. The OAuth flow opens a browser; the user completes
consent there, the Bash call blocks until the localhost callback
returns. That blocking is expected behaviour, not a reason to defer to
the user.

```bash
bash scripts/gws/refresh-auth.sh
```

`refresh-auth.sh` is the wrapper purpose-built for this case (7-day
Testing-mode token expired, same Google account — no account-switch
intent). It:

1. Sources `~/.config/gws/env.sh` (issue #119 workaround env vars must
   be present before `gws auth login`).
2. Runs `gws auth login --scopes=presentations,drive,documents,spreadsheets,gmail,calendar`
   (the 6-API scope set; matches `auto-setup.sh` step 8 and
   `slides-builder` runtime needs).
3. Opens the browser for consent; total wall time ~10 seconds end-to-end.

For account switch (different Google account), use
`scripts/gws/gws-login.sh --switch` instead — that script clears local
creds first via `gws-logout.sh` so the Google account picker reappears.

**No need to rerun the setup flow** — your Client Secret and OAuth
client are still valid, only the refresh token expired.

**Passive notification strategy (TECH-SPEC §6.3)**: when
`slides-builder`'s pre-flight sees an expired token it exits
with code 10. Claude sees that exit code and prompts you to re-auth
on demand, rather than nagging you on every run.

## Error messages guide

| Message / state | Root cause | Go to |
|---|---|---|
| `401 Unauthorized` | Token expired or never authed | [Every 7 days maintenance](#every-7-days-maintenance-personal-account-only) (personal) or `bash scripts/gws/refresh-auth.sh` (workspace) |
| `403 Forbidden` + `access_denied` | Your Gmail is not in Test users | walkthrough §3 (add test user) |
| `403 Forbidden` + `access_denied` (Workspace) | Your Workspace admin restricts Gmail/Calendar OAuth scopes | Escalate to your Workspace admin; see brief §Axis 4 Q3 |
| `403 Forbidden` + `API not enabled` | Slides or Drive API not enabled | walkthrough §6 |
| `invalid_scope` | gws built-in client rejects the scope on personal Gmail | [Issue #119 workaround](#issue-119--invalid_scope--invalid_client-on-personal-gmail) |
| `invalid_client` | Client ID / Secret not exported, or `client_secret.json` missing | walkthrough §5, §8 |
| `Google hasn't verified this app` | Expected; click Advanced → Go to app (unsafe) | walkthrough §10 |
| exit 17 `SHA-256 mismatch` | Binary checksum failed (possible network attack or upstream release change) | Check the network and rerun bootstrap. If it persists, check upstream releases and SHA256SUMS. |
| exit 18 `Keychain unavailable and file-backend also failed` | Keychain permissions broken and `~/.config/gws/` permissions broken | Verify `~/.config/gws/` is chmod 600, rerun setup steps 8–9 |
| `gws auth login` hangs on the localhost callback | Firewall blocking loopback, or the browser window was closed | Rerun step 9; verify `127.0.0.1` is reachable |

## Checklist

After every setup run, self-verify using the 6 state checks in
`checklists/setup-state.md`: (1) gws binary / (2) jq binary /
(3) gcloud (optional) / (4) `client_secret.json` present / (5) issue
#119 env vars / (6) `gws auth whoami` returns your email. Any
failure points you back to the matching step in
`gcp-console-walkthrough.md`.

## References

- `protocols/gcp-console-walkthrough.md` — full 10-step tutorial
- `protocols/issue-119-workaround.md` — gws personal-Gmail workaround, full detail
- `standards/credential-hygiene.md` — 5 hard rules + incident response + ASVS L1 mapping
- `checklists/setup-state.md` — 6 state checks
- Upstream TECH-SPEC: `slides-toolkit/TECH-SPEC.md` §3.2, §4.2, §6.1, §6.2, §8
- Upstream PRODUCT-SPEC: `slides-toolkit/PRODUCT-SPEC.md` §6.3.3 risks
