---
name: a-recorded-package-hash-is-only-valid-as-the-last-edit
description: A fingerprint of a package recorded inside a document is stale the moment anything else in that package changes, so recomputing it and then editing a changelog, manifest, or any other packaged file commits a hash that describes a tree that no longer exists — and a test run made before that last edit is a verification claim about the wrong tree
type: gotcha
origin: codex/standardize-complexity-gate (stage-specific complexity gates, close-out, 2026-08-27)
---

A behaviour-evidence report records SHA-256 fingerprints of the cold-install
package. During close-out the sequence ran: recompute the fingerprints, run the
full suite (green), edit `loom-code/CHANGELOG.md`, commit, mint the review-pass
gate marker. The changelog is inside the package, so the recorded hash was one
edit stale before it landed. The binding test was red at that commit, the marker
was minted over a red tree, and the "3204 passed" figure quoted to the reviewers
described the tree as it stood before the last edit.

**Why:** the danger is not the stale hash, which a test catches. It is that
"I ran the tests" reads as verification while naming no point in time. A suite
run is evidence about the tree that existed when it ran, and every later edit
silently widens the gap between that tree and the one being committed. Editing a
changelog feels like paperwork rather than a change to the artifact, which is
exactly why it slips past — see
[[a-mechanical-check-can-go-green-by-skipping]] for the sibling failure where the
green itself was the wrong evidence.

**How to apply:** recompute a recorded package hash as the LAST edit before
staging, never before a changelog line or a manifest bump. Run the suite after
the final edit, not after the last interesting one, and re-run it after the
commit rather than trusting the pre-commit run. When quoting a test result to a
reviewer or into a gate marker, the number must come from a run that postdates
every edit in the commit it describes.
