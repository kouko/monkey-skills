# Changelog

All notable changes to the `domain-teams` plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.10.0] — 2026-04-11

planning-team primary-source grounding refactor — the **final domain
team to complete grounding**. planning-team joins qa-team v4.2.0
(ISTQB / VSTeP), docs-team v4.3.0 (Diátaxis / Google Style / JTAP),
devops-team v4.4.0 (Google SRE / DORA / 12-Factor / Continuous
Delivery), code-team v4.6.0 (GoF / Fowler / NIST), design-team v4.8.0
(Norman / Nielsen / WCAG), and research-team v4.9.0 (Booth / Cochrane /
IPCC) in having every load-bearing framework claim anchored to a
named primary source. **All 7 domain teams are now grounded**.

MINOR bump per `skill-team/standards/commit-convention.md` CHK-CMT-005
because **3 new standards files** are added that worker and evaluator
agents will Read at runtime: `discovery-frameworks.md`,
`goals-and-metrics.md`, `spec-completeness-standards.md`. The 4th
standards file (`planning-frameworks.md`) is a rewrite of a
pre-existing file, not a new addition.

The grounding pass surfaced **24 Critical Attribution Corrections**
in the research note, of which 10 are load-bearing enough to appear
inline in the standards files. The corrections are documented in
`standards/planning-frameworks.md` §Critical Attribution Corrections,
`standards/discovery-frameworks.md` §Critical Attribution Corrections,
`standards/goals-and-metrics.md` §Critical Attribution Corrections,
and `standards/spec-completeness-standards.md` §Critical Attribution
Corrections.

### Added

- **`standards/discovery-frameworks.md`** (tier 1, new, 272 lines) —
  Lean Startup canonical (Ries 2011) including MVP as
  validated-learning-minimum NOT smallest-shippable-feature-set,
  Build-Measure-Learn loop, Validated Learning as unit of progress,
  Pivot or Persevere with 10 pivot types; Customer Development (Blank
  2005) 4 steps; Product Discovery vs Delivery distinction (Cagan
  2017 *Inspired* 2nd ed Parts III–IV) including the 4 Big Risks
  cross-reference; Continuous Discovery Habits Opportunity Solution
  Tree (Torres 2021) 4-layer structure; Amazon PR/FAQ Working
  Backwards method (Bryar & Carr 2021 Ch.4) with Press Release 9-item
  and FAQ internal+customer structure. JP genealogy note on Ries's
  explicit Lean lineage to 大野耐一 1978『トヨタ生産方式』.

- **`standards/goals-and-metrics.md`** (tier 1, new, 262 lines) —
  **the largest additive upgrade** in v4.10.0. planning-team v4.9.x
  had **zero OKR coverage**; v4.10.0 adds full OKR specification:
  origin at Intel 1970s (Grove 1983 *High Output Management*),
  modern canonical (Doerr 2018 *Measure What Matters*) with formula
  "I will [O] as measured by [KR]", 0.0-1.0 grading scale, 0.7 is
  aspirational success floor, 3-5 KRs per O. Also adds North Star
  Metric (Ellis & Brown 2017 *Hacking Growth*) with selection
  criteria, AARRR Pirate Metrics (McClure 2007, 5-stage canonical),
  Goals / Non-Goals convention (Ubl 2020 "Design Docs at Google"
  personal blog as community-established de-facto canonical).

- **`standards/spec-completeness-standards.md`** (tier 2, new, 164
  lines) — 5W2H completeness check with correct genealogy (Kipling
  1902 "The Elephant's Child" 5W1H poetic origin → 1960s JUSE
  Japanese quality movement added +2H → Ohno 1978 TPS book-form
  popularization) — NOT purely "Japanese business convention" as
  prior planning-team standards claimed. Per-letter mapping of 7
  questions to PRODUCT-SPEC.md sections (Why/What/Who/When/Where/
  How/How much). JP 企画 cultural anchoring via ヤング 1988 日譯
  『アイデアのつくり方』(James Webb Young 1940 US original, but the
  1988 Japanese translation with 竹内均 commentary is the canonical
  edition in JP 企画 culture). Decision rationale rule: every "we
  chose X" needs a "because Y". Full JP integration (highest JP
  density of the 4 standards files).

- **`checklists/market-validation.md`** (new, 132 lines) — fixes
  the long-standing dangling MAY gate reference in SKILL.md that
  pointed to a file that did not exist (a CHK-SKL-008 Resource
  Manifest consistency failure). 5 checks (CHK-MKT-001 through 005)
  covering customer validation, competitive landscape, market
  sizing claims (FATAL if unsourced), regulatory/compliance claims
  (FATAL if unsourced), go-to-market coherence. Lightweight sanity
  check; defers deep market analysis to research-team's
  `market-analysis` or `competitive-analysis` protocol.

- **`research/grounding-v4.10.0.md`** (new, 569 lines) — complete
  cluster-by-cluster primary source verification note. 9 framework
  clusters covered: JTBD / Lean Startup / OKR / BMC-Lean Canvas /
  DVF assumption frameworks / Product Discovery / Strategy (3C-VPC) /
  Japanese 企画 methodology / North Star-AARRR-Goals-Non-Goals.
  Appendix A: all primary-source ISBNs (audit trail). Appendix B:
  open-access canonical URLs (used in standards file Primary Sources
  sections). Maintainer-facing only per
  `skill-team/protocols/grounding-research.md` Phase 3 rules;
  not referenced by worker/evaluator at runtime.

- **`SKILL.md` persona** — new primary-source discipline paragraph
  naming the canonical authors planning-team anchors on: Christensen,
  Adams, Ries, Grove, Doerr, Cagan, Bland, Osterwalder, 大前研一.

- **`SKILL.md` Behavioral Rules** — 4 new planning-team-specific
  discipline rules:
  1. Primary-source discipline — every framework citation must name
     the canonical author
  2. Job Story template attribution — Adams (2016) Intercom, not
     Christensen
  3. 4 Big Risks is Cagan 2017, not Bland 2020 (Bland uses 3 axes)
  4. MVP is learning, not shipping (Ries 2011)

### Changed

- **`standards/planning-frameworks.md`** — rewritten from 89 lines
  of ungrounded prose to 292 lines of primary-source-anchored
  framework reference. Coverage: JTBD with correct Job Story
  template attribution to Adams 2016 Intercom, Business Model
  Canvas (compact reference — full 9-block treatment stays in
  research-team's `strategic-frameworks.md`), Lean Canvas with
  authoritative Maurya 2022 4-block substitution mapping (Key
  Partners → Unfair Advantage, Key Activities → Key Metrics, Key
  Resources → Solution, Customer Relationships → Problem), Value
  Proposition Canvas (Osterwalder et al. 2014), 4 Big Risks (Cagan
  2017 *Inspired* 2nd ed Part III) as 4-axis canonical — NOT
  Bland, Assumption Mapping (Bland & Osterwalder 2020) as the
  3-axis DVF operational tool, 3C 分析 with full JP integration
  (Japanese subheading, 大前 1975 Japanese original cite, Ohmae
  1982 English expansion as secondary access point). JP genealogy
  preamble with 4 anchors: ヤング 1988 / 大野 1978 / 三枝 1994 /
  大前 1975.

- **`protocols/product-spec-writing.md`** — all 5 phases now anchor
  to the 4 standards files. Phase 1 Vision anchors to JTBD (Adams
  2016 for Job Story, Christensen 2003/2016 HBR for theory), 3C
  (大前 1975), North Star Metric (Ellis & Brown 2017). Phase 2
  Concept anchors to VPC (Osterwalder et al. 2014). Phase 3 Scope
  anchors to OKR format (Grove 1983 / Doerr 2018), Goals/Non-Goals
  (Ubl 2020), 4 Big Risks (Cagan 2017), Assumption Mapping (Bland
  & Osterwalder 2020), MVP-as-validated-learning (Ries 2011). Phase
  4 Direction anchors to decision rationale rule, Lean Canvas,
  AARRR (McClure 2007). Phase 5 Handoff adds 5W2H cross-check with
  correct genealogy.

- **`protocols/planning-brainstorming.md`** — 10-task checklist
  anchored to specific standards references. Task 1 Spark references
  ヤング 1988 5-step idea generation (材料収集 → 咀嚼 → 熟成 →
  ひらめき → 具象化). Task 3 JTBD now explicitly uses Job Story
  template with Adams (2016) Intercom attribution (NOT Christensen).
  Task 4 Landscape anchors to Blank 2005 Customer Development +
  3C 分析 Competitor lens. Task 7 Assumptions uses 4 Big Risks
  (Cagan 2017) — with explicit note that 4-axis is Cagan not Bland.
  Task 9 Scope Boundary anchors to Ubl 2020 Non-Goals convention.

- **`checklists/product-spec-completeness.md`** — expanded from 7
  checks (CHK-PROD-001 through 007) to 9 checks:
  - CHK-PROD-001 Vision & Problem — now requires Job Story template
    (Adams 2016) over "As a user" form
  - CHK-PROD-002 Scope Definition — now requires Non-Goals to name
    plausible rejected goals (Ubl 2020), not trivial exclusions;
    MVP must be learning-minimum (Ries 2011), not smallest shippable
  - **CHK-PROD-003 Assumption Discovery (NEW)** — top 3 assumptions
    must map to 4 Big Risks (Cagan 2017) with named validation
    approaches (Bland 2020)
  - **CHK-PROD-008 5W2H Completeness Cross-Check (NEW)** — 7-letter
    coverage per Kipling → JUSE → Ohno genealogy
  - Renumbered existing checks to 004-005-006-007 (UX / Tech /
    Decision Rationale / Handoff) and 009 (Formatting)

- **`rubrics/cross-domain-consistency.md`** — expanded from 5 flags
  (FLAG-XD-001 through 005) to 6 flags:
  - Existing 4 flags updated to cross-reference grounded standards
  - **FLAG-XD-005 Assumption → Risk Coverage (NEW)** — verifies that
    every [ASSUMPTION] tag maps to one of the 4 Big Risks, and that
    top 3 assumptions cover ≥2 distinct risk categories
  - FLAG-XD-006 Terminology Consistency (renumbered from FLAG-XD-005)
    — now checks Job Story vs user-story consistency

- **`SKILL.md` Resource Manifest** — worker/evaluator now pass 4
  standards files (previously 1). Both launch templates updated to
  pass the full 4-file standards array.

- **`SKILL.md` Worker launch template** — `### Input` now includes
  `output_language` and `scope_clarity: {clear | unclear}` fields
  for consistency with research-team v4.9.1 launch convention.
  `scope_clarity=unclear` routes to planning-brainstorming first.

- **`SKILL.md` Evaluator launch template** — now passes standards
  array (for gates to verify claims map to primary sources) and
  `output_language` field.

- **`SKILL.md` frontmatter description** — adds "grounded in
  primary-source product-management canon" language and names the
  load-bearing frameworks (JTBD, Lean Startup, OKR, 4 Big Risks,
  BMC/Lean Canvas). Satisfies CHK-SKL-002 by surfacing the
  grounding in the description itself so downstream routers know
  what planning-team now anchors on.

- **`SKILL.md` When to Use** — MVP bullet now cites Ries 2011
  ("minimum for validated learning, not smallest shippable feature
  set") to reinforce the discipline.

### Fixed

- **Dangling MAY gate reference** — SKILL.md has referenced
  `checklists/market-validation.md` as a MAY gate since v3.x, but
  the file never actually existed (a CHK-SKL-008 Resource Manifest
  consistency failure that the skill-coherence gate would have
  caught). v4.10.0 creates the file properly.

- **Prior 4-axis DVF misattribution** — planning-team v4.9.x listed
  "Desirability / Feasibility / Viability / Usability" as 4-axis
  assumption categories and (implicitly) attributed the framework
  to Bland & Osterwalder. Bland uses only 3 axes (DVF). The 4-axis
  version with Usability as a distinct fourth is **Marty Cagan's
  Four Big Risks** from *Inspired* 2nd ed 2017 Part III. v4.10.0
  corrects the attribution: the 4 Big Risks are cited to Cagan
  (Value / Usability / Feasibility / Business Viability), and
  Assumption Mapping is cited separately to Bland & Osterwalder 2020
  as a 3-axis DVF operational tool (Impact × Evidence 2×2).

- **Prior Job Story template misattribution** — planning-team v4.9.x
  used the "When [situation], I want to [motivation], so I can
  [outcome]" template under JTBD as if it were Christensen's. The
  template is actually Paul Adams 2016-06-28 Intercom blog post
  "How we accidentally invented Job Stories", later named "Job
  Stories" by Alan Klement in *When Coffee and Kale Compete* (2018).
  Christensen's 2003 book and 2016 HBR article never used this
  sentence form. v4.10.0 cites Adams (2016) for the template and
  Christensen (2003 / 2016 HBR) for the theory, separately.

- **Prior 5W2H misattribution** — planning-team v4.9.x described
  5W2H as "日本ビジネス慣習由來" ("derived from Japanese business
  customs") as a single-origin claim. The correct genealogy is
  multi-origin composite: Kipling 1902 poetic origin → late-19th-
  century US journalism → 1960s JUSE Japanese quality movement
  added +2H → Ohno 1978 TPS popularization. v4.10.0 spells out the
  full genealogy in `spec-completeness-standards.md`.

- **Prior 3C 分析 missing publication anchor** — planning-team
  v4.9.x attributed 3C vaguely to "（大前研一）" without a citation.
  v4.10.0 cites 大前研一 (1975)『企業参謀』プレジデント社 as the
  Japanese original and Ohmae (1982) *The Mind of the Strategist*
  McGraw-Hill as the English expansion (~60% rewritten, not a
  direct translation).

### Notes

planning-team does NOT adopt the quick/deep cost modes that
research-team introduced in v4.9.1. Planning work has a different
cost profile — the dominant cost is human-clarification loops (the
10-task brainstorming checklist), not LLM token consumption per
source. Planning-team's natural cost tiering is already handled by
its 3 existing workflows (Scope Refinement < Major Direction Change <
New Project) and does not need a separate mode parameter. If future
usage shows that the New Project workflow is too expensive by
default, a cost-aware mode can be added in a follow-up PATCH.

SKILL.md line count: 225 → 302. Still well within the 500-line
budget. No skill-team CI regression expected
(`check-skill-structure.py`).

## [4.9.1] — 2026-04-11

research-team cost-aware research modes (quick / deep) with
**default-cheap discipline**: every research task starts in quick
mode (~15k tokens, ≤5 sources, SELF check only) unless the user
opts into deep mode via explicit trigger phrase or post-hoc
escalation after seeing the quick output. PATCH bump per
`skill-team/standards/commit-convention.md` CHK-CMT-005 because no
new files are added at runtime — all changes are modifications to
existing standards / protocols / gates / SKILL.md / plugin.json /
CHANGELOG.md. The v4.10.0 reservation for planning-team grounding
is preserved. Cost impact: typical research task drops from
~150-300k tokens (deep-by-default in v4.9.0) to ~15-30k tokens
(quick-by-default in v4.9.1), an estimated 5-10× reduction for
general-purpose research while preserving audit-trail-grade rigor
as an opt-in path.

### Added

- `standards/confidence-and-claim-language.md` §**Cost-Aware
  Early-Exit Rule** — the canonical mode-threshold SSOT referenced
  by SKILL.md `## Research Modes`. Defines per-mode exit thresholds
  on the IPCC 3×3 evidence × agreement grid: **quick** exits when
  each key claim reaches medium-confidence with ≥1 primary source;
  **deep** exits at very-high-confidence OR budget exhaustion OR
  marginal-value flatline. Per-claim (not per-deliverable) policy
  targets the worst-confidence key claim so workers cannot
  triangulate the easy claims and leave hard claims
  under-evidenced. Partial completion is a first-class outcome
  (mixed-confidence deliverable with `unresolved: true` metadata),
  NOT a BLOCKED condition. Explicit anti-patterns block
  auto-escalation from quick to deep and aggregation of per-claim
  confidence into a single "overall confidence".

- **SKILL.md `## Research Modes` section** (between `## Gate
  Protocol` and `## Resource Manifest`) — full quick/deep mode
  specification: default budgets, synthesis shape, gate suites,
  exit thresholds, use cases. Quick-first default + post-hoc
  escalation UX flow with actual footer format. Explicit-deep
  bypass trigger phrase table in English / 日本語 / 繁體中文 /
  简体中文 plus deliberately-excluded ambiguous phrases. Mid-stream
  escalation (`run deep`) re-launches a second worker in deep mode
  with the quick artifact as `### Input` seed context (~30-40%
  saving vs cold-start deep). Quick-mode BLOCKED handling
  explicitly forbids worker-side auto-escalation.

- **SKILL.md `## Behavioral Rules` default-cheap discipline bullet**
  — codifies the two-condition escalation rule: only (a) explicit
  deep-mode trigger phrase in user prompt OR (b) "run deep" reply
  after quick output triggers deep mode. Worker never auto-
  escalates; escalation belongs to the user.

### Changed

- **7 research-team protocols gained Phase 0 mode detection +
  budget enforcement** (commit 2/3 `cf89269`):
  - `protocols/research.md`
  - `protocols/research-brainstorming.md`
  - `protocols/academic-research.md`
  - `protocols/market-analysis.md`
  - `protocols/competitive-analysis.md`
  - `protocols/investment.md`
  - `protocols/stack-evaluation.md`

  Each protocol now reads `mode` + `max_tokens` + `max_sources` +
  `max_web_searches` from worker `### Input` and applies per-team
  quick-mode reductions (e.g., single-framework-only for Market
  Analysis quick mode, reduced PRISMA scope for Academic Research
  quick mode, skip Investment Clock full 2×2 for Investment quick
  mode).

- **3 gates gained Mode-Aware Triggering note** (commit 2/3):
  - `checklists/source-citation-checklist.md` (MUST gate — skipped
    in quick mode per `## Research Modes`)
  - `rubrics/research-quality-gate.md` (SHOULD gate — skipped in
    quick mode)
  - `checklists/oss-due-diligence.md` (MAY gate — explicit opt-in
    regardless of mode, but full suite only runs in deep mode)

- **SKILL.md persona** — new **default-cheap discipline** line near
  the Mission / Delivers block: "every research task starts in
  quick mode (~15k tokens, ≤5 sources) unless the user explicitly
  requests deep mode via trigger phrase or post-hoc escalation."

- **SKILL.md workflows table refactored 8 → 7 rows**:
  - Standalone Deep Research / Analysis workflow DELETED (see
    Removed)
  - New **Default Mode** column added to the 5 worker-dispatching
    workflow phase tables (Market Analysis, Competitive Analysis,
    Academic Research, Investment Analysis, Tech Stack / OSS
    Evaluation) — every entry reads `quick`
  - Quick Lookup / Fact-Check and Research Summary gained an
    explicit `**Default mode**: quick (handled in main, no worker
    dispatch)` line
  - Header notes added: "All worker-dispatching workflows default
    to quick mode" + "`scope_clarity=unclear` invokes Brainstorm +
    Synthesize phase hooks"
  - Per-gate-table header annotations now mark MUST + SHOULD as
    "skipped in quick mode per `## Research Modes`"

- **SKILL.md worker launch template `### Input`** — gained 5 new
  fields: `output_language`, `mode`, `max_tokens`, `max_sources`,
  `max_web_searches`, `scope_clarity`. Existing artifact / context
  fields preserved.

- **SKILL.md evaluator launch template `### Input`** — new
  `mode` field so evaluators know which per-mode threshold to
  enforce from the Cost-Aware Early-Exit Rule.

- **SKILL.md Note on Global Context** — second paragraph compressed
  from 11 lines to 8 lines to stay well under the 500-line hard cap
  while preserving the same preamble-integration decision record.

### Removed

- **Deep Research / Analysis workflow as standalone entry** — the
  Brainstorm (Phase 1) + Research (Phase 2) + Synthesize (Phase 3)
  flow is replaced by optional **Brainstorm phase hook** and
  **Synthesize phase hook** invokable via `scope_clarity=unclear`
  on any worker-dispatching workflow. This collapses the 3-phase
  dedicated workflow into an opt-in capability that composes with
  every other workflow, rather than duplicating the effect as a
  separate entry.

### Design rationale

Why post-hoc escalation default + trigger phrase bypass + no
upfront cost preview: the v4.7.0 Obsidian opt-in directive
precedent established that **"silence means default behavior — do
not prompt"**. Upfront cost previews force every user through a
confirmation round-trip before any work starts, even for trivial
research that will finish in quick mode's default budget. The
better UX is to run quick mode silently, show the result, and
offer escalation **after** the user has seen whether it was
sufficient — at which point they have the most information for
the decision. The Plan-agent critique that landed this refactor
explicitly recommended collapsing cost preview prose, $-amount
estimates, and confirmation prompts into a post-hoc footer.

Why a trigger phrase bypass: users who have pre-decided on deep
mode (because they know the task is high-stakes) should not be
forced through the quick-first intermediate. The trigger phrase
table explicitly excludes ambiguous phrases like "thorough
analysis", "comprehensive review", and 「詳細分析」 because those
are how normal users phrase normal requests; only unambiguous
phrases like "deep research", "spare no expense", 「徹底調査」, or
「深入研究」 trigger the bypass.

### Cost impact

Typical research task drops from ~150-300k tokens (deep-by-default
in v4.9.0 and earlier, which triggered the full MUST + SHOULD gate
suite for every workflow) to ~15-30k tokens (quick-by-default in
v4.9.1, which skips MUST + SHOULD for quick output and calls a
lightweight SELF check instead). Estimated **5-10× cost
reduction** for general-purpose research while preserving
audit-trail-grade IPCC-level rigor as an opt-in path for
high-stakes tasks. Mid-stream escalation (quick → deep with the
quick artifact as seed) is ~30-40% cheaper than cold-start deep
mode because the deep worker focuses on gap-filling rather than
duplicating the triangulation the quick pass already performed.

### Out of scope (deferred)

- **Mode-aware gate threshold tuning** (v4.9.2 if needed) — the
  current implementation is a binary skip: quick mode skips MUST +
  SHOULD entirely rather than running relaxed per-mode variants.
  A future refinement could introduce per-mode threshold tiers
  inside the gate files themselves.
- **Per-workflow budget tuning** (v4.9.2 if needed) — every
  worker-dispatching workflow currently uses the default 15k /
  150k quick / deep budgets. Some workflows (e.g., Academic
  Research with PRISMA-grade scope) may deserve per-workflow
  budget defaults in a future refinement.
- **Cost preview prose and dollar-amount estimates** —
  deliberately excluded per the v4.7.0 Obsidian opt-in directive
  precedent. Users see actual consumption in the post-hoc footer,
  not projected estimates before work starts.
- **planning-team grounding** — v4.10.0 milestone reservation
  preserved. planning-team remains the only ungrounded domain team
  after v4.9.x.
- **Hooks** — v5.0+ milestone; not touched by v4.9.1.

### Meta

**PATCH bump rationale** per `skill-team/standards/commit-convention.md`
CHK-CMT-005 distinguishing rule ("does this branch introduce new
files that worker or evaluator agents will Read at runtime? Yes →
MINOR. No → PATCH."): v4.9.1 introduces **zero new files**. Every
change in this release is a modification to an existing runtime
file:

- `confidence-and-claim-language.md` gains a new section but the
  file itself already existed from v4.9.0
- 7 protocols gain a Phase 0 block but the files already existed
- 3 gates gain a Mode-Aware Triggering note but the files already
  existed
- SKILL.md gains sections and table columns but the file already
  existed
- plugin.json and CHANGELOG.md are the standard version-bump
  files

This makes v4.9.1 a textbook PATCH bump — the new section in
`confidence-and-claim-language.md` is a section addition inside
an existing file, not a new file.

**3-commit split pattern** per `skill-team/protocols/skill-redesign.md`:
- Commit 1/3 `3be7860` — standards (§Cost-Aware Early-Exit Rule)
- Commit 2/3 `cf89269` — protocols + gates (Phase 0 mode detection +
  Mode-Aware Triggering notes)
- Commit 3/3 (this commit) — SKILL.md + plugin.json + CHANGELOG

### Verification

- `python3 scripts/check-skill-structure.py domain-teams` → all 9
  skills PASS (research-team included) after this commit.
- SKILL.md line count: 496 lines (under the 500-line hard cap per
  `skill-md-structure.md` §Line Budget).
- Frontmatter description word count unchanged from v4.9.0 (69
  tokens, comfortably above the 40-token CHK-SKL-001 floor).
- Investment Clock phase naming from v4.9.0 (Reflation / Recovery /
  Overheat / Stagflation) preserved — not touched by v4.9.1.

## [4.9.0] — 2026-04-11

research-team grounding refactor — closes the "philosophical
hotspot" gap where research-team's own rules were previously
self-invented despite its job being primary-source rigor. The Phase 1
gap report catalogued six major taxonomy clusters without primary
source anchors (source quality, confidence language, research
process, strategic frameworks, investment regime phases, OSS
thresholds). Phase 2 research (`research/grounding-v4.9.0.md`, 1991
lines, 30+ verified primary sources) assembled the canonical anchors.
Phase 4-6 landed 6 NEW standards and 2 REWRITE-in-place standards as
three atomic commits per the grounding refactor convention. With
research-team grounded, **6 of 8 domain teams are now grounded**
(qa / docs / devops / code / design / research). Only `planning-team`
remains ungrounded for a future v4.10.0 milestone. research-team also
adopts the **preamble** JP integration strategy per
`skill-team/standards/grounding-principle.md`: JP contributes
information-infrastructure (NDL リサーチ・ナビ + CiNii Research +
SIST 02 + 倉田敬子 2007) but has no parallel research-methodology
canon to rival Cochrane / PRISMA / Booth / Damodaran / Porter.

### Added

- **6 new research-team standards** (Phase 4 synthesis of Phase 2
  grounding research, `research/grounding-v4.9.0.md`):
  - `source-quality-and-evidence.md` (Tier 1) — JMU/Cornell/ACRL
    primary / secondary / tertiary source taxonomy + Kovach &
    Rosenstiel 2021 *The Elements of Journalism* 4th ed. discipline
    of verification + SPJ ethics code. Structural source-quality
    SSOT for all research workflows.
  - `confidence-and-claim-language.md` (Tier 2) — IPCC AR5
    Mastrandrea et al. 2010 5-level confidence ladder (very low /
    low / medium / high / very high) + 7-level likelihood ladder
    (virtually certain → exceptionally unlikely) + 3×3 evidence ×
    agreement grid + Sherman Kent 1964 words-of-estimative-probability
    + Tetlock & Gardner 2015 *Superforecasting* calibration discipline.
  - `systematic-review-methodology.md` (Tier 2) — Cochrane Handbook
    for Systematic Reviews of Interventions v6.5 (2024) 8-step
    workflow + PRISMA 2020 27-item 7-section reporting checklist +
    Booth, Colomb, Williams, Bizup & FitzGerald *The Craft of
    Research* 5th ed. (2024) 5-element argument model (claim /
    reason / evidence / warrant / acknowledgement).
  - `strategic-frameworks.md` (Tier 1) — Porter 1980
    *Competitive Strategy* Five Forces + value chain + Kim &
    Mauborgne 2015 *Blue Ocean Strategy* ERRC grid and strategy
    canvas + Osterwalder & Pigneur 2010 Business Model Canvas
    9-block + Aaker 1991 brand equity 5-component.
  - `investment-analysis-canon.md` (Tier 3) — Damodaran 2012
    *Investment Valuation* 3rd ed. three-framework taxonomy
    (DCF / relative / contingent-claim) + Graham & Dodd *Security
    Analysis* margin of safety + Mr. Market parable + Greetham &
    Hartnett 2004 *Merrill Lynch Investment Clock* growth × inflation
    2×2 regime mapping. Tier 3 body fully self-contained: all 4
    Investment Clock phases (Reflation / Recovery / Overheat /
    Stagflation) spelled out with their {Bonds, Stocks, Commodities,
    Cash} asset-class implications.
  - `information-infrastructure.md` (Tier 3) — JP preamble standard
    grounded on 倉田敬子 2007 『学術情報流通とオープンアクセス』
    (勁草書房) + 国立国会図書館リサーチ・ナビ 3-tier structure
    (テーマ別調査案内 / 資料群別案内 / 調べ方マニュアル) + 国立
    情報学研究所 CiNii Research 2022 統合 + ACRL 2016 Framework
    6 frames as comparative anchor + SIST 02-2007 参照文献書き方
    + 野末俊比古 2010 情報リテラシー教育. Tier 3 body fully
    self-contained with JP/Anglo primary-secondary-tertiary
    comparison table and JP-database decision rules.

- `research-team/research/grounding-v4.9.0.md` — 1991-line Phase 2
  grounding research audit trail. 30+ primary-source citations
  independently verified: Booth 5th ed. 2024, Cochrane Handbook
  v6.5 (2024), PRISMA 2020, IPCC Mastrandrea et al. 2010, Kent
  1964, Tetlock & Gardner 2015, Kovach & Rosenstiel 2021 4th ed.,
  SPJ ethics code, JMU / Cornell / ACRL source-quality guides,
  Porter 1980, Kim & Mauborgne 2015, Osterwalder & Pigneur 2010,
  Aaker 1991, Damodaran 2012, Graham & Dodd, Greetham & Hartnett
  2004, APA 7th, Chicago 18th (2024-09), IEEE, SIST 02-2007,
  OpenSSF Scorecard, NIST SSDF 1.1, SLSA v1.1, CVSS v4.0, SPDX
  v3.0, 倉田敬子 2007, NDL リサーチ・ナビ, CiNii Research 2022,
  野末俊比古 2010. Includes cluster mapping, JP parallel-tradition
  check, tier classification worksheet, and 5 residual known-knowns.

- **research-team SKILL.md new sections**:
  - `## Note on Global Context` — declares **preamble** JP
    integration strategy. Documents that Japan has substantial
    information-infrastructure apparatus (NDL / CiNii / SIST 02 /
    倉田 2007 / 野末 2010) but no JP-native parallel research-
    methodology framework to rival Cochrane / PRISMA / Booth /
    Damodaran / Porter. Same pattern as docs-team v4.3.0 (JTAP
    preamble to Google Style) and code-team v4.6.0 (徳丸本 Ch.6
    preamble to OWASP ASVS).
  - `## When NOT to Use` — explicit arrow-delegation list split
    out from the old Cross-Domain Awareness prose. Delegations
    to code-team, design-team, planning-team, docs-team, qa-team,
    devops-team, and skill-team.

- **Checklist item additions**:
  - `source-citation-checklist.md` — CHK-SRC-005 (Primary Source
    Priority) [FATAL] grounded in source-quality-and-evidence;
    CHK-SRC-006 (Confidence Calibration) [FIXABLE] grounded in
    confidence-and-claim-language; CHK-SRC-007 (Citation Format)
    [FIXABLE] grounded in citation-standards.
  - `oss-due-diligence.md` — CHK-OSS-007 (SLSA Build Level)
    [FIXABLE][MAY] optional check grounded in SLSA v1.1.

### Changed

- **2 standards rewritten in place** (preserving filename
  contracts so existing protocol / gate references do not break):
  - `citation-standards.md` (Tier 2, +176 lines) — adds explicit
    Primary Sources section citing APA 7th, Chicago 18th (2024-09),
    IEEE, and SIST 02-2007 with format examples; preserves existing
    search protocol, freshness heuristics, confidence language, and
    Fact/Analysis/Speculation labeling. Structural reorganization
    aligns with v4.7.2 Compact+Admonitions + tier declaration.
  - `oss-safety.md` (Tier 2, +204 lines) — adds OpenSSF Scorecard
    18-check 3-theme structure + NIST SSDF 1.1 4 practice groups +
    SLSA v1.1 L0-L3 + CVSS v4.0 4 metric groups + SPDX v3.0;
    preserves existing license taxonomy.

- **7 protocols gain ## Primary Sources cross-refs** (commit 2/3):
  - `research.md` — systematic-review-methodology +
    confidence-and-claim-language + source-quality-and-evidence;
    Phase 2 adds claim taxonomy + Phase 3 adds Booth 5-element
    argument model
  - `research-brainstorming.md` — source-quality-and-evidence +
    ACRL "Research as Inquiry" frame; JP prose preserved
  - `academic-research.md` — systematic-review-methodology
    (Cochrane 8-step + PICO/PICOC + PRISMA 2020 + Booth) +
    source-quality-and-evidence + information-infrastructure (JP
    database list now references the standard)
  - `market-analysis.md` — strategic-frameworks (Porter Five
    Forces + value chain) + source-quality-and-evidence +
    confidence-and-claim-language
  - `competitive-analysis.md` — strategic-frameworks (Blue Ocean
    Four Actions + Strategy Canvas + Porter + BMC + Aaker) +
    source-quality-and-evidence
  - `investment.md` — PROMOTED from 31-line rubric-like snippet
    to full Phase 0-3 + Rules + Output Format protocol (~130 lines)
    grounded in investment-analysis-canon (Damodaran three-framework
    + Graham & Dodd margin of safety + Mr. Market + Greetham &
    Hartnett 2004 Investment Clock)
  - `stack-evaluation.md` — oss-safety (OpenSSF Scorecard + NIST
    SSDF + SLSA v1.1 + CVSS v4.0 + SPDX v3.0) + citation-standards
    + source-quality-and-evidence; Step 4 quantitative thresholds
    disclosed as internal operational heuristics.

- **2 checklists and 1 rubric modified**:
  - `checklists/source-citation-checklist.md` — 3 new items +
    Primary Sources section (see Added)
  - `checklists/oss-due-diligence.md` — CHK-OSS-002 expanded with
    CVSS v4.0 severity bands + CHK-OSS-007 added (see Added)
  - `rubrics/research-quality-gate.md` — grounds each of 4 flag
    dimensions: Source Quality & Cross-Verification →
    source-quality-and-evidence (Kovach); Reasoning & Logic →
    Booth 5-element argument model; Completeness → PRISMA 2020;
    Actionability → Kovach "Discipline of Verification"

- **SKILL.md persona** — new "anchored on eleven primary sources"
  clause in prose form: Booth 2024, Cochrane v6.5, PRISMA 2020,
  IPCC Mastrandrea 2010, Kovach & Rosenstiel 2021, OpenSSF
  Scorecard, Porter 1980, Damodaran 2012, Greetham & Hartnett
  2004, 倉田敬子 2007, NDL リサーチ・ナビ. Follows the code-team
  v4.6.0 + design-team v4.8.0 persona shape.

- **SKILL.md frontmatter description** — expanded from 43 word
  tokens to 69 word tokens (comfortably above the v4.6.1 40-word
  floor). Adds "OSS license audits" and "investment / macro
  analysis" and "academic literature review" as explicit trigger
  verbs. Adds "tech stack assessments, investment memos" to the
  Delivers clause.

- **MAY Gates table format fixed**: 2-column `Gate | File` →
  3-column `Gate | Trigger | File` per
  `skill-team/standards/skill-md-structure.md` §Quality Gates
  Sub-Section Rules. Trigger text: "User explicitly requests OSS
  license or compliance audit."

- **Behavioral Rules and Agents sections promoted** from nested
  `### Behavioral Rules` / `### Agents` (under Resource Manifest)
  to top-level `## Behavioral Rules` / `## Agents`. Aligns
  research-team with the required-section order in
  `skill-md-structure.md` §Required Sections positions 9 and 10.

- **SKILL.md Resource Manifest expanded** from 1 standard
  (`citation-standards.md` only) to all 8 standards with tier
  annotations (T1 × 2: source-quality, strategic-frameworks;
  T2 × 4: citation, confidence, systematic-review, oss-safety;
  T3 × 2: investment-analysis-canon, information-infrastructure).
  Worker default = 3 always-loaded standards; additional 5
  standards load per-workflow. Worker and evaluator launch
  templates updated to show the 3-standard default + commented
  injection pattern for workflow-specific additions.

- **SKILL.md workflow tables** — every workflow's Notes column and
  gate Standards column updated to reflect the new standards map:
  Deep Research → 3 defaults + systematic-review (SHOULD);
  Market → 3 defaults + strategic-frameworks (SHOULD);
  Competitive → 3 defaults + strategic-frameworks (SHOULD);
  Academic → 3 defaults + systematic-review + information-infrastructure;
  Investment → 3 defaults + investment-analysis-canon (SHOULD);
  Tech Stack / OSS → 3 defaults + oss-safety (SHOULD + MAY).

- **SKILL.md Cross-Domain Awareness** — trimmed; "When NOT to
  Use"-style content moved to the new dedicated `## When NOT to
  Use` section. Remaining content is only lightweight cross-domain
  task examples, with an explicit pointer to `## When NOT to Use`
  for full switches.

- **`protocols/investment.md` restructured** — from a 31-line rubric-
  like snippet to the full Phase 0-3 + Rules + Output Format
  protocol pattern used by other research-team protocols. +148
  lines total.

### Fixed

Three critical attribution corrections, each isolated in a
dedicated section per grounding-principle.md Critical Attribution
Corrections convention:

1. **Investment Clock 4-phase renaming**
   (`protocols/investment.md` line 15 +
   `standards/investment-analysis-canon.md`) — previously labeled
   regime states as "expansion / slowdown / contraction / recovery"
   (generic business-cycle vocabulary not attributable to any
   source). The correct Greetham & Hartnett 2004 *Merrill Lynch
   Investment Clock* phase names are **Reflation / Recovery /
   Overheat / Stagflation**, mapped to {Bonds, Stocks, Commodities,
   Cash} via growth × inflation axes. The standards body spells
   out the full 2×2 matrix with asset-class implications for each
   phase; the investment protocol now cites the correct names.

2. **Chicago 18th + Booth 5th editions current**
   (`standards/citation-standards.md` +
   `standards/systematic-review-methodology.md`) — LLM training-
   data drift tends to treat Chicago 17th (2017) and Booth 4th as
   current. v4.9.0 adopts **Chicago Manual of Style 18th ed.
   (2024-09)** which removes place-of-publication and chapter
   inclusive-pages from author-date format, and **Booth, Colomb,
   Williams, Bizup & FitzGerald *The Craft of Research* 5th ed.
   (2024-06-25)** which retains the 5-element argument model with
   the FitzGerald co-authorship added.

3. **Internal operational conventions disclosed**
   (`standards/citation-standards.md` + `standards/oss-safety.md`) —
   the 6-month freshness threshold (used in the "data freshness"
   guard rail) is a research-team **internal heuristic**, NOT an
   IPCC / PRISMA / Cochrane-grounded value. The stack-evaluation
   quantitative thresholds (>500 issues, >12 months no commit,
   <1000 weekly downloads) are research-team **internal heuristics**,
   NOT CHAOSS metrics or OpenSSF Scorecard values. Both are
   retained because they have been operationally useful, but now
   explicitly flagged as internal convention so evaluators do not
   misattribute them to the primary sources.

### Removed

- **Hard-coded "kouko's vault" path references**
  (`protocols/investment.md` lines 20-24) — replaced with generic
  "consult research notes if available" guidance. Protocols must
  not reference a single maintainer's personal Obsidian vault
  structure; v4.9.0 closes the last known occurrence.

### Primary Sources adopted

Research note (`research/grounding-v4.9.0.md`) summary cluster list
— 30+ verified citations organized by cluster:

- **Source Quality** (Cluster A): JMU library source-type guide,
  Cornell library research primer, ACRL Framework for Information
  Literacy for Higher Education (2016), Kovach & Rosenstiel
  *The Elements of Journalism* 4th ed. (2021), Society of
  Professional Journalists Code of Ethics.
- **Confidence and Claim Language** (Cluster B): IPCC AR5
  guidance note on uncertainty (Mastrandrea et al. 2010), Sherman
  Kent 1964 "Words of Estimative Probability" CIA Studies in
  Intelligence, Tetlock & Gardner 2015 *Superforecasting*.
- **Systematic Review** (Cluster C): Cochrane Handbook for
  Systematic Reviews of Interventions v6.5 (2024, Higgins et al.
  eds.), PRISMA 2020 statement (Page et al. 2021), Booth / Colomb
  / Williams / Bizup / FitzGerald *The Craft of Research* 5th ed.
  (2024).
- **Strategic Frameworks** (Cluster F): Porter 1980 *Competitive
  Strategy*, Kim & Mauborgne 2015 *Blue Ocean Strategy* expanded
  ed., Osterwalder & Pigneur 2010 *Business Model Generation*,
  Aaker 1991 *Managing Brand Equity*.
- **Investment Analysis** (Cluster G): Damodaran 2012 *Investment
  Valuation* 3rd ed., Graham & Dodd *Security Analysis* (6th ed.
  2008 McGraw-Hill with Buffett foreword), Greetham & Hartnett
  2004 *The Investment Clock* (Merrill Lynch Global Strategy).
- **Citation Format** (Cluster D): APA Publication Manual 7th ed.
  (2020), Chicago Manual of Style 18th ed. (2024), IEEE Citation
  Reference, SIST 02-2007 参照文献の書き方 (日本学術情報センター).
- **OSS Safety** (Cluster E): OpenSSF Scorecard (current), NIST
  Secure Software Development Framework v1.1 (SP 800-218), SLSA
  v1.1 Supply-chain Levels for Software Artifacts, CVSS v4.0
  (FIRST.org), SPDX v3.0 (Linux Foundation).
- **JP Information Infrastructure** (Cluster H): 倉田敬子 2007
  『学術情報流通とオープンアクセス』(勁草書房, 日本図書館情報
  学会賞 2008), 国立国会図書館リサーチ・ナビ (NDL, current),
  国立情報学研究所 CiNii Research (NII, 2022 統合), 野末俊比古
  2010 情報リテラシー教育, ACRL Framework 2016 (comparative anchor).

### JP integration decision

research-team v4.9.0 adopts **preamble** integration, matching
docs-team v4.3.0 and code-team v4.6.0, not qa-team v4.2.0 (full)
or devops-team v4.4.0 (no overlay).

- **Evidence**: Phase 2 research JP parallel-tradition check
  (`research/grounding-v4.9.0.md`) verified that Japan has
  substantial information-infrastructure works — 倉田敬子 2007,
  NDL リサーチ・ナビ, CiNii Research 2022, SIST 02-2007, 野末
  2010 情報リテラシー教育 — but these are **infrastructure and
  access works**, not parallel research-methodology canons. There
  is no JP-native equivalent to Cochrane / PRISMA / Booth /
  Damodaran / Porter. The Anglo-American canon dominates research
  methodology, systematic review, strategic frameworks, and
  investment analysis.
- **Pattern match**: docs-team v4.3.0 (JTAP 技術文書 3 原則 as
  reader-first preamble to Google Style) + code-team v4.6.0
  (徳丸本 Ch.6 as multi-byte security preamble to OWASP ASVS).
- **Implementation**: one Tier 3 preamble standards file
  (`standards/information-infrastructure.md`) orienting workers
  to JP database infrastructure + SIST 02 citation conventions.
  Plus 倉田敬子 2007 and NDL リサーチ・ナビ named in the
  SKILL.md persona "anchored on" list as 2 of 11 load-bearing
  anchors.

### Tier distribution

Following `skill-team/standards/grounding-principle.md` §3-Tier
Parametric Classification (v4.7.2):

- **Tier 1 (high parametric)** × 2:
  - `source-quality-and-evidence.md`
  - `strategic-frameworks.md`
- **Tier 2 (medium parametric)** × 4:
  - `citation-standards.md` (rewrite)
  - `confidence-and-claim-language.md`
  - `systematic-review-methodology.md`
  - `oss-safety.md` (rewrite)
- **Tier 3 (low parametric, fully self-contained body)** × 2:
  - `investment-analysis-canon.md` — Investment Clock 2×2 matrix
    fully spelled out; Damodaran three-framework explained with
    DCF / relative / contingent-claim distinctions; Graham & Dodd
    margin-of-safety in body
  - `information-infrastructure.md` — NDL 3-tier structure
    explained in body; CiNii Research 2022 統合 cataloged;
    倉田 2007 core thesis summarized; JP/Anglo comparison table
    in body

### research-team v4.9.0 achievement summary

- **6th grounded team** (after qa / docs / devops / code / design)
- **Closes the "philosophical hotspot" gap**: research-team's own
  rules were previously self-invented despite its job being
  primary-source rigor — the meta-cringiest gap in the repo
- **1 team left**: `planning-team` is the only remaining ungrounded
  domain team. Targeted for v4.10.0 (next milestone).
- Scope discipline: the 3-commit split strictly separated
  standards (commit 1/3), protocols + gates (commit 2/3), and
  SKILL.md + plugin.json + CHANGELOG (commit 3/3) per
  `skill-team/protocols/skill-redesign.md` Phase 4-6.

### Meta

**MINOR bump rationale** per v4.8.1 `commit-convention.md`
§Semver and CHK-CMT-005 distinguishing rule: this refactor adds 6
new standards files and 1 research note file that the worker and
evaluator will Read at runtime (via Resource Manifest + Agent
Launch templates). New files that agents read at runtime
classifies as MINOR, not PATCH. The 2 rewrite-in-place files
(`citation-standards.md`, `oss-safety.md`) are not new, but the
SKILL.md wiring exposes them alongside the 6 new files as an
8-standard array — the pattern is "additive", not "modify-only".

3-commit split pattern per skill-redesign protocol:
- Commit 1/3 `0fb0b22` — standards + research note
- Commit 2/3 `73076a1` — protocols + checklists + rubric
- Commit 3/3 (this commit) — SKILL.md + plugin.json + CHANGELOG

### Verification

- `python3 scripts/check-skill-structure.py domain-teams` → all 9
  skills PASS (research-team included) after this commit.
- Dogfood gate suite (Skill Completeness + Skill Coherence +
  Primary Source Grounding rubric + Commit Split) will run after
  this commit lands, per skill-redesign protocol Phase 7.
- 3-commit structure verified: standards isolated to 1/3,
  protocols + gates isolated to 2/3, SKILL.md + plugin.json +
  CHANGELOG isolated to 3/3. No cross-commit drift.

## [4.8.2] — 2026-04-11

First CI infrastructure for the repo. Adds a deterministic
SKILL.md structure validator and a Conventional Commits checker
that run on every push to main and every pull request. PATCH bump
because the new files are CI infrastructure (build / validation),
not runtime files read by worker or evaluator agents — per the
v4.8.1 CHK-CMT-005 distinguishing rule "does this branch introduce
new files that worker or evaluator agents will Read at runtime?
Yes → MINOR. No → PATCH."

### Added

- `scripts/check-skill-structure.py` — standalone Python validator
  that walks every `domain-teams/skills/*/SKILL.md` and runs five
  deterministic CHK-SKL-* checks from skill-team v4.8.1
  `checklists/skill-completeness-checklist.md`. Designed for both
  local invocation (`python3 scripts/check-skill-structure.py
  domain-teams`) and CI use. Targets zero false positives on the
  current grounded teams (qa / docs / devops / code / design) plus
  the ungrounded teams (research / planning) and the router skill
  (`using-domain-teams`).

  Checks implemented:

  - **CHK-SKL-001** (FATAL) — frontmatter `description` >= 40 word
    tokens after the v4.6.1 hyphen/slash compound tokenization rule
    and exclusion of CJK tokens. Counts only English prose body per
    `skill-md-structure.md` §Frontmatter Schema §Word count rule.
    Router skills (no `protocols/` subdirectory, no worker launch
    template in SKILL.md) are exempt per the v4.6.1 router exemption
    landed in `skill-md-structure.md` §Router-skill exemption.
  - **CHK-SKL-005** (FATAL) — every concrete `{base_path}/<dir>/
    <filename>.md` path in the `## Agent Launch Protocol` section
    actually exists on disk. Resource Manifest list bullets are
    deliberately NOT validated because they often list aspirational
    MAY gates with `(MAY)` annotations; Resource-Manifest-vs-launch-
    template drift is documentation drift, not runtime drift, and
    is caught by the `skill-coherence` SHOULD gate at refactor time.
  - **CHK-SKL-010** (FATAL) — SKILL.md <= 500 lines (hard cap from
    `skill-md-structure.md` §Line Budget).
  - **CHK-SKL-011** (FATAL) — SKILL.md contains no absolute paths
    (`/Users/...`) and no plugin-rooted paths (`domain-teams/skills/
    ...`). Standards / protocols / checklists / rubrics files are
    intentionally NOT scanned because they legitimately reference
    example paths inside markdown code blocks, inline backticks,
    anti-pattern documentation, and primary source citations to
    repo SSOT files outside the plugin (such as
    `/Users/.../monkey-skills/CLAUDE.md`).
  - **CHK-SKL-012** (FATAL) — directory layout: required
    subdirectories `standards/`, `protocols/`, `checklists/`,
    `rubrics/` plus the optional `research/` per v4.7.0; any other
    subdirectory is FATAL; if `research/` exists, every file inside
    must match `grounding-v{X.Y.Z}.md` per v4.7.0 file naming.
    Router skills are exempt from the required-subdirectory check.
    `.DS_Store`, `._*`, and `Thumbs.db` are ignored as filesystem
    noise so local runs match what GitHub Actions sees on a fresh
    checkout.

- `.github/workflows/skill-structure.yml` — GitHub Actions workflow
  with two independent jobs:

  - `structure` — runs `scripts/check-skill-structure.py
    domain-teams` on every push to main and every PR targeting main.
    Uses `actions/setup-python@v5` with Python 3.11.
  - `conventional-commits` — runs only on `pull_request` events.
    Walks `git log {base}..{head}` for the PR range and validates
    every non-merge commit's subject against a relaxed Conventional
    Commits regex. Enforces the **load-bearing** parts of skill-team
    v4.8.1 `commit-convention.md` §Commit Message Format: type ∈
    {refactor, feat, fix, chore, docs}, scope = kebab-case
    identifier, colon-space-subject, no trailing period. Does NOT
    enforce "lowercase first letter" because real subjects
    legitimately start with acronyms (CHK-CMT-001, OWASP, JSON,
    API). The optional version/position suffix is permissive to
    match observed precedent: `(vX.Y.Z N/3)` for 3-commit splits,
    `(vX.Y.Z N/2)` for 2-commit splits, `(vX.Y.Z gate-feedback)`
    for follow-up patches.

### Changed

- `.gitignore` — added `.DS_Store`, `**/.DS_Store`, `._*`, and
  `Thumbs.db` patterns. None of these were tracked in git, but they
  exist on local macOS filesystems and would otherwise be flagged by
  the new `scripts/check-skill-structure.py` CHK-SKL-012 check
  during local runs (the script also explicitly skips them as noise
  for parity with what CI sees on a fresh checkout).

### Verification

Local dry-run on the current branch (after the script bug fix
iterations) returns:

```
check-skill-structure: scanned 9 skills under
    /Users/kouko/GitHub/monkey-skills/domain-teams/skills
PASS  code-team
PASS  design-team
PASS  devops-team
PASS  docs-team
PASS  planning-team
PASS  qa-team
PASS  research-team
PASS  skill-team
PASS  using-domain-teams

All 9 skills PASS
```

Deliberate-breakage test (inject a non-existent path into qa-team's
launch template, run script, restore) confirms the CHK-SKL-005 path
existence check correctly fails on injected drift and exits 1.
Word count distribution across non-router skills (with the v4.6.1
hyphen/slash tokenization rule + CJK token exclusion):
code-team 139, devops-team 82, skill-team 78, docs-team 67, qa-team
51, planning-team 46, design-team 45, research-team 43; router
`using-domain-teams` 31 (exempt). All non-router skills are above
the 40-word floor.

### Meta

This is the **first CI infrastructure** for the repo. Future
candidates for additional checks (deferred):

- Per-gate-file linting (e.g. checklist item ID format `CHK-XXX-NNN`)
- Workflow phase table dependency graph (verify every Phase row's
  Protocol/Input/Output cell is populated)
- skill-team's full dogfood gate suite (would require running
  evaluator agents inside CI, which requires Claude Code CI
  integration that does not yet exist)
- Cross-plugin scope expansion (validate `obsidian` and
  `philosophers-toolkit` plugins under their own conventions)

PATCH bump rationale per v4.8.1 `commit-convention.md` §Semver:
this branch adds files (CI script + workflow + .gitignore patterns)
but none of those files are read by worker or evaluator agents at
runtime. The distinguishing rule classifies this as PATCH, not
MINOR. Per the v4.8.1 CHK-CMT-003 refinement, modify-only PATCH
bumps may also ship as a single-commit chore without splitting into
the 3-commit pattern that grounding refactors use; v4.8.2 takes
that single-commit path because the work is naturally cohesive
(script + workflow + .gitignore + version bump are all the same
"add CI" change).

## [4.8.1] — 2026-04-11

Skill-team research-note convention cleanup patch — consolidates
seven related fixes surfaced by the v4.8.0 design-team dogfood
(Skill Coherence and Commit Split gates) plus a second-pass dogfood
on this very branch. All changes are modify-only (no new files, no
new grounded content). First PATCH bump codified under the refined
CHK-CMT-005 three-way distinction between MINOR (additive) and
PATCH (modify-only).

**Why seven fixes in one patch**: the initial Track B scope
identified two literal-vs-intent gaps (CHK-CMT-001 and
skill-md-structure.md §Research Subdirectory Convention). Running
skill-team's own dogfood against a first-pass fix surfaced four
additional drifts in commit-convention.md, grounding-principle.md,
and grounding-research.md — all caused by the same root issue:
the research-note convention landed in v4.7.0 but its downstream
references in commit-convention.md, grounding-principle.md,
grounding-research.md, and skill-completeness-checklist.md were
never updated. Re-running dogfood after the second-pass fix
surfaced one more instance of the same drift in
skill-completeness-checklist.md CHK-SKL-012. Fixing only some
instances would have left main with the same root issue partially
unfixed, so the scope was expanded twice to land all seven fixes
as a single consistent cleanup.

Honest disclosure: this branch went through THREE commit-set
generations:
- Generation 1 (3 fixes): commits 0a10ac4 + 45ae04c + 9d0c050.
  Dogfood surfaced 4 more drifts.
- Generation 2 (6 fixes): soft-reset + commits 8876323 + 5d1c782
  + b40eb7b. Re-dogfood surfaced 1 more drift.
- Generation 3 (7 fixes, FINAL): soft-reset of commits 2/3 + 3/3
  only (commit 1/3 8876323 preserved) + commits e93284a + new 3/3.

This is the v4.6.1 self-bootstrap precedent extended over multiple
dogfood iterations. Each iteration is honest about what it found
and what it missed.

### Changed

#### Standards

- `skill-team/standards/skill-md-structure.md` §Research Subdirectory
  Convention — the section heading "SKILL.md does NOT reference
  research/ files" was over-broad; it was interpreted strictly to
  prohibit any mention of `research/*.md` anywhere in SKILL.md, even
  in maintainer-facing prose sections like `## Note on Global
  Context`. The original intent was narrower: prevent worker and
  evaluator agents from attempting to Read research files at runtime.
  This release rewrites the section with a runtime-dependency scope:
  - **Forbidden (structural)**: Resource Manifest entries, launch
    template `standards` arrays, `gate_file:` / `protocol:` fields,
    and cross-file references that imply runtime reads.
  - **Permitted (prose)**: rationale mentions in `## Note on Global
    Context`, `## Appendix`, commit messages, PR descriptions, and
    CHANGELOG entries, provided they do not appear in any field an
    agent launch interprets as a file path to Read.
  - Distinguishing test: "Would a worker or evaluator, following its
    launch template literally, end up calling the Read tool on this
    path?" If yes → forbidden; if no → permitted.
  - Discovery: v4.8.0 Skill Coherence gate flagged
    `design-team/SKILL.md:61` as an "out of rubric scope" observation
    because the `## Note on Global Context` section mentions
    `research/grounding-v4.8.0.md` in prose. The reference is
    legitimate rationale and should stand.

- `skill-team/standards/commit-convention.md` §Commit 1/3 — added
  optional bullet explicitly permitting a single
  `research/grounding-v{X.Y.Z}.md` in commit 1 alongside
  `standards/*.md`, per the v4.7.0 research-note convention.
  Previously the section was silent on the research note, leaving
  `commit-split-checklist.md` CHK-CMT-001 with no grounding anchor.

- `skill-team/standards/commit-convention.md` §Commit 3/3 — SKILL.md
  changes are now REQUIRED for additive MINOR bumps (where new
  structure must be wired into the discovery surface) and OPTIONAL
  for modify-only PATCH bumps (where no rewiring is needed). Also
  explicitly lists `CHANGELOG.md` as part of commit 3/3 contents
  (previously implicit).

- `skill-team/standards/commit-convention.md` §Semver table —
  rewrote the PATCH/MINOR/MAJOR rows with the distinguishing rule
  "does this branch introduce new files that worker or evaluator
  agents will Read at runtime?" Added explicit clause permitting
  3-commit PATCH splits when SKILL.md rewiring is not needed.
  Removed the old "A 3-commit refactor always bumps at least MINOR"
  line which contradicted observed precedent (v4.6.1, v4.7.1,
  v4.7.2 were all 3-commit PATCHes).

- `skill-team/standards/grounding-principle.md` §The Research
  Workflow step 4 — fixed broken cross-reference. Previously
  pointed to `file-conventions.md §Research Subdirectory
  Convention` which does not exist. Now correctly points to
  `file-conventions.md §Directory Semantics (research/ row)` AND
  `skill-md-structure.md §Research Subdirectory Convention`.

#### Gates

- `skill-team/checklists/commit-split-checklist.md` CHK-CMT-001 — the
  literal text said "ONLY changes to files under `standards/` of the
  target team", but the v4.7.0 research-note convention requires
  commit 1/3 to also include the layer-3 research note at
  `research/grounding-v{X.Y.Z}.md`. The v4.8.0 dogfood evaluator had
  to manually reconcile the literal text against
  `standards/grounding-principle.md` §The Research Workflow step 4
  and `standards/file-conventions.md` §Directory Semantics.
  CHK-CMT-001 now explicitly allows the research note alongside
  `standards/` in commit 1/3.

- `skill-team/checklists/commit-split-checklist.md` CHK-CMT-003 —
  previously said "contains SKILL.md changes AND a version bump",
  forcing every 3-commit branch to modify SKILL.md even when there
  was nothing to rewire. Now distinguishes by bump level: REQUIRED
  for additive MINOR bumps, OPTIONAL for modify-only PATCH bumps.
  Must always contain plugin.json bump AND CHANGELOG entry. Without
  this relaxation, the v4.8.1 PATCH itself would FAIL_FATAL its own
  dogfood because commit 3/3 only touches plugin.json + CHANGELOG.

- `skill-team/checklists/commit-split-checklist.md` CHK-CMT-005 — the
  literal text said "PATCH-only bumps are rejected for 3-commit
  splits", forcing every 3-commit branch to be MINOR. Observed
  precedent contradicts this: v4.6.1, v4.7.1, and v4.7.2 were all
  3-commit PATCHes for skill-team convention fixes. CHK-CMT-005 now
  defines a three-way distinction:
  - **MINOR bump** — additive work that introduces new grounded
    content or new convention infrastructure (grounding refactors,
    brand-new teams, new standards / protocols / gates, research-note
    infrastructure, backfilled research files). Example precedents:
    v4.2.0, v4.7.0, v4.8.0.
  - **PATCH bump** — modify-only skill-team convention clarification,
    policy fix, or meta-improvement that does not introduce new files
    or new grounded content. Example precedents: v4.6.1, v4.7.1,
    v4.7.2, and this release (v4.8.1).
  - **MAJOR bump** — requires explicit authorization in the PR
    description; never applied automatically.
  - Distinguishing rule: "Does this branch introduce new files that
    will be read by worker or evaluator agents at runtime?" Yes →
    MINOR. No (only modifies existing runtime files) → PATCH.

- `skill-team/checklists/skill-completeness-checklist.md` CHK-SKL-012
  — fixed broken cross-reference. Previously pointed to
  `standards/file-conventions.md §Research Subdirectory Convention`
  which does not exist (file-conventions.md has §Directory Semantics
  with a research/ row but no top-level §Research Subdirectory
  Convention heading). Now points correctly to BOTH authoritative
  locations: `file-conventions.md §Directory Semantics (research/
  row)` AND `skill-md-structure.md §Research Subdirectory
  Convention`. Same drift pattern as the grounding-principle.md and
  grounding-research.md fixes — surfaced by the second-pass dogfood
  on this branch.

#### Protocols

- `skill-team/protocols/grounding-research.md` Phase 3 — fixed
  broken cross-reference. Previously pointed to
  `file-conventions.md §Directory Semantics and §Research
  Subdirectory Convention` — the second heading does not exist in
  file-conventions.md (only in skill-md-structure.md). Now points
  correctly to `file-conventions.md §Directory Semantics
  (research/ row)` AND `skill-md-structure.md §Research Subdirectory
  Convention`.

### Meta

This is the first self-applied PATCH bump under the refined
CHK-CMT-005 three-way distinction. The distinguishing rule correctly
identifies v4.8.1 as PATCH: the branch touches exactly 6 existing
runtime files (`skill-md-structure.md`, `commit-convention.md`,
`grounding-principle.md`, `commit-split-checklist.md`,
`grounding-research.md`, `skill-completeness-checklist.md`) plus
the plugin version file and this CHANGELOG. Zero new files added.

**Dogfood status**: the 3-commit branch was evaluated against the
**refined** CHK-CMT-001 / CHK-CMT-003 / CHK-CMT-005 wording it
introduces (bootstrapped self-evaluation; the gate's v4.8.1 text
defines the rule that the v4.8.1 branch passes). This is analogous
to the v4.6.1 self-patch precedent — skill-team can only dogfood
its own convention fixes against the post-fix version of the
convention.

**Three-generation scope-expansion disclosure**: this branch went
through three commit-set generations to reach the final 7-fix
scope. Each generation's dogfood surfaced additional drifts caused
by the same root issue — the v4.7.0 research-note convention was
landed but its downstream references in 5 other runtime files were
never updated.

- **Generation 1** (3 fixes, commits 0a10ac4 + 45ae04c + 9d0c050):
  fixed skill-md-structure §Research Subdirectory Convention scope
  + CHK-CMT-001 + CHK-CMT-005. Dogfood surfaced 4 more drifts:
  commit-convention.md §Commit 1/3 one-bullet-behind, commit-
  convention.md:137 direct contradiction, grounding-principle.md
  :73 broken cross-ref, grounding-research.md:67-68 broken cross-
  ref, plus CHK-CMT-003 literal-vs-intent gap.

- **Generation 2** (6 fixes, soft-reset + 8876323 + 5d1c782 +
  b40eb7b): added the 4 surfaced fixes + CHK-CMT-003. Re-dogfood
  surfaced 1 more instance of the same drift pattern in
  skill-completeness-checklist.md CHK-SKL-012.

- **Generation 3** (7 fixes, soft-reset of commits 2/3 + 3/3 only,
  commit 1/3 8876323 preserved, + e93284a + new 3/3): added the
  CHK-SKL-012 fix to commit 2/3, updated CHANGELOG and bumped
  plugin in commit 3/3. Final dogfood expected to PASS with no new
  drifts.

The pre-publication commit history was rewritten via local soft-
resets twice. None of the rewritten generations were ever pushed
to origin, so no shared history was disturbed. The narrative is
preserved in this CHANGELOG and in the v4.6.1 self-bootstrap
precedent.

## [4.8.0] — 2026-04-11

### Added

- **7 new design-team standards** (Phase 4 synthesis of Phase 2
  grounding research, `research/grounding-v4.8.0.md`):
  - `nielsen-norman-heuristics.md` (Tier 1) — Jakob Nielsen 10
    Usability Heuristics (1994, re-published 2024) + Donald Norman
    2013 *The Design of Everyday Things* affordance / signifiers /
    mappings / 7-stage action cycle. Primary anchor for interaction
    quality review.
  - `garrett-elements-of-ux.md` (Tier 1) — Jesse James Garrett 2010
    *The Elements of User Experience* 5-plane model (strategy /
    scope / structure / skeleton / surface). Primary anchor for UX
    structural reasoning.
  - `platform-conventions.md` (Tier 2) — Apple Human Interface
    Guidelines / Google Material Design 3 / Microsoft Fluent 2
    platform conventions and component semantics. Tier 2 because LLM
    parametric knowledge mixes up version-specific component states.
  - `ooui-and-object-modeling.md` (Tier 2) — Sophia Prater 2015/2016
    OOUX / ORCA + 上野学 2020 *オブジェクト指向 UI デザイン*
    co-canonical object modeling for UI. Tier 2 because method
    details drift in LLM recall.
  - `kansei-engineering-and-sd.md` (Tier 3) — 長町三生 1989
    *感性工学のおはなし* kansei word collection → SD scale →
    factor analysis → design element mapping methodology.
    Fully self-contained 173-line body per Tier 3 self-containment
    test (no parallel Anglo framework; LLM cold-query hallucinates).
  - `japanese-design-aesthetics.md` (Tier 3) — 原研哉 2003
    *デザインのデザイン* and 2008 *白* (引き算 / 白 / 佇まい) +
    深澤直人 2005 *デザインの輪郭* (無意識のデザイン / Without
    Thought). Fully self-contained 199-line body.
  - `ux-temporal-and-quality-models.md` (Tier 3) — 安藤昌也 2016
    *UX デザインの教科書* 4 temporal UX phases (anticipated /
    momentary / episodic / cumulative, as JP introducer of Roto et
    al. 2011 UX White Paper) + 黒須正明 2020 *UX 原論* Ch.11 §11.3
    4 Quality Regions 2×2 matrix. Fully self-contained 214-line body
    including Roto 2011 upstream anchor citation.

- **1 upgraded standard**: `wcag-baseline.md` (Tier 2) — explicit
  Primary Sources section, Success Criteria numbering table, and
  SC 2.5.8 (24×24 AA) / SC 2.5.5 (44×44 AAA) touch target
  disambiguation per WCAG 2.2 (recommendation 2024-12-12).

- `design-team/research/grounding-v4.8.0.md` — 1065-line Phase 2
  grounding research audit trail. Documents 24 primary sources
  independently verified (Norman 2013, Nielsen 1994/2024, WCAG 2.2,
  Garrett 2010, Verganti 2009, Prater 2015/2016, 長町 1989, 深澤
  2005, 原研哉 2003/2008, 安藤 2016, 黒須 2020, 上野 2020, Roto et
  al. 2011, Apple HIG, Material 3, Fluent 2, and others). Captures
  the 12 implicit JP methodology anchors surfaced during research
  that justified FULL JP integration strategy.

- **design-team SKILL.md new sections**:
  - `## Note on Global Context` — declares FULL JP integration
    strategy (2nd team after qa-team v4.2.0). Documents that 4 of 8
    standards ground on JP primary sources as load-bearing SSOT, not
    preamble decoration. Comparison table across all 5 grounded
    teams and their JP strategies.
  - `## When NOT to Use` — explicit delegations to code-team,
    qa-team, devops-team, docs-team, research-team, planning-team,
    and skill-team.
  - `## Worker BLOCKED Handling` — standard BLOCKED handling pattern
    (do NOT proceed to gates, present reason, wait for user input).
  - Worker launch template — 8-standard array in
    `## Agent Launch Protocol`. design-team previously had only an
    evaluator launch template.
  - Tier annotations — every entry in the Resource Manifest standards
    list is now prefixed with its tier (T1 × 2: nielsen-norman,
    garrett; T2 × 3: wcag, platform-conventions, ooui; T3 × 3:
    kansei, japanese-aesthetics, ux-temporal).

### Changed

- **design-team SKILL.md persona** — new "anchored on eleven primary
  sources" clause in prose form: Donald Norman 2013, Jakob Nielsen
  1994/2024, W3C WCAG 2.2 2024-12-12, Jesse James Garrett 2010,
  Roberto Verganti 2009, Sophia Prater 2015/2016, 長町三生 1989,
  深澤直人 2005, 原研哉 2003/2008, 安藤昌也 2016, 黒須正明 2020,
  上野学 2020. Follows the code-team v4.6.0 persona shape.

- **4 protocols now cite primary sources**:
  - `protocols/design-brainstorming.md` — Norman 2013 action cycle +
    Verganti 2009 meaning innovation framing
  - `protocols/ui-interaction.md` — Nielsen 10 heuristics + WCAG 2.2
    SC references + Apple HIG / Material 3 / Fluent 2 platform
    conventions
  - `protocols/ux-strategy.md` — Garrett 2010 5-plane model + 安藤
    2016 4 temporal phases + 黒須 2020 4 Quality Regions + 長町 1989
    感性工学 + OOUX/OOUI co-canonical
  - `protocols/visual-design.md` — 原研哉 引き算 / 白 / 佇まい +
    深澤 無意識のデザイン + WCAG 2.2 contrast SC

- **4 gates now cite primary sources**:
  - `checklists/a11y-checklist.md` — each CHK-A11Y item annotated
    with its WCAG 2.2 Success Criterion number + level (A / AA / AAA).
    Touch target correction: SC 2.5.8 = 24×24 CSS px AA (NEW in
    WCAG 2.2); SC 2.5.5 = 44×44 CSS px AAA. The previous bare
    "44×44 minimum" claim was a conflation of the AA and AAA targets.
  - `rubrics/ui-interaction-gate.md` — Nielsen 10 heuristics +
    Norman 2013 + platform conventions citations
  - `rubrics/ux-strategy-gate.md` — **3 critical attribution
    corrections landed**:
    - "3D Quality" (which does not exist as a canonical model in any
      primary source) → corrected to 黒須正明 2020 *UX 原論* Ch.11
      §11.3 **4 Quality Regions** (objective / subjective ×
      designer / user 2×2 matrix).
    - 意味のイノベーション (meaning innovation) misattributed to
      黒須 → corrected to **Roberto Verganti 2009
      *Design-Driven Innovation*** (Harvard Business Review Press).
      黒須 2020 does NOT treat meaning innovation; Verganti does.
    - 4 temporal UX dimensions (anticipated / momentary / episodic /
      cumulative) previously floating without citation → grounded in
      **Roto, Law, Vermeeren, Hoonhout eds. 2011** UX White Paper
      (upstream Anglo source) + 安藤昌也 2016 §2.2.4 (JP introducer).
  - `rubrics/visual-gate.md` — **5 anti-pattern citations removed**
    and replaced with primary sources. The removed citations (J-SEMS,
    AIIT, KOGEI STANDARD, studio-tabi, Wikipedia, btrax blog) were
    secondary / blog / marketing sources that should never have
    been used as normative references in a grounded gate. Replaced
    with 原研哉 2003/2008, 深澤 2005 (for aesthetic vocabulary) and
    Norman 2013, Nielsen 1994/2024 (for usability dimensions).

- **MAY gate table format fixed**: 2-column `Gate | File` →
  3-column `Gate | Trigger | File` per
  `skill-team/standards/skill-md-structure.md` §Quality Gates
  Sub-Section Rules. Trigger: "Visual design audit requested, or
  visual design review needed for production PR".

- **Behavioral Rules and Agents sections promoted** from nested
  `### Behavioral Rules` / `### Agents` (under Resource Manifest) to
  top-level `## Behavioral Rules` / `## Agents`. Aligns design-team
  with qa-team v4.2.0 and code-team v4.6.0 precedent where these
  sections are top-level.

- **design-team Resource Manifest expanded** from 1 standard
  (`wcag-baseline.md` only) to all 8 standards with tier annotations.
  Worker and evaluator launch templates updated with the 8-standard
  array.

### JP integration decision

design-team v4.8.0 is the **second team after qa-team v4.2.0 to
declare FULL JP integration** (per
`skill-team/standards/grounding-principle.md` Japanese Integration
Strategy). 4 of 8 standards ground on JP primary sources as
load-bearing structural SSOT (not preamble decoration):

- `kansei-engineering-and-sd.md` (Tier 3) — 長町 1989 感性工学
- `japanese-design-aesthetics.md` (Tier 3) — 原研哉 + 深澤
- `ux-temporal-and-quality-models.md` (Tier 3) — 安藤 + 黒須
- `ooui-and-object-modeling.md` (Tier 2) — 上野 2020 co-canonical
  with Prater

**Rationale**: Phase 2 research (`research/grounding-v4.8.0.md`)
surfaced 12 implicit JP methodology anchors already functioning as
structural SSOT in existing design-team protocols and rubrics.
Making the grounding formal just aligns the standards layer with
what the protocols already assumed. Contrast with code-team (preamble
integration — no parallel JP code-craft canon) and devops-team (no
overlay — SRE / DORA / 12-Factor are Anglo-only).

### v4.7.2 policy compliance (first real application)

design-team v4.8.0 is the **first team grounded under the v4.7.2
tier classification + body self-containment + ISBN removal policy**.
Compliance highlights:

- **All 8 standards declare `tier:` in frontmatter** (T1 × 2, T2 × 3,
  T3 × 3) per `skill-team/standards/grounding-principle.md`
  §3-Tier Parametric Classification.
- **Tier 3 files have fully self-contained bodies** per the
  self-containment test: kansei-engineering-and-sd.md 173 lines,
  japanese-design-aesthetics.md 199 lines, ux-temporal-and-quality-
  models.md 214 lines. Each Tier 3 body can be acted on without
  relying on citation-triggered parametric recall — critical
  because cold-query hallucinates on 黒須 4-quality regions, 長町
  感性工学, and 深澤 無意識のデザイン.
- **Zero ISBN strings in any Primary Sources bullet** per v4.7.2
  per-source minimum field list (Author / Year / Title / URL if
  web-accessible / one-line rationale; ISBN demoted to layer 3
  research note).
- **Critical Attribution Corrections consolidated** into 4 dedicated
  sections (in wcag-baseline.md, kansei-engineering-and-sd.md,
  japanese-design-aesthetics.md, and ux-temporal-and-quality-
  models.md) per the Compact+Admonitions rule — not scattered as
  inline Admonition blocks.

### design-team v4.8.0 achievement summary

- **5th grounded team** (after qa / docs / devops / code)
- **2nd team with FULL JP integration** (after qa-team v4.2.0)
- **1st team grounded under v4.7.2 policy** (tier classification +
  body self-containment + ISBN removal)
- 8 standards with tier frontmatter + Compact+Admonitions style +
  zero ISBN in Primary Sources
- 3 critical attribution corrections landed in ux-strategy-gate.md
  (3D Quality → 4 Quality Regions, 意味性 → Verganti 2009,
  Roto 2011 as upstream anchor for 安藤 2016)
- 5 anti-pattern secondary-source citations removed from
  visual-gate.md

## [4.7.2] — 2026-04-11

### Changed

- `skill-team/standards/grounding-principle.md` §Citation Density Rule
  — three architectural additions:
  - **New §3-Tier Parametric Classification subsection**. Standards
    files now declare a `tier: 1|2|3` in their frontmatter based on
    the parametric strength of the knowledge they document:
    - **Tier 1 (high parametric)**: LLM training data covers the
      topic accurately; body can be anchor-only. Examples: Clean
      Code, SOLID, Nielsen 10 heuristics, Fowler Bad Smells.
    - **Tier 2 (medium parametric)**: LLM knows the framework but
      confuses details, version numbers, or enum values; body
      supplies the specific details. Examples: WCAG 2.2 SC numbers,
      OWASP ASVS v5.0.0 V-chapter mapping, Material 3 component
      states enumeration.
    - **Tier 3 (low parametric)**: LLM training data is sparse or
      absent; cold-query hallucinates; body must be fully
      self-contained. Examples: 黒須 2020 4-quality regions, 安藤
      2016 4 temporal UX phases, 長町 1989 感性工学 methodology,
      徳丸本 Ch.6 multi-byte encoding security, わびさび / 間 /
      佇まい design aesthetic concepts, internal company conventions.
    The classification comes with a "cold-query decision rule"
    (`claude -p "What is X?"` with no context — if it hallucinates,
    it's Tier 3) and a worked example table mapping design-team
    v4.8.0's 8 standards to their respective tiers.
  - **New §Body Self-Containment Rule subsection**. Codifies that
    Primary Sources is **anchor + audit trail**, NOT knowledge
    delivery. The body of each standards file must be self-contained
    to tier-appropriate depth such that a worker/evaluator reading
    only the body can act on the rule without relying on
    citation-triggered parametric recall. Ships with the
    "self-containment test" (mentally remove Primary Sources and ask
    if the body still suffices) and per-tier body writing examples.
  - **Per-source minimum required fields: ISBN removed**. The 5-field
    minimum is now **Author / Year / Title / URL (if web-accessible) /
    one-line load-bearing rationale**. ISBN is demoted to the
    "explicitly OPTIONAL / belongs in layer 3" list alongside DOIs,
    translator metadata, supplementary bibliography, subchapter
    titles, and publisher verbosity. Rationale: **ISBN has near-zero
    LLM semantic value**. LLM training data does not index books by
    ISBN; the anchoring activation that makes "Martin 2008 *Clean
    Code*" light up the right parametric knowledge comes from the
    author + year + title triple, not the ISBN string. ISBN is
    valuable only to human reviewers doing library/catalog lookup
    and as anti-drift metadata — both use cases belong in layer 3
    (`research/grounding-v{X.Y.Z}.md`) and the CHANGELOG.
  - **Anti-patterns expanded**: 4 new items (ISBN padding,
    miscalibrated tier, Tier-1-defaulting without cold-query test,
    Tier 3 body under-specification).
  - **Honesty disclosure expanded** to document the 2-patch evolution
    (v4.7.1 Compact+Admonitions → v4.7.2 tier + body self-containment
    + ISBN demotion). Credits the user's question "does ISBN help LLMs
    understand?" as the catalyst.

- `skill-team/protocols/grounding-research.md` §Phase 4 Standards
  Synthesis — integrated tier selection as a mandatory step:
  - Per-cluster template gained `Tier` and `Body outline` fields;
    estimated length replaced with tier-dependent ranges (T1 60-90,
    T2 100-150, T3 150-250 lines).
  - New §Tier Selection subsection with cold-query decision rule,
    heuristics (non-Anglo canon → T3, post-2024 standards → T2,
    mainstream Anglo canon → T1, internal conventions → always T3),
    and "default to higher tier when in doubt" rule.
  - §Citation style updated to list 4 mandatory elements: frontmatter
    `tier`, compact Primary Sources (no ISBN), tier-calibrated body,
    optional Critical Attribution Corrections.
  - Minimal template for Primary Sources: ISBN slot removed.
  - New §Body Self-Containment by tier subsection with per-tier body
    writing checklists and concrete target exemplars from design-team
    v4.8.0 (Tier 1 target: nielsen-norman-heuristics.md; Tier 2
    target: wcag-baseline.md with SC number table; Tier 3 target:
    ux-temporal-and-quality-models.md with full 2×2 matrices).
  - Phase 4 anti-patterns expanded (ISBN padding, missing tier
    declaration, Tier-1-defaulting without cold-query test, Tier 3
    body too thin).

### Why this change

Exposed by user review of the v4.7.1 Compact+Admonitions policy. The
user asked two questions in sequence:

1. **"Does ISBN actually help LLMs understand the content? If not,
   shouldn't it be in the research note / CHANGELOG instead of the
   standards file?"** — Analysis confirmed ISBN has near-zero LLM
   semantic value. LLM training data does not index books by ISBN;
   the anchoring activation that makes citations "work" is the
   Author+Year+Title triple, not the ISBN string. ISBN is valuable
   only to human reviewers and as anti-drift metadata, both of which
   belong in layer 3.

2. **"How should we balance '依靠模型內部知識' (relying on LLM
   parametric memory) vs 'providing independent knowledge files'?"** —
   Analysis surfaced that different topics have different parametric
   strengths. Clean Code and Nielsen 10 heuristics are massively
   represented in LLM training data (high parametric); a short anchor
   plus LLM memory is enough. 黒須 4-quality regions and 長町 感性
   工学 methodology are Japanese 専門書 with thin LLM coverage (low
   parametric); the body must be fully self-contained or the
   evaluator gate will hallucinate. The right rule is **tier-aware
   body depth**, not a single density target.

The root architectural insight documented in §Honesty disclosure:
**layer 2 (`standards/*.md`) is neither pure bibliography nor pure
knowledge delivery — it is a tier-aware runtime resource where body
depth and citation density are co-calibrated to the parametric
strength of the knowledge being documented.**

### Impact on design-team v4.8.0 (upcoming)

When design-team v4.8.0 grounding refactor restarts in Step 2, the
Phase 4 worker will read this updated policy and:
- Classify each of the 8 planned design-team standards into a tier
  using the cold-query decision rule
- Write body depth per tier (`ux-temporal-and-quality-models.md`,
  `kansei-engineering-and-sd.md`, and `japanese-design-aesthetics.md`
  are all Tier 3 and will have full self-contained bodies; the other
  5 standards will be Tier 1 or 2 with lighter bodies)
- Omit ISBN from all Primary Sources bullets
- Declare `tier:` in each standard's frontmatter
- Run the self-containment test before finalizing each file

### Known residual — grounded teams predating this rule

The 4 teams grounded before v4.7.1 (qa/docs/devops/code) and v4.7.2
(no new grounded teams between v4.7.1 and v4.7.2) are **grandfathered**.
They do NOT need to retroactively add `tier:` frontmatter or rewrite
their body depth. The Tier classification + Body Self-Containment
rules apply to **design-team v4.8.0 onward** and future grounding
refactors (research-team, planning-team, and any future re-groundings
of the precedent teams when they are next refactored). Same rationale
as v4.7.1's grandfather clause: retrofitting in a single sweep would
mix concerns and bloat the diff beyond reviewability.

## [4.7.1] — 2026-04-11

### Changed

- `skill-team/standards/grounding-principle.md` §Citation Density
  Rule (new section): codified the **Compact+Admonitions** style for
  layer 2 of the 3-layer primary-source record structure (per-
  `standards/*.md` `## Primary Sources` sections). Specifies
  minimum required per-source fields (author / year / title / ISBN
  or URL / one-line rationale), explicitly optional fields (DOIs,
  translator names, JP translation ISBNs, supplementary
  bibliography, subchapter titles, publisher verbosity — do NOT
  include unless materially helpful), and a dedicated
  `## Critical Attribution Corrections` section convention for
  anti-drift guardrails (consolidated after Primary Sources, not
  scattered as inline Admonitions in the body). Includes observed
  precedent table (code-team ~1.8%, devops-team ~2.5%, docs-team
  ~4.0%, qa-team ~7.5%, design-team target 2-4%), honesty
  disclosure explaining the trigger, and 7 new anti-patterns (DOI
  padding, translator proliferation, supplementary bibliography in
  layer 2, scattered Admonition blocks, publisher verbosity,
  subchapter padding, layer confusion).

- `skill-team/protocols/grounding-research.md` Phase 4 Standards
  Synthesis: updated per-cluster template to include a `Critical
  attribution corrections` field; expanded estimated length 60-140
  → 60-160 to accommodate optional Critical Attribution Corrections
  section. Added 3 new subsections: "Citation style for each
  standards file" (cross-reference to new §Citation Density Rule),
  "Minimal template for a Primary Sources section" (concrete markdown
  fill-in-the-blank), "Minimal template for a Critical Attribution
  Corrections section". New Phase 4 anti-patterns block forbids
  reproducing the research note in layer 2, scattered Admonitions,
  DOI/translator padding, and omission of Critical Attribution
  Corrections when the research note surfaced attribution errors.

### Why this change

Exposed by the first Commit 1/3 attempt of the design-team v4.8.0
grounding refactor (commit SHA `4a00cae` produced in-session, never
landed on main because the branch was reset before PR creation).
That commit's 8 standards files went academic-density on first pass:
each `## Primary Sources` entry included DOI strings for peer-
reviewed papers, full JP translation ISBNs with 訳者 names,
supplementary bibliography subsections, detailed subchapter titles,
publisher-imprint-format metadata, and 3 critical attribution
corrections scattered as inline `> ⚠️ Critical correction`
Admonition blocks spread across Primary Sources and body sections.

Comparison against 4 grounded precedent teams confirmed the drift:
code-team mean ~1.8% of file is Primary Sources; design-team v4.8.0
first attempt was ~3.2-3.4% but padded with ~45 lines of scattered
Admonition blocks — conflating bibliography (Reference mode), audit
trail (research note territory), and anti-drift guardrails (which
ARE load-bearing but belong in a consolidated section).

The user caught the academic drift during Commit 1/3 review and
halted Commit 2/3 launch. v4.7.1 codifies the Compact+Admonitions
policy so future grounding refactors follow it by default. The
design-team branch has been reset; the v4.8.0 refactor will restart
after v4.7.1 merges, with the Phase 4 worker reading the new policy
before producing standards.

### Known residual — grounded teams predating this rule

The 4 teams grounded before v4.7.1 (qa/docs/devops/code) were each
written with their own intuitive density, landing in a range of
1.3-8.3% per file. None of them are retroactively compliant with
the Compact+Admonitions rule. Per scope discipline, v4.7.1 does NOT
retro-apply the rule to existing grounded teams — their Primary
Sources sections stay as-is until the next refactor of each team.
The rule applies to **design-team v4.8.0 onward** and any future
grounding refactors (research-team, planning-team).

## [4.7.0] — 2026-04-11

### Added

- **Optional `research/` subdirectory convention for domain-team
  skills**. Each grounded skill may now have a
  `domain-teams/skills/{team}/research/grounding-v{X.Y.Z}.md` file
  preserving the Phase 2 grounding research artifact in-repo
  alongside the skill it grounds. This is the third layer of
  skill-team's primary-source record structure (layer 1 = SKILL.md
  persona anchor; layer 2 = per-`standards/*.md` `## Primary Sources`
  section; **layer 3 (new in-repo) = research audit trail**). See
  `skill-team/standards/file-conventions.md` §Directory Semantics and
  `skill-team/standards/skill-md-structure.md` §Research Subdirectory
  Convention for full specification.
- `skill-team/standards/file-conventions.md`: new fifth row in the
  Directory Semantics table for `research/`, marked optional, with
  explicit "NOT read by worker/evaluator at runtime" semantics. New
  subsections "Why research/ is optional" (documents grandfather
  clause for pre-v4.7.0 grounded skills) and "research/ file naming"
  (mandates `grounding-v{X.Y.Z}.md` ASCII filenames).
- `skill-team/standards/skill-md-structure.md`: new top-level
  `## Research Subdirectory Convention` section documenting (a)
  SKILL.md does NOT reference research/ files in Resource Manifest
  or launch templates, (b) research/ is maintainer-facing only,
  (c) grandfather clause, (d) Diátaxis single-quadrant exemption
  (research notes are fundamentally mixed-mode Explanation +
  Reference + ADR; cannot be split into single-quadrant docs without
  heavy overhead), (e) docs-team is an **optional** downstream
  consumer, NOT a mandatory pipeline stage for research reformatting.
- **Backfilled 3 research notes** from the maintainer's Obsidian
  vault to the repo (grandfather devops-team — see Known issues):
  - `domain-teams/skills/qa-team/research/grounding-v4.2.0.md` (201
    lines) — synthesized from the qa-team 再設計研究綜合 note;
    歐美 / 日本 / MOC companion notes are authoring workspace
    artifacts and were NOT backfilled.
  - `domain-teams/skills/docs-team/research/grounding-v4.3.0.md`
    (445 lines) — full copy of the 技術文件框架研究 note (Diátaxis,
    Google Style, Microsoft Style, Write the Docs, Standard README,
    Nygard ADR, MADR, OpenAPI 3.2.0, Vale, Google docs-rot, The
    Good Docs Project, JP 3 原則).
  - `domain-teams/skills/code-team/research/grounding-v4.6.0.md`
    (893 lines) — full copy of the code-team v4.6.0 research note
    (Clean Code, Pragmatic Programmer, SOLID, Beck TDD, Fowler
    Refactoring, Feathers Legacy Code, OWASP ASVS v5.0.0, 徳丸本
    Ch.6, 97のこと JP).
- All 3 backfilled notes include a "Backfill note" header
  documenting the migration and any wikilink normalization applied
  (Obsidian `[[X]]` → plain text with in-repo or out-of-repo
  annotation).

### Changed

- `skill-team/standards/grounding-principle.md` §The Research
  Workflow step 4: **inverted default**. Was "save to Obsidian
  vault"; now "save in-repo by default to
  `domain-teams/skills/{team}/research/grounding-v{X.Y.Z}.md`.
  Obsidian vault export is opt-in via explicit user directive."
  Multilingual trigger phrases documented (English, 日本語, 繁體中文,
  简体中文).
- `skill-team/protocols/grounding-research.md` Phase 3: renamed
  from "Obsidian Note Capture" to "Research Note Capture". Default
  path is now the in-repo research/ subdirectory. Added required
  YAML frontmatter schema (`title` / `date` / `team` /
  `refactor_version` / `tags`). Added new "Opt-in Obsidian export
  (user directive only)" subsection handling the "user asked for
  Obsidian but vault not discoverable" edge case gracefully.
- `skill-team/protocols/grounding-research.md` Phase 6: Grounding
  Plan template `Research source` field now defaults to the in-repo
  path. New `Obsidian export` field records whether opt-in export
  was requested.
- `skill-team/SKILL.md` L244 + L260 (New Skill Creation and Skill
  Redesign workflow tables): Output column "grounding plan +
  Obsidian note" → "grounding plan + in-repo research note
  (research/grounding-v{X.Y.Z}.md)". Notes column adds "Obsidian
  export is opt-in via user directive".
- `skill-team/checklists/skill-completeness-checklist.md` CHK-SKL-012:
  amended to allow an optional `research/` subdirectory without
  making it FATAL. Added a research/ file-naming sub-check (files
  MUST match `grounding-v{X.Y.Z}.md` ASCII pattern; non-conforming
  filenames are FATAL). Explicit note that absence of `research/`
  is NOT a failure.

### Known issues

- **devops-team v4.4.0 is grandfathered** without a `research/`
  file. An Obsidian vault search returned no standalone research
  note for the devops-team grounding refactor. devops-team v4.4.0
  was executed before the skill-team meta-skill (v4.5.0) existed,
  and its Phase 2 grounding research was not captured as a
  separate artifact. The grounding evidence is distributed across
  v4.4.0 commit messages, the `[4.4.0]` CHANGELOG entry, and the
  `## Primary Sources` sections of each grounded standards file
  (layers 1 and 2 of the primary-source record structure are
  complete; layer 3 does not exist historically). This is accepted
  as-is per the grandfather clause in the Research Subdirectory
  Convention. If devops-team is re-grounded in a future refactor,
  the new Phase 2 research will land in
  `domain-teams/skills/devops-team/research/grounding-v{new}.md`
  under the v4.7.0+ convention.

### Why this change

Exposed by design-team v4.8.0 refactor Phase 2 (paused in-session
before completion). skill-team's grounding-research.md Phase 3 was
writing research notes to the maintainer's Obsidian vault as the
default with repo as a fallback. All 4 previously grounded teams
(qa/docs/devops/code) therefore had their layer-3 audit trail
**only** in the maintainer's Obsidian — invisible to PR reviewers
and future maintainers. v4.7.0 inverts the default so audit trails
live in git review alongside the grounding changes they explain.
The Obsidian vault remains available as an opt-in export destination
for users who want Obsidian's graph view, backlinks, and local
search, but it is no longer the authoritative storage.

## [4.6.1] — 2026-04-11

### Changed

- `skill-team/standards/skill-md-structure.md` §Frontmatter Schema —
  lowered the `description` word-count floor from 80 to **40** words
  to match observed precedent across all grounded teams. The earlier
  80-word floor was aspirational and matched by zero existing
  SKILL.md files (measured range: 44–127 words, stabilizing around
  44–74 for teams with concise four-clause descriptions). Added an
  explicit counting rule (English prose body only; exclude YAML
  tokens, CJK suffix, punctuation, list bullets, block-quote
  markers) and a router-skill exemption clause for skills without
  worker/evaluator launch templates (e.g. `using-domain-teams`).
  Also added a **tokenization rule** making hyphenated compounds
  (`code-team`, `cross-domain`) and slash-separated compounds
  (`UX/UI`) count as separate word tokens, which resolves a 1–2
  word ambiguity at the floor boundary affecting `research-team`
  and `planning-team` descriptions. Without this rule, the same
  description could count as 38 (strict `wc -w`) or 43 (token-split)
  depending on reader interpretation — tokenization is now the
  mandated convention.
- `skill-team/checklists/skill-completeness-checklist.md` CHK-SKL-001
  — mirrored the 40-word floor, counting rule, tokenization rule,
  and router exemption from the standard. Evaluators must now
  record "router skill — exempt" in the evidence field when the
  exemption applies.
- `skill-team/standards/skill-md-structure.md` §Quality Gates
  Sub-Section Rules — added a new dedicated sub-section making the
  four gate tiers (SELF / MUST / SHOULD / MAY) structurally required
  and explicitly documenting the table format (`Gate | Trigger |
  File` for MUST/SHOULD/MAY) and empty-MAY-case convention
  (`None currently.` + optional `Future candidates: …`). Resolves
  inconsistency where some team SKILL.md files used 2-column
  `Gate | File` tables or omitted the `### MAY Gates` sub-section
  entirely.

### Fixed

- Universal frontmatter drift exposed by the code-team v4.6.0
  dogfood (PR #31). CHK-SKL-001 previously failed against every
  existing team's SKILL.md because the 80-word floor was never met
  in practice. v4.6.1 makes the standard match observed precedent
  instead of retroactively expanding every team's description to
  fit an aspirational target.

### Known issues (not addressed here)

- Several domain-team SKILL.md files use a 2-column `Gate | File`
  table in the `### MAY Gates` sub-section instead of the now-required
  3-column `Gate | Trigger | File` shape: `design-team` (line 75+),
  `planning-team` (line 79+), `research-team` (line 74+). These
  will be corrected in each team's next refactor rather than in
  this patch, per the "only modify skill-team self-consistency"
  scope discipline.

## [4.6.0] — 2026-04-11

### Added

- `code-team` grounding via primary sources (PR #31):
  - Clean Code (Martin 2008, ISBN 978-0132350884) — naming, function
    granularity, comment hierarchy
  - The Pragmatic Programmer, 20th Anniversary Edition (Hunt & Thomas
    2019, ISBN 978-0135957059) — DRY, Orthogonality, ETC, Tracer Bullets
  - SOLID principles (Martin 2000 *Design Principles and Design
    Patterns*; Martin 2017 *Clean Architecture* Part III)
  - Test-Driven Development by Example (Beck 2002, ISBN 978-0321146533)
    — canonical Red-Green-Refactor cycle (supersedes Clean Code Ch.9 as
    TDD primary)
  - Refactoring 2nd edition (Fowler 2018, ISBN 978-0134757599) —
    behavior-preserving transformation, Two Hats, Rule of Three (Don
    Roberts attribution), Bad Smells catalog
  - Working Effectively with Legacy Code (Feathers 2004, ISBN
    978-0131177055) — Seam Model, 24 dependency-breaking techniques
  - OWASP Application Security Verification Standard v5.0.0 (released
    2025-05-30; 17 chapters V1-V17; L1 baseline tier)
  - 徳丸浩『体系的に学ぶ安全な Web アプリケーションの作り方』第 2 版
    (2018, ISBN 978-4797393163) Ch.6「文字コードとセキュリティ」—
    JP preamble for multi-byte encoding security (Shift_JIS 5C
    problem, UTF-8 over-long, multi-byte boundary XSS)
  - 和田卓人 訳『テスト駆動開発』オーム社 2017 (ISBN 978-4274217883) —
    canonical JP TDD translation + evangelism lineage
- 7 new grounded standards: `naming-and-functions.md`,
  `pragmatic-principles.md`, `solid-principles.md`, `tdd-standard.md`,
  `refactoring-standard.md`, `app-security-standard.md`,
  `character-encoding-security.md`
- `code-team/SKILL.md` new sections: `When NOT to Use` (explicit peer
  team delegation), `Note on Global Context` (JP preamble integration
  decision), MAY Gates table slot
- `security-checklist.md` CHK-SEC-005 — multi-byte character encoding
  security check (JP locale applicable, `NOT_APPLICABLE` escape valve
  for non-JP apps)
- Research note: `kouko-obsidian-vault/research/2026-04-11 code-team
  再設計研究 — Clean Code・Pragmatic・SOLID・OWASP・徳丸本.md` (893
  lines, full Phase 2 grounding research with EN + JP parallel search)

### Changed

- `code-team/SKILL.md` — persona rewrite anchoring on 8 primary sources
  (Clean Code, Pragmatic Programmer, SOLID, Beck TDD, Fowler
  Refactoring, Feathers Legacy Code, OWASP ASVS v5.0.0, 徳丸本 Ch.6)
- 5 protocols + 4 gates cite primary sources:
  - `protocols/code-brainstorming.md` — Pragmatic Programmer ETC,
    Tracer Bullets; Fowler bliki "Yagni"
  - `protocols/spec-writing.md` — arc42, IEEE 29148 acknowledgment
  - `protocols/tdd.md` — Beck 2002 Ch.1/Ch.25; Clean Code Ch.9 Three
    Laws; 和田訳 2017
  - `protocols/test-writing.md` — Meszaros *xUnit Test Patterns* 2007;
    Fowler bliki "Mocks Aren't Stubs"; Clean Code F.I.R.S.T
  - `protocols/refactoring.md` — Fowler 2018 definition + Two Hats;
    Feathers 2004 Seam Model
  - `checklists/security-checklist.md` — ASVS v5.0.0 V1/V2/V6/V7/V11/
    V13/V14/V16 chapter references; ASVS 4.0.3→5.0.0 migration note
  - `checklists/spec-consistency.md` — arc42, IEEE 29148 acknowledgment
  - `rubrics/arch-gate.md` — Martin 2000 SOLID, Martin 2017 *Clean
    Architecture*, Fowler 2018 Bad Smells; honest disclosure that
    numeric thresholds ("3x more complex", "5+ files across 3+
    modules") are house heuristics, not primary-source rules
  - `rubrics/quality-gate.md` — Clean Code Ch.2/Ch.3/Ch.9, Fowler 2018
    Bad Smells, Beck 2002, Feathers 2004; note 20-line vs 100-line
    function threshold discrepancy with Martin
- **OWASP ASVS migration from 4.0.3 to v5.0.0** — V-number
  reorganization: V5 (validation) → V2, V5.3 (injection) → V1+V2, V7.4
  (error handling) → V16, V14+V2 (secrets) → V14+V13
- `code-team/SKILL.md` Resource Manifest expanded from 1 standard
  (`code-conventions.md`) to 7 grounded standards; worker and evaluator
  launch templates updated with 7-standard array
- `code-team/SKILL.md` frontmatter description expanded from ~52 to 122
  words, adding primary-source grounding anchor and explicit peer-team
  delegation clauses (fixes CHK-SKL-001 gate feedback during dogfood)
- Bug Fix workflow Phase 3 protocol `—` placeholder → `protocols/tdd.md`
  (Green phase: minimal change to pass test)

### Removed

- `code-team/standards/code-conventions.md` — 67-line self-invented
  file superseded by the 7 new primary-source-grounded standards

### Dogfood verification

code-team v4.6.0 is the first real dogfood of the skill-team
meta-workflow (v4.5.0). All 4 gates passed before PR push:

- `checklists/skill-completeness-checklist.md` (MUST) — PASS (1 round
  of feedback on CHK-SKL-001 frontmatter word count, fixed via amend;
  re-run PASS on 12/12 items)
- `checklists/commit-split-checklist.md` (MUST) — PASS (8/8 items; 3
  disjoint commits: standards → protocols+gates → SKILL.md+bump+delete)
- `rubrics/primary-source-grounding.md` (SHOULD) — PASS (16/16 files
  GREEN across 4 dimensions; ASVS v5.0.0 V-numbers independently
  verified against official OWASP/ASVS v5.0.0 repository; zero
  fabrication)
- `rubrics/skill-coherence.md` (SHOULD) — PASS (4/4 dimensions clear:
  line budget 376, workflow completeness, router fit, duplicate-skill
  check)

### Known precedent drift (exposed by this dogfood, not addressed here)

- `skill-team/checklists/skill-completeness-checklist.md` CHK-SKL-001
  requires frontmatter description 80–200 words. qa-team (~46),
  docs-team (~57), devops-team (~67), and others fall below the
  80-word floor. Only code-team v4.6.0 is compliant (122 words).
  Resolution options: (a) lower the standard floor to ~40 words
  matching observed precedent, or (b) expand all existing team
  descriptions. To be addressed in a follow-up patch.

## [4.5.1] — 2026-04-11

### Added

- `commands/skill.md` — slash command wrapper for `skill-team`, matching the
  convention used by the other 7 teams.
- `domain-teams/CHANGELOG.md` — this file. Consolidated version history.
- `standards/agent-interface.md` §"Output Footer Convention" — documents the
  `🔄 CHECKPOINT:` footer contract that workers and evaluators enforce.

### Changed

- `standards/agent-interface.md` §"Worker BLOCKED Handling" — replaced the
  plain-text BLOCKED format description with the structured JSON format
  actually used by `agents/worker.md`. Fixed drift between standard and agent.
- `agents/worker.md` — added explicit `output_language` handling rule to match
  `standards/agent-interface.md` §"Language Handling". Previously the
  evaluator documented language protocol but the worker did not.

### Fixed

- Drift between `skill-team/standards/agent-interface.md` and `agents/worker.md`
  discovered during v4.5.0 dogfood verification follow-up. The standard is now
  an accurate description of actual agent behavior.

## [4.5.0] — 2026-04-11

### Added

- `skill-team` — new meta-skill for building and modifying domain-team skills.
  Codifies conventions accumulated across the v4.2.0 / v4.3.0 / v4.4.0 grounded
  team refactors. Scope is deliberately narrow: domain-team skills only.
  Generic Claude skill authoring remains delegated to `superpowers:writing-skills`.
  - 6 standards: `skill-md-structure`, `file-conventions`, `gate-system`,
    `grounding-principle`, `agent-interface`, `commit-convention`
  - 4 protocols: `skill-brainstorming`, `grounding-research`,
    `new-skill-creation`, `skill-redesign`
  - 2 MUST gates: `skill-completeness-checklist`, `commit-split-checklist`
  - 2 SHOULD gates: `primary-source-grounding`, `skill-coherence`
- `using-domain-teams/SKILL.md` — new row in Available Teams table and 2 new
  rows in Intent Routing for skill-team.

## [4.4.0] — 2026-04-10

### Added

- `devops-team` grounding via primary sources:
  - Google SRE Book (Beyer, Jones, Petoff, Murphy 2016)
  - DORA / Accelerate (Forsgren, Humble, Kim 2018)
  - The Twelve-Factor App (Wiggins 2011)
  - Continuous Delivery (Humble & Farley 2010) + Martin Fowler bliki
  - GitHub Actions workflow conventions + security hardening
- `protocols/monitoring-design.md` — fixes previously broken Monitoring & Observability workflow (Phase 1 had `--` protocol placeholder)
- `rubrics/twelve-factor-compliance.md` — SHOULD gate for 12-Factor audit
- New workflows: DORA Metrics Baseline, Twelve-Factor Audit

### Changed

- `devops-team/SKILL.md` — persona rewrite anchoring on SRE/DORA/12-Factor/CD
- Added `Note on Global Context` section explicitly declining Japanese overlay
  (devops has no parallel Japanese tradition — honesty over symmetry)

## [4.3.0] — 2026-04-09

### Added

- `docs-team` grounding via primary sources:
  - Diátaxis framework (Daniele Procida) — 4 quadrants
  - Google Developer Documentation Style Guide (primary style authority)
  - Microsoft Writing Style Guide (secondary voice reference)
  - JTAP 技術文書 3 原則 第 1 原則 (書き手と読み手の違いを認識する) — reader-first preamble
  - Write the Docs docs-as-code philosophy
  - Standard README, Nygard ADR / MADR, OpenAPI 3.2.0
- New workflows per Diátaxis quadrant: Write Tutorial, Write How-to, Write
  Reference, Write Explanation, Write README, Write ADR, Write API Reference,
  Documentation Audit
- 3 MUST gates: Diátaxis Mode Clarity, README Completeness, ADR Structure
- 2 SHOULD gates: Style Convention, Freshness (with `NEEDS_METADATA` verdict)

## [4.2.0] — 2026-04-08

### Added

- `qa-team` grounding via primary sources:
  - ISTQB CTFL v4.0 (vocabulary, test levels/types/techniques)
  - ISO/IEC/IEEE 29119-3 (test documentation structure, with "Stop 29119"
    note)
  - Japanese テスト観点 methodologies: VSTeP (西康晴), HAYST法 (秋山浩一),
    ゆもつよメソッド (湯本剛) — full parallel integration since JP tradition
    has equivalent standing to ISTQB
  - 品質は工程で作り込む quality philosophy
- Protocols: `test-viewpoint-extraction`, `test-strategy-selection`
- Rubric: `viewpoint-coverage` (SHOULD gate, cites ASTER テスト設計コンテスト)
- Checklist: `risk-register-depth` (MAY gate)

### Removed

- `standards/test-conventions.md` — self-invented, superseded by ISTQB grounding

## [4.1.0] — 2026-04-07

### Added

- `qa-team` skill (initial version, pre-grounding)
- `devops-team` skill (initial version, pre-grounding)
- `using-domain-teams` routing skill — the router for all domain-specialized teams

## [4.0.0] — 2026-04-06

### Changed

- **BREAKING**: skill-agent dynamic integration. Skills now pass file paths to
  agents via Resource Paths Input Contract instead of inlining file content
  into launch prompts. Agents Read files themselves using their own tools.
- `code-team` split into `code-team` + `docs-team` by gate boundary
  (Security/Architecture MUST gates stay with code-team; Documentation has
  no MUST gates and moves to docs-team)
- `agents/worker.md` and `agents/evaluator.md` — added Input Contract section,
  First Action section (Read files before working)
- `code-team/standards/code-conventions.md` — added KISS/YAGNI/DRY principles
  with full names, Comments section with Docstring/Intent/Why/Why Not pattern
  reflecting Japanese community "なぜコメント" tradition

### Removed

- `agents/context-compressor.md` — YAGNI, compressing artifacts before
  evaluator loses evidence

## [3.x] — earlier

- Checkpoint architecture: prescriptive pipeline replaced by checkpoint gates
  with flat skills and open knowledge access
- 17 specialized agents collapsed to 5 generic agents + domain knowledge files

## [2.x] — earlier

- Phase-driven refactor: 17 agents → 5 generic + domain knowledge + hybrid eval
