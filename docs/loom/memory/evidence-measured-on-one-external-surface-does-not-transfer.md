---
name: evidence-measured-on-one-external-surface-does-not-transfer
description: A key/field name measured on ONE surface of an external library is not evidence about another surface of the same library — a reviewer correctly measured `dim_*` column spellings on edgartools' FACT rows, the fix was applied to its PRESENTATION rows, and the widened match then deleted the top line of every statement that discloses segments
type: gotcha
origin: branch feat-spine-chain-coverage (as-filed statement reconstruction, 2026-07-26) — the `dim` substring widening
---

A predicate rejected a presentation row when any key whose name contained
`dimension` held a truthy value. A reviewer correctly observed that edgartools
spells dimension-bearing columns `dim_srt_ProductOrServiceAxis` — no `dimension`
substring — and recommended widening the match to `dim`. The orchestrator
relayed it as the preferred option; the implementer applied it.

**That evidence came from the FACT-row surface. It was applied to the
PRESENTATION-row surface, which has a different key vocabulary**, and there four
keys contain `dim` in two groups meaning OPPOSITE things:

| key | meaning |
|---|---|
| `is_dimension`, `full_dimension_label`, `dimension_metadata` | this row IS a segment slice |
| `has_dimension_children` | this row is an ordinary CONSOLIDATED line whose slices follow it |

So the widened match rejected every consolidated total. Measured: KO FY2017
income kept 17 of 26 lines, losing `NET OPERATING REVENUES`, `OPERATING INCOME`
and `INCOME BEFORE INCOME TAXES`; DUK FY2017 income kept 18 of 52; Realty Income
FY2025 lost `Total assets`, `Total liabilities` and `Total equity`. Silent
DELETION of a filer's headline figures — and every one of 1230 package tests was
green.

The plan had predicted this presumption would fail OPEN (a leak). It failed
CLOSED. What caught it was a written obligation in the plan requiring the
downstream task to RE-CONFIRM the live row shape rather than inherit an untested
presumption; that task returned BLOCKED with the measurement.

**Why:** a library's surfaces are separate contracts. `facts.to_dataframe()`
columns, `get_statement()` rows and `calculation_trees` nodes are three
vocabularies from one package, and a name measured in one says nothing about the
others. The error is invisible in review because the evidence is real, correctly
cited, and correctly reasoned — only its SCOPE is wrong, and a citation carries
no scope unless someone writes one.

**How to apply:**

1. When citing an external library's field or key name as evidence, name the
   SURFACE it was measured on, not just the library. "edgartools spells it
   `dim_*`" is unscoped; "edgartools' FACT rows spell it `dim_*`" is a fact.
2. Before applying a name-based rule to a surface you have not measured, dump
   that surface's actual keys. One command; it would have shown the four-way
   split immediately.
3. A downstream task that touches a surface an upstream task only presumed about
   must be given an explicit obligation to RE-CONFIRM it. That obligation, not a
   test, is what caught this — write it into the plan's Decision Log where the
   next dispatch packet will carry it.
4. Both failure directions need naming. This entry's plan predicted a leak and
   got a deletion; a prediction of the direction is itself a claim that can be
   wrong, so pin the behaviour, not the prediction.

Related: [[a-shared-helper-can-be-right-in-one-lane-and-destructive-in-another]]
(the same shape one level down — a helper, not evidence, crossing lanes) and
[[importing-a-module-runs-its-module-level-imports]].
