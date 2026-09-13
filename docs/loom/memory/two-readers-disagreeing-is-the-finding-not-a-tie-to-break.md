---
name: two-readers-disagreeing-is-the-finding-not-a-tie-to-break
description: At the memory-grep wave-end checkpoint one reader ran every suite, found them all green and passed the change, while the other ran nothing, read the new field encoding and found a subject byte that silently dropped a record — the reader who executed the tests was the one who missed the defect, so a split verdict is evidence that the two lenses looked at different things, never a tie to average away
type: practice
sources:
  - resource: 2026-09-06 memory-grep-single-pass (loom-workflow 4.1.0) — wave-end:1 round 1, Codex NEEDS_REVISION versus Claude PASS_WITH_NOTES
---

The review station stores both verdicts whole and takes the worst one; it
does not average. This checkpoint showed why the rule is worth its cost.

Two fresh readers received the same brief over the same delta. One ran
all five pre-existing suites under two shells, the golden suite, the
performance suite and every probe, confirmed 60-plus assertions green,
and returned PASS_WITH_NOTES. The other could not run anything — its
sandbox was read-only and fixture creation failed — so it read the code
instead, asked which byte the new field separator could collide with, and
returned NEEDS_REVISION naming a commit subject containing 0x1F. That
input made the record disappear with exit code 0. Reproduced in one
minute; the passing reader's whole green suite had never held that shape.

The two readers overlapped on exactly one finding, and each found it
independently: production code had been reshaped to satisfy a defective
test harness. Everything else was disjoint. Six findings were opened, all
six fixed, none dismissed — and the check added for one of them
immediately exposed a second latent bug in a test fixture that had been
quietly producing 19 of the 20 records it claimed.

**What holds now:** when two readers disagree, do not look for which one
is right. Read what each one did: an inability to execute is not a weaker
review, and a full green suite is not a stronger one. Record both
verdicts, open every finding, and let the fix round settle it. See
[[a-rewrite-that-promises-byte-identical-output-needs-an-oracle-built-from-the-old-code-first]]
for the oracle that produced the green the passing reader trusted.
