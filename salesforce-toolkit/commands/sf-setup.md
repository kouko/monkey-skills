---
name: sf-setup
description: First-time salesforce-toolkit setup — brew installs sf CLI + salesforce-mcp, runs sf org login web for your Salesforce instance, sets default alias. Idempotent — safe to re-run after partial failure or token expiry.
allowed-tools: Bash(bash:*), Bash(brew:*), Bash(sf:*), Bash(curl:*), Bash(command:*)
---

# /sf-setup

End-to-end Salesforce DX backend onboarding — replaces the manual `brew install sf` → `sf org login web` → alias-bookkeeping walkthrough with an idempotent automation that wires `sf` + `salesforce-mcp` and authenticates your default org.

`$ARGUMENTS` accepts:

| Flag | Effect |
|---|---|
| `--dry-run` | Print the plan only; no `brew` / `curl` / `sf` invocations. Safe to run anywhere. |
| `--alias=<name>` | Explicit alias override (Layer 1 — wins over inference). |
| `--no-alias` | Force omit alias; `sf` derives one from your username. Mutually exclusive with `--alias=<name>`. |
| `--no-prompt` | Skip the Enter-to-accept prompt; use the inferred (or empty) alias directly. |
| `--force-reauth` | Re-run `sf org login web` even when an active default org already exists. |
| `--instance-url=<url>` | Pass-through to `sf org login web --instance-url=<url>`; also feeds the Layer-2 subdomain alias parser. |
| `--skip-mcp-brew` | Skip step 4 (`brew install salesforce-mcp`); the launcher shim falls back to `npx` at runtime. |

## Run

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/auto-setup.sh" $ARGUMENTS
```

If `CLAUDE_PLUGIN_ROOT` is not set in your runtime, resolve via the directory containing this command file (`$(dirname this-file)/..`).

## What it does

6 idempotent steps. First-time end-to-end: ~3-5 minutes (most time is the `sf org login web` browser OAuth flow). Already-set-up: ~5 seconds (each step probes current state and skips).

| # | Step | Action |
|---|---|---|
| 1 | OS + TTY guard | macOS only (`uname -s == Darwin`); requires a controlling terminal for OAuth + Enter-to-accept prompts. Skipped in `--dry-run`. |
| 2 | Ensure Homebrew | `command -v brew` else prompt + run the official `https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh` curl-pipe (y/N confirmation required). |
| 3 | Ensure `sf` CLI | `command -v sf` else `brew install sf`. Captures `sf --version` for the final JSON. |
| 4 | Ensure `salesforce-mcp` | `command -v salesforce-mcp` else `brew install salesforce-mcp`. Skipped under `--skip-mcp-brew` (launcher shim handles npx fallback at runtime). |
| 5 | `sf org login web` | 3-layer alias resolution (explicit `--alias=` / `--instance-url=` subdomain parse / well-known endpoint) → Enter-to-accept prompt → `sf org login web [--alias=…] [--set-default] [--instance-url=…]`. Skipped when an active default org already exists, unless `--force-reauth`. |
| 6 | Verify + JSON | `sf org display [--target-org=<alias>] --json` to confirm; extract `instanceUrl` + `accessTokenExpirationDate`; emit final stdout JSON. |

Final stdout: JSON with `{status, sf_version, mcp_version, org_alias, instance_url, oauth_expiry, elapsed_sec, dry_run}`.

## Prerequisites

- **macOS only** (MVP) — `darwin-arm64` or `darwin-x86_64`. Step 1 hard-fails with exit 11 on other OSes.
- **TTY required** — run from Terminal.app / iTerm2 / VSCode integrated terminal. Not from a piped stdin or background bash invocation; steps 2, 5 need `/dev/tty` for confirmation prompts and OAuth.
- **Salesforce org credentials** — a Production, Sandbox, Scratch, or Developer Edition org you can sign into via browser OAuth. For non-Production orgs pass `--instance-url=<url>` (e.g. `--instance-url=https://test.salesforce.com` for sandboxes).

## Re-running / idempotence

Each step probes current state and emits an `already done: <step>` stderr line when complete. Safe to re-run after a partial failure — only the failed step (and its dependents) will re-execute.

- **Token expired** (every-N-hours re-auth) — re-run with `--force-reauth` to re-authenticate the same alias without touching brew installs.
- **New org / alias** — re-run with `--alias=<new-name> --instance-url=<url>` to add another org without disturbing the existing default.

## When this doesn't apply

- Just expired token — `sf org login web --alias=<existing-alias>` directly is faster than `/sf-setup`.
- State detection / debugging — read the underlying `scripts/sf/auto-setup.sh` (annotated step headers) and `scripts/sf/alias-infer.sh` (3-layer algorithm) directly.
- Non-macOS host — Phase 2+; manual setup required (`brew` doesn't apply; install `sf` per the official Salesforce DX docs and run `sf org login web` by hand).
- Org-level admin needed first — if your org requires API access enablement, Connected App approval, or IP allow-listing, do that in the Setup UI before re-running.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `auto-setup.sh requires a controlling terminal` (exit 10) | Invoked without TTY (background bash / piped stdin) | Re-run from a real terminal app |
| `unsupported OS` (exit 11) | Not macOS | Phase 2+; install `sf` + run `sf org login web` manually |
| `brew install sf failed` / `brew install salesforce-mcp failed` (exit 12) | Network, brew tap drift, or disk-full | Run the failing `brew install ...` directly to surface the real error; re-run `/sf-setup` after fixing. Use `--skip-mcp-brew` to defer the MCP install. |
| `sf org login web failed` (exit 10) | OAuth flow cancelled, wrong account picked, or `--instance-url` mismatch (e.g. sandbox URL on Production login) | Re-run with `--force-reauth`; pass `--instance-url=https://test.salesforce.com` for sandboxes |
| `--no-alias and --alias=<name> are mutually exclusive` (exit 1) | Both flags passed | Pick one — explicit alias or username-derived default |
| Final `sf org display` empty / verify fails (exit 10) | Login appeared to succeed but token didn't persist (Keychain ACL block, profile drift) | Re-run with `--force-reauth`; if it recurs, run `sf org logout --target-org=<alias>` then re-try |

## See also

- `docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` — full PRODUCT-SPEC (Decision setup steps, JSON contract)
- `docs/code-toolkit/plans/2026-05-20-salesforce-toolkit-v0.1.0-part-2.md` — Part-2 plan (this command's parent atomic task)
- `scripts/sf/auto-setup.sh` — the underlying installer (step-by-step source)
- `scripts/sf/alias-infer.sh` — 3-layer alias inference (explicit / instance-url subdomain / well-known endpoint)
