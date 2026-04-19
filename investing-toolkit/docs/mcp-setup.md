# investing-toolkit MCP setup

v1.14.0 introduces an MCP (Model Context Protocol) server that wraps
the 8 data-fetch scripts as 13 tools, exposing them directly to Claude.
This bypasses the Claude Desktop Cowork sandbox URL restrictions that
previously blocked every data-fetch call, and gives non-developer users
a "one-click install + automatic environment provisioning" flow.

This document is for **users installing the plugin**. For architecture,
see [`servers/mcp_bootstrap.sh`](../servers/mcp_bootstrap.sh) and the
v1.14.0 commit history.

---

## TL;DR

| Environment | Install path | Prerequisites | Setup time |
|-------------|--------------|---------------|------------|
| **Claude Code CLI** (any paid tier) | `/plugin marketplace add kouko/monkey-skills` → `/plugin install investing-toolkit` | macOS/Linux; auto-installs uv | ~90 s first run, <3 s after |
| **Claude Cowork (Team / Enterprise)** | Admin adds `https://github.com/kouko/monkey-skills` as custom marketplace → users browse + install | Team tier; repo must be accessible to org (private fork recommended) | ~90 s first run, <3 s after |
| **Claude Cowork (Pro / Max)** | ⚠️ No direct install from public repo. Wait for Anthropic curation OR use Claude Code CLI | — | — |
| **Claude Desktop Chat tab** | ❌ Not supported in v1.14.0 (no plugin system on Chat tab) | — | — |

---

## How the automatic setup works

When you install the plugin, Claude spawns the MCP server
(`.mcp.json` → `servers/mcp_bootstrap.sh`). On first launch:

1. `mcp_bootstrap.sh` checks for a readiness marker at
   `${CLAUDE_PLUGIN_DATA}/.mcp_ready`. First time, it's missing.
2. It **spawns `setup.sh` in the background** (detached; continues even
   if you quit Claude) and immediately execs the stdlib JSON-RPC
   wrapper to respond to Claude's `initialize` handshake in <100 ms —
   safely under the observed 60 s timeout.
3. `setup.sh` installs [`uv`](https://docs.astral.sh/uv/) if absent:
   - **Tier 1**: `brew install uv` (macOS with Homebrew)
   - **Tier 2**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. It pre-warms the dep cache by running
   `uv run --script servers/mcp_server.py --self-check`, which resolves
   and downloads Python 3.11 plus ~66 wheels (mcp, yfinance, pandas,
   akshare, curl_cffi, etc.).
5. On success, it writes the plugin version into `.mcp_ready`.
6. **You quit and reopen Claude Desktop** (Cmd+Q on macOS). Next
   bootstrap sees the marker and takes the fast path, spawning the
   real 13-tool MCP server in <3 s.

During step 1–5 you can already interact with Claude — the wrapper
exposes one tool, `investing_toolkit_status`, that reports live
setup progress.

---

## Install: Claude Code CLI (simplest)

```bash
# Inside Claude Code (CLI)
/plugin marketplace add kouko/monkey-skills
/plugin install investing-toolkit
```

Then verify:

```bash
# Your ordinary shell
ls ~/.cache/investing-toolkit/.mcp_ready   # exists once setup.sh finishes
cat ~/.cache/investing-toolkit/setup.log   # shows uv install + dep resolve
```

Ask Claude: `"Use investing-toolkit to show me NVDA's latest SEC
10-K filing date."` — if MCP tools are registered, Claude will call
`sec_edgar_filings(ticker='NVDA', forms=['10-K'], limit=1)`.

---

## Install: Claude Cowork (Team / Enterprise)

Only an organization owner / primary owner can add marketplaces. **The
public `kouko/monkey-skills` URL cannot be added directly to a Cowork
organizational marketplace** (per Anthropic's current Cowork plugin
policy). Two workarounds:

**Option A — Private fork** (recommended):
1. Fork `https://github.com/kouko/monkey-skills` to your organization's
   private GitHub account.
2. In Claude Cowork web UI: `Settings → Custom marketplaces → Add →
   https://github.com/your-org/monkey-skills`.
3. Marketplace syncs every ~30 min from the fork's `main` branch.
4. Users: `Customize → Browse plugins → investing-toolkit → Install`.

**Option B — Wait for claude.com/plugins curation**: Anthropic
occasionally promotes community plugins to its public marketplace
listing, which Pro/Max users can install directly. No submission
timeline is guaranteed.

---

## Troubleshooting

### "investing-toolkit tools aren't showing up"

Call the `investing_toolkit_status` tool directly:

> Claude: use the investing_toolkit_status tool

Expected replies:

- `⏳ still provisioning` — setup is running; wait 1–2 min and try
  again.
- `✅ ready, please restart Claude Desktop` — quit and reopen Claude
  Desktop. On the next launch, the 13 tools will register.
- `❌ FAILED: ...` — read the attached log tail. Common failures:
  - **No network** during `curl install.sh` or `pip download`.
  - **No Homebrew and no curl** → install one, re-install the plugin.
  - **Disk full** on `~/.cache/uv/`.

### "Setup finished but tools still not visible after restart"

1. Check the marker matches the plugin version:
   ```bash
   cat ~/.cache/investing-toolkit/.mcp_ready
   # should print "1.14.0" (or later)
   grep '"version"' <plugin_root>/.claude-plugin/plugin.json
   ```
2. If versions mismatch (e.g. plugin upgraded without marker refresh),
   delete the marker to force re-provisioning:
   ```bash
   rm ~/.cache/investing-toolkit/.mcp_ready
   ```
   Then restart Claude Desktop.

### "Which path (fast / bootstrap) is being taken?"

Check `bootstrap.log`:

```bash
tail ~/.cache/investing-toolkit/bootstrap.log
# "fast path → exec uv run ..." = success
# "bootstrap path: spawning setup.sh ..." = first run / version mismatch
```

### "I want to force a re-setup (debug / re-try after failure)"

```bash
rm -f ~/.cache/investing-toolkit/.mcp_ready
rm -f ~/.cache/investing-toolkit/setup.log
# Then restart Claude Desktop.
```

### "Can I run setup.sh manually without Claude?"

Yes, for testing:

```bash
export CLAUDE_PLUGIN_ROOT=/path/to/investing-toolkit
export CLAUDE_PLUGIN_DATA=/tmp/it-manual-setup
mkdir -p $CLAUDE_PLUGIN_DATA
bash $CLAUDE_PLUGIN_ROOT/servers/setup.sh
```

---

## FAQ

**Q: What data does the plugin send to external servers?**
A: Only queries to the data providers' public APIs (SEC EDGAR, FRED,
Yahoo Finance, MOPS, TWSE/TPEx OpenAPI, FinMind, akshare mirrors, NBS
new-SPA). No telemetry, no user-identifying data. `setup.sh` installs
uv either from Homebrew or from Astral's official installer.

**Q: Does the plugin work offline?**
A: Setup requires network (wheel downloads). After setup, cached API
responses stay usable offline (1 h TTL for price data, 24 h for macro
indicators). Fresh queries need network.

**Q: Can I opt out of the MCP server and only use CLI scripts?**
A: Yes — delete `.mcp.json` or the `mcpServers` entry from Claude's
config. The `uv run scripts/...` subprocess commands referenced in each
skill's SKILL.md still work unchanged.

**Q: Does this work on Windows?**
A: Not tested in v1.14.0. `setup.sh` uses bash and `curl`; a Windows
port would need PowerShell equivalents. Accept PRs.

**Q: Why 13 tools, not 8 (one per script)?**
A: Scripts with heterogeneous actions (sec_edgar: 4 distinct entry
points; yfinance: 3) get one tool per action for LLM discoverability.
Scripts with many homogeneous actions (mops: 16 endpoints; twse: 10)
use a single dispatch tool with an `action` parameter to keep the
session token cost manageable (~2 K tokens for the full surface).

**Q: Session token cost?**
A: ~1.5–2 K tokens per session for the tool schemas. Tool-call payload
sizes match the CLI JSON output identically.

---

## Reporting issues

- Plugin bugs: [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- Sandbox-related issues after v1.14.0 MCP install: attach
  `bootstrap.log` + `setup.log` tail.
