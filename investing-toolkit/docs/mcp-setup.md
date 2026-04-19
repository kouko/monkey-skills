# investing-toolkit MCP setup

> **⚠️ v1.16.1 retrospective correction (2026-04-19)**
>
> v1.14.0 shipped MCP infrastructure under the premise that a
> plugin-installed MCP server bypasses the Claude Desktop Cowork
> sandbox URL allowlist. **This premise was wrong** — empirical
> testing in Cowork confirms that plugin-installed stdio MCP servers
> run **inside the same sandbox** as plugin-executed subprocesses, so
> both paths are blocked equally by Cowork's URL allowlist. Anthropic's
> own plugins (knowledge-work-plugins, financial-services-plugins) all
> use remote `type: http` MCPs — in retrospect, that was the signal we
> misread.
>
> **Practical impact**:
> - Claude Desktop Cowork tab: neither MCP nor subprocess work for
>   URL-fetching scripts. Use Claude Code CLI for this plugin.
> - Claude Code CLI: both MCP and subprocess work. Subprocess is the
>   cheaper default (zero token overhead); MCP adds ~4.4K session
>   tokens in return for marginal tool-UX / cache benefits.
>
> **MCP infrastructure remains shipped** because (a) it preserves
> optionality for a future remote-HTTP-MCP pivot if we ever want to
> solve Cowork properly, (b) it works fine in Claude Code CLI, and
> (c) rolling back would cost more than keeping it.

This document is for **users installing the plugin**. For architecture,
see [`servers/mcp_bootstrap.sh`](../servers/mcp_bootstrap.sh) and the
v1.14.0 / v1.16.0 / v1.16.1 commit history.

---

## What actually works where

| Environment | Subprocess (`uv run`) | MCP tool calls | Recommended path |
|-------------|:--------------------:|:--------------:|------------------|
| **Claude Code CLI** (any paid tier) | ✅ works | ✅ works | **Either**; subprocess is lower token cost |
| **Claude Desktop Code tab** (embedded CLI) | ✅ works | ✅ works | Same as CLI |
| **Claude Desktop Cowork tab** (Team / Ent / Pro / Max) | ❌ URL blocked by sandbox | ❌ URL blocked by sandbox (confirmed v1.16.1) | Pivot to Claude Code CLI |
| **Claude Desktop Chat tab** | — | ❌ (no plugin system) | Not supported |

**Cowork users**: the investing-toolkit plugin's data-fetch scripts
cannot reach external financial data providers from inside Cowork,
regardless of MCP vs subprocess invocation. Until Anthropic's allowlist
relaxes OR a remote-hosted MCP endpoint ships, use Claude Code CLI.

---

## How the automatic MCP setup works (Code CLI / Code tab)

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
   and downloads Python 3.11 plus ~66 wheels.
5. On success, it writes the plugin version into `.mcp_ready`.
6. **You quit and reopen Claude Desktop** (Cmd+Q on macOS). Next
   bootstrap sees the marker and takes the fast path, spawning the
   real 29-tool MCP server in <3 s.

During step 1–5 you can already interact with Claude — the wrapper
exposes one tool, `investing_toolkit_status`, that reports live
setup progress.

---

## Install: Claude Code CLI (simplest, recommended)

```bash
# Inside Claude Code (CLI)
/plugin marketplace add kouko/monkey-skills
/plugin install investing-toolkit
```

Verify after setup completes:

```bash
ls ~/.cache/investing-toolkit/.mcp_ready   # exists once setup.sh finishes
cat ~/.cache/investing-toolkit/setup.log   # shows uv install + dep resolve
```

Ask Claude: `"Use investing-toolkit to show me NVDA's latest SEC
10-K filing date."` — Claude will call either `sec_edgar_filings(...)`
(MCP) or `uv run scripts/sec_edgar_client.py --action filings ...`
(subprocess) depending on its own cost heuristic.

---

## Token / latency trade-off (Code CLI)

| Path | Session overhead | Per-call latency | Per-call tokens |
|------|-----------------|------------------|-----------------|
| MCP | ~4.4 K (schema of 29 tools) | ~5-20 ms (hot process) | ~80 (JSON-RPC args) |
| Subprocess | 0 | ~500-1500 ms (uv spawn) | ~150 (bash command) |

**Break-even** at ~63 calls per session. Typical sessions use 5-30 calls
→ **subprocess is cheaper in tokens** for most workflows. MCP wins on
latency for batch / repeated calls.

If you're on a tight context budget (e.g. long multi-agent sessions),
consider disabling the `investing-toolkit` MCP in `~/.claude.json`'s
`mcpServers` block and relying on subprocess alone.

---

## Troubleshooting

### "investing-toolkit tools aren't showing up"

Call the `investing_toolkit_status` tool directly:

> Claude: use the investing_toolkit_status tool

Expected replies:

- `⏳ still provisioning` — setup is running; wait 1–2 min and try
  again.
- `✅ ready, please restart Claude Desktop` — quit and reopen Claude
  Desktop. On the next launch, the 29 tools will register.
- `❌ FAILED: ...` — read the attached log tail. Common failures:
  - **No network** during `curl install.sh` or `pip download`.
  - **No Homebrew and no curl** → install one, re-install the plugin.
  - **Disk full** on `~/.cache/uv/`.

### "Cowork tab can't fetch data" (expected)

This is the v1.14.0 premise failure documented at the top of this doc.
Cowork's sandbox URL allowlist blocks both MCP-wrapped and
subprocess-invoked HTTP requests from plugins. Switch to Claude Code
CLI for this plugin.

### "Setup finished but tools still not visible after restart"

1. Check the marker matches the plugin version:
   ```bash
   cat ~/.cache/investing-toolkit/.mcp_ready
   # should print current plugin version
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
new-SPA, EDINET, TDnet, BOJ, ECB, e-Stat, CBC, DGBAS, NDC, stat.gov.tw,
FinanceDataReader). No telemetry, no user-identifying data. `setup.sh`
installs uv either from Homebrew or from Astral's official installer.

**Q: Does the plugin work offline?**
A: Setup requires network (wheel downloads). After setup, cached API
responses stay usable offline (1 h TTL for price data, 24 h for macro
indicators). Fresh queries need network.

**Q: Can I opt out of MCP entirely?**
A: Yes — delete `.mcp.json` or the `mcpServers.investing-toolkit`
entry from Claude's `~/.claude.json`. The subprocess commands in each
skill's SKILL.md still work unchanged, saving ~4.4K session tokens at
the cost of MCP tool-UX and future remote-MCP optionality.

**Q: Does this work on Windows?**
A: Not tested. `setup.sh` uses bash and `curl`; a Windows port would
need PowerShell equivalents. Accept PRs.

**Q: Why 29 tools?**
A: Scripts with heterogeneous actions (sec_edgar: 4 distinct entry
points; yfinance: 4 incl. financials; edinet: 4) get one tool per
action for LLM discoverability. Scripts with many homogeneous actions
(mops: 16 endpoints; twse: 10) use a single dispatch tool with an
`action` parameter to keep the session token cost manageable
(~4.4 K tokens for the full surface).

**Q: When will Cowork work?**
A: Either Anthropic relaxes the plugin-MCP sandbox URL allowlist (no
ETA, do not assume), or investing-toolkit ships a remote-hosted MCP
endpoint (out of scope for a solo-maintained OSS plugin — cost +
privacy concerns). Track the ROADMAP.md "v1.16.1 retrospective" entry
for any changes.

---

## Reporting issues

- Plugin bugs: [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- Cowork-related issues: please check this doc's top retrospective
  section first — it's almost certainly the documented sandbox
  limitation, not a plugin bug.
- For install failures, attach `bootstrap.log` + `setup.log` tail.
