---
name: reviewers-rerun-mutations-before-accepting-fix
description: Reviewers should re-run the breaking mutation themselves (e.g. delete the guard in scratch and watch the test fail) before accepting a fix claim
type: practice
origin: PR #488 (loom family connective tissue, SDD wave reviews 2026-07-04)
---

When an implementer claims "fixed, test now catches it", the
reviewer should re-run the mutation themselves rather than trusting
the claim: in a scratch copy, delete or break the guard the fix
added and confirm the test actually fails. Observed working on
PR #488's review rounds — one reviewer re-verified that all three
claimed-failing cases fail, another deleted the guard in scratch to
prove the new test catches its removal.

**Why:** a test can pass for reasons unrelated to the fix (false
green), and a fix claim is a belief until the failure mode is
re-demonstrated; re-running the mutation converts the claim into an
executed check.

**How to apply:** as a reviewer, before accepting a fix for a
finding, revert or mutate the fix in a scratch checkout and confirm
the accompanying test goes red; then restore and confirm green.
