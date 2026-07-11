# Brief: replay-matrix stage-throw guard (single atomic task)

- Date: 2026-07-11
- Source: BACKLOG harness entry next-touch candidate (1), evidenced by the
  #534 committed baseline: in 2 of 3 matrix runs one seed's grade courier
  failed schema-forced output, the stage THREW, and `pipeline()` dropped
  that seed's row to null — the existing `if (!g)` null-guard only covers
  `agent()` RETURNING null, not the stage throwing. Grading had to be
  recovered manually on disk both times.

## Smallest end state

`.claude/workflows/principles-replay-matrix.js`: both pipeline stages
(Replay, Grade) wrap their body in try/catch; a caught stage error returns
the same degraded failed-row shape as the existing null-guards, with
`misses: ['<stage>: stage error — <message>']`, so a single seed's courier
failure can never silently remove that seed from the pass table. Static
test pins the catch presence. Single module, one failing test — this brief
IS the plan per writing-plans §When NOT to Use (brief explicitly single
atomic task); SDD triad not triggered (<1 module boundary, well under an
hour); implementer dispatch under tdd-iron-law + whole-branch review at
close-out.

## Companion decision — anchor first-cell precision: DEFER

The sibling BACKLOG candidate (restrict anchor match to the first cell)
is deliberately NOT built: whole-row matching has both a reproduced false
NEGATIVE (r3 `Qt` via the HIG row's version-cell prose) and a legitimate
true positive that first-cell-only would break (r1 seed4's
`| Technology Stack | C++ 17+ …, Qt 6 … |` row anchors the stack in the
VERSION cell). n=1 observed false-negative, under-report-only, and no
mechanical rule cleanly separates the two shapes yet — revisit when L1
data shows drop-signal distortion attributable to it. BACKLOG updated in
this branch to record the DEFER + reason.

## Acceptance

- Static tests pin: try/catch present in both stages; degraded-row error
  string present; existing null-guards untouched; no Date.now/Math.random.
- Full suite green; BACKLOG candidate (1) discharged, candidate (2)
  rewritten as DEFER with reason.
