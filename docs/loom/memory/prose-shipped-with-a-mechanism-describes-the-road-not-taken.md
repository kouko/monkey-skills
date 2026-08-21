---
name: prose-shipped-with-a-mechanism-describes-the-road-not-taken
description: Prose authored in the SAME commit as the mechanism it describes reliably overstates it — the author writes what the mechanism was FOR while a reader can only see what it DOES, so the sentence records the design the commit rejected, the guarantee it aimed at, or the count it had before the last edit; no round of review catches its own overclaim, and the cheap fix is to write the description in a SECOND commit, reading the already-finished code
type: practice
origin: north-star-serves-link / dissolve-direction-layer (2026-08-21) — four separate whole-branch review rounds (5, 6, 7, 8) each found this class in a different sentence, three of them inside the hunk that had just been written to fix the previous instance
---

Four instances on one branch, each caught by a reviewer and none by the
author:

| The sentence shipped | What shipped |
|---|---|
| "This is the ONE home of the out-of-vocabulary guard" | Four copies of the walk |
| "Validate EVERY entry, archive tier included" | The commit's own design call was live-entries-only — the comment described the REJECTED alternative, three lines above the function that says so |
| "a completeness leg that fails when a script grows a read" | It did not; a reviewer injected a bare read and the suite stayed green |
| "three exempt scripts are leaky by the contract's own metric" | Fourteen — measured before the same commit widened the recogniser, never re-run |

The last one is the sharpest: it was written INTO the backlog entry filed
to be the honest debt ledger for the third one.

**Why:** the author of a mechanism has its purpose in working memory and
writes that down. The reader has only the artifact. Between intent and
artifact sits everything the commit tried, narrowed, or deferred — and the
sentence, written at the moment intent is loudest, records intent. This is
not carelessness about wording; every one of these sentences was written
carefully. Round 7's reviewer named the tell precisely: *"my own decisive
finding came from running an injection, not from reading the AST code,
which reads plausibly."* Plausible is exactly what intent-shaped prose is.

**How to apply:** when a commit ships a mechanism AND prose describing it,
split them. Write the mechanism, commit it, then write the description
while reading the finished code rather than the intent. Where that is
impractical, the mechanical substitutes that caught these four are:
recompute any COUNT with a test (see
[[a-number-in-prose-needs-a-test-that-recomputes-it]]), turn any existence
claim ("filed as backlog work") into a path a checker resolves, and treat
every load-bearing superlative — *the one*, *every*, *always*, *only* — as
requiring a pin before it may ship. Changing a function's contract obliges
grepping the file for every sentence naming it; two of these four were
stale pointers at a callee whose contract moved in the same commit. See
also [[a-bounded-check-must-state-its-bound]].
