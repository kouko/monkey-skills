# asana-automate Failure Modes (MCP V2)

Failure modes against `mcp.asana.com/v2/mcp`. Read-only protocols only.

## OAuth scope insufficient

**Symptom**: tool call returns 403 / "insufficient scope" / "forbidden" on a specific endpoint (often portfolios or workspace admin endpoints), even though task/project endpoints work.

**Background**: Asana MCP V2 grants a broad read scope by default during the `/mcp add asana` OAuth flow. Specific resource types (notably portfolios and some workspace-admin reads) may require additional scopes that aren't included by default.

**Remediation**:
1. Re-run `/mcp add asana` — Claude Code's native OAuth pre-registration will re-prompt for scopes.
2. During the OAuth consent screen, accept any additional scope checkboxes that match the failing endpoint.
3. If still failing, the user's Asana account tier may not include that resource type (portfolios are a paid feature).

## V2 lifecycle / deprecation lookahead

**Background**: Asana MCP V1 was deprecated 2026-05-11. V2 (`mcp.asana.com/v2/mcp`) is the current stable endpoint.

**Watch for**: deprecation banners in tool-call responses, or Asana developer-blog announcements of V3. When V2 is sunset, this skill needs a follow-up migration.

**Remediation when V2 is deprecated**: bump skill version, point `/mcp add asana` to the new endpoint, re-verify tool names.

## Rate limit

**Symptom**: tool call returns 429 / "rate limit exceeded".

**Background**: Asana standard API rate limit is ~1500 requests/minute per token (varies by tier — free tier lower).

**Remediation**:
- Implement exponential backoff: wait 2s, retry; on second 429 wait 8s; on third give up and surface error.
- The MCP server may handle backoff automatically — check response metadata for `Retry-After` header value.
- For bulk operations (e.g., enumerating all tasks across all projects), throttle client-side to <20 req/s.

## Token refresh

**Symptom**: tool call returns 401 / "invalid token" / "token expired".

**Background**: Claude Code's native MCP OAuth pre-registration handles refresh-token rotation automatically — this should be rare.

**Remediation**:
- If seen during a session: retry the tool call (Claude Code refreshes silently between calls).
- If persistent: run `/mcp add asana` to re-authenticate from scratch.
- Flag in the protocol output so the user knows refresh occurred.

## Tool name verification needed

**Status**: tool names below are **assumed** based on Asana V2 REST endpoint naming. Verified against `https://developers.asana.com/docs/using-asanas-mcp-server`: **not done during initial v0.2.0 rewrite** — flagged for follow-up.

**Assumed tool names**:
- `mcp__asana__list_tasks` (for protocols/task-list.md)
- `mcp__asana__get_task` (for protocols/task-detail.md)
- `mcp__asana__list_projects` (for protocols/project-overview.md)
- `mcp__asana__search` (for protocols/search-global.md)

**Possibly also needed but not yet verified**:
- `mcp__asana__list_task_stories` (for comments in task-detail)
- `mcp__asana__list_subtasks` (for subtasks in task-detail, if `opt_fields` expansion doesn't suffice)
- `mcp__asana__list_workspaces` (for resolving workspace gid)

**Verification procedure** (one-shot, run after first `/mcp add asana`):
1. Open an MCP-capable Claude Code session.
2. Ask: "list the tools exposed by the asana MCP server".
3. Compare returned names to the assumed list above.
4. If any tool name differs, update both `SKILL.md` `allowed-tools` and the protocol's `allowed-tools` frontmatter, plus the example invocations.

## Workspace gid discovery

**Symptom**: protocol asks for `workspace` parameter but user doesn't know the gid.

**Remediation**: call `mcp__asana__list_workspaces` (assumed name) to enumerate, then cache the gid in `/collab-setup` output. Until that's wired, prompt the user to find it via `app.asana.com` URL (the segment after `/0/` in any project URL is *not* the workspace gid — workspace gid is exposed via API only).

## Empty result vs error

**Disambiguation**:
- Tool call returns `data: []` with HTTP 200 → valid empty result. Emit `No <items> matching <filter>.`
- Tool call returns non-2xx → error. Surface `ERR: <status>: <message>` to user.
