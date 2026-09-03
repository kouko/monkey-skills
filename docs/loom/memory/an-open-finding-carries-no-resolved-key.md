---
name: an-open-finding-carries-no-resolved-key
description: In review.json, an open finding must carry NO resolved/dismissed key at all — push.open-findings-closed treats any non-empty string, including a placeholder like "open", as closed, so writing resolved:"open" on an unaddressed finding silently passes the gate it should fail
type: gotcha
origin: 2026-09-03-loom-post-merge-seams — 17 findings carried resolved: "open" and the push gate passed them as closed
---

`push.open-findings-closed` checks whether a finding's `resolved` (or
`dismissed`) key is present and non-empty — it does not check the key's
VALUE against the string `"open"`. A finding record that writes
`resolved: "open"` to mean "still open" satisfies the same condition as
`resolved: "fixed in a1b2c3d"`: both are non-empty strings, so both count
as closed.

**Why:** the check exists to make sure nothing slips through unaddressed.
A key whose presence means closed and whose absence means open is the
correct shape for that; a key whose VALUE has to be parsed for meaning
reopens the exact gap the gate was built to close, because the gate never
reads the value.

**How to apply:** to mark a finding open, omit the `resolved`/`dismissed`
key entirely — never write a placeholder value. When writing or
reviewing a finding record, treat "does this key exist" as the only
question that matters for the gate; a non-empty placeholder string is a
closed finding as far as `push.open-findings-closed` is concerned, no
matter what the string says.
