---
name: absence-pin-fix-recurred-in-files-authored-after-the-fix
description: Grep absence pins must compare lowercased-both-sides — case-sensitive pins false-pass on a capitalization-only revival; and a pin-bug fix does NOT stop recurrence, because new test files are written by copying the nearest sibling (which may predate the fix) — the fix must travel in the dispatch packet, not just in the repo
type: practice
origin: feat-copywriting-convergence-modernization (copywriting-toolkit 1.15.0, 2026-07-30) — same bug class fixed three separate times in one arc (7f13682c, 0e85e073, bf1b3dcc)
---

An absence pin like `assert PHRASE not in text` guards against a retired rule
or a restated canonical definition coming back. Case-sensitive substring
comparison false-passes when the revival differs only in capitalization
(sentence-initial "Qualitative observation…" vs the pinned lowercase). The fix
is one line — `assert PHRASE.lower() not in text.lower()` — but in this arc it
had to be applied THREE times: the reviewer-flagged file (7f13682c), then two
siblings carrying the identical pin that no reviewer had looked at (0e85e073,
caught only by the whole-branch sweep), then a brand-new test file authored
AFTER both fixes landed (bf1b3dcc) — its author copied the pattern from a
pre-fix sibling.

**Why:** implementers write new tests by imitating the nearest existing test
file, so a repaired bug class keeps re-entering through un-repaired copies and
through dispatch packets that don't carry the lesson. Repo state converges;
the generative pattern doesn't, unless told.

**How to apply:** (1) absence pins always lowercase both sides; presence pins
stay exact. (2) When a review fixes a *pattern* bug in one test file, grep the
sibling test files for the same pattern in the same commit — the reviewer only
looked where the dispatch pointed. (3) Add the repaired pattern to every later
implementer dispatch packet in the same arc ("absence pins: lowercase both
sides") — the packet, not the repo, is what the next author actually reads.
Related: [[verbatim-phrase-guards-break-on-hard-line-wrap]].
