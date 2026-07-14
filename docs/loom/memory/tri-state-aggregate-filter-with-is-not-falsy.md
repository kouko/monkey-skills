---
name: tri-state-aggregate-filter-with-is-not-falsy
description: When a check returns a TRI-STATE result (pass / fail / not-applicable, e.g. True/False/None), an aggregate that collects failures MUST filter with `is False` (or `is True`), never a falsy test — `if not result` / `if not passed` silently miscounts the N/A (None) state as a failure. Pin it with a test that would FAIL under the wrong (falsy) filter.
type: gotcha
origin: 2026-07-14 session — investing-toolkit analysis-kpi slice 4 (kpi_validate.validate aggregating tri-state rule checks)
---

`kpi_validate.py`'s four rule checks each return `{"rule", "passed", "detail"}`
where `passed` is TRI-STATE: `True` (rule satisfied), `False` (real violation),
or `None` (N/A — the constraint doesn't apply: no declared unit, no segments to
sum, a non-GAAP metric with no GAAP obligation). `validate` aggregates them:

```python
failures = [r for r in results if r["passed"] is False]   # correct
eligible = len(failures) == 0
```

Writing the filter as `if not r["passed"]` (or `if not passed`) would be a
silent, dangerous bug: `None` is falsy in Python, so every N/A rule would be
counted as a FAILURE — a value would be wrongly rejected (and, in a fail-closed
pipeline, needlessly withheld or sent to human review) just because a rule
didn't apply to it.

**Why:** a tri-state's whole point is that "not applicable" ≠ "failed". A falsy
test collapses `None` and `False` together, destroying that distinction; the bug
is invisible until a value hits the N/A branch.

**How to apply:** aggregate a tri-state by identity — `is False` / `is True` /
`is None` — never a bare truthiness test. And PIN it: write a test where an
applicable-but-N/A rule (e.g. a record with no segments → subtotal `None`)
asserts the item stays eligible with empty failures — that test passes under
`is False` and FAILS under a falsy filter, so it guards the exact hazard (the
same "assertion must encode the property" discipline as
[[assertion-must-encode-the-property-it-claims]]).
