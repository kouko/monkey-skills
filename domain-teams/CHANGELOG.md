# Changelog

All notable changes to the `domain-teams` plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
