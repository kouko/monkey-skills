---
name: a-cross-field-check-over-a-bitemporal-store-must-pin-one-vintage
description: A check that relates several stored fields (an accounting identity, a ratio, a sum) must read them all from ONE vintage — taking each field's own latest silently compares across filings whenever one field was restated more often than another, and reports the store working correctly as if it were an error; 4 of 6 live filers false-flagged this way, one by 5.7% on a period that balances to the dollar inside its own filing
type: gotcha
origin: US as-reported statement lane (feat-us-as-reported-statement-lane, investing-toolkit 2.38.0, 2026-07-26) — found by the live dogfood; invisible to 1165 green tests
---

A bitemporal store keeps every vintage: a restatement APPENDS a record rather
than overwriting, which is the property that makes the store an analysis
substrate instead of a snapshot. A cross-field check written against it will
reach for each field's `latest` because that is what a reader sees — and that
is the bug. Fields are not restated in lockstep.

Measured, Microsoft at 2016-06-30:

```
Assets       filed 2016-07-28  193,694,000,000
             filed 2017-08-02  193,468,000,000   <- latest
Liabilities  filed 2016-07-28  121,697,000,000
             filed 2017-08-02  121,471,000,000   <- latest
Equity       filed 2016-07-28   71,997,000,000
             filed 2017-08-02   71,997,000,000
             filed 2018-08-03   83,090,000,000   <- latest
```

The identity computed `193,468 − (121,471 + 83,090)` and reported a 5.7%
residual. But `193,468 = 121,471 + 71,997` — the 2017 filing balances
exactly. Equity simply carried one more vintage than the other two, so the
check compared a 2017-filed asset figure against a 2018-filed equity figure.
Four of six dogfooded filers flagged; every one was this shape. The check
whose job is to catch a wrong number was instead reporting the store's
correct behaviour as an error.

**Why nothing caught it.** Every unit fixture had one vintage per field,
because that is what a hand-built fixture naturally has — the defect needs a
field restated more times than its neighbours, which is a property of real
filing history, not of a plausible test payload.

**How to apply:** a check spanning multiple stored fields picks the VINTAGE
first and reads every term out of it, never the other way round. Concretely:
intersect the `(as_of, source_accession)` pairs the required fields carry,
take the newest pair present in all of them, and read every term — including
the optional ones — from that pair alone. A period no single vintage covers
is UNCHECKABLE, not failing; silence there is correct, the same way it is for
a field the filer never reported.

Two consequences worth designing for rather than discovering:

1. **Name the vintage in the output.** The checked figures will differ from
   the `latest` a renderer shows for the same period whenever that period was
   restated. That is reconcilable only if the check says which filing it read,
   so naming it is load-bearing, not cosmetic.
2. **"Absent reads as zero" must mean absent from the PERIOD, not from the
   chosen vintage.** If another filing tagged the optional term at that
   instant, the instant demonstrably had one, and the chosen filing merely not
   carrying it is a MISSING amount — go uncheckable. Cross-vintage evidence
   may only ever widen uncheckability; no number entering the arithmetic may
   come from outside the chosen vintage, or the fix reintroduces the mixing it
   was written to remove.

Relates to [[a-data-probe-is-not-a-pipeline-dogfood]] (only a live run over
real filing history exposes it) and [[falsy-guard-rejects-legitimate-zero-provenance]]
(same family: a guard that is right about the common case and wrong about the
case the data actually contains).
