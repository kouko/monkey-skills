---
name: a-test-can-pin-behaviour-with-a-false-rationale
description: A test can assert exactly what the code does, fail honestly if that changes, and still be wrong — when its stated REASON for the behaviour is false and the production scope was designed from that reason. The assertion is not vacuous, so every "would this fail if the property broke?" check passes; what nobody checks is whether the property is the right size. Read a guard's justification as a claim to verify, not as context — and verify it on every axis the boundary depends on, because a one-axis probe re-introduces the same error pointing the other way.
type: gotcha
origin: company total (top-line) revenue arc (branch feat-total-revenue-lane, investing-toolkit 2.36.0, 2026-07-25) — found by whole-branch review after eleven per-task review triads passed it
---

The top-line backfill lane skips any annual row whose period end sits near
Jan 1, because it has no fiscal calendar and must not guess a fiscal-year
label. The guard was written symmetrically — proximity to Jan 1 measured on
BOTH sides — and a test pinned exactly that, with this rationale:

> both inside the tolerance of Jan 1, on either side of it, where Lane A's
> period-end-year rule is unsound

The assertion was honest: remove the guard and the test goes red. It is not
vacuous, not construction-guaranteed, not count-only. It would have caught a
real regression. Every "would this fail if the claimed property broke?" audit
passes on it.

**The rationale was false on one side.** The consumer lane's label function
walks to the first nominal fiscal-year end at-or-after the period end, so for
a December year-end it returns the period end's own calendar year — the exact
label the producer lane derives. The two rules AGREE there. Only a year-end
that has crossed INTO January diverges. Measured directly:

```
period_end     producer label   consumer label   agree?   skipped?
2025-12-27     2025             2025             True     True     <- over-broad
2024-12-31     2024             2024             True     True     <- over-broad
2026-01-03     2026             2025             False    True     <- correct
```

That table is correct and it is also the second half of this lesson: it
varies ONE variable. See "The one-axis probe", below.

Because the guard's SCOPE was designed from the false half of the rationale,
every December-fiscal-year-end filer — most of the US market — had its entire
backfill silently skipped, while the brief, the CHANGELOG and two skill
surfaces all described the lane as the general history backfill. Nothing
disclosed the gap, and the test read as proof that the behaviour was intended.

**Why this survives review that catches vacuous assertions:** the two defects
look identical from the outside — a green test next to production code — but
they fail different audits. A vacuous assertion fails "would this fail if the
property broke?". This one passes that audit and fails a question almost
nobody asks: *is the property the right size?* Per-task review cannot ask it,
because the task's spec inherited the same false premise; the test and the
code agree, and agreement reads as correctness. It took a whole-branch reviewer
that treated the docstring's justification as a claim to verify rather than as
context to trust.

**The one-axis probe — how the fix went wrong in the other direction.** The
guard was re-narrowed to fire only after Jan 1, verified by the table above,
and shipped. A whole-branch re-review then found a second, narrower gap the
new guard misses. The probe was sound about the axis it varied — `period_end`
— and silent about the axis it held fixed: the filing's *nominal* fiscal-year
end, which the same module documents as DRIFTING per filing for 52/53-week
filers. The consumer's label depends on BOTH. Varying both:

```
period_end   nominal FYE   producer   consumer   agree?   guard fires?
2025-12-27   --12-27       2025       2025 FY    True     False   <- correct
2026-01-03   --12-28       2026       2025 FY    False    True    <- correct
2024-12-28   --01-03       2024       2025 FY    False    False   <- MISSED
2025-12-31   --01-02       2025       2026 FY    False    False   <- MISSED
```

The old symmetric guard caught those two by accident, so the fix traded a
large over-broad gap for a small silent one. Both the original defect and
this one are the same error at different scales: a boundary judged on fewer
axes than the boundary actually has. A one-variable probe cannot tell
"asymmetric hazard" from "asymmetric along the one axis I happened to vary",
and it returns a confident-looking table either way.

**How to apply:**
1. When a guard's docstring explains WHY it fires, treat that explanation as a
   claim under review, not as background. Ask what the world looks like on each
   side of the boundary it describes, and check whether the hazard actually
   exists on both.
2. Before trusting that check, enumerate every variable the boundary's
   correctness depends on — then vary ALL of them, not just the one the guard
   takes as its argument. The inputs a predicate RECEIVES are not the inputs
   its correctness DEPENDS ON; here the guard took `period_end` while the
   divergence it approximates was a function of `period_end` AND the nominal
   year-end. A probe that holds an axis fixed has assumed that axis is
   irrelevant — which is the claim under test, so state it out loud and check
   it rather than encoding it silently in the fixture.
3. A symmetric guard for an asymmetric hazard is the specific shape to hunt.
   Boundary conditions phrased as "near X" or "within tolerance of X" are where
   it hides — proximity is symmetric by default, hazards frequently are not.
   Hunt the mirror too: a guard narrowed to one side on a one-axis probe is how
   the SAME error re-enters pointing the other way.
4. Cheap discriminator: pin the NEGATIVE case too. A test asserting the guard
   does NOT fire on the side where the hazard is absent would have failed
   immediately and forced the question. A guard pinned only in the firing
   direction can be any size and still look right.
5. When a feature's stated coverage and its actual coverage diverge silently,
   the cost is not a wrong value — it is an absent one, which no
   anti-fabrication floor catches. Check what a capability returns for the
   COMMON case, not only for the edge case the guard was written for.

Relates to [[assertion-must-encode-the-property-it-claims]] (the vacuous-
assertion sibling this is distinct from — there the assertion proves nothing;
here it proves something true about the wrong-sized behaviour) and
[[construction-guaranteed-invariant-proves-nothing]].
