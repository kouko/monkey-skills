# <title> — spec
intent: <change-id>@<sha>
confirmed-behavior: <date> @<spec-blob-sha7>   # only when kind: product; written by the agent after decision point ②
#   <spec-blob-sha7> = the first seven chars of the spec file's blob sha
#   "before" this line was written (`git hash-object spec.md`);
#   if the spec is rewritten afterward, this line no longer matches, and
#   the checker requires the visible behavior to be presented again

## Requirements                                    [user-readable; shown for product]
REQ-1 — <name>
  WHEN <trigger>, the <system> shall <verifiable obligation> → Acceptance #<n>

## Design decision                                 [mixed; not shown]
<what to do, what not to do, and why; each agent-decided fork gets one line of reasoning; a user-decided one-way door is marked user-decided>

## Alternatives considered                         [engineering; not shown]
- <rejected alternative and reason>

## Current state evidence                          [engineering; not shown]
- Forward: <path and anchor>
- Reverse: <…>
- Error: <…>
- Data: <…>
- Boundary: <…>

## UI flows                                        [user-readable; shown for product]
<each action and the system's response (command/screen → output/state); write N/A if there is no interface>
