---
name: 2026-08-13-a-brief-item-can-name-a-mechanism-with-no-observable-consequence
description: nothing requires a Smallest End State item to state an observable difference, so an item can name an internal mechanism instead — one shipped this arc that was specified, implemented, tested and released while having no effect any output could distinguish
status: open
origin: brief-item-addressability arc (2026-08-13) — "coverage is the union of citing tasks" survived brief, plan, implementation, per-task review and release before mutation testing showed the union was unobservable
start: next touch of brainstorming's handoff-brief-format.md, or the next arc whose Smallest End State contains an item phrased as a data structure or algorithm
---

One of the arc's Smallest End State items read: coverage of a brief item is
the **union** of the tasks citing it. It was implemented as a union, tested,
reviewed per task, and released.

Whole-branch review then ran a mutation: replace the accumulating `add` with a
last-write-wins assignment. **All tests stayed green** — and not because the
assertions were weak. The union was *genuinely unobservable*: the sole
consumer only ever asks whether the set is empty, so "union of citing tasks"
and "at least one citing task" produce byte-identical output on every input.

Nobody had asked the one-sentence question that dissolves the item: **what
would a user see differently if this were not a union?** Nothing. The feature
had no behavioural content.

**Why every existing gate passed it.** The item is not vague — "union" is
precise. It is not unimplemented — the code really did compute a union. It is
not untested — tests exercised it. Plan review checks that every brief item
maps to a task, which it did. The one-failing-test criterion is satisfied by a
test that passes for the wrong reason. What no gate asks is whether the item
names an OUTCOME or a MECHANISM, and a mechanism can be delivered perfectly
while delivering nothing.

**Candidate rule.** In `handoff-brief-format.md`, require each Smallest End
State item to be phrased so that its negation names a visible difference:
every item must survive the test *"if this item were not delivered, what
would a reader of the output see instead?"* An item whose honest answer is
"nothing" is a mechanism and must be rewritten as the outcome it serves, or
dropped.

Two cautions before adopting:

- This is an authoring rule about phrasing, and this repo has repeated
  evidence that prose rules requiring **judgment** fail on weak executors
  while prose rules pointing at a **verifiable action** hold. "Is this an
  outcome or a mechanism?" is judgment-shaped. The rule may need a mechanical
  companion — e.g. requiring each item to carry the observable it changes, so
  the missing observable is a blank field rather than a bad sentence.
- It interacts with legitimate mechanism items. A brief item may deliberately
  name an internal structure when the arc's whole point is that structure
  (a refactor, a data-model change). The rule must not force those to be
  laundered into fake user-facing language — the honest form there is "no
  output changes; the observable is X test/API surface".

Related: [[2026-08-13-a-widened-field-grammar-has-no-mechanical-consumer-enumeration]]
and [[2026-08-13-a-plan-can-dispatch-a-task-whose-acceptance-depends-on-an-unresolved-open-question]]
— the same arc's other two plan-time proposals; all three were surfaced by
whole-branch review finding what per-task review structurally could not.
