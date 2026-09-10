---
name: measure-a-checks-fire-rate-before-building-it
description: Before building a mechanical check, run its naive form over the existing corpus and count how often it fires — the measurement is cheaper than the build and can kill the design; a signal that fires on most instances is a notifier rather than a gate, and a defect class that is not deterministically decidable at all is answered by removing the category of claim from the format contract instead of by a detector
type: practice
sources:
  - resource: the docs-review mechanism arc (2026-08-04), where the same measurement was run twice in one session and returned opposite verdicts
---

A proposed check arrives already justified: a real defect shipped, and the
check would have caught it. That argument establishes the check's *recall*
on one instance and says nothing about how often it fires on everything
else. The corpus is already on disk and git already has the history, so
the fire rate is measurable before a line is written.

Both halves of the rule were exercised in one session, from the same
motivating defect:

- **A memory entry's `description` contradicted its own body.** The
  proposed check was "the body changed and the description did not."
  Measured over every commit touching the store: 20 body edits to
  existing entries, 12 with no description change. A 60% fire rate is
  not a gate. The design died at the measurement, unbuilt.
- **A doc claimed a CLI flag the script does not have.** Naive form:
  729 doc lines pairing a script with a flag, 84 apparent misses. After
  excluding argparse-generated flags (`--help`, `--version`), flags
  belonging to the runner rather than the script (`--no-project`), and
  frozen document trees, it fell to 10 of 407. That is a gate.

**Why:** the expensive failure is not a check that misses — it is a
check that fires constantly, gets muted, and thereafter provides
false assurance while costing a step in every close-out. Recall is
argued from the motivating instance; precision can only be measured,
and only against the corpus the check will actually run on.

The second half matters just as much. When the measurement shows the
signal is noise *because the underlying question is semantic* — does
this sentence contradict that one — no threshold rescues it: the class
is not deterministically decidable. The move then is not a better
detector but the format contract: forbid the kind of claim that goes
stale, so the defect cannot be written. Prevention by construction has
no false-positive rate at all.

**How to apply:** before building a check, write the throwaway naive
version and run it over the repo (and, where the defect is drift, over
`git log`). Report three numbers — instances examined, times fired,
times fired correctly on a spot-check. If it fires on most instances,
do not build it as a gate; either narrow it until the rate drops or say
plainly that the class is not mechanizable and move the fix to the
contract that lets the claim be written. Record the measurement whether
it kills the design or clears it — the killed one is the finding that
stops it being re-proposed.
