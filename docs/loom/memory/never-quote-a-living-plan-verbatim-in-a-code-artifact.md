---
name: never-quote-a-living-plan-verbatim-in-a-code-artifact
description: A code artifact that quotes plan prose verbatim, or narrates a task's ownership history, is false the moment the plan is amended — and under parallel SDD the orchestrator amends the plan WHILE the implementer is writing those quotes; in one round every plan quotation in an artifact was false while its code citations failed at about 1 in 12, because code is a stable citation target within a task and a plan under active amendment is not. A reviewer's own "all twelve citations hold" did not survive a second audit either
type: gotcha
sources:
  - resource: feat-us-quarterly-statement-series Task D round 3 (US quarterly series arc, 2026-07-30)
---

Task D's round 3 was audited by two independent reviewers. The first opened twelve
of the artifact's code citations and reported **twelve holding**. The second
re-audited the same set and found **one mis-attributed** (a subprocess call site
credited to the wrong callee — a valid precedent, wrongly labelled). So even
"all twelve are clean" was a relayed claim that did not survive a second audit —
which is this entry's sibling lesson arriving unbidden inside its own evidence.

Set that one aside, and the asymmetry is still stark. Its code citations failed at
roughly 1 in 12; **both of its fatal findings were quotations of the plan
document**, and a third mis-stated the plan's coverage. One quoted a Decision Log
heading verbatim that `grep` could not find. One asserted "the Decision Log still
carries the older wording" when it no longer did. Two restated an acceptance clause
the plan had explicitly deleted as unexecutable — and the test file's version went
further, claiming that clause "witnesses the two halves fitting together offline"
when the plan says no offline witness exists at all.

Nobody was careless. The sequence was:

1. The orchestrator dispatched the round describing the plan's then-current state.
2. Plan review, running concurrently, split a task out — so the dispatch was stale
   before the implementer read it.
3. The implementer **noticed this itself**, re-read the plan, and rewrote its prose
   to match. Correct behaviour.
4. The orchestrator then applied plan review's remaining findings — narrowing the
   very clause the implementer had just quoted, and rewriting the very heading.

The target moved twice, the second time after the implementer had already chased it
once. No amount of care inside the round could have won that race.

**Why:** within a task, source code is a *stable* citation target — the implementer
owns it and nobody else edits it mid-round. A plan under amendment is the opposite:
it is the orchestrator's working surface, and in parallel SDD the orchestrator is
amending it while implementers run. Quoting it verbatim converts every future plan
edit into a false claim inside a committed artifact, and the artifact's author is
not the person who will make that edit. The asymmetry — code citations failing at
about 1 in 12 while every plan quotation in the same artifact, in the same round,
was false — is the whole lesson.

There is a second, simpler defect underneath: **the module was narrating plan
history at all.** "Ownership moved from Task D to Task H to Task J" is the Decision
Log's jurisdiction. A module's docstring restating it duplicates a record that
already exists, in a place that cannot be kept current, for a reader who does not
need it.

**How to apply:**

1. **Never quote plan prose verbatim in code, tests, or fixtures.** Cite the plan
   by stable heading (`plan Task J, Acceptance`) and state the contract **in the
   artifact's own words**. A paraphrase that drifts is a stale comment; a verbatim
   quote that drifts is a false citation, and reviewers correctly escalate the
   second.
2. **Do not narrate task-ownership history in a code artifact.** Record the
   boundary and its rationale — which is durable — and leave the history to the
   plan's Decision Log, which is where anyone looking for it will go.
3. **Orchestrators: treat "plan amended" as invalidating in-flight dispatches that
   quote it.** Either finish plan amendments before dispatching implementers who
   will cite the plan, or tell the dispatch explicitly that the plan is being edited
   concurrently and that it must cite by heading, never by quotation.
4. **Reviewers: audit plan quotations separately from code citations**, because they
   fail for structurally different reasons and at different rates.

Relates to [[a-relayed-claim-becomes-fact-in-one-hop]] (the same branch's dominant
defect — this is its concurrent-edit variant, where nobody relayed anything wrong
and the claim still ended up false) and to
[[a-passage-that-describes-itself-decays-on-every-edit]] (a claim whose subject is
its own container; here the subject is a *sibling* document under concurrent edit,
which the citation machinery also cannot protect).
