---
name: version-bump-packets-must-name-changelog-entry
description: Every loom plugin keeps a Keep-a-Changelog CHANGELOG.md and every prior version bump updated it in the same commit — but implementer task packets that say only "bump plugin.json" ship entry-less bumps (5 consecutive misses across v1+v2 knowledge-triage); the packet must name the CHANGELOG entry as an explicit deliverable
type: gotcha
origin: feat-knowledge-triage-v2 (2026-07-18) — T9 reviewer caught loom-interface-design 0.6.0; check generalized to all five bumps on the arc
---

The knowledge-triage arc bumped five plugin versions (loom-code 0.32.0/
0.33.0, loom-spec 0.5.0, loom-discovery 0.2.0, loom-product-principles
0.10.0, loom-interface-design 0.6.0). Every dispatch packet said "version
bump: plugin.json minor + codex sync" — and every implementer did exactly
that and nothing more. All five CHANGELOGs went stale; three shipped to
main entry-less in PR #581 before T9's code-quality reviewer checked ONE
plugin's commit precedent and found the convention.

**Why:** "version bump" reads as a manifest edit; the CHANGELOG entry is
governed by convention (every prior bump commit updated it), not by any
test or hook, so nothing fails when it's missed. Reviewers scoped per-task
don't check sibling-plugin precedent — only one reviewer thought to.

**How to apply:** any task packet that bumps a plugin version must list
"CHANGELOG.md entry under `## [X.Y.Z] — <date>`" as a named deliverable
next to the manifest bump — and a reviewer checking a version bump should
`git log --follow <plugin>/CHANGELOG.md` for the convention before
passing. Candidate mechanization if it recurs: a CI check that a
plugin.json version appearing in a diff has a matching CHANGELOG heading.
