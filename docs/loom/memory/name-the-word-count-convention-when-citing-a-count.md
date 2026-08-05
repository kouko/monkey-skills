---
name: name-the-word-count-convention-when-citing-a-count
description: Two live word-count conventions (`wc -w` and Python `len(text.split())`) can differ by 1 on the same file — a document citing a count without naming its convention reads as contradicting a sibling document that used the other one, and the phantom off-by-one costs real review rounds; name the convention next to the number, and use the pin-test convention when a pin test governs the file
type: practice
origin: 2026-08-05 extraction-batch arc (4119 vs 4118 on requesting-docs-review/SKILL.md, two reviewer findings + a Decision Log erratum)
---

During the 0.55.0 extraction batch, the same file measured 4119 words
by `wc -w` and 4118 by `len(text.split())`. Two documents on the
branch cited the two different numbers without naming their
conventions; two reviewer arms independently flagged the "wrong"
number as an arithmetic defect, and settling it took a Decision Log
clarification naming both conventions.

**Why:** the two counters split tokens differently in edge cases, so
both numbers are simultaneously correct — but a bare number carries no
convention, and a reader (human or reviewer agent) comparing two bare
numbers sees a contradiction, not a convention mismatch.

**How to apply:** any document citing a word count states the
convention once next to the number or in a Notes line ("counted by
`len(text.split())`"). When a pin test governs the file's ceiling, cite
in the pin test's convention — the test is the enforcement surface, so
its number is the one that gates. Forward-only: fix bare counts on
next touch, no retrofit sweep.
