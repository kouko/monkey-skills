# Gmail Failure Modes

## UI evolution

**Symptom**: Protocol exits with `ERR: UI changed: <role>+<name> not found`.

**Cause**: Gmail renamed an element, changed a role, or restructured navigation. Gmail ships frequent incremental UI updates.

**Remediation**:
1. Open `references/ui-patterns.md` and locate the failing entry
2. Run `ABX_SERVICE=gmail abx snapshot -i --json > /tmp/gmail-snap.json` against `mail.google.com`
3. Find the new role+name combination via `jq '.elements[] | select(.role==...)'`
4. Update `references/ui-patterns.md` entry
5. Update the protocol's jq filter to match
6. Re-run protocol to verify fix

## Auth expiry / login wall

**Symptom**: Page title contains `Sign in` / `Log in`, OR URL redirects to `accounts.google.com`.

**Cause**: Google session expired or Google prompted re-authentication (common after 30–60 days, or when accessing from a new IP).

**Remediation**:
- **Shared profile mode**: Open `mail.google.com` in your daily Chrome, complete any sign-in prompt. Next protocol invocation picks up fresh cookies.
- **Dedicated profile mode**: Run `/collab-setup --reauth gmail`.

Protocols MUST fail fast on login wall detection — do not attempt to scrape a logged-out page.

## Category tabs absent (inbox-summary)

**Symptom**: `inbox-summary` reports "Tab not present" for Social / Promotions / Updates tabs.

**Cause**: Gmail's "Categories" feature is disabled in this account's settings. When disabled, all mail arrives in Primary (or a flat inbox) with no tab separation.

**Remediation**:
1. Open Gmail → Settings → See all settings → Inbox tab
2. Under "Inbox type", select "Default"
3. Under "Categories", enable Social, Promotions, Updates, or Forums as desired
4. Reload Gmail; tabs should appear

Alternatively, if category tabs are intentionally disabled, use `mail-search` with `in:social`, `in:promotions` operators instead.

## List density mode differences

**Symptom**: Protocols return different row counts or cell layouts than expected.

**Cause**: Gmail supports three density modes — Default, Comfortable, and Compact — via Settings → Density & Color. Compact mode shows more rows; Default shows fewer but with snippet text. The `role=row` selector works across all density modes, but `.cells[]` structure may vary slightly.

**Remediation**: Protocols are written to handle density variations via `.cells // []` fallback. If cell extraction fails, full row `.name // "(unknown)"` is emitted (less structured). No specific remediation needed unless cell field positions shift.

## Conversation view vs. individual message view

**Symptom**: `thread-read` finds only one message body region when the thread has multiple messages, OR row counts in inbox are unexpectedly low.

**Cause**: Gmail's "Conversation View" (default on) groups replies into threads, showing each thread as one row and collapsing earlier messages. If "Conversation View" is off, each message is a separate row and `thread-read` navigates to a single message, not a thread.

**Remediation**:
- With Conversation View on (default): `thread-read` expands all messages; inbox shows threads as single rows — expected behavior.
- With Conversation View off: `thread-read` will show only one message; inbox shows individual messages — row counts differ. No protocol change needed; behavior is correct for the setting.
- Check setting: Gmail → Settings → See all settings → General → Conversation view.

## iframe body extraction (thread-read)

**Symptom**: `thread-read` reports empty body or partial body text even for messages with content.

**Cause**: Gmail renders message body content inside a sandboxed `<iframe>` in the live DOM. agent-browser's AT snapshot may not flatten iframe content into the top-level accessibility tree, resulting in the `role=region name="Message body"` node appearing with minimal or no accessible text.

**Remediation**:
- This is a known v0.1.0 limitation. Full body text extraction fidelity depends on agent-browser's iframe AT-flattening support, which is unverified as of v0.1.0.
- Mitigation: agent-browser may support `--allow-insecure-content` or iframe access flags in future versions; check agent-browser release notes.
- Workaround for critical content: use `mail-search` to identify the message, then open the thread URL in Chrome manually to read the full body.

## Nested label visibility (label-read)

**Symptom**: `label-read` cannot find a nested label even after parent expansion.

**Cause**: Gmail may not show all nested labels in the sidebar until explicitly expanded. The parent expansion click may not trigger a re-render that adds child label links to the AT snapshot immediately, especially if Gmail uses virtualized rendering.

**Remediation**:
1. Manually open Gmail in Chrome and expand the parent label in the sidebar to ensure it renders.
2. Verify the exact label display name including `/` path separator.
3. If label is below the visible fold (many labels), Gmail may show a "More labels" link — not automated in v0.1.0; click manually to expose the label in the sidebar before re-running the protocol.

## "Labels below the fold" (label-read)

**Symptom**: `label-read` exits with `ERR: label 'X' not found` even though the label exists.

**Cause**: Gmail's sidebar shows a limited number of labels in the AT snapshot. Labels below the visible fold are not rendered until the user scrolls or clicks "More labels".

**Remediation**: v0.1.0 does not automate "More labels" click. To access labels below the fold:
1. Open Gmail in Chrome
2. Scroll the sidebar or click "More labels" / "Show all labels"
3. Re-run the protocol (the now-visible labels should appear in the AT snapshot)

Automating sidebar scroll + "More labels" is deferred to v0.2.0.

## Gmail "Less secure app" / OAuth limitations

**Symptom**: Not applicable — this plugin does NOT use Gmail API or OAuth. It operates exclusively via Chrome browser session cookies.

**Cause**: Less secure app access, OAuth scopes, and App Passwords are Gmail API concerns, not relevant to agent-browser browser automation.

**Note**: agent-browser reads existing Chrome session cookies directly from the Chrome profile. No OAuth token or API key is required. The user simply needs to be logged into Gmail in the Chrome profile used by the plugin.

## Large attachment / download limits

**Symptom**: `thread-read` finds attachment link names but clicking them (write-scope, not in v0.1.0) would trigger download.

**Cause**: v0.1.0 is read-only — attachment links are extracted by name only; no download is triggered. If attachment names appear truncated, it is due to the AT snapshot capturing only what is visible on screen.

**Note**: Downloading or opening attachments is deferred to v0.2.0 (requires write-scope permission).

## Free Gmail vs. Workspace accounts

**Symptom**: Label behavior or filter results differ from expectations.

**Cause**: Free Gmail and Google Workspace (formerly G Suite) accounts behave identically for label / search / inbox AT-snapshot purposes. The only relevant difference is attachment quota (15 GB free vs. Workspace-configured quota) — not relevant for read-only v0.1.0 protocols.

**Note**: Workspace accounts may have admin-enforced policies (e.g., "Conversation view locked to on") that cannot be changed by the user. Such policies affect behavior but do not require protocol changes.

## Empty result vs. UI evolution

**Disambiguation**:
- If the expected structural elements (e.g., `role=row`, `role=tab`, `role=region`) appear in the snapshot but no matching items are found → likely valid empty result.
- If the structural elements themselves are absent → UI evolved; treat as error.

Protocols emit different output:
- Empty result: `(no messages matched)` / `(no messages with this label)` / `(no messages visible)`
- UI evolved: `ERR: UI changed: <role>+<name> not found`

## Rate limiting / load failure

**Symptom**: agent-browser returns timeout, or page load takes > 25s.

**Cause**: Google rate-limit, slow network, or a large inbox with many lazy-loaded rows.

**Remediation**: agent-browser retries automatically. If persistent:
- Increase `AGENT_BROWSER_TIMEOUT_MS=45000` env var
- Use more specific `mail-search` queries to reduce result size
- Narrow `inbox-summary` to fewer tabs via the `tabs` argument
