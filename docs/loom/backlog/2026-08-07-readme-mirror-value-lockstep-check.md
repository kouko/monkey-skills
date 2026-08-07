---
name: 2026-08-07-readme-mirror-value-lockstep-check
description: Tri-language README mirrors keep shipping stale counts/versions after English-only sweeps; a lockstep check on shared factual values (version, skill count, agent counts) would make the class unwritable
status: OPEN
origin: arc-1 + arc-2 whole-branch docs reviews (2026-08-07) — the same sweep-miss class gated twice in one day; requesting-docs-review Directive 1's corollary says prefer a standing mechanism over extra review rounds
---

Both complexity-governance arcs hit the same defect class: a factual value
(dimension count, plugin version, skill count, reviewer-agent count) was
corrected in an English surface while its README.ja.md / README.zh-TW.md
mirrors — or a sibling English restatement — kept the old value. Arc-2's
docs review round 2 gated on exactly this (loom-code READMEs split at
v0.23.0/12-skills after the English sweep), and the fix round then missed
a heading-vs-table contradiction the round-3 reviewer caught.

Candidate mechanism (shape, not commitment): a repo-root pin test in the
arc-1 drift-guard family that extracts a small set of shared factual
tokens (version string, "N skills", "N reviewer agents", dimension
counts) from each README trio and asserts the three languages agree —
disagreement names the file and value. Deliberately value-agreement, not
translation-equality: prose may diverge freely; facts may not.

Next step: when the class fires again (third occurrence) or at the next
README-touching arc, build the check per the drift-guard precedent
(scripts/test_*.py, check(root), mutation-catch test) instead of
authorizing more review rounds.
