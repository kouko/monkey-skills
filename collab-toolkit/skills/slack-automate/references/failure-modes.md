# slack-automate Failure Modes (Slack MCP)

Failure modes against the official Slack MCP server. Read-only protocols only.

## OAuth scope insufficient

**Symptom**: tool call returns `missing_scope` / `not_allowed_token_type` / 403, often on a specific resource (e.g., `search.messages` works but `users.list` fails, or public channels work but private DMs don't).

**Background**: Slack MCP grants a default read scope set during the `/mcp add slack` OAuth flow. Specific resources require additional scopes:
- `search:read` for `search.messages`
- `channels:history` / `groups:history` / `mpim:history` / `im:history` for `conversations.history` and `conversations.replies` (one per channel type)
- `users:read` (+ `users:read.email` for emails) for `users.list` / `users.lookupByEmail`

**Remediation**:
1. Re-run `/mcp add slack` — Claude Code's native OAuth pre-registration will re-prompt for scopes.
2. During the OAuth consent screen, accept the additional scope checkboxes that match the failing resource type.
3. If still failing, the workspace admin may have restricted scope grants for non-admin users — escalate.

## Workspace visibility (private vs public channels)

**Symptom**: `channel_not_found` for a channel that visibly exists, or empty `messages: []` for a channel known to have activity.

**Background**: Slack scopes channel visibility per token-holder. Even with `channels:read`:
- Private channels require the user to be a member.
- DMs / group DMs are visible only to participants.
- Channels in other connected workspaces (Slack Connect) may not be enumerated unless explicitly shared.

**Remediation**:
- Verify the authenticated user is a member of the target channel via the Slack UI.
- For private channels: join the channel, then retry.
- For Slack Connect channels: confirm the external workspace has granted access.

## Rate limit

**Symptom**: tool call returns 429 / `ratelimited` / `Retry-After: <seconds>` header.

**Background**: Slack Web API rate limits are tier-scoped (api.slack.com/docs/rate-limits):
- Tier 1 (e.g., `team.info`): ~1 req/min — rarely used here.
- Tier 2 (e.g., `conversations.history`, `users.list`): ~20 req/min.
- Tier 3 (e.g., `chat.postMessage`): ~50 req/min — not used (read-only skill).
- Tier 4: ~100 req/min.
- Special: `search.messages` enforces its own quota (often ~30 req/min per workspace, plus daily caps on Free / Pro tiers).

**Remediation**:
- Honor the `Retry-After` header value if present — wait that many seconds before retry.
- For bulk operations (e.g., enumerating thread replies across many threads), throttle client-side to <10 req/s.
- The MCP server may handle backoff automatically — check response metadata.

## Real-Time Search API quota

**Symptom**: `search.messages` returns `error: ratelimited` or `error: search_disabled`, or results are silently truncated to recent days.

**Background**:
- Free Slack tier: only the most recent 90 days of messages are searchable; older messages return as "missing" without error.
- Paid tiers: full history searchable but `search.messages` is a separate quota (typically ~30 req/min, with daily caps).

**Remediation**:
- For deep history on Free tier: not possible via `search.messages`; archive export is the only path.
- For repeated bulk search: throttle, or cache results in `/collab-setup` output.

## Token refresh

**Symptom**: tool call returns 401 / `invalid_auth` / `token_expired`.

**Background**: Claude Code's native MCP OAuth pre-registration handles refresh-token rotation automatically — this should be rare.

**Remediation**:
- If seen mid-session: retry the tool call (Claude Code refreshes silently between calls).
- If persistent: run `/mcp add slack` to re-authenticate from scratch.
- Flag in protocol output so the user knows refresh occurred.

## Tool name verification needed

**Status**: tool names below are **assumed** based on Slack Web API method naming and the Asana MCP V2 precedent. Verification against the official Slack MCP catalogue (GA 2026-02): **not done during initial v0.2.0 rewrite** — flagged for follow-up.

**Assumed tool names**:
- `mcp__slack__search_messages` (for protocols/search-messages.md)
- `mcp__slack__read_channel` (for protocols/channel-read.md; may instead be exposed as `mcp__slack__channel_history` or `mcp__slack__conversations_history`)
- `mcp__slack__read_thread` (for protocols/thread-read.md; may instead be `mcp__slack__conversations_replies`)
- `mcp__slack__find_user` (for protocols/find-user.md — **Open Q4**: may not exist as a single tool; could require `mcp__slack__list_users` + client-side filter, or may be absent entirely on the official MCP)

**Possibly also needed but not yet verified**:
- `mcp__slack__list_channels` (to resolve channel-name → channel-id for protocols/channel-read.md)
- `mcp__slack__get_user_info` (for individual user lookups by ID)

**Verification procedure** (one-shot, run after first `/mcp add slack`):
1. Open an MCP-capable Claude Code session.
2. Ask: "list the tools exposed by the slack MCP server".
3. Compare returned names to the assumed list above.
4. If any tool name differs, update both `SKILL.md` `allowed-tools` and the protocol's `allowed-tools` frontmatter, plus the example invocations.
5. **If `mcp__slack__find_user` (or equivalent) is absent**: drop `protocols/find-user.md` in v0.3.0, update `SKILL.md` hero-protocols list to show 3, and surface in CHANGELOG.

## Channel-name resolution

**Symptom**: protocol asks for `channel` parameter but user gave a name (`engineering`) and MCP requires an ID (`C0123456789`).

**Remediation**: call `mcp__slack__list_channels` (assumed name) to enumerate and match by name; cache the channel-id map in `/collab-setup` output. Until cached, prompt the user for the channel ID (visible in the Slack web URL: `https://<workspace>.slack.com/archives/<channel_id>`).

## Empty result vs error

**Disambiguation**:
- Tool call returns `messages: []` (or equivalent) with `ok: true` → valid empty result. Emit `No <items> matching <filter>.`
- Tool call returns `ok: false` with `error: <code>` → error. Surface `ERR: <error_code>: <message>` to user.
