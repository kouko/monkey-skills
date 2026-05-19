# Changelog

All notable changes to the `collab-toolkit` plugin will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

---

## [0.2.0] - 2026-05-19 — **Migrate from agent-browser to official MCP servers (non-Google scope)**

`agent-browser` is **retired**. The 3 non-Google services (Asana / Slack /
Notion) are now driven by each one's official remote MCP server,
auto-registered via the plugin's `mcpServers` block. The vendor-side gap
that justified the UI-snapshot approach in v0.1.0 has closed for all
three.

> **Scope change vs v0.1.6**: Gmail and Google Calendar (covered by v0.1.6
> `gmail-automate` / `gcal-automate`) have **moved to** [`gws-toolkit`](../gws-toolkit/).
> See §"Late-pivot 2026-05-19" below for the rationale.

### Per-service channels

| Service | Channel | How it's wired |
|---|---|---|
| Asana  | Official MCP V2 (`mcp.asana.com/v2/mcp`) | Auto-registered via plugin's `mcpServers` block |
| Slack  | Official MCP (GA 2026-02, `mcp.slack.com/mcp`) | Auto-registered; OAuth scopes declared inline |
| Notion | Official remote MCP (`mcp.notion.com/mcp`) | Auto-registered via plugin's `mcpServers` block |

### What changed in-repo

- **MCP servers ship inside the plugin.** 3 servers (Asana / Slack /
  Notion) declared in `.claude-plugin/plugin.json` `mcpServers` block,
  HTTP+OAuth transport. **No manual `/mcp add` step needed** — Claude
  Code auto-registers when the plugin loads, and triggers OAuth on
  first tool call per server.
- 3 × `SKILL.md` rewritten to declare new tools (`mcp__asana__*` /
  `mcp__slack__*` / `mcp__notion__*`).
- 12 × `protocols/*.md` rewritten as MCP invocation recipes — no UI
  snapshots, no per-locale label tables.
- `commands/collab-setup.md` simplified to MCP-verification only
  (no install / auth step — plugin handles registration; OAuth is
  per-service on first tool call).
- agent-browser fully retired: `scripts/abx`, `scripts/setup.sh`,
  `scripts/tests/` deleted.
- READMEs (en / ja / zh-TW) rewritten — drop browser framing,
  drop profile-mode table, drop Gmail/GCal rows.
- Lock-step version bump 0.1.6 → 0.2.0 across `plugin.json` + 3
  SKILL.md + 3 README.

### Late-pivot 2026-05-19 — Google services moved to `gws-toolkit`

The v0.2.0 brief originally scoped **5 services** (Asana / Slack / Notion
+ Gmail / Calendar). Mid-cycle, the 2 Google services pivoted out of
collab-toolkit into `gws-toolkit` for the following reasons:

1. **Single OAuth client** — `gws-toolkit` already owns the
   `googleworkspace-cli` (`gws`) binary, the GCP OAuth client, the
   credential file at `~/.config/gws/`, and 4 Workspace scopes
   (Slides / Docs / Sheets / Drive). Adding Gmail + Calendar there
   means one OAuth client across all Google APIs vs duplicating
   client setup in collab-toolkit.
2. **No binary/scope duplication** — collab-toolkit's brew-installed
   `gws` would race `gws-toolkit`'s vendored `~/.cache/slides-toolkit/bin/gws`
   on PATH ordering. Consolidating in `gws-toolkit` eliminates the
   race surface.
3. **Cleaner plugin boundary** — collab-toolkit becomes "non-Google
   office collab over MCP"; `gws-toolkit` becomes "all Google Workspace
   over `gws` CLI". Single-responsibility plugins are easier to
   document, install, and reason about.

**Skills do not disappear** — they relocate. Track `gws-toolkit`'s
Gmail + Calendar absorption in its own CHANGELOG / brief. The 4 Gmail
hero protocols and 4 Calendar hero protocols documented in v0.1.6 will
re-emerge as `gws-toolkit` skills in a follow-up effort (Phase 2+).

### Migration — user-machine cleanup

Run on each machine that previously installed v0.1.x:

```bash
rm -rf ~/.config/collab-toolkit \
       ~/.local/share/agent-browser \
       ~/.local/share/collab-toolkit/profiles \
       ~/.local/bin/abx
```

Optionally also uninstall the `agent-browser` brew / npm package — it
is no longer referenced by any skill.

If you previously used v0.1.6 `gmail-automate` / `gcal-automate`,
those skills now live in [`gws-toolkit`](../gws-toolkit/) (Phase 2+).
Install `gws-toolkit` and run its `/gws-setup` for the Google
Workspace side.

### Notes

- **Read-only charter preserved** — no write operations introduced;
  v0.1.x non-goals carry forward.
- **Notion `page-backlinks` dropped** — Notion API has no native
  backlinks endpoint; the v0.1.6 UI-scraping workaround is not
  portable to the official MCP. Documented as a limitation rather
  than reinvented.
- **Cowork still N/A**, but the reason changed: it is now an MCP
  availability question, not a Chrome-for-Testing question.
- **No secrets in `plugin.json`** — the `mcpServers` block ships only
  public URLs + OAuth scope names. Scope strings are public OAuth
  metadata, not credentials. If a service requires user-specific
  OAuth `clientId` / `clientSecret` (e.g. Asana V2 with strict DCR
  enforcement), those go in the user's `~/.claude.json` mcpServers
  block (user-level overrides plugin-level) — never in this plugin's
  config. Repo `.gitignore` carries defensive patterns for
  `*.env` / `*credentials*.json` / `oauth-*.json` / `*.pem` /
  `*.key` to prevent accidental commits.

Brief: `docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md`
(originally 5-service; mid-cycle pivot to 3 documented in this entry's
§"Late-pivot 2026-05-19".)
