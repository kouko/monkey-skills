# General Research Protocol

Universal research methodology for any investigation task.
Fallback when no specialized protocol (market, competitive,
academic, investment, stack) matches the task.

## Primary Sources

- `standards/systematic-review-methodology.md` — Cochrane 8-step + PRISMA 2020 + Booth 5-element argument model
- `standards/confidence-and-claim-language.md` — IPCC/Kent calibrated language + Fact/Analysis/Speculation taxonomy + 高/中/低 mapping
- `standards/source-quality-and-evidence.md` — primary/secondary/tertiary taxonomy + Kovach verification discipline

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
- Quick-mode reduction: skip Phase 3 deep synthesis; output is a
  structured summary only (Key Findings + confidence tags, no full
  Booth 5-element expansion)

In **deep mode**, run the protocol per the existing v4.9.0 grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full Phase 1-4 cycle with cross-verification,
  Booth 5-element synthesis, and counter-argument treatment per
  the existing protocol body

**Budget enforcement**: track source count, search count, token
estimate. On overrun, finish current source verification (atomic),
then return BLOCKED with summary: `"budget overrun: collected N
sources, M searches, ~Tk tokens. Partial result attached. Reply
'expand budget to X' or 'accept partial'."`

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific exit thresholds and the
per-claim (not per-deliverable) policy.

## Deep-Mode Hooks

Deep mode lazy-loads three pre-writing / synthesis hooks. Quick
mode skips them to preserve the ~15k token budget.

| Hook | File | Trigger phase |
|---|---|---|
| Multi-perspective seeding | `protocols/hooks/multi-perspective.md` | end of Phase 0 (before Phase 1 Scoping) |
| Parallel sub-worker fan-out | `protocols/hooks/parallel-fanout.md` | start of Phase 1 (after sub-questions defined) |
| Self-critique block | `protocols/hooks/self-critique.md` | end of Phase 3 (before artifact handoff) |

Worker reads the relevant hook file at each trigger phase and
follows its rule. Specialized protocols (academic / market /
competitive / stack) inherit the same trigger map.

## Protocol

### Phase 1: Scoping

1. **Define research question**: State the question precisely.
   A vague question produces vague research. Rewrite until
   someone could independently verify the answer.
2. **Set scope boundary**: Explicitly state what is IN scope
   and what is OUT of scope. Prevent scope creep before it starts.
3. **Plan source strategy**: Identify the best source types
   for this question. Primary sources (official docs, filings,
   reports, peer-reviewed papers) always outrank secondary.

### Phase 2: Collection

**Mode discipline**: in quick mode, cap collection per Phase 0
budget; in deep mode, follow existing collection workflow.

4. **Multi-source search**: Search in English AND Japanese
   in parallel.
   - EN: natural phrasing ("topic best practices")
   - JP: 「〇〇 使い方」「〇〇 ベストプラクティス」
   - Add user's language for regional topics if needed
5. **Cross-reference**: Verify every key claim across 2+
   independent sources. A single source is a lead, not a fact.
6. **Recency check**: Flag sources older than 6 months for
   fast-moving topics. Always note the data date.

### Phase 3: Synthesis

7. **Categorize claims**: Tag every assertion as Fact / Analysis /
   Speculation per `standards/confidence-and-claim-language.md`
   §Fact / Analysis / Speculation Taxonomy. Never present opinion
   as fact.
8. **Tag confidence**: Mark key conclusions with confidence level
   (高/中/低) per `standards/confidence-and-claim-language.md`
   §Mapping Research-Team 高/中/低 to IPCC 5-Tier. No unqualified
   certainty on contested claims.
9. **Counter-arguments**: Address opposing viewpoints and risks
   explicitly. Ignoring counter-evidence is a fatal flaw.

### Phase 4: Output

10. **Actionable recommendations**: End with specific, prioritized
    next steps. Structure findings per Booth 5-element argument
    model (claim + reasons + evidence + warrants + acknowledgments)
    from `standards/systematic-review-methodology.md` §Booth's
    5-Element Argument Model. Include confidence level on each
    recommendation. Vague advice ("consider improving X") is
    not acceptable.

## Rules

- Always search in both EN and JP — missing one language
  halves your source coverage
- Primary sources first; secondary sources for context only
- Cite every factual claim with source
- Distinguish facts from analysis from speculation — never
  present opinion as fact
- Flag stale data explicitly ("as of YYYY-MM, ...")
- If sources contradict each other, present both positions
  with evidence rather than silently picking one

## Output Format

1. **Research Question**: Precise statement of what was investigated
2. **Key Findings**: Major discoveries with citations and
   confidence levels (高/中/低)
3. **Analysis**: Reasoned interpretation of findings
4. **Counter-Arguments**: Opposing evidence or alternative
   interpretations
5. **Recommendations**: Specific, prioritized, actionable next steps
