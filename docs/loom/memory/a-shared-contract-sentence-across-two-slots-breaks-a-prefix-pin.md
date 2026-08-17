---
name: a-shared-contract-sentence-across-two-slots-breaks-a-prefix-pin
description: When a second template slot adopts the same contract sentence as an existing slot (fill-or-declare's "Do not delete the section heading …"), a sibling test that pinned only the shared PREFIX with count()==1 breaks on the new slot's legitimate copy — pin the slot-specific continuation of the sentence, and at plan time grep sibling slot pins for shared clause prefixes so the pin file lands in Files touched up front
type: gotcha
origin: branch loom-doc-container (loom-code 0.85.0, 2026-08-17) — Task 2, Decision Log 1
---

The brief's `## Alternatives Considered` became fill-or-declare, reusing
the clause "Do not delete the section heading" that the `## Diagrams` slot
already carried. `test_brief_diagram_slot.py` pinned that bare prefix
with `count()==1` over the whole file; the second slot's verbatim copy
made it 2, and a correct implementation went RED in a test the plan had
not listed. The implementer stopped (BLOCKED) rather than edit an
undeclared file; the fix was to narrow the pin to the Diagrams-specific
continuation ("…and an N/A whose reason does not hold …") — stricter, not
weaker.

**Why:** a prefix pin encodes "this phrase is unique in the file", which
is true only until a sibling slot legitimately reuses the phrase; the
grep-pin discipline (pin the full phrase the failure message names) is
what keeps the pin true across slot additions.

**How to apply:** when pinning a slot's contract sentence, pin the part
that is unique to that slot, not the shared opener; when planning a
second slot that reuses a contract sentence, grep sibling slot pins for
that sentence's prefix and declare the pin file in the task's Files
touched. Related: [[substring-assertions-must-pin-the-phrase-their-message-names]].
