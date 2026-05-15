# Notion Failure Modes

## UI evolution

**Symptom**: Protocol exits with `ERR: UI changed: <role>+<name> not found`.

**Cause**: Notion renamed an element, changed a role, or restructured navigation.

**Remediation**:
1. Open `references/ui-patterns.md` and locate the failing entry
2. Run `ABX_SERVICE=notion abx snapshot -i --json > /tmp/notion-snap.json` against the affected page
3. Find the new role+name combination via `jq 'select(...)'`
4. Update `references/ui-patterns.md` entry
5. Update the protocol's jq filter to match
6. Re-run protocol to verify fix

## Auth expiry / login wall

**Symptom**: Page title contains `Log in` / `Sign up` / `Sign in to Notion`, OR URL redirects to `notion.so/login`.

**Cause**: Notion session expired.

**Remediation**:
- **Shared profile mode**: Open Notion in your daily Chrome, log in. Next protocol invocation picks up fresh cookies.
- **Dedicated profile mode**: Run `/collab-setup --reauth notion`.

Protocols MUST fail fast on detection — do not attempt to scrape content from a logged-out session.

## No-access pages

**Symptom**: Page loads but shows a "This content is not accessible" or similar message. The `Page content` region may still appear but be empty, or the heading may read `Forbidden`.

**Cause**: The Notion page is in a workspace or sub-page the authenticated user does not have access to.

**Remediation**: Verify the page URL and ensure the Notion account used has been granted access by the page owner.

## Archived pages

**Symptom**: Page title shows a banner `This page is in Trash`. Content may still be readable.

**Cause**: The target page was archived/trashed by a workspace member.

**Remediation**: Restore the page in Notion, or note that content may be stale. `page-fetch` will still render what is visible.

## Empty result vs UI evolution

**Disambiguation**:
- If the expected role appears in the snapshot but no element matches the name → likely valid empty result (e.g., no search results, no backlinks)
- If the expected role itself is absent from the snapshot → UI evolved, treat as error

Protocols emit different output:
- Empty result: `No pages link to this page.` / `(no results)`
- UI evolved: `ERR: UI changed: <role>+<name> not found`

## Rate limiting / load failure

**Symptom**: `agent-browser` returns timeout, or page load takes > 25s.

**Cause**: Notion rate-limit, network issue, or slow page rendering (large databases).

**Remediation**: agent-browser retries automatically. If persistent:
- Increase `AGENT_BROWSER_TIMEOUT_MS=45000` env var
- For large databases, consider narrowing the URL to a filtered view before running `database-query`
