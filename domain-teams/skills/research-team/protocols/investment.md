# Investment Analysis Protocol

Structured investment research organized by **analysis scale**
(L1 macro → L2 sector → L3 security → portfolio meta-layer),
matching professional top-down investment process. For market
structure without investment recommendation use
`market-analysis.md`; for competitor deep-dives use
`competitive-analysis.md`.

## Primary Sources

- `standards/investment-macro-regime.md` — **L1 Macro**: Greetham &
  Hartnett 2004 Merrill Lynch Investment Clock (2×2 growth ×
  inflation 4-regime matrix) + Dalio 2018 two-horizon debt cycle
  (6 phases × {short 5-8yr, long 50-75yr}) + Koo 2008 JP
  balance-sheet recession parallel + McCullough 2024 Hedgeye GIP
  4-quadrant refinement (2-axis + derived policy overlay, NOT
  3-axis) + Mosler 1996 / Wray 2012 / Kelton 2020 MMT background
  theory (with mainstream critique) + Kumar & Persaud 2002 /
  Illing & Aaron 2005 RAI contrarian positioning signal
- `standards/investment-sector-industry.md` — **L2 Sector**:
  Fama & French 1993 3-factor + Fama & French 2015 5-factor +
  Carhart 1997 4-factor disambiguation + Asness 2011 / Kubota &
  Takehara 2018 JP exception + sector rotation by IC/Dalio
  regime mapping + factor × regime dependency tables + cross-ref
  to `strategic-frameworks.md` for stand-alone sector diagnosis
  (Porter / Value Chain / Blue Ocean / BMC)
- `standards/investment-security-valuation.md` — **L3 Security**:
  Damodaran 2012 three-framework valuation taxonomy (DCF +
  Relative + Contingent-claim) + Graham & Dodd 1934 margin of
  safety + Mr. Market price-independent verdict discipline +
  Campbell & Shiller 1998 CAPE cycle-smoothing (cross-layer: L3
  P/E variant + L1 market-valuation sanity check)
- `standards/investment-portfolio-construction.md` — **Portfolio
  meta-layer**: Taleb 2012 Antifragile Ch 11 Barbell Strategy
  (extreme-extreme allocation, NOT moderate middle) + Geman-
  Geman-Taleb 2015 mathematical anchor + Dalio 2015 Bridgewater
  Risk Parity (risk-contribution-balanced, NOT 60/40) +
  allocation philosophy comparison table
- `standards/source-quality-and-evidence.md` — filings and central
  bank releases as primary; analyst reports and financial media
  as secondary
- `standards/confidence-and-claim-language.md` — Fact / Analysis /
  Speculation taxonomy and 高/中/低 confidence mapping for
  forward-looking claims

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

**Layer loading by mode** (v4.11.0 context-cost optimization):

| Mode | L1 Macro | L2 Sector | L3 Security | Portfolio |
|---|---|---|---|---|
| **quick** | load if relevant | skip (cross-ref only) | load if relevant | skip (cross-ref only) |
| **deep** | always load if regime matters | load on demand | always load if security matters | load on demand |

Worker only loads the standards files for the layers actually
needed by the question. A single-security valuation question
loads only `investment-security-valuation.md`; a regime call loads
only `investment-macro-regime.md`; a top-down thesis loads all 4
progressively as the analysis moves from L1 → L2 → L3 → Portfolio.

In **quick mode**, this protocol runs in a stripped-down form per the
mode-specific exit rule defined in `standards/confidence-and-claim-language.md`
§Cost-Aware Early-Exit Rule:
- Skip cross-language (EN+JP) parallel search unless natural
- ≥1 primary source per key claim is sufficient (vs ≥2 for deep)
- Exit immediately when all key claims reach Medium confidence
  (medium evidence × medium agreement on the IPCC 3×3 grid)
- Skip MUST `source-citation-checklist` gate (SELF check applies)
- Quick-mode layer reduction: load only 1-2 standards files (the
  layer(s) directly relevant to the question), skip cross-layer
  bridge analysis
- Quick-mode framework reduction: within the loaded layer(s), use
  the single most appropriate framework only — L3: pick DCF OR
  relative OR contingent-claim per the asset type, not all three;
  L1: call IC regime in one line without full 2×2 matrix, skip
  Dalio debt-cycle deep dive (one-line phase call only), skip
  Hedgeye GIP / MMT / RAI unless directly probed; L2: skip sector
  rotation deep dive; Portfolio: skip entirely unless user asks
- Skip CAPE cycle-smoothing — use rolling P/E only; skip Graham
  margin-of-safety detailed calculation (narrative bracket only)

In **deep mode**, run the protocol per the existing grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full Damodaran 3-framework L3 valuation (DCF +
  relative + contingent-claim where applicable) with CAPE
  cycle-smoothing against Campbell & Shiller 1998 historical bands
  for cyclical or market-level equity calls + Merrill Lynch
  Investment Clock 2×2 regime identification (Reflation / Recovery
  / Overheat / Stagflation — NEVER business-cycle terminology) +
  Dalio 2018 full 6-phase debt-cycle identification for BOTH the
  short-term (5-8 yr) and long-term (50-75 yr) cycles as a
  structural risk overlay + Hedgeye GIP 4-quadrant refinement
  where relevant + MMT background theory for sovereign-currency
  regime questions (with mainstream critique) + RAI contrarian
  positioning signal + L2 sector rotation mapping + factor ×
  regime dependency analysis + Portfolio construction layer
  (Barbell + Risk Parity philosophy comparison) + Graham
  margin-of-safety detailed calculation + Mr. Market
  price-independent verdict discipline

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
2. **Identify the analytical scale(s)**: Classify the question
   into one or more of the 4 layers (L1 Macro / L2 Sector / L3
   Security / Portfolio). This determines which standards files
   load in subsequent phases:
   - "What regime are we in?" → L1 only
   - "Valuate AAPL" → L3 only
   - "Which sectors lead in Overheat?" → L2 + L1 cross-ref
   - "Top-down thesis for current regime" → L1 → L2 → L3 → Portfolio
3. **Identify the right analytical lens within each scale**:
   - L1: IC + Dalio minimum; add Hedgeye / MMT / RAI on demand
   - L2: Fama-French + sector rotation mapping; cross-ref Porter
     Five Forces in `strategic-frameworks.md` for stand-alone
     sector diagnosis
   - L3: Pick the appropriate Damodaran framework per
     `standards/investment-security-valuation.md` §Choosing Among
     the Three — the choice is a function of the asset and the
     question, not a preference
   - Portfolio: Barbell vs Risk Parity vs traditional 60/40
     philosophy call

### Phase 2: L3 Security Analysis

**Loads**: `standards/investment-security-valuation.md` only

**Skip if**: question is pure L1 macro regime or pure L2 sector
rotation.

**Mode discipline**: in quick mode, cap collection per Phase 0
budget; in deep mode, follow existing collection workflow.

4. **Business Model**: Revenue sources, competitive moats, TAM,
   unit economics. Cite primary filings (10-K, 有価証券報告書) not
   analyst summaries per `standards/source-quality-and-evidence.md`.
5. **Financials**: Revenue growth, margins, FCF, balance sheet
   strength. Use official financial statements as the primary
   source. Note data date explicitly.
6. **Valuation**: Apply the three-framework taxonomy per
   `standards/investment-security-valuation.md` §Damodaran's
   Valuation Taxonomy:
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
     `standards/investment-security-valuation.md` §Cyclically-Adjusted
     P/E) when single-year earnings are deeply cyclical — the
     10-year window eliminates business-cycle noise. Cite BOTH
     Campbell & Shiller 1998 for the operational formulation, NOT
     Shiller alone.
   - **Contingent-claim / real options** for assets dominated by
     optionality (undeveloped reserves, early-stage patents, equity
     in distressed firms).
7. **Margin of Safety check**: Per
   `standards/investment-security-valuation.md` §Graham & Dodd,
   require a substantial gap between price and intrinsic value
   estimate (canonical 30-50% discount, or ~2/3 of net current
   asset value for deep-value candidates). The margin of safety
   is the antidote to false precision in the valuation model —
   not an optional comfort.
8. **Catalysts**: Upcoming events, product launches, regulatory
   changes with explicit timeframes.
9. **Risks**: Key risk factors with probability and impact
   assessment. Counter-arguments are mandatory.

### Phase 3: L1 Macro Regime Analysis

**Loads**: `standards/investment-macro-regime.md` only

**Skip if**: question is pure L3 single-security valuation with
no regime sensitivity.

10. **Data**: Use official primary sources (Fed, BOJ, ECB, central
    bank reports, national statistics offices). Financial media
    citing central bank releases are secondary; cite the primary
    release.
11. **Indicators**: CPI, PMI, yield curve, employment, leading
    indicators. Always note the data date.
12. **Identify the regime — 2-layer read (deep mode)**. Deep-mode
    macro regime analysis produces TWO complementary layers, not
    one:

    **Layer A — Investment Clock regime (tactical 1-3 year call)**
    per `standards/investment-macro-regime.md` §The Merrill Lynch
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
    conflating them is a fatal attribution error.

    **Layer B — Dalio debt-cycle phase (structural 5-8 / 50-75 year
    risk overlay)** per `standards/investment-macro-regime.md`
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

13. **Optional refinements (deep mode, on demand)**:
    - **Hedgeye GIP 4-quadrant** refinement per
      `standards/investment-macro-regime.md` §Hedgeye GIP — use
      when a more granular quadrant read is needed beyond the IC
      2×2. Hedgeye GIP is a **2-axis + derived policy overlay**
      refinement descended from Dalio's 1996 4-box, NOT an
      independent 3-axis framework and NOT a refinement of
      Greetham IC.
    - **MMT background theory** per
      `standards/investment-macro-regime.md` §Modern Monetary
      Theory — apply only when the question touches sovereign-
      currency issuance, fiscal-monetary coordination, or the
      debt-vs-inflation constraint. Present neutrally with
      mainstream critique (Krugman / Summers / Rogoff). MMT is
      NOT "just print money".
    - **RAI contrarian positioning signal** per
      `standards/investment-macro-regime.md` §Risk Appetite Index
      — use as positioning / sentiment indicator, not as primary
      regime call. Cite Kumar & Persaud 2002 peer-reviewed origin;
      disambiguate variants (Credit Suisse vs Goldman Sachs
      Risk-Aversion Index vs Citi Panic/Euphoria vs State Street
      ICI vs BofA Bull & Bear — NOT "Global Investor Confidence
      Index").

14. **Implications — tactical call + structural overlay**. Map the
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

### Phase 4: L2 Sector/Industry Analysis (deep mode optional)

**Loads**: `standards/investment-sector-industry.md` + cross-ref
`standards/strategic-frameworks.md` for stand-alone sector
diagnosis

**Skip if**: quick mode, OR question is pure L1 / L3 without
sector rotation component.

15. **Sector rotation by regime**: Map the L1 regime (from Phase 3)
    to which sectors historically lead per
    `standards/investment-sector-industry.md` §Sector Rotation by
    L1 Regime:
    - **Reflation** → long-duration bonds / utilities / REITs
    - **Recovery** → consumer discretionary / technology
    - **Overheat** → commodities / energy / industrials
    - **Stagflation** → cash / short-duration + defensive sectors
    Document the bridge between the L1 regime call (Phase 3) and
    the L2 sector tilt explicitly.

16. **Factor × regime dependency**: Document how Value / Momentum
    / Quality / Low-Vol / Size factors correlate with the
    identified IC regime and Dalio phase per
    `standards/investment-sector-industry.md` §Factor × Regime
    Mapping. Value typically underperforms during Recovery
    (growth leadership) and outperforms during Reflation / early
    rebounds. Quality outperforms in Stagflation. Note that
    factor regime dependency is **historical tendency, not
    deterministic** — always state confidence (高/中/低).

17. **Factor attribution discipline**: When citing factor results,
    specify which model — Fama-French 3-factor (1993) OR 5-factor
    (2015) OR Carhart 4-factor (1997). FF5 **explicitly excludes
    momentum**; Carhart is the canonical source for momentum-as-
    factor. Quality = AQR QMJ (Asness-Frazzini-Pedersen 2019), NOT
    FF RMW. Low-Vol / BAB = Frazzini-Pedersen 2014, NOT FF.
    Fama-French ≠ APT (Ross 1976). **JP exception is load-bearing**:
    FF5 fails in Japan per Kubota-Takehara 2018, Fama-French 2012
    documents no-momentum in Japan, Asness 2011 reinterprets
    momentum-as-value-hedge.

18. **Stand-alone sector diagnosis (cross-ref)**: For deep
    sector/industry analysis beyond rotation (competitive
    dynamics, value chain, market structure), cross-reference
    `standards/strategic-frameworks.md` §Porter Five Forces /
    §Value Chain / §Blue Ocean / §BMC. These are Tier 1 shared
    frameworks also used by market-analysis.md and
    competitive-analysis.md protocols.

### Phase 5: Portfolio Construction (deep mode optional)

**Loads**: `standards/investment-portfolio-construction.md`

**Skip if**: quick mode, OR question is not about allocation
philosophy / risk budgeting / position sizing at portfolio level.

19. **Allocation philosophy call**: Classify the portfolio
    construction approach per
    `standards/investment-portfolio-construction.md`:
    - **Traditional 60/40** — capital-weighted
    - **Risk Parity** — risk-contribution-weighted (Dalio 2015
      Bridgewater All Weather; ≠ 60/40)
    - **Barbell** — extreme-extreme allocation (Taleb 2012
      *Antifragile* Ch 11; 85/15 illustrative not prescriptive;
      NOT moderate middle-of-road)
    - **Concentrated value** — Graham-style high-conviction few
      positions
    - **Indexed passive** — Bogle-style cap-weighted

20. **Integration with L1+L2+L3 calls**: Blend the L1 regime call
    (Phase 3) + L2 sector tilt (Phase 4) + L3 position-sized
    security calls (Phase 2) into a coherent portfolio. Risk
    Parity is regime-agnostic; Barbell is convexity-maximizing;
    traditional 60/40 is implicitly regime-agnostic. State
    which philosophy is being applied and why it fits the
    question.

21. **Critical attribution discipline**: Barbell primary is
    *Antifragile* 2012 Ch 11, NOT *Black Swan* 2007 Ch 13.
    Barbell is extreme-extreme, NOT moderate. Universa
    (Spitznagel) runs a 96.7% SPX + 3.3% tail hedge overlay —
    technically NOT pure Barbell. Risk Parity ≠ 60/40 —
    risk-contribution-based, not capital-contribution-based.
    Japanese バーベル戦略 typically refers to bond duration
    barbell (short + long, no middle), NOT Taleb's Barbell —
    disambiguate in JP context.

### Phase 6: Output

22. **Price-independent verdict**: Per Graham's Mr. Market
    allegory in `standards/investment-security-valuation.md`
    §Graham & Dodd, derive the intrinsic-value estimate from
    fundamentals **first**, then compare to market price — never
    the other way around. An analyst who anchors on current
    market price and reasons toward a valuation is doing reverse
    Mr. Market, a guaranteed calibration failure.
23. **Actionable recommendation**: Specific call (buy / hold / sell /
    overweight / underweight, OR regime diagnosis, OR sector tilt,
    OR portfolio construction philosophy) with position sizing
    implication, explicit confidence level (高/中/低), and
    explicit data date.

## Rules

- Cite every factual claim with source; prefer primary filings
  and central bank releases over secondary commentary
- Apply the 3-framework L3 valuation taxonomy explicitly — do not
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
  (Investment Clock) or Dalio 2018 (debt cycle) or McCullough 2024
  (Hedgeye GIP)
- Hedgeye GIP is 2-axis + derived policy overlay, descendant of
  Dalio 1996 4-box — NOT a 3-axis framework and NOT a refinement
  of Greetham IC
- MMT primary canonical sequence: Mosler 1996 (origin) → Wray 2012
  (academic) → Kelton 2020 (popular). Do NOT cite Kelton alone.
  Always include mainstream critique when citing MMT.
- RAI peer-reviewed origin is Kumar & Persaud 2002 *International
  Finance* 5(3), NOT Credit Suisse Wilmot. Disambiguate variants
  explicitly — Goldman Sachs publishes a Risk-**Aversion** Index
  (inverse semantics), NOT an RAI. There is no "BofA Global
  Investor Confidence Index" — the real product is the Bull & Bear
  Indicator by Hartnett. State Street ICI = Froot & O'Connell NBER
  WP **10157** (not 8226)
- Barbell primary canonical is Taleb 2012 *Antifragile* Ch 11,
  NOT *Black Swan* 2007 Ch 13. Barbell is extreme-extreme, NOT
  moderate. Universa ≠ pure Barbell
- Risk Parity is risk-contribution-balanced, NOT capital-weighted;
  explicitly distinguish from 60/40
- Fama-French factor model must specify FF3 (1993) or FF5 (2015);
  Carhart 4-factor (1997) is distinct. FF5 excludes momentum.
  Quality/Low-Vol are NOT FF factors
- Japan factor-model exception is load-bearing when citing factor
  results for JP equities — cite Kubota-Takehara 2018, Fama-French
  2012 JFE 105(3), Asness 2011 JPM 37(4)
- Include confidence level (高/中/低) on every forward-looking claim
- Always note the data date — stale data kills analysis
- Consult research notes (e.g., a user's personal vault) if
  available; otherwise rely on fresh primary-source research
  within this protocol

## Output Format

1. **Decision Question**: Precise, testable investment question
2. **Analytical Scale(s) Used**: Which of L1 / L2 / L3 / Portfolio
   layers applied and why
3. **Framework(s) Selected**: Which frameworks within each loaded
   layer and why
4. **L3 Business & Financial Summary** (if loaded): Key metrics
   with sources
5. **L3 Valuation** (if loaded): Intrinsic value estimate with
   margin of safety assessment
6. **L1 Macro Regime** (if loaded): Investment Clock regime +
   Dalio phase overlay with evidence from growth + inflation
   indicators; optional Hedgeye GIP / MMT / RAI refinements
7. **L2 Sector Tilt** (if loaded): Sector rotation + factor ×
   regime mapping
8. **Portfolio Construction** (if loaded): Allocation philosophy
   + risk budgeting
9. **Catalysts & Risks**: Both sides, with timeframes
10. **Recommendation**: Specific action, confidence level (高/中/低),
    data date
