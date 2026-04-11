# Market & Industry Analysis Protocol

Structured market investigation focused on market structure,
growth dynamics, and strategic landscape. For investment decisions
use `investment.md`; for individual competitor deep-dives use
`competitive-analysis.md`.

## Primary Sources

- `standards/strategic-frameworks.md` — Porter Five Forces + Porter value chain (industry structure + rent capture)
- `standards/source-quality-and-evidence.md` — primary/secondary source taxonomy for market data (filings, analyst reports, trade publications)
- `standards/confidence-and-claim-language.md` — Fact / Analysis / Speculation taxonomy for separating actual data from projections

## Protocol

### Phase 0: Market Definition

1. **Define market boundary**: Geography, segment, value chain
   position. Be specific — "AI market" is too broad;
   "enterprise AI code assistant tools, global" is actionable.
2. **Identify key questions**: What does the user need to know?
   Market size? Growth rate? Key players? Regulatory trends?
   Prioritize questions before researching.

### Phase 1: Market Structure

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

### Phase 2: Landscape Mapping

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

### Phase 3: Synthesis

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
