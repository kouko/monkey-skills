---
name: investment-macro-regime
description: L1 macro regime frameworks for asset-class rotation calls
tier: 3
layer: L1-macro
---

# Investment — L1 Macro Regime

Fully self-contained Tier 3 standard covering the **L1 macro regime
layer** of research-team's investment-analysis work: the set of
frameworks used to diagnose which asset class leads in the current
growth / inflation / credit / liquidity state. This file is the
SSOT for macro-level asset-rotation claims.

Tier 3 because multiple entries here are **cold-query hallucination
hotspots** — LLMs routinely (a) conflate the Merrill Lynch Investment
Clock's 4 phases with business-cycle terminology, (b) collapse
Dalio's 6 debt-cycle phases into 4, (c) cite Hedgeye GIP as a
descendant of Greetham's Investment Clock when it is actually a
sibling descended from Bridgewater's 1996 4-box, (d) cite Kelton as
the origin of MMT when the origin is Mosler 1996, and (e) cite
Wilmot / Credit Suisse as the origin of the Risk Appetite Index when
the peer-reviewed origin is Kumar & Persaud 2002. Body spells out
each framework with enough detail to act on without the cited
sources in hand.

**Scope**: L1 macro regime diagnosis → cross-asset allocation.
Individual sector rotation belongs to `investment-sector-industry.md`;
individual security valuation belongs to
`investment-security-valuation.md`; portfolio construction belongs
to `investment-portfolio-construction.md`.

## Primary Sources

- Trevor Greetham & Michael Hartnett (2004) *The Investment Clock: Making money from the business cycle*. Merrill Lynch Global Asset Allocation report, 2004-11-10. Canonical 2×2 growth × inflation → 4-asset-class rotation model. The original Merrill URL is defunct; access via Royal London Asset Management commentary (where Greetham continued the framework) or archived copies circulated via financial education sites. Grey-literature primary.
- Ray Dalio (2018) *Principles for Navigating Big Debt Crises*. Bridgewater Associates, self-published. https://www.principles.com/big-debt-crises/. Canonical source for the two-horizon debt-cycle framework: Part 1 establishes the 6-phase template (Early / Bubble / Top / Depression / Beautiful Deleveraging / Pushing on a String); consolidates 48 historical case studies; freely available PDF from Bridgewater.
- Richard C. Koo (2008) *The Holy Grail of Macroeconomics: Lessons from Japan's Great Recession*. John Wiley & Sons (Singapore). Canonical source for the balance-sheet recession concept — the load-bearing JP parallel to Dalio's Depression + Beautiful Deleveraging phases, grounded in Japan 1990–2005.
- Keith McCullough (2024) *Master The Market: A Hedge Fund Manager's Guide to Process and Profit*. Hedgeye Risk Management / Hedgeye Gear (self-published ebook). Canonical author text for the Hedgeye Growth-Inflation-Policy (GIP) 4-Quadrant model. Grey-literature primary.
- Keith McCullough & Darius Dale — Hedgeye Risk Management. *An Introduction to the Hedgeye Macro GIP Model Risk Management Process*. https://docs3.hedgeye.com/macroria/Hedgeye_GIP_Model_Risk_Management_Process.pdf. Firm-published technical white paper for GIP. Dale is co-architect, not a user.
- Warren Mosler (1996) *Soft Currency Economics*. Self-published, distributed at moslereconomics.com. **Origin document of Modern Monetary Theory**, grounded in Mosler's 1992 Italian bond trade operational insight. Do NOT cite Kelton 2020 as the origin of MMT.
- L. Randall Wray (2012, 2nd ed 2015, 3rd ed 2024) *Modern Money Theory: A Primer on Macroeconomics for Sovereign Monetary Systems*. Palgrave Macmillan / Springer Nature. The canonical academic treatment of MMT. Wray (UMKC; Levy Economics Institute) was Hyman Minsky's student.
- Stephanie Kelton (2020) *The Deficit Myth: Modern Monetary Theory and the Birth of the People's Economy*. PublicAffairs. Popular canonical. Kelton (Stony Brook; ex-Chief Economist Senate Budget Committee Democratic staff).
- Manmohan Kumar & Avinash Persaud (2002) "Pure Contagion and Investors' Shifting Risk Appetite: Analytical Issues and Empirical Evidence." *International Finance* 5(3): 401–436. **Peer-reviewed academic origin of the cross-sectional Global Risk Appetite Index (GRAI)**, using Spearman rank correlation between excess returns and past volatilities across a cross-section of risky assets. Pre-dates Credit Suisse / Wilmot 2004.
- Mark Illing & Meyer Aaron (2005) "A Brief Survey of Risk-Appetite Indexes." *Bank of Canada Financial System Review* (June 2005): 37–43. https://www.bankofcanada.ca/wp-content/uploads/2012/01/fsr-0605-illing.pdf. Central-bank survey anchor cataloguing 10 RAI variants with methodological comparison and the load-bearing caveat: *"It seems premature to rely on any given index when assessing risk appetite."*

## Critical Attribution Corrections

### Investment Clock 4-phase naming vs business-cycle vocabulary

Earlier research-team drafts labelled regime states as "expansion /
slowdown / contraction / recovery". This is **business-cycle
vocabulary**, not the Investment Clock model. The Investment Clock's
4 phases have different names and a different 2×2 structure,
grounded in Greetham & Hartnett 2004. The correct phases are
**Reflation / Recovery / Overheat / Stagflation**, mapped to
{Bonds, Stocks, Commodities, Cash} via a growth × inflation matrix.
Business-cycle phases describe GDP dynamics; Investment Clock phases
describe asset-class leadership in a regime and the two taxonomies
are **not interchangeable**.

### Dalio debt-cycle 6 phases, not 4 or 5

LLMs routinely collapse Dalio's 6 canonical phases (Early part of
the cycle / Bubble / Top / Depression / Beautiful Deleveraging /
Pushing on a String) into 4 or 5, usually by dropping "Early part
of the cycle" or merging Depression + Beautiful Deleveraging. The
canonical count is **6**, applied symmetrically to both the
short-term cycle (5–8 years ± 3) and long-term cycle (50–75 years
± 25). Do not simplify.

### Dalio is diagnostic, not prescriptive

Dalio 2018 does NOT produce direct asset-allocation calls. The
framework identifies **which phase we are in**; downstream allocation
decisions are derived separately (and Bridgewater's All-Weather
portfolio is a related but **distinct** construct — see
`investment-portfolio-construction.md`). Do NOT present Dalio's
debt-cycle phases as buy/sell signals.

### Hedgeye GIP is a sibling to the Investment Clock, not a child

Hedgeye GIP (McCullough & Dale 2008+) is widely misattributed as a
descendant of Greetham's Investment Clock. It is not. GIP's
genealogical lineage is **Bridgewater / Dalio 1996 4-box** (which
predates Greetham by ~8 years), as publicly acknowledged by Darius
Dale. GIP and the Investment Clock share a 2-axis growth × inflation
diagnostic but differ in authors, firms, years, measurement (GIP
uses second-derivative rate-of-change; IC uses level vs trend),
intended use, and regime labels. They are **cousins**, not
parent/child.

### Hedgeye GIP is 2-axis with derived policy overlay, not 3-axis

Popular summaries (including some Hedgeye marketing) describe GIP as
a "3-dimensional model" because the "P" stands for Policy. This is
technically wrong. Policy is a **derived expected Fed response**
mapped 1-to-1 from the Growth × Inflation quadrant, not an
independent measurement. McCullough's own operational statement: *"If
I get the Growth and Inflation right, I'm front-running the policy
move."* Cite GIP as a **2-axis framework with a derived policy
reaction-function overlay**.

### Darius Dale is co-architect of GIP, not a user

Early drafts attributed GIP solely to McCullough. Hedgeye's own
podcast credits Dale as "instrumental in creating Hedgeye's GIP
Model quad-based economic outlooks". Canonical attribution:
**McCullough, Dale et al., Hedgeye Risk Management**.

### MMT origin is Mosler 1996, not Kelton 2020

LLMs and popular-press coverage routinely cite Kelton 2020
*The Deficit Myth* as the origin of MMT. It is the **popular
canonical**, not the origin. The origin is **Mosler 1996**
*Soft Currency Economics*, grounded in Mosler's 1992 Italian bond
trade. The canonical academic treatment is **Wray 2012**
*Modern Money Theory: A Primer*. Cite all three with awareness of
distinct roles (origin / academic / popular).

### MMT is not "just print money"

MMT explicitly identifies inflation and real-resource constraint as
the binding limit on sovereign spending. Kelton *Deficit Myth* Ch 2
is entirely devoted to this constraint. Describing MMT as "unlimited
money printing" indicates no engagement with the primary sources.

### MMT dual-citation rule — never stand alone

Every MMT claim in a research deliverable MUST be paired with at
least one mainstream-critique citation (Krugman, Rogoff, Summers,
Mankiw NBER WP 26650, Blanchard AER 2019, or Palley's Post-Keynesian
internal critique). A 2019 University of Chicago IGM Forum poll of
leading academic economists found **zero** agreement with MMT's
strongest deficit-irrelevance claims. MMT is a **heterodox,
contested framework**, not textbook consensus.

### RAI origin is Kumar & Persaud 2002, not Wilmot / Credit Suisse

"Credit Suisse launched the Risk Appetite Index in the early 2000s"
is commonly cited as the origin of cross-sectional RAI methodology.
It is wrong. **Kumar & Persaud (2002)** *International Finance*
5(3): 401–436 is the **peer-reviewed academic origin**.
Wilmot / Mielczarski / Sweeney (2004) CSFB *Market Focus* is a
linear-regression **extension** of Kumar-Persaud applied to 64
bond+equity indexes — per Illing-Aaron (2005) Bank of Canada FSR
and Uhlenbrock (2009) Bundesbank. The practitioner "Credit Suisse
RAI" branding is grey literature built on a 2002 peer-reviewed
concept. Cite Kumar & Persaud first.

### Goldman Sachs publishes a Risk-AVERSION Index, not RAI, and not by Hatzius

The "Goldman Sachs Risk Appetite Index by Jan Hatzius" commonly
cited in practitioner commentary is a misattribution on two counts.
Goldman's product is the **Risk-Aversion Index** (inverse semantics
— higher = risk-averse, not risk-appetitive), originated in GS
Economics Research *The Foreign Exchange Market* (2003-10) using a
consumption-CAPM Arrow-Pratt specification. It is not tied to
Hatzius (who is GS Chief Economist associated with the Current
Activity Indicator and Financial Conditions Index, not the
Risk-Aversion Index).

### State Street ICI is NBER WP 10157, not 8226

The State Street Investor Confidence Index academic origin is
**Froot & O'Connell, NBER Working Paper 10157** (2003-12) "The Risk
Tolerance of International Investors", DOI 10.3386/w10157 — not
WP 8226. Froot is Harvard Business School; O'Connell is State
Street Associates. The index is flow-based (holdings imbalances
from the State Street global custody database), releases monthly,
and uses **100 = neutral**.

### "BofA Global Investor Confidence Index" does not exist

BofA's sentiment flagships are the **Bull & Bear Indicator**
(Hartnett team, formalized ~2013, 0–10 scale, buy signal < 2.0,
sell signal > 8.0, "16 sell signals since 2002, 63% accurate" per
BofA 2024 disclosure) and the **Global Fund Manager Survey**. Citing
a "BofA Global Investor Confidence Index" conflates BofA with State
Street ICI; correct the name to **Bull & Bear Indicator**.

## Merrill Lynch Investment Clock (Greetham & Hartnett 2004)

The Investment Clock is a regime-rotation model that maps the **two
axes of growth direction × inflation direction** to the asset class
that historically leads in each regime. It is **not a business-cycle
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
   still accommodative. **Stocks lead** because earnings recover
   faster than inflation rises. Historically the strongest equity
   phase.

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
   and roll over.

### The Cycle Rotation

Under normal macroeconomic dynamics, the regime rotates in a
canonical sequence:

```
  Reflation  →  Recovery  →  Overheat  →  Stagflation  →  Reflation  ...
  (bonds)       (stocks)     (commodities) (cash)          (bonds)
```

Real economies do not always traverse the sequence in order —
regimes can skip, reverse, or stall — but the canonical 4-phase
rotation is the reference against which deviations are diagnosed.

### Anti-drift

When invoking the Investment Clock, use the exact phase names
**Reflation / Recovery / Overheat / Stagflation** and the exact
asset-class mapping **{Bonds, Stocks, Commodities, Cash}**. Do NOT
substitute business-cycle terminology. Business-cycle "contraction"
can be either Reflation (supportive for bonds) or Stagflation
(hostile to everything except cash), and the asset-allocation
implications are opposite.

See also: factor-regime mapping in `investment-sector-industry.md`
for how L1 Investment Clock phases translate to L2 factor tilts.

## Dalio Two-Horizon Debt Cycle (Dalio 2018)

Ray Dalio's two-horizon debt-cycle framework is a **diagnostic**
regime model that sits alongside — not inside — the Investment
Clock. Dalio 2018 consolidates the framework: a **short-term debt
cycle** (5–8 years ± 3) driven by credit expansion / contraction,
and a **long-term debt cycle** (50–75 years ± 25) driven by
decades-long accumulation of debt relative to income. Both cycles
move through the **same 6 canonical phases** with the same names.
The framework's purpose is **phase identification**, not direct
asset-allocation prescription.

### Two horizons, same 6 phases

| Horizon | Time span | Driver |
|---|---|---|
| **Short-term debt cycle** | 5–8 years (±3) | Credit expansion / contraction ("the credit cycle") |
| **Long-term debt cycle** | 50–75 years (±25) | Debt-to-income accumulation; reserve-currency transitions; generational leverage build-up |

Both cycles move through the same 6 phases in sequence:

1. **Early part of the cycle** — healthy debt growth supports
   productivity growth. Debt-to-income ratios are sustainable. Asset
   prices extrapolate past trends. Expectations remain anchored.
2. **Bubble** — borrowing accelerates to invest in assets on the
   expectation that past trends continue. Leverage increases. Asset
   prices decouple from fundamentals. Credit growth outpaces income
   growth.
3. **Top** — central banks tighten OR debt service becomes
   unsustainable. Credit growth peaks. Asset-price momentum stalls.
   The turning point — not yet a crisis, but the setup is complete.
4. **Depression** — the bubble bursts. Credit contracts. Asset
   values collapse. In worst cases, interest rates hit the zero
   lower bound. Deflationary in hard-currency systems; can be
   inflationary in reserve-currency-losing systems (Dalio 2021
   extends this distinction).
5. **Beautiful deleveraging** — Dalio's term for a coordinated mix
   of **(a) modest austerity, (b) debt restructuring, and (c) money
   printing** that together reduce debt relative to income **while
   growth remains positive and inflation remains controlled**. The
   2007–2011 US case study is Dalio's canonical example.
6. **Pushing on a string / normalization** — monetary policy's
   marginal efficacy declines. The cycle transitions back toward
   Phase 1 as debt is worked off. In long-cycle transitions this
   phase often coincides with reserve-currency shifts.

### Three variables, not two

The Investment Clock uses 2 variables (Growth direction × Inflation
direction). Dalio uses **3**:

- **Growth** (rate of change in GDP / income)
- **Inflation** (rate of change in price level)
- **Productivity** (long-term trend around which debt cycles
  oscillate — separable from short-term cycles)

Productivity is what lets Dalio distinguish "healthy" credit growth
(matching productivity) from "bubble" credit growth (outpacing
productivity) — a distinction the Investment Clock's 2-axis matrix
cannot capture.

### Relationship to Investment Clock — complementary layers

| Dimension | Investment Clock | Dalio short-term | Dalio long-term |
|---|---|---|---|
| Time horizon | 1–3 year regime rotation | 5–8 year credit cycle | 50–75 year leverage accumulation |
| Variables | Growth × Inflation | + Credit dynamics | + Productivity trend |
| Asset output | Explicit (4-asset mapping) | Diagnostic (phase ID) | Diagnostic (structural phase) |
| Typical question | "Which asset wins next quarter?" | "Are we in early cycle or bubble?" | "Are we 20 years into a 75-year cycle?" |

An economy can simultaneously be in IC's **Recovery** phase
(Growth Up, Inflation Down → Stocks lead) AND in Dalio's short-cycle
**Bubble** phase (credit overstretching, 2–4 years until the regime
breaks). These are **not** contradictions — they are complementary
layers. The IC call is "stocks lead now"; the Dalio call is "but
the credit cycle will break the regime in 2–4 years, size down and
hedge accordingly".

## Koo Balance-Sheet Recession (Koo 2008) — the Japanese Parallel

Richard C. Koo (2008) *The Holy Grail of Macroeconomics: Lessons
from Japan's Great Recession* (Wiley Singapore) is the canonical JP
parallel to Dalio's Depression + Beautiful Deleveraging phases.
Koo's central observation, grounded in Japan's 1990–2005 experience:
when assets collapse in value relative to the debt financing them,
**firms switch from profit-maximization to debt-minimization**.
This behavioral shift produces a prolonged demand collapse even at
zero interest rates, because corporate balance-sheet repair takes
precedence over investment regardless of how cheap capital becomes.

Koo and Dalio are complementary:

- **Koo** focuses on the **corporate behavioral shift** during the
  Depression → Beautiful Deleveraging phases. His empirical base is
  heavily-documented Japan 1990s with lighter 2008 US and Euro
  crisis coverage.
- **Dalio** covers the **full 6-phase cycle** mechanism including
  preceding Bubble / Top and subsequent Pushing on a String /
  normalization phases. His empirical base is 48 historical crises.

When invoking Koo, name the book by title (*The Holy Grail of
Macroeconomics*, 2008) and attribute the balance-sheet recession
concept to Koo specifically. The Japanese 1990s "Lost Decade" is
the primary case study.

## Hedgeye GIP 4-Quadrant Model (McCullough, Dale et al., Hedgeye 2008+)

The Hedgeye Growth-Inflation-Policy (GIP) model is a **grey-literature
practitioner regime framework** developed by Keith McCullough and
Darius Dale at Hedgeye Risk Management (Stamford, CT) from 2008
onward. It is widely cited in the practitioner macro community but
has **no peer-reviewed validation** and no independently-audited
backtest.

### Core definition — 2-axis framework

GIP tracks two variables:

1. **Real GDP growth** year-over-year **rate of change** (second
   derivative — whether YoY growth is accelerating or decelerating
   relative to the previous period)
2. **Headline CPI inflation** (CPI index, not core) year-over-year
   **rate of change**

Two axes × two states each → **4 quadrants**. McCullough's
methodology uses **second derivatives** of YoY rates, not absolute
level vs trend (the key distinguishing feature from Greetham's
Investment Clock).

| Quad | Real Growth | Inflation | Hedgeye Label | Default Fed posture |
|------|-------------|-----------|---------------|----------------------|
| **Quad 1** | Accelerating ↑ | Decelerating ↓ | "Goldilocks" | Neutral |
| **Quad 2** | Accelerating ↑ | Accelerating ↑ | "Reflation" / "White-hot" | Hawkish |
| **Quad 3** | Decelerating ↓ | Accelerating ↑ | "Stagflation" | "In-a-box" |
| **Quad 4** | Decelerating ↓ | Decelerating ↓ | "Slowdown" / "Deflationary" | Dovish |

### "Policy" is a derived reaction function, not a third axis

The "P" in GIP is NOT an independent input variable. GIP does not
ask analysts to independently classify Fed stance. Policy is a
**1-to-1 mapping** from the Growth × Inflation quadrant to an
**expected Fed response**:

- Quad 1 → Neutral (disinflationary growth is benign for Fed)
- Quad 2 → Hawkish (inflation at / above target)
- Quad 3 → In-a-box (Fed cannot ease — inflation high; cannot tighten — growth weak)
- Quad 4 → Dovish (Fed cuts / QE)

**GIP is a 2-axis framework with a derived policy-reaction overlay,
not a 3-dimensional model in the independent-variable sense.**

### Asset playbook by Quad (summary)

| Quad | Best assets / sectors | Worst | Style factor preference |
|---|---|---|---|
| **Quad 1 (Goldilocks)** | Tech, Cons Disc, Materials, Industrials, Comm Services | Utilities, REITs, Cons Staples, Energy | High Beta, Momentum, Secular Growth |
| **Quad 2 (Reflation)** | Tech, Cons Disc, Industrials, Energy, Financials | Telecom, Utilities, REITs, Cons Staples, Health Care | Cyclical, nominal-growth |
| **Quad 3 (Stagflation)** | Gold, broad commodities, Energy, long-duration UST (later in quad) | High-beta equity, credit spreads widen | Defensive |
| **Quad 4 (Slowdown)** | USD, long-duration UST, Gold, Cons Staples, Utilities | High-beta Tech, Momentum, Russell 2000 Growth, HY credit | High Dividend Yield, Low Beta, Min Vol, Quality |

### Lineage and relationship to Investment Clock

| Dimension | ML Investment Clock (Greetham 2004) | Bridgewater 4-Box (Dalio 1996) | Hedgeye GIP (McCullough / Dale 2008+) |
|---|---|---|---|
| Origin | Greetham & Hartnett, ML internal report 2004-11-10 | Dalio / Bridgewater 1996 (Dalio family trust → All Weather) | McCullough + Dale, Hedgeye Risk Management |
| Venue | Sell-side bank research | Hedge fund internal → commercialized | Independent subscription research |
| Axes | Growth vs trend × Inflation vs trend | Growth expectations × Inflation expectations | Growth ROC × Inflation ROC + derived policy |
| Regime labels | Reflation → Recovery → Overheat → Stagflation | Rising/Falling × Rising/Falling | Quad 1/2/3/4 + nicknames |
| Intended use | Sell-side rotation heuristic | Risk-parity balance across 4 boxes | Active tactical concentration in current Quad |

**Key observations**:

1. All three are 2-axis growth × inflation frameworks. "3-axis GIP"
   is wrong.
2. Bridgewater's 4-box (1996) predates Greetham IC (2004) and
   Hedgeye GIP (2008) by 8 and 12 years respectively; it is the
   earliest progenitor. Hedgeye GIP's lineage flows from Bridgewater
   via Dale's public acknowledgment, not from Greetham.
3. GIP's novelty is **rate-of-change measurement + rules-based
   playbook**, not a new axis.
4. GIP and Bridgewater diverge on **intended use**: Dalio says "you
   cannot predict the Quad → risk-parity across all four"; Hedgeye
   says "you can predict via ROC → concentrate in current Quad".
   Opposite philosophies on the same 2×2 diagnostic.
5. GIP and Greetham IC are **siblings, not parent / child**.

### Backtest status

Hedgeye claims "grounded in over 27 years of back-tested history"
(~1998–present for US GIP). This is **firm-published, not
independently audited**. Hedgeye does not publicly disclose asset
universe, rebalancing frequency, transaction cost treatment, regime
transition handling, or data revision policy. Cite as **"Hedgeye
states ..."**, not as validated empirical fact.

### JP integration

**None.** Hedgeye is a US firm with English-only research; no
Japanese corpus describes GIP. Do not fabricate a JP GIP variant.

## Modern Monetary Theory (Mosler 1996 / Wray 2012 / Kelton 2020)

Modern Monetary Theory is a **heterodox macroeconomic framework**
that describes sovereign-currency-issuer fiscal and monetary
operations. In `investment-macro-regime.md` MMT is treated as
**background theory for regime analysis**, not as an investable
predictive model. Investment workers cite MMT to explain post-2008
fiscal / monetary behavior, never as a trade-signal generator.

### Origin and canonical texts

- **Mosler 1996** *Soft Currency Economics* — **origin document**.
  Mosler, a former hedge fund manager (Illinois Income Investors),
  developed the framework from his 1992 Italian bond trade: the
  market was pricing Italian sovereign default risk but Mosler
  reasoned that Italy (then a lira issuer) could always credit bank
  reserves to pay lira-denominated debt. He confirmed operational
  mechanics with Italian Treasury official Luigi Spaventa and took
  a ~$100M long position for clients. The 2012 expanded edition
  *Soft Currency Economics II: The Origin of Modern Monetary Theory*
  formalizes the framework.
- **Wray 2012** *Modern Money Theory: A Primer on Macroeconomics
  for Sovereign Monetary Systems* (Palgrave Macmillan; 2nd ed 2015;
  3rd ed 2024 Springer) — **canonical academic treatment**. Wray
  (UMKC; Levy Economics Institute) was Hyman Minsky's student.
- **Kelton 2020** *The Deficit Myth* (PublicAffairs) — **popular
  canonical**, NYT bestseller. Kelton is ex-Chief Economist, Senate
  Budget Committee Democratic staff under Bernie Sanders, and
  Sanders 2016/2020 campaign advisor.

### Intellectual ancestors (5 traditions MMT synthesizes)

MMT explicitly synthesizes five prior traditions:

- **Knapp (1905)** *The State Theory of Money* — chartalism,
  "money is a creature of law"; Wray calls MMT **neo-chartalism**
- **Mitchell-Innes (1913, 1914)** *Banking Law Journal* — credit
  theory of money; tally sticks / ledgers predate coinage
- **Lerner (1943)** "Functional Finance and the Federal Debt",
  *Social Research* 10(1): 38–51 — direct ancestor of MMT's
  policy framework (judge fiscal by real outcomes, not
  balance-sheet metrics)
- **Minsky (1986)** *Stabilizing an Unstable Economy* — financial
  instability hypothesis + employer-of-last-resort proposal (basis
  for Job Guarantee); Wray's dissertation advisor
- **Godley & Lavoie (2007)** *Monetary Economics* — sectoral
  balances three-sector identity: (Private + Government + Foreign
  surpluses) = 0, the accounting backbone of MMT

### Seven core MMT propositions (exact restatement, not worker voice)

When quoting MMT, use these propositions verbatim as "MMT
proponents argue ..." — never as "MMT shows / proves".

1. **Operational sovereignty**: a government that issues its own
   fiat currency, borrows only in that currency, and allows the
   exchange rate to float **cannot be forced to default** on
   domestic-currency obligations. Default is a political choice,
   not financial necessity. [Wray 2012 Ch 1–3; Kelton 2020 Ch 1]
2. **Binding constraint is inflation, not debt-to-GDP**: spending
   becomes a problem when aggregate demand exceeds real-resource
   capacity (labor / materials / productive capital). Debt-to-GDP
   is an accounting artifact. [Kelton 2020 Ch 2]
3. **Taxes drive money, not fund spending**: the operational
   sequence is spend-first-then-tax; tax liabilities denominated in
   state currency create currency demand. [Wray 2012 Ch 2; Mosler 1996]
4. **Deficits = non-government surplus (accounting identity)**:
   from Godley sectoral balances; a "balanced budget" forces either
   a private-sector deficit or a current account surplus.
5. **Functional finance**: fiscal policy should target real
   outcomes, not balance-sheet metrics. [Lerner 1943]
6. **Interest rates are a policy variable**: central banks choose
   short rates operationally and can anchor long rates (BoJ 2016–
   2024 YCC is the demonstration). [Kelton 2020 Ch 3]
7. **Job Guarantee as automatic stabilizer**: a permanent federal
   job offer at fixed wage functions as a counter-cyclical buffer
   stock of employed labor, simultaneously a price-stability
   mechanism and full-employment mechanism. [Tcherneva 2020
   *The Case for a Job Guarantee*]

### Mainstream critique (MUST cite alongside MMT)

- **Krugman (2019)** "Running on MMT" (NYT Opinion) — MMT ignores
  fiscal-monetary interest-rate tradeoff
- **Rogoff (2019)** "Modern Monetary Nonsense" (Project Syndicate)
  — calls MMT a "recipe for hyperinflation"; Weimar / Zimbabwe /
  Venezuela historical comparisons
- **Summers (2019)** *Washington Post* 2019-03-05 — "voodoo
  economics" and "the supply-side economics of our time"
- **Blanchard (2019)** "Public Debt and Low Interest Rates" AEA
  Presidential Address, *AER* 109(4): 1197–1229 — **partial
  endorsement of ONE MMT conclusion** (low r–g makes debt less
  costly) but **NOT MMT itself**; retains overlapping-generations
  framework and rejects MMT operational claims. Commonly misread.
- **Mankiw (2020)** "A Skeptic's Guide to Modern Monetary Theory",
  NBER WP 26650 / *AEA Papers and Proceedings* 110: 141–144 —
  concedes "kernels of truth" but novel policy prescriptions do
  not follow from premises. Most even-handed mainstream critique.
- **Palley (2015)** *Review of Political Economy* 27(1): 1–23 —
  **Post-Keynesian internal critique**, not mainstream; argues
  MMT is "a restatement of established Keynesian monetary
  macroeconomics", over-simplified, open-economy blind.
- **Powell (2019)** Senate Banking Committee testimony: *"The idea
  that deficits don't matter for countries that can borrow in
  their own currency I think is just wrong."* Fed on-record.
- **2019 IGM Forum poll** (Chicago Booth): **zero** agreement
  with MMT's strongest deficit claims.

### JP context — load-bearing

Japan is the most-cited real-world case for MMT and simultaneously
the most-contested. Workers writing about Japan must cite **both**
sides.

**The Japan-validates-MMT argument** (Kelton, Mitchell, Wray):
debt-to-GDP > 250%, 10-year JGB yield ~zero from ~2016 to ~2022
(BoJ YCC 2016–2024), average CPI inflation ~zero for ~20 years
(pre-2022), no insolvency / currency collapse / hyperinflation →
orthodox bond-vigilante prediction falsified.

**The Japan-does-NOT-validate-MMT arguments**:

- **黒田東彦 Haruhiko Kuroda** (BoJ Governor 2013–2023) publicly
  rejected MMT: *"全く同意できない"* (cannot agree at all, CEBRA
  New York 2019-07), restated 衆議院 Finance Committee 2019-11-13.
  **BoJ official on-record position**.
- **伊藤隆敏 Takatoshi Ito** (Columbia / GRIPS), Project Syndicate
  "Does Japan Vindicate Modern Monetary Theory?" (2021-12) —
  argues Japan's fiscal position hides an **intergenerational
  transfer** as working-age population shrinks.
- **藤巻健史 Takeshi Fujimaki** — calls Japan "the experimental
  ground of MMT" and predicts currency collapse via hyperinflation.
- **櫻川昌哉 Masaya Sakuragawa** (Keio) *金融経済研究* 44 (2021-12).
- **Nersisyan & Wray (2021)** Levy WP 985 "Has Japan Been Following
  MMT Without Recognizing It? No! And Yes" — nuanced both-sides:
  operational practice consistent with MMT description (yes);
  policymakers have not adopted the framework explicitly (no).

**Japanese MMT proponents**: **藤井聡 Satoshi Fujii** (Kyoto U;
ex-PM Abe advisor), *MMT による令和「新」経済論* (勁草書房 2019);
**中野剛志 Takeshi Nakano** (ex-METI); **西田昌司 Shoji Nishida**
(LDP senator; 2020-05 Diet advocacy of MMT-based consumption tax
cut).

**2022–2024 inflation stress test**: Japan CPI breached 2% in 2022
(first in decades); BoJ exited YCC 2024-03; yen weakened
significantly (140s → 160s 2024). MMT proponents: inflation was
cost-push (energy + yen), not demand-pull from fiscal excess.
Critics: goalpost-moving. **Case is genuinely open**; workers
writing post-2024 must present both interpretations.

### MMT anti-drift guardrails (enforce at runtime)

1. **Dual-citation rule**: every MMT claim MUST be paired with at
   least one mainstream-critique citation.
2. **Attribution discipline**: use "MMT proponents argue ..." /
   "Kelton 2020 claims ..." / "Wray 2012 frames ..." — never
   "MMT shows" / "MMT proves".
3. **Banned phrases** (except when directly quoting a critic):
   "just print money", "MMT solves", "Japan proves MMT",
   "deficits don't matter", "free lunch".
4. **Scope restriction preamble** (required when citing MMT in a
   research deliverable): "MMT's claims apply to sovereign currency
   issuers with floating exchange rates and domestic-currency debt
   (US, Japan, UK, Canada, Australia, Sweden). They do NOT apply
   to Eurozone members, emerging markets with significant USD
   debt, or dollarized economies."
5. **Post-2022 inflation caveat**: the 2021–2023 inflation episode
   is the contested empirical test of MMT in the modern record;
   present both interpretations.
6. **IGM Forum one-liner**: cite the 2019 IGM poll zero-endorsement
   result to show MMT is not textbook consensus.
7. **Japan dual-citation**: cite Kuroda + Fujii (or equivalent
   JP-side-by-side) when Japan is the case study; never present
   Japan as "proof" or "refutation" without acknowledging the live
   debate.

## Risk Appetite Index (Kumar & Persaud 2002 / Illing & Aaron 2005)

The Risk Appetite Index (RAI) family is a set of **positioning and
sentiment indicators** used by investment banks, central banks, and
academics to measure whether markets are in a risk-on (appetite)
or risk-off (aversion) state. The term is **genuinely ambiguous** —
between 2002 and 2008 at least 8 distinct methodologies were
published under "RAI" branding. This section disambiguates the
family and identifies the true academic origin.

### Concept lineage

**Kumar & Persaud (2002)** *International Finance* 5(3): 401–436 is
the **peer-reviewed academic origin** of the cross-sectional Global
Risk Appetite Index (GRAI). At any given time *t*, if investors'
aggregate risk appetite shifts, risky assets' cross-section should
show a **monotonic relationship** between past realized volatility
and subsequent excess return. Operationalized as the Spearman rank
correlation ρ between (a) prior-250-day realized volatility and
(b) subsequent monthly / quarterly excess return across *N* risky
assets:

- Risk appetite **high** when ρ > 0 (high-vol assets outperform —
  investors paying up for risk)
- Risk appetite **low** when ρ < 0 (low-vol assets outperform —
  flight to safety)

Kumar & Persaud tested originally on FX markets and US sector
equities. IMF and JPMorgan subsequently adopted GRAI for internal
monitoring (per Bank of Canada survey).

### Practitioner canonical — Credit Suisse RAI (Wilmot 2004)

**Wilmot, Mielczarski & Sweeney (2004-02)**, Credit Suisse First
Boston *Global Strategy Research: Market Focus* (subscription), is
a **linear-regression extension** of Kumar-Persaud applied daily to
64 bond+equity indexes across developed and emerging markets. The
slope coefficient from E(R_i,t+1) − R_f = α_t + β_t · σ_i,t + ε is
the RAI level. CSFB standardizes as a z-score; practitioner usage
treats −3σ ≈ panic / +3σ ≈ euphoria, but these thresholds are
**inferred from chart annotation, not disclosed by CS**. The
pre-2004 "Credit Suisse RAI 1981–2011" chart series was **backfilled**
— the actual live index began 2004-02.

### Other RAI variants (disclose, do not conflate)

| Variant | Author(s) | Publication | Method |
|---|---|---|---|
| **Kumar-Persaud GRAI** | Kumar & Persaud (2002) | *International Finance* 5(3): 401–436 | Spearman rank correlation — oldest peer-reviewed |
| **Credit Suisse RAI** | Wilmot, Mielczarski, Sweeney (2004-02) | CSFB *Market Focus* | Linear regression on 64 DM+EM indexes |
| **BIS RAI** | Tarashev, Tsatsaronis, Karampatos (2003-06) | *BIS Quarterly Review* | Ratio of statistical to option-implied left-tail distributions |
| **BoE RAI** | Gai & Vause (2005) | BoE WP 283 | Ratio of full distributions (not left-tail) |
| **State Street ICI** | Froot & O'Connell (2003-12) | **NBER WP 10157** | Holdings-based flow imbalance; 100 = neutral; monthly |
| **GS Risk-**Aversion** Index** | GS Economics Research (2003-10) | *The Foreign Exchange Market* | Consumption-CAPM Arrow-Pratt coefficient — **inverse semantics** |
| **JPMorgan LCVI** | Kantor & Caglayan (2002) | JPM *Global FX Research* | Percentile composite of spreads / VIX / FX vol / GRAI |
| **Citi Panic/Euphoria Model** | Levkovich (Citi 1990s+) | Citi Equity Strategy | 9-component composite; panic < 0.17, euphoria > 0.38 (circa 2011 calibration) |
| **BofA Bull & Bear Indicator** | Hartnett et al. (BofA, formalized ~2013) | BofA Global Research | 6-component composite, 0–10 scale; buy < 2.0, sell > 8.0; 16 sell signals since 2002, 63% accurate per BofA 2024 |

### Interpretation — contrarian signal at extremes

- **Panic territory** → forward 3–12 month returns tend positive
- **Euphoria territory** → forward 3–12 month returns tend negative
- **Neutral zone** → low informational content

### The load-bearing academic caveat

**Illing & Aaron (2005)** Bank of Canada FSR survey documented that
the 10 measured RAI indexes do NOT tell the same story — cross-
correlations among theory-based measures are often small or even
negative. CS RAI vs Kumar-Persaud GRAI correlation is approximately
**−2%** despite near-identical theoretical motivation (Illing &
Aaron Table 2). The survey's conclusion, which MUST appear in
every research deliverable that cites an RAI:

> *"Measurement of risk appetite is highly sensitive to the
> chosen methodology. It seems premature to rely on any given
> index when assessing risk appetite."*
> — Illing & Aaron (2005), Bank of Canada Financial System Review

### What RAI is NOT

- **RAI ≠ VIX**. VIX is option-implied volatility; RAI is positioning
  / sentiment / cross-section pricing pattern. Correlation ≠ identity.
- **RAI is positioning / sentiment-based, not fundamental**. No RAI
  variant uses GDP / earnings / valuation as input — all derive from
  market prices, flows, or cross-sectional return patterns.
- **"Single canonical RAI" does not exist**. The family is
  heterogeneous.

### JP integration

**No public JP-specific RAI variant**. Bank of Japan's *金融
システムレポート* (Financial System Report, semi-annual) contains a
**financial-activity heat map** (14 indicators — stock prices,
credit-to-GDP, real-estate prices — with green / yellow / red
thresholds), which is a macroprudential overheating signal rather
than a trading-desk risk-appetite indicator. Nomura / Daiwa / SMBC
Nikko do not publish branded RAI variants. Do NOT fabricate a
"Nomura RAI". If JP coverage is needed, cite BoJ FSR heat map as
the closest analogue while flagging the macroprudential-not-
sentiment distinction.

## Layer Complementarity

The five frameworks in this file are **complementary, not
substitute**. Each produces a different output and answers a
different question:

| Framework | Time horizon | Primary question | Output |
|---|---|---|---|
| **Investment Clock** | 1–3 years (tactical) | Which asset class leads in the current growth × inflation regime? | Explicit 4-asset call (Bonds / Stocks / Commodities / Cash) |
| **Dalio debt cycle (short)** | 5–8 years | Are we early / bubble / top / depression / beautiful deleveraging / pushing on a string? | Diagnostic phase ID, structural risk overlay |
| **Dalio debt cycle (long)** | 50–75 years | Are we 20 years into a 75-year cycle? | Diagnostic structural phase |
| **Koo balance-sheet recession** | Crisis-specific | Is the corporate sector in debt-minimization mode? | JP-parallel diagnostic during Depression / Beautiful Deleveraging |
| **Hedgeye GIP** | 1 quarter + (TREND) | Which of Quad 1 / 2 / 3 / 4 is the current ROC reading? | Active tactical rotation, sector / factor tilt |
| **MMT** | Structural / background | What fiscal / monetary state are we in; what are the real-resource constraints? | Background theory for interpreting post-2008 macro behavior |
| **RAI** | Days to months | Are positioning / sentiment at extremes? | Contrarian positioning indicator |

A single research deliverable can use all seven simultaneously:

- **IC call**: stocks lead in Recovery (Growth Up, Inflation Down)
- **Dalio short-cycle overlay**: but we are in Bubble phase,
  credit cycle will break in 2–4 years → size down
- **GIP refinement**: current reading is Quad 2 (Reflation),
  Hedgeye style playbook prefers Energy / Financials
- **MMT background**: post-2022 inflation is the stress test; real
  resources are tight but central bank and fiscal coordination is
  politically constrained
- **RAI check**: Bull & Bear Indicator at 7.8 → approaching sell
  signal → further size-down
- **Koo check**: does not apply (corporate sector not in
  debt-minimization mode in the US 2026 context; highly relevant
  to Japan 1990s case studies)

These layers form a **coherent risk-weighted tactical call**, not
a single monolithic forecast. The failure mode is treating any one
layer as the single canonical regime model.

See also: factor-regime mapping in `investment-sector-industry.md`
for how L1 phases translate into L2 factor-tilt decisions.
