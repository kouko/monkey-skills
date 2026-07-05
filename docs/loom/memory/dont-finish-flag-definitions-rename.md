---
name: dont-finish-flag-definitions-rename
description: The "Flag Definitions" heading in domain-teams rubrics is a deliberate convention — do not sweep it into the loom-code flags→findings rename
type: practice
origin: PR #468 (loom-* suite audit batch 1, 2026-07-02)
---

loom-code renamed its review vocabulary from "flags" to "findings"
(PR #468). The rubric-layer heading **"Flag Definitions"** was
deliberately KEPT: it is the gate-system convention of the
`domain-teams` plugin, used across 20+ rubric files there. It is not
a leftover — "finishing" the rename there would break a different
subsystem's own naming convention.

**Why:** a vocabulary sweep that looks incomplete invites a future
cleanup pass; without this guard, someone greps for the old word,
finds "Flag Definitions", and renames a convention 20+ files depend
on.

**How to apply:** when sweeping a rename and an apparent survivor
turns up, check whether it belongs to another subsystem's own
convention before touching it. Leave "Flag Definitions" in
domain-teams rubrics as-is.
