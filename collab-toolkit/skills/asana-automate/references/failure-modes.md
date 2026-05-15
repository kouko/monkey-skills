# Asana Failure Modes

## UI evolution

**Symptom**: Protocol exits with `ERR: UI changed: <role>+<name> not found`.

**Cause**: Asana renamed an element, changed a role, or restructured navigation.

**Remediation**:
1. Open `references/ui-patterns.md` and locate the failing entry
2. Run `ABX_SERVICE=asana abx snapshot -i --json > /tmp/snap.json` against the affected page
3. Find the new role+name combination via `jq 'select(...)'`
4. Update `references/ui-patterns.md` entry
5. Update the protocol's jq filter to match
6. Re-run protocol to verify fix

## Auth expiry / login wall

**Symptom**: Page title contains `Sign in` / `Log in` / `Login`, OR URL redirects to `*asana.com/-/login*`.

**Cause**: Asana session expired.

**Remediation**:
- **Shared profile mode**: Open Asana in your daily Chrome, log in. Next protocol invocation picks up fresh cookies.
- **Dedicated profile mode**: Run `/collab-setup --reauth asana`.

Protocols MUST fail fast on detection — do not attempt to scrape login state from a logged-out session.

## Empty result vs UI evolution

**Disambiguation**:
- If the expected role appears in the snapshot but no element matches the name → likely valid empty result (e.g., no tasks matching filter)
- If the expected role itself is absent from the snapshot → UI evolved, treat as error

Protocols emit different output:
- Empty result: `No tasks matching filter`
- UI evolved: `ERR: UI changed: <role>+<name> not found`

## Rate limiting / load failure

**Symptom**: `agent-browser` returns timeout, or page load takes > 25s.

**Cause**: Asana rate-limit, network issue, or slow page.

**Remediation**: agent-browser retries automatically. If persistent:
- Increase `AGENT_BROWSER_TIMEOUT_MS=45000` env var
- Reduce frequency of protocol invocations
