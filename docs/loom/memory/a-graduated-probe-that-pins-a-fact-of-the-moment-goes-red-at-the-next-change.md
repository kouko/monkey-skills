---
name: a-graduated-probe-that-pins-a-fact-of-the-moment-goes-red-at-the-next-change
description: Three changes in a row (#794, #795, this one) graduated a probe that pinned a fact true only while its branch existed — the intent-confirmation commit found by subject, the live plugin version, a dispatch-commit count with the round number hardcoded — and each went red on main or on the next branch; a graduated probe recomputes what grows (rounds, waves, versions) and skips with a reason when its branch history is gone, the way the language-policy probes already did
type: gotcha
sources:
  - resource: 2026-09-05 user-declared-express-lane (loom-code 1.6.0) — the W1-03 implementer hit the red on a fresh branch, the other session hit it on main and fixed the copy without the original, this change re-synced the pair
---

A probe under `evidence/` is written against one branch at one moment,
and graduation copies it into the permanent suite unchanged. Anything the
probe learned from that moment — a commit it finds by subject, the version
string of the day, the number of rounds so far — is a fact of the branch,
not of the repository, and the squash merge or the next checkpoint erases
it. The probe then fails where nobody is watching for it: on `main`, in
CI, or on the next change's first package run.

**What holds now:** a probe that reads a growing quantity recomputes it
from the record (`review.json`, `git log --grep`) at run time; a probe
that needs its own branch's history skips with a reason naming the change
when that history is absent; a probe that pins a version pins the
changelog heading, never the live plugin file. The graduated copy stays a
byte copy of the evidence original (path line aside), so a fix lands in
both or in neither.

**How to apply:** before graduating, read every literal in the probe and
ask which branch-moment it belongs to; if it belongs to this branch, make
it a lookup or a skip.

Related: [[one-record-commit-per-wave-and-per-round-keeps-the-record-honest-and-the-log-short]],
[[a-gate-that-binds-records-to-commit-ids-taxes-every-bookkeeping-commit]].
