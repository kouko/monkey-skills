---
name: sf-setup
description: Walks you through Salesforce DX backend setup entirely in this conversation — installs sf CLI + salesforce-mcp via brew, then opens browser for one OAuth click. No terminal switching.
allowed-tools: Bash(brew:*), Bash(sf:*), Bash(command:*), Bash(bash:*), Bash(jq:*), Bash(pkill:*)
---

# /sf-setup

**End-to-end Salesforce DX onboarding without leaving Claude Code** (after the one-time Homebrew prerequisite is met — see below). Claude orchestrates every step — probes state, installs missing binaries via brew, infers your org alias, runs OAuth in background + polls for completion, then tells you to `/reload-plugins`.

## Prerequisite (one-time, outside this command)

**Homebrew must already be installed.** This command does not install brew itself because the brew installer is interactive and runs `sudo` — which cannot work from a Claude Code Bash tool (no controlling terminal).

If `command -v brew` fails when this command runs, Claude will halt and show you the one-liner to paste into Terminal.app:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Run that once, restart Claude Code (so brew is in `PATH`), then re-invoke `/sf-setup`.

## $ARGUMENTS

| Flag | Effect |
|---|---|
| `--instance-url=<url>` | Salesforce instance URL (e.g. `https://ichef.my.salesforce.com`). If omitted, Claude asks via `AskUserQuestion` (unless `--no-prompt`, then defaults to Production). |
| `--alias=<name>` | Explicit alias override. If omitted, Claude infers from instance URL subdomain and asks you to confirm (unless `--no-prompt`, then uses inferred directly). |
| `--no-alias` | Force omit alias; `sf` derives one from your username. Mutually exclusive with `--alias=<name>`. |
| `--force-reauth` | Re-run `sf org login web` even when an active default org already exists. Disables the early-exit shortcut at Step 4. |
| `--skip-mcp-brew` | Skip `brew install salesforce-mcp`; the launcher shim falls back to `npx -y @salesforce/mcp` at runtime. |
| `--no-prompt` | Use inferred / default values directly; skip all `AskUserQuestion` prompts. Defaults: instance URL → Production, alias → URL-inferred. |

## Control flow

```
Step 0 Argument validation
   │   - reject --no-alias + --alias=X (mutex)
   │   - reject unknown flags
   │
   ├── invalid args? ──► HALT (error message) ─► END
   │
   ▼
Step 1 Probe
   │
   ├── brew missing? ──► HALT (show prereq + curl one-liner) ─► END
   │
   ▼
Step 2 Resolve target alias (cheap — needed for Step 4's early-exit comparison)
   │   - if --no-alias: target = "" (empty)
   │   - else if --alias=X: target = X
   │   - else if --instance-url=Y: target = infer_alias(Y, "")
   │   - else: target = null (unresolved — Step 4 case b handles)
   │   - NOTE: --no-prompt does NOT change this — it only suppresses
   │     interactive AskUserQuestion in Step 5+
   ▼
Step 3 Install missing binaries (idempotent — cheap if already installed)
   │   - emit BEFORE-progress: "🔧 Installing missing binaries (~2-3 min)..."
   │   - if BOTH missing: brew install sf salesforce-mcp (combined, v0.1.1+)
   │   - else if only sf missing: brew install sf
   │   - else if only salesforce-mcp missing AND NOT --skip-mcp-brew: brew install salesforce-mcp
   │   - emit AFTER-progress: "✅ Installed: sf vX.Y + salesforce-mcp vA.B"
   │
   ├── any brew install fails? ──► HALT (surface stderr) ─► END
   │
   ▼
Step 4 Early-exit check (skip OAuth if already authenticated)
   │   - probe authoritative connectedStatus via:
   │       sf org display --json
   │   - early-exit if ALL hold:
   │       • NOT --force-reauth
   │       • default_org connected (sf already authed)
   │     AND ANY of:
   │       (a) target equals current default alias (string match)
   │       (b) target is null (re-run with no relevant args)
   │       (c) target == "" AND --no-alias (user wants default; connected)
   │
   ├── early-exit? ──► emit summary + remind /reload-plugins ─► END
   │
   ▼
Step 5 Fully resolve instance URL + alias (interactive)
   │   - if --instance-url not set AND NOT --no-prompt: AskUserQuestion (4 options)
   │   - if --instance-url not set AND --no-prompt: default Production + warn user
   │   - run alias-infer.sh with final URL + --alias= value
   │   - if NOT --no-prompt AND NOT --alias= explicit: AskUserQuestion confirm alias
   │   - if --no-alias: force empty alias
   ▼
Step 6 OAuth in background + poll with 30-sec window progress (v0.1.1+)
   │   - Bash run_in_background: sf org login web [--alias=…] --set-default --instance-url=…
   │     (always pass --set-default; only --alias= is conditional on final_alias non-empty)
   │   - tell user browser will open + poll cadence
   │   - poll in 10 windows × 30 sec (6 polls × 5s each per window) — up to 5 min total
   │   - between EVERY window emit: "⏳ Still waiting... <Ns> elapsed (max 5 min)"
   │   - after window 2 (60s) add "sign in + click Allow on consent screen if not yet"
   │   - after window 8 (4:00) add "1 min before I'll ask continue/abort"
   │
   ├── poll timeout (window 10)? ──► ask user (continue / abort)
   │   ├── abort → pkill -INT -f "sf org login web --alias=…" → END (error)
   │   └── continue → reset window counter, another 5 min
   │
   ▼
Step 7 Verify + emit summary
   │   - sf org display --target-org=<alias> --json
   │   - extract instanceUrl / username / accessTokenExpirationDate
   │
   ▼
Step 8 Tell user to /reload-plugins ─► END
```

## Procedure (Claude follows these steps in order)

### Step 0 — Validate arguments

Before any work, check `$ARGUMENTS`:

- If both `--no-alias` and `--alias=<name>` appear → halt with error: "`--no-alias` and `--alias=<name>` are mutually exclusive. Pick one."
- If any flag is not in the `$ARGUMENTS` table above → halt with error: "unknown flag: `<flag>`. See `/sf-setup --help` or the `$ARGUMENTS` section."

(Unrecognised flags fail fast so typos don't silently change behavior. `$ARGUMENTS` parsing is whitelist, not blacklist.)

### Step 1 — Probe current state

Run via Bash tool:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/credential-check.sh"
```

Parse the JSON: `{brew, sf_cli, sf_version, salesforce_mcp, mcp_version, node, default_org, default_org_status}`.

**Halt if `.brew == "missing"`** — show the Prerequisite section above and stop. User must install brew in Terminal.app, restart Claude Code, then re-run.

### Step 2 — Resolve target alias (cheap pre-pass)

This is a lightweight resolution to enable Step 4's early-exit comparison. It does NOT yet open `AskUserQuestion` — that's deferred to Step 5 if needed.

| Input | `target_alias` becomes |
|---|---|
| `--no-alias` | `""` (empty — user wants omitted) |
| `--alias=X` (explicit) | `X` |
| `--instance-url=Y` (no `--alias`, no `--no-alias`) | `bash alias-infer.sh "Y" ""` result (may be empty) |
| Neither `--alias` nor `--instance-url` (with or without `--no-prompt`) | `null` (unresolved — Step 4 case b handles) |

**`--no-prompt` does NOT change `target_alias` resolution.** It only affects Step 5 (skip `AskUserQuestion` prompts, use defaults). Earlier versions of this doc had `--no-prompt + no --instance-url` map target to `"prod"`, which broke re-runs against existing non-prod default orgs — fixed.

### Step 3 — Install missing binaries (non-interactive, idempotent)

**Progress emit BEFORE the install** (so user sees the wait is starting, not silent):

> 🔧 Installing missing binaries via Homebrew (~2-3 min on a clean system)...

Then choose ONE of these three patterns based on Step 1's probe:

**Fast path — both missing (combined install, v0.1.1+)**:

If `.sf_cli == "missing"` AND `.salesforce_mcp == "missing"` AND `--skip-mcp-brew` was NOT passed, run a **single combined** brew install (saves one brew startup + parallel formula download):

```bash
brew install sf salesforce-mcp
```

**Slow paths — only one missing**:

If only `.sf_cli == "missing"`:
```bash
brew install sf
```

If only `.salesforce_mcp == "missing"` AND `--skip-mcp-brew` was NOT passed:
```bash
brew install salesforce-mcp
```

Both formulas (NOT casks) install non-interactively on modern Homebrew (≥4.x). Expect 1-3 min total on a clean system (combined path) or 2-6 min if installing sequentially across separate runs. **If both binaries are already installed from a prior run, Step 3 is a near-zero-cost no-op** (~50ms total for the two `command -v` probes embedded in `credential-check.sh`'s output).

**Progress emit AFTER the install** (so user sees concrete done state, not just "ok"):

> ✅ Installed: `sf v<sf_version>` + `salesforce-mcp v<mcp_version>` — proceeding to OAuth setup.

Substitute `<sf_version>` / `<mcp_version>` from the post-install `sf --version` + `brew list --versions salesforce-mcp` probes.

**On failure** (`brew install` returns non-zero):

1. Capture the full stderr from the failed `brew install`.
2. Halt: surface the stderr to user verbatim.
3. Tell user: "brew install failed. Run `brew install <package>` directly in Terminal.app to see the full error and recovery options. Re-run `/sf-setup` after fixing."
4. END procedure with error. Do NOT proceed to Step 4 — partial install state is the user's problem to resolve, not Claude's to paper over.

### Step 4 — Early-exit check (skip OAuth if already authenticated)

This step uses `sf org display --json` directly for authoritative `connectedStatus` (not `credential-check.sh`'s mapped value, to avoid value-mapping drift). **By the time we get here, Step 3 has guaranteed both `sf` and `salesforce-mcp` are installed (or `--skip-mcp-brew` opted out of the latter)** — so this early-exit only needs to consider OAuth state, not install state.

Pre-conditions to even probe (ALL must hold):

- `--force-reauth` NOT passed
- `.default_org` from Step 1 is non-empty (a default org exists)

If both hold, run:

```bash
sf org display --json 2>/dev/null
```

Parse `.result.connectedStatus`. **Early-exit if `connectedStatus == "Connected"` AND any one of**:

- (a) `target_alias` (from Step 2) is non-null AND non-empty AND equals `.result.alias`
- (b) `target_alias` is `null` (user passed no `--alias`, no `--instance-url`) — treated as "re-run with no args, just verify"
- (c) `target_alias == ""` AND `--no-alias` was passed — user wants the default which is connected

If early-exit fires:

1. Emit summary (Step 7 format) using current `sf org display --json` data
2. Tell user: "Already set up. If the MCP server isn't loaded yet, run `/reload-plugins`."
3. END procedure.

Otherwise, proceed to Step 5. **Multi-org safety**: when `target_alias` is non-null and DIFFERS from `.result.alias`, user is adding a new org → Steps 5-7 MUST run (do NOT skip), so this early-exit correctly falls through.

**Common scenario unblocked by re-ordering** (was a bug in early drafts): user has `sf` authed to ichef + missing `salesforce-mcp` only. Old order ran Step 3 early-exit first → gate fail because mcp missing → fell through to install → then re-OAuthed unnecessarily. New order (install first → early-exit second) lets Step 3 install salesforce-mcp + Step 4 detect "still authed, alias matches" → clean early-exit without redundant OAuth.

### Step 5 — Fully resolve instance URL + alias (interactive)

**Resolve instance URL**:

| Input state | Action |
|---|---|
| `--instance-url=<url>` passed in `$ARGUMENTS` | Use `<url>` directly |
| no `--instance-url`, `--no-prompt` passed | Default to `https://login.salesforce.com` (Production); emit `[/sf-setup] --no-prompt without --instance-url: defaulting to Production` to user |
| no `--instance-url`, no `--no-prompt` | Ask user via `AskUserQuestion`: 4 options below |

> **AskUserQuestion**: "Which Salesforce instance?"
> 1. **Production** (`https://login.salesforce.com`) — default for production orgs
> 2. **Sandbox** (`https://test.salesforce.com`) — for sandbox / test orgs
> 3. **My Domain** (e.g. `https://ichef.my.salesforce.com`) — for company-specific Domain

(The `AskUserQuestion` tool automatically appends an "Other" choice with free-text input — no need to enumerate it explicitly. If the user picks Other, Claude reads the typed URL from the response.)

**Resolve alias**:

If `target_alias` (from Step 2) is already non-null (i.e. user passed `--no-alias` or `--alias=X`, OR Step 2 inferred from a `--instance-url=Y` flag), **use it directly as `final_alias`** — no need to re-run alias-infer. The only case Step 2 left unresolved is "neither `--alias` nor `--instance-url`" → `target_alias = null`, which falls through to fresh inference here.

When `target_alias` is `null` (URL was just resolved above), run alias-infer.sh against the new URL:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/alias-infer.sh" "<resolved-url>" ""
```

(`alias-infer.sh` ships a direct-invocation entry point — `bash alias-infer.sh URL [ALIAS]` prints the resolved alias to stdout. 3-layer logic: explicit override → URL subdomain parse → well-known endpoint fallback → empty.)

| Input state | `final_alias` becomes |
|---|---|
| `--no-alias` passed | `""` (omit alias; sf uses username default) |
| `--alias=X` passed | `X` (already resolved in Step 2; skip confirmation) |
| `--no-prompt` passed (no `--alias`) | Step 2's `target_alias` if non-null, else alias-infer result against resolved URL (no confirmation) |
| Neither `--no-prompt` nor `--alias` | alias-infer result against resolved URL → ask user via `AskUserQuestion` to confirm |

> **AskUserQuestion**: "Use alias `<inferred>` for this org?"
> - Yes (accept `<inferred>`)
> - Use a different name (Claude will prompt for the custom alias)
> - Don't set alias (omit; `sf` uses username-derived default)

### Step 6 — OAuth in background + poll for completion

**Build the login command** (always export `SF_DISABLE_TELEMETRY=true` first to skip first-run consent prompt that would block in non-TTY):

```bash
SF_DISABLE_TELEMETRY=true sf org login web [--alias=<final_alias>] --set-default --instance-url=<resolved-url>
```

- If `final_alias` is **non-empty**: pass `--alias=<final_alias>` AND `--set-default`.
- If `final_alias` is **empty** (`--no-alias` path): omit only the `--alias=` flag; **still pass `--set-default`** so the newly-authed org becomes the default. Without `--set-default`, sf would log in but not mark this org as default → polling `sf org display --json` without `--target-org` would look at the OLD default and never detect the new login.

**Start in background** via Bash tool with `run_in_background: true`. The Bash tool returns a background reference; **also remember the exact `--alias` value** you launched with — that's the unique string used by `pkill -f` if abort is needed (sf-CLI background PID isn't directly exposed through the Bash tool's return; pattern-matching the command line is the robust kill mechanism).

**Tell the user**:

> 🌐 Opening browser for Salesforce OAuth. Sign in + click **Allow** when the consent screen appears. I'll check every 30 seconds and let you know when complete (up to 5 min). If the browser doesn't open within ~10 sec, see Troubleshooting — sf-CLI suppresses URL output in non-TTY mode so we can't inline the URL; fall back to Path B in your own terminal which prints the URL natively.

**Poll structure — 30-second windows with progress emit between (v0.1.1+)**:

The poll command:

```bash
SF_DISABLE_TELEMETRY=true sf org display --target-org=<final_alias> --json 2>/dev/null | \
  jq -e '.result.connectedStatus == "Connected"'
```

(If `final_alias` is empty, omit `--target-org=` flag — sf uses the most-recently-logged-in org by default.)

**Window structure** — split the 5-min poll budget into 10 windows of 30 sec each (6 polls × 5 sec per window):

```
Window 1: poll × 6 (5s each = 30s)  → if Connected, exit; else emit progress
Window 2: poll × 6                  → if Connected, exit; else emit progress
...
Window 10 (4:30-5:00): poll × 6     → if Connected, exit; else timeout handler
```

**Between every window, emit a progress line so the user knows you're still alive**:

> ⏳ Still waiting for OAuth completion... 30s elapsed (5 min max). If the browser tab didn't open, see Troubleshooting §"Browser didn't auto-open".

After **window 2 (60s)** add a hint:

> ⏳ 60s elapsed. Sign in + click **Allow** on the Salesforce consent screen if you haven't yet.

After **window 8 (4:00)** add a near-timeout warning:

> ⏳ 4 min elapsed. ~1 min remaining before I'll ask whether to keep waiting or abort.

**When `jq -e` returns exit 0 within any window** (Connected): emit success line + proceed to Step 7:

> ✅ OAuth complete — Salesforce org connected. Verifying setup...

**On poll timeout (after window 10 = 5 min)**: Ask user via `AskUserQuestion`:

> OAuth not detected yet (5 min elapsed). Choose:
> - Keep waiting — give me another 5 min
> - Abort — cancel and clean up

If **Abort**:
1. Kill the background process via pattern-match (sf-CLI PID is not directly exposed by `run_in_background`):
   ```bash
   pkill -INT -f "sf org login web --alias=<final_alias>"
   ```
   If `final_alias` was empty (`--no-alias` path), match a less-specific pattern: `pkill -INT -f "sf org login web --set-default --instance-url=<resolved-url>"`.
   SIGINT simulates Ctrl-C so sf shuts its localhost:1717 listener gracefully and frees the port. If SIGINT doesn't work after 3 seconds (unlikely), follow with `pkill -9 -f ...` as last resort.
2. Report to user: "Aborted. The `sf org login web` background process has been terminated. Re-run `/sf-setup --force-reauth` when ready."
3. END procedure with error status.

If **Keep waiting**: reset poll counter, loop again (another 60 × 5 sec = 5 min).

### Step 7 — Verify + emit summary

Final check:

```bash
sf org display --target-org=<final_alias> --json
```

Extract from `.result`: `instanceUrl`, `username`, `accessTokenExpirationDate`. Report to user:

> ✅ Salesforce setup complete
> - **Alias**: `<final_alias>` (or "(omitted — sf uses username default)" if empty)
> - **Instance**: `<instanceUrl>`
> - **Account**: `<username>`
> - **Token expires**: `<accessTokenExpirationDate>`

### Step 8 — Activate MCP server

Tell user with **visual emphasis** so the next-step doesn't get lost in the surrounding text (this is the most-commonly-forgotten step in v0.1.0 dogfood):

> ╔══════════════════════════════════════════════════════════════════╗
> ║  ⚠️  NEXT STEP REQUIRED — RUN: `/reload-plugins`                  ║
> ╚══════════════════════════════════════════════════════════════════╝
>
> The salesforce MCP server won't start until you run `/reload-plugins` (Claude Code primitive — must be triggered by you). Without it, the MCP server stays in its previously-failed state until you restart Claude Code.
>
> **Try these immediately after `/reload-plugins`** (paste-ready):
> - `列出最近 5 筆 Account`  /  `List the 5 most-recent Accounts`
> - `本季結案的 Opportunity 前 10 筆`  /  `Top 10 Opportunities closed this quarter`
> - `今年的 Lead 依 Source 分群`  /  `Leads this year grouped by Source`

The example queries serve two purposes: (1) demonstrate `sf-query` skill capability immediately, (2) give the user a concrete validation step — if the first query works, the whole pipeline is healthy.

END procedure.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `brew: command not found` halt at Step 1 | Homebrew not installed | Run the brew installer one-liner in Terminal.app (see Prerequisite), restart Claude Code, re-run `/sf-setup` |
| `brew install sf` or `brew install salesforce-mcp` fails at Step 4 | Network / tap drift / Homebrew API outage / disk full | Claude surfaces the stderr; resolve in Terminal.app (`brew install <pkg>` directly), then re-run `/sf-setup` |
| OAuth poll times out at Step 6 + user picks "Abort" | User closed browser / network blocked callback / OAuth consent denied | Re-run `/sf-setup --force-reauth`; check browser default + popup blocker |
| `sf org login web` immediately errors (e.g. before browser opens) | Wrong instance URL for org type (sandbox URL on Production login, or vice versa) | Re-run `/sf-setup --instance-url=<correct-url> --alias=<your-alias> --force-reauth` (pass `--alias` so it's preserved across the new URL — inference would otherwise re-compute from the new subdomain) |
| MCP server still failing after `/reload-plugins` | `sf-mcp-server` binary not installed yet (Step 4 skipped or `--skip-mcp-brew`; brew formula is `salesforce-mcp` but the binary it ships is `sf-mcp-server`) | Run `command -v sf-mcp-server` — if missing, re-run `/sf-setup` without `--skip-mcp-brew` |
| `--no-alias` and `--alias=<name>` both passed | Mutually exclusive (rejected at Step 0) | Pick one; re-run |
| `localhost:1717 already in use` error from sf | Previous `sf org login web` background process still alive (e.g. prior `/sf-setup` aborted but its bg process not killed) | Claude runs `pkill -f 'sf org login web'` (in-conversation) to free the port; then re-run `/sf-setup --force-reauth` |
| Browser didn't auto-open at Step 6 | `open` command failed (no default browser / sandbox / SSH session without X forwarding); ALSO sf-CLI suppresses URL output in non-TTY mode so Claude can't show URL inline | Fall back to Path B — run `bash $CLAUDE_PLUGIN_ROOT/scripts/sf/auto-setup.sh` in your own Terminal.app where sf prints the URL natively |
| sf-CLI hangs at Step 6 without opening browser | First-run telemetry consent prompt blocking (sf shows y/N prompt that needs stdin which is unavailable in non-TTY) | Procedure exports `SF_DISABLE_TELEMETRY=true` automatically; if you see this anyway, run `SF_DISABLE_TELEMETRY=true sf --version` once via Claude Bash to verify env var works, then retry `/sf-setup --force-reauth` |

## Alternative — terminal power-user path

If you prefer to run setup in your own terminal (one-shot, TTY-bound):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/auto-setup.sh"
```

This invokes the 6-step idempotent installer with TTY prompts (no Claude orchestration). Use when you want full control over the brew install confirmation, are debugging step-by-step, or are scripting `/sf-setup` into a larger provisioning pipeline. Both paths converge on the same end state — `sf` CLI authenticated + `salesforce-mcp` installed + default org bound.

## See also

- `docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` — PRODUCT-SPEC (setup steps, JSON contract)
- `scripts/sf/credential-check.sh` — state probe (Step 1 source)
- `scripts/sf/alias-infer.sh` — 3-layer alias inference (Steps 2 + 5 source)
- `scripts/sf/auto-setup.sh` — TTY-bound terminal-mode installer (alternative path)
- `scripts/sf/refresh-auth.sh` — standalone re-auth helper for token expiry
