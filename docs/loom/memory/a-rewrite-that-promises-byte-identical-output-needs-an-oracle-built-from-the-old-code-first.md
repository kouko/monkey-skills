---
name: a-rewrite-that-promises-byte-identical-output-needs-an-oracle-built-from-the-old-code-first
description: The memory-grep single-pass rewrite promised byte-identical output; the first task built a golden oracle by running the PRE-change script over one fixture and freezing its six outputs, and every later task diffed against those goldens — yet a reviewer still found a shape the fixture never held (a subject containing 0x1F) that the new code silently dropped, so the oracle is the floor a rewrite starts from and never the proof it finished
type: practice
origin: 2026-09-06 memory-grep-single-pass (loom-workflow 4.1.0) — W1-01 built the goldens, wave-end round 1 found the gap the goldens could not see
---

A rewrite whose contract is "the output does not change" has an obvious
test available before a single line moves: run the old code, keep what it
printed, and diff every later version against it. `memory-grep.sh` did
this as its own first task — one deterministic fixture repository (fixed
identity, fixed commit dates, so short hashes are stable), six
invocations covering the option matrix, the six outputs and their exit
codes committed as golden files whose first line names the commit that
generated them. Each of the two rewrite tasks then ran against those
goldens at every step, and both reported them green.

The goldens were not enough. A reviewer reading the new field encoding
asked what byte the separator could collide with, and found that a commit
subject containing 0x1F made the record vanish — exit code 0, no warning,
one fewer memory in the digest. The fixture had hostile bytes in trailer
*values* but never in a *subject*, so every golden passed while the
regression was live. The fix replaced the separator with NUL, the one
byte a commit message provably cannot contain, and the regression test
now runs the pre-change script from git history and compares the two
byte for byte.

**What holds now:** build the oracle from the old code before the rewrite
starts — it catches the ordinary mistakes cheaply and lets the rewriting
agent move fast. Then treat its green as a floor, not a verdict: ask
separately, for each field the new code parses, which byte or shape would
break it, and whether the fixture holds one. A golden suite proves the
inputs you thought of still work. See
[[two-readers-disagreeing-is-the-finding-not-a-tie-to-break]] for who
asked the question the goldens could not.
