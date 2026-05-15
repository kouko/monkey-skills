# Slack Failure Modes

## UI evolution

Same playbook as asana-automate. Update `references/ui-patterns.md` first, then protocol jq filters.

1. Run `ABX_SERVICE=slack abx snapshot -i --json > /tmp/slack-snap.json` against the affected page
2. Inspect for elements near the failing area
3. Identify new role+name combination
4. Update `references/ui-patterns.md`
5. Update the failing protocol's jq filter

## Auth expiry

Detection: title contains `Sign in to Slack`. Or URL redirects to `slack.com/signin`.

Remediation:
- Shared mode: log into Slack in your daily Chrome
- Dedicated mode: `/collab-setup --reauth slack`

## Channel not in sidebar

User might have left the channel, or it might be hidden under "More" expansion. Protocol falls back to channel URL-based access (`https://app.slack.com/client/<workspace>/<channel-id>`).

## Free tier limitations

Slack Free workspaces have:
- 90-day message history (older messages return "Upgrade to see")
- No People view

`find-user` protocol handles People-view absence by falling back to @-typeahead in any open channel.

## People view absent

`find-user` detects `ERR: People link not found` and suggests the @-typeahead fallback — type `@<query>` in a channel message input, snapshot the suggestion `option` elements for user names.

## Search returns 0 results

For a known-good query, 0 results often means auth has expired silently. Run:
```bash
ABX_SERVICE=slack abx snapshot -i --json | jq '.elements[] | select(.role=="button" and .name=="Sign in")'
```
Non-empty output confirms auth expiry — remediate as above.
