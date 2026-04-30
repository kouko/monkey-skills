# Protocol: Solo — Discover personal lead measures (voice = personal coach)

> Loaded by SKILL.md orchestrator when scope detection identifies a solo
> user with a personal WIG and no team — the agent fills the role of
> personal coach guiding Socratic discovery.

## R — Reading (verbatim source quote)

> Lead measures track the critical activities that drive, or lead to, the lag measure. ... A good lead measure has two primary characteristics: It's predictive ... and it's influenceable.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 3

## I — Interpretation (mode-specific)

A goal (the lag measure: weight, revenue, finished novel) tells the user
whether they have already won or lost. By the time it moves, the behavior
that moved it is in the past. Lead measures are the upstream behaviors
the user can act on TODAY that the goal depends on.

The discovery rule has exactly two axes, and both must be true:

1. **Predictive** — when this measure moves, the lag measure later moves
   with it. There is a causal chain the user can articulate in one
   sentence.
2. **Influenceable** — the user, personally, with no permission required,
   can move this measure by doing something this week.

Most metrics fail one axis. Stock-market returns predict portfolio P&L
but the user can't influence them — fail. Drinking 2L water daily is
influenceable but doesn't predict whether the user publishes their novel
— fail. Weekly weight is neither lead nor influenceable — it's the lag
on a shorter clock.

A lead measure is also typically counter-intuitive. The shoe-store study
of 4,500 outlets found that *measuring children's feet* was the highest-
leverage behavior — not friendliness, not price, not stock width. The
obvious answers are usually wrong; the leverage point hides one layer
below.

Aim for 2-3 lead measures total. One frequency-based ("do X N times per
week") and one quality-based ("ensure each X meets standard Y") is the
canonical pair. More than three and the user has recreated the whirlwind.

Voice contrast vs sibling protocols: this protocol is solo — the agent is
the user's personal coach, surfacing the two-axis test loudly, pushing
back on lag-masquerading-as-lead and influenceable-but-not-predictive
candidates, never inventing leads on the user's behalf.

## A1 — Past Application

### Case 1: Shoe retailer, 4,500 stores
- **Problem**: WIG was per-store sales growth. Hundreds of plausible
  lead candidates (friendliness, conversion, basket size, foot traffic,
  stock width).
- **Methodology applied**: Statistical leverage analysis across stores
  asking "which behavior, when present, predicts higher sales AND can a
  clerk control it daily?"
- **Conclusion**: *Measuring a child's feet for fit* — single highest-
  correlated behavior. Both predictive (correctly fitted shoes → parent
  buys + returns) and fully influenceable (any clerk can do it).
- **Outcome**: Counterintuitive lead became the new training standard;
  validated as leverage point across the chain.

### Case 2: Younger Brothers Construction — safety
- **Problem**: WIG was reducing serious safety incidents (lag =
  injuries). Tracking incidents only tells you after someone's hurt.
- **Methodology applied**: Distilled compliance to six observable
  behaviors (hard hats, eye protection, scaffolding, etc.); supervisors
  walked sites and physically logged compliance.
- **Conclusion**: Behavioral compliance both predicted incidents and
  was daily-influenceable by every worker.
- **Outcome**: Incidents fell from 57 to 12 per year. The lead was
  harder to track than the lag (P-11: pay the price), but tracking it
  was the whole point.

### Case 3: Personal-scale shoe-store analogue (Younkers / writer / book-
reader pattern)
- **Problem**: Knowledge-worker / creative-worker variant — "I want to
  finish my novel" / "I want to read 50 books this year" / "I want to
  ship a side project." The obvious lead ("write more", "read more") is
  too vague to verify and gameable; user thrashes.
- **Methodology applied**: Apply the two-axis test like the shoe study —
  what's the equivalent of "measure children's feet" for THIS goal?
  For the novel: "30 min focused writing with phone in another room,
  Mon-Fri" (frequency) + "each session ends with one named scene
  beat" (quality). For reading: "1 chapter per night" (frequency) +
  "one-paragraph summary per book" (quality).
- **Conclusion**: Counter-intuitive specificity beats generic effort.
  The quality-axis lead protects against self-Goodharting (screen-
  staring counted as writing; speed-reading without comprehension).
- **Outcome**: Personal-scale leads, when paired frequency + quality
  and re-checked at 4 weeks, behave like the operational cases.

## A2 — Future Trigger

When a solo user would need this protocol:

1. User has a clearly-defined WIG (From X to Y by When) but is staring
   at it not knowing what to do MONDAY.
2. User has been "working hard" on a goal for weeks but the lag measure
   isn't moving — they're acting on noise, not leverage.
3. User has named a "lead measure" that's actually the lag-on-a-
   shorter-clock (weekly weight, monthly revenue) or that they can't
   influence (market direction, competitor moves).
4. User is about to install a tracking dashboard with 20+ metrics and
   needs to be cut down to the 2-3 that actually drive the goal.
5. User asks "what's a leading indicator for X?" — generic answer would
   miss the influenceable axis.

## E — Execution

The agent acts as **personal coach** — Socratic discovery, never inventing
leads on the user's behalf.

1. **WIG gate check**
   - Ask: "State your WIG in one sentence: from X to Y by when."
   - Completion: user produces a single sentence with current state,
     target state, and deadline.
   - Halt: if user can't produce this, STOP and route to
     `4dx-d1-wig-formulation`. Leads built on a vague WIG are noise.

2. **Brainstorm candidate behaviors (5-10)** — see
   `../standards/lead-vs-lag-distinction.md`
   - Prompt: "What daily or weekly behaviors do you BELIEVE would drive
     this WIG? Don't filter — list 5-10 candidates."
   - Push for counter-intuitive options: "What's something nobody else
     would think of? What's the equivalent of 'measure children's feet'
     for your goal?"
   - Halt: if user proposes a one-shot task ("buy a sit-stand desk"),
     name it: "that's a deliverable, not a measure — what underlying
     behavior would you track every week?" Re-add as a measure or drop.
   - Completion: ≥5 candidate behaviors written down.

3. **Two-axis scoring (1-5 × 1-5)** — see
   `../standards/predictive-and-influenceable.md`
   - For each candidate, ask the user to score:
     - **Predictive (1-5)**: "If you do this consistently for 6 weeks,
       how confident are you the lag measure will move? Articulate the
       causal chain in one sentence."
     - **Influenceable (1-5)**: "Can you, alone, with no permission,
       move this measure THIS WEEK?"
   - Completion: every candidate has both scores + a one-sentence
     causal chain for predictive.

4. **Drop anything <4 on either axis**
   - ≤3 on predictive: noise (e.g. "drink water").
   - ≤3 on influenceable: rainfall-class (e.g. "market conditions
     improve").
   - Completion: only 4-5★ candidates remain on both axes.

5. **Select 2-3, prefer one frequency + one quality**
   - Prompt: "Pick 2-3 — at most. Ideally one frequency-based (do X N
     times per week) and one quality-based (each X meets standard Y)."
   - Halt: if user picks >3, force a cut. More than three recreates
     the whirlwind.
   - Completion: 2-3 named lead measures.

6. **Operational definition**
   - For each selected lead, write:
     - What exactly counts as "done" (specific — "30 min focused
       writing with phone in another room", not "write more").
     - How and when it gets logged.
     - Weekly target number.
   - Completion: each lead has a definition another person could apply
     without asking clarifying questions.

7. **Predict the causal chain (in writing)**
   - User writes one paragraph: "If I hit my lead targets every week
     for 6 weeks, here's why I expect the lag to have moved by [Y]:
     ..."
   - This is a falsifiable forecast — the anchor for D4 review and the
     trigger for `4dx-sustain-personal-momentum-rescue` if the lag
     stays flat at 4 weeks.
   - Completion: written paragraph linking lead activity → lag movement
     with explicit mechanism.

8. **Goodhart self-check** — see `../standards/goodhart-self-check.md`
   - Ask: "If you attach high stakes to these leads (visible counter,
     accountability partner, public commitment), where might you start
     gaming them? Speed-reading? Screen-staring? Voicemails as 'calls'?"
   - Completion: user names the gaming risk per lead and either pairs
     a quality lead with a frequency lead, or commits to a 4-week
     causal-chain re-check.

9. **Output & hand-off**
   - 2-3 named lead measures, each with operational definition + weekly
     target + causal-chain rationale + Goodhart counter.
   - Hand off to `4dx-d3-scoreboard` for display, and to
     `4dx-d4-cadence` (solo mode) for weekly review.

## B — Boundary (mode-specific)

### Do NOT use this protocol in:

- **No defined WIG yet** — leads need a lag to be predictive of. Route
  to `4dx-d1-wig-formulation`.
- **Stroke-of-pen goals** — single decision/purchase. No daily behavior
  to discover.
- **Domains where the lag is structurally unmeasurable on a weekly
  clock** — true scientific R&D, novel-writing, drug discovery — the
  lead-to-lag feedback loop may run in months/years and weekly leads
  become theatrical. Substitute "specific experiments per week"
  (Cystic Fibrosis Center pattern) or honestly admit the cadence
  doesn't fit.
- **Team / leader / member contexts** — load `team-facilitate.md` or
  `member-influence.md` instead.
- **Stale leads** — if leads exist but lag is flat for 4+ weeks, route
  to `4dx-sustain-personal-momentum-rescue`, not first-time selection.

### Author-warned failure modes (cluster CEs)

- **Lag-masquerading-as-lead (CE-01)** — "weekly weight" tracked as a
  lead for "lose 10kg by year-end" is just the lag on a shorter clock.
  Real leads: daily caloric deficit logged, weekly cardio sessions
  completed.
- **Predictive but not influenceable (CE-02)** — "rainfall predicts
  crop yield, but no farm worker can make it rain." Stock direction,
  industry tailwinds, "the economy" — disqualified regardless of
  predictive power.
- **Lead-data-too-hard-so-skipped (CE-17)** — lead data is almost
  always harder to collect than lag data. Pay the price (P-11); if the
  user gives up on tracking the lead, they have abandoned D2.
- **Leader-only game (CE-20, personal analogue)** — "I'll just do it
  perfectly when I have time." The lead must be doable in the user's
  actual normal week, not in an imagined ideal one.
- **Lead at frequency-only quality (CE-21)** — user hits the count but
  quality is hollow. Quality-based leads exist precisely to catch this.
- **Goodhart / measure-gaming (CE-24)** — see
  `../standards/goodhart-self-check.md`.

### Easily-confused neighbouring concepts

- **"Leading indicator" (generic)** — usually means "anything
  predictive." Lead measure (4DX) requires influenceable too.
- **"Habit"** — a habit is a behavior; a lead measure is a *measurement*
  of a behavior tied to a specific WIG.
- **OKR Key Results** — KRs can be either lag or lead in 4DX terms;
  4DX is stricter.

## Standards used

- `../standards/predictive-and-influenceable.md` — Step 3 + Step 4
  filters
- `../standards/goodhart-self-check.md` — Step 8 self-check
- `../standards/lead-vs-lag-distinction.md` — Step 2 brainstorm guard

## References

See `../references/industry-grounding.md` sections **Goodhart**,
**Strathern**, and the **Wells Fargo / Phoenix VA / Atlanta APS** cases
— mechanism + documented gaming failures the book under-treats.
