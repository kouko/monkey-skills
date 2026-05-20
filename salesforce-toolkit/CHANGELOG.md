# Changelog

All notable changes to the `salesforce-toolkit` plugin will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

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
- **Part 3** — `sf-query` SKILL.md + `sf-report` SKILL.md +
  `PRODUCT-SPEC.md` + `TECH-SPEC.md` + CI workflow (shellcheck + bats +
  marketplace-sync).
- **Part 4a** — English authoritative READMEs (plugin-level +
  sf-query + sf-report).
- **Part 4b** — Japanese + Traditional Chinese translation pairs (per
  natural unit: same en source → ja + zh-TW).

### Added

- `.claude-plugin/plugin.json` — plugin metadata (name / version /
  description / license MIT / keywords).
- `.mcp.json` — static MCP config (stdio transport via
  `bin/sf-mcp-launcher.sh` shim; read-only `data,metadata` toolset;
  `--orgs DEFAULT_TARGET_ORG` arg binds MCP server to whichever org
  `sf config set target-org=<alias>` has marked default — switch orgs
  by changing the sf alias, no `.mcp.json` edit needed).
- `bin/sf-mcp-launcher.sh` — runtime brew→npx fallback launcher
  (`salesforce-mcp` brew binary preferred; `npx -y @salesforce/mcp`
  fallback; explicit setup-command pointer if neither available).
- `scripts/sf/` setup-automation scripts (6-step idempotent installer
  driving brew install of `sf` CLI + `salesforce-mcp`, OAuth via
  `sf org login web`, alias inference from instance URL).
- `commands/sf-setup.md` — `/salesforce-toolkit:sf-setup` slash command.
  Claude-orchestrated walkthrough that stays in the conversation: probes
  state, runs missing brew installs non-interactively, asks for instance
  URL + alias via `AskUserQuestion`, starts `sf org login web` in
  background, polls until OAuth completes, then prompts the user to
  `/reload-plugins`. Homebrew is the only one-time external prerequisite
  (its installer needs `sudo` so it stays outside Claude Code).
- Two read-only skills:
  - `sf-query` — natural-language → SOQL/SOSL query patterns.
  - `sf-report` — Salesforce Report / Dashboard pull + analysis.
- `CHANGELOG.md` + `LICENSE-MIT.txt` (plugin-level, per gws-toolkit
  per-plugin license precedent).
- Tri-language READMEs (en / ja / zh-TW) at plugin-level + per-skill,
  per PR #150 convention.
- CI workflow (`.github/workflows/salesforce-toolkit-ci.yml`) —
  shellcheck + bats + marketplace-description-sync.

### Scope (v0.1.0)

- **Read-only by default** — MCP toolset scoped to `data,metadata`
  (SOQL/SOSL queries, Report retrieval, metadata describe). Write
  toolsets (`users` / `code-analyzer` / Apex deploy) deferred to v0.2+.
- **macOS only** (brew dependency); Linux / WSL deferred to Phase 2+.
- **Claude Code CLI only** — Cowork sandbox not supported
  (`sf org login web` is TTY-bound; matches `gws-toolkit` /
  `collab-toolkit` Cowork-incompatible posture).
- **Alias inference** — 3-layer from `--alias=` flag / instance-URL
  subdomain / well-known endpoint fallback (`prod` / `sandbox`); user
  ENTER to accept inferred, override or `-` to omit.

### Open follow-ups (Phase 2+)

- Write toolsets opt-in (Apex deploy / metadata push / user CRUD) —
  requires destructive-op safety wrapper analogous to
  `gws-toolkit/scripts/gws/safe-delete.sh`.
- Salesforce Hosted MCP HTTP path — Enterprise Edition+ license; runs
  server-side on user's org instance.
- Linux / WSL install path — Phase 2 trigger upon first external user
  request.
- `sf-deploy` skill (write operations) — once safety wrapper lands.
