---
name: a-guard-test-pinned-to-the-shipping-version-ratchets-the-tag-it-guards
description: A test that asserts a document's version tag equals plugin.json's CURRENT version turns every release bump into a silent rewrite of that tag — check 19's "(v0.89.0+)" introduction marker ratcheted through 9 releases to "(v0.98.0+)", becoming the only drifting tag in its table and factually wrong; the guard must live-compare against the fact's own SSOT (the schema heading's tag), never against the shipping version
type: gotcha
origin: branch loom/code-reviewer-sonnet-default (2026-08-24) — both docs-review panel arms independently caught the drift (dual-semantics + incorrect-fact); root cause was test_check19_version_tag_matches_shipping_version comparing the tag to plugin.json
---

A `(vX.Y.Z+)` tag on a rule means "in force since X.Y.Z" — a frozen
introduction version. Check 19's guard test instead asserted the tag equals
`plugin.json`'s current version, so every routine release bump "fixed" the
tag forward: 0.89.0 → … → 0.98.0 across 9 releases. The row became the only
drifting tag among six in its table, told readers the check was newer than it
was, and contradicted its own schema heading (`plan-format.md` §Field-value
grammar `(v0.89.0+)`). Each bump's diff looked correct locally — the test
demanded it — which is exactly why nobody read the sequence.

**Why:** the original intent was sound (avoid a hardcoded literal that goes
stale mid-bump), but the live-comparison target was chosen wrong. Pinning a
document fact to the SHIPPING version makes the test enforce drift instead of
preventing it: the assertion converts "someone forgot to think about this tag"
into "the tag was silently rewritten", which review cannot catch because the
test error message instructs the editor to make the wrong change.

**How to apply:** when a guard test live-compares a documented fact, the
comparison target must be that fact's own SSOT — here the schema heading's
`(vX.Y.Z+)` tag, which moves only when the grammar is genuinely
re-introduced — never a value that changes on every release. Symptom to grep
for: a version literal in a prose/contract file that appears in release-bump
diffs alongside plugin.json. A tag that has moved in 2+ release bumps without
its underlying rule changing is this failure. Related:
[[a-cap-raised-at-every-touch-is-not-a-cap]] (the same read-the-sequence
tell on a different constant).
