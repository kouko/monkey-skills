---
name: an-untagged-test-needs-no-req-marker-a-none-tag-breaks-the-index
description: When a test has no registered REQ id, the convention is NO `@req` comment at all — writing `@req: none` (or any value outside the REQ namespace) creates a dangling tag that lands in the living-spec index as a "dangling @req (not in namespace)" section and turns two index tests red; delete the line, don't invent a null token
type: gotcha
origin: check-wayfinder decision-map arc (2026-08-28) — two different implementers in one branch (git-guard fence task, fog-checker task) each added `# @req: none — no registered REQ-id in this plan`, each time breaking test_check_living_spec_index's committed-index-current and no-structural-violations tests; both fixes were the same one-line comment deletion
---

The living-spec tag grammar treats every `@req:` occurrence as a
claim into the REQ namespace; there is no null value. An implementer
wanting to be explicit about "this test maps to no requirement"
should simply write no tag — absence is the convention, and the index
builder counts tags, not intentions. The failure surfaces one suite
away from the edit (loom-code's index tests, not the edited file's own
suite), which is why both authors shipped it green locally: dispatch
packets for test-writing tasks should say "no `@req` tags unless the
plan declares REQ ids" rather than leaving the null-token invention
open.
