---
name: an-advertised-permission-gets-one-live-run-against-its-own-validator
description: A permission sentence and the validator banning its side effect can ship in ONE branch and contradict each other — each reads fine alone, per-task review passes both, and no text sweep sees it because neither text quotes the other; the catch is EXECUTING the advertised action once against the branch's own shipped validator (build the smallest artifact the permission licenses, run the validator, expect exit 0), so every review of a branch that both grants a capability and ships an enforcement mechanism owes one such live probe per granted capability
type: gotcha
origin: 2026-08-08 direction-layer arc (loom-code 0.69.0), whole-branch round-1 docs arm — DIRECTION.md's charter granted "## Next may point at a roadmap entry by filename" while the same branch's validator banned date tokens outside ## Now; backlog filenames are date-prefixed by the store's own filename rule, so exercising the permission failed validate exit 1; caught only by the docs arm running the validator on a pointer-bearing fixture, after two per-task review rounds and a CHANGELOG round had passed all three carriers
---

The direction-layer branch shipped, in one arc: a charter permission
("a `## Next` line MAY point at a roadmap entry by filename"), a
filename rule making those filenames date-prefixed, and a validator
banning date-like tokens outside the generated `## Now`. Every carrier
was individually reviewed — per-task rounds on the charter and the
validator, plus a dedicated CHANGELOG fix round — and all passed,
because each sentence is true in isolation. The feature was unusable:
exercising the permission produced a file the branch's own validator
rejected (exit 1), found only when the whole-branch docs arm built a
pointer-bearing fixture and ran the validator on it.

**Why:** this class is invisible to text-level review. The permission
does not quote the ban; the ban does not quote the permission; the
contradiction only exists in the COMPOSITION of three rules, so string
sweeps, pin tests, and neighbor re-reading (the
[[a-rule-edit-falsifies-the-unchanged-prose-composed-with-it]] pass)
all miss it. The only reliable detector is execution: perform the act
the prose licenses and let the branch's own machinery judge it.

**How to apply:** when a branch both GRANTS a capability in prose (a
MAY/CAN sentence, an advertised flag, a documented pattern) and ships
an enforcement mechanism (validator, hook, guard, schema), the review
owes one live probe per granted capability: construct the smallest
artifact the permission licenses, run the branch's own
validator/guard against it, and require the permitted form to pass.
Reviewers should treat a MAY-sentence like untested code — a
capability without one green execution is unverified, whatever the
prose rounds said. Cheapest venue: the whole-branch review dispatch
packet names each newly granted capability and asks one arm to
exercise it.
