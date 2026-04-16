---
name: position-sizing-and-risk
description: Kelly criterion, risk budgeting, vol-targeting — how to translate conviction into portfolio weight
tier: 2
layer: portfolio
---

# Position Sizing and Risk

Fully self-contained Tier 2 standard covering how to **translate a
verdict and conviction grade into an actual portfolio weight**. This
file is the SSOT for all position-sizing calculations, capital
allocation decisions, and risk-limit rules produced by the
investing-team.

Tier 2 because this topic contains two classes of systematic error:
(a) LLMs routinely mis-state the Kelly formula, reducing it to
f* = p − q and dropping the odds parameter, which produces
incorrect weights whenever b ≠ 1; (b) VaR is commonly described as
"worst-case loss" when it is the *threshold* loss at the X%
confidence level — the tail beyond that threshold is what VaR
explicitly excludes, and it is precisely that tail that causes ruin.
Body below spells out both formulas in full operational detail so
workers can size positions correctly without the cited sources in hand.

**Scope**: conviction-to-weight translation, sizing calculation,
risk limits, and failure modes. Verdict grading belongs to
`decision-framework-and-verdict.md`; portfolio-level risk budgeting
and correlation management belong to
`investment-portfolio-construction.md`.

## Primary Sources

- John L. Kelly Jr. (1956) "A New Interpretation of Information
  Rate." *Bell System Technical Journal* 35(4): 917–926. The Kelly
  criterion in its exact form: f* = (bp − q) / b, where f* is the
  fraction of capital to allocate, b is the net odds (upside divided
  by downside), p is the probability of the favorable outcome, and
  q = 1 − p. Maximizes the expected logarithm of wealth, which is
  equivalent to maximizing the long-run compounding rate. The
  information-theoretic derivation connects bet sizing to Shannon
  channel capacity.
- Edward O. Thorp (2006) "The Kelly Criterion in Blackjack, Sports
  Betting, and the Stock Market." In: S.A. Zenios & W.T. Ziemba
  (eds.), *Handbook of Asset and Liability Management*, Vol. 1,
  pp. 385–428. North-Holland / Elsevier. Extends Kelly to
  continuous-time finance; introduces fractional Kelly (f*/2 or
  f*/4) as the practical compromise between growth maximization and
  drawdown reduction. Thorp's core empirical finding: full Kelly
  produces drawdowns that are psychologically and institutionally
  unsustainable; f*/2 loses roughly half the long-run edge but cuts
  drawdown severity by approximately 75%. Fractional Kelly is a
  correction for probability mis-estimation, not a risk-aversion
  parameter.
- CFA Institute (2024) *CFA Program Curriculum, Level 3, Volume 6:
  Portfolio Management and Wealth Planning*. CFA Institute. Risk
  budgeting: allocate risk (not capital) across positions; marginal
  contribution to portfolio VaR; correlation-aware position sizing.
  The canonical practitioner framework for multi-asset, multi-factor
  portfolios. Risk budgeting operates in VaR-contribution space,
  not notional-weight space.
- Nassim Nicholas Taleb (2007) *The Black Swan: The Impact of the
  Highly Improbable*. Random House. Ch. 15 "The Bell Curve, That
  Great Intellectual Fraud." VaR critique: real return distributions
  have fat tails that normal-distribution models cannot capture; the
  1% tail events that VaR explicitly excludes by construction are
  precisely the events that cause portfolio ruin. VaR does not
  measure worst-case loss; it measures the loss at the X% confidence
  threshold and says nothing about what happens beyond it.
- Nassim Nicholas Taleb, Elie Canetti, Tidiane Kinda, Elena
  Loukoianova, Christian Schmieder (2012) "A New Heuristic Measure
  of Fragility and Tail Risks: Application to Stress Testing." IMF
  Working Paper WP/12/216. Formalizes fragility detection: a system
  is fragile if it is more harmed by negative deviations than it is
  helped by positive deviations of equal magnitude. This asymmetry
  is the basis for asymmetric sizing — when the downside of a
  position can exceed the upside by construction (leveraged
  positions, short options), normal Kelly sizing is invalid.
- Ralph Vince (1992) *The Mathematics of Money Management: Risk
  Analysis Techniques for Traders*. Wiley. Optimal-f: the
  empirical equivalent of Kelly for trading, derived from the
  geometric mean of the trade distribution rather than from a
  probability estimate. Vince also provides the terminal ruin
  probability formula and establishes the relationship between
  leverage and the probability of drawdown-to-zero.

## Critical Attribution Corrections

### Kelly formula is mis-stated as f* = p − q

The most common error in practitioner and AI-generated content is
reducing Kelly to f* = p − q. This simplified form is correct only
when b = 1 (i.e., when the upside and downside are equal, as in an
even-money coin flip). The **correct and general form** from Kelly
1956 is:

```
f* = (bp − q) / b
```

where b is the net odds (if you risk $1 and win, you receive $b
back in profit), p is the probability of the favorable outcome, and
q = 1 − p. When b ≠ 1 — which is always the case in equity
investing — the simplified form produces incorrect weights. For
example, if p = 0.6 and b = 0.5 (asymmetric downside), the
simplified f* = p − q = 0.2, but the correct f* = (0.5 × 0.6 −
0.4) / 0.5 = −0.2, meaning the position should not be taken at all.
Never use f* = p − q outside the even-money special case.

### Fractional Kelly is not a risk-aversion parameter

Practitioner commentary often frames fractional Kelly (f*/2, f*/4)
as a way to express "how risk-averse you are" or "how conservative
you want to be." This framing is wrong. Thorp 2006 derives
fractional Kelly as a **practical correction for probability
mis-estimation**. Kelly's formula is exquisitely sensitive to errors
in p and b: overestimating p by 5 percentage points can more than
double the Kelly-implied position size, and systematic
over-confidence in probability estimates is the norm, not the
exception. Fractional Kelly survives estimation error. The
justification is not subjective risk tolerance — it is that p and b
are never known with precision, and f*/2 or f*/4 remains solvent
across a wide range of estimation errors while f* does not.

### VaR does not measure worst-case loss

A common and dangerous misstatement: "our 95% 1-day VaR is $X,
meaning our worst-case loss is $X." This is wrong in two ways.
First, VaR at the 95% confidence level means the loss will exceed
$X on 5% of trading days — roughly 12–13 days per year. Second, and
more critically, VaR says nothing about how large the loss is when
it exceeds $X. The distribution of losses in the 5% tail is exactly
what VaR excludes. Taleb 2007 documents that fat-tailed return
distributions produce losses in that excluded tail that are orders
of magnitude larger than the VaR threshold. Correct statement: "our
95% 1-day VaR is $X, meaning on 5% of days the loss is expected to
exceed this amount; we do not know from VaR alone how far it will
exceed it." Use CVaR (Conditional VaR / Expected Shortfall) if you
need a measure of average loss in the tail.

## Kelly Criterion — Exact Formula and Operational Mapping

### The Formula

Kelly 1956 derives the optimal fraction of capital to allocate to a
bet with known odds and probability:

```
f* = (bp − q) / b
```

Variables:
- **f*** — optimal fraction of current capital to allocate
- **b** — net odds received per unit risked (if you risk $1 and win,
  you receive $b profit)
- **p** — subjective probability that the thesis is correct
- **q** — probability that the thesis is wrong; q = 1 − p

The formula maximizes E[log(wealth)] — the expected logarithm of
terminal wealth — which is equivalent to maximizing the long-run
compounding rate. A negative f* means the Kelly criterion recommends
not taking the position at all.

### Mapping to Stock Investing

In equity investing, b and p are not given — they must be estimated
from the thesis:

| Kelly variable | Stock investing interpretation |
|---|---|
| **b** | Upside / downside ratio: if the stock reaches fair value, what is the gain? Divided by the expected loss if the thesis is wrong. Example: 30% upside to fair value, 15% downside to stop or thesis-invalidation → b = 30/15 = 2.0 |
| **p** | Subjective probability that the thesis is correct within the investment horizon. Must be explicitly stated; no historical base rate can substitute for the analyst's judgment on the specific idea. |
| **q** | 1 − p; the probability of being wrong |

**Example calculation**: A stock has 40% upside to fair value and
20% downside if the thesis breaks. Analyst assigns 60% probability
to the thesis being correct.

```
b = 40 / 20 = 2.0
p = 0.60
q = 0.40

f* = (2.0 × 0.60 − 0.40) / 2.0
f* = (1.20 − 0.40) / 2.0
f* = 0.80 / 2.0
f* = 0.40  →  40% of capital
```

Full Kelly says allocate 40% of capital. This is the theoretical
maximum-compounding allocation. In practice, never use full Kelly
(see Fractional Kelly below).

### Full Kelly Is Theoretically Optimal But Practically Dangerous

Kelly 1956's proof requires exact knowledge of p and b. In stock
investing, both are estimates. Thorp 2006 shows that a 5-percentage-
point overestimate of p (estimating 0.60 when the true probability
is 0.55) causes Kelly to over-size by approximately 20%. A 10-point
overestimate can cause the Kelly fraction to exceed 1.0 (leveraged
exposure). Over-sizing relative to true Kelly produces worse
compounding outcomes than the corresponding fractional Kelly, and
can cause drawdowns from which full recovery is mathematically
unlikely under repeated play. The Kelly bet is also the *boundary*
of sensible play: above full Kelly, expected log-wealth declines and
ruin probability increases.

### Fractional Kelly — The Standard Practitioner Approach

Thorp 2006 recommends f*/2 or f*/4 for individual stock positions
as the standard compromise:

| Kelly fraction | Position size (from example above) | Rationale |
|---|---|---|
| **Full Kelly (f*)** | 40% | Optimal only if p and b are exactly known; catastrophic if overestimated |
| **Half Kelly (f*/2)** | 20% | Loses ~half the edge but cuts drawdown severity ~75%; suitable for concentrated portfolios with high-quality estimates |
| **Quarter Kelly (f*/4)** | 10% | Robust to wide estimation error; standard for individual stock positions in a diversified fund |

**Hard cap**: regardless of Kelly output, never exceed 20–25% of
portfolio in a single position. Kelly at full conviction on an
apparently high-edge idea can still output > 50% in theory; this
output indicates either an error in the probability estimate or an
extreme concentration that violates basic portfolio construction
principles. Cap the output, not the formula.

## Three Practical Sizing Methods

| Method | Formula / Rule | Inputs Required | Use When |
|---|---|---|---|
| **Fractional Kelly** | f*/4 for individual positions; f*/2 for highest-conviction concentrated portfolios | Estimated upside (b numerator), downside (b denominator), probability p | High-conviction ideas where analyst has explicitly estimated p and b from the thesis |
| **Volatility targeting** | weight = target_vol / position_vol | Target portfolio volatility (%), position annualized volatility (%) | Normalizing across assets with very different volatility profiles; replaces ad hoc "feels riskier" judgments |
| **Risk budgeting (CFA)** | Allocate % of portfolio VaR contribution, not notional capital | Portfolio VaR, marginal VaR contribution per position, correlation matrix | Multi-asset or multi-factor portfolios where correlation structure matters; risk must be measured in the same units across all positions |

### Fractional Kelly — Step by Step

1. **State the thesis explicitly**: what has to be true for the
   investment to work?
2. **Estimate b**: what is the price target if right? What is the
   expected loss if wrong? b = (price target − current) / (current
   − stop or thesis-invalidation price).
3. **Estimate p**: what probability do you assign to the thesis
   being correct within the investment horizon? Write a number.
   Do not leave it implicit.
4. **Apply the formula**: f* = (bp − q) / b.
5. **Apply fractional Kelly**: use f*/4 as the starting allocation.
6. **Apply hard cap**: if f*/4 > 15%, cap at 15% (Grade A) or lower
   (see Conviction Grade map below).
7. **Failure mode**: the main failure is treating p as objective
   when it is subjective. Analysts systematically overstate p;
   using f*/4 rather than f* partially corrects for this bias.

### Volatility Targeting — Step by Step

Volatility targeting normalizes positions so each contributes
equally to portfolio volatility, rather than allowing high-
volatility positions to dominate.

```
weight = target_portfolio_vol / position_annualized_vol
```

**Example**: target portfolio volatility = 12% annualized.
A stock with 30% annualized volatility:

```
weight = 12% / 30% = 40%
```

But a 40% single-position weight violates the hard cap. Apply the
hard cap after volatility targeting:

```
weight = min(target_vol / position_vol, hard_cap_for_grade)
```

**Failure mode**: volatility targeting treats all assets as
interchangeable risk units. It ignores the direction of the thesis,
the quality of the edge, and the correlation structure. A 30%-vol
stock with a strong fundamental thesis and a 30%-vol stock with a
weak speculative thesis receive the same weight. Volatility
targeting should be combined with conviction grading, not substituted
for it.

### Risk Budgeting — Step by Step (CFA Level 3)

Risk budgeting allocates a percentage of total portfolio VaR to each
position, rather than allocating capital. Two positions with the
same notional weight can have very different risk contributions if
their volatilities and correlations differ.

1. **Set the portfolio-level risk budget**: e.g., total portfolio
   VaR ≤ 2% per day at 95% confidence.
2. **Decompose VaR by position**: each position has a Marginal
   Contribution to VaR (MCVaR), which depends on its own volatility
   and its correlation with the rest of the portfolio.
3. **Allocate risk budget**: assign each position a fraction of the
   total risk budget. A position contributing 30% of portfolio VaR
   is using 30% of the risk budget.
4. **Rebalance**: if a position's VaR contribution drifts above its
   budget (e.g., because volatility increased or correlation shifted),
   trim the position.

**Failure mode**: risk budgeting uses VaR as its measurement unit.
Per Taleb 2007, VaR underestimates tail risk in fat-tailed
distributions. A position that consumes its VaR budget under the
normal-distribution assumption may consume multiples of that budget
in an actual tail event. Use risk budgeting for the day-to-day
allocation structure, but always overlay a stress test: what happens
to each position's contribution if volatility doubles and
correlations converge to 1?

## VaR — What It Is and Why It Fails

### What VaR Measures

Value at Risk answers a specific, narrow question: "at the X%
confidence level, over Y days, assuming returns are normally
distributed, what is the maximum loss?" A 95% 1-day VaR of $100K
means: "under normal-distribution assumptions, there is a 95%
probability that the loss over the next trading day does not exceed
$100K."

VaR does NOT answer:
- What is the maximum possible loss?
- What is the loss when the threshold is breached?
- What happens in the 5% of days when the loss exceeds the VaR?

### Taleb's Critique — Fat Tails Invalidate VaR-Based Sizing

Taleb 2007 Ch. 15 documents that financial return distributions
have fatter tails than the normal distribution assumes. The 1% of
observations that fall outside the 99% VaR threshold are not drawn
from the same bell-curve distribution — they are drawn from a power-
law or heavy-tailed distribution where losses can be 10x to 100x the
VaR level. When position sizing is derived from a VaR model, the
model is implicitly saying "the tail beyond this threshold doesn't
exist or is negligible." Taleb's critique is precisely that this tail
is where ruin occurs.

Taleb-Canetti et al. 2012 formalizes this as **fragility**: a
position is fragile if it is harmed more by a negative deviation of
size ε than it is helped by a positive deviation of the same size ε.
A short gamma position (short options) is the archetype: it gains
small amounts when markets are calm, then loses catastrophically
when volatility spikes. VaR-based sizing for such positions
systematically underestimates required capital.

### How to Use VaR Correctly

VaR is a **floor check**, not a ceiling. Use it to answer: "does
this position consume so much VaR budget that it already violates
portfolio-level limits before considering tail risk?" If yes, size
down. But never use VaR as the primary justification for sizing up.

Supplement VaR with:
- **Scenario analysis**: what happens if the thesis is completely
  wrong AND the broad market falls 20% simultaneously? This stress
  test captures correlation convergence (correlations go to 1 in
  a crash) and fat tails (the 20% market decline is a multi-sigma
  event that VaR assigns near-zero probability to).
- **CVaR / Expected Shortfall**: the average loss conditional on
  exceeding the VaR threshold. CVaR is a coherent risk measure that
  VaR is not; it does measure something about the tail.
- **Fragility check** (Taleb-Canetti 2012): for any position with
  asymmetric payoffs, test whether a negative deviation of size ε
  causes more P&L damage than a positive deviation of the same size
  causes P&L benefit. If yes, the position is fragile and requires
  barbell treatment (see Asymmetric Risk below).

## Conviction-Grade to Size Map

The conviction grade is assigned by the verdict process in
`decision-framework-and-verdict.md`. This map translates that grade
into position-sizing bounds.

| Conviction Grade | Max Single Position | Kelly Fraction | Note |
|---|---|---|---|
| **Grade A** | up to 15% of portfolio | f*/2 Kelly | High conviction: multiple independent valuation methods converge; upside and downside explicitly estimated; scenario analysis complete |
| **Grade B** | up to 8% of portfolio | f*/4 Kelly | Partial conviction: primary thesis clear but key uncertainties unresolved; one or more valuation methods incomplete |
| **Grade C** | 1–3% fixed (no Kelly) | Fixed allocation | Speculative or early-stage; sized for lottery-ticket payoff profile; do not increase if it moves against you |

### Grade Definitions

**Grade A** requires all of the following, per
`decision-framework-and-verdict.md`:
- Verdict: BUY or STRONG BUY
- At least two independent valuation methods applied
- Upside and downside explicitly estimated with probability assigned
- Thesis written out: what has to be true, what would make it wrong
- Scenario analysis run

**Grade B** requires:
- Verdict: BUY
- At least one valuation method applied
- Upside and downside estimated; probability may be qualitative
- Thesis stated; full stress test not required but key risk factors
  named

**Grade C** is for ideas that do not yet meet Grade B criteria but
warrant a position: early-stage companies, turnarounds with binary
outcomes, special situations. The 1–3% fixed size reflects "I am
willing to lose this entire position if wrong." Do not calculate
Kelly for Grade C; the uncertainty in p and b is too large for
Kelly to be meaningful. Apply the barbell rule instead (see
Asymmetric Risk below).

### Anti-Drift

Do NOT express Grade C sizing as "a small Kelly fraction." The
uncertainty in p and b for Grade C ideas means Kelly is not
operational. Fix the allocation at 1–3% and accept that the
allocation is a defined loss limit, not a compounding-optimization
calculation. Upgrading from Grade C to Grade B requires going
through the full valuation and thesis documentation process —
it is not automatic if the stock price moves in your favor.

## Asymmetric Risk and the Barbell Heuristic (Taleb Fragility)

### When Normal Sizing Rules Do Not Apply

Standard Kelly and risk budgeting both assume a roughly symmetric
payoff structure: you can lose approximately b_downside or gain
approximately b_upside. When the worst-case loss is structurally
unbounded or much larger than the normal-case loss, these formulas
are invalid:

- **Levered positions**: if the position can be subject to a margin
  call, the downside is not the price of the underlying falling to
  zero — it is an unlimited cash demand that can exceed the
  original position size.
- **Short options positions** (naked calls, short puts): gain is
  bounded by the premium received; loss is theoretically unlimited
  (calls) or very large relative to premium (puts in a crash).
- **Concentrated single-stock exposure**: if the stock is a single
  company and that company fails, loss = 100% of position. Kelly
  handles this case mathematically, but the human tendency to
  over-estimate p for high-conviction ideas makes full Kelly on a
  binary position extremely dangerous.

For all three categories: apply the Taleb-Canetti 2012 fragility
test. If negative deviations harm the position more than positive
deviations of equal size help it, the position is fragile and
requires barbell treatment.

### Barbell Heuristic

The barbell strategy (referenced in `investment-portfolio-construction.md`)
resolves asymmetric risk by separating the portfolio into:
- A large, conservative allocation (bonds, cash) that is robust to
  bad scenarios
- A small, speculative allocation where total loss of the
  speculative portion is defined in advance

For sizing a fragile or speculative position under the barbell rule:

```
position_size = X% of portfolio / probability_of_total_loss
```

Where X% is the **maximum portfolio loss you can tolerate if this
idea goes to zero**. If you are willing to lose 2% of your portfolio
on a high-risk idea, and you estimate the probability of total loss
at 50%, then:

```
position_size = 2% / 0.50 = 4%
```

This allocation means: in the 50% of scenarios where the position
goes to zero, you lose 2% of portfolio. In the 50% of scenarios
where it does not go to zero, the expected upside justifies the
allocation. The key discipline is defining X% in advance and never
exceeding it.

### Hard Limit for Levered and Short-Options Positions

Never use standard Kelly or volatility-targeting formulas for
levered positions or short-options structures without explicitly
modeling the maximum possible loss under a fat-tail scenario. If
the maximum possible loss under a 3-sigma adverse scenario is not
bounded by a value you can tolerate losing in full, do not take the
position — or reduce size until it is.

## Sizing vs. Entry Timing — Critical Distinction

### The Averaging-Down Trap

A common failure mode: starting with a small position "to test the
thesis," then adding aggressively when the price falls because "now
it's even cheaper." This is not a sizing decision — it is a disguised
entry-timing decision with no defined exit. Its pathology is that
it increases exposure precisely when the market is providing evidence
against the thesis.

**Averaging down is valid only under both of the following
conditions simultaneously**:
1. The thesis is explicitly reviewed and remains intact (the price
   decline is not providing new information that updates the thesis).
2. The lower price creates a materially better margin of safety —
   i.e., the new Kelly calculation at the lower price produces a
   higher f*, not merely "it's cheaper."

If the price declines because the thesis is being invalidated (e.g.,
earnings miss, regulatory change, management change that was a key
thesis pillar), adding to the position is not averaging down — it
is compounding an error.

### Correct Sequencing

1. **Thesis formation**: write the thesis, estimate upside/downside,
   assign p, calculate f*, apply fractional Kelly, set conviction
   grade, cap to grade limit. This produces the **target position
   size**.
2. **Entry timing**: decide how to build to the target size —
   all at once, over several days, scaled in as the thesis
   confirms. Entry timing does not change the target size.
3. **Thesis review**: if price moves against you, review the thesis
   explicitly. If the thesis is intact and the new price creates
   better value, recalculate f* at the new price. If the new f*
   is materially higher and the new price genuinely improves the
   margin of safety, adding is justified up to the grade cap. If
   the thesis is impaired, reduce or exit.

Do NOT conflate step 2 (entry timing) with step 3 (thesis review).
"I'll start small and add when it falls" is only valid if you have
pre-committed to a clear thesis-review process at the lower price
and have defined what "intact" looks like. Without that pre-
commitment, adding on price decline is a behavioral bias, not a
disciplined sizing rule.

### Anti-Drift

Never describe "starting small" as a form of risk management unless
the context explicitly includes a defined thesis-review trigger and
target-size cap. Risk management is the position size you are
willing to hold given the thesis; entry timing is the schedule for
reaching that size. They are separate decisions that should not be
used to justify each other.

## Putting It Together — Sizing Workflow

The complete sizing workflow from thesis to weight:

```
1. Complete thesis document
   └── Per decision-framework-and-verdict.md:
       - Thesis narrative (what must be true)
       - Explicit upside estimate → b numerator
       - Explicit downside estimate → b denominator
       - Probability estimate p (written down, not implicit)
       - Conviction grade (A / B / C)

2. Calculate b and f*
   └── b = upside / downside
       f* = (b × p − q) / b
       where q = 1 − p

3. Apply fractional Kelly
   └── Grade A: use f*/2; cap at 15%
       Grade B: use f*/4; cap at 8%
       Grade C: ignore Kelly; use 1–3% fixed

4. Check for asymmetric risk (fragility test)
   └── Is worst-case loss unbounded?
       Is position leveraged or short-options?
       If yes: apply barbell rule instead of step 3

5. VaR floor check
   └── Does this position consume more than its share of
       portfolio VaR budget?
       If yes: trim to budget; note this as a risk constraint
       Do NOT use VaR to justify increasing size

6. Stress test
   └── What happens if thesis is wrong AND market falls 20%?
       Is the portfolio-level loss tolerable?
       If no: reduce position before entry

7. Document the final position size and the key inputs (b, p, f*)
   └── This creates a traceable record for later thesis review
```

## Relationship to Other Standards

- **Verdict and conviction grade** are defined in
  `decision-framework-and-verdict.md`. Conviction grades A / B / C
  used in the size map above come from that standard. The investing-
  team workflow is: verdict first, then sizing. Never size first
  and then reverse-engineer a conviction grade.
- **Portfolio-level risk** — total portfolio VaR, correlation
  structure, barbell construction, and diversification rules — are
  in `investment-portfolio-construction.md`. This standard governs
  individual position sizing; the portfolio standard governs how
  multiple positions combine.
- **Security valuation** — the upside and downside estimates
  that feed the Kelly formula (b numerator and denominator) are
  produced by the valuation process in
  `investment-security-valuation.md`. Kelly sizing without a
  valuation-based b estimate is not operational.
- **Macro regime** — `investment-macro-regime.md` provides the L1
  regime context that may warrant regime-level sizing adjustments
  (e.g., reducing gross exposure in Dalio Bubble phase regardless
  of individual-position Kelly outputs).
