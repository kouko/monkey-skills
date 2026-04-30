# Standard: Predictive AND Influenceable — the two-axis test

## Statement

Every lead-measure candidate must pass two axes, scored 1-5 each. Failing
either disqualifies the candidate completely — not "interesting but…",
just out. The threshold is 4-5 on **both** axes; anything ≤3 on either
side gets dropped.

1. **Predictive (1-5)** — when this measure moves, the lag (the WIG)
   later moves with it. The user / team can articulate the causal chain
   in **one sentence**, ending in the WIG. No chain → not predictive,
   regardless of how "leading" the metric feels.
2. **Influenceable (1-5)** — the user / team can move this measure
   **this week, with no permission from anyone outside the user's seat
   or the team's boundary**. Score reflects the fraction of the measure
   they directly control. Below 60% controllable → re-scope to the
   controllable portion or drop.

The score is **multiplicative in spirit**: a 5×3 candidate is not better
than a 4×4 candidate; it's worse, because the 3 means the influence axis
is broken. Both axes must clear 4 independently.

## Source

> A good lead measure has two primary characteristics: It's predictive of achieving the goal, and it's influenceable by the team members.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 3 (F-09)

> The lead measures with the most impact come from a collaboration between the leader and the frontline team.
>
> — *4DX* 2nd ed., Ch. 3 (F-19, supports the team-facilitator
>   application of this standard)

## Why both axes are needed

- **Predictive-only failures** (CE-02 family): "rainfall predicts crop
  yield, but no farm worker can make it rain." Stock-market direction
  predicts portfolio returns; industry tailwinds predict sales;
  competitor pricing predicts market share. Rainfall-class metrics
  flatter the dashboard but produce no leverage.
- **Influenceable-only failures**: "drink 2L water daily" is fully
  influenceable but doesn't predict whether the user publishes their
  novel; "send more emails" is influenceable but doesn't predict
  pipeline. Vanity leads pass influenceability cleanly and still don't
  move the lag.
- **Lag-on-a-shorter-clock disguised as a lead** (CE-01): "weekly
  weight" tracked as a lead for "lose 10kg by year-end" fails both
  axes — it's not influenceable by today's choices alone (water,
  digestion, hormones), and it's not predictive of anything other than
  itself. It's the lag on a faster cadence, not a leverage point.

## Application across modes

| Mode | How this standard applies |
|---|---|
| **Personal-discover (solo)** | Agent runs the test in Step 3 of `personal-discover.md`. User scores each candidate 1-5 on each axis; agent pushes for the one-sentence causal chain on predictive and the "no permission required, this week" check on influenceable. Drops anything ≤3 on either side in Step 4. |
| **Team-facilitate (leader)** | Leader runs the test as the *gating mechanism* in Step 4 of `team-facilitate.md`. Team scores together; mediation script for influenceability disagreement: "what fraction of X do we directly control? Score it as that fraction × 5." Below 60% → re-scope or drop. Leader vetoes, doesn't replace. |
| **Member-influence (member, V1 ⚠️ partial)** | Member applies the test from their personal seat in Step 2 (ladder check, predictive read) and Step 3 (per-lead 0-5 influence audit, influenceable read narrowed to "from where I sit, this week, with no permission"). Distribution of scores routes to focus pick (Step 5) or no-influence escalation (Step 6). |

## Common gaming of the test

- **"Influenceable in principle"** — the user / team scores 5 on
  influenceable because someone, somewhere, in some role, could move
  the measure. The standard asks: can YOU (or THIS team) move it THIS
  week WITHOUT permission. Replace "in principle" with "this week."
- **"Predictive because it sounds related"** — the user proposes a
  candidate whose causal chain is hand-waved. Force the one-sentence
  chain ending in the WIG. If the chain has more than one inference
  step or invokes "general best practice," it isn't predictive enough.
- **External-precedent justification** — "Stripe does X, Toyota does
  X, the book says X." External precedent is permissible as a search
  prompt (broaden the candidate pool) but never as the predictive
  evidence (only the local two-axis test against THIS WIG counts).
  See Pfeffer & Sutton 2006 in `../references/industry-grounding.md`.
