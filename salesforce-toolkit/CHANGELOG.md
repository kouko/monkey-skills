# Changelog

All notable changes to the `salesforce-toolkit` plugin will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

---

## [0.1.1] - 2026-05-22 — **Onboarding-friction reduction (no functional change)**

UX-only release addressing v0.1.0 dogfood findings: shorten the first-time
install path's wall-clock time and visible silence. No behavioral surface
change — `.mcp.json` toolset still `data` only, MCP tools unchanged, auth
flow unchanged, all existing `--flag` semantics preserved.

### Changed

- **`scripts/sf/auto-setup.sh`** — Step 3 (`ensure_sf`) now detects the
  common case of "both `sf` CLI and `sf-mcp-server` missing" and runs a
  **single combined `brew install sf salesforce-mcp`** instead of two
  separate installs. Saves ~3-5 sec brew startup + enables parallel
  formula download (~30-60 sec network save on clean systems).
  ensure_mcp (Step 4) skips its own install when `COMBINED_INSTALL_DONE=1`.
  Existing 6-step structure preserved (bats `(a)` test still asserts
  `step N/6` labels). Partial-state re-runs (only one binary missing)
  unchanged.
- **`commands/sf-setup.md`** Step 3 — added explicit BEFORE/AFTER
  progress emit (`🔧 Installing missing binaries...` / `✅ Installed:
  sf vX.Y + salesforce-mcp vA.B`) so the user sees concrete start/done
  signals around the 2-3 min brew wait, instead of silence.
- **`commands/sf-setup.md`** Step 6 — restructured the 5-min OAuth
  poll from "60 polls × 5 sec, silent" to "10 windows × 30 sec, emit
  progress between each window". User now gets a `⏳ Still waiting...`
  status line every 30 sec instead of waiting up to 5 min in silence.
  Adds extra hints at 60 sec ("sign in + click Allow if not yet") and
  4:00 ("1 min before continue/abort prompt").
- **`commands/sf-setup.md`** Step 8 — visual emphasis on the
  `/reload-plugins` reminder (boxed callout) + paste-ready example
  query templates (`列出最近 5 筆 Account` / `本季結案的 Opportunity`
  / `今年的 Lead 依 Source 分群`) so the most-commonly-forgotten step
  in v0.1.0 dogfood becomes hard to miss + immediately verifiable.
- **`README.md` / `README.ja.md` / `README.zh-TW.md`** — promoted the
  one-shot `--instance-url=<url> --no-prompt` invocation form as the
  **primary recommendation** in §Quick Start. Interactive form kept as
  alternative for users who don't know their org URL. Tri-lang
  parallel update.

### Migration

None — drop-in replacement for v0.1.0. Existing users:
`/plugin update salesforce-toolkit@monkey-skills` + `/reload-plugins`.

### Friction-cost delta (vs v0.1.0)

| Step | v0.1.0 | v0.1.1 | Δ |
|------|--------|--------|---|
| Step 3 brew install (both missing) | 2-6 min sequential | 1-3 min combined | **-1 to -3 min** |
| Step 6 OAuth wait visibility | 5 min silent | progress emit every 30s | **eliminated silence anxiety** |
| Step 8 `/reload-plugins` recall | prose line | boxed callout + try-this queries | **lower forget rate** |
| One-shot setup discoverability | buried as power-user note | primary Quick Start example | **lower decision cost for users who know their URL** |

---

## [0.1.0] - 2026-05-20 — **Initial release: Salesforce DX MCP plugin with brew-first auto-setup**

First public cut. Wraps the upstream Salesforce DX MCP server
([`salesforcecli/mcp`](https://github.com/salesforcecli/mcp), Apache-2.0)
as a Claude Code plugin with brew-first installer, read-only-by-default
toolset selection, and a one-shot setup walkthrough. macOS only. Claude
Code CLI only — Cowork sandbox not supported (TTY-bound OAuth flow).

Shipped via 5-part SDD (subagent-driven-development) cycle:

- **Part 1** — Plugin scaffold + cross-cutting registration (root
  marketplace + root README plugin-list) + `.mcp.json` static config +
  `bin/sf-mcp-launcher.sh` brew→npx shim + `scripts/common/tty-guard.sh`.
- **Part 2** — `scripts/sf/` setup automation: `alias-infer.sh` /
  `credential-check.sh` / `auto-setup.sh` (6-step idempotent installer,
  TTY-bound terminal-mode) / `refresh-auth.sh` + Claude-orchestrated
  `/salesforce-toolkit:sf-setup` slash command (in-conversation default;
  no terminal switching for sf + salesforce-mcp install + OAuth).
- **Part 3** — `sf-query` SKILL.md + `PRODUCT-SPEC.md` + `TECH-SPEC.md`
  + CI workflow (shellcheck + bats + marketplace-sync).
- **Part 4a** — English authoritative READMEs (plugin-level + sf-query).
- **Part 4b** — Japanese + Traditional Chinese translation pairs (per
  natural unit: same en source → ja + zh-TW).
- **Pre-ship verification (2026-05-20)** — Web + dogfood verification
  of upstream `salesforcecli/mcp` v0.30.9 tool surface forced a scope
  cut before v0.1.0 ship: the `metadata` toolset includes
  `deploy_metadata` (destructive write) and the upstream MCP server
  exposes no Salesforce Report / Dashboard tools, so `sf-report` was
  dropped and the `.mcp.json` toolset narrowed from `data,metadata` to
  `data`. See **Notes — upstream-tool caveats** below.

### Added

- `.claude-plugin/plugin.json` — plugin metadata (name / version /
  description / license MIT / keywords).
- `.mcp.json` — static MCP config (stdio transport via
  `bin/sf-mcp-launcher.sh` shim; truly read-only `data` toolset only
  — single tool `run_soql_query`; `--orgs DEFAULT_TARGET_ORG` arg binds
  MCP server to whichever org `sf config set target-org=<alias>` has
  marked default — switch orgs by changing the sf alias, no `.mcp.json`
  edit needed).
- `bin/sf-mcp-launcher.sh` — runtime brew→npx fallback launcher
  (`sf-mcp-server` binary preferred — the binary that brew formula
  `salesforce-mcp` and npm package `@salesforce/mcp` both install;
  `npx -y @salesforce/mcp` fallback; explicit setup-command pointer
  if neither available).
- `scripts/sf/` setup-automation scripts (6-step idempotent installer
  driving brew install of `sf` CLI + `salesforce-mcp`, OAuth via
  `sf org login web` with `SF_DISABLE_TELEMETRY=true` exported to
  skip the non-TTY-hanging first-run consent prompt, alias inference
  from instance URL).
- `commands/sf-setup.md` — `/salesforce-toolkit:sf-setup` slash command.
  Claude-orchestrated walkthrough that stays in the conversation: probes
  state, runs missing brew installs non-interactively, asks for instance
  URL + alias via `AskUserQuestion`, starts `sf org login web` in
  background, polls until OAuth completes, then prompts the user to
  `/reload-plugins`. Homebrew is the only one-time external prerequisite
  (its installer needs `sudo` so it stays outside Claude Code).
- One read-only skill:
  - `sf-query` — natural-language → SOQL query patterns (via upstream
    `run_soql_query` MCP tool).
- `CHANGELOG.md` + `LICENSE-MIT.txt` (plugin-level, per gws-toolkit
  per-plugin license precedent).
- Tri-language READMEs (en / ja / zh-TW) at plugin-level + per-skill,
  per PR #150 convention.
- CI workflow (`.github/workflows/salesforce-toolkit-ci.yml`) —
  shellcheck + bats + marketplace-description-sync.

### Scope (v0.1.0)

- **Truly read-only** — MCP toolset scoped to `data` only (single
  upstream tool: `run_soql_query`). The broader `metadata` toolset is
  intentionally NOT enabled because it includes `deploy_metadata`
  (destructive write to org); write toolsets (`metadata` / `users` /
  `code-analyzer` / Apex deploy) deferred to v0.2+.
- **SOQL only, no SOSL** — upstream MCP `data` toolset exposes
  `run_soql_query` but no SOSL equivalent; SOSL deferred to v0.2+ if /
  when upstream adds it.
- **No Salesforce Report / Dashboard skill** — upstream MCP exposes no
  Report or Dashboard tools (verified against `salesforcecli/mcp`
  v0.30.9); previously-drafted `sf-report` skill was dropped before
  v0.1.0 ship. Deferred to Phase 2+ if upstream lands a Report tool.
- **macOS only** (brew dependency); Linux / WSL deferred to Phase 2+.
- **Claude Code CLI only** — Cowork sandbox not supported
  (`sf org login web` is TTY-bound; matches `gws-toolkit` /
  `collab-toolkit` Cowork-incompatible posture).
- **Alias inference** — 3-layer from `--alias=` flag / instance-URL
  subdomain / well-known endpoint fallback (`prod` / `sandbox`); user
  ENTER to accept inferred, override or `-` to omit.

### Notes — upstream-tool caveats discovered during 2026-05-20 dogfood

- **Toolset choice — `data` only, not `data,metadata`** — Pre-ship
  verification against the installed `sf-mcp-server` (live JSON-RPC
  `tools/list` introspection + `--help` toolset enum) confirmed: the
  `data` toolset exposes a single tool, `run_soql_query`; the
  `metadata` toolset includes `deploy_metadata` (destructive write to
  the org) plus `retrieve_metadata`. Because we want v0.1.0 to be
  truly read-only with no chance of an accidental tool call mutating
  the org, `.mcp.json` ships with only the `data` toolset enabled. The
  `metadata` toolset is deferred to v0.2+ behind an explicit
  destructive-op safety wrapper.
- **No upstream Report / Dashboard tools** — Same pre-ship
  verification confirmed `salesforcecli/mcp` v0.30.9 exposes no
  Salesforce Report, Dashboard, or Analytics MCP tools at all. The
  previously-drafted `sf-report` skill was therefore dropped before
  v0.1.0 ship. If upstream lands these tools later, the skill returns
  in Phase 2+.
- **No SOSL tool in upstream MCP** — The `data` toolset's `run_soql_query`
  is SOQL-only; there is no `run_sosl_query` (or equivalent) in
  upstream `salesforcecli/mcp` today. Earlier drafts of the `sf-query`
  skill mentioned SOSL routing; those were dropped before v0.1.0 ship.
  Will be added if upstream adds the tool.
- **Binary name vs brew formula name** — `brew install salesforce-mcp`
  ships a binary called `sf-mcp-server`, not `salesforce-mcp`. The
  npm package `@salesforce/mcp` ships the same `sf-mcp-server` binary.
  Setup scripts + launcher shim probe for `sf-mcp-server` on PATH;
  docs that previously referenced a `salesforce-mcp` binary have been
  corrected. The brew formula name is unchanged — only the installed
  binary name differs.
- **`sf` first-run telemetry prompt** — `sf` shows an interactive y/N
  telemetry consent prompt on first invocation, which hangs in non-TTY
  contexts (Claude Code's Bash tool). All setup scripts export
  `SF_DISABLE_TELEMETRY=true` before any `sf` invocation to skip it;
  no user action needed.
- **`sf org login web` URL suppression in non-TTY** — `sf org login web`
  does not print the OAuth URL on stdout/stderr when running without a
  controlling TTY (Claude orchestrated Path A). The browser still opens
  automatically. If the browser fails to open, the user must fall back
  to Path B (Terminal power-user `auto-setup.sh`), which prints the URL
  natively because it runs in a real TTY.

### Open follow-ups (Phase 2+)

- **`sf-report` skill** — once upstream MCP exposes Report / Dashboard
  tools (none in v0.30.9). Until then, Report / Dashboard analysis is
  out of scope for this plugin.
- **SOSL support in `sf-query`** — once upstream MCP exposes a SOSL
  query tool. SOQL-only for now.
- **Schema-aware describe via `metadata` toolset** — currently
  unavailable because the `metadata` toolset bundles destructive
  `deploy_metadata`. Either upstream needs to split `metadata` into
  read-only + write subsets, or this plugin needs a safety wrapper.
- **Write toolsets opt-in** (Apex deploy / metadata push / user CRUD) —
  requires destructive-op safety wrapper analogous to
  `gws-toolkit/scripts/gws/safe-delete.sh`.
- **Salesforce Hosted MCP HTTP path** — Enterprise Edition+ license;
  runs server-side on user's org instance.
- **Linux / WSL install path** — Phase 2 trigger upon first external
  user request.
- **`sf-deploy` skill** (write operations) — once safety wrapper lands.
