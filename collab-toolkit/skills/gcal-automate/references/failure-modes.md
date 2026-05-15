# Google Calendar Failure Modes

## UI evolution

**Symptom**: Protocol exits with `ERR: UI changed: <role>+<name> not found`.

**Cause**: Google Calendar renamed an element, changed a role, or restructured navigation.

**Remediation**:
1. Open `references/ui-patterns.md` and locate the failing entry
2. Run `ABX_SERVICE=gcal abx snapshot -i --json > /tmp/gcal-snap.json` against `calendar.google.com`
3. Find the new role+name combination via `jq '.elements[] | select(.role==...)'`
4. Update `references/ui-patterns.md` entry
5. Update the protocol's jq filter to match
6. Re-run protocol to verify fix

## Auth expiry / login wall

**Symptom**: Page title contains `Sign in` / `Log in`, OR URL redirects to `accounts.google.com`.

**Cause**: Google session expired or Google prompted re-authentication.

**Remediation**:
- **Shared profile mode**: Open `calendar.google.com` in your daily Chrome, complete any sign-in prompt. Next protocol invocation picks up fresh cookies.
- **Dedicated profile mode**: Run `/collab-setup --reauth gcal`.

Protocols MUST fail fast on login wall detection — do not attempt to scrape a logged-out page.

## Time-zone confusion

**Symptom**: Events appear at unexpected times (off by hours), or event times don't match user's expected local time.

**Cause**: Chrome profile's system timezone differs from the user's expected timezone. GCal inherits timezone from the Chrome profile's OS locale settings. If the dedicated profile was set up on a machine in a different timezone, all event times display in that timezone.

**Remediation**:
1. In shared mode, GCal timezone follows your OS clock — usually correct.
2. In dedicated mode: open `calendar.google.com` in the dedicated profile, go to Settings → General → Time zone, set the correct timezone, and save. This persists per-profile.
3. Protocols do not perform timezone conversion — times are returned exactly as they appear in the GCal UI.

## Calendar permission issues

**Symptom**: Colleague's calendar is visible in "Other calendars" but events show only as "Busy" with no titles or details.

**Cause**: The sharing permission granted by the colleague is **free/busy only** (not **see all event details**). Google Calendar has three sharing levels:
- Free/busy only — no event details visible
- See all event details — titles visible
- Make changes to events — full read/write

**Remediation**: Ask the colleague to change their sharing setting to "See all event details" in GCal Settings → Share with specific people. Protocol will still run; titles will show as `"Busy"` or similar placeholder until permissions are upgraded.

## Recurring event handling

**Symptom**: A recurring event appears multiple times across different dates — user asks for "the next instance" but several are returned.

**Cause**: GCal renders each instance of a recurring event as a separate `role=button` element in the week/day view. There is no series-level identifier exposed in the AT snapshot (v0.1.0).

**Remediation**: All visible instances are returned as individual events. Filtering to a single instance must be done by the caller (e.g., filter by date). Series-level deduplication is deferred to v0.2.0.

## Calendar not found in "Other calendars"

**Symptom**: `shared-calendar-read` exits with `ERR: colleague calendar 'X' not found`.

**Cause**: Either (a) the calendar was never shared with you, (b) the sharing invitation was not accepted, or (c) the display name does not match exactly.

**Remediation**:
1. Verify the calendar was shared with you in GCal → Settings → People sharing their calendars with me.
2. Accept the sharing invitation if pending.
3. Check the exact display name as it appears in GCal's "Other calendars" sidebar. Names are case-sensitive for `contains()` matching.

## Empty result vs UI evolution

**Disambiguation**:
- If the expected structural elements (e.g., `columnheader`, `Other calendars` list) appear in the snapshot but no matching events/calendars are found → likely valid empty result.
- If the structural elements themselves are absent → UI evolved; treat as error.

Protocols emit different output:
- Empty result: `(no events visible ...)` / `(no events matched)`
- UI evolved: `ERR: UI changed: <role>+<name> not found`

## Rate limiting / load failure

**Symptom**: `agent-browser` returns timeout, or page load takes > 25s.

**Cause**: Google rate-limit, slow network, or complex calendar with many events.

**Remediation**: agent-browser retries automatically. If persistent:
- Increase `AGENT_BROWSER_TIMEOUT_MS=45000` env var
- Narrow the date range before running `find-free-slots` or `agenda-view`
- For `event-search`, use more specific query terms to reduce result size
