# Instrument v0.1 — PRINCIPLES construction flow (designer/PM loop)

> **Type**: dogfood instrument, revision of `instrument.md` (v0, kept
> as-run for report traceability)
> **Date**: 2026-07-10
> **Deltas from v0**: Q8 added (FINDING-01); Q4 annotated (FINDING-02);
> cross-section answer propagation codified (FINDING-03); artifact
> landing spot specified (FINDING-07); derivation-for-confirmation
> pattern added to the tech-stack slot (FINDING-08); editorial — the
> read-back line now names the per-section + final-total cadence, and the
> Product-set intro now names the 4-type-split re-trigger (BACKLOG).
> No other changes.
> **Consumers**: skill drafting of the PRINCIPLES construction flow; the
> pre-ship cold-operator dogfood round (operator ≠ instrument author).

## Flow script (all three sections)

```
user states direction (their words, unprompted structure)
  → probe per section (question sets below; propose-then-react when stuck)
  → propose 2-3 canon candidates + fit/tension notes
      · candidates from ≥2 distinct traditions
      · name 1-2 considered-but-rejected, with reasons
      · consult the base lists as completeness audit BEFORE finalizing;
        if every candidate is in that list's popularity head, re-check
      · user never sees the raw lists
  → user decides (mix allowed; bespoke section legal — escape hatch)
  → write: base canon (version-pinned) + deviation ledger entries
          + product-unique falsifiable trade-off principles
  → read-back confirmation (per section; final total read-back at the end)
```

Probing rules: push each answer until it is falsifiable ("X > Y" shape —
it could lose a trade-off). When the user stalls, switch to
propose-then-react: offer a concrete hypothesis to attack, never repeat
the open question.

**Cross-section answer propagation** (v0.1, FINDING-03): before asking any
question in a later section, check whether an earlier section's decisions
already answer it (e.g. an iCloud-native sync principle answers most of
the cost-posture question). If so, do NOT re-ask — present the derived
stance for **confirmation-as-durable-principle** instead. Same rule as
"documented decision beats re-asking", applied within one session.

**Artifact landing spot** (v0.1, FINDING-07): when the product has a
target repo, the artifact lands at `docs/loom/PRINCIPLES.md` there. Paper
runs (no repo) land the artifact in the run's dogfood folder alongside
the report.

## Product section — generic question set (v0.1)

One set for all product types; the type is *revealed* by answers (esp.
Q7), not selected upfront. Watch for type-specific dimensions this set
misses — that is the re-trigger for the 4-type split (BACKLOG).

1. **Task**: what job does the user hire this product to do? How do they
   get it done today without it?
2. **Who**: core user? Is the buyer the user? Who is explicitly NOT the
   target (who are we willing to lose)?
3. **The one quality**: if only one experience quality survives, which?
   What are we willing to sacrifice for it?
4. **Success & kill**: one year out, what signal says it worked? What
   signal says kill it?
   **Annotation (v0.1, FINDING-02)**: if the answer is phrased as
   "replaces X" — enumerate X's capability set and force an explicit
   in/out classification per capability. A replacement target smuggles in
   scope; never accept the product name as the scope.
5. **Why not existing**: why are current alternatives not enough? What is
   our unfair difference?
6. **Not doing**: what is explicitly out of scope?
7. **Money shape**: who pays, and why do they pay? (reveals 2B/2C/platform
   shape — replaces upfront type selection)
8. **Lifecycle & scale** (v0.1, FINDING-01): how long does the content
   (or core object) live, and how large does the collection grow? Once it
   grows, how does the user find one item? Push for an explicit stance on
   the simplicity-vs-scale trade-off (a declared scale ceiling is a
   legitimate, falsifiable answer).

## Design section — expert lane

No fixed question set. Open invitation: state your design stance in your
own words (schools you identify with, products whose feel you want,
anti-references you reject). Agent maps the statement onto canon
(lists 2 + 3: interaction + visual, separately), returns 2-3 candidates
per lens with fit notes, probes only the deviation points.

## Engineering section — stance questions (v0.1, 5 questions)

Each question delivered as a mini-briefing: plain-language stakes first,
then 2-3 options with product consequences, then a recommendation.
"Delegate to agent" is a legal answer to every question. Answers land in
PRINCIPLES.md Engineering Principles. **Apply cross-section propagation
first** — questions already answered by Product/Design decisions become
confirmation items, not questions.

1. **Iteration vs robustness**: when learning speed and polish conflict,
   which wins by default? (stakes: what users see breaking vs how fast
   the product improves)
2. **Reversibility posture**: prefer reversible-but-suboptimal choices,
   or optimal-but-committing ones? (stakes: fewer interruptions asking
   you to decide, vs occasionally paying a rebuild)
3. **Cost posture**: monthly infra appetite and what happens at the ceiling —
   degrade features, or spend more? (stakes: cost surprises vs
   experience surprises)
4. **Data & privacy posture**: what user data may we store, how long,
   and what is never collected? (stakes: future features need data that
   wasn't collected; trust and regulatory surface)
5. **Escalation appetite**: which engineering decisions do you want to
   see? (full delegation / kickoff briefings only / down to architecture
   choices — the per-project dial from the architecture doc §2)

Plus: **tech-stack declaration slot** — name commitments if any (platform,
language, hosting), or delegate. When the stack is already determined by
the principles, present it as a **derivation for confirmation**, not an
open option set (FINDING-08 pattern).

## Success criteria for a run (graded in the report)

| # | Criterion | Pass looks like |
|---|---|---|
| 1 | Question-set adequacy | No product-shaping dimension surfaced mid-run that the set failed to ask about (or: the miss is named in the report → feeds the 4-type re-trigger) |
| 2 | Candidate breadth | Final candidates NOT all from the popularity heads; ≥2 traditions; considered-but-rejected named with real reasons |
| 3 | Propose-then-react | Every stall recovered with a hypothesis, not a repeated question |
| 4 | Falsifiability | Every written principle could lose a trade-off; zero motherhood statements survive read-back |
| 5 | Output shape | Base canon pinned + deviation ledger + unique principles + read-back all produced |
