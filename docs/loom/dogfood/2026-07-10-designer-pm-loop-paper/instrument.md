# Paper-dogfood instrument — PRINCIPLES construction flow (designer/PM loop)

> **Type**: dogfood instrument (frozen before the run; revisions go in the
> report, not here)
> **Date**: 2026-07-10
> **Tests**: the §3 construction flow of
> `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md`, with the
> canon base lists in
> `docs/loom/research/2026-07-10-principles-canon-base-lists.md` as the
> propose-step completeness audit.
> **Validates** (from BACKLOG COMMITTED-NEXT): (1) generic Product
> question-set adequacy — the DEFER bet against a 4-type split; (2)
> candidate breadth — does the double guard beat popularity bias; (3)
> propose-then-react probing feel.

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
  → read-back confirmation
```

Probing rules: push each answer until it is falsifiable ("X > Y" shape —
it could lose a trade-off). When the user stalls, switch to
propose-then-react: offer a concrete hypothesis to attack, never repeat
the open question.

## Product section — generic question set (v0, the DEFER bet)

One set for all product types; the type is *revealed* by answers (esp. Q7),
not selected upfront. Dogfood watches for type-specific dimensions this
set misses.

1. **Task**: what job does the user hire this product to do? How do they
   get it done today without it?
2. **Who**: core user? Is the buyer the user? Who is explicitly NOT the
   target (who are we willing to lose)?
3. **The one quality**: if only one experience quality survives, which?
   What are we willing to sacrifice for it?
4. **Success & kill**: one year out, what signal says it worked? What
   signal says kill it?
5. **Why not existing**: why are current alternatives not enough? What is
   our unfair difference?
6. **Not doing**: what is explicitly out of scope?
7. **Money shape**: who pays, and why do they pay? (reveals 2B/2C/platform
   shape — replaces upfront type selection)

## Design section — expert lane

No fixed question set. Open invitation: state your design stance in your
own words (schools you identify with, products whose feel you want,
anti-references you reject). Agent maps the statement onto canon
(lists 2 + 3: interaction + visual, separately), returns 2-3 candidates
per lens with fit notes, probes only the deviation points.

## Engineering section — stance questions (v0, 5 questions)

Each question delivered as a mini-briefing: plain-language stakes first,
then 2-3 options with product consequences, then a recommendation.
"Delegate to agent" is a legal answer to every question. Answers land in
PRINCIPLES.md Engineering Principles.

1. **Iteration vs robustness**: when learning speed and polish conflict,
   which wins by default? (stakes: what users see breaking vs how fast
   the product improves)
2. **Reversibility posture**: prefer reversible-but-suboptimal choices,
   or optimal-but-committing ones? (stakes: fewer interruptions asking
   you to decide, vs occasionally paying a rebuild)
3. **Cost posture**: monthly infra appetite and what happens at the
   ceiling — degrade features, or spend more? (stakes: cost surprises vs
   experience surprises)
4. **Data & privacy posture**: what user data may we store, how long,
   and what is never collected? (stakes: future features need data that
   wasn't collected; trust and regulatory surface)
5. **Escalation appetite**: which engineering decisions do you want to
   see? (full delegation / kickoff briefings only / down to architecture
   choices — the per-project dial from the architecture doc §2)

Plus: **tech-stack declaration slot** — name commitments if any (platform,
language, hosting), or delegate.

## Success criteria for the run (graded in the report)

| # | Criterion | Pass looks like |
|---|---|---|
| 1 | Question-set adequacy | No product-shaping dimension surfaced mid-run that the set failed to ask about (or: the miss is named in the report → feeds the 4-type re-trigger) |
| 2 | Candidate breadth | Final candidates NOT all from the popularity heads; ≥2 traditions; considered-but-rejected named with real reasons |
| 3 | Propose-then-react | Every stall recovered with a hypothesis, not a repeated question |
| 4 | Falsifiability | Every written principle could lose a trade-off; zero motherhood statements survive read-back |
| 5 | Output shape | Base canon pinned + deviation ledger + unique principles + read-back all produced |
