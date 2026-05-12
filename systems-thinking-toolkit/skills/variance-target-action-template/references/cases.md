# Variance/Target/Action — Past Application Cases

Four calibrating cases for the V/T/A balancing-loop template and the
do-nothing-under-oscillation diagnostic. Three are Sherwood originals
(hotel shower, inventory manager, Bank of England MPC) and one is V2
novel-domain transfer (NPS playbook ping-pong). Read all four before
applying the skill — they encode the delay-vs-target distinction, the
"doing nothing was the right action" precedent, the institutional
small-moves-long-intervals exemplar, and the modern customer-success
analogue.

## Case 1 — Strange Hotel Shower (c08)

- **Problem**: Hotel shower has a long pipe; water adjustment takes
  ~10 seconds to reach the head. The guest turns it hotter, nothing
  happens, turns it hotter more, then suddenly scalding water arrives,
  turns it cold, eventually frozen water arrives.
- **Methodology applied**: The shower is a B-loop with delay. The
  target (comfortable temperature) is fixed, but the action (turn
  knob) feeds back to the actual (water temperature) with a 10-second
  lag. The guest reads variance before the prior action has worked
  through, so each correction overshoots.
- **Conclusion**: The mechanic is identical to corporate over-correction.
  The cure is the same — make a small adjustment, *wait one full
  cycle*, observe, then adjust.
- **Outcome**: Pedagogical anchor for every later B-loop case in the
  book. The hotel shower is the canonical visceral example of why
  acting faster than the loop converges amplifies, not damps,
  oscillation.

## Case 2 — Inventory Control Manager (c09)

- **Problem**: Inventory levels were self-stabilizing under the prior
  policy. A new manager, untrained in systems thinking, reset the
  target inventory level every month based on the previous month's
  variance. Inventory began oscillating with growing amplitude.
- **Methodology applied**: Sherwood diagnoses a moving-target B-loop.
  The system's natural response cycle was longer than monthly, so
  monthly retargeting added a forcing oscillation on top of the
  natural correction. The "fix" was making things worse.
- **Conclusion**: The intervention was to **stop moving the target**
  and let the existing loop converge. The destabilization was 100%
  endogenous — the system was already correct; the manager's
  well-meaning adjustments were the source of the problem.
- **Outcome**: Sherwood's flagship "doing nothing was the right action"
  case. This is the precedent to cite when the organization expects
  visible activity as proof of management; the case proves
  visible restraint can be the correct managerial output.

## Case 3 — Bank of England Monetary Policy Committee (c10)

- **Problem**: How to manage inflation, a metric with very long
  transmission lags from rate-change to price-effect (12-24 months).
- **Methodology applied (retrospective)**: The MPC's institutional
  discipline — meet monthly, change rates by 25bp at most, often
  do nothing for many months — is structurally exactly Sherwood's
  prescription: small moves, long intervals, allow each move to
  work through before the next. The MPC is engineered to resist
  the corporate over-correction reflex.
- **Conclusion**: Long-lag B-loops require institutional commitment
  to restraint that is hard for ad-hoc decision-makers to sustain.
  The MPC's structural arrangement (fixed cadence + bounded move
  size + multi-voter veto) operationalizes the discipline.
- **Outcome**: Held up by Sherwood as the institutional best-practice
  exemplar for managing any long-lag B-loop. *Caveat: period-dated.*
  The Sir Edward George MPC of 1997-2003 predates post-2008
  unconventional policy, post-2021 inflation regime change, and
  central-bank credibility crises. Use the *structural* lesson
  (small moves, long intervals) without inheriting the institutional
  confidence.

## Case 4 — NPS Playbook Ping-Pong (V2 novel-domain transfer)

- **Problem**: A customer-success org changes its onboarding playbook
  every quarter to fix swinging NPS. Each change makes swings wider.
- **Methodology applied**: NPS responds to onboarding cohort experience
  with ~6+ month lag from playbook change to NPS effect; quarterly
  playbook changes act faster than the loop can respond. Classic
  delay-induced amplification, identical to the hotel shower at
  organizational scale.
- **Conclusion**: "Do nothing for two quarters" first — let the loop
  converge. If action is genuinely needed, shorten the *detection*
  lag (run NPS on fresh cohorts at weeks 2, 4, 8) not the target.
  Attacking the lag is structurally legitimate; moving the target
  is not.
- **Outcome**: Demonstrates V/T/A transfers cleanly from 2002
  manufacturing/macro contexts to modern SaaS customer-success.
  The mechanic is the same; only the time-scale and the vocabulary
  changed. This is the case to cite when stakeholders argue
  "but that's old-economy stuff, our metric is different."
