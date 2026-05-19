---
description: One-time bootstrap for collab-toolkit v0.2.0 — installs gws CLI + registers 3 MCP servers (Asana / Slack / Notion).
allowed-tools: Bash(brew:*), Bash(gws:*), Bash(npm:*), Bash(/mcp:*)
---

# /collab-setup

Walks you through the one-time bootstrap for collab-toolkit v0.2.0.
Read top-to-bottom; pause where prompted.

## What this sets up

- **Google Workspace CLI (`gws`)** — drives Gmail + GCal (also exposes
  Drive / Sheets for future skills).
- **3 official remote MCP servers** — Asana / Slack / Notion.

5 services, 4 OAuth dances (the Google one covers Gmail + GCal in a
single consent).

## Step 1 — Install `gws`

Try Homebrew first (preferred):

```bash
brew search gws
brew install gws   # if the formula appears
```

If the brew formula is unavailable on your machine, fall back to npm:

```bash
npm i -g @googleworkspace/gws
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

```bash
gws auth
```

This opens your default browser for the OAuth dance. **Click through
fast** — the local terminal handshake can fail with `connection
refused` if you stall in the browser (documented in the Zenn gog
設定指南). Just re-run `gws auth` on failure; it is idempotent.

## Step 4 — Asana MCP

In Claude Code:

```
/mcp add asana
```

Native OAuth pre-registration → browser opens → approve.

## Step 5 — Slack MCP

```
/mcp add slack
```

Same flow — browser-based OAuth, approve in your workspace.

## Step 6 — Notion MCP

```
/mcp add notion
```

> ⚠️ **`page-backlinks` is gone in v0.2.0.** The Notion API has no
> native backlinks endpoint; the v0.1.6 UI-scraping workaround does
> not port to the official MCP. See `CHANGELOG.md` §Notes.

## Verify

```bash
gws gmail list --limit 1      # Gmail OAuth healthy
gws calendar list --limit 1   # GCal shares the same OAuth
/mcp list                     # confirms 3 MCP servers connected
```

You should see Gmail + GCal results, plus `asana`, `slack`, `notion`
listed as connected MCP servers.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `gws: command not found` | Re-run `brew install gws` (or the npm fallback); ensure your `PATH` includes the brew prefix (`brew --prefix`/bin). |
| `GOOGLE_CLOUD_PROJECT not set` | Step 2 — export the env var and reload your shell. |
| `gws auth` → `connection refused` | Browser flow timed out — re-run `gws auth` and click through faster. |
| OAuth scope exceeded 25 | Trim unused APIs in the Cloud Console (personal-account 25-scope limit). |
| `/mcp add` fails | Update Claude Code — native OAuth pre-registration shipped late 2026; older builds lack the one-click flow. |

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
