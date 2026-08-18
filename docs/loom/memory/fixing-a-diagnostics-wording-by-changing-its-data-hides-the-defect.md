---
name: fixing-a-diagnostics-wording-by-changing-its-data-hides-the-defect
description: When a reviewer flags a diagnostic's WORDING as misleading, fix the message, never the data feeding it — collapsing the data so the message reads cleanly (deduping the repeated path that made "multiple files: p, p" look wrong) can erase the very condition the diagnostic existed to report, and the change ships green because the only test that touched the case is reshaped to pin the new, holed behaviour
type: gotcha
origin: requirement-identity-hybrid arc, whole-branch review round 1 → 2 (2026-08-18) — a 🟢 nit ("same-file duplicate REQ reports 'declared in multiple files: p, p'") was fixed by deduping paths per file in `load_req_paths`; round 2 found the same-file duplicate now passed the CI structural lane silently (rc=0, `--next-req-id` moved on to REQ-6) — exactly the merge-boundary collision the arc's BI-3 exists to catch; fixed by keeping the repeats and emitting "declared N times in <path>"
---

A round-1 whole-branch nit said the duplicate-declaration violation read
oddly when both declarations sat in one file: "REQ-5 declared in multiple
files: spec.md, spec.md". The implementer fixed it by making the loader
return each path once per file. The message became clean because the
condition it reported had been deleted from the data: with one path per
file, `len(paths) > 1` was false, no violation fired, and a same-file
duplicate id — two branches each appending a requirement to the same
capability spec, merged cleanly by git — sailed through the structural
lane. The reshaped test pinned the hole as the intended contract, so the
suite was green.

**Why:** a diagnostic's wording and the data it summarises are two
different surfaces. A wording complaint is a complaint about the
projection, not the fact; changing the fact to make the projection read
well is a category error that a green suite cannot catch, because the
test that would have caught it is the one you just rewrote to match. The
signal (a duplicate exists) and the noise (the path is printed twice) got
removed together. Same family as
[[widening-a-value-grammar-needs-a-consumer-census-at-plan-time]]'s
"fixing the symptom removed the signal" — this is the review-fix-time
instance, where the shortcut is one line and looks like tidying.

**How to apply:** when a finding is about how a message READS, the fix
lives in the formatting branch — dedupe, count, or reword AT the print
site, and add a distinct message for the case that produced the odd
wording ("declared N times in <path>" beside "declared in multiple
files: …"). Leave the collected data lossless. Before rewriting a test
that pins the old behaviour, ask what real-world condition the old
assertion was catching; if the answer is "the thing this arc is for",
the fix is wrong, not the test. A message-wording nit that requires
touching a data structure or a loader is a red flag: stop and re-derive
what the diagnostic is protecting.
