# Competitive Analysis Protocol

Deep comparison of individual competitors. More granular than
market-analysis.md (which maps the overall landscape). Use this
when the user needs to understand specific competitors in depth
or identify differentiation opportunities.

## Primary Sources

- `standards/strategic-frameworks.md` — Porter Five Forces + Blue Ocean Four Actions (ERRC) + Business Model Canvas + Aaker brand equity
- `standards/source-quality-and-evidence.md` — verification discipline for claims about competitors (filings, product docs, press releases as primary; analyst commentary as secondary)

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
- Quick-mode reduction: skip detailed Strategy Canvas construction
  (narrative positioning only); profile 3 competitors (vs 5-10);
  skip Aaker brand-equity dimension analysis; skip Four Actions
  (ERRC) framework application — surface uncontested space
  qualitatively only

In **deep mode**, run the protocol per the existing v4.9.0 grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full Strategy Canvas with plotted axes + 5-10
  competitor profiles + Porter Five Forces overlay + Business
  Model Canvas per competitor + Aaker brand equity dimensions

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

### Phase 0.5: Concept-first onboarding (MANDATORY)

Before competitor identification, draft the artifact's opening
**Core Concepts** section. This is the reader onboarding
required by `rubrics/research-quality-gate.md` §Reader Onboarding
for the competitive-analysis protocol.

For each load-bearing term the analysis will use to compare
competitors (the category itself, the comparison dimensions, any
business-model concept that recurs), write one entry containing:

1. **One-sentence definition** — what this thing is, in the
   simplest accurate phrasing.
2. **Why it exists** — what user need or market dynamic it serves.
3. **Distinction from neighboring concepts** — if competitors
   span overlapping but distinct categories (e.g., "vertical SaaS"
   vs "horizontal SaaS", "freemium" vs "free-trial", "marketplace"
   vs "aggregator"), make the boundary explicit.

The Core Concepts section is **exempt from Fact / Analysis /
Speculation tagging** per `standards/citation-standards.md`
§Onboarding-Layer Exemption.

User override: if the user states they are familiar with the
market category and want to skip concept definitions, omit and
record the override in the deep-mode Self-Critique block as
`Concept-first onboarding skipped per user override.`

### Phase 1: Scope

1. **Define competitors**: Identify direct competitors (same
   product/market), indirect competitors (alternative solutions),
   and potential entrants. Limit to 3-5 for depth over breadth.
2. **Define comparison dimensions**: Agree on what to compare.
   Common dimensions: product/features, pricing/business model,
   distribution/go-to-market, technology, brand/positioning,
   team/funding. Let user prioritize.

### Phase 2: Competitor Profiling

**Mode discipline**: in quick mode, cap collection per Phase 0
budget; in deep mode, follow existing collection workflow.

3. **Per-competitor profile**: For each competitor, document:
   - Core strengths and weaknesses
   - Strategy and positioning
   - Recent moves (launches, pivots, funding, acquisitions)
   - Key metrics (if public: revenue, users, growth rate)
4. **Product / service comparison matrix**: Feature-by-feature
   comparison table across all competitors. Use consistent
   scoring (has / partial / lacks) rather than subjective ratings.
5. **Pricing & business model comparison**: How does each
   competitor monetize? Pricing tiers, free tier limits,
   enterprise vs self-serve, usage-based vs seat-based.

### Phase 3: Differentiation Analysis

6. **Differentiation map**: Plot competitors on 2 axes that
   matter most to the target segment using the Strategy Canvas
   technique (Kim & Mauborgne 2015) per
   `standards/strategic-frameworks.md` §Blue Ocean Strategy.
   Identify where the density is (red ocean) and where gaps exist.
7. **Uncontested space identification**: Apply the Four Actions
   Framework (Eliminate / Reduce / Raise / Create) per
   `standards/strategic-frameworks.md` §Blue Ocean Strategy to
   surface factors that could open new market space.
8. **Competitive response prediction**: If we enter or change
   position, how will each competitor likely react? What are
   their constraints and incentives?

### Phase 4: Synthesis

9. **Competitive advantage assessment**: For each competitor,
   is their advantage sustainable (structural moat, network
   effects, switching costs) or temporary (first-mover, funding)?
10. **Actionable differentiation strategy**: Specific positioning
    recommendations. Not "differentiate on quality" but
    "focus on [specific dimension] where competitors X and Y
    are weakest, targeting [specific segment]."

## Rules

- Limit competitor set to 3-5 for meaningful depth
- Use public, verifiable data — do not fabricate metrics
- Feature comparisons must use consistent criteria across
  all competitors (no cherry-picking dimensions)
- Search in EN and JP — many competitors have different
  positioning in different markets
- Separate observation (what competitors DO) from interpretation
  (what it MEANS)
- Cite sources for all factual claims about competitors

## Output Format

1. **Core Concepts** (concept-first onboarding per Phase 0.5): Per-term definition + why it exists + distinction from neighboring concepts. Untagged per §Onboarding-Layer Exemption.
2. **Competitor Set**: Who was analyzed and why
3. **Comparison Matrix**: Feature/pricing/positioning table
4. **Differentiation Map**: Visual positioning with axes defined
5. **Per-Competitor Profiles**: Strengths, weaknesses, strategy
6. **Uncontested Space**: Opportunities identified via Blue Ocean
7. **Recommended Strategy**: Specific, actionable differentiation plan
