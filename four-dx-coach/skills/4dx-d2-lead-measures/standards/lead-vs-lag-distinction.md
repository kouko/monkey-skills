# Standard: Lead vs lag — what a lead measure is NOT

## Statement

Most first-time D2 work fails not because users / teams pick a "wrong"
lead, but because they pick something that isn't a lead measure at all.
Five categories collapse into "lead" in everyday language; 4DX is
stricter. A candidate must clear all five exclusions before the two-axis
test (`predictive-and-influenceable.md`) is worth running.

A lead measure is **not**:

1. **A lag-on-a-shorter-clock.** "Weekly weight" tracked as a lead for
   "lose 10kg by year-end" is just the year-end lag on a faster cadence.
   Real leads: daily caloric deficit logged, weekly cardio sessions
   completed. Tell: the candidate is itself a result, not the behavior
   that drives the result.
2. **A sub-WIG ("Battle").** "Improve arrival experience" as a lead for
   guest satisfaction is a sub-WIG (a lag at a smaller scale), not a
   lead. Tell: the candidate is itself an outcome the team would want
   measured at quarter-end, not a daily/weekly behavior.
3. **A one-shot task.** "Ship the cache PR by Friday" is a deliverable.
   "% of requests served from cache, weekly" is a measure. Tell: the
   candidate has an end state — once done, there's nothing to track.
4. **A generic "leading indicator" (finance/ops usage).** Stock-market
   direction, GDP, industry tailwinds — predictive-only metrics. 4DX's
   lead measure requires *influenceable* in addition to predictive.
   Tell: the candidate is something nobody on the user's seat or team
   can move this week without permission.
5. **An OKR Key Result without further filtering.** KRs in OKR-trained
   teams are often a mix of lag and lead. 4DX is stricter. Tell: the
   candidate was authored against a different framework's grammar and
   hasn't been re-tested against THIS WIG's two-axis test.

## Source

> The lead measures are NOT the team's sub-WIGs ("Battles"). The Battles drive the WIG; the lead measures drive the Battles.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 7 (P-12, structural
>   distinction stated explicitly)

> Lead measures track the critical activities that drive, or lead to, the lag measure.
>
> — *4DX* 2nd ed., Ch. 3

## Why it matters

The five collapses produce specific failure modes downstream:

- **Lag-on-shorter-clock** (CE-01) makes the user / team feel like
  they're tracking leverage when they're tracking lag at higher
  frequency. The lag still doesn't move; the user blames themselves
  for not "pushing harder."
- **Sub-WIG masquerading as lead** turns the team's selection session
  into a sub-goaling exercise; the actual leverage points (daily
  behaviors) never get surfaced.
- **One-shot tasks as leads** burn out within weeks — once the task is
  done, the measure has no future state, and the team thrashes for a
  replacement instead of operating against a sustained lever.
- **Generic leading indicator** disqualifies on the influenceable axis
  but flatters the dashboard; the user spends time tracking something
  no daily action can move.
- **Inherited OKR KRs** import a different framework's evaluation
  grammar; without two-axis re-testing, the team runs D2 against the
  KR list rather than the WIG.

## Application across modes

| Mode | Where this distinction is enforced |
|---|---|
| **Personal-discover (solo)** | Step 2 brainstorm guard in `personal-discover.md` — when user proposes a one-shot ("buy a sit-stand desk") or a lag-shorter-clock ("weekly weight"), agent names it and asks for the underlying behavior. |
| **Team-facilitate (leader)** | Step 3 brainstorm-veto scripts in `team-facilitate.md`. Leader has the explicit Ch. 7 caution as veto language: "that's a battle (sub-WIG), not a lead — what's the daily behavior driving it?" / "that's a deliverable, not a measure." |
| **Member-influence (member)** | Step 1 comprehension guard in `member-influence.md` — if the member can't distinguish the team WIG from the team's lead measures, route to `4dx-d1-wig-formulation`. Member-side mirror: if member treats a team lead as their *personal task list*, surface the lead-as-personal-task confusion. |

## Diagnostic prompts (use when in doubt)

- **"Could this candidate be 'done' by Friday?"** — if yes, it's a task,
  not a lead.
- **"Is this candidate something we'd want measured at quarter-end?"**
  — if yes, it's a (sub-)lag, not a lead.
- **"Can the user / team move this candidate THIS week without
  permission from anyone?"** — if no, it's a generic leading
  indicator, not a 4DX lead.
- **"What's the one-sentence causal chain from this candidate to the
  WIG?"** — if the chain has more than one inference step or invokes
  generic best-practice, the candidate is loosely related, not
  predictive in the 4DX sense.

If a candidate clears all five exclusions, run the two-axis test
(`predictive-and-influenceable.md`).
