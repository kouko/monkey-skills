---
name: gws-setup
description: First-time Google Workspace backend onboarding for gws-toolkit — GCP Console OAuth setup (Slides + Drive + Docs + Sheets API), gws CLI bootstrap, issue #119 workaround, credential hygiene, and upstream gws-* skill installation. 使用時機：第一次用 gws / 看到 401 403 auth / invalid_scope / invalid_client / 重新跑 setup / state detection 判斷要補哪一步 / OAuth scope 升級。MVP 只處理個人 @gmail.com（macOS）；Google Workspace 企業帳號 Phase 2+。
---

# gws-setup

One-time machine setup so that `slides-builder` can call the gws
CLI against Google Slides. MVP scope is personal `@gmail.com` accounts
on macOS. Workspace accounts, Linux, and CI are Phase 2+.

## When to use

Invoke this skill in any of these four situations:

1. **First-time setup** — brand-new machine or brand-new Google
   account, no `~/.config/gws/` yet.
2. **Expired credentials** — more than 7 days since the last
   `gws auth` (Google's hard limit for External + Testing; see
   [Every 7 days maintenance](#every-7-days-maintenance)).
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
| OS | macOS (darwin-arm64 or darwin-x86_64) | The only MVP-supported platform. Linux / WSL are Phase 2+. |
| Shell | zsh or bash | The default macOS zsh is fine. |
| Network tool | `curl` | Preinstalled on macOS. |
| Browser | Chrome or Safari | Needed once for the GCP Console steps. |
| Google account | Personal `@gmail.com` | Workspace accounts are Phase 2+. |
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
           │ JSON: {backend, token_valid, expires_in_sec}
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
{"backend":"keychain","token_valid":true,"expires_in_sec":518400}
```

Branch on the result:

| Result | Branch | Entry point |
|---|---|---|
| `credential-check.sh` not found, or `~/.cache/slides-toolkit/bin/` empty | Fresh machine | Setup flow step 1 |
| `backend=keychain`, `token_valid=true`, `expires_in_sec > 0` | All green | Run `slides-builder` directly |
| `backend=keychain`, `token_valid=false` or `expires_in_sec <= 0` | Expired | [Every 7 days maintenance](#every-7-days-maintenance) |
| `backend=file` | Keychain silently failed, fell back to file | Continue, but read the Keychain note in [Workarounds](#workarounds) |
| exit 18 | Keychain unreadable and file backend also failed | Rerun setup step 3 (download the Client Secret) and steps 8–9 |

Full checklist: `checklists/setup-state.md`.

## Setup flow

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
| 9 | Terminal | `gws auth login --scopes=presentations,drive,documents,spreadsheets` (**never use the `recommended` preset**) | walkthrough §9 |
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

## Every 7 days maintenance

**Refresh tokens issued under External + Testing last 7 days** — this
is a Google OAuth policy. Since the MVP intentionally does not pursue
production verification, there's no way around it.

Every 7 days (or whenever you see exit 10 `token expired`):

```bash
gws auth login --scopes=presentations,drive,documents,spreadsheets
# Browser opens → consent → callback returns
# Takes about 10 seconds
```

**No need to rerun the setup flow** — your Client Secret and OAuth
client are still valid, only the refresh token expired.

**Passive notification strategy (TECH-SPEC §6.3)**: when
`slides-builder`'s pre-flight sees an expired token it exits
with code 10. Claude sees that exit code and prompts you to re-auth
on demand, rather than nagging you on every run.

## Error messages guide

| Message / state | Root cause | Go to |
|---|---|---|
| `401 Unauthorized` | Token expired or never authed | [Every 7 days maintenance](#every-7-days-maintenance) |
| `403 Forbidden` + `access_denied` | Your Gmail is not in Test users | walkthrough §3 (add test user) |
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
