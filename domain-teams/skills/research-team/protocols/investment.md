# Investment Analysis Protocol

Structured investment research — individual security analysis
and macro regime assessment. For market structure without
investment recommendation use `market-analysis.md`; for
competitor deep-dives use `competitive-analysis.md`.

## Primary Sources

- `standards/investment-analysis-canon.md` — Damodaran 2012 valuation taxonomy (DCF / Relative including Campbell & Shiller 1998 CAPE cycle-smoothing / Contingent-claim) + Graham & Dodd margin of safety + Mr. Market + Merrill Lynch Investment Clock (Greetham & Hartnett 2004) 2×2 growth × inflation matrix + Dalio 2018 two-horizon debt-cycle framework (6 phases × {short 5-8 yr, long 50-75 yr}) + Koo 2008 balance-sheet recession JP parallel
- `standards/source-quality-and-evidence.md` — filings and central bank releases as primary; analyst reports and financial media as secondary
- `standards/confidence-and-claim-language.md` — Fact / Analysis / Speculation taxonomy and 高/中/低 confidence mapping for forward-looking claims

## Phase 0: Mode Detection and Budget Setup

**MUST run before Phase 1.** Read the `mode:` field from the worker
launch `### Input` section. If absent, default to `quick`.

| Mode | Default budget | Source cap | Search cap | Token cap |
|---|---|---|---|---|
| **quick** (default) | single-pass triangulation | 5 sources | 5 web searches | ~15k tokens |
| **deep** (opt-in) | full audit trail | 15 sources | 20 web searches | ~150k tokens |

User-overridable via `### Input` fields: `max_sources`, `max_web_searches`,
`max_tokens`. Reject budgets below quick floor (15k tokens / 5 sources)
with `BLOCKED: budget below minimum viable quick mode`.

In **quick mode**, this protocol runs in a stripped-down form per the
mode-specific exit rule defined in `standards/confidence-and-claim-language.md`
§Cost-Aware Early-Exit Rule:
- Skip cross-language (EN+JP) parallel search unless natural
- ≥1 primary source per key claim is sufficient (vs ≥2 for deep)
- Exit immediately when all key claims reach Medium confidence
  (medium evidence × medium agreement on the IPCC 3×3 grid)
- Skip MUST `source-citation-checklist` gate (SELF check applies)
- Quick-mode reduction: skip Damodaran 3-framework deep dive — use
  the single most appropriate framework only (DCF, relative, or
  contingent-claim, per the asset type); skip Investment Clock
  2×2 macro regime analysis entirely (call the regime in one line
  without full matrix construction); skip Dalio debt-cycle deep
  dive — one-line phase call only (e.g., "late-cycle bubble phase"),
  no full 6-phase enumeration; skip CAPE cycle-smoothing — use
  rolling P/E only; skip Graham margin-of-safety detailed
  calculation (narrative bracket only, e.g., "~30% margin" without
  per-line derivation)

In **deep mode**, run the protocol per the existing v4.9.0 grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full Damodaran 3-framework valuation (DCF +
  relative + contingent-claim where applicable) with CAPE
  cycle-smoothing against Campbell & Shiller 1998 historical bands
  for cyclical or market-level equity calls + Merrill Lynch
  Investment Clock 2×2 regime identification (Reflation / Recovery
  / Overheat / Stagflation — NEVER business-cycle terminology) +
  Dalio 2018 full 6-phase debt-cycle identification for BOTH the
  short-term (5-8 yr) and long-term (50-75 yr) cycles as a
  structural risk overlay + Graham margin-of-safety detailed
  calculation + Mr. Market price-independent verdict discipline

**Budget enforcement**: track source count, search count, token
estimate. On overrun, finish current source verification (atomic),
then return BLOCKED with summary: `"budget overrun: collected N
sources, M searches, ~Tk tokens. Partial result attached. Reply
'expand budget to X' or 'accept partial'."`

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific exit thresholds and the
per-claim (not per-deliverable) policy.

## Protocol

### Phase 1: Scope

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

### Phase 2: Individual Security Analysis

**Mode discipline**: in quick mode, cap collection per Phase 0
budget; in deep mode, follow existing collection workflow.

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
   - **Relative** (P/E, EV/EBITDA, P/B, P/S, or **CAPE** for
     cyclicals and market-level equity calls) for firms embedded
     in a deep, well-matched comparable set. Match the comparable
     set rigorously; adjust for fundamental differences in growth,
     risk, and reinvestment. Use **CAPE** (Campbell & Shiller 1998
     10-year real-earnings smoothing, per
     `standards/investment-analysis-canon.md` §Cyclically-Adjusted
     P/E) when single-year earnings are deeply cyclical — the
     10-year window eliminates business-cycle noise. Cite BOTH
     Campbell & Shiller 1998 for the operational formulation, NOT
     Shiller alone.
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

### Phase 3: Macro Regime Analysis

9. **Data**: Use official primary sources (Fed, BOJ, ECB, central
   bank reports, national statistics offices). Financial media
   citing central bank releases are secondary; cite the primary
   release.
10. **Indicators**: CPI, PMI, yield curve, employment, leading
    indicators. Always note the data date.
11. **Identify the regime — 2-layer read**. Deep-mode macro regime
    analysis produces TWO complementary layers, not one:

    **Layer A — Investment Clock regime (tactical 1-3 year call)**
    per `standards/investment-analysis-canon.md` §The Merrill Lynch
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
    Corrections §Investment Clock 4-phase naming).

    **Layer B — Dalio debt-cycle phase (structural 5-8 / 50-75 year
    risk overlay)** per `standards/investment-analysis-canon.md`
    §Dalio's Debt Cycle Framework (Dalio 2018 *Principles for
    Navigating Big Debt Crises*). Diagnose which of the 6 canonical
    phases the current state maps to, for BOTH the short-term
    (5-8 yr credit cycle) and long-term (50-75 yr leverage cycle)
    horizons:
    1. **Early part of the cycle** — healthy debt growth
    2. **Bubble** — credit decoupling from fundamentals
    3. **Top** — central banks tighten OR debt service breaks
    4. **Depression** — bubble bursts, credit contracts, zero-bound
    5. **Beautiful deleveraging** — coordinated austerity + debt
       restructuring + money printing while growth stays positive
    6. **Pushing on a string / normalization** — monetary policy
       loses marginal efficacy; cycle resets toward Phase 1

    Dalio's framework is **diagnostic, NOT prescriptive**: it
    identifies the phase but does NOT produce buy/sell signals.
    Layer A (Investment Clock) produces the asset-class call;
    Layer B (Dalio) is the **structural risk overlay**.

    Cite BOTH Dalio 2018 for the framework itself AND, where
    relevant, Koo 2008 *The Holy Grail of Macroeconomics* for the
    Japanese balance-sheet-recession deep-dive on the Depression
    → Beautiful Deleveraging phases.

12. **Implications — tactical call + structural overlay**. Map the
    identified Investment Clock regime to asset-class preferences
    using the Greetham 2004 mapping — this is the **tactical call**.
    Then overlay the Dalio phase as **structural risk context**:
    if the IC says "Recovery → Stocks lead" but Dalio says "Bubble
    phase of the short-term debt cycle", the tactical call remains
    "stocks lead", but the spec must flag that the stock leadership
    is accompanied by credit-overstretch risk and downstream
    size-down / hedging / shorter-horizon disciplines apply.
    State confidence (高/中/低) for both layers separately per
    `standards/confidence-and-claim-language.md`.

### Phase 4: Output

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
- Never present Dalio's debt-cycle phases as asset-allocation
  prescription — the framework is diagnostic (phase identification
  only). Asset-class calls come from the Investment Clock. Dalio's
  6 phases (Early / Bubble / Top / Depression / Beautiful
  deleveraging / Pushing on a string) must be named verbatim when
  cited; do NOT collapse to 4 or 5 phases or substitute
  business-cycle vocabulary
- When citing CAPE, cite BOTH Campbell & Shiller 1998 authors and
  name the 10-year real-earnings window. Do NOT credit CAPE to
  Shiller alone or cite Shiller 2000 *Irrational Exuberance* as
  the operational canonical
- Do NOT cite "Damodaran's macro framework" or "Damodaran regime
  model" — no such framework exists. Damodaran is bottom-up
  valuation only. For regime models, cite Greetham & Hartnett 2004
  (Investment Clock) or Dalio 2018 (debt cycle)
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
