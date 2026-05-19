---
description: One-time bootstrap for collab-toolkit v0.2.0 — install gws CLI + verify auto-registered MCP servers.
allowed-tools: Bash(brew:*), Bash(gws:*), Bash(npm:*)
---

# /collab-setup

Walks you through the one-time bootstrap for collab-toolkit v0.2.0.
Read top-to-bottom; pause where prompted.

## What this sets up

- **Google Workspace CLI (`gws`)** — drives Gmail + GCal (also exposes
  Drive / Sheets for future skills).
- **3 official remote MCP servers** (Asana / Slack / Notion) —
  **already auto-registered** by this plugin's `mcpServers` block in
  `plugin.json` when you installed `collab-toolkit`. Each one's OAuth
  flow triggers the first time you invoke a tool on that server.

5 services, 4 OAuth dances (the Google one covers Gmail + GCal in a
single consent; the 3 MCP OAuths fire on first tool call).

## Step 1 — Install `gws`

Try Homebrew first (preferred):

```bash
brew install googleworkspace-cli
```

The Homebrew formula name is `googleworkspace-cli` (not `gws`); the
installed binary is `gws`. If brew is unavailable, fall back to npm:

```bash
npm i -g @googleworkspace/cli
```

Verify:

```bash
gws --version
```

## Step 2 — Google Cloud project ID

`gws` needs a Google Cloud project ID exposed via env var. If you
don't have one yet:

1. Visit https://console.cloud.google.com/projectcreate
2. Create a project and note the **project ID** (not the display name).
3. Append to your shell rc (`~/.zshrc`, `~/.bashrc`):

   ```bash
   export GOOGLE_CLOUD_PROJECT=<your-project-id>
   ```

4. Reload your shell (`exec zsh` or open a new terminal).

> ⚠️ **Workspace-org vs personal Google accounts**: Workspace-org
> accounts can pick **"Internal"** on the OAuth consent screen for
> simpler scope approval. Personal Google accounts must use
> **"External"**, which enforces a **25-scope limit** on unverified
> apps — you will hit it if you enable too many APIs at once. Trim
> unused APIs in the Cloud Console if you bump the ceiling.

## Step 3 — Google OAuth

First-time setup (walks GCP config + opens browser):

```bash
gws auth setup
```

Subsequent re-auth (token refresh / scope change):

```bash
gws auth login
```

**Click through fast** — the local terminal handshake can fail with
`connection refused` if you stall in the browser (documented in the
Zenn gog 設定指南). Just re-run on failure; both commands are
idempotent.

## Step 4 — MCP servers (already registered)

The Asana / Slack / Notion MCP servers are **auto-registered** by
this plugin — open Claude Code and run:

```
/mcp list
```

You should see `asana`, `slack`, `notion` listed. **No manual
`/mcp add` step is needed.** The OAuth flow for each fires the first
time you invoke a tool on that server (e.g. asking Claude to list
your Asana tasks triggers the Asana OAuth dance).

> ⚠️ **`page-backlinks` is gone in v0.2.0.** The Notion API has no
> native backlinks endpoint; the v0.1.6 UI-scraping workaround does
> not port to the official MCP. See `CHANGELOG.md` §Notes.

## Verify

```bash
gws gmail messages list --max-results 1   # Gmail OAuth healthy
gws calendar events list --max-results 1  # GCal shares the same OAuth
```

And in Claude Code:

```
/mcp list
```

You should see Gmail + GCal results from `gws`, plus `asana`,
`slack`, `notion` listed as connected MCP servers (status pending
until first tool call triggers OAuth).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `gws: command not found` | Re-run `brew install googleworkspace-cli` (or the npm fallback `@googleworkspace/cli`); ensure your `PATH` includes the brew prefix (`brew --prefix`/bin). |
| `GOOGLE_CLOUD_PROJECT not set` | Step 2 — export the env var and reload your shell. |
| `gws auth setup` → `connection refused` | Browser flow timed out — re-run and click through faster. |
| OAuth scope exceeded 25 | Trim unused APIs in the Cloud Console (personal-account 25-scope limit). |
| MCP server missing from `/mcp list` | Plugin not loaded — verify `collab-toolkit` is installed via `/plugin list`; reinstall if missing. |
| MCP tool returns "auth required" | First-call OAuth not yet completed — Claude Code should auto-prompt; if not, restart Claude Code. |
| Asana OAuth fails with `redirect_uri not registered` / DCR error | Asana V2 officially does not support Dynamic Client Registration — some Claude Code builds rely on a default client that may stop working. **Escape hatch (per-user, never goes to git)**: register your own OAuth client at https://app.asana.com/0/my-apps, then add the `clientId` to your user-level `~/.claude.json` `mcpServers.asana.oauth` block — that user-level config overrides this plugin's entry. **Do NOT add `client_secret` to plugin.json** — it would be committed to git and exposed to every installer of this plugin. |

## Migrating from v0.1.x?

If you previously ran v0.1.x on this machine, clean up the old
user-machine state first — see `CHANGELOG.md` §Migration block for the
exact `rm -rf` command and the optional package-uninstall step. None
of the v0.1.x dependencies are referenced by any skill in v0.2.0.

## See also

- Plugin README: `<plugin-root>/README.md`
- v0.2.0 brief: `docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md`
- Skills consuming this setup: `asana-automate`, `slack-automate`,
  `notion-automate`, `gcal-automate`, `gmail-automate`
