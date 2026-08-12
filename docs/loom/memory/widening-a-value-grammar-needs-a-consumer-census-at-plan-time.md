---
name: widening-a-value-grammar-needs-a-consumer-census-at-plan-time
description: A plan that widens what a field may legally contain must enumerate every consumer of that field's grammar at plan time and give each one a task or a recorded reason it needs none — otherwise the new value is legal in the SSOT and rejected by a downstream gate, which makes it inert in practice; the tell is subtle because the gate's rejection reads as a defect in the value rather than as evidence about the gate, so fixing the symptom removes the signal
type: practice
origin: brief-item-addressability arc (2026-08-13) — a plan legalised `none — <reason>` in `Brief item covered`, and the plan-document-reviewer's own prompt still enumerated only two referent kinds, so the value conformed to the schema and was gapped by the project's own plan reviewer
---

The plan widened one field's grammar: `Brief item covered` gained a third
referent kind and a legal no-requirement value. It gave tasks to the schema
file, the coverage checker and the gate wiring. It did not give one to
`plan-document-reviewer-prompt.md`, whose Check 3 enumerates the accepted
referent kinds and whose Check 9 requires every such field to quote or
reference the brief.

Result: a task using the newly-legal value conforms to the schema and is
gapped by the project's own plan reviewer. The feature is real in the SSOT and
inert where it executes — authors would meet a gap every time they used the
value and stop using it.

**Why it survived plan review.** The plan HAD done a consumer sweep, and done
it well: `## Current State Evidence` checked `plan_card.py`, found it reads the
field as an opaque string, and correctly recorded "no change needed". It simply
stopped one consumer short — of the one the brief's own `## Users` section
named FIRST, quoting that consumer's check verbatim. No plan-review check
covers this: Check 8 sweeps `Smallest End State`, `Decision`, and
obligation-marker sentences. **A stakeholder named in `## Users` creates an
implicit obligation that no check sweeps.**

**The sharper half — the signal was visible one round earlier and got
deleted.** Round 1 of that same plan's review DID gap a task for using the
value, citing Check 9. That was resolved by strengthening the task's own field
text until the check passed. The check was rejecting a value the plan was in
the process of legalising, and nobody asked why the check rejected it. Fixing
the symptom removed the signal, and the root defect survived to be found three
tasks later by an implementer who happened to read the prompt file.

**How to apply.** The rule is named for widening because that is where it
was found, but the mechanism is symmetric: NARROWING a grammar fails the same
way, with a downstream gate still accepting what the SSOT just made illegal.
The census is identical in both directions.

When a task changes what a value may legally be — a new
referent kind, a new enum member, a new accepted format, a relaxed
constraint — enumerate every consumer of that grammar at plan time and give
each one either a task or a recorded reason it needs none. The recorded
no-change reason is the load-bearing half: it is what distinguishes "swept and
cleared" from "never looked". Start the enumeration from the brief's own
`## Users` — a stakeholder the brief names is a consumer the plan owes an
answer about.

And when a gate rejects a value your change is making legal, treat the
rejection as **evidence about the gate**, not only about the value. Widening
the value until the gate stops complaining is how the gate's own staleness
ships.

**Contradiction check:** distinct from
[[a-semantics-change-needs-a-plugin-wide-contradiction-sweep-arm]], which adds
a REVIEW arm after the fact to sweep unchanged files for restatements of old
semantics. This entry is upstream of that: a PLAN-time census of a specific
field's consumers, which the review arm would otherwise have to discover.
Both are needed — the census misses consumers nobody documented, the sweep
misses nothing but costs a review round. Related to
[[an-absence-claim-in-a-plan-is-a-hypothesis-not-a-fact]]: "no other consumer
exists" is exactly such a claim, and it wants the same treatment.
