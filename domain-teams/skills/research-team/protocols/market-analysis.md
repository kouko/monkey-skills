# Market & Industry Analysis Protocol

Structured market investigation focused on market structure,
growth dynamics, and strategic landscape. For investment decisions
use `investment.md`; for individual competitor deep-dives use
`competitive-analysis.md`.

## Primary Sources

- `standards/strategic-frameworks.md` — Porter Five Forces + Porter value chain (industry structure + rent capture)
- `standards/source-quality-and-evidence.md` — primary/secondary source taxonomy for market data (filings, analyst reports, trade publications)
- `standards/confidence-and-claim-language.md` — Fact / Analysis / Speculation taxonomy for separating actual data from projections

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
- Quick-mode reduction: skip full Porter Five Forces analysis —
  focus on the top 3 forces that most shape the observed dynamics;
  skip detailed competitor profiling (top 5 players only, headline
  positioning only); skip JP-specific market data unless the
  geography is explicitly Japan

In **deep mode**, run the protocol per the existing v4.9.0 grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full Porter Five Forces + Porter value chain
  analysis + Blue Ocean framing + Business Model Canvas overlay
  where relevant + global AND JP market data coverage

**Budget enforcement**: track source count, search count, token
estimate. On overrun, finish current source verification (atomic),
then return BLOCKED with summary: `"budget overrun: collected N
sources, M searches, ~Tk tokens. Partial result attached. Reply
'expand budget to X' or 'accept partial'."`

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific exit thresholds and the
per-claim (not per-deliverable) policy.

**Deep-mode hooks**: load per the trigger map in
`protocols/research.md` §Deep-Mode Hooks (multi-perspective end
of Phase 0; parallel-fanout start of Phase 1; self-critique end
of Phase 4 / Synthesis). Quick mode skips.

## Protocol

### Phase 1: Market Definition

1. **Define market boundary**: Geography, segment, value chain
   position. Be specific — "AI market" is too broad;
   "enterprise AI code assistant tools, global" is actionable.
2. **Identify key questions**: What does the user need to know?
   Market size? Growth rate? Key players? Regulatory trends?
   Prioritize questions before researching.

### Phase 2: Market Structure

**Mode discipline**: in quick mode, cap collection per Phase 0
budget; in deep mode, follow existing collection workflow.

3. **Market sizing**: Estimate TAM / SAM / SOM with explicit
   data sources. Distinguish bottom-up from top-down estimates.
   Tag actual historical data as **Fact** and analyst projections
   as **Analysis** (or **Speculation** for multi-year forward
   forecasts) per `standards/confidence-and-claim-language.md`
   §Fact / Analysis / Speculation Taxonomy. Never present a
   projection as if it were realized data.
4. **Growth drivers & headwinds**: What accelerates and what
   constrains market growth? Categorize as technology, regulatory,
   economic, or behavioral. Map against Porter Five Forces per
   `standards/strategic-frameworks.md` §Porter's Five Forces to
   identify which forces actually shape the observed dynamics.
5. **Regulatory environment**: Current regulations, pending
   legislation, and compliance requirements that shape the market.

### Phase 3: Landscape Mapping

6. **Key player identification**: Major players with market
   share estimates (if available). Include incumbents, challengers,
   and notable new entrants.
7. **Value chain analysis**: Where is value created and captured?
   Identify which positions in the chain have the most leverage
   per `standards/strategic-frameworks.md` §Porter's Five Forces
   (buyer / supplier bargaining power dimensions).
8. **Trend analysis**: Technology trends, regulatory shifts,
   and consumer behavior changes that will reshape the market
   in the next 1-3 years.

### Phase 4: Synthesis

9. **Opportunity / threat matrix**: Organize findings into
   opportunities (where to play) and threats (what to watch).
10. **Strategic implications**: Specific, actionable insights
    for decision-making. Not "the market is growing" but
    "segment X is growing at Y% driven by Z — consider entry
    via [specific approach]."

## Rules

- Always cite data sources for market size and growth figures
- Distinguish actual data from analyst projections
- Search in EN and JP for both global and Japan-specific data
- Flag data older than 12 months for market sizing
- TAM/SAM/SOM must include methodology (top-down vs bottom-up)
- Do not conflate market analysis with investment recommendation

## Output Format

1. **Market Definition**: Boundary, segments, scope
2. **Market Size & Growth**: TAM/SAM/SOM with sources and methodology
3. **Competitive Landscape**: Key players, positioning, market share
4. **Trends & Dynamics**: Drivers, headwinds, regulatory environment
5. **Opportunity/Threat Matrix**: Structured assessment
6. **Strategic Implications**: Actionable recommendations
