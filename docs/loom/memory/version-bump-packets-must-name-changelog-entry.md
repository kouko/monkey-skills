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

**Second variant, 2026-08-04 (loom-code 0.51.0 arc): the shipping-version
PIN TEST is a fourth deliverable of the same class.**
`loom-code/scripts/test_docs_review_blocking_class.py` pins the current
shipping version by design ("each bump rewrites it"), so a bump packet
that names only manifest + codex sync + CHANGELOG ships a red suite —
exactly what happened: the per-task triad passed (the pin lives in a file
no task touched) and only the whole-branch review caught the tip failing
its own suite. A loom-code bump packet must name the pin test rewrite as
a deliverable alongside the other three; the cheap self-check is running
the full suite AFTER the bump commit, not before it.

**Third instance, 2026-08-11 (visualization-trigger-layer, loom-code
0.76.0): the pin-test deliverable was omitted from the plan AGAIN —
and the arc-start recall missed this entry** because the recall query
named the arc's topics (templates/reviewers/pointers), not "version
bump". Two lessons layered on: (1) recall before a plan should also
grep the store for each task KIND the plan contains (a bump task →
grep "bump"), not only the arc's subject; (2) the failure was caught
this time by the mechanical-lane self-check's scope rule (diff ⊄
declared Files touched → exemption voided → full triad fallback), which
is the intended safety net — but it costs a triad; naming the pin test
in the packet up front remains the cheap path. Occurrence count is now
three: the CI-check mechanization named above graduates from candidate
to warranted next time anyone touches the bump tooling.

**Fourth instance, 2026-08-14 (loom-doc-language-layering, loom-code
0.81.0): the bump commit itself omitted the pin test + CHANGELOG — the
packet named them, the commit didn't.** The bump commit (f931c683)
changed the four plugin.json manifests and nothing else; the pin test
kept asserting 0.80.0 and the CHANGELOG had no 0.81.0 entry. The
per-task triad and whole-branch review both passed (the pin lives in a
file no task touched and the review reads the diff, not the suite), and
only verification-before-completion caught the red suite. The fix was
mechanical (rewrite the pin + add the release-record entries) but the
occurrence pattern is now four-for-four: the bump packet naming the pin
test is necessary but not sufficient — the bump COMMIT must land the
pin rewrite + CHANGELOG entry in the same commit, and the cheap
self-check is running the full suite AFTER the bump commit, not before
it. The CI-check mechanization is now warranted on the next bump-tooling
touch.
