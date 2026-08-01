---
name: 2026-07-06-goal-oriented-firing-corpus-expected-narrower-than-design
description: Goal-oriented firing-corpus `expected` narrower than design
status: OPEN
origin: PR #489 residual; transcript-check requirement documented as trap #6 in the loom-code/scripts/loom_firing_harness.py module docstring
start: next reuse of docs/loom/firing-corpus/goal-oriented.jsonl, or next firing-harness touch
---

- Start: next reuse of docs/loom/firing-corpus/goal-oriented.jsonl, or
  next firing-harness touch
- Origin: PR #489 residual; transcript-check requirement documented as
  trap #6 in the loom-code/scripts/loom_firing_harness.py module
  docstring
- What: every goal-oriented record expects `loom-code:using-loom-code`,
  so fired-skill grading alone cannot catch a design-side on-ramp
  regression (deleting brainstorming's Axis 0 would not move a single
  record off EXACT/FAMILY). The corpus's real acceptance criterion —
  whether the design-side recommendation SURFACES in the transcript —
  is not automated; any reuse must run the F3-style transcript check,
  or the corpus needs `expected` widened to the design-sanctioned set.
