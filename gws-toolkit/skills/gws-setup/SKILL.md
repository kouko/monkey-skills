---
name: gws-setup
description: First-time Google Workspace backend onboarding for gws-toolkit — GCP Console OAuth setup (Slides + Drive + Docs + Sheets + Gmail + Calendar API), gws CLI bootstrap, BYO-OAuth-client mechanism for External-audience accounts, credential hygiene, and upstream gws-* skill installation. 使用時機：第一次用 gws / 看到 401 403 auth / invalid_scope / invalid_client / 重新跑 setup / state detection 判斷要補哪一步 / OAuth scope 升級。v0.6.0: Workspace accounts auto-detected by gcloud active-account email domain (Internal app, no 7-day refresh limit); personal @gmail.com still supported via External + Testing path with 7-day refresh. macOS only.
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
| Credential store | macOS Keychain (strict since gws v0.22.3) | macOS / Windows now use strict Keychain — no silent file-backend fallback. To force the file backend, explicitly set `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`. See [Workarounds](#workarounds). |

**Not required**: Python, uv, gcloud, brew, npm. The `gws` and `jq`
binaries are fetched by `scripts/gws/bootstrap.sh` into
`~/.cache/gws-toolkit/bin/` via HTTPS + `curl -f` with URL pin to the
official `googleworkspace/cli` + `jqlang/jq` GitHub orgs (SHA-256
verification was retired in v0.4.0 — see TECH-SPEC §2.3).

### Quota awareness — 2026-05-01 API quota change

Google rolled out a new Gmail / Calendar API quota (クォータ / 配額)
schedule on **2026-05-01**, with potential billing (課金 / 計費)
arriving later in 2026 ("at least 90 days' notice before changes take
effect"). Whether your GCP project is affected depends on when it
first saw API traffic:

- Projects with API usage between **Nov 2025 and Apr 2026** are
  **grandfathered (旧基準維持 / 沿用舊額度)** to the old quotas — this
  includes the GCP project kouko created during the slides-toolkit
  Phase 1 era.
- Projects **created on/after 2026-05-01** (new marketplace users
  doing first-time `/gws-setup`) are subject to the new quota
  schedule and the upcoming billing change.
- Gmail per-user limits: **250 quota units/user/second** moving
  average; **2,000 messages/day** per Workspace user; **500
  recipients/message**.
- Calendar per-project limits: **1,000,000 queries/day**; transient
  `429` rate-limit errors are handled transparently by `gws-wrap.sh`'s
  exponential backoff (5s / 10s / 20s). `403` is treated as a scope /
  auth error (exit 10) — in Workspace contexts `403` typically signals
  missing OAuth scope rather than transient throttling, so re-run
  `gws-setup` instead of waiting for backoff.

Authoritative references:

- [Gmail API Usage Limits](https://developers.google.com/workspace/gmail/api/reference/quota)
- [Calendar API Usage Limits](https://developers.google.com/workspace/calendar/api/guides/quota)

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
| `credential-check.sh` not found, or `~/.cache/gws-toolkit/bin/` empty | Fresh machine | Setup flow step 1 |
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
| 6 | Browser | Enable 6 APIs: Slides + Drive + Docs + Sheets + Gmail + Calendar | walkthrough §6 |
| 7 | Terminal | `bash scripts/gws/bootstrap.sh` (installs gws + jq) | walkthrough §7 |
| 8 | Terminal | Export the BYO-client env vars (see below) | `protocols/issue-119-workaround.md` |
| 9 | Terminal | `gws auth login --scopes=presentations,drive,documents,spreadsheets,gmail,calendar` — pass the explicit 6-URL scope list; do NOT use the picker's "all scopes" (Testing mode caps at 25 scopes per [upstream README §Authentication](https://github.com/googleworkspace/cli#authentication)) | walkthrough §9 |
| 10 | Browser | Consent screen → Advanced → Go to app (unsafe) → Allow | walkthrough §10 |

**Done when**:

```bash
gws auth whoami
# Expected: your_email@gmail.com
```

## Workarounds

### BYO OAuth client (the External-audience standard pattern)

> **Historical naming**: this used to be framed as "issue #119
> workaround". Upstream's [README §Authentication](https://github.com/googleworkspace/cli#authentication)
> now documents `GOOGLE_WORKSPACE_CLI_CLIENT_ID` /
> `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` as the **first-class
> External-audience BYO-client mechanism** — not a workaround.
> Personal `@gmail.com` accounts under External + Testing always
> need their own OAuth Client because there is no shared `gws`
> consumer client (the IAP OAuth Admin API was deprecated 2025; see
> upstream `setup.rs`'s `create_oauth_client removed` comment).
> Issue #119's underlying parsing bug was separately fixed by
> upstream PR #177 (merged 2026-03-05, shipped in v0.22.5).

Quick command (full version plus shell-profile setup is in
`protocols/issue-119-workaround.md`):

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
```

Or delegate to `scripts/gws/env-guard.sh`:

```bash
bash scripts/gws/env-guard.sh check   # detect whether the env vars need (re-)applying
bash scripts/gws/env-guard.sh apply   # write ~/.config/gws/env.sh (chmod 600)
```

### macOS Keychain (v0.22.3+ strict mode)

Since gws v0.22.3, macOS and Windows use **strict Keychain** — when
Keychain is unavailable the call **fails fast** instead of silently
falling back to a file. Any old `~/.config/gws/.encryption_key`
fallback files are auto-deleted on successful Keychain login. This
is the secure default and you should rarely need to override it.

If you genuinely need the file backend (e.g. running in a no-Keychain
context like SSH without a graphical session), **explicitly** opt in:

```bash
export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file
```

The token is then stored in `~/.config/gws/keyring-file.json` (chmod
600, already covered by `.gitignore`). Trade-off vs Keychain: plaintext-
at-rest instead of OS-level encryption. On a personal machine with
correct `~/` permissions this stays within ASVS V14 L1.

**Do not set `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file` by default
on a personal machine** — that violates rule 5 of
`standards/credential-hygiene.md`.

### OAuth client maintenance (Google 2025-06 Console changes)

Two Google-side behaviors worth knowing:

1. **Client secret is shown only once**. The Cloud Console masks
   the secret after creation (Google Auth Platform 2025-06 update).
   Step 5 of Path A's setup downloads `client_secret_*.json`
   immediately for this reason; if you ever lose the file, you must
   delete the old client and create a new one.
2. **6-month inactivity → auto-delete**. OAuth clients with no API
   usage for 6 months are auto-deleted; there is a 30-day restore
   window. If your gws-toolkit usage lapses for half a year, expect
   to re-run `/gws-setup` afterwards.

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

1. Sources `~/.config/gws/env.sh` (BYO-client env vars
   `GOOGLE_WORKSPACE_CLI_CLIENT_ID/_SECRET` must be present before
   `gws auth login`).
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
| `invalid_scope` | BYO-client env vars not exported (or stale scope picker selection) | [BYO OAuth client](#byo-oauth-client-the-external-audience-standard-pattern) |
| `invalid_client` | Client ID / Secret not exported, or `client_secret.json` missing | walkthrough §5, §8 |
| `Google hasn't verified this app` | Expected; click Advanced → Go to app (unsafe) | walkthrough §10 |
| exit 18 `Keychain unavailable and file-backend also failed` | Keychain permissions broken and `~/.config/gws/` permissions broken | Verify `~/.config/gws/` is chmod 600, rerun setup steps 8–9 |
| `gws auth login` hangs on the localhost callback | Firewall blocking loopback, or the browser window was closed | Rerun step 9; verify `127.0.0.1` is reachable |

## Checklist

After every setup run, self-verify using the 6 state checks in
`checklists/setup-state.md`: (1) gws binary / (2) jq binary /
(3) gcloud (optional) / (4) `client_secret.json` present / (5)
BYO-client env vars exported / (6) `gws auth whoami` returns your
email. Any failure points you back to the matching step in
`gcp-console-walkthrough.md`.

## References

- `protocols/gcp-console-walkthrough.md` — full 10-step tutorial
- `protocols/issue-119-workaround.md` — historical name for the BYO-client env-var mechanism (kept as a stable cross-link anchor)
- `standards/credential-hygiene.md` — 5 hard rules + incident response + ASVS L1 mapping
- `checklists/setup-state.md` — 6 state checks
- TECH-SPEC: `../../TECH-SPEC.md` §3.2, §4.2, §6.1, §6.2, §8
- PRODUCT-SPEC: `../../PRODUCT-SPEC.md` §6.3.3 risks
