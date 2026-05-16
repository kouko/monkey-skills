# notion-automate Failure Modes

Common failure modes and their remediations.

## Auth expiry / login wall

**Symptom**: page title contains `Sign in` / `Log in` / `Login`, OR URL redirects to the service's login path / `accounts.google.com`.

**Remediation**:
- **Shared profile mode**: log into notion in your daily Chrome under the configured profile. Next protocol invocation picks up fresh cookies.
- **Dedicated profile mode**: `/collab-setup --reauth notion`

Protocols MUST fail fast on detection — do NOT attempt to scrape login-walled pages.

## UI changed

**Symptom**: protocol expected an element with specific role+name (e.g., `[link] "My tasks"`), but it's not in the snapshot output.

**Remediation**:
1. Run `abx snapshot -i` against the affected page yourself
2. Inspect the text output for similar elements (capitalization variation, role change, restructured navigation)
3. Update the protocol's "look for" hint to match the new pattern

Common UI evolution patterns:
- Service rebranding (e.g., link text changes)
- Role swap (`[link]` → `[button]` or vice versa)
- Wrapping inside an extra container (the element you want is now a grandchild)

## Empty result vs UI evolution

**Disambiguation**:
- If the expected role appears in the snapshot but no element matches the name → valid empty result (e.g., no tasks matching filter)
- If the expected role itself is absent → UI evolved, treat as error

Protocols emit different output for each case:
- Empty: `No <items> matching <filter>.`
- UI evolved: `ERR: UI changed: <role>+<name> not found.` (with hint to re-snapshot)

## Daemon stale profile

**Symptom**: warning `⚠ --profile, --headed ignored: daemon already running. Use 'agent-browser close' first to restart with new options.`

**Impact**: usually no actual problem — the daemon already has the correct profile from a previous `/collab-setup` or earlier invocation. The warning is agent-browser being conservative.

**When to actually act**: only if extracted data is from the wrong account (verify by checking title or URL in protocol output). To force fresh:
```bash
agent-browser close
```

## Network timeout / page load failure

**Symptom**: `abx open` returns timeout, page load > 25s default.

**Remediation**:
```bash
export AGENT_BROWSER_TIMEOUT_MS=45000   # bump to 45s
abx open <url>
```

Or retry once after `agent-browser close`.
