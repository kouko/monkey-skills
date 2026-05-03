# ADR-0008: Remove MCP Server (revert to skill-only single-consumer model)

- **Status**: Accepted
- **Date**: 2026-05-03
- **Version target**: investing-toolkit v2.2.0
- **Supersedes**: parts of ADR-0001 (§"Acceptable Duplications" canonical-vs-skill-copy duality), parts of ADR-0007 (dual-consumer framing)

## Context

investing-toolkit shipped MCP server support in v1.14.0 (`investing-toolkit/servers/mcp_server.py`) so external MCP clients (Claude Desktop, Cline, Cursor, etc.) could consume the same data clients that Claude Code's slash commands invoke directly. Each of the 14 data clients gained a `register_mcp_tools(mcp)` function and a canonical copy under `investing-toolkit/scripts/<client>.py` for the server's `sys.path` import.

Through v2.0–v2.1 this design held two consumers:

1. **Claude Code path** — slash commands (`/invest-snapshot`, `/invest-macro`, etc.) and agent dispatch invoke `uv run skills/data-{country}/scripts/<client>.py` directly. **No MCP involved.**
2. **External MCP path** — `mcp_server.py` boots FastMCP, imports each client from `investing-toolkit/scripts/<client>.py`, registers tools, exposes JSON-RPC over stdio.

By 2026-05-03 four data points converged that made the dual-consumer design net-negative:

### 1. Zero observed external usage

Verified during the 2026-05-03 architecture session:
- The user is the sole maintainer + sole consumer
- Claude Code is the only client used end-to-end
- No external LLM (Claude Desktop, Cursor, Cline, etc.) has been pointed at the toolkit's MCP server
- Plugin manifest `plugin.json` does not advertise MCP usage; commands route via SKILL.md → `uv run`

The "future external consumer" benefit of MCP is purely speculative for this toolkit.

### 2. CI-level instability

After the v2.1.x-d gate promotion, MCP equivalence tests (`tests/test_mcp_equivalence_auto.py` + `test_mcp_contract.py`) became part of the per-PR `pytest -m "not network"` gate. Throughout the 2026-05-03 session:
- 5 PRs opened
- 4 hit `test_mops_fetch_*` or `test_mcp_matches_cli[...]` failures
- Pattern: server logs `Processing CallToolRequest` but reply never reaches the test reader before timeout
- ~80% empirical flake rate

Root cause: FastMCP × stdio × Azure runner combination has timing-sensitive race (likely stdout buffering or asyncio scheduling). Tests pass 6/6 locally on macOS (faster CPU, unbuffered stdio). v2.1.x-i tracks investigation but the fix is non-trivial (audit FastMCP version, retry-with-backoff in test reader, server warmup probe).

PR #224 mitigated symptomatically by demoting MCP tests to `@pytest.mark.network`. That preserved CI velocity but admitted MCP equivalence is structurally incompatible with our cloud-CI environment.

### 3. Maintenance overhead doubles cache architecture cost

ADR-0007 (v2.2.0-j cache policy) committed to embedding identical helper blocks in every client + byte-equality CI guards. With MCP, that means:

- 14 clients × 2 copies (skill + canonical at `investing-toolkit/scripts/`) = **28 file edits** for any cache-helper change
- 9 sync-clients.sh groups (PR #222) — most exist solely to keep MCP canonical aligned with skill copy
- Block-level CI sync guard (planned Phase 2) needs to span 28 files instead of 14

If MCP goes away:
- 14 clients × 1 copy = **14 file edits**
- sync-clients.sh shrinks from 9 groups to 2 (only yfinance × 5 cross-skill, fred × 2 cross-skill — these are real cross-skill duplications, not MCP-driven)
- Phase 3 of v2.2.0-j (bulk migration to cadence-aware TTL) drops from 26 file edits to 13

### 4. Reversibility argument fails

The "keep MCP just in case" argument assumed re-enabling later would be cheap. By 2026-05-03:
- FastMCP API is rapidly evolving (multiple breaking changes between minor versions during 2026)
- MCP protocol itself adopted new transport options (HTTP, WebSocket) that may supersede stdio
- Today's `mcp_server.py` boilerplate would likely be obsolete within 6–12 months even without active changes

If the user's workflow ever needs external LLM access, rebuilding from current best practices will likely produce a cleaner result than maintaining today's stale code. Reversibility is not as cheap as "keep the file".

## Decision

**Remove the MCP server entirely**. Revert to a single-consumer (Claude Code skill) architecture.

### Removed surface

| Path | Reason |
|---|---|
| `investing-toolkit/servers/` | MCP server entry, bootstrap script, wrapper, setup |
| `investing-toolkit/scripts/<client>.py` × 14 | Canonical copies that existed solely for `mcp_server.py` `sys.path` import. Skill copies under `skills/data-*/scripts/` remain authoritative. |
| `investing-toolkit/scripts/setup.sh` + `requirements.txt` + 3 README files | MCP-installation focused; no longer needed |
| `investing-toolkit/scripts/sync-clients.sh` | Heavily restructured (9 groups → 2) |
| `investing-toolkit/scripts/ta_client.py` | Single consumer (`analysis-technical`) — moved into the skill (was already canonical owner) |
| `investing-toolkit/tests/test_mcp_contract.py` | MCP-only test |
| `investing-toolkit/tests/test_mcp_equivalence_auto.py` | MCP-only test |
| `investing-toolkit/docs/mcp-setup.md` | MCP installation guide |
| `register_mcp_tools(mcp)` function in 14 skill client files | Dead code without server |

Total: ~10,000 lines net deletion (most are 1:1 mirrors of skill copies that are now redundant).

### Kept surface (skill-only consumer)

- All `skills/data-{country}/scripts/<client>.py` files — authoritative client implementations
- `pack.py` orchestration in each data skill
- All cross-skill-shared clients: `yfinance_client.py` (5 skill copies), `fred_client.py` (2 skill copies). PR #222's sync-clients.sh logic for these two groups remains.

### sync-clients.sh restructure

Before (9 groups, after PR #222):

| Group | Canonical | Targets |
|---|---|---|
| 1 | `investing-toolkit/scripts/yfinance_client.py` | 5 skills |
| 2 | `investing-toolkit/scripts/fred_client.py` | 2 skills |
| 3 | `investing-toolkit/scripts/nbs_client.py` | 1 skill |
| 4 | `investing-toolkit/scripts/akshare_client.py` | 1 skill |
| 5 | `investing-toolkit/scripts/dgbas_client.py` | 1 skill |
| 6 | `investing-toolkit/scripts/ndc_client.py` | 1 skill |
| 7 | `investing-toolkit/scripts/cbc_client.py` | 1 skill |
| 8 | `investing-toolkit/scripts/statgov_client.py` | 1 skill |
| 9 | `investing-toolkit/scripts/fdr_client.py` | 1 skill |

After (2 groups — only real cross-skill duplications):

| Group | Reference | Cross-skill copies |
|---|---|---|
| 1 | `data-us/scripts/yfinance_client.py` (canonical-by-position) | data-jp, data-tw, data-kr, data-cn (4 copies, each must equal data-us) |
| 2 | `data-us/scripts/fred_client.py` | data-cn (1 copy) |

The "no canonical, just first-skill = reference" pattern is acceptable because these clients existed for cross-skill use (yfinance: every country uses Yahoo; fred: US + CN macro reuse) — not for an MCP consumer.

### check-script-sync.yml restructure

Groups 3–9 deleted from the workflow's embedded Python check; Groups 1 + 2 retained with reference-skill (data-us) substituted for the deleted `investing-toolkit/scripts/` canonical.

### v2.2.0-j Phase 3 effort halved

`ROADMAP.md §v2.2.0-j` Phase 3 explicitly stated "13 clients × 2 copies = 26 file edits". Updated to "13 clients × 1 copy = 13 file edits" since the canonical-vs-skill-copy duality goes away. Phase 2 (block-level CI sync guard) sims simpler (14 files instead of 28).

### v2.1.x-i marked obsolete

ROADMAP §v2.1.x-i ("MCP stdio test stability hardening") is closed-as-obsolete: MCP server gone → MCP tests gone → no flake to fix.

## Consequences

### Positive

- **CI-level stability** — `pytest -m "not network"` no longer at risk of MCP flakes; per-PR gate becomes reliable
- **Cache architecture cost halved** — Phase 3 bulk migration goes from 26 → 13 file edits; block-level sync guard spans 14 files instead of 28
- **Repository size shrinks** ~10,000 lines (mostly mirror duplications)
- **Cognitive load reduced** — single consumer model; no "two parallel paths" to track
- **Sync mechanism radically simpler** — 9 groups → 2 groups; only real cross-skill duplications remain
- **Anthropic skill convention preserved more cleanly** — no more "canonical at toolkit-level outside skill scope" exception

### Negative

- **Loss of external LLM client capability** — external MCP clients can no longer point at this toolkit. Reversal cost: 1–2 days to rebuild against the FastMCP version in vogue at that time (unlikely to be today's, given protocol churn).
- **MCP equivalence test as integration safety net is gone** — replaced by trust in Claude Code's direct invocation path being sufficient (as it has been for 100% of observed usage).
- **ADR-0001 requires amendment** — its "Acceptable Duplications" §canonical-vs-skill-copy reasoning no longer applies to nbs/akshare/dgbas/ndc/cbc/statgov/fdr.
- **ADR-0007 dual-consumer framing is partially obsolete** — the "MCP consumer + skill consumer" justification for the embed-not-import decision becomes "single consumer with cross-skill duplication for yfinance/fred". The core argument (PEP 723 self-contained scripts + Anthropic skill convention) still stands; just one of the supporting reasons drops.

### Neutral

- **Plugin manifest** (`plugin.json`) doesn't advertise MCP usage today, so no user-facing change there.
- **Existing cache files in `~/.cache/investing-toolkit/`** continue to work unchanged — the cache layer is in skill scripts, not in MCP server.
- **`servers/` directory deletion** affects nothing in the standard Claude Code workflow.

## Alternatives considered (recap)

- **Option B — keep but quarantine**: Mark MCP tests `@pytest.mark.network`, leave server code in place. Considered earlier in 2026-05-03 session. Rejected because it preserves the cache-architecture-cost penalty (still 28 file edits across 14 × 2 copies) without the offsetting external-consumer benefit (still 0 actual external users).
- **Option C — keep + fix flakes**: Pursue v2.1.x-i (stdout flush + retry-with-backoff). Rejected because the underlying cause is FastMCP × Azure-runner timing fragility; even a successful fix would only paper over the larger maintenance burden.
- **Option D — publish toolkit-cache as PyPI package** (from ADR-0007): Re-evaluated as the *future* path for cross-LLM exposure. If the user later needs external LLM access, publishing data clients as a PyPI package (not via MCP stdio) is likely cleaner and survives MCP protocol churn.

## Migration impact

### Existing users

None — sole consumer is the maintainer, who uses Claude Code path exclusively.

### CI/CD pipelines

- `pytest -m "not network"` continues to gate per-PR. After this PR, total test count drops by ~24 (MCP tests deleted entirely; were already deselected via mark in PR #224).
- `check-script-sync.yml` Groups 1+2 retain. Groups 3–9 removed.
- `sync-clients.sh --check` continues to enforce yfinance/fred byte-equality across cross-skill copies.

### Documentation

- ADR-0001 §"Acceptable Duplications" amended to remove canonical-vs-skill-copy table for the 7 single-skill clients.
- ADR-0007 amended: "two consumers" framing replaced with "cross-skill duplication for yfinance + fred" framing. Core decision (embed not import) stands.
- ROADMAP §v2.2.0-j Phase 3 effort numbers halved.
- ROADMAP §v2.1.x-i marked closed/obsolete.
- `docs/mcp-setup.md` deleted.

### Cache files in user filesystem

Unaffected. `~/.cache/investing-toolkit/<client>/<key>.json` continues as before; v2.2.0-j Phase 0+1 schema v2.0 envelope is preserved.

## References

- ADR-0001 (three-layer architecture) — v2.0.0 commitment to PEP 723 self-contained scripts
- ADR-0007 (skill-self-contained cache helpers) — v2.2.0-j cache architecture; framing partially superseded
- ROADMAP §v2.1.x-i — closed as obsolete with this PR
- ROADMAP §v2.2.0-j Phase 3 — effort halved with this PR
- 2026-05-03 architecture session — Option A (full removal) chosen after evaluating B/C/D
- PR #224 — predecessor that demoted MCP tests to network-marked (tactical unblock)
