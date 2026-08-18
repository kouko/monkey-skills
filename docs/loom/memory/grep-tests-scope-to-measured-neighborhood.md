---
name: grep-tests-scope-to-measured-neighborhood
description: Whole-file substring grep-tests over prose files go false-green when the asserted phrase pre-exists elsewhere in the file, and pinning a phrase's text plus its file-wide uniqueness still does not pin the SECTION that makes it fire — scope assertions to a measured window around the feature's anchor, make the anchor the enclosing section whenever placement is load-bearing, and verify RED against the pre-change content
type: gotcha
origin: PR feat-loom-code-upstream-hardening (2026-07-10), plan T11 round-2 — two of seven grep-tests passed with the feature entirely absent
---

Grep-style behavioral tests over SKILL.md / agent prose assert phrase
presence. When the asserted phrases are generic ("stage", "close-out
commit", "orchestrator-only"), they often pre-exist in OTHER bullets of
the same file, so the test passes with the new feature entirely absent —
a false green that survives full-suite runs and per-task review.

**Why:** the failure is invisible exactly when it matters — the test
"guards" a feature it never actually gates, and nothing fails when the
feature is deleted. In this repo two of T11's seven tests were
false-green on first review (caught by the quality reviewer diffing
against `git show HEAD:<file>`), and the fix's window size itself had to
be measured, not guessed, to avoid re-acquiring the same risk from a
different neighbor bullet.

**How to apply:** (1) scope each assertion to a neighborhood window
around the feature's unique anchor string (e.g. the script filename),
with the radius MEASURED against the real file: window must include the
feature's own phrases and exclude the nearest sibling carrying the same
generic terms; (2) prove RED by running the assertions against the
pre-change content (`git show HEAD:<file>` or a scratch copy with the
feature stripped) — "suite is green" never demonstrates a grep-test is
load-bearing; a mutation check (strip the feature, expect fail) does.

**A wording pin is not a wiring pin** (second variant, observed
2026-08-14 in `feat/open-question-dispatch-gate`). A guard asserted its
paragraph's exact text AND that the text appeared exactly once in the
file — both true, both green — and still did not pin the paragraph's
**section membership**. Relocating the whole paragraph out of
`## Self-review`, the section that is what makes it fire, left the
suite green: the rule's text survived, its wiring did not. Whenever
placement is load-bearing (a rule that fires only because of the
section it sits in), the window's anchor must be the enclosing section
heading, not the rule's own phrase, and the mutation check is "move the
paragraph, expect fail" — not "delete it, expect fail". Precedent for
the right shape already existed in the same suite:
`test_wp_extraction_pointers.py::test_coverage_gate_reachable_from_self_review`.
Judging whether placement IS load-bearing stays a judgment call; this
entry pins the test shape, not the trigger for reaching for it.
