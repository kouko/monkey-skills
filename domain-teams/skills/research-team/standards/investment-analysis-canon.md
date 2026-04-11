---
title: Investment Analysis Canon
tier: 3
---

# Investment Analysis Canon

Fully self-contained Tier 3 standard covering the three load-bearing
pillars of research-team's investment-analysis work: Damodaran's
valuation taxonomy (DCF, relative valuation, contingent-claim /
real options); Graham & Dodd's margin-of-safety and Mr. Market
discipline; and the Merrill Lynch Investment Clock 4-phase rotation
model. Tier 3 because the **Investment Clock 4-phase naming is a
cold-query hallucination hotspot** — LLMs routinely conflate the
Investment Clock's 4 phases (Reflation / Recovery / Overheat /
Stagflation) with business-cycle phases (expansion / slowdown /
contraction / recovery), and the specific growth × inflation 2×2
mapping is not reliably recalled. The body spells out each
framework with enough detail to act on without the cited sources
in hand.

## Primary Sources

- Aswath Damodaran (2012) *Investment Valuation: Tools and Techniques for Determining the Value of Any Asset*, 3rd ed. Wiley. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/Inv3ed.htm. Damodaran's canonical 3-framework valuation taxonomy (DCF, relative, contingent claim). Ch.2 establishes the three approaches; Parts II-IV elaborate each in detail.
- Aswath Damodaran (2018) *The Dark Side of Valuation: Valuing Young, Distressed, and Complex Businesses*, 3rd ed. Pearson FT Press. The companion volume for edge cases where vanilla DCF breaks down (young companies with no earnings, distressed firms, commodity cyclicals, financial services, complex conglomerates).
- Benjamin Graham & David L. Dodd (2008) *Security Analysis: Sixth Edition*. McGraw-Hill. The foundational text for value investing; the origin of the margin-of-safety concept and the analytical framework Warren Buffett cites as his own intellectual inheritance. The 6th edition retains the 1940 second-edition text with forewords and chapter commentary from contemporary value investors.
- Trevor Greetham & Michael Hartnett (2004) *The Investment Clock: Making money from the business cycle*. Merrill Lynch Global Asset Allocation report, 2004-11-10. The canonical source for the Investment Clock 4-phase rotation model mapping growth × inflation to asset-class leadership. **The original Merrill Lynch URL is defunct; readers should access the report via subsequent commentary from Royal London Asset Management (where Greetham continued developing the framework) or archived copies circulated via financial education sites such as drwealth.com.**

## Critical Attribution Corrections

### Investment Clock 4-phase naming

Earlier versions of `protocols/investment.md` (line 15) labeled regime
states as "expansion / slowdown / contraction / recovery". This is
**business-cycle vocabulary**, not the Investment Clock model. The
Investment Clock's 4 phases have **different names and a different
2×2 structure**, grounded in Greetham & Hartnett 2004. The correct
phases are **Reflation / Recovery / Overheat / Stagflation**, mapped
to {Bonds, Stocks, Commodities, Cash} via a growth × inflation matrix
(see §The Investment Clock below). Do NOT use business-cycle
terminology (expansion / slowdown / contraction / recovery /
peak / trough) when citing the Investment Clock model — business-cycle
phases describe GDP dynamics; Investment Clock phases describe
**asset-class leadership in a regime** and the two taxonomies are
not interchangeable.

## Damodaran's Valuation Taxonomy — 3 Frameworks

Damodaran 2012 Ch.2 establishes that every valuation belongs to one
of three families. The choice is a function of the asset and the
question, not a preference.

### 1. Discounted Cash Flow (DCF) Valuation

DCF values an asset as the present value of its expected future cash
flows, discounted at a rate that reflects the riskiness of those
flows. The two canonical variants:

**Free Cash Flow to Firm (FCFF)** discounts cash flows available to
**all** providers of capital (both debt and equity holders) at the
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
WACC = (E / (D+E)) × Cost of Equity + (D / (D+E)) × Cost of Debt × (1 − tax rate)
```

**Free Cash Flow to Equity (FCFE)** discounts cash flows available to
**equity holders only** (after debt service) at the **cost of equity**:

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
exceed the long-run growth rate of the underlying economy** (Damodaran
2012 Ch.12). A terminal growth rate above nominal GDP growth implies
the firm eventually becomes larger than the economy — an impossibility
that is the single most common DCF modeling error.

**Cost of Equity (Ke)** is typically estimated via the Capital Asset
Pricing Model:

```
Ke = Rf + β × (Rm − Rf)
```

where `Rf` is the risk-free rate, `β` is the firm's beta against the
market, and `(Rm − Rf)` is the equity risk premium.

### 2. Relative Valuation (Multiples)

Relative valuation values an asset by comparing it to the prices of
"similar" assets in the market, via a standardized multiple. Common
multiples:

- **P/E** (price / earnings) — most common equity multiple; breaks
  down for firms with negative earnings.
- **EV/EBITDA** — enterprise-value / earnings-before-interest-taxes-
  depreciation-amortization; capital-structure-neutral; standard for
  M&A comparisons.
- **P/B** (price / book) — standard for financial institutions where
  book equity is a meaningful asset base.
- **P/S** (price / sales) — used for growth firms with negative
  earnings or volatile margins.
- **EV/Revenue**, **EV/EBIT**, **PEG** (P/E ÷ growth) — specialized.

The two load-bearing disciplines in relative valuation:

1. **Matching the comparable set** — the comparables must actually be
   comparable (industry, size, growth, risk). A multiple "anchored"
   against a badly-matched comparable set produces meaningless output.
2. **Adjusting for fundamentals** — if the target differs from the
   comparable set on growth, risk, or reinvestment, the raw multiple
   must be adjusted. Damodaran 2012 Part III works through the
   regression approach for controlling for fundamental differences.

### 3. Contingent-Claim (Real Options) Valuation

Contingent-claim valuation treats the asset as holding **optionality**
— the right, but not the obligation, to take a future action. Grounded
in the Black-Scholes-Merton options framework. Typical use cases:

- **Undeveloped natural resource reserves** — the firm has the option,
  but not the obligation, to develop reserves if prices rise above
  the development cost.
- **Patents with uncertain commercial potential** — the firm has the
  option to commercialize if the product becomes viable.
- **Equity in a distressed firm** — shareholders hold a residual call
  option on the assets with strike price equal to the debt.

Real-options valuation is the only framework that produces a positive
value for assets whose **expected** cash flows are zero or negative
but whose **conditional** cash flows (given favorable outcomes) are
large. Vanilla DCF on a patent with 95% failure probability produces
a small or negative value; real-options analysis on the same patent
produces the correct value by separately weighting the upside
scenario.

### Choosing Among the Three

| Asset profile | Preferred framework |
|---|---|
| Mature firm with stable, positive cash flows | DCF (FCFF or FCFE) |
| Young firm with volatile margins, positive revenue, but no stable earnings | Relative (P/S) with adjustment, or Damodaran 2018 growth-stage DCF |
| Firm embedded in a deep comparable set with similar fundamentals | Relative (P/E or EV/EBITDA) |
| Asset whose value is dominated by optionality | Contingent-claim / real options |
| Financial institution | Relative (P/B) or equity DCF with dividend model |
| Commodity cyclical | Cross-cycle DCF (Damodaran 2018) with normalized margins |

## Graham & Dodd — Margin of Safety and Mr. Market

### Margin of Safety (*Security Analysis* 1934; 2008 6th ed retains)

The central discipline of value investing: **pay substantially less
than your best estimate of intrinsic value**. The gap between price
paid and intrinsic value is the **margin of safety**, and that gap
is what absorbs the inevitable errors in the intrinsic-value
estimate itself. Graham's canonical phrasing: "The function of the
margin of safety is, in essence, that of rendering unnecessary an
accurate estimate of the future." You do not need to be precisely
right about intrinsic value if you paid so little that even a
substantial overestimate still leaves you profitable. The margin of
safety is the **antidote to false precision** in valuation models.

Graham's operational heuristic was to buy at roughly **two-thirds of
net current asset value** for deep-value candidates; modern
practitioners generalize to "30-50% discount to intrinsic value
estimate". The specific threshold is less important than the
**discipline of requiring a discount**.

### Mr. Market (*The Intelligent Investor* 1949; *Security Analysis*)

Graham's allegory: imagine the market as a business partner, Mr.
Market, who shows up every day and quotes you a price to either buy
your stake or sell you his. Mr. Market is emotional — some days
euphoric, some days despondent — and the prices he quotes reflect
his mood, not the underlying value. The intelligent investor
**transacts with Mr. Market only when his price is favorable**
(buys when despondent, sells when euphoric) and **ignores him
otherwise**. The error is letting Mr. Market's mood dictate your
own judgment of intrinsic value.

Mr. Market is the grounding for the discipline of
**price-independent valuation** — the intrinsic-value estimate must
be derived from fundamentals first, then compared to market price,
never the other way around. An analyst who anchors on the current
market price and reasons toward a valuation is doing reverse
Mr. Market — a guaranteed calibration failure.

## The Merrill Lynch Investment Clock (Greetham & Hartnett 2004)

The Investment Clock is a regime-rotation model that maps the **two
axes of growth direction × inflation direction** to the asset class
that historically leads in each regime. It is **not a business cycle
model** — business cycles describe GDP dynamics; the Investment
Clock describes the relative performance of 4 asset classes (Bonds,
Stocks, Commodities, Cash) across the 4 growth × inflation regimes.

### The 2×2 Matrix — Full Phase Mapping

|  | **Inflation falling** | **Inflation rising** |
|---|---|---|
| **Growth rising (Growth Up)** | **Recovery** → **Stocks** outperform | **Overheat** → **Commodities** outperform |
| **Growth falling (Growth Down)** | **Reflation** → **Bonds** outperform | **Stagflation** → **Cash** outperforms |

### The 4 Phases in Detail

1. **Reflation** (Growth Down, Inflation Down) — economy slowing,
   inflation falling, central banks cutting rates. **Bonds lead**
   because falling rates lift bond prices. Stocks underperform
   because earnings are contracting. Asset allocation tilts toward
   duration and government bonds.

2. **Recovery** (Growth Up, Inflation Down) — economy re-accelerating
   from the trough, inflation still low or falling, monetary policy
   still accommodative. **Stocks lead** because earnings are
   recovering faster than inflation is rising. This is historically
   the strongest equity phase.

3. **Overheat** (Growth Up, Inflation Up) — economy at or above
   trend, inflation accelerating, central banks tightening.
   **Commodities lead** because commodity prices are the leading
   indicator of inflation. Stocks still positive but trailing
   commodities; bonds underperform as rates rise.

4. **Stagflation** (Growth Down, Inflation Up) — economy slowing
   while inflation remains elevated, central banks caught between
   supporting growth and fighting inflation. **Cash outperforms**
   because no productive asset class is working — stocks fall on
   recession fears, bonds fall on inflation fears, commodities peak
   and roll over. The defensive move is to hold cash and wait for
   the regime to rotate back to Reflation.

### The Cycle Rotation

Under normal macroeconomic dynamics, the regime rotates in a
canonical sequence:

```
  Reflation  →  Recovery  →  Overheat  →  Stagflation  →  Reflation  ...
  (bonds)       (stocks)     (commodities) (cash)          (bonds)
```

The clock metaphor comes from this sequential rotation: the regime
moves around the clock face. Real economies do not always traverse
the sequence in order — regimes can skip, reverse, or stall — but
the canonical 4-phase rotation is the reference against which
deviations are diagnosed.

### Anti-Drift Note

When invoking the Investment Clock in a research deliverable, use the
exact phase names — **Reflation / Recovery / Overheat / Stagflation**
— and the exact asset-class mapping — **{Bonds, Stocks, Commodities,
Cash}**. Do NOT substitute business-cycle terminology
(expansion / slowdown / contraction / recovery / peak / trough) when
citing the Investment Clock. Business-cycle phases and Investment
Clock phases are not the same taxonomy and conflating them produces
wrong asset-allocation conclusions — a "contraction" in business-cycle
terms can be either Reflation (supportive for bonds) or Stagflation
(hostile to everything except cash), and the asset-allocation
implications are opposite.

## Anti-Patterns

- Using DCF with a terminal growth rate above long-run nominal GDP
  growth (the firm ends up larger than the economy).
- Running relative valuation against a badly-matched comparable set
  (different industry, size, growth, or risk) and reporting the
  multiple as if it were load-bearing.
- Anchoring the intrinsic-value estimate on the current market price
  and reasoning backward ("the price is X so intrinsic value must
  be in the neighborhood"). This is reverse Mr. Market.
- Labeling regimes with business-cycle vocabulary (expansion /
  slowdown / contraction / recovery) while citing the Investment
  Clock. The correct phases are Reflation / Recovery / Overheat /
  Stagflation.
- Treating the Investment Clock 4-phase rotation as a deterministic
  calendar ("we are in Q3 so we must be in Overheat"). The phases
  are defined by the **state** of growth and inflation, not by
  elapsed time.
