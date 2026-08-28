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
its underlying rule changing is this failure.

**The loud twin (2026-08-28, pin-granularity arc).** The failure above is
silent — the tag is rewritten and nobody notices. A version literal can also
fail LOUDLY and name the wrong thing, and the two want opposite fixes, so
sort them before touching either:

- A **deliberate** release pin asserts `plugin.json` reads version X and the
  changelog carries a `## [X]` heading. Its function is to make a bump
  expensive enough that the changelog entry gets written. Bumping the
  manifest reddens it, and green needs TWO edits — retarget the literal AND
  add the heading. Keep it hardcoded; retargeting is the maintenance it
  exists to demand. It does NOT catch a missed bump, whatever its docstring
  says — `check_version_bump.py` does. On this arc a skill-content file
  landed with plugin.json unmoved and this pin stayed green.
- An **incidental** literal sits in a test whose subject is not versioning at
  all — here a path-resolution test whose fixture deliberately installs the
  plugin under a `0.100.0` directory to prove the directory name is never
  consulted. A shipping-version literal there turns every release into a red
  test that names path resolution. Read the version from the manifest the
  test already copied.

Tell them apart by the test's subject, not by the literal: if the test would
still be meaningful with no version anywhere in it, the literal is incidental.

Related: [[a-cap-raised-at-every-touch-is-not-a-cap]] (the same
read-the-sequence tell on a different constant);
[[a-test-can-pin-behaviour-with-a-false-rationale]] (why the deliberate pin's
own docstring claimed a guarantee it does not provide, undetected for eleven
review rounds until an arm ran the scenario the sentence described).
