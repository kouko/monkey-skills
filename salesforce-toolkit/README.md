# salesforce-toolkit

> Read-only Salesforce toolkit — natural-language SOQL / SOSL queries and Report / Dashboard analysis over your org via the official Salesforce DX MCP server (`salesforcecli/mcp`, Apache-2.0).

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> ⚠️ **Cowork compatibility — Claude Code CLI / Code tab only.** First-time setup runs `sf org login web` which is a TTY-bound browser OAuth flow; the Claude Desktop Cowork sandbox does not surface that path (same constraint as [`gws-toolkit`](../gws-toolkit/) and [`collab-toolkit`](../collab-toolkit/)). If you are on Cowork, switch to Claude Code CLI or the Claude Desktop Code tab.

## What it does

Connects Claude Code to your Salesforce org so you can ask in prose:

- **Data queries** — natural-language SOQL / SOSL: list objects, fetch records, filter, aggregate, traverse parent-child relationships
- **Reports & Dashboards** — list folders, fetch metadata, execute Reports, pull row data, snapshot Dashboard widgets, run trend / Top-N / funnel analysis
- **Read-only charter** — `data,metadata` MCP toolsets only; no Apex deploy, no metadata push, no user CRUD until v0.2+ ships a destructive-op safety wrapper

v0.1.0 wraps the upstream Salesforce DX MCP server ([`salesforcecli/mcp`](https://github.com/salesforcecli/mcp), Apache-2.0, GA 2026) — vendor-maintained schema-aware tool surface, no third-party query DSL drift.

## Quick start

```bash
# Install plugin via Claude Code marketplace
/plugin install salesforce-toolkit

# One-time bootstrap (~3-5 min — most time is the browser OAuth flow)
/salesforce-toolkit:sf-setup
```

`sf-setup` is a 6-step idempotent installer: macOS / TTY guard → ensure Homebrew → `brew install sf` → `brew install salesforce-mcp` → `sf org login web` with 3-layer alias inference → verify `sf org display`. Already set up? Re-runs take ~5 seconds and skip each step that's done.

After that, ask Claude things like:

- "List the 10 most-recent Opportunities over $50K"
- "Show me the pipeline by stage for the EMEA team"
- "Pull the Weekly Revenue Dashboard and summarise the top movers"

## Skills

| Skill | Purpose |
|---|---|
| [`sf-query`](skills/sf-query/) | Natural-language SOQL / SOSL — list objects, fetch records, filter, aggregate, traverse parent-child relationships |
| [`sf-report`](skills/sf-report/) | Salesforce Reports + Dashboards — list folders, fetch metadata, execute Reports, pull row data, snapshot widgets, trend / Top-N / funnel analysis |

Both skills are read-only. Write toolsets (`users` / `code-analyzer` / Apex deploy) are deferred to v0.2+ and require user-typed explicit write requests even then.

## Tooling stack

| Component | Source | Role |
|---|---|---|
| [`sf` CLI](https://developer.salesforce.com/tools/salesforcecli) | `brew install sf` | Salesforce DX CLI — provides OAuth (`sf org login web`), org / alias management, token cache |
| [`salesforce-mcp`](https://github.com/salesforcecli/mcp) | `brew install salesforce-mcp` (Apache-2.0) | MCP server exposing 60+ Salesforce tools (data / metadata / orgs / users / code-analyzer); v0.1.0 ships with `data,metadata` toolsets enabled |
| [`bin/sf-mcp-launcher.sh`](bin/sf-mcp-launcher.sh) | Plugin-bundled shim | Launcher: prefers brew binary, falls back to `npx -y @salesforce/mcp` when brew is unavailable; prints `sf-setup` pointer if neither path works |
| Homebrew | https://brew.sh | macOS package manager — installed automatically by `sf-setup` if missing (with y/N confirmation) |
| Node ≥ 26 (transitive) | Homebrew dependency | Runtime for the `salesforce-mcp` server |

`sf-setup` orchestrates the four installable pieces in one shot. The launcher shim means `.mcp.json` still loads if brew is missing — the server boots via `npx` at first MCP tool call.

## Prerequisites

| Item | Requirement |
|---|---|
| OS | macOS 14+ (darwin-arm64 / darwin-x86_64). Linux / WSL are Phase 2+. |
| Shell | zsh or bash (default macOS zsh is fine) |
| Terminal | Real TTY (Terminal.app / iTerm2 / VS Code integrated terminal) — required for OAuth confirmation prompts |
| Browser | Chrome or Safari (needed once for `sf org login web`) |
| Salesforce org | Production, Sandbox, Scratch, or Developer Edition org you can sign into via browser OAuth. For non-Production orgs pass `--instance-url=` to `sf-setup`. |

**Not required**: Python, uv, gcloud, custom Connected App. The `sf` CLI ships a public OAuth client that v0.1.0 uses.

## Re-auth on token expiry

Salesforce DX OAuth refresh tokens have org-policy-driven expiry (typically hours to days for sandboxes, longer for Production). When that hits, Claude Code will say the MCP server can't reach the org. Re-auth without re-running the full installer:

```bash
bash scripts/sf/refresh-auth.sh
```

Or, equivalently, re-run `/salesforce-toolkit:sf-setup --force-reauth`. Both skip the brew steps and only re-run `sf org login web` against the existing alias.

## Troubleshooting

Most common symptoms are covered in [`commands/sf-setup.md`](commands/sf-setup.md) §Troubleshooting (TTY guard / unsupported OS / brew install failure / OAuth flow cancelled / verify-empty / mutually-exclusive flags). For deeper state inspection, run `bash scripts/sf/credential-check.sh --json` to dump current `sf` + brew + MCP state without side effects.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Claude Code (CLI / Code tab)                                │
│                                                              │
│  ┌─────────────┐         ┌─────────────┐                     │
│  │  sf-query   │         │  sf-report  │                     │
│  │  (SKILL.md) │         │  (SKILL.md) │                     │
│  └──────┬──────┘         └──────┬──────┘                     │
│         │                       │                            │
│         └───────────┬───────────┘                            │
│                     ▼                                        │
│        mcp__salesforce__*  (60+ tools, data + metadata)      │
└─────────────────────┬────────────────────────────────────────┘
                      │  stdio MCP transport
                      ▼
        bin/sf-mcp-launcher.sh   (brew → npx fallback)
                      │
                      ▼
        salesforce-mcp  (Apache-2.0, salesforcecli/mcp)
                      │
                      ▼
                  sf CLI  (OAuth token from sf org login web)
                      │
                      ▼
              Salesforce org REST API
```

Setup time (one-off): `/salesforce-toolkit:sf-setup` runs the 6-step installer in the user's terminal. Runtime: Claude Code loads `.mcp.json` → spawns the launcher shim → spawns `salesforce-mcp` over stdio → MCP tools become available to the two skills.

## Links

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — product direction, Users, JTBD, Scope, Non-goals, Competitive positioning, KR targets
- [TECH-SPEC.md](TECH-SPEC.md) — module design, `.mcp.json` shape, shell script contracts, alias inference, security
- [CHANGELOG.md](CHANGELOG.md) — version history
- [`commands/sf-setup.md`](commands/sf-setup.md) — `/salesforce-toolkit:sf-setup` command reference + troubleshooting
- Parent repository: [`monkey-skills`](https://github.com/kouko/monkey-skills)

## See also

- [`gws-toolkit`](../gws-toolkit/) — Google Workspace (Slides / Docs / Sheets / Drive) toolkit; same Cowork-incompatible posture (TTY-bound OAuth)
- [`collab-toolkit`](../collab-toolkit/) — Asana / Slack / Notion via each service's official MCP server; same read-only charter
- [Salesforce DX MCP](https://github.com/salesforcecli/mcp) — upstream MCP server this plugin wraps (Apache-2.0)
- [Salesforce CLI documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_unified.htm) — `sf` command reference

## License

MIT — see [LICENSE-MIT.txt](LICENSE-MIT.txt).
