---
name: a-spy-that-also-simulates-must-record-before-it-branches
description: A test double that both RECORDS calls and SIMULATES a branch must append to its ledger before the branch, not after — putting an early return above the append silently stopped recording the one call the assertion was watching for, leaving `attempted == [good]` green while the guard under test was deleted and the boundary really was reached
type: gotcha
sources:
  - resource: feat-us-quarterly-statement-series (US quarterly three-statement series arc, round-4 whole-branch review, 2026-08-07)
---

A test pins three properties in its own name: a row with no accession is
**recorded**, **never attempted**, **never dropped**. "Never attempted" is checked
by a spy:

```python
def _fake_acquire(accession):
    if accession is None:          # simulate the real boundary
        return {"error": ..., "error_class": "resolution"}
    attempted.append(accession)    # <-- ledger written AFTER the branch
    return acquired
...
assert attempted == [good]
```

The stub was correct about production: `_acquire_raw_filing` really does return a
slot for `None` rather than raising. But putting the simulation **above** the
append meant a `None` call could no longer be recorded — so `attempted` stopped
being a ledger of calls and became a ledger of *non-None* calls.

**Measured consequence.** With the production guard deleted, stderr showed the
boundary being reached — `[pack-us] pack [acquire]: None` — and
`assert attempted == [good]` **passed**. One of the three properties the test is
named for was held by nothing. Moving `attempted.append(accession)` above the
branch makes the same mutant fail with the true message, and leaves the full suite
green (1532 passed) in both directions.

**Why it is easy to write.** The early return reads like a guard clause, and guard
clauses belong at the top of a function. That instinct is right for production code
and wrong for a double whose *first* responsibility is observation. The double has
two jobs and they have a required order: **observe, then simulate**.

**What to do**

- In any test double, put every recording side effect at the very top, before any
  branch, early return, or raise. If the double can return without recording, the
  assertion downstream is conditional on the path — which is exactly the path the
  test usually exists to forbid.
- When you change a double's control flow to match a production change, re-run the
  mutation the test exists to kill. Behaviour fidelity and observability are
  separate properties; fixing the first can silently break the second, and the
  suite stays green because nothing else reads that ledger.

Related: [[a-test-can-be-correct-and-still-unable-to-fail]] (same end state,
reached through inputs rather than through the double), [[a-no-mutation-test-cannot-baseline-off-shared-fixture-state]].
