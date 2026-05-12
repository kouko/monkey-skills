---
name: variance-target-action-template
description: |
  Use to model any management-control situation as a balancing loop
  (target ↔ variance ↔ action ↔ actual) and diagnose oscillation. Tells
  you when to "do nothing" instead of acting. Triggers: "metric keeps
  swinging," "we keep adjusting and it's getting worse," "ping-ponging
  between two states," "every time we change [X] it gets worse," "should
  I act now or wait?", "I don't know if my last move worked yet,"
  "the numbers go up and down." NOT for systems that are genuinely
  diverging (run loop-and-link-primitives diagnosis instead), one-off
  non-recurring decisions, or real-time control with zero detection lag.
  KEYWORDS: balancing loop, B-loop, target, variance, action, actual,
  oscillation, ping-pong, over-correction, do nothing, feedback delay,
  detection lag, small moves long intervals, moving target, endogenous
  oscillation, growing amplitude, monetary policy committee, inventory
  control, NPS swing. JA: バランス型ループ・目標と実績の差・振動・何もしない判断 /
  zh-TW: 平衡迴路・目標差異行動範本・振盪・無為而治的時機。
source_book: Seeing the Forest for the Trees — Dennis Sherwood
source_chapter: "Chapter 6 (balancing loops, time delays, oscillation); Chapter 10 (B-loop template per lever)"
source_language: en
tags: [systems-thinking, control, oscillation, management-loops, balancing-loop, feedback-delay]
related_skills:
  - slug: loop-and-link-primitives
    relation: depends-on
  - slug: cld-craft
    relation: depends-on
  - slug: limits-to-growth-take-the-brakes-off
    relation: contrasts-with
---

# Variance/Target/Action Balancing-Loop Template + Do-Nothing-Under-Oscillation

## R — Reading

> "The wise manager — and wise boss — knows when to do absolutely
> nothing… because the system is already on its way back toward target,
> and any action will make the swing worse, not better."
>
> — Dennis Sherwood, Chapter 6

## I — Interpretation

A balancing loop has four canonical nodes: **target** (where you want
the metric), **actual** (where it is), **variance** (target minus
actual, or vice versa), and **action** (the lever movement variance
triggers). The action moves the actual toward the target; when they
match, variance is zero and action stops. This is the generic structure
of every thermostat, every quota system, every monetary-policy
committee, every customer-success playbook.

Two things make this loop misbehave:

1. **Time delay between action and actual.** The action moves the
   actual, but not immediately. If the operator reads the variance
   *before* the prior action has worked through, they over-shoot.
   The metric overshoots the target, variance flips sign, they
   correct in the opposite direction, overshoot again. The system
   oscillates with growing amplitude.

2. **Goal-moving / playbook-changing faster than the loop can
   converge.** Each adjustment resets the loop before it finishes
   its response cycle. The system never reaches steady state.

Sherwood's counter-intuitive prescription: when you see oscillation
with growing or sustained amplitude, the right move is often **do
nothing for one full feedback cycle** and let the loop converge. If
you must act, attack the *delay* (faster measurement, faster channel
between detection and action), not the *target*.

## A1 — Past Application

The four cases that calibrate the V/T/A template and the
do-nothing-under-oscillation diagnostic (hotel shower c08, inventory
control manager c09, Bank of England MPC c10, NPS playbook ping-pong
V2-derived) are detailed in `references/cases.md`.

**MANDATORY — READ ENTIRE FILE**: Before diagnosing an oscillating
metric or recommending "do nothing," you MUST read
[`references/cases.md`](references/cases.md) (~85 lines) for the
delay-vs-target distinction, the "doing nothing was the right action"
precedent, the institutional small-moves-long-intervals exemplar, and
the modern customer-success analogue.

## A2 — Future Trigger ★

### When will the user need this skill?

1. A KPI is swinging quarter-to-quarter and each intervention seems
   to widen the swing.
2. Designing a new management-control mechanism (quota, OKR,
   inventory rule, retention program) and want to predict whether it
   will oscillate.
3. Diagnosing why a "perfectly reasonable" management response is
   making things worse.
4. Coaching a junior manager who is changing tactics every Monday
   because last Friday's numbers were bad.
5. Reviewing a proposed change to compensation, pricing, or staffing
   that has a long lag between change and visible result.

### Language signals

- "metric keeps swinging" / "ping-ponging"
- "every time we change [X] it gets worse"
- "we keep adjusting"
- "the numbers go up and down"
- "I don't know if my last move worked yet"
- "should I act now or wait?"

### Distinction from neighboring skills

- vs. `limits-to-growth-take-the-brakes-off`: V/T/A is a *single*
  B-loop's internal dynamics; limits-to-growth is the *coupling* of
  an R-loop and a B-loop. Symptom: V/T/A's signature is *oscillation*
  around a value; limits-to-growth's is *deceleration toward* one.
- vs. `strategy-lever-and-cascade` (sk07): V/T/A assumes you already
  have a correctly-classified lever. If you're trying to operate
  directly on the actual, that's an outcome-as-lever error (run sk07
  first to reframe the lever before applying V/T/A to it).
- vs. classic PID control theory: same physics, but Sherwood's
  contribution is the *managerial* operationalization — "small moves,
  long intervals, attack the lag" — and the "do nothing" cultural
  permission slip that PID theory takes for granted.

## E — Execution

```
E flow:
  Step 0: signal-vs-noise pre-check (SPC ±2σ + autocorrelation)
        │ noise → not a V/T/A case (use noise-filtering)
        │ signal
        v
  metric oscillating? ── no → not a V/T/A case
        │ yes              (if decelerating, try limits-to-growth)
        v
  4 nodes named + variance direction explicit?
        │
        ├── no → Step 1: sketch the 4-node loop
        └── yes → Step 2: estimate feedback delay
        │
        v
  Step 3: plot 3+ feedback-cycle durations of actual
        │
        v
  Step 4: classify dysfunction
  ├── (a) converging, manager impatient → wait
  ├── (b) sustained oscillation → lengthen interval, shrink move
  ├── (c) growing amplitude → DO NOTHING for two cycles
  └── (d) target keeps moving → stop moving the target
        │
        v
  Step 5: if action: smallest move that lets system respond
        │
        v
  Step 6: communicate the "do nothing" rationale upward
```

When this skill activates, follow these steps:

0. **Pre-check: signal vs noise.** Before V/T/A diagnosis, verify the
   variance is *from a system*, not from random noise. Apply SPC
   (Statistical Process Control) one-pass: if variance falls within
   ±2σ of historic mean and shows no autocorrelation, it is NOISE —
   V/T/A template does not apply (use noise-filtering / control-chart
   tooling instead). If variance shows trend, autocorrelation, or
   clusters > 2σ, proceed with Step 1. Halt condition: cannot compute
   σ on the metric → at least eyeball the recent series for cluster /
   trend / cyclicality before continuing; otherwise you risk
   prescribing "do nothing" against actual signal, or "small moves"
   against actual noise.
1. **Sketch the candidate B-loop in 4 nodes** — completion criterion:
   target, actual, variance, action all named with noun labels;
   variance direction explicitly written (target minus actual or
   reverse); action's effect on actual labeled S or O. If the loop
   is not balancing (odd O-count), you're modeling the wrong
   structure.
2. **Estimate the feedback delay** — completion criterion: a number
   in time units for "from action to detectable change in actual."
   For NPS, weeks-to-months; for inventory, days-to-weeks; for
   macro-rates, quarters-to-years. Halt condition: if you can't
   estimate the delay, you do not understand the loop well enough to
   intervene safely.
3. **Plot the recent trajectory** — completion criterion: 3+
   feedback-cycle durations of actual values. Look for: convergence
   (good — let it run), sustained oscillation (delay is poorly
   understood), growing oscillation (over-correction — STOP
   intervening).
4. **Diagnose the dysfunction class** — completion criterion: one of:
   (a) loop is converging fine, manager is impatient → action: wait;
   (b) sustained oscillation → action: lengthen interval between
   moves to ≥1 feedback cycle, reduce move magnitude. **Heuristic:
   new interval ≥ 1.5 × estimated delay between action and observable
   effect.** Below 1.5× = still ping-ponging on stale state; at or
   above 1.5× = at least one full delay-cycle absorbed before the
   next move; (c) growing
   amplitude → action: do absolutely nothing for two cycles, then
   re-baseline; (d) target keeps moving → action: stop moving the
   target. Halt condition: if it's "genuinely diverging" (not
   oscillating, just running off to infinity), this is not your
   skill — investigate whether an R-loop has flipped.
5. **Specify the smallest move** — completion criterion: if action
   is needed, name the smallest intervention that lets the system
   respond before the next decision point. Sherwood's BoE rule:
   small moves, long intervals, often no move.
6. **Communicate the "do nothing" decision upward** — completion
   criterion: the rationale is documented (this loop is converging /
   the prior action hasn't had time to land yet) so that the
   organization doesn't interpret restraint as inaction. Sherwood:
   "wise boss as well as wise manager." **Organizational-politics
   escalation note:** in quarterly-OKR / weekly-review orgs, "do
   nothing" may be rejected as a legitimate action regardless of
   correctness. Counter-moves: (i) reframe as "scheduled non-
   intervention through cycle N+1" with an explicit review date,
   (ii) attach a falsifiable abort trigger ("if amplitude grows by
   >X% before T, we re-intervene"), (iii) escalate the diagnosis,
   not the inaction — name the loop, the delay, and the prior
   over-correction so the decision is read as *informed restraint*
   not absence. If the org structurally cannot tolerate this, the
   diagnosis still holds; the constraint is political, not analytic.

## B — Boundary ★

### Do NOT use when:

- **The system is genuinely diverging, not oscillating.** Numbers
  monotonically running off (e.g., a vicious R-loop spinning) require
  `loop-and-link-primitives` (sk01) reinforcing-loop diagnosis and
  probably immediate intervention. "Do nothing" applied here is
  malpractice.
- **One-off, non-recurring decisions.** A go/no-go gate on a single
  project launch has no feedback loop to oscillate; V/T/A doesn't
  apply.
- **The detection lag is genuinely zero.** Real-time control systems
  (a thermostat in a tight room) don't oscillate noticeably; the
  cure-by-waiting is unnecessary.
- **The target itself was wrong and is being legitimately revised.**
  V/T/A's "stop moving the target" assumes the target is sound. If
  the target was set on a now-invalidated assumption, revise it once
  *clearly*, then run a full cycle before evaluating.

### Author-warned failure modes (Sherwood's counter-examples)

- **ce08** — acting too fast on a time-delayed loop (the hotel-shower
  amplification). The reflex to "do something" before the prior
  action has worked through is the most common over-correction
  failure. Sherwood prescribes the cycle-length wait *even when it
  feels like you're being negligent*.
- **ce31** — confusing detail complexity (lots of moving parts in a
  spreadsheet) with dynamic complexity (delayed loop behavior). A
  manager who responds to a swinging metric by *adding more inputs to
  the spreadsheet* is treating dynamic dysfunction as a precision
  problem. More precision doesn't shorten the lag; only structural
  changes to the loop do.

### Author's blind spots / period limitations

- **BoE / Greenspan macro examples are period-dated** (BOOK_OVERVIEW
  Critical #7). The MPC under Sir Edward George is a 1997-2003
  artifact; post-2008 unconventional monetary policy, post-2021
  inflation regime change, and central-bank credibility crises all
  postdate the example. Use the *structural* lesson (small moves,
  long intervals) without inheriting the institutional confidence.
- **Manager-as-protagonist framing** (Critical #3): the procedure
  assumes one person can authorize "do nothing for two quarters."
  In organizations measured on quarterly OKRs, doing nothing reads
  as failure even when it is correct; the procedure produces a
  diagnosis the organization may be structurally unable to act on.
- **No engagement with stochastic noise.** Real metrics have both
  endogenous oscillation and exogenous noise; Sherwood treats
  oscillation as cleanly endogenous. In practice the manager's job
  starts with separating signal from noise — which Sherwood under-
  serves. Pair with basic SPC / control-chart literacy.

### Easily-confused neighboring methodologies

- **PID control theory**: V/T/A is informally PID with P-only
  control + lag awareness. PID adds integral and derivative terms
  that Sherwood ignores. For high-stakes industrial control, use
  PID; for management decisions, Sherwood's coarser version is
  usually right-sized.
- **Statistical Process Control (Shewhart / Deming)**: SPC tells
  you whether a metric is within-control-limits (don't act) vs
  out-of-control (act). It is the empirical complement to V/T/A's
  structural diagnosis — V/T/A explains *why* a system might
  oscillate; SPC tells you *whether* the observed variation is
  noise vs signal. Use both.
- **Lean / Kanban WIP limits**: a different way to attack the same
  oscillation problem (cap WIP so the system can't be perturbed
  faster than it converges).

## Related skills

- **depends-on `loop-and-link-primitives`** — the template is *the*
  canonical balancing loop; you must already be able to distinguish B
  from R (even-O / odd-O rule) and sign each link S/O before applying
  the variance/target/action structure to a real situation, otherwise
  you risk pulling a B-style lever inside an R-loop.
- **depends-on `cld-craft`** — the four-node loop has to be drawn
  cleanly (nouns, S/O labels in pen, dangle for the target) for the
  do-nothing-under-oscillation diagnostic to read off the diagram.
  Rule 8 ("label every arrow in pen") is what makes the variance
  direction explicit in Step 1.
- **contrasts-with `limits-to-growth-take-the-brakes-off`** — both
  intervene on systems behaving badly, but the intervention
  philosophy inverts: variance/target/action says "wait and let the
  B-loop converge" (or attack the delay); limits-to-growth says
  "actively relieve the B-loop that is braking the R-loop." Choose
  by asking whether the unwanted behavior is *oscillation around a
  target* (this skill) or *deceleration of a growth engine*
  (limits-to-growth).

## Audit metadata

> Source-unit codes (f10/p14/p15/p21/p22/ce08/ce31/c08/c09/c10/g12/g18/g22/g45)
> refer to Stage-1.5 verified.md entries. See
> `<plugin-root>/references/VERIFIED.md`.

- **Verification status**: V1 ✓ (4 domains: plumbing, ops mgmt, central banking, multi-lever strategy) / V2 ✓ (novel NPS swing diagnosis) / V3 ✓ ("do nothing" is counter-cultural; endogenous-oscillation recognition is specialized)
- **Source units merged**: f10, p14, p15, p21, p22, ce08, ce31, c08, c09, c10, g12, g18, g22, g45
- **Distilled at**: 2026-05-11
- **Polished at**: 2026-05-12 (Profile B standalone polish; 5 applicable improvements applied; cases extracted to `references/cases.md`)
- **Output language**: body — English; metadata — English
