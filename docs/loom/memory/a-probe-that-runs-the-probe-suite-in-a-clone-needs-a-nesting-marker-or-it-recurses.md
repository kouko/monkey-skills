---
name: a-probe-that-runs-the-probe-suite-in-a-clone-needs-a-nesting-marker-or-it-recurses
description: A probe that clones the repository and runs every graduated probe file inside the clone runs its own graduated copy there, which clones again without end (40 nested rehearsals before the tree was killed); both the rehearsal script and such a probe set `REHEARSE_PROBES_NESTED` to the clone's own absolute path for the pytest they spawn, the probe skips only when it finds itself inside that path (a marker naming some other path is ignored; a bare non-path value still skips, loudly, naming itself), and a classifier that reads skip lines matches the reason only, because the probe's own filename carried the word it was hunting for
type: gotcha
sources:
  - resource: 2026-09-05-graduated-probes-independent-of-local-history — memory step (2026-09-06), the first rehearsal after graduation
---

The clone-and-run probe was green all through wave 1 because its
graduated copy did not exist yet. The moment it was copied into
`loom-code/scripts/test_probes_rehearsal_*.py`, the rehearsal ran it,
it cloned the repository, ran the probe files in the clone, met its own
copy, cloned again — the working tree's shell showed 40
`rehearse_probes.py` processes and five clone directories before the
tree was killed. The 600 s tool timeout, not any assertion, was what
surfaced it.

Two changes closed it:

- The rehearsal script and the probe both run their inner pytest with
  `REHEARSE_PROBES_NESTED=<absolute clone path>` in the environment; the
  probe skips only when its own location resolves inside that path, with
  a reason that names the marker and the path — a marker naming some
  other path is ignored, while a bare non-path value (the marker's
  first shape) still skips and says so (branch-end adversary nit, and
  the adversary probe that pins the bare-value case). One skip therefore always appears in a rehearsal's SKIPPED list —
  the guard, by design, not a history-bound skip.
- The probe classifies a `-rs` skip line by its **reason**, the text
  after `<path>:<line>: `, never by the whole line: its own filename
  contains `history`, so the whole-line match flagged the guard's skip
  as history-bound.

Rule: a probe that spawns the suite it belongs to marks the spawn and
skips on the mark; a rehearsal is not a fixed point without it.

Related: [[a-graduated-probe-that-clones-the-repo-asserts-the-subprocess-exit-code]],
[[pre-branch-end-ci-rehearsal-uses-full-history-without-a-local-main]].
