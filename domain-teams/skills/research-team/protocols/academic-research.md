# Academic Research Protocol

Systematic literature review and theoretical framework construction.
For deep academic investigation — tracing theory evolution, mapping
schools of thought, identifying research gaps. Use this for tasks
like the domain-design Japanese design theory research.

## Primary Sources

- `standards/systematic-review-methodology.md` — Cochrane 8-step workflow + PICO/PICOC question framing + PRISMA 2020 27-item checklist + PRISMA flow diagram + Booth 5-element argument model
- `standards/source-quality-and-evidence.md` — primary/secondary/tertiary source taxonomy + Kovach verification discipline
- `standards/information-infrastructure.md` — NDL リサーチ・ナビ 3 層構造 + CiNii Research 系譜 + 倉田 2007 学術情報流通 + JP database decision rule

## Phase 0: Mode Detection and Budget Setup

**MUST run before Phase 1.** Read the `mode:` field from the worker
launch `### Input` section. If absent, default to `quick`.

| Mode | Default budget | Source cap | Search cap | Token cap |
|---|---|---|---|---|
| **quick** (default) | single-pass triangulation | 5 sources | 5 web searches | ~15k tokens |
| **deep** (opt-in) | full audit trail | 15 sources | 20 web searches | ~150k tokens |

User-overridable via `### Input` fields: `max_sources`, `max_searches`,
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
- Quick-mode reduction: skip JP database parallel search (CiNii
  Research, J-Stage, NDL リサーチ・ナビ); skip systematic-review
  methodology rigor — the Cochrane 8-step workflow is abbreviated
  to 3 steps (question → search → screen); cite-ratio relaxed to
  ≥1 primary source per claim; skip PRISMA 27-item completeness
  check

In **deep mode**, run the protocol per the existing v4.9.0 grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full Cochrane 8-step workflow + PRISMA 2020
  27-item checklist + bilingual JP database coverage (NDL + CiNii
  + J-Stage per `standards/information-infrastructure.md`) + Booth
  5-element argument synthesis

**Budget enforcement**: track source count, search count, token
estimate. On overrun, finish current source verification (atomic),
then return BLOCKED with summary: `"budget overrun: collected N
sources, M searches, ~Tk tokens. Partial result attached. Reply
'expand budget to X' or 'accept partial'."`

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific exit thresholds and the
per-claim (not per-deliverable) policy.

## Protocol

### Phase 1: Research Design

1. **Define research question & scope**: State the theoretical
   question precisely. What phenomenon are we trying to understand?
   What is the disciplinary scope? Frame with PICO or PICOC per
   `standards/systematic-review-methodology.md` §PICO and PICOC
   Question Framing when the question suits intervention/comparison
   structure.
2. **Identify academic databases**: Select databases by discipline.
   For Japanese-language academic sources, consult
   `standards/information-infrastructure.md` §NDL リサーチ・ナビ
   and §CiNii Research 系譜 for the canonical JP database list
   (NDL, CiNii Research, J-Stage) with decision rules on which
   to use when. For Anglo sources:
   - General: Google Scholar, Semantic Scholar
   - Domain-specific: SSRN (social science), arXiv (CS/physics),
     PubMed (bio/med), JSTOR (humanities), IEEE Xplore (engineering)
3. **Set inclusion / exclusion criteria**: Define what qualifies
   as relevant literature — time range, language, methodology,
   publication type (peer-reviewed, conference, book chapter).
   Treat inclusion/exclusion as a formal Cochrane Step 2 decision
   per `standards/systematic-review-methodology.md` §The Cochrane
   8-Step Workflow.

### Phase 2: Literature Collection

**Mode discipline**: in quick mode, cap collection per Phase 0
budget; in deep mode, follow existing collection workflow.

4. **Systematic search**: Search in English AND Japanese academic
   sources. Use domain-specific terminology in both languages.
   Follow the Cochrane 8-step workflow (Step 3 "Search") per
   `standards/systematic-review-methodology.md`.
   - EN: "{theory} systematic review", "{concept} framework"
   - JP: 「〇〇 理論」「〇〇 研究動向」「〇〇 レビュー」
5. **Citation chain tracing**: Start from seminal works, trace
   forward (who cited them) and backward (what they cited).
   Identify the intellectual lineage of the field.
6. **Key author / research group identification**: Who are the
   foundational and active researchers? What institutions are
   producing the most relevant work? Record the screening funnel
   (identification → screening → eligibility → inclusion) per
   `standards/systematic-review-methodology.md` §PRISMA 2020
   Flow Diagram when the output is a formal review.

### Phase 3: Analysis & Synthesis

7. **Theoretical framework mapping**: Map schools of thought,
   competing theories, and how the field has evolved over time.
   Identify where theories converge and where they conflict.
8. **Methodology comparison**: How do different studies approach
   the same question? Qualitative vs quantitative? What
   assumptions underlie each approach?
9. **Gap identification**: What hasn't been studied? Where do
   theories fail to explain observed phenomena? What
   contradictions remain unresolved?

### Phase 4: Output

10. **Literature synthesis**: Integrated narrative connecting
    the key works, not just a list of summaries. Show how
    ideas build on each other. Structure the synthesis per
    Booth 5-element argument model (claim + reasons + evidence +
    warrants + acknowledgments) from
    `standards/systematic-review-methodology.md` §Booth's
    5-Element Argument Model.
11. **Research gaps & future directions**: Explicitly state
    what is unknown or contested, and what research would
    resolve it.
12. **Practical implications**: Bridge theory to application.
    How do these academic findings inform real-world decisions?

## Rules

- Prefer peer-reviewed sources over popular media
- Always search in both EN and JP academic databases —
  Japanese scholarship often contains unique perspectives
  absent from English literature
- Trace citation chains — do not rely solely on keyword search
- Distinguish foundational works (must-cite) from incremental
  contributions
- When theories conflict, present both with evidence rather
  than choosing sides without justification
- Note the recency and citation count of key works for context
- Preserve original terminology in both languages — do not
  force-translate academic concepts that lose meaning

## Output Format

1. **Research Question**: Precise theoretical question investigated
2. **Literature Map**: Key works organized by school of thought
   or chronological evolution
3. **Theoretical Framework**: Synthesized model showing how
   theories relate, converge, and conflict
4. **Methodology Summary**: How the field studies this question
5. **Research Gaps**: What remains unknown or contested
6. **Practical Implications**: Theory → application bridge
7. **References**: Full citation list (APA format preferred)
