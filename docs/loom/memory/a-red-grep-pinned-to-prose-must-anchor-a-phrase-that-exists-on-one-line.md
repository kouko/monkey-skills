---
name: a-red-grep-pinned-to-prose-must-anchor-a-phrase-that-exists-on-one-line
description: A plan's RED/GREEN grep against prose files fails silently when the pinned phrase is soft-wrapped across lines or exists only as close variants — before pinning, run the exact grep against the live file and anchor to a phrase that occurs on ONE line with the expected count (n=2 - arc-3 Task 5's unsatisfiable RED, arc-4b plan round-1's zero-count RED)
type: process
origin: loom arc 3 (Task 5 RED grep unsatisfiable, phrase soft-wrapped; plan Amendment log 2026-08-07) + loom arc 4b (plan round-1 🔴 — RED pinned "same shape as its Step 8 siblings", 0 single-line occurrences vs 3 wording variants, 2026-08-07)
---

Markdown prose in this repo is hard-wrapped near 72-80 columns, so a
phrase that reads as one sentence usually spans lines in the raw file.
A `grep -c "<phrase>"` acceptance criterion written from memory of the
RENDERED text can be unsatisfiable (count 0) before any work starts —
which makes the RED never red and the GREEN vacuously green, zero
discriminating power. Sibling trap: near-variants ("same as" vs "same
shape as") make a composite quote grep 0 even when each variant exists.

**Why:** the grep runs against raw bytes, not rendered prose; a plan
author quotes rendered meaning. The two diverge exactly at line wraps
and wording variants — the places a reviewer without file access cannot
see.

**How to apply:** before writing any grep-based RED/GREEN into a plan,
run that exact grep against the live file and paste the observed count
into the criterion ("returns 5 at :187/:195/:215/:226/:258"). Anchor to
a phrase that verifiably occurs on one line; if the target text is
wrapped, either pick a shorter within-line fragment or normalize
whitespace in the check. When a collapse/extraction moves wrapped prose
into single-line carriers (table cells), state which floor strings were
unwrapped so raw greps flip from 0 to 1 by design.
