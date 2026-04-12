---
name: investment-sector-industry
description: L2 sector / industry / factor frameworks for rotation and factor-tilt decisions
tier: 2
layer: L2-sector
---

# Investment — L2 Sector / Industry / Factor

Tier 2 standard covering the **L2 sector / industry / factor layer**
of research-team's investment-analysis work: the frameworks used to
decide which sectors or factor styles to tilt toward, given an L1
macro regime view. This file is the SSOT for factor-investing
claims, factor-regime mapping, and sector-rotation-by-regime bridge
tables.

Tier 2 because Fama-French factor investing is well-indexed in LLM
training data as a family, but LLMs routinely mis-specify **which**
Fama-French model (3-factor 1993 vs 5-factor 2015), mis-attribute
momentum / quality / low-vol to Fama-French (they belong to Carhart
/ AQR / Frazzini-Pedersen respectively), and miss the Japan
exception that is load-bearing for any JP equity factor claim. The
body spells out the specific details LLMs confuse.

**Scope**: L2 sector and factor analysis → equity-portfolio tilt.
L1 macro regime belongs to `investment-macro-regime.md`; L3
individual security valuation belongs to
`investment-security-valuation.md`; portfolio construction belongs
to `investment-portfolio-construction.md`. For **individual sector
strategic analysis** (Porter Five Forces, Value Chain, BMC,
Blue Ocean), cross-reference `strategic-frameworks.md` — this L2
file focuses on **sector rotation** and **factor premia**, not
stand-alone sector diagnosis.

## Primary Sources

- Eugene F. Fama & Kenneth R. French (1992) "The Cross-Section of Expected Stock Returns." *Journal of Finance* 47(2): 427–465. The empirical paper that killed single-factor CAPM by showing size and book-to-market capture cross-section of expected returns, and that market-β slope is flat when allowing β variation unrelated to size. Does NOT yet present the operational 3-factor model.
- Eugene F. Fama & Kenneth R. French (1993) "Common Risk Factors in the Returns on Stocks and Bonds." *Journal of Financial Economics* 33(1): 3–56. **The operational 3-factor model**: introduces SMB (Small Minus Big) and HML (High Minus Low) as mimicking portfolios traded against the Mkt-Rf market-excess-return factor. When practitioners say "Fama-French three-factor model", this is the canonical citation.
- Eugene F. Fama & Kenneth R. French (2015) "A Five-Factor Asset Pricing Model." *Journal of Financial Economics* 116(1): 1–22. **The 5-factor extension**: adds RMW (Robust Minus Weak) for operating profitability and CMA (Conservative Minus Aggressive) for asset-growth / investment, based on a dividend-discount decomposition. **FF5 explicitly excludes momentum**; once RMW + CMA are included, HML becomes statistically redundant.
- Eugene F. Fama & Kenneth R. French (2012) "Size, Value, and Momentum in International Stock Returns." *Journal of Financial Economics* 105(3): 457–472. Tests 3-factor + momentum across North America / Europe / Japan / Asia Pacific. **Load-bearing finding**: value exists in all four regions, but *"except for Japan, there is return momentum everywhere"*; local factor models outperform global ones for NA / Europe / Japan.
- Mark M. Carhart (1997) "On Persistence in Mutual Fund Performance." *Journal of Finance* 52(1): 57–82. **Momentum factor canonical citation** as addition to FF framework. "Carhart 4-factor model" = FF3 + WML/UMD. **Not a Fama-French paper** — Carhart packaged the Jegadeesh-Titman 1993 momentum anomaly as a factor portfolio.
- Narasimhan Jegadeesh & Sheridan Titman (1993) "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency." *Journal of Finance* 48(1): 65–91. The **momentum anomaly's** original empirical discovery (3–12 month winners outperform losers over 3–12 month holding), not explained by systematic risk. Carhart later packaged this as the UMD factor.
- Clifford S. Asness, Andrea Frazzini & Lasse H. Pedersen (2019) "Quality Minus Junk." *Review of Accounting Studies* 24(1): 34–112. **Canonical primary source for the Quality factor as implemented by AQR and adopted by practitioner factor ETFs**. Quality is a rank-composite of profitability + growth + safety. **QMJ is NOT FF RMW** — RMW captures only operating profitability.
- Andrea Frazzini & Lasse H. Pedersen (2014) "Betting Against Beta." *Journal of Financial Economics* 111(1): 1–25. **Canonical primary source for the low-volatility / low-beta anomaly as a tradable factor**. The BAB factor longs leveraged low-β assets and shorts deleveraged high-β assets, with each leg β = 1 at formation. US 1926–2012 Sharpe ≈ 0.78. Theoretical mechanism: funding/leverage constraint. **No Fama-French paper defines a low-volatility factor**.
- Kosuke Kubota & Hitoshi Takehara (2018) "Does the Fama and French Five-Factor Model Work Well in Japan?" *International Review of Finance* 18(1): 137–146. **Canonical primary source for the JP factor-model exception**. Tests FF5 on 1978–2014 Japanese stock data and finds **RMW and CMA are not statistically significant** in GMM tests with Hansen-Jagannathan distance metrics. Conclusion: original FF5 is not the best benchmark pricing model for Japan.
- Clifford S. Asness (2011) "Momentum in Japan: The Exception that Proves the Rule." *Journal of Portfolio Management* 37(4): 67–75. **Canonical practitioner rebuttal to "momentum is dead in Japan"**. Value and momentum in Japan have strong negative correlation (ρ ≈ −0.55), so a zero-Sharpe momentum leg with large negative correlation to positive-Sharpe value is a valuable hedge, not a broken factor.
- Strategic-frameworks cross-reference: see `strategic-frameworks.md` for Porter Five Forces / Blue Ocean / Value Chain / Business Model Canvas (individual sector strategic analysis). This L2 file focuses on rotation and factor premia, not stand-alone sector diagnosis.

## Critical Attribution Corrections

### "Fama-French" must specify which model (3 vs 5)

LLMs routinely cite "the Fama-French model" without specifying 3-factor
or 5-factor. These are **distinct models** from distinct papers:

- **"Fama-French 3-factor"** ≡ Fama & French 1993 *JFE* 33(1) =
  {Mkt-Rf, SMB, HML}
- **"Fama-French 5-factor"** ≡ Fama & French 2015 *JFE* 116(1) =
  {Mkt-Rf, SMB, HML, RMW, CMA}

FF5 is **not a simple addition** of RMW + CMA to FF3. The 2015
paper respecifies SMB to be orthogonal to the new factors and notes
that HML becomes statistically redundant once RMW + CMA are
included (its mean return is absorbed), though HML is retained for
consistency. Cite the specific paper, not "Fama-French" in generic.

### FF5 EXCLUDES momentum

Fama & French 2015 and their follow-up 2016 "Dissecting Anomalies"
paper explicitly exclude momentum from the 5-factor model. Their
stated position is that momentum is a "lethal challenge" behavioral
pattern rather than an integral part of a rational asset-pricing
model. **If you need a momentum-inclusive factor model, use Carhart
4-factor or an ad-hoc "FF5 + UMD" specification** — do not say
"Fama-French model" and mean to include momentum.

### Carhart 4-factor is NOT a Fama-French paper

Carhart 1997 *JoF* 52(1) = **FF3 + UMD** (Up Minus Down / Winners
Minus Losers). It is a separate paper by a separate author. The
term "Fama-French-Carhart 4-factor" is common shorthand but Fama
and French are not construction authors of the 4-factor model.
Cite Carhart 1997 for the 4-factor specification; cite Carhart as
"FF3 + momentum, per Carhart 1997" — do not compress to
"Fama-French-Carhart".

### Momentum anomaly origin vs factor construction

- **Empirical anomaly**: Jegadeesh & Titman 1993 *JoF* 48(1) —
  buying 3–12 month winners and shorting 3–12 month losers
- **Factor-portfolio construction (UMD / WML)**: Carhart 1997 *JoF*
  52(1)
- **Neither is a Fama-French paper**

Cite momentum-as-anomaly → Jegadeesh-Titman 1993. Cite momentum-
as-factor → Carhart 1997. Do not attribute either to Fama-French.

### Quality factor = AQR QMJ, not FF RMW

Fama-French 2015 RMW captures **only operating profitability** — a
single metric defined as (revenues − COGS − SG&A − interest) ÷ book
equity. The Asness-Frazzini-Pedersen 2019 **QMJ** factor is a
**rank-composite of three sub-scores**:

- **Profitability** (gross profits / assets, ROE, ROA, cash-flow /
  assets, gross margin, accruals)
- **Growth** (prior 5-year growth in profitability measures)
- **Safety** (low β, low leverage, low earnings volatility, low
  bankruptcy risk)

Practitioner Quality factor ETFs (iShares QUAL, MSCI USA Quality)
align with QMJ construction, not RMW. Do NOT cite "Fama-French"
for the Quality factor — cite **Asness, Frazzini, Pedersen (2019)
*Review of Accounting Studies* 24(1): 34–112**.

### Low-Volatility factor = Frazzini-Pedersen BAB, not Fama-French

**No Fama-French paper defines a low-volatility factor.** The
canonical source is **Frazzini & Pedersen (2014) *JFE* 111(1)**.
The BAB factor longs leveraged low-β assets and shorts deleveraged
high-β assets. Practitioner Min-Vol ETFs (iShares USMV) use MSCI
minimum-variance optimization — a different construction that
exploits the same funding / leverage-constraint premium. Cite BAB
for the anomaly; cite MSCI Min Vol for the ETF construction.

### Fama-French is NOT APT

**APT (Ross 1976 *Journal of Economic Theory* 13(3): 341–360)** is
a theoretical no-arbitrage argument that asset returns can be
expressed as linear combinations of **unspecified** systematic
factors. APT provides the mathematical foundation (factor structure
+ no-arbitrage → linear factor pricing) but does NOT specify which
factors.

**Fama-French is an empirical factor-pricing model** — it specifies
SMB / HML / RMW / CMA based on characteristic sorts, with no
theoretical argument for why these specific characteristics should
be priced.

Correct framing: "APT is the theoretical umbrella; FF is one
empirical specification that sits under that umbrella." But FF is
not a literal APT test, and FF papers do not cite APT as their
foundation — they build from CAPM literature empirically. **Do NOT
say "Fama-French is a specific case of APT"** as a primary claim.

### Fama-French SUBSUMES CAPM, does not replace it

CAPM (Sharpe 1964, Lintner 1965) is a single-factor model with
market risk only. FF3 preserves Mkt-Rf as the first factor and adds
SMB + HML to capture cross-sectional variation β cannot explain.
Fama & French 1992 empirically showed β alone is insufficient —
when size is controlled for, the β-return slope is flat. The market
factor is NOT removed in FF; it is the first component and is
augmented. Frame FF as a multi-factor extension of CAPM, not a
replacement.

### Japan is the load-bearing exception — 3 papers, never omit

Any claim about factor investing applied to Japanese equities MUST
cite all three of the following, because each captures a different
piece of the Japan exception:

1. **Kubota & Takehara 2018** *International Review of Finance*
   18(1) — FF5 RMW and CMA are not statistically significant in
   Japan 1978–2014 GMM tests. Recommends FF3 or Carhart 4-factor
   (with domestic factor data from Nomura / Daiwa) as the JP
   equities base pricing model.
2. **Fama & French 2012** *JFE* 105(3) — Japan is the momentum
   exception globally; use **local** factor models rather than
   global ones.
3. **Asness 2011** *JPM* 37(4) — Japan's zero-Sharpe momentum leg
   is still valuable as a hedge within a combined value-momentum
   sleeve due to strong negative correlation with value (ρ ≈ −0.55).
   Do not discard momentum from Japanese factor portfolios.

A JP-facing factor claim that omits any of these three is
**incomplete** by this standard.

### Nobel credit is joint, not for the 3-factor model

The 2013 Sveriges Riksbank Prize in Economic Sciences was **jointly**
awarded to **Eugene Fama, Lars Peter Hansen, and Robert Shiller**
"for their empirical analysis of asset prices". The Nobel citation
covers Fama's body of empirical asset-pricing work including
efficient-markets theory (Fama 1970) and tests of CAPM, not
specifically the 3-factor model. Do NOT say "Fama won the Nobel
for the 3-factor model".

### Practitioner ETF construction ≠ academic FF factor

Academic Fama-French factors (SMB, HML, RMW, CMA) are **long-short**
portfolios. Practitioner factor ETFs (iShares MTUM, VLUE, QUAL) are
**long-only tilts** — they rank stocks by characteristic and weight
toward the top half, with no short leg. Practitioner factor ETF
return therefore contains market beta; it is not pure factor
premium. MSCI also applies sector-neutral constraints and
composite characteristic definitions (e.g. MSCI Enhanced Value
combines P/B, P/E-forward, EV/CFO, not B/M alone). Fee drag of
15–30 bps further eats into thin factor premia. **The factor-regime
mapping table below directionally applies to both, but magnitudes
differ.**

## Sector Analysis Frameworks — Cross-Reference

For stand-alone strategic analysis of an individual sector or
company (Porter Five Forces, Value Chain, Blue Ocean Strategy,
Business Model Canvas), see `strategic-frameworks.md`. That file
is shared with `C3-market-analysis.md` and
`C4-competitive-analysis.md` workflows and is the SSOT for
five-forces-style diagnosis.

**This file (`investment-sector-industry.md`) focuses on two
different L2 questions:**

1. **Sector rotation by L1 regime** — given a macro regime view
   from `investment-macro-regime.md`, which sectors historically
   lead?
2. **Factor premia** — which factor styles (Value, Momentum,
   Quality, Low-Vol, Size) generate excess return over the market
   portfolio, and how do they map to regime?

## Fama-French 3-Factor Model (Fama & French 1993)

The FF3 operational model expresses an asset's expected return as:

```
E(R_i) − R_f = β_i,Mkt · (E(R_M) − R_f) + β_i,SMB · E(SMB) + β_i,HML · E(HML)
```

where the three factors are defined as follows.

### Mkt-Rf — market excess return

Value-weight return on the market portfolio minus the 1-month
T-bill risk-free rate. This is the CAPM single factor; FF3 preserves
it as the first factor. **Not a long-short portfolio — it is a
direct market excess return.**

### SMB — Small Minus Big

Average return on small-cap portfolios minus average return on
large-cap portfolios, constructed via a **2×3 sort** of market-cap
median (Small / Big) × B/M tercile 30/70 NYSE breakpoint
(Growth / Neutral / Value):

```
SMB = (1/3) · (Small Value + Small Neutral + Small Growth)
    − (1/3) · (Big Value + Big Neutral + Big Growth)
```

**Interpretation**: long small-caps, short large-caps, approximately
dollar-neutral within size quintile.

### HML — High Minus Low (value factor)

Average return on high B/M (value) portfolios minus average return
on low B/M (growth) portfolios:

```
HML = (1/2) · (Small Value + Big Value) − (1/2) · (Small Growth + Big Growth)
```

where Value = top 30% B/M and Growth = bottom 30% B/M within each
size group, using NYSE breakpoints for big stocks. Book equity uses
prior-year-end accounting data lagged 6 months (matching
July-of-year-t return to December-of-year-(t−1) book equity).

**Data source**: Kenneth French Data Library,
http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html.
This is the definitive operational reference for factor
construction — used by academic tests and most practitioner
factor-tilt portfolios.

## Fama-French 5-Factor Model (Fama & French 2015)

FF5 adds two factors to FF3, based on a dividend-discount
decomposition that links expected return to profitability and
investment at constant B/M:

```
E(R_i) − R_f = β_i,Mkt · (E(R_M) − R_f)
             + β_i,SMB · E(SMB)
             + β_i,HML · E(HML)
             + β_i,RMW · E(RMW)
             + β_i,CMA · E(CMA)
```

### RMW — Robust Minus Weak (profitability factor) [FF5 only]

Average return on high operating-profitability portfolios minus
average return on low operating-profitability portfolios, via 2×3
sort:

```
RMW = (1/2) · (Small Robust + Big Robust) − (1/2) · (Small Weak + Big Weak)
```

**Operating profitability** = (revenues − COGS − SG&A − interest
expense) ÷ book equity, computed from the most recent fiscal year
ending before July of year *t*. Robust = top 30% OP; Weak = bottom
30% OP. Economic interpretation: captures the gross-profitability
anomaly (Novy-Marx 2013).

### CMA — Conservative Minus Aggressive (investment factor) [FF5 only]

Average return on low-asset-growth (conservative) portfolios minus
average return on high-asset-growth (aggressive) portfolios:

```
CMA = (1/2) · (Small Conservative + Big Conservative)
    − (1/2) · (Small Aggressive + Big Aggressive)
```

**Investment** = asset growth = (total_assets_t − total_assets_{t−1})
/ total_assets_{t−1}. Conservative = bottom 30% asset growth;
Aggressive = top 30%. Economic interpretation: asset growth
anomaly (Cooper, Gulen, Schill 2008).

### FF5 respecifies SMB

In FF5, SMB is averaged across **three** 2×3 sorts (one on B/M,
one on OP, one on INV) to remove loading on HML, RMW, CMA:

```
SMB = (1/3) · SMB(B/M) + (1/3) · SMB(OP) + (1/3) · SMB(INV)
```

This is a subtle but load-bearing distinction: FF3 SMB and FF5 SMB
are **not the same series**, even though they share the name.

### HML becomes redundant in FF5

Fama & French 2015 document that once RMW + CMA are included, HML's
mean return is **absorbed** (statistically redundant). HML is
retained for consistency with FF3 but is no longer the load-bearing
value signal in the 5-factor model.

### FF5 momentum exclusion — explicit

FF5 does **not** include a momentum factor. Fama & French 2015/2016
explicitly excluded momentum as a "lethal challenge" behavioral
pattern unsuitable for a rational asset-pricing model. If a
practitioner needs a momentum-inclusive specification, use Carhart
4-factor (FF3 + UMD) or an ad-hoc FF5 + UMD construction.

## Carhart 4-Factor Model (Carhart 1997)

**Carhart 4-factor** = FF3 + **UMD** (Up Minus Down, also written
WML = Winners Minus Losers). From Carhart 1997 *JoF* 52(1): 57–82,
"On Persistence in Mutual Fund Performance".

### UMD — momentum factor construction

Ranked by **prior-12-month return skipping the most recent month**
(months *t*−12 through *t*−2, excluding *t*−1 to avoid short-term
reversal). The Kenneth French data library constructs UMD via a
2×3 sort on size × prior-12-2 return:

```
UMD = (1/2) · (Small Winners + Big Winners)
    − (1/2) · (Small Losers + Big Losers)
```

where Winners = top 30% prior return, Losers = bottom 30%.

### Carhart's core finding

Mutual fund "hot hands" persistence is explained by loading on the
momentum factor, not by manager skill. This is the paper's primary
contribution — the 4-factor specification is the tool used to
decompose fund returns.

### Not a Fama-French paper

Carhart 1997 is by Mark M. Carhart, not by Fama or French. The
UMD factor lives on Kenneth French's data library website for
distribution convenience (it uses French's factor-construction
convention), but the factor and the 4-factor model belong to
Carhart.

## Factor Attribution Traps — Consolidated Anti-Drift

LLMs routinely mis-attribute practitioner factors to Fama-French.
The correct attributions:

| Factor | Correct primary source | NOT Fama-French |
|---|---|---|
| **Market (Mkt-Rf)** | Sharpe 1964 / Lintner 1965 (CAPM), preserved in FF3/5 | n/a (FF preserves it) |
| **Size (SMB)** | Fama & French 1993 *JFE* 33(1) | ✓ FF3/5 |
| **Value (HML)** | Fama & French 1993 *JFE* 33(1) | ✓ FF3/5 |
| **Profitability (RMW)** | Fama & French 2015 *JFE* 116(1) | ✓ FF5 only |
| **Investment (CMA)** | Fama & French 2015 *JFE* 116(1) | ✓ FF5 only |
| **Momentum (UMD / WML)** | Carhart 1997 *JoF* 52(1); anomaly from Jegadeesh-Titman 1993 *JoF* 48(1) | ❌ NOT FF |
| **Quality (QMJ)** | Asness, Frazzini, Pedersen 2019 *Review of Accounting Studies* 24(1): 34–112 | ❌ NOT FF RMW |
| **Low-Volatility (BAB)** | Frazzini & Pedersen 2014 *JFE* 111(1) | ❌ no FF low-vol |
| **Arbitrage Pricing Theory (APT)** | Ross 1976 *JET* 13(3): 341–360 — theoretical, not empirical | Different framework |

Additional rules:

- **Always specify FF3 (1993) vs FF5 (2015)** when citing
  "Fama-French". The two models are distinct and have distinct
  SMB construction.
- **Do NOT compress "FF3 + momentum, per Carhart 1997" to
  "Fama-French-Carhart"** — it invites the reader to assume Fama
  and French co-authored the momentum factor.
- **Practitioner Quality ETFs track QMJ, not RMW** — iShares QUAL,
  MSCI USA Quality. Cite Asness-Frazzini-Pedersen 2019.
- **Practitioner Min-Vol ETFs track MSCI Min Var optimization,
  related to but distinct from BAB**. Both exploit the
  funding/leverage-constraint premium Frazzini-Pedersen identified.

## Sector Rotation by L1 Regime

Bridging table: which sectors historically lead in each L1
Investment Clock phase (per Greetham & Hartnett 2004 supplementary
analysis and standard sell-side sector-performance empirical
tables).

| IC Phase | Growth | Inflation | Leading sectors | Lagging sectors |
|---|---|---|---|---|
| **Reflation** | ↓ | ↓ | **Long-duration bonds**, utilities, REITs, bond proxies | Cyclicals, energy, commodities |
| **Recovery** | ↑ | ↓ | **Consumer discretionary**, tech, financials, industrials | Defensives (utilities, staples), cash |
| **Overheat** | ↑ | ↑ | **Energy**, materials, industrials, broad commodities | Long-duration bonds, high-multiple tech |
| **Stagflation** | ↓ | ↑ | **Cash**, defensive sectors (utilities, staples, healthcare), short-duration fixed income | Cyclicals, high-beta equity, credit |

### Dalio debt-cycle sector mapping (inferred parallel)

Mapping Dalio's 6 canonical phases to sector leadership is less
established in published research (Dalio does not write factor or
sector investing). Reasonable inference:

| Dalio phase | Analogous IC phase | Expected sector leadership |
|---|---|---|
| **Early** | Recovery | Consumer discretionary, tech, financials |
| **Bubble** | Overheat (late) | Momentum leadership; high-multiple tech, growth-at-any-price |
| **Top** | Stagflation (entry) | Quality flight; late-cycle defensives starting to outperform |
| **Depression** | (sui generis) | Quality, low-vol, long-duration bonds, cash |
| **Beautiful deleveraging** | Reflation → Recovery | Value, size, cyclicals as growth normalizes |
| **Pushing on a string** | Stagnation (sui generis) | Quality, low-vol, high dividend yield |

**Flag**: this Dalio → sector mapping is synthesized, not a direct
Dalio claim. Cite as "inferred parallel" or "analogous to IC
phase X" rather than as Dalio's explicit call.

## Factor × Regime Mapping — the Load-Bearing L2-to-L1 Bridge

This is what makes L2 factor analysis actionable from an L1 regime
view. Academic and practitioner consensus maps factor premia to
macro regime phases as follows.

**Primary citations**:

- **Polk, Haghbin & de Longis (2020)** "Time-Series Variation in
  Factor Premia: The Influence of the Business Cycle."
  *Journal of Investment Management* 18(1). Canonical academic
  reference for factor-cycle dynamics — regime-based dynamic
  rotation outperforms static equal-weight factor blending, net of
  transaction cost.
- **MSCI (Bender et al.)** "Foundations of Factor Investing" +
  "Adaptive Multi-Factor Allocation" research notes. Canonical
  practitioner reference. MSCI classifies factors as
  **pro-cyclical** (Value / Size / Momentum) versus **defensive**
  (Quality / Low-Vol / High Dividend Yield).

### Factor-by-factor regime mapping

Synthesis of Polk-Haghbin-de Longis 2020 + MSCI Bender et al. +
OSAM 2016 "Economic Cycle: A Factor Investor's Perspective":

| Factor | Pro / Defensive | Best phase | Worst phase | Mechanism |
|---|---|---|---|---|
| **Value (HML)** | Pro-cyclical | Recovery → early Reflation transition | Stagflation, late-cycle Overheat | Cheap stocks re-rate when growth restarts; value is the bet on economic normalization |
| **Size (SMB)** | Pro-cyclical | Recovery (early cycle) | Contraction, slowdown | Small-caps are more sensitive to domestic credit conditions; lever up in recovery |
| **Momentum (UMD)** | Pro-cyclical (distinct mode) | Expansion / steady regime (trends persist) | Regime inflection point (sharp reversal — 2009 / 2020 crash the factor) | Momentum is trend-following; fails when macro regime changes faster than look-back window |
| **Quality (QMJ)** | Defensive | Contraction / late-cycle slowdown (flight to safety) | Early cycle / reflation (junk rally dominates) | High-profitability + low-leverage firms survive credit crunches; underperform in "trash rallies" |
| **Low-Vol (BAB / USMV)** | Defensive | Stagflation, contraction (downside protection) | Strong reflation / recovery (beta rallies) | Funding-constraint premium + lower downside capture; bull regime drag |
| **Profitability (RMW)** | Mildly defensive | Late cycle / contraction | Early reflation | Mechanism similar to QMJ but narrower in construction |
| **Investment (CMA)** | Mildly defensive | Late cycle / slowdown | Early recovery | Conservative-investment firms lag when capex animal-spirits dominate |

### Mapping to Investment Clock phases explicitly

Cross-referencing `investment-macro-regime.md` §Merrill Lynch
Investment Clock, the mapping is:

- **Reflation** (Growth Down, Inflation Down, Bonds leadership):
  defensive factors (Quality, Low-Vol) outperform; Value is weak
  because recovery hasn't begun
- **Recovery** (Growth Up, Inflation Down, Stocks leadership):
  **Value + Size outperform** (pro-cyclical factor lead); Quality
  lags
- **Overheat** (Growth Up, Inflation Up, Commodities leadership):
  **Momentum continues**; Value plateaus; Quality + Low-Vol start
  to rebuild
- **Stagflation** (Growth Down, Inflation Up, Cash leadership):
  **Quality + Low-Vol outperform**; Momentum breaks at inflection;
  Value underperforms

This is the load-bearing L2-to-L1 bridge. Factors are the vehicle
that translates an L1 regime view into an actionable equity-
portfolio tilt.

## Factor ETF Industry Adoption (practitioner context)

Making L2 factor analysis operational via ETFs:

| ETF | Ticker | Launch | Benchmark | Notes |
|---|---|---|---|---|
| iShares MSCI USA Min Vol | USMV | 2011-10-18 | MSCI USA Minimum Volatility Index | First wave of factor ETFs |
| iShares MSCI USA Momentum | MTUM | 2013-04-16 | MSCI USA Momentum (6m + 12m risk-adjusted) | Not identical to Carhart UMD |
| iShares MSCI USA Value | VLUE | 2013-04-16 | MSCI USA Enhanced Value (P/B, P/E-fwd, EV/CFO composite) | Not identical to HML |
| iShares MSCI USA Quality | QUAL | 2013-04-16 | MSCI USA Sector Neutral Quality (ROE, D/E, earnings variability) | Aligned with QMJ philosophy, not FF RMW |
| iShares MSCI USA Size | SIZE | 2013-04-16 | MSCI USA Risk Weighted Index | Not identical to SMB |

Smart-beta ETF AUM reached approximately US$1.56 trillion globally
by early 2024 (ETFGI), roughly 8% of the broader ~$19.4T ETF
universe. **Practitioner factor ETF construction is long-only,
sector-neutral, and uses composite characteristic definitions** —
directionally aligned with academic factors but not identical.

## Japan — Load-Bearing Exception

Any factor-investing claim applied to Japanese equities MUST cite
all three of the following:

1. **Kubota & Takehara 2018** *International Review of Finance*
   18(1) — FF5 RMW and CMA are not statistically significant on
   Japanese data 1978–2014. Recommendation: use FF3 or Carhart
   4-factor with domestic factor data (Nomura / Daiwa) as the base
   pricing model for JP equities.
2. **Fama & French 2012** *JFE* 105(3) — "except for Japan, there
   is return momentum everywhere"; use local factor models, not
   global ones, for NA / Europe / Japan.
3. **Asness 2011** *JPM* 37(4) — Japan's near-zero Sharpe momentum
   leg is still valuable as a hedge within a value-momentum sleeve
   (ρ ≈ −0.55 with value). Do NOT discard momentum from JP factor
   portfolios based on raw-return failure alone.

The inverse pattern to US post-2010: in Japan, **value survives**
while momentum struggles; in the US post-2010, value struggled
while momentum led. Regional factor dynamics are distinct — do not
assume US factor empirics transfer to Japan.
