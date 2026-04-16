---
name: investment-security-valuation
description: L3 individual security valuation frameworks (Damodaran / Graham & Dodd / CAPE)
tier: 3
layer: L3-security
---

# Investment — L3 Security Valuation

Fully self-contained Tier 3 standard covering the **L3 individual
security valuation layer** of research-team's investment-analysis
work: the frameworks used to estimate the intrinsic value of a
specific company or security. This file is the SSOT for bottom-up
valuation claims, margin-of-safety discipline, and the cycle-
smoothed P/E (CAPE) refinement of relative valuation.

Tier 3 because multiple entries here are **cold-query hallucination
hotspots** — LLMs routinely (a) credit CAPE to Shiller alone rather
than Campbell & Shiller 1998, (b) treat CAPE as an arbitrary 10-
year window when the lineage is Graham & Dodd 1934, (c) fabricate a
"Damodaran macro framework" that does not exist (Damodaran's
corpus is strictly bottom-up), and (d) anchor intrinsic-value
estimates on the current market price and reason backward —
reverse Mr. Market, a guaranteed calibration failure.

**Scope**: L3 bottom-up valuation of an individual security or
company. L1 macro regime → `investment-macro-regime.md`; L2 sector
rotation and factor tilts → `investment-sector-industry.md`;
portfolio construction → `investment-portfolio-construction.md`.

## Primary Sources

- Aswath Damodaran (2012) *Investment Valuation: Tools and Techniques for Determining the Value of Any Asset*, 3rd ed. Wiley. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/Inv3ed.htm. Damodaran's canonical 3-framework valuation taxonomy (DCF, relative valuation, contingent-claim / real options). Ch.2 establishes the three approaches; Parts II–IV elaborate each in detail. **The single most-cited reference textbook for bottom-up security valuation**.
- Aswath Damodaran (2018) *The Dark Side of Valuation: Valuing Young, Distressed, and Complex Businesses*, 3rd ed. Pearson FT Press. Companion volume for edge cases where vanilla DCF breaks down: young companies with no earnings, distressed firms, commodity cyclicals, financial services, complex conglomerates.
- Benjamin Graham & David L. Dodd (2008) *Security Analysis: Sixth Edition*. McGraw-Hill. **The foundational text for value investing** and the origin of the margin-of-safety concept. Warren Buffett cites this as his primary intellectual inheritance. The 6th edition retains the 1940 second-edition text with forewords and chapter commentary from contemporary value investors.
- John Y. Campbell & Robert J. Shiller (1998) "Valuation Ratios and the Long-Run Stock Market Outlook." *Journal of Portfolio Management* 24(2): 11–26. https://www.econ.yale.edu/~shiller/pubs/p1049.pdf. **The canonical operational formulation of the Cyclically-Adjusted Price-to-Earnings ratio (CAPE / CAPE^10)**, with the 10-year real-earnings smoothing window and the predictive R² evidence on 10-year-forward equity returns. Cite **both** authors, not Shiller alone.
- Robert J. Shiller (2015) *Irrational Exuberance*, 3rd ed. Princeton University Press. Book-form popularization of CAPE with updated historical thresholds and explicit acknowledgment of the Graham & Dodd 1934 lineage. Shiller's Yale CAPE dataset (http://www.econ.yale.edu/~shiller/data.htm) is the de-facto empirical reference, continuously updated. **Not** the operational primary source for CAPE.

## Critical Attribution Corrections

### CAPE authorship is Campbell & Shiller 1998, not Shiller alone

The Cyclically-Adjusted Price-to-Earnings ratio is routinely
miscredited to Shiller's 2000 / 2005 / 2015 *Irrational Exuberance*
or to Shiller alone. The **operational CAPE formulation** — the
10-year real-earnings smoothing window and the predictive-R²
evidence on 10-year-forward equity returns — is in
**Campbell & Shiller (1998) *Journal of Portfolio Management*
24(2): 11–26**. An earlier academic predecessor, Campbell & Shiller
(1988) "Stock Prices, Earnings, and Expected Dividends"
*Journal of Finance* 43(3): 661–676, laid the cyclically-adjusted-
earnings foundation. Shiller's 2000/2005/2015 books are the
popularization, not the origin. When citing CAPE, name **both**
authors and cite the 1998 JPM paper as the operational canonical.

### The 10-year CAPE window is Graham & Dodd 1934, not Shiller's invention

The choice of a 10-year earnings average is frequently presented as
Shiller's innovation. It is not. **Graham & Dodd's *Security
Analysis* (1934 1st ed, retained in 1940 2nd ed and 2008 6th ed)**
recommended averaging earnings over 7 to 10 years to eliminate the
cyclical noise of any single business cycle. Campbell & Shiller
(1988, 1998) explicitly credit Graham & Dodd for the 10-year
smoothing rationale. The correct lineage is:

> **Graham & Dodd 1934 → Campbell & Shiller 1988 → operational CAPE 1998**

Do NOT present the 10-year window as an arbitrary or Shiller-
derived choice.

### Damodaran has NO canonical macro or regime framework

A recurring misconception is that Aswath Damodaran has a "macro
regime framework" comparable to the Investment Clock or Dalio's
debt cycle. **This framework does not exist.** Damodaran's
published corpus is exclusively bottom-up valuation:

- **Damodaran (2012)** *Investment Valuation* — DCF, Relative, Real
  Options (the 3-framework taxonomy already cited in this file)
- **Damodaran (2018)** *The Dark Side of Valuation* — edge cases
  for distressed / young / complex firms
- **Damodaran (2024)** *The Corporate Life Cycle* — **firm-stage**
  taxonomy (startup / growth / mature / decline), often confused
  with macro cycles but is strictly a micro-level framework about
  individual companies
- Annual SSRN updates on Equity Risk Premium estimation and Country
  Risk Premium — these are **DCF discount-rate inputs**, not
  regime-rotation frameworks. Implied ERP moves with macro state
  but is presented by Damodaran explicitly as a valuation input,
  not as an asset-allocation signal
- Blog posts on political regime change in country risk — these
  address going-concern risk in distressed / emerging-market
  valuations, not cross-asset rotation

When a user or an earlier draft references "Damodaran's macro
framework" or "Damodaran regime model", the correct response is to
**refuse the premise**: redirect to `investment-macro-regime.md`
for Greetham & Hartnett (2004) Investment Clock, Dalio (2018) debt
cycle, or — if a contemporary narrative-cycle reference is needed —
Howard Marks (2018) *Mastering the Market Cycle*. Do NOT fabricate
a Damodaran regime framework from his ERP or country risk work;
they are discount-rate tooling, not regime models.

### Terminal growth rate ≤ long-run nominal GDP

The single most common DCF modeling error is using a terminal
growth rate that exceeds long-run nominal GDP growth. Damodaran
(2012) Ch.12 states this as a hard constraint: a firm whose
terminal growth rate exceeds nominal GDP growth eventually becomes
larger than the economy — an impossibility. Terminal growth must
be **bounded above by long-run nominal GDP growth** (typically
2–4% in developed markets). Exceptions require explicit
justification (e.g. emerging market with structurally higher
nominal growth).

### Margin of safety is the antidote to false precision, not optional

Graham's margin-of-safety discipline is not a stylistic preference
— it is the structural compensation for the inherent imprecision
of any intrinsic-value estimate. Graham's canonical phrasing:
*"The function of the margin of safety is, in essence, that of
rendering unnecessary an accurate estimate of the future."*
Dropping the margin-of-safety discipline implies false confidence
in the valuation output.

### Mr. Market discipline: fundamentals FIRST, price SECOND

The single most common value-investing failure is reversing
Graham's Mr. Market discipline. The correct sequence is:

1. Estimate intrinsic value from fundamentals (DCF / comparables /
   NCAV) **before looking at the market price**
2. Compare intrinsic value to market price
3. Decide action based on the gap

The incorrect (reverse) sequence is to anchor on the current market
price and reason backward ("the price is X, so intrinsic value must
be in the neighborhood of X"). This is **reverse Mr. Market** — a
guaranteed calibration failure. Research deliverables that present
an intrinsic value numerically close to the current market price
without independent derivation should be treated as suspect.

## Damodaran's Three-Framework Valuation Taxonomy

Damodaran 2012 Ch.2 establishes that every valuation belongs to one
of three families. The choice is a function of the asset and the
question, not a preference.

### 1. Discounted Cash Flow (DCF) Valuation

DCF values an asset as the present value of its expected future
cash flows, discounted at a rate that reflects the riskiness of
those flows. The two canonical variants:

**Free Cash Flow to Firm (FCFF)** discounts cash flows available to
**all** providers of capital (debt + equity holders) at the
**weighted average cost of capital (WACC)**:

```
Firm Value = Σ [FCFF_t / (1 + WACC)^t] + Terminal Value / (1 + WACC)^n
```

where

```
FCFF = EBIT × (1 − tax rate) + Depreciation & Amortization
     − Capital Expenditure − Change in Working Capital
```

and

```
WACC = (E / (D+E)) × Cost of Equity
     + (D / (D+E)) × Cost of Debt × (1 − tax rate)
```

**Free Cash Flow to Equity (FCFE)** discounts cash flows available
to **equity holders only** (after debt service) at the **cost of
equity**:

```
Equity Value = Σ [FCFE_t / (1 + Ke)^t] + Terminal Value / (1 + Ke)^n
```

where

```
FCFE = Net Income + Depreciation & Amortization
     − Capital Expenditure − Change in Working Capital
     − Debt Repayment + New Debt Issuance
```

**Terminal Value** is typically computed via the Gordon Growth
formulation:

```
Terminal Value_n = CashFlow_(n+1) / (discount rate − g)
```

where `g` is the sustainable long-run growth rate, which **cannot
exceed the long-run growth rate of the underlying economy**
(Damodaran 2012 Ch.12). See §Critical Attribution Corrections
§Terminal growth rate.

**Cost of Equity (Ke)** is typically estimated via the Capital
Asset Pricing Model:

```
Ke = Rf + β × (Rm − Rf)
```

where `Rf` is the risk-free rate, `β` is the firm's beta against
the market, and `(Rm − Rf)` is the equity risk premium.

### 2. Relative Valuation (Multiples)

Relative valuation values an asset by comparing it to the prices of
"similar" assets in the market, via a standardized multiple. Common
multiples:

- **P/E** (price / earnings) — most common equity multiple; breaks
  down for firms with negative earnings. For cyclical industries
  (where single-year earnings are deeply volatile) the trailing
  P/E should be replaced by CAPE.
- **CAPE** (Cyclically-Adjusted P/E, also written CAPE^10 or
  Shiller P/E) — price / 10-year average of real earnings. The
  cycle-smoothed variant of P/E, operationalized by Campbell &
  Shiller (1998); see §Cyclically-Adjusted P/E below.
- **EV/EBITDA** — enterprise-value / EBITDA;
  capital-structure-neutral; standard for M&A comparisons.
- **P/B** (price / book) — standard for financial institutions
  where book equity is a meaningful asset base.
- **P/S** (price / sales) — used for growth firms with negative
  earnings or volatile margins.
- **EV/Revenue**, **EV/EBIT**, **PEG** (P/E ÷ growth) —
  specialized.

The two load-bearing disciplines in relative valuation:

1. **Matching the comparable set** — comparables must actually be
   comparable (industry, size, growth, risk). A multiple anchored
   against a badly-matched comparable set produces meaningless
   output.
2. **Adjusting for fundamentals** — if the target differs from the
   comparable set on growth, risk, or reinvestment, the raw
   multiple must be adjusted. Damodaran 2012 Part III works
   through the regression approach for controlling fundamental
   differences.

### 3. Contingent-Claim (Real Options) Valuation

Contingent-claim valuation treats the asset as holding
**optionality** — the right, but not the obligation, to take a
future action. Grounded in the Black-Scholes-Merton options
framework. Typical use cases:

- **Undeveloped natural resource reserves** — the firm has the
  option, but not the obligation, to develop reserves if prices
  rise above development cost
- **Patents with uncertain commercial potential** — the firm has
  the option to commercialize if the product becomes viable
- **Equity in a distressed firm** — shareholders hold a residual
  call option on the assets with strike price equal to the debt

Real-options valuation is the only framework that produces a
positive value for assets whose **expected** cash flows are zero
or negative but whose **conditional** cash flows (given favorable
outcomes) are large. Vanilla DCF on a patent with 95% failure
probability produces a small or negative value; real-options
analysis on the same patent produces the correct value by
separately weighting the upside scenario.

### Choosing Among the Three

| Asset profile | Preferred framework |
|---|---|
| Mature firm with stable positive cash flows | DCF (FCFF or FCFE) |
| Young firm with volatile margins, positive revenue, no stable earnings | Relative (P/S) with adjustment, or Damodaran 2018 growth-stage DCF |
| Firm embedded in a deep comparable set with similar fundamentals | Relative (P/E or EV/EBITDA) |
| Asset whose value is dominated by optionality | Contingent-claim / real options |
| Financial institution | Relative (P/B) or equity DCF with dividend model |
| Commodity cyclical | Cross-cycle DCF (Damodaran 2018) with normalized margins, or CAPE |

## Graham & Dodd — Margin of Safety and Mr. Market

### Margin of Safety (*Security Analysis* 1934; 2008 6th ed retains)

The central discipline of value investing: **pay substantially less
than your best estimate of intrinsic value**. The gap between price
paid and intrinsic value is the **margin of safety**, and that gap
is what absorbs the inevitable errors in the intrinsic-value
estimate itself.

Graham's canonical phrasing: *"The function of the margin of safety
is, in essence, that of rendering unnecessary an accurate estimate
of the future."* You do not need to be precisely right about
intrinsic value if you paid so little that even a substantial
overestimate still leaves you profitable.

Graham's operational heuristic was to buy at roughly **two-thirds
of net current asset value (NCAV)** for deep-value candidates;
modern practitioners generalize to **30–50% discount to intrinsic
value estimate**. The specific threshold is less important than
the discipline of requiring a discount.

**Margin of safety is the antidote to false precision**, not an
optional stylistic element. Cutting it out implies false confidence
in the underlying valuation.

### Mr. Market (*The Intelligent Investor* 1949; *Security Analysis*)

Graham's allegory: imagine the market as a business partner, Mr.
Market, who shows up every day and quotes you a price to either
buy your stake or sell you his. Mr. Market is emotional — some
days euphoric, some days despondent — and the prices he quotes
reflect his mood, not the underlying value. The intelligent
investor **transacts with Mr. Market only when his price is
favorable** (buys when despondent, sells when euphoric) and
**ignores him otherwise**.

Mr. Market is the grounding for the discipline of
**price-independent valuation** — the intrinsic-value estimate must
be derived from fundamentals **first**, then compared to market
price, **never the other way around**. An analyst who anchors on
the current market price and reasons toward a valuation is doing
reverse Mr. Market — a guaranteed calibration failure. See
§Critical Attribution Corrections §Mr. Market discipline for the
explicit correct sequence.

## Cyclically-Adjusted P/E (Campbell & Shiller 1998)

CAPE (also written CAPE^10 or Shiller P/E) is the cycle-smoothed
refinement of the trailing P/E multiple, operationalized by
Campbell & Shiller (1998) in *Journal of Portfolio Management*
24(2). The formula:

```
CAPE = P_real / (average of 10 years of real earnings)

where:
  P_real       = current inflation-adjusted market index price
  real earnings = trailing 12-month earnings per share, inflation-adjusted
  10-year window = 120-month trailing average of real earnings
```

**Both inputs are in real (inflation-adjusted) terms.** LLMs
frequently drop the "real" qualifier and conflate CAPE with a
nominal trailing P/E. Shiller's Yale dataset
(http://www.econ.yale.edu/~shiller/data.htm) publishes the real
series monthly; all historical thresholds below refer to this real
series.

### Why 10 years? — Graham & Dodd 1934 lineage

The 10-year smoothing window derives from **Graham & Dodd (1934)
*Security Analysis***, which recommended averaging earnings over
7–10 years to eliminate the cyclical volatility of any single
business cycle. Campbell & Shiller (1988, 1998) explicitly credit
this lineage and operationalize 10 years as the canonical window.
A 10-year average spans a full typical business cycle (~7–11
years) while remaining responsive to secular profitability shifts.

Lineage summary: **Graham & Dodd 1934 → Campbell & Shiller 1988 →
operational CAPE 1998**.

### Historical Thresholds (Shiller 2015 3rd ed)

| CAPE range | Historical frequency | Interpretation |
|---|---|---|
| **< 10** | ~5% of ~150-year history | Extremely depressed — fire-sale valuations, strong forward returns |
| **10 – 16** | ~30% | Below-average valuation — favorable entry |
| **~16–17** | long-run mean | Fair value baseline; average real forward 10-year return ~6–7% |
| **17 – 25** | ~30% | Above-average valuation — caution warranted |
| **> 25** | ~5% | Extremely elevated — bubble territory, low-to-negative forward returns |

### Predictive Power

Campbell & Shiller (1998) document that CAPE explains roughly
**30–40% of the variance in subsequent 10-year real equity
returns** (R² ≈ 0.3–0.4). This is a **regime-level indicator** —
strongly predictive at the extremes (< 10 or > 25), weak in the
middle zone (16–20), and **not a trading signal** for quarterly or
annual timing. CAPE answers *"where are equities in their long-run
valuation distribution?"* — it does NOT answer *"what should I do
tomorrow?"*.

### CAPE is single-variable, not a regime model

CAPE is a **single-variable equity valuation indicator**, not a
multi-asset regime rotation framework. The Investment Clock (see
`investment-macro-regime.md`) is a 2×2 growth × inflation → 4-asset
mapping; CAPE is 1D and equity-only. CAPE and the Investment Clock
are **complementary, not competing**:

- The Investment Clock tells you **which asset class leads** in
  the current growth × inflation regime
- CAPE tells you whether **equities are richly or cheaply valued**
  within whichever leadership phase is current

Example: in a Recovery phase (Growth Up, Inflation Down → Stocks
lead per Investment Clock), a CAPE reading of 35 does not change
the asset-class call — stocks still lead — but it warns that the
equity leadership is accompanied by bubble-era valuations, and
downstream size-down / hedging / margin-of-safety disciplines apply.

### Japanese Market Application

Shiller's dataset includes Nikkei 225 CAPE since 1957. No parallel
JP-authored methodological framework exists; Japanese researchers
apply Shiller's methodology directly. Empirical observation:
Nikkei CAPE's structural level has been lower than the US since
the 1990s (reflecting Japan's lower structural growth), so the
16–17 "fair value" threshold may be conservatively high for the
Nikkei. This is an empirical observation, not a theoretically-
derived adjustment.

## Cross-Layer Usage Notes

Two of the frameworks in this file are **cross-layer** — they serve
both L3 individual security valuation AND L1 whole-market pricing
signals. Workers must be explicit about which layer they are
invoking.

### CAPE is cross-layer

- **L3 usage** (primary): CAPE is a P/E variant for cyclical firms
  where single-year trailing earnings are deeply volatile. Use the
  company's own 10-year real EPS average versus its current real
  price.
- **L1 usage** (cross-reference): CAPE applied to a broad market
  index (S&P 500, Nikkei 225) is a **whole-market valuation
  signal** — it answers "where are equities in their long-run
  valuation distribution?". When used at the L1 level, cross-
  reference `investment-macro-regime.md`. Do NOT treat L1 CAPE as
  a tactical trade signal; treat it as a structural overlay on the
  L1 Investment Clock asset-class rotation call.

### Damodaran Implied Equity Risk Premium is cross-layer

Damodaran's implied ERP (published in annual SSRN updates) is
computed from the current S&P 500 level and analyst earnings
forecasts. It serves:

- **L3 usage**: as the ERP input to company-level DCF cost of
  equity (`Ke = Rf + β × (Rm − Rf)`). Use the current implied ERP
  rather than a historical average when running a DCF in the
  current market context.
- **L1 usage** (cross-reference): implied ERP also functions as a
  **whole-market pricing barometer** — when implied ERP compresses
  below ~4%, the market is pricing equities as low-risk-premium,
  which historically precedes period of underperformance. Use as
  an L1 sanity check against CAPE and Investment Clock signals.
  See `investment-macro-regime.md` for the cross-reference.

**Neither CAPE nor Damodaran implied ERP is a standalone regime
model.** Both are valuation signals that serve as **structural
overlays** on the L1 regime call.

## Integration with L1 + L2 Layers

L3 security valuation is the **final filter** after L1 regime
identification and L2 sector / factor tilt decisions. A full
top-down research process:

1. **L1 regime call** → asset-class and macro context
   (`investment-macro-regime.md`)
2. **L2 sector and factor tilts** → which sectors and factor styles
   to overweight within equities (`investment-sector-industry.md`)
3. **L3 security valuation** → bottom-up derivation of intrinsic
   value for individual names within the preferred sectors
   (this file)
4. **Portfolio construction** → assemble individual L3 positions
   into a coherent portfolio consistent with the L1 risk posture
   (`investment-portfolio-construction.md`)

The margin-of-safety discipline at L3 interacts with the L1
structural risk overlay: when L1 says "we are in a Dalio Bubble
phase with 2–4 years until the cycle breaks", the appropriate
L3 response is to **widen the required margin of safety** rather
than abandon the intrinsic-value process. Graham & Dodd's discipline
is the right one; the risk regime adjusts the size of the required
discount, not the existence of the requirement.
