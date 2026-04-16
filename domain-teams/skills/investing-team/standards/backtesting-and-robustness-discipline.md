---
name: backtesting-and-robustness-discipline
description: Backtest overfitting detection, out-of-sample discipline, and multiple-testing penalty — per López de Prado and Harvey-Liu-Zhu
tier: 2
layer: validation
---

# Backtesting and Robustness Discipline

Tier 2 standard covering the **validation layer** of any
backtested strategy or screened factor presented in an
investing-team deliverable. This file is the SSOT for
backtest methodology claims: what constitutes a valid
out-of-sample test, how to disclose the number of trials
tested, how to apply the multiple-testing penalty, how
to interpret the Sharpe ratio correctly, and what the
minimum five-step validation protocol is before presenting
a strategy to a principal.

Tier 2 because this is a **methodological discipline standard**.
The failure mode is not factual error but **statistical
self-deception** — presenting an in-sample pattern as a
confirmed strategy. The literature on this is unambiguous:
backtests with enough parameters always find patterns in
noise. This standard enforces the disciplines that separate
genuine strategy research from data mining.

**Scope**: any quantitative strategy, factor screen, or
backtest result presented by investing-team workers.
Applies equally to long/short equity screens, macro rotation
signals, and options / derivatives strategies. Fundamental
analysis without a quantified back-test is out of scope
for this standard (though look-ahead bias rules still apply).

## Primary Sources

- **Marcos López de Prado** (2018). *Advances in Financial Machine Learning*. Wiley. Ch. 7 "Cross-Validation in Finance." ISBN 978-1-119-48231-2. The canonical quantitative-finance treatment of backtest overfitting: combinatorial purged cross-validation (CPCV), the deflated Sharpe ratio, and why standard train/test splits fail on financial time series due to serial dependence and label-leakage.
- **Campbell R. Harvey, Yan Liu & Heqing Zhu** (2016). "...and the Cross-Section of Expected Returns." *Review of Financial Studies* 29(1): 5–68. Oxford University Press. doi:10.1093/rfs/hhv059. Establishes that most published factor returns are likely false discoveries given the cumulative number of factors tested. The paper that raised the correct t-statistic threshold for novel factors from 2.0 to 3.0 and introduced Bonferroni / Benjamini-Hochberg corrections into factor research practice.
- **Andrew W. Lo** (2002). "The Statistics of Sharpe Ratios." *Financial Analysts Journal* 58(4): 36–52. CFA Institute. doi:10.2469/faj.v58.n4.2453. The standard annualized Sharpe ratio is distribution-dependent and overstated when returns are non-i.i.d. (autocorrelated, fat-tailed, or skewed). Provides the corrected asymptotic distribution. The correction is non-trivial for trend-following and momentum strategies with high autocorrelation.
- **David H. Bailey, Jonathan M. Borwein, Marcos López de Prado & Qiji Jim Zhu** (2014). "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance." *Notices of the American Mathematical Society* 61(5): 458–471. doi:10.1090/noti1105. Defines the Probability of Backtest Overfitting (PBO): as the number of trials grows relative to sample size, PBO approaches 1. The paper that quantified what practitioners knew qualitatively. Freely available at ams.org.
- **Robert D. Arnott, Campbell R. Harvey & Harry Markowitz** (2019). "A Backtesting Protocol in the Era of Machine Learning." *Journal of Financial Data Science* 1(1): 64–74. doi:10.3905/jfds.2019.1.1.064. The most accessible practitioner checklist for avoiding data mining bias — five questions every strategy researcher must answer before reporting results. Note: Harry Markowitz here is the late Nobel laureate (1927–2023), co-author on this specific paper.

## Critical Attribution Corrections

### Harvey, Liu & Zhu 2016 is about factor research, not ML per se

HLZ 2016 is frequently cited as a "machine learning overfitting"
paper. It is not. The paper is a **factor-zoo critique**: given the
~300+ factors published in academic finance by 2012, the classical
p < 0.05 (t ≥ 2.0) threshold is insufficient because researchers
collectively perform hundreds of hypothesis tests on overlapping
data. The insight applies to any multi-trial search — manual
screening, algorithmic search, or ML grid search. The paper's
t ≥ 3.0 recommendation for "new" factors is grounded in simulation
of the accumulated multiple-testing burden, not in ML-specific
theory.

### The t ≥ 3.0 threshold applies to novel factors, not all tests

HLZ 2016's t ≥ 3.0 recommendation is the bar for claiming a
**genuinely new factor** contributes to the cross-section of
expected returns. It is not a universal threshold for all
statistical tests. HLZ explicitly propose different thresholds
depending on whether the factor is (a) a replication of a
published factor (lower threshold acceptable), (b) a variation
on a published factor (intermediate threshold), or (c) a truly
novel claim (t ≥ 3.0 minimum, Bonferroni-adjusted ideally).
Applying t ≥ 3.0 as a blanket rule to single-hypothesis tests
is an overcorrection.

### Bailey et al. 2014 is a *Notices* paper, not a journal article

The Bailey-Borwein-López de Prado-Zhu (BBLZ) 2014 paper appeared
in the *Notices of the American Mathematical Society* — a broad-
audience mathematics journal, not a peer-reviewed finance journal.
Its reception in the quantitative finance community has been
positive, but it should be cited as it is: a rigorous mathematical
exposition in a mathematics notices publication, subsequently
expanded in López de Prado 2018. Do not cite it as if it appeared
in a finance peer-reviewed journal.

### Deflated Sharpe Ratio is Bailey & López de Prado, not just López de Prado

The Deflated Sharpe Ratio (DSR) was introduced in:

**David H. Bailey & Marcos López de Prado** (2014). "The Deflated
Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting,
and Non-Normality." *Journal of Portfolio Management* 40(5): 94–107.
doi:10.3905/jpm.2014.40.5.094.

Attribution to López de Prado alone is incomplete. Both Bailey
and López de Prado are co-originators of DSR.

### Lo 2002 corrects the *annualized* Sharpe, not the period Sharpe

Lo (2002) corrects the **annualization formula** applied to
Sharpe ratios when returns are autocorrelated. The standard
annualization multiplies the period Sharpe by √T (where T =
number of periods per year). This is correct only when returns
are i.i.d. (independent and identically distributed). For
autocorrelated return series (trend-following, momentum,
mean-reversion), Lo provides the corrected multiplier that
accounts for the autocorrelation structure. The correction
can cause the annualized Sharpe to be **substantially lower**
for strategies with positive autocorrelation (trend-following)
and somewhat lower for strategies with negative autocorrelation.

### Arnott, Harvey & Markowitz 2019 does NOT propose the DSR or CPCV

Arnott et al. 2019 is a **practitioner-level protocol paper** —
five questions / five practices for clean backtesting. It does not
introduce new statistical tools. Workers sometimes conflate it with
Bailey-López de Prado DSR (2014) or López de Prado CPCV (2018).
Cite Arnott et al. 2019 specifically for the five-step disclosure
protocol; cite the earlier papers for the underlying statistical
tools.

## Why Backtests Fail: The Core Problem

A backtest is an optimization over historical data. With enough
free parameters, any optimizer will find combinations that fit
historical noise. This is not a failure of implementation — it is
a mathematical certainty.

### The Law of Large Numbers, Working Against You

Given *N* independent random strategies tested on a fixed dataset,
the expected maximum Sharpe ratio from the best strategy scales
as **√(2 ln N)** (a standard result from order statistics for
normal variates). For N = 100 strategies, the expected maximum
random Sharpe is ~√(2 ln 100) ≈ 3.03 — higher than the HLZ
t ≥ 3.0 bar for "real" factors. A researcher who tests 100
parameter combinations on in-sample data and presents the best
as a "strategy" has proven nothing.

### Probability of Backtest Overfitting (Bailey et al. 2014)

PBO is defined as the probability that the strategy with the
highest in-sample (IS) performance will have below-median
out-of-sample (OOS) performance. Bailey et al. formalize PBO
via combinatorial testing: partition the total sample into *S*
non-overlapping sub-periods; form all C(S, S/2) combinations
of training / test splits; compute the fraction where the
IS-optimal trial performs below median OOS.

**Key findings from Bailey et al. 2014**:
- PBO is strictly between 0 and 1 for any finite dataset.
- PBO approaches 1 as the number of trials grows relative to
  sample size.
- A strategy with high IS Sharpe is NOT evidence of a genuine
  edge when PBO is high.

**Rule**: every quantitative screen or strategy must report
the number of parameter combinations tested. That number
is load-bearing for the validity of any IS result.

## Multiple Testing Penalty (Harvey, Liu & Zhu 2016)

### The Factor Zoo Problem

Academic finance had published over 300 distinct risk factors
claiming to predict the cross-section of stock returns by 2012
(Harvey, Liu & Zhu count 316 in their Table 1). If researchers
collectively test hundreds of factors on overlapping datasets
with overlapping sample periods, classical p < 0.05 significance
is nearly meaningless — by construction, 5% of 316 tests will
appear "significant" by chance even if all factors are pure noise.

### Adjusted Thresholds (HLZ 2016 Table 2)

HLZ propose **minimum t-statistic thresholds** that account
for the cumulative multiple-testing burden in factor research:

| Context | t-statistic threshold | Approximate p-value |
|---|---|---|
| First factor ever tested | 2.0 | < 0.05 |
| Factor published before 1991 (early literature) | 2.57 | < 0.01 |
| Factor in recent literature (post-2002) | 3.0 | < 0.003 |
| Novel claim with extensive data mining | 3.0+ (Bonferroni-adjusted) | < 0.003 |

For investing-team purposes: if you screened 50 criteria and
selected the best-performing one, you cannot present it with a
classical t ≥ 2.0 threshold. Apply the correction.

### Corrections to Apply

**Bonferroni correction**: most conservative. Divide the
significance threshold α by the number of tests *m*. For
α = 0.05 and m = 50 tests: threshold becomes p < 0.001,
t > ~3.3.

**Benjamini-Hochberg (BH) FDR control**: less conservative;
controls the **false discovery rate** (expected proportion of
false discoveries among all rejections) rather than the
family-wise error rate. Appropriate when multiple discoveries
are expected and the cost of each false positive is comparable
to the cost of each false negative. HLZ also cite Benjamini-
Hochberg-Yekutieli (BHY) for correlated tests.

**Applying to investing-team memos**: every memo that presents
a backtested screen must disclose:
1. How many criteria / parameter combinations were evaluated
2. Which correction was applied (Bonferroni, BH, none with justification)
3. The adjusted significance threshold used

## Out-of-Sample Discipline (López de Prado 2018 Ch. 7)

### The Fundamental Rule: Use the Test Set Once

The out-of-sample (OOS) test set exists to provide an unbiased
estimate of strategy performance. It loses this property the
moment it is used to **make decisions** — parameter adjustments,
strategy selection, threshold tuning. Every decision made with
awareness of OOS results turns OOS into IS.

**Rule**: the OOS test set is reserved before any optimization
begins and is consulted **exactly once** — at the final
evaluation stage, after all parameters are fixed. Any
researcher who has peeked at OOS results to inform development
no longer has an OOS test.

### Walk-Forward Validation

Walk-forward validation (WFV) is the standard approach for
simulating real-time strategy deployment:

```
[Train window 1] → [Test window 1]
         [Train window 2] → [Test window 2]
                  [Train window 3] → [Test window 3]
                           ...
```

Each test window is strictly after each training window. The
training window may be:
- **Expanding** (anchored start, grows each step) — preferred
  when earlier data is informative and not subject to regime
  change.
- **Rolling** (fixed-size, advances each step) — preferred
  when the market regime has changed and old data is
  uninformative or adversely confounds training.

WFV produces a sequence of OOS returns that can be analyzed
for strategy properties. The aggregate of all OOS windows
is the unbiased performance estimate.

### The Leakage Problem (Why Standard CV Fails for Finance)

Standard k-fold cross-validation (as used in ML) randomly
assigns observations to folds. For financial time series,
this creates **leakage**: observations near a label's date
contain information about the label (e.g., a stock's return
over days 1–5 "leaks" into the prediction of its return over
days 1–20 if the same underlying bar is used in adjacent folds).

López de Prado identifies three leakage channels:
1. **Overlap**: return labels computed over overlapping windows
   (e.g., rolling 20-day returns) cause adjacent observations
   to share information.
2. **Serial correlation**: adjacent bars are not independent;
   including both sides of a boundary in adjacent folds allows
   patterns to "bleed" across the fold boundary.
3. **Look-ahead**: features computed using data that would not
   have been available at the decision time (e.g., using a
   52-week high that incorporates post-decision prices).

### Combinatorial Purged Cross-Validation (CPCV)

CPCV (López de Prado 2018 Ch. 12) addresses leakage by:
1. **Purging**: removing all training observations whose label
   overlaps in time with any test observation.
2. **Embargo**: further removing a fixed number of observations
   on both sides of the train/test boundary to prevent serial
   correlation leakage.
3. **Combinatorial**: testing all C(N_splits, k) combinations
   of splits, generating a distribution of OOS paths rather
   than a single OOS estimate — directly enabling PBO
   computation.

For investing-team workers who are not running full CPCV
implementations: the minimum acceptable discipline is
strict temporal separation (training always precedes test,
no random shuffling) plus look-ahead bias checks.

## The Deflated Sharpe Ratio (Bailey & López de Prado 2014)

### Why Standard Sharpe Is Optimistic in Backtests

The standard annualized Sharpe ratio is overstated when any
of the following hold:

1. **The strategy was selected from multiple trials** — even if
   each trial is individually unbiased, selecting the highest
   Sharpe introduces selection bias. The expected maximum Sharpe
   from N trials scales as √(2 ln N) even if all strategies
   are pure noise.

2. **Returns are non-normal** — most financial return distributions
   are fat-tailed (positive excess kurtosis) and negatively
   skewed (strategy payoffs that "collect nickels in front of
   steamrollers"). Standard Sharpe uses variance as the risk
   metric, which underweights tail events. Lo (2002) provides
   the asymptotic correction.

3. **Returns are autocorrelated** — trend-following strategies
   have positively autocorrelated returns; mean-reversion
   strategies have negatively autocorrelated returns. Standard
   annualization (multiply by √T) assumes i.i.d. Lo (2002)
   corrects this.

### Deflated Sharpe Ratio Definition

The DSR (Bailey & López de Prado 2014) adjusts for all three
simultaneously. Formally:

```
DSR = SR* / √(V[SR_hat])
```

Where:
- `SR*` = the maximum expected Sharpe under the null hypothesis
  of a pure-noise strategy selected from N trials with known
  skewness and kurtosis
- `V[SR_hat]` = the variance of the estimated Sharpe ratio,
  incorporating non-normality and autocorrelation corrections
  from Lo (2002)

**Practical interpretation**:
- DSR > 0 means the strategy's Sharpe is above the expected
  maximum from N random trials → minimum bar for claiming
  genuine positive edge.
- DSR ≤ 0 means the strategy's Sharpe is consistent with
  data mining from pure noise → no evidence of edge.
- DSR is a **minimum bar**, not a sufficient condition. A
  strategy can pass DSR and still fail OOS due to regime
  change or model instability.

### Investing-Team Reporting Requirement

Any backtested strategy memo MUST include:
1. The number of trials tested (N).
2. The reported in-sample Sharpe.
3. Whether DSR was computed; if not, why (e.g., single trial,
   pre-specified hypothesis, no optimization conducted).
4. The OOS Sharpe and whether it was computed on a held-out
   set or walk-forward.

Presenting only the IS Sharpe without disclosing N is a red
flag that SHOULD trigger a MUST-gate failure in the evaluator.

## Practical Backtest Checklist (Arnott, Harvey & Markowitz 2019)

Five mandatory questions before presenting any backtested strategy.
This checklist is adapted from Arnott et al. 2019 for
investing-team use.

### 1. Data Hygiene

**Questions to answer**:
- Is there any **look-ahead bias**? Are any features computed
  using data that would not have been available at the time of
  the trading decision? Common examples: using an annual report
  filed on day T+60 as if it were available on day T; using a
  52-week high that extends past the decision date; normalizing
  by a factor computed on the full sample.
- Is there **survivorship bias**? If the universe is "current
  S&P 500 constituents," stocks that were delisted, acquired,
  or went bankrupt during the test period are excluded — making
  the strategy appear better than it would have been in
  real time. Correct by using a point-in-time constituent
  database.
- Is there **index reconstitution bias**? Strategies that buy
  stocks added to an index and short stocks removed benefit
  from price moves that already occurred when the strategy
  signal fires.

**Required disclosure**: state explicitly whether each bias
was addressed and how.

### 2. Transaction Costs

Any backtest without transaction costs is a toy. For a strategy
to be viable, returns must exceed total frictional costs:

- **Bid-ask spread**: varies by market cap, exchange, and time
  period. Small-cap stocks in emerging markets can have spreads
  of 50–200 bps; large-cap US stocks can be 1–5 bps. Use
  realistic period-appropriate estimates.
- **Market impact**: for position sizes above ~$100k in small/
  mid-cap names, order flow moves the market against the trader.
  Model using square-root impact law or equivalent.
- **Commissions**: for institutional strategies, typically
  $0.002–0.005 per share or 5–10 bps.
- **Slippage**: execution at the end-of-day close vs intraday
  execution; backtests using closing prices understate slippage
  for strategies that react to intraday events.

**Required disclosure**: state the transaction cost model
used and the per-trade cost assumption.

### 3. Out-of-Sample Discipline

(See the full section above for methodology.)

**Required disclosure**: describe the train/test split or
walk-forward scheme. State the percentage of total data
held out for OOS testing. State that the OOS test set was
reserved BEFORE optimization began. If it was not — if the
researcher was aware of OOS behavior during development —
the OOS result is not a valid OOS result and must not be
presented as one.

**Minimum hold-out**: 20–30% of total sample as pure OOS
test set. For walk-forward: OOS windows must constitute at
least 20% of total sample period.

### 4. Multiple Testing Disclosure

**Required disclosure**:
1. How many strategies / parameter combinations were evaluated
   in total (N_trials)?
2. Was any correction applied? (Bonferroni, BH FDR, or other)
3. What is the corrected significance threshold?

If N_trials = 1 (single pre-specified hypothesis): standard
t ≥ 2.0 threshold applies; state this explicitly.

If N_trials > 10: Bonferroni or BH correction is required
unless a specific pre-registration or hold-out argument
is made.

**Do not present a "best of 50" result without this
disclosure.** A strategy selected from 50 trials needs a
t-statistic of approximately 3.0+ to clear the corrected
threshold.

### 5. Regime Sensitivity

No strategy works in all macro regimes. A momentum strategy
that works spectacularly in 2010–2021 US bull market conditions
may fail catastrophically in 2022-type rate-hike regimes.
Before presenting a strategy as generally applicable:

- Test performance across the major Investment Clock regimes
  (Recovery / Overheat / Reflation / Stagflation) as defined
  in `investment-macro-regime.md`.
- If data does not span at least one full regime cycle
  (typically 5–10 years), flag this as a regime coverage gap.
- Report the strategy's Sharpe and drawdown separately for each
  regime period. A strategy that works only in one regime is
  a **regime bet**, not a robust strategy.
- Consider stress tests for: high-inflation environments,
  credit events (2008, 2020), rate-rising environments
  (2022–2023), and market structure changes (e.g., commission-
  free trading, PFOF, SPACs, crypto correlation periods).

**Required disclosure**: performance breakdown by regime;
explicit statement of which regimes the strategy has
been tested in; explicit flag for gaps.

## Relationship to Other Standards

- The OOS discipline here is the **validation gate** for any
  screen produced by `quick-stock-screen.md` that is elevated
  to a claimed strategy. A screen is a hypothesis; a strategy
  requires this checklist.
- Regime sensitivity check (item 5 above) connects to
  `investment-macro-regime.md` — use the Investment Clock
  phase definitions from that standard for regime period
  classification.
- Sharpe ratio interpretation (Lo 2002 corrections, DSR) feeds
  into `position-sizing-and-risk.md` — position sizing decisions
  made on the basis of a Sharpe ratio must use the corrected,
  not raw, Sharpe.
- Data hygiene (look-ahead bias, survivorship) connects to
  `data-sources-and-fixtures.md` — the provenance contract
  is the prerequisite for clean backtest data.

## Anti-Drift Guardrails

### Never present IS Sharpe as "the strategy's Sharpe"

In-sample Sharpe is an artifact of optimization. It is not
the strategy's expected forward Sharpe. The correct phrasing
is "in-sample Sharpe of X over the training period" — never
"the strategy has a Sharpe of X" without specifying IS vs OOS.

### Never omit N_trials

Presenting a backtest result without disclosing the number
of trials tested is equivalent to presenting a p-value
without disclosing the test being performed. It is an
incomplete result.

### "It worked on 20 years of data" is not sufficient

20 years of daily data ≈ 5,000 observations. With 10 free
parameters, this is a low effective sample size for strategy
validation. Bailey et al. show PBO remains high even for
multi-decade samples when the number of trials is large.
Never let "long sample" substitute for "low trial count
and applied corrections."

### Hedgeye GIP "27-year backtest" caveat applies here

The Hedgeye GIP framework claims "27 years of back-tested
history" (per `investment-macro-regime.md` — Hedgeye GIP
section). This is **firm-published, not independently
audited**, and does not disclose trial count, parameter
selection methodology, or transaction costs. Apply the
same scrutiny to this claim as to any internal backtest:
it is a claim, not validated evidence. Cite as "Hedgeye
states...".
