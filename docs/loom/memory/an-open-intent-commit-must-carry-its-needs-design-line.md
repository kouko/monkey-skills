---
name: an-open-intent-commit-must-carry-its-needs-design-line
description: Even for a status:open intent, the commit that last changed its status/needs-design line must carry the needs-design: line verbatim in the commit message, or intent.needs-design-reason blocks — write the line into the commit body whenever an intent file is created or its status/needs-design line changes
type: gotcha
origin: 2026-09-03-squash-merge-drops-the-needs-design-line intent, discovered during 2026-09-03-loom-post-merge-seams
---

`intent.needs-design-reason` does not exempt an open intent from carrying
its `needs-design:` line in the commit message — the check looks at the
commit that last touched the intent's status/needs-design line,
regardless of whether that status is `open` or `closed`. A commit that
creates or updates an intent file without echoing the `needs-design:`
line in its own message fails the check even though the intent file on
disk is correct.

**Why:** the check's evidence is the commit message, not the file
content — a squash merge or a rewritten commit body can carry a stale or
missing line while the file itself is fine, so the gate reads the
message as the durable record of the decision, not the file.

**How to apply:** whenever an intent file is created, or its
`needs-design:` line changes for any reason (including while the intent
stays `status: open`), copy that line verbatim into the body of the
commit that makes the change. Do not rely on "the intent is still open,
so the line doesn't need restating yet" — restate it at every touch.
