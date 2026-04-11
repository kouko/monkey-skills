# Investment Analysis Protocol

Structured investment research — individual security analysis
and macro regime assessment. For market structure without
investment recommendation use `market-analysis.md`; for
competitor deep-dives use `competitive-analysis.md`.

## Primary Sources

- `standards/investment-analysis-canon.md` — Damodaran 2012 valuation taxonomy (DCF / Relative / Contingent-claim) + Graham & Dodd margin of safety + Mr. Market + Merrill Lynch Investment Clock (Greetham & Hartnett 2004) 2×2 growth × inflation matrix
- `standards/source-quality-and-evidence.md` — filings and central bank releases as primary; analyst reports and financial media as secondary
- `standards/confidence-and-claim-language.md` — Fact / Analysis / Speculation taxonomy and 高/中/低 confidence mapping for forward-looking claims

## Protocol

### Phase 0: Scope

1. **Define the investable question**: State the specific
   decision — single stock, sector rotation, asset allocation,
   macro regime call. Vague questions ("is X a good buy?") must
   be rewritten into testable form ("is X underpriced relative
   to its 3-framework intrinsic value at a ≥30% margin of safety?").
2. **Identify the right analytical lens**: Pick the appropriate
   valuation framework per `standards/investment-analysis-canon.md`
   §Damodaran's Valuation Taxonomy §Choosing Among the Three —
   the choice is a function of the asset and the question, not
   a preference.

### Phase 1: Individual Security Analysis

3. **Business Model**: Revenue sources, competitive moats, TAM,
   unit economics. Cite primary filings (10-K, 有価証券報告書) not
   analyst summaries per `standards/source-quality-and-evidence.md`.
4. **Financials**: Revenue growth, margins, FCF, balance sheet
   strength. Use official financial statements as the primary
   source. Note data date explicitly.
5. **Valuation**: Apply the three-framework taxonomy per
   `standards/investment-analysis-canon.md` §Damodaran's Valuation
   Taxonomy:
   - **DCF** (FCFF with WACC or FCFE with cost of equity) for mature
     firms with stable cash flows. Terminal growth rate must NOT
     exceed long-run nominal GDP growth (the single most common
     DCF modeling error).
   - **Relative** (P/E, EV/EBITDA, P/B, P/S) for firms embedded in
     a deep, well-matched comparable set. Match the comparable set
     rigorously; adjust for fundamental differences in growth, risk,
     and reinvestment.
   - **Contingent-claim / real options** for assets dominated by
     optionality (undeveloped reserves, early-stage patents, equity
     in distressed firms).
6. **Margin of Safety check**: Per `standards/investment-analysis-canon.md`
   §Graham & Dodd, require a substantial gap between price and
   intrinsic value estimate (canonical 30-50% discount, or ~2/3 of
   net current asset value for deep-value candidates). The margin
   of safety is the antidote to false precision in the valuation
   model — not an optional comfort.
7. **Catalysts**: Upcoming events, product launches, regulatory
   changes with explicit timeframes.
8. **Risks**: Key risk factors with probability and impact
   assessment. Counter-arguments are mandatory.

### Phase 2: Macro Regime Analysis

9. **Data**: Use official primary sources (Fed, BOJ, ECB, central
   bank reports, national statistics offices). Financial media
   citing central bank releases are secondary; cite the primary
   release.
10. **Indicators**: CPI, PMI, yield curve, employment, leading
    indicators. Always note the data date.
11. **Identify Investment Clock regime** per
    `standards/investment-analysis-canon.md` §The Merrill Lynch
    Investment Clock (Greetham & Hartnett 2004). The Investment
    Clock is a **2×2 growth direction × inflation direction**
    matrix with **four named regimes**:
    - **Reflation** (Growth ↓, Inflation ↓) → **Bonds** outperform
    - **Recovery** (Growth ↑, Inflation ↓) → **Stocks** outperform
    - **Overheat** (Growth ↑, Inflation ↑) → **Commodities** outperform
    - **Stagflation** (Growth ↓, Inflation ↑) → **Cash** outperforms

    Do **NOT** use business-cycle terminology (expansion / slowdown
    / contraction / recovery) when citing the Investment Clock —
    business cycles describe GDP dynamics; the Investment Clock
    describes relative asset-class performance across growth ×
    inflation regimes. The two are different concepts and
    conflating them is a fatal attribution error (see
    `standards/investment-analysis-canon.md` §Critical Attribution
    Corrections).
12. **Implications**: Map the identified regime to asset-class
    preferences using the Greetham 2004 mapping above. State
    confidence (高/中/低) per
    `standards/confidence-and-claim-language.md`.

### Phase 3: Output

13. **Price-independent verdict**: Per Graham's Mr. Market
    allegory in `standards/investment-analysis-canon.md` §Graham
    & Dodd, derive the intrinsic-value estimate from fundamentals
    **first**, then compare to market price — never the other way
    around. An analyst who anchors on current market price and
    reasons toward a valuation is doing reverse Mr. Market, a
    guaranteed calibration failure.
14. **Actionable recommendation**: Specific call (buy / hold / sell /
    overweight / underweight) with position sizing implication,
    explicit confidence level (高/中/低), and explicit data date.

## Rules

- Cite every factual claim with source; prefer primary filings
  and central bank releases over secondary commentary
- Apply the 3-framework valuation taxonomy explicitly — do not
  silently rely on "I think this stock is cheap"
- Terminal growth rate in DCF must never exceed long-run nominal
  GDP growth
- Never cite the Investment Clock with business-cycle terminology
- Include confidence level (高/中/低) on every forward-looking claim
- Always note the data date — stale data kills analysis
- Consult research notes (e.g., a user's personal vault) if
  available; otherwise rely on fresh primary-source research
  within this protocol

## Output Format

1. **Decision Question**: Precise, testable investment question
2. **Framework Selected**: Which of the 3 Damodaran frameworks
   applies and why
3. **Business & Financial Summary**: Key metrics with sources
4. **Valuation**: Intrinsic value estimate with margin of safety
   assessment
5. **Macro Regime** (if applicable): Investment Clock regime with
   evidence from growth + inflation indicators
6. **Catalysts & Risks**: Both sides, with timeframes
7. **Recommendation**: Specific action, confidence level (高/中/低),
   data date
