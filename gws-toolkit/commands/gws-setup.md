---
name: gws-setup
description: First-time gws-toolkit setup — installs gcloud, runs OAuth login, creates GCP project, enables 4 Workspace APIs (Slides / Drive / Docs / Sheets), guides through OAuth Consent + Client setup, bootstraps gws + jq, runs gws auth login. Idempotent — safe to re-run after partial failure.
allowed-tools: Bash(bash:*), Bash(gcloud:*), Bash(brew:*), Bash(curl:*), Bash(gws:*), Bash(jq:*)
---

# /gws-setup

End-to-end Google Workspace backend onboarding — replaces the 10-step manual GCP Console walkthrough with an idempotent automation.

`$ARGUMENTS` accepts:

- `--dry-run` — print the plan only; no network / file / install changes
- `--force-reinstall` — force `gws auth login` to re-run even if already authed

## Run

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/gws/auto-setup.sh" $ARGUMENTS
```

If `CLAUDE_PLUGIN_ROOT` is not set in your runtime, resolve via the directory containing this command file (`$(dirname this-file)/..`).

## What it does

8 idempotent steps. First-time end-to-end: ~6-8 minutes (most time is OAuth Console clicking). Already-set-up: ~30 seconds (each step probes current state and skips).

| # | Step | Action |
|---|---|---|
| 1 | Detect / install gcloud | brew cask `google-cloud-sdk` preferred; falls back to the official `https://sdk.cloud.google.com` installer if brew is unavailable |
| 2 | `gcloud auth login` | Opens browser; skipped if an active account is already signed in |
| 3 | Create GCP project | `slides-toolkit-<YYMMDD>` by default; override via `SLIDES_TOOLKIT_PROJECT_ID` env var |
| 4 | Enable 4 APIs | Slides / Drive / Docs / Sheets (must match the OAuth scope set used in step 8) |
| 5 | Guided OAuth Consent screen | 5a Branding → 5b Test User → 5c OAuth Client. Opens one Console URL per sub-step, prints inline instructions, waits for the user's ENTER (read from `/dev/tty`). 5c also polls `~/Downloads/` for `client_secret_*.json` and validates it is a Desktop app (rejects Web app early) |
| 6 | Install credentials | Move `client_secret.json` → `~/.config/gws/` (chmod 600) + write `~/.config/gws/env.sh` (issue #119 workaround env vars) |
| 7 | Bootstrap binaries | Download `gws` + `jq` binaries to `~/.cache/slides-toolkit/bin/` (via `scripts/gws/bootstrap.sh`) |
| 8 | `gws auth login` + verify | `gws auth login --scopes=presentations,drive,documents,spreadsheets` then verify `gws auth status` reports `auth_method=oauth2` |

Final stdout: JSON with `{status, project_id, account, scopes, elapsed_sec, dry_run}`.

## Prerequisites

- **macOS only** (MVP) — `darwin-arm64` or `darwin-x86_64`
- **TTY required** — run from Terminal.app / iTerm2 / VSCode integrated terminal. Not from a piped stdin or background bash invocation; steps 5a/5b/5c need to prompt for ENTER
- **Personal `@gmail.com` account** — Google Workspace organization accounts: Phase 2+

## Re-running / idempotence

Each step probes current state and skips with an "already done" stderr line when complete. Safe to re-run after a partial failure — only the failed step (and its dependents) will re-execute. Use `--force-reinstall` to force step 8 re-auth even when an OAuth token is already valid.

## When this doesn't apply

- Just expired token (every-7-days re-auth) — run `gws auth login --scopes=presentations,drive,documents,spreadsheets` directly; `/gws-setup` would also work but is overkill
- State detection (you're unsure where things stand) — `bash scripts/gws/credential-check.sh` first; branch on the JSON
- Manual control / debugging — see the 10-step browser walkthrough in `skills/gws-setup/SKILL.md` §"Path B (manual)"

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `auto-setup.sh requires a controlling terminal` | Invoked without TTY (background bash / piped stdin) | Re-run from a real terminal app |
| `unsupported OS` | Not macOS | Phase 2+; manual setup required |
| `gcloud auth login failed` (exit 10) | OAuth flow cancelled, network issue, or wrong account | Re-run; idempotent |
| `gcloud projects create failed` (exit 12) | Quota / billing / name-collision issue | Try `SLIDES_TOOLKIT_PROJECT_ID=my-custom-id /gws-setup` |
| Step 5c stalls forever | `~/Downloads/client_secret_*.json` never appeared (download blocked, wrong app type, or not on the expected path) | Manually move the JSON to `~/Downloads/`, or re-run |
| Final `gws auth status` fails | issue #119 env vars missing (`env.sh` not sourced) | Verify `~/.config/gws/env.sh` exists; `source` it manually |

## See also

- `skills/gws-setup/SKILL.md` — full skill: Path A (this command) vs Path B (manual), state detection, error guide
- `scripts/gws/auto-setup.sh` — the underlying script
- `skills/gws-setup/protocols/gcp-console-walkthrough.md` — Path B's manual 10-step walkthrough
- `skills/gws-setup/protocols/issue-119-workaround.md` — env-var workaround documented in step 8
