# TECH-SPEC — salesforce-toolkit

Technical specification for the `salesforce-toolkit` plugin in the
`monkey-skills` repository. Scope: module design, data flow, interface
contracts. Product-level direction (users, JTBD, scope, non-goals,
competitive positioning, success criteria) lives in
[`PRODUCT-SPEC.md`](./PRODUCT-SPEC.md) and is referenced by section
name throughout this file.

- Spec type: TECH-SPEC (code-team ownership)
- Target plugin: `salesforce-toolkit` (v0.1.0, greenfield)
- Upstream PRODUCT-SPEC: [`./PRODUCT-SPEC.md`](./PRODUCT-SPEC.md)
- Upstream brief:
  [`../docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md`](../docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md)
- Hard constraints: macOS only (PRODUCT-SPEC §Users) / bash 3.2
  compatible (macOS default) / no Python runtime / no `ci:` commit type
  (use `chore(<plugin>)`) / UTF-8 only

---

## Reference

This TECH-SPEC is the technical counterpart of
[`PRODUCT-SPEC.md`](./PRODUCT-SPEC.md) under the
[CLAUDE.md §Two-Layer Spec convention](../CLAUDE.md): PRODUCT-SPEC owns
cross-domain product direction (Users / JTBD / Scope / Non-goals /
Competitive positioning / Success criteria); this TECH-SPEC owns the
technical realization (Modules / Data Flow / Interfaces / Setup Flow).

Section-by-section pointer map back to
[`PRODUCT-SPEC.md`](./PRODUCT-SPEC.md):

| TECH-SPEC section | Pairs with PRODUCT-SPEC.md section |
|---|---|
| §Modules | §Scope (Phase 1 file inventory) + §Competitive positioning (Path A DX MCP) |
| §Data Flow | §JTBD primary (read-only query path) + §Success criteria KR3 (read-only by default) |
| §Interfaces | §Scope (per-script affordance) + §Success criteria KR2 (idempotency) + KR4 (refresh-auth) |
| §Setup Flow | §JTBD primary (single-line setup) + §Success criteria KR1 (< 5 min end-to-end) + KR2 (idempotent re-run) |
| Non-goals (no Hosted MCP, no schema validation, no multi-org wrapper) | §Non-goals (verbatim mirror) |

Brief Decision Q1–Q7 (in [`../docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md`](../docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md))
are realized as:

- Q1 (Path D shim launcher) → §Modules `bin/sf-mcp-launcher.sh`
- Q2 (toolsets `data,metadata`) → §Modules `.mcp.json` args
- Q3 (3-layer alias infer) → §Modules `scripts/sf/alias-infer.sh`; §Interfaces `alias-infer.sh` contract
- Q4 (Enter-to-accept UX) → §Setup Flow Step 5
- Q5 (sf-query + sf-report skills) → §Modules skills/
- Q6 (`prod` / `sandbox` alias names) → §Interfaces `alias-infer.sh` Layer 3
- Q7 (brew→npx shim fallback) → §Modules `bin/sf-mcp-launcher.sh`

---

## Modules

### Plugin layout (target v0.1.0 state)

```
salesforce-toolkit/
├── .claude-plugin/
│   └── plugin.json             # plugin manifest + marketplace.json sync source
├── PRODUCT-SPEC.md             # cross-domain product spec
├── TECH-SPEC.md                # this file
├── README.md                   # plugin top-level entry (en, authoritative)
├── README.ja.md                # ja translation (PR #150 i18n rule)
├── README.zh-TW.md             # zh-TW translation (PR #150 i18n rule)
├── CHANGELOG.md
├── LICENSE-MIT.txt
├── .mcp.json                   # static MCP server config; shim dispatch
├── bin/
│   └── sf-mcp-launcher.sh      # brew→npx dynamic dispatcher (Q1 Path D)
├── commands/
│   └── sf-setup.md             # /salesforce-toolkit:sf-setup slash command
├── scripts/
│   ├── common/
│   │   └── tty-guard.sh        # require_tty helper (sourced by setup scripts)
│   └── sf/
│       ├── alias-infer.sh      # 3-layer alias inference (Q3); sourced
│       ├── credential-check.sh # read-only diagnostic; JSON stdout
│       ├── auto-setup.sh       # 6-step idempotent installer (orchestrator)
│       └── refresh-auth.sh     # standalone re-auth helper
├── skills/
│   ├── sf-query/
│   │   ├── SKILL.md            # SOQL/SOSL natural-language query
│   │   ├── README.md           # en, authoritative
│   │   ├── README.ja.md
│   │   └── README.zh-TW.md
│   └── sf-report/
│       ├── SKILL.md            # Dashboard/Report fetch + analyze
│       ├── README.md
│       ├── README.ja.md
│       └── README.zh-TW.md
├── tests/
│   ├── bats/                   # bash test files (dry-run paths)
│   └── fixtures/               # sample sf JSON payloads
└── .github/workflows/
    └── salesforce-toolkit-ci.yml  # shellcheck + bats
```

Root [`../.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json)
adds one entry `{"name": "salesforce-toolkit", "source": "./salesforce-toolkit"}`.
[`scripts/check-marketplace-description-sync.py`](../scripts/check-marketplace-description-sync.py)
enforces verbatim sync between `plugin.json` and `marketplace.json`
description fields.

### Module chain (install → launch → execute)

```
plugin.json
    │  (CC plugin registry reads on install)
    ▼
.mcp.json
    │  (CC MCP loader; type=stdio; command=bash; args=[${CLAUDE_PLUGIN_ROOT}/bin/sf-mcp-launcher.sh])
    ▼
bin/sf-mcp-launcher.sh
    │  resolve at runtime:
    │  1. salesforce-mcp on PATH  → exec it
    │  2. npx on PATH             → exec npx -y @salesforce/mcp
    │  3. neither                 → stderr pointer to /salesforce-toolkit:sf-setup; exit 127
    ▼
salesforce-mcp (brew bottle, v0.30.9+, Apache-2.0)   OR   npx -y @salesforce/mcp (cold-start fallback)
    │  stdio MCP transport; 60+ tools; default toolsets data,metadata
    ▼
sf CLI (brew formula, v2.x, Apache-2.0)
    │  OAuth2 token in macOS Keychain (file backend fallback ~/.sfdx/)
    ▼
Salesforce instance API (https://<sub>.my.salesforce.com)
```

**Why shim launcher (Q1 Path D)** — Plugin install loads `.mcp.json`
*before* the user can run `/salesforce-toolkit:sf-setup`; alternatives
A (brew binary hardcoded) and C (auto-setup dynamically writes
`.mcp.json`) both create race conditions where MCP fails to load on
first install. Path D ships a static `.mcp.json` whose `command` is
always available (`bash`) and resolves the real entrypoint at launch
time — brew bottle if installed (<1s cold start), else npx fallback
(10–30s but works), else explicit error pointing at `/sf-setup`.

### MCP default toolsets

`.mcp.json` invokes `sf-mcp-launcher.sh` with `--toolsets data,metadata`
to scope the 60+ available MCP tools down to the read-only surface
PRODUCT-SPEC §Scope allows. Phase 2+ `sf-deploy` skill (per
PRODUCT-SPEC §Scope Phase 2+ table) will expand to
`metadata,data,users`.

The launcher also passes `--orgs DEFAULT_TARGET_ORG` — the
`salesforce-mcp` arg that binds the MCP server to whichever org the
local `sf` CLI has set as `target-org` (via `sf config set
target-org=<alias>`). Multi-org users can switch the bound org at
runtime by changing their default alias and reconnecting MCP, without
editing `.mcp.json` or restarting Claude Code from scratch.

---

## Data Flow

### Read path (PRODUCT-SPEC §JTBD primary)

```
Claude Code (user session: "list 10 open opportunities")
    │
    │  ① skill prompt: skills/sf-query/SKILL.md routes to MCP tool
    ▼
MCP stdio transport
    │  ② Claude → salesforce-mcp via stdio (JSON-RPC over stdin/stdout)
    ▼
salesforce-mcp (brew bottle / npx)
    │  ③ MCP tool maps to sf CLI subcommand (e.g. `sf data query --query "SELECT ..."`)
    ▼
sf CLI
    │  ④ sf reads OAuth2 token from macOS Keychain (file fallback ~/.sfdx/)
    │     ↳ token-cache key derived from alias (e.g. "ichef" or "prod")
    ▼
Salesforce instance API
    │  ⑤ HTTPS GET https://<sub>.my.salesforce.com/services/data/vXX.X/query?q=...
    │     Authorization: Bearer <access_token>
    ▼
Response JSON
    │  ⑥ sf CLI parses + emits JSON to stdout
    ▼
salesforce-mcp
    │  ⑦ MCP packages stdout into MCP tool-result message
    ▼
Claude Code (renders result inline; offers follow-up analysis)
```

**Read-only by default** (PRODUCT-SPEC §Success criteria KR3) — Step ③
the MCP server is launched with `--toolsets data,metadata`, which
restricts the tool surface to read affordances + metadata describe;
write tools (data record insert/update/delete, metadata deploy) are
absent unless user explicitly requests Phase 2+ `sf-deploy` skill (not
present in v0.1.0).

### Setup path (PRODUCT-SPEC §Success criteria KR1)

**Two paths converge on the same end state.** Default is Claude-orchestrated (in-conversation); terminal-power-user path is opt-in.

#### Path A — Claude-orchestrated (default)

```
user types /salesforce-toolkit:sf-setup
    │
    │  commands/sf-setup.md handed to Claude as 9-step procedural walkthrough
    ▼
Claude executes step-by-step (Step 0-8 per commands/sf-setup.md):
    │  Step 0  Validate $ARGUMENTS: reject --no-alias + --alias=X mutex;
    │          reject unknown flags
    │
    │  Step 1  Bash: bash scripts/sf/credential-check.sh → probe state JSON
    │          halt if .brew == "missing" (show user brew curl one-liner;
    │          user runs in Terminal.app + restarts Claude Code + re-invoke)
    │
    │  Step 2  Resolve target_alias (cheap pre-pass, no AskUserQuestion):
    │          --no-alias → ""; --alias=X → X; --instance-url=Y → infer_alias(Y, "");
    │          neither flag → null
    │
    │  Step 3  Install missing binaries (idempotent):
    │          brew install sf (if sf_cli == "missing")
    │          brew install salesforce-mcp (if missing AND NOT --skip-mcp-brew)
    │          halt on non-zero exit (surface stderr)
    │
    │  Step 4  Early-exit check (skip OAuth if already authenticated):
    │          probe `sf org display --json` → .result.connectedStatus
    │          early-exit if Connected AND target_alias matches current default
    │          (or target null with no args, or target "" with --no-alias)
    │          → emit summary + /reload-plugins reminder + END
    │
    │  Step 5  Resolve instance URL + alias (interactive):
    │          AskUserQuestion: instance URL (Production / Sandbox / My Domain
    │          / Other) if not in $ARGUMENTS AND NOT --no-prompt
    │          run alias-infer.sh against resolved URL if target_alias was null
    │          AskUserQuestion: confirm alias (accept / custom / omit)
    │          if NOT --no-prompt AND NOT --alias= explicit
    │
    │  Step 6  OAuth in background + poll:
    │          Bash run_in_background:
    │            sf org login web [--alias=X] --set-default --instance-url=Y
    │            (--set-default ALWAYS passed; --alias= conditional on non-empty)
    │          tells user: "browser will open, complete OAuth"
    │          poll every 5s: sf org display [--target-org=X] --json
    │            until .result.connectedStatus == "Connected" (max 5 min, then
    │            asks user to keep waiting or abort; abort kills bg via
    │            pkill -INT -f "sf org login web --alias=X")
    │
    │  Step 7  Verify + emit summary:
    │          sf org display [--target-org=X] --json → extract instanceUrl,
    │          username, accessTokenExpirationDate; report to user
    ▼
Claude reports summary to user + instructs: /reload-plugins to activate MCP
    │  Step 8  user runs /reload-plugins in same conversation → MCP server reloads
    ▼
End state: sf authenticated + salesforce-mcp installed + default org bound
```

TTY: not required at any step (`AskUserQuestion` replaces `read </dev/tty`; `run_in_background` replaces blocking on browser OAuth callback). Bash tool subprocesses don't need TTY because Claude handles every interactive moment.

**Install-before-early-exit ordering** (important): Step 3 (install) runs BEFORE Step 4 (early-exit check) deliberately. If the user has `sf` authed to an existing org but is missing `salesforce-mcp` (e.g. re-running `/sf-setup` to add the MCP binary), Step 3 installs `salesforce-mcp` and Step 4 detects "still authed, alias matches" → clean early-exit without redundant OAuth. Earlier doc drafts ordered early-exit-before-install, which made this scenario re-OAuth unnecessarily.

#### Path B — Terminal power-user (opt-in)

```
user opens Terminal.app
    │
    │  ① user finds plugin path (e.g.
    │      ~/.claude/plugins/cache/monkey-skills/<ver>/salesforce-toolkit/)
    ▼
user runs: bash scripts/sf/auto-setup.sh
    │  ② 6 idempotent steps (see §Setup Flow); stderr progress + stdout JSON
    │     interactive: brew install confirm + Enter-to-accept alias prompt
    │     opens browser: sf org login web (TTY-bound; runs in user terminal)
    ▼
auto-setup.sh emits final JSON contract
    │  ③ {status, sf_version, mcp_version, org_alias, instance_url,
    │      oauth_expiry, elapsed_sec, dry_run}
    ▼
user returns to Claude Code → /reload-plugins
```

TTY: required. Used for brew install y/N prompt (Step 2) + Enter-to-accept alias prompt (Step 5). Cannot run from Claude Code Bash tool (which lacks a controlling terminal); must run from a real terminal app.

#### Why both paths

Path A is friction-minimized for the common case (kouko's iChef instance, single-org workflow). Path B is preserved for: (a) advanced debugging where you want full bash control + see brew prompts directly, (b) automated provisioning scripts that bash-pipe into auto-setup.sh, (c) environments where Claude Code is unavailable. Both paths share the same atomic helpers (`tty-guard.sh` / `alias-infer.sh` / `credential-check.sh` / `refresh-auth.sh`) — only the orchestration layer differs.

### Re-auth path (PRODUCT-SPEC §Success criteria KR4)

```
OAuth token expired (typically 90 days inactivity for SF refresh tokens)
    │
    │  ① user notices Claude can no longer answer SF queries
    ▼
user runs `bash scripts/sf/refresh-auth.sh` in terminal
    │  ② resolve alias: explicit --alias=X | sf config get target-org
    │     → sf org login web --alias=X --set-default (opens browser)
    │     → sf org display --target-org=X --json (verify)
    ▼
emits {status, alias, instance_url, expiry} JSON to stdout
    │  ③ Claude session reconnects MCP transparently (no plugin reload)
```

---

## Interfaces

### `scripts/common/tty-guard.sh`

- **Role**: provide `require_tty` helper sourced by `auto-setup.sh` and
  `refresh-auth.sh`. Refuses to proceed when there is no controlling
  TTY (e.g. CI runner, Bash tool background invocation) since the
  browser-based OAuth flow requires user interaction.
- **Public API**: `require_tty` function. Exits 10 (auth/interaction
  error) on no-TTY with structured stderr message. Side-effect-free
  otherwise.
- **Sourcing**: `source "${SCRIPT_DIR}/../common/tty-guard.sh"`.

### `scripts/sf/alias-infer.sh`

- **Role**: provide `infer_alias` pure-function for 3-layer alias
  derivation (Decision Q3).
- **Public API**: `infer_alias INSTANCE_URL USER_ALIAS` — both args
  required (use `""` for absent). Echoes alias (may be empty) to
  stdout; always returns 0; no side effects.
- **Layering**:
  - Layer 1 — explicit override: `USER_ALIAS` non-empty wins
    unconditionally.
  - Layer 2 — subdomain parse: `INSTANCE_URL` matches
    `^https?://<sub>.(my.salesforce.com | lightning.force.com |
    sandbox.my.salesforce.com)` → lowercase `<sub>`, collapse `--` →
    `-`, strip leading/trailing `-`.
  - Layer 3 — endpoint fallback: `login.salesforce.com` or empty URL
    → `prod` (Decision Q6); `test.salesforce.com` → `sandbox`
    (Decision Q6); anything else → empty (caller lets `sf` derive from
    username).
- **Bash 3.2 compatibility**: no `${var,,}` (uses `tr`); no associative
  arrays; regex via `BASH_REMATCH`.

### `scripts/sf/credential-check.sh`

- **Role**: read-only diagnostic — probe brew / sf / salesforce-mcp /
  node / default org / org status. Pure read; never installs or
  modifies state.
- **Input**: stdin none; args none (any `--help` ignored in v0.1.0).
- **Output (stdout)**: single JSON object —
  ```json
  {
    "brew":               "installed" | "missing",
    "sf_cli":             "installed" | "missing",
    "sf_version":         "<version-string>" | null,
    "salesforce_mcp":     "installed" | "missing",
    "mcp_version":        "<version-string>" | null,
    "node":               "installed" | "missing",
    "default_org":        "<alias>"   | null,
    "default_org_status": "active" | "expired" | null
  }
  ```
- **Stderr**: silent on success path (orchestrator owns user-facing
  messaging).
- **Exit code**: ALWAYS 0. Errors out-of-band would force the caller
  (`auto-setup.sh`) to treat missing tools as script failures rather
  than states to remediate.
- **Fallback**: if `jq` is missing, emits a static all-`missing` JSON
  via `printf` and still exits 0.

### `scripts/sf/auto-setup.sh`

- **Role**: 6-step idempotent installer (orchestrator).
- **Args**:
  - `--dry-run` — print plan only; no brew/sf/curl invocations.
  - `--alias=<name>` — explicit alias (wins over inference, Layer 1).
  - `--no-alias` — force omit alias (sf uses username default).
  - `--no-prompt` — skip Enter-to-accept prompt; use inferred (or
    empty) alias directly.
  - `--force-reauth` — re-run `sf org login web` even when active
    default org already exists.
  - `--instance-url=<url>` — pass to `sf org login web --instance-url=`
    + feed Layer-2 subdomain parser.
  - `--skip-mcp-brew` — skip `brew install salesforce-mcp`; launcher
    shim falls back to npx at runtime.
  - `-h | --help` — print usage.
- **Stdin**: none. Interactive: `/dev/tty` reads for brew-install
  confirm + Enter-to-accept alias prompt.
- **Output (stdout)**: single JSON object —
  ```json
  {
    "status":       "ok",
    "sf_version":   "<string>" | null,
    "mcp_version":  "<string>" | null,
    "org_alias":    "<string>" | null,
    "instance_url": "<string>" | null,
    "oauth_expiry": "<string>" | null,
    "elapsed_sec":  <number>,
    "dry_run":      true | false
  }
  ```
- **Stderr**: `[auto-setup] step N/6: ...` progress + dry-run plan
  lines + `[auto-setup] already done: <step>` idempotency markers +
  structured error JSON on failure.
- **Exit codes**:
  - `0` success
  - `1` generic error (usage / unknown flag / unknown state)
  - `10` auth / interaction error (TTY missing, sf login failed)
  - `11` unsupported OS (non-Darwin)
  - `12` install error (brew / sf / mcp install failed)
- **Idempotency**: each step probes current state with `command -v` or
  `sf org display --json` and emits `already done: <step>` stderr when
  skipped (PRODUCT-SPEC §Success criteria KR2).

### `scripts/sf/refresh-auth.sh`

- **Role**: standalone re-auth helper. Direct `sf org login web
  --alias=<X> --set-default` invocation without 6-step orchestrator
  overhead.
- **Args**:
  - `--alias=<name>` — explicit alias override. Falls back to
    `sf config get target-org` when omitted.
  - `--dry-run` — print plan only; do NOT invoke `sf`.
  - `-h | --help` — print usage.
- **Stdin**: none (interactive — controlling TTY required unless
  `--dry-run`).
- **Output (stdout)**: single JSON object on real re-auth path —
  ```json
  {
    "status":       "ok",
    "alias":        "<string>",
    "instance_url": "<string>" | null,
    "expiry":       "<string>" | null
  }
  ```
- **Stderr**: `[refresh-auth] ...` progress + dry-run plan + structured
  error JSON on failure.
- **Exit codes**:
  - `0` success (re-auth complete)
  - `1` generic error (unknown flag, `--alias` resolution failed)
  - `10` auth / interaction error (no TTY, sf login failed)
  - `12` install error (sf CLI missing — user should run
    `auto-setup.sh` first)

### `bin/sf-mcp-launcher.sh`

- **Role**: brew → npx dynamic dispatcher (Decision Q1 Path D).
  Resolves the Salesforce MCP entrypoint at launch time so the static
  `.mcp.json` is always loadable, regardless of whether the user has
  run `/salesforce-toolkit:sf-setup` yet.
- **Args**: any args forwarded verbatim to the chosen entrypoint via
  `"$@"` (typically `--toolsets data,metadata` from `.mcp.json`, plus
  user-supplied flags).
- **Stdin / Stdout / Stderr**: pass-through from the exec'd binary
  (MCP stdio transport — JSON-RPC frames on stdin/stdout).
- **Resolution order**:
  1. `salesforce-mcp` on PATH (brew bottle) → `exec salesforce-mcp "$@"`
  2. `npx` on PATH → `exec npx -y @salesforce/mcp "$@"` (cold-start
     fallback)
  3. neither → stderr pointer to `/salesforce-toolkit:sf-setup`;
     exit 127
- **Exit code**: pass-through from exec'd binary; 127 only on
  resolution failure.

---

## Setup Flow

The 6-step diagram below mirrors `scripts/sf/auto-setup.sh` `main()`
exactly (Decision Q1 §setup steps; PRODUCT-SPEC §Success criteria KR1
+ KR2). Each step is **idempotent** — re-running prints
`[auto-setup] already done: <step name>` on stderr and skips the
underlying action.

```
                       ┌─────────────────────────────────────┐
                       │  /salesforce-toolkit:sf-setup       │
                       │  (commands/sf-setup.md)             │
                       └────────────────┬────────────────────┘
                                        │
                                        ▼
                       ┌─────────────────────────────────────┐
                       │  bash scripts/sf/auto-setup.sh      │
                       │  (orchestrator)                     │
                       └────────────────┬────────────────────┘
                                        │
                  ┌─────────────────────┴─────────────────────┐
                  ▼                                            ▼
       [DRY_RUN=0 — real path]                    [DRY_RUN=1 — bats path]
                  │                                            │
                  │   Step 1: ensure_os_and_tty                │
                  │   ─ require uname -s == Darwin             │
                  │     (exit 11 on non-Darwin)                │
                  │   ─ require_tty (exit 10 on no TTY)        │
                  │                                            │
                  │   Step 2: ensure_brew                      │
                  │   ─ command -v brew  → skip               │
                  │   ─ else prompt y/N → curl install.sh      │
                  │     (exit 12 on declined / installer fail) │
                  │                                            │
                  │   Step 3: ensure_sf                        │
                  │   ─ command -v sf    → skip; capture       │
                  │     SF_VERSION via `sf --version`          │
                  │   ─ else brew install sf                   │
                  │                                            │
                  │   Step 4: ensure_mcp                       │
                  │   ─ command -v salesforce-mcp → skip       │
                  │   ─ --skip-mcp-brew → skip (shim → npx)    │
                  │   ─ else brew install salesforce-mcp       │
                  │                                            │
                  │   Step 5: ensure_org_login                 │
                  │   ─ resolve_alias (3-layer infer +         │
                  │     Enter-to-accept via /dev/tty)          │
                  │   ─ sf org display --json → "already       │
                  │     done" unless --force-reauth            │
                  │   ─ else sf org login web                  │
                  │     [--alias=X --set-default]              │
                  │     [--instance-url=URL]                   │
                  │     (exit 10 on login failure)             │
                  │                                            │
                  │   Step 6: verify_org                       │
                  │   ─ sf org display --target-org=X --json   │
                  │   ─ extract .result.instanceUrl +          │
                  │     .result.accessTokenExpirationDate      │
                  │                                            │
                  ▼                                            ▼
       ┌──────────────────────────────────┐    ┌────────────────────────────┐
       │  stdout: emit_result JSON        │    │  stdout: dry_run=true JSON │
       │  {status, sf_version,            │    │  stderr: plan lines only   │
       │   mcp_version, org_alias,        │    │  (no brew / sf / curl)     │
       │   instance_url, oauth_expiry,    │    └────────────────────────────┘
       │   elapsed_sec, dry_run:false}    │
       └──────────────────────────────────┘
```

**Step semantics**:

| Step | Action | Idempotency probe | Exit code on failure |
|---|---|---|---|
| 1 | OS + TTY guard | `uname -s == Darwin` + `tty -s` | 11 (OS), 10 (TTY) |
| 2 | Homebrew install | `command -v brew` | 12 |
| 3 | `sf` CLI install | `command -v sf` | 12 |
| 4 | `salesforce-mcp` install | `command -v salesforce-mcp` OR `--skip-mcp-brew` | 12 |
| 5 | `sf org login web` | `sf org display --json` (returns 0 if active default org) | 10 |
| 6 | verify org + capture instance_url + oauth_expiry | always runs | 10 (empty payload), 12 (sf missing) |

**Interactive points**:
- Step 2 prompts `y/N` via `/dev/tty` before pulling the Homebrew
  installer over `curl`
- Step 5 prompts `ENTER` via `/dev/tty` to accept the inferred alias
  (unless `--no-prompt` or `--alias=<name>` already set)
- Step 5 opens browser for `sf org login web` (TTY-bound — runs in
  user's terminal, never via Bash tool background per
  `feedback_plugin_metadata_conventions`)

**Performance target** (PRODUCT-SPEC §Success criteria KR1): full path
end-to-end < 5 min on a clean macOS machine with Homebrew already
installed; the dominant cost is `brew install sf` (~30s) + browser
OAuth round-trip (~60s user interaction time).
