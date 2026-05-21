# GCP Console Walkthrough — First-time Google Slides Backend Setup

> A step-by-step tutorial that takes you from zero to `gws auth whoami`
> returning your email. MVP scope is personal `@gmail.com` on macOS.
>
> **Aligned with the 2026-04 Google Cloud Console UI (Google Auth
> Platform)**. The old "APIs & Services → OAuth consent screen" entry
> still redirects, but the page structure is now Overview / Branding /
> Audience / Clients / Data Access.

## Before you start

Confirm the following before touching anything:

- You have a working **personal `@gmail.com`** account. Google
  Workspace accounts go through Admin Console, which is Phase 2+ and
  not covered by this walkthrough.
- You're on **macOS** (darwin-arm64 or darwin-x86_64 — Apple Silicon
  or Intel).
- Your browser is **Chrome or Safari**. Other browsers usually work,
  but Google's OAuth pages are designed around these two.
- `curl --version` runs cleanly in your terminal.

If you're in a half-completed state (binary downloaded, or
`client_secret.json` present but auth broken), run
`checklists/setup-state.md` first to locate where you got stuck, then
jump straight to the matching section. **Do not rerun the whole
flow.**

---

## Choose your path: Path A (Fast) vs Path B (Manual)

This walkthrough splits into **two paths**. Pick one based on whether
`gcloud` is available:

```bash
command -v gcloud >/dev/null && echo "gcloud installed" || echo "gcloud not installed"
```

| Condition | Path | Why |
|---|---|---|
| `gcloud` already installed, **or** you're willing to let the script install it | **Path A (Fast Path)** | ~6–8 minutes; automates project creation + API enable |
| You'd rather not install gcloud and prefer clicking through the Console | **Path B (Full Manual)** | ~10–15 minutes; Console + bash only |

> **Both paths share the same ending**: §Local 4 steps (move
> `client_secret.json` → env vars → `gws auth login` → verify).

**Decision tree**:

```
                  ┌──────────────────────────┐
                  │  command -v gcloud?      │
                  └────────────┬─────────────┘
                      yes      │      no
                  ┌────────────┴────────────┐
                  ▼                         ▼
           ┌─────────────┐         ┌──────────────────┐
           │ Path A      │         │ Install gcloud?  │
           │ auto-setup  │         └────┬──────────┬──┘
           └──────┬──────┘              │ yes      │ no
                  │                     ▼          ▼
                  │              ┌──────────┐  ┌────────┐
                  │              │ Path A   │  │ Path B │
                  │              │ (after   │  │ (click │
                  │              │  install)│  │  UI)   │
                  │              └────┬─────┘  └───┬────┘
                  └─────────────────┐ │            │
                                    ▼ ▼            ▼
                           ┌──────────────┐  ┌──────────────┐
                           │ 2 Console    │  │ 6 Console    │
                           │ steps        │  │ steps        │
                           │ (Audience +  │  │ (full flow)  │
                           │  Clients)    │  │              │
                           └──────┬───────┘  └──────┬───────┘
                                  │                 │
                                  └────────┬────────┘
                                           ▼
                                   ┌───────────────┐
                                   │ 4 local steps │
                                   │ (shared tail) │
                                   └───────────────┘
```

---

## URL reference (used by both paths)

Every Google Auth Platform page binds project context through
`?project=<PROJECT_ID>`. This document uses `<PROJECT_ID>` as a
placeholder for the project ID you just created (**not** the Project
Name — the ID is visible in the project selector dropdown at the top
of the Console and usually looks like `slides-toolkit-123456`).

| Page | URL |
|---|---|
| Overview | `https://console.cloud.google.com/auth/overview?project=<PROJECT_ID>` |
| Branding | `https://console.cloud.google.com/auth/branding?project=<PROJECT_ID>` |
| Audience | `https://console.cloud.google.com/auth/audience?project=<PROJECT_ID>` |
| Clients | `https://console.cloud.google.com/auth/clients?project=<PROJECT_ID>` |
| Data Access | `https://console.cloud.google.com/auth/dataaccess?project=<PROJECT_ID>` |
| API Library | `https://console.cloud.google.com/apis/library?project=<PROJECT_ID>` |

> **UI navigation fallback**: left-side hamburger menu → **Google
> Auth Platform**. If that item isn't visible, paste any of the URLs
> above directly into your browser.

---

# Path A — Fast Path (`gcloud` + `auto-setup.sh`)

> **Use this if**: you have gcloud, or you're willing to let the
> script install it. Total time: ~6–8 minutes.
>
> **Script contract**: `scripts/gws/auto-setup.sh` handles
> (1) detect / install gcloud → (2) `gcloud auth login` → (3) create
> project (if not already present) → (4) enable Slides + Drive API →
> (5) print the Console URLs and open the browser so you can finish
> the two remaining manual Console steps (Audience + Clients).

## §A1. Run `auto-setup.sh`

**Why this step matters**: Path B's §1 (create project) and §6
(enable APIs) are automatable. This script does them for you and
leaves only the two steps that *must* happen in the Console UI
(creating an OAuth client + adding a test user — no gcloud equivalent
API exists for either).

**Do this**:

```bash
cd /path/to/monkey-skills/slides-toolkit
bash scripts/gws/auto-setup.sh
```

**What the script does** (hands-off):

1. `command -v gcloud` check. If missing, it prompts you to run
   `brew install --cask google-cloud-sdk`.
2. `gcloud auth login` (one browser OAuth allow).
3. `gcloud projects create slides-toolkit-<random>`, or reuse an
   existing one.
4. `gcloud services enable slides.googleapis.com drive.googleapis.com`.
5. Prints the Console URLs you'll need:
   - Branding page (for §A2)
   - Audience page (for §A3)
   - Clients page (for §A4)
6. Opens the Branding page in your browser via `open <url>`.

**✅ Verify**: the terminal prints something like:

```json
{
  "project_id": "slides-toolkit-123456",
  "gcloud_version": "5XX.0.0",
  "apis_enabled": ["slides.googleapis.com", "drive.googleapis.com"],
  "next": "Complete Branding/Audience/Clients in browser"
}
```

**❌ Common errors**:
- `command not found: gcloud` (installation didn't stick) → install
  manually with `brew install --cask google-cloud-sdk` and rerun.
- `ERROR: (gcloud.projects.create) Project creation failed` → project
  IDs must be globally unique. Try a different suffix, or point
  `gcloud config set project` at an existing project and rerun.
- `API [slides.googleapis.com] not enabled on project ...` despite
  exit 0 → your account has no Billing link. (Personal Gmail is free
  tier but still needs a link.) Visit
  `https://console.cloud.google.com/billing` to link the free tier,
  then rerun.

## §A2. Branding (equivalent of Path B §2)

**Why this step matters**: the Branding page in the new UI = the
"App information" section of the old "OAuth consent screen". Google
uses what you enter here as the app identity shown on the consent
screen.

**Do this**:

1. `auto-setup.sh` will have already opened
   `https://console.cloud.google.com/auth/branding?project=<PROJECT_ID>`.
2. If the project is using Google Auth Platform for the first time,
   you'll see a **Get Started** button. Click it — the new UI asks for
   Branding + Audience basics in a single wizard.
3. Fill in:
   - **App name**: `slides-toolkit`
   - **User support email**: your own Gmail
   - **Audience**: **External** (personal Gmail has no org, so this
     is the only option)
   - **Developer contact information**: your own Gmail
4. Click **CREATE** (or **Save**).

**✅ Verify**: the Branding page shows App name = `slides-toolkit`
and Publishing status = **Testing**.

**❌ Common errors**:
- You accidentally clicked **PUBLISH APP** and landed on Verification
  needed → click **BACK TO TESTING** to revert.
- App-name collision (rare on personal projects) → pick a different
  name.

## §A3. Audience → Test users (equivalent of Path B §3)

**Why this step matters**: under Testing mode, Google only allows
Gmail addresses on the Test users list to complete OAuth. **If you
skip this step you'll hit `403 access_denied` at §Local step L3** —
this is the single most common beginner trap.

> **New-UI gotcha**: Test users is **not a separate page** — it's a
> section partway down the **Audience** page.

**Do this**:

1. Navigate to
   `https://console.cloud.google.com/auth/audience?project=<PROJECT_ID>`.
2. Scroll down to the **"Test users"** section.
3. Click **+ Add users**.
4. Enter your own Gmail (must match the account you'll later use with
   `gws auth`).
5. Click **Save**.

**✅ Verify**: the Test users list contains your Gmail, and the page
shows "Up to 100 test users allowed".

**❌ Common errors**:
- Can't find the Test users section → scroll to the bottom of the
  Audience page. The new UI buries it under the fold.
- Three different Gmail addresses in play (Console login / Test user /
  `gws auth`) — they must all be the same account. Confirm the avatar
  in the top right corner of the Console.

## §A4. Create the Desktop OAuth Client (equivalent of Path B §4 + §5)

**Why this step matters**: this is the OAuth client gws will use for
its auth flow. **Application type must be `Desktop app`** — not Web,
not Mobile. Desktop type hands you a client ID + client secret and
can open a localhost callback, which is exactly what a CLI tool
needs. Web type requires a public redirect URI and won't work.

**Do this**:

1. Navigate to
   `https://console.cloud.google.com/auth/clients?project=<PROJECT_ID>`.
2. Click **+ Create client** (new-UI name; old UI was "Create
   Credentials" → "OAuth client ID").
3. **Application type**: pick **Desktop app**.
4. **Name**: `slides-toolkit-cli`.
5. Click **Create**. A dialog shows you the Client ID / Client Secret.
6. Click **Download JSON**. The file lands in
   `~/Downloads/client_secret_*.json`.

**✅ Verify**:
- The Clients list contains one new OAuth 2.0 Client of type Desktop.
- `~/Downloads/` contains a freshly downloaded
  `client_secret_*.json`.

**❌ Common errors**:
- You picked Web application → you'll hit `invalid_redirect_uri`
  later. Return to this page, delete the client, and recreate it as
  Desktop app.
- You closed the dialog without clicking Download JSON → no problem.
  The Clients list has a download icon (down arrow) on the right of
  each row; click it to download again.

**Path A is done with the Console portion — jump to [§Local](#local--4-steps-local-commands-shared-by-both-paths)**.

---

# Path B — Full Manual (Console + bash only)

> **Use this if**: you'd rather not install gcloud and prefer UI
> clicks. Total time: ~10–15 minutes.
>
> Everything happens in the new Console UI (Google Auth Platform) +
> local bash commands.

## §B1. Create a GCP project

**Why this step matters**: OAuth Client IDs must belong to a GCP
project — that's Google's tenant boundary. All your API quota,
credentials, and audit logs will live under this project.

**Do this**:

1. Open https://console.cloud.google.com.
2. If this is your first visit, accept the T&C.
3. Find the project selector in the top-left (it may currently show
   "Select a project").
4. In the dropdown, click **NEW PROJECT** in the top-right of the
   popup.
5. **Project name**: `slides-toolkit` (or anything you prefer).
6. **Organization**: pick **No organization** (personal Gmail has no
   org).
7. Click **CREATE**, wait ~30 seconds.
8. Switch the top-right project selector to your newly created
   project.

**✅ Verify**: the project selector shows your new project name, and
the URL bar's `?project=<PROJECT_ID>` carries the new ID. **Record
this `<PROJECT_ID>`** — every URL below uses it.

**❌ Common errors**:
- "You don't have permission to create projects" → your current
  account may be restricted by a Google Workspace policy. Switch to a
  genuinely personal Gmail.
- Project created but not visible → reload and confirm the dropdown
  actually selected it.

## §B2. Branding (the new name for OAuth consent screen)

**Why this step matters**: GCP's OAuth stack requires you to declare
"who can use my app" before it'll issue tokens. Personal Gmail has no
org, so your only option is **External**. If you don't want to go
through Google's production verification, you stay on **Testing**.
The cost of Testing is a 7-day refresh token lifetime (see SKILL.md
§Every 7 days maintenance); the benefits are zero review and zero
waiting.

> **New-UI change**: the old "APIs & Services → OAuth consent screen"
> is now **Google Auth Platform → Branding** (`/auth/branding`). The
> new UI splits Branding and Audience into separate pages, but the
> **Get Started** wizard asks for the required fields from both at
> once.

**Do this**:

1. Open
   `https://console.cloud.google.com/auth/branding?project=<PROJECT_ID>`
   (or go via hamburger menu → **Google Auth Platform** →
   **Branding**).
2. If this is your first time here, click **Get Started**.
3. App information:
   - **App name**: `slides-toolkit`
   - **User support email**: your own Gmail
4. Next, Audience:
   - **User Type**: **External**
5. Next, Developer contact:
   - **Email address**: your own Gmail
6. Click **Create**.

**✅ Verify**: the Branding page shows App name =
`slides-toolkit`, and the Overview page
(`/auth/overview?project=<PROJECT_ID>`) shows Publishing status =
**Testing**.

**❌ Common errors**:
- You accidentally clicked **PUBLISH APP** → you're now in
  Verification needed. Click **BACK TO TESTING** to revert.
- The Scopes page asks you to add scopes → **don't add any**. Scopes
  are requested dynamically by the CLI during `gws auth login`.
  Skip / Save and continue.

## §B3. Audience → Test users

**Why this step matters**: under Testing mode, Google only allows
Gmail addresses on the Test users list to complete OAuth. **Skipping
this = `403 access_denied` at §L3**.

> **New-UI gotcha**: Test users is **not a separate page** — it's a
> section of the **Audience** page. (An earlier version of the UI
> briefly made it its own page; the current UI merges them.)

**Do this**:

1. Open
   `https://console.cloud.google.com/auth/audience?project=<PROJECT_ID>`.
2. Scroll down to the **"Test users"** section.
3. Click **+ Add users**.
4. Enter your own Gmail. This must be the same Gmail you used to log
   into the Console and the one you'll use with `gws auth` later —
   all three must match.
5. Click **Save**.

**✅ Verify**: the Test users list shows your Gmail.

**❌ Common errors**:
- Spent ages looking for a "Test users" page → it's not a page, it's
  a section on Audience. Scroll down.
- Three different Gmail accounts in play → check the avatar in the
  top-right corner of the Console to confirm which account you're
  signed in as.

## §B4. Create the Desktop OAuth Client (Clients page)

**Why this step matters**: this is the OAuth client gws will use to
run its auth flow. **Application type must be `Desktop app`** — not
Web, not Mobile.

> **New-UI change**: the old Credentials page is now **Clients**
> (`/auth/clients`). "+ CREATE CREDENTIALS → OAuth client ID" has
> been replaced by a direct **+ Create client**.

**Do this**:

1. Open
   `https://console.cloud.google.com/auth/clients?project=<PROJECT_ID>`.
2. Click **+ Create client**.
3. **Application type**: pick **Desktop app**.
4. **Name**: `slides-toolkit-cli`.
5. Click **Create**. The dialog shows you the Client ID / Client
   Secret.

**✅ Verify**: the Clients list contains a new entry with type =
Desktop, Name = `slides-toolkit-cli`.

**❌ Common errors**:
- Picked Web application → `gws auth login` will hit
  `invalid_redirect_uri`. Return here, delete, and recreate as
  Desktop.

## §B5. Download `client_secret.json`

**Why this step matters**: the gws CLI reads this JSON to find the
client ID and client secret.

**Do this**:

1. In the dialog from §B4, click **Download JSON**.
2. If you've already closed the dialog, use the download icon (down
   arrow) on the right of the Clients list row.

**✅ Verify**: `~/Downloads/client_secret_*.json` exists.

**❌ Common errors**:
- Dialog closed and you can't see a download icon → reload the page;
  the icon sometimes only appears when you hover the row.

## §B6. Enable APIs: Google Slides API + Google Drive API

**Why this step matters**: GCP enables no APIs by default — you must
explicitly enable each one you want to call. gws-toolkit needs four
APIs (covering the scope set granted in §L3):

- **Google Slides API** — for `presentations.create` / `batchUpdate`
  (`createSlide` / `insertText` / `createImage`).
- **Google Drive API** — for `files.create` (image upload), `files.list`
  (search via `q`), `files.update` (trash), `permissions.create`
  (sharing). Scope = `drive` (full); the toolkit's three-tier
  `safe-delete.sh` wrapper enforces trash-default + typed confirmation
  for destructive ops, providing application-layer safety equivalent
  to a narrower scope.
- **Google Docs API** — for `documents.{create, batchUpdate, get}` via
  vendored `gws-docs` skill.
- **Google Sheets API** — for `spreadsheets.{create, batchUpdate, get,
  values.append, values.get}` via vendored `gws-sheets` skill.

**Do this**:

1. Open
   `https://console.cloud.google.com/apis/library?project=<PROJECT_ID>`.
2. Search `Google Slides API` → open it → click **Enable**.
3. Navigate back (or reopen the library URL), search
   `Google Drive API` → open → click **Enable**.

**✅ Verify**: open
`https://console.cloud.google.com/apis/dashboard?project=<PROJECT_ID>`
and confirm both Slides API and Drive API are listed.

**❌ Common errors**:
- You enabled Slides but forgot Drive → template-copy will fail with
  `403 API not enabled`.
- You enabled extra APIs (e.g. Google Docs API) → harmless but
  violates least-privilege. Ignore, or disable from the API
  dashboard.

**Path B is done with the Console portion — continue to §Local below**.

---

# §Local — 4 steps (local commands, shared by both paths)

> Both Path A (after §A1–A4) and Path B (after §B1–B6) start here.

## §L1. Move `client_secret.json` → `~/.config/gws/`

**Why this step matters**: `~/.config/gws/` is the gws convention,
and it lines up with rule 2 of `standards/credential-hygiene.md`
(user credentials live only in `~/.config/gws/`).

**Do this**:

```bash
mkdir -p ~/.config/gws
chmod 700 ~/.config/gws
mv ~/Downloads/client_secret_*.json ~/.config/gws/client_secret.json
chmod 600 ~/.config/gws/client_secret.json
```

**✅ Verify**:

```bash
ls -l ~/.config/gws/client_secret.json
# -rw-------  1 you  staff  ~400  ...  client_secret.json
```

Permissions must be `600` (readable/writable only by you). This rule
comes from `standards/credential-hygiene.md` and ASVS V14.

**❌ Common errors**:
- Forgot to chmod → `.gitignore` will block accidental commits, but
  other processes with home-dir read access can still read the file.
  Run chmod immediately.
- Wrong path → gws will report missing `client_secret`. Both
  `env-guard.sh` and `credential-check.sh` hard-code this path.

## §L2. Run `bootstrap.sh` and set the env vars

**Why this step matters**: this skill doesn't require you to
preinstall `gws` or `jq`. `bootstrap.sh` fetches both binaries from
their official GitHub releases into `~/.cache/gws-toolkit/bin/`.

Then we write the issue #119 env vars into `~/.config/gws/env.sh`:
the gws built-in OAuth client trips `invalid_scope` /
`invalid_client` on personal Gmail, so we point gws at your own
OAuth client instead. Full details:
`protocols/issue-119-workaround.md`.

**Do this**:

```bash
cd /path/to/monkey-skills/slides-toolkit

# 1) Fetch binaries
bash scripts/gws/bootstrap.sh

# 2) Write env vars to ~/.config/gws/env.sh (chmod 600)
bash scripts/gws/env-guard.sh apply
```

What `env-guard.sh apply` does internally is equivalent to:

```bash
cat > ~/.config/gws/env.sh <<EOF
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
EOF
chmod 600 ~/.config/gws/env.sh
```

From then on, `scripts/gws/gws-wrap.sh` sources this file
on every call.

**✅ Verify**:

```bash
source ~/.config/gws/env.sh
echo $GOOGLE_WORKSPACE_CLI_CLIENT_ID
# 40+ character string, usually ending in .apps.googleusercontent.com

ls -l ~/.config/gws/env.sh
# -rw-------  1 you  staff  ...  env.sh
```

**❌ Common errors**:
- bootstrap exits with download failure → confirm the network and
  the upstream release URL. (SHA-256 verification was retired in
  v0.4.0; HTTPS + URL pin + official GitHub org is now the integrity
  boundary — TECH-SPEC §2.3.)
- exit 1 `unknown platform` → your machine isn't darwin-arm64 or
  darwin-x86_64. The MVP doesn't support Linux / WSL.
- `jq: command not found` → `bootstrap.sh` didn't finish, or PATH
  doesn't include `~/.cache/gws-toolkit/bin`.
- One of the env vars is the empty string → `client_secret.json`
  structure is off (you probably picked the wrong client type at
  download). Return to §A4 / §B4 and confirm Desktop app was
  selected.

## §L3. Run `gws auth login` and consent in the browser

**Why this step matters**: this is where gws obtains the refresh
token. gws opens a browser for you to consent to the requested
scopes, takes the callback on `localhost`, and writes the token to
the Keychain (or file backend as fallback).

**Do this**:

```bash
source ~/.config/gws/env.sh   # if §L2 was not in the same shell
gws auth login --scopes=https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets
```

**Important**: **list the 6 scope URLs explicitly** (least-privilege,
TECH-SPEC §4.4). gws v0.22.5's scope picker fetches all available
scopes from each enabled API's Discovery Document (`setup.rs:259-371`);
Testing mode caps consent at 25 scopes total — picking "all scopes"
in the picker exceeds that and produces `invalid_scope`. The 6-URL
explicit list keeps you well under.

The browser flow:

1. The terminal prints a URL and opens the browser automatically.
2. The browser lands on Google's account picker / login. Pick the
   Gmail you added as a Test user in §A3 / §B3.
3. You'll see "**Google hasn't verified this app**". **This is
   expected** — you never requested production verification.
4. Click **Advanced** in the bottom left.
5. Click **Go to slides-toolkit (unsafe)** (the text matches the App
   name you set in §A2 / §B2).
6. Review the scope list (4 entries):
   - `See, edit, create, and delete all your Google Drive files`
     (drive — full; the toolkit's safe-delete wrapper enforces
     trash-default + typed confirmation policy)
   - `See, edit, create, and delete all your Google Slides
     presentations` (presentations)
   - `See, edit, create, and delete all your Google Docs documents`
     (documents)
   - `See, edit, create, and delete all your Google Sheets
     spreadsheets` (spreadsheets)
7. Click **Continue** → **Allow**.
8. The browser shows "Authentication successful, you can close this
   tab".
9. The terminal shows `Login successful` or similar.

**✅ Verify**: see §L4.

**❌ Common errors**:
- `invalid_scope` → you picked too many scopes (Testing mode caps
  consent at 25 total) or used a preset that pulls extras. Pass the
  6-URL explicit list shown above.
- `invalid_client` → §L2 env vars were not exported / `env.sh` was
  not sourced. Return to §L2.
- `403 access_denied` → the Gmail you signed in with is **not** on
  the Test users list. Add it at §A3 / §B3.
- You clicked **Back to safety** and cancelled → just rerun `gws
  auth login`.
- Callback stuck → the browser tab was closed, or a firewall is
  blocking loopback. Rerun `gws auth login` and verify `127.0.0.1`
  is reachable.

## §L4. Verify with `gws auth status`

**Why this step matters**: confirms the refresh token is stored
(Keychain or file backend) so subsequent calls won't re-trigger
OAuth.

**Do this**:

```bash
gws auth whoami
gws auth status
```

**✅ Verify**:

```bash
$ gws auth whoami
your_email@gmail.com

$ gws auth status
Backend: keychain          # or file (see SKILL.md §Workarounds)
Token valid: true
Expires in: 6d 23h 58m     # 7-day hard cap under Testing mode
```

**❌ Common errors**:
- `gws auth whoami` prints nothing → return to §L3 and re-login.
- Backend = file (not keychain) → macOS Keychain silently failed and
  the fallback activated. Read the Keychain section of SKILL.md
  §Workarounds; this is not an error.
- Expires in shows a negative value → more than 7 days elapsed. Run
  `gws auth login` to re-auth (see SKILL.md §Every 7 days
  maintenance).

---

## Completion criterion

```bash
gws auth whoami
# Returns your Gmail = ✅ setup complete
```

Now you can switch to `slides-builder` and build your first
deck. If `whoami` doesn't return anything or errors out, walk through
`checklists/setup-state.md` to diagnose.

## Estimated total time

| Path | Segment | Estimate |
|---|---|---|
| **Path A** | §A1 auto-setup.sh (including first-time gcloud install) | 3–4 minutes |
| | §A2–A4 Console manual (Audience + Clients) + 1 browser OAuth | 2–3 minutes |
| | §L1–L4 Local | 1–2 minutes |
| | **Path A total** | **~6–8 minutes** |
| **Path B** | §B1–B6 Console manual (6 steps) | 7–10 minutes |
| | §L1–L4 Local | 2–5 minutes |
| | **Path B total** | **~10–15 minutes** (KR2 target ≤ 20 minutes) |

Next time you set up a new machine, jump straight to §L2 — you can
reuse the existing GCP project, OAuth client, and enabled APIs.
Only bootstrap and re-auth need to run again.
