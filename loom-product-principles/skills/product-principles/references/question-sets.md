# PRINCIPLES construction flow — question sets

> Source of truth for facts/question texts:
> `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/instrument-v0.1.md`
> (dogfood report, 2026-07-10). Referenced by SKILL.md instead of
> inlining question text. Sanctioned exception: content tagged
> `[editorial addition — ...]` inline is a provenance-marked
> derivation from a named source, not SSOT-verbatim content.

Apply **cross-section answer propagation** before asking any question
in a later section: check whether an earlier section's decisions
already answer it (e.g. an iCloud-native sync principle answers most
of the cost-posture question). If so, do NOT re-ask — present the
derived stance for **confirmation-as-durable-principle** instead. Same
rule as "documented decision beats re-asking", applied within one
session.

## Product question set (generic, all product types)

One set for all product types; the type is *revealed* by answers
(esp. Q7), not selected upfront. Watch for type-specific dimensions
this set misses — that is the re-trigger for the 4-type split
(BACKLOG).

1. **Task**: what job does the user hire this product to do? How do
   they get it done today without it?
2. **Who**: core user? Is the buyer the user? Who is explicitly NOT
   the target (who are we willing to lose)?
3. **The one quality**: if only one experience quality survives,
   which? What are we willing to sacrifice for it?
4. **Success & kill**: one year out, what signal says it worked? What
   signal says kill it?

   **Annotation**: if the answer is phrased as "replaces X" —
   enumerate X's capability set and force an explicit in/out
   classification per capability. A replacement target smuggles in
   scope; never accept the product name as the scope.
5. **Why not existing**: why are current alternatives not enough?
   What is our unfair difference?
6. **Not doing**: what is explicitly out of scope?
7. **Money shape**: who pays, and why do they pay? (reveals 2B/2C/
   platform shape — replaces upfront type selection)
8. **Lifecycle & scale**: how long does the content (or core object)
   live, and how large does the collection grow? Once it grows, how
   does the user find one item? Push for an explicit stance on the
   simplicity-vs-scale trade-off (a declared scale ceiling is a
   legitimate, falsifiable answer).

## Design section — expert lane

No fixed question set. Open invitation: state your design stance in
your own words (schools you identify with, products whose feel you
want, anti-references you reject). Agent maps the statement onto
canon: the interaction lens (list 2) runs as one candidate round; the
visual lens runs as **two axis-typed candidate rounds** — Axis A
(cultural) reads only `canon-design-visual.md`, Axis B (surface) reads
only `canon-design-surface.md` (contamination guard: each round reads
only its own file).

The interaction lens returns 2-3 candidates with fit notes, probes
only the deviation points. The visual lens returns **3-5 candidates**
with fit notes (widened from 2-3): of the 3-5, deliberately include
1-2 **divergent** candidates — transparently labeled **exploratory** —
that deviate from the stated design stance yet stay **defensible**
against the PRINCIPLES **values**. Divergent candidates deviate on
aesthetic expression, never on values: a low-stimulus constitution
still excludes Memphis.

## Engineering section — stance questions (5 questions)

Each question delivered as a mini-briefing: plain-language stakes
first, then 2-3 options with product consequences, then a
recommendation. "Delegate to agent" is a legal answer to every
question. Answers land in PRINCIPLES.md Engineering Principles.
**Apply cross-section propagation first** — questions already
answered by Product/Design decisions become confirmation items, not
questions.

1. **Iteration vs robustness**: when learning speed and polish
   conflict, which wins by default?
   stakes: what users see breaking vs how fast the product improves.
2. **Reversibility posture**: prefer reversible-but-suboptimal
   choices, or optimal-but-committing ones?
   stakes: fewer interruptions asking you to decide, vs occasionally
   paying a rebuild.
3. **Cost posture**: monthly infra appetite and what happens at the
   ceiling — degrade features, or spend more?
   stakes: cost surprises vs experience surprises.
4. **Data & privacy posture**: what user data may we store, how
   long, and what is never collected?
   stakes: future features need data that wasn't collected; trust
   and regulatory surface.
5. **Escalation appetite**: which engineering decisions do you want
   to see? (full delegation / kickoff briefings only / down to
   architecture choices — the per-project dial from the architecture
   doc §2)
   stakes: how often the agent interrupts you vs how much drifts
   without your sign-off. [editorial addition — derived from the
   per-project escalation dial,
   docs/loom/design/2026-07-10-designer-pm-loop-architecture.md §2;
   not in instrument v0.1]
   Lands as a normal `## Engineering Principles` entry (see
   principles-rules.md §Escalation appetite — landing shape); optional.

### Tech-stack declaration slot

Name commitments if any (platform, language, hosting), or delegate.
When the stack is already determined by the principles, present it as
a **derivation for confirmation** — the agent derives a stack proposal
from context and the user confirms — not an open-ended ask.
