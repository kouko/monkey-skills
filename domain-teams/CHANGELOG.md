# Changelog

All notable changes to the `domain-teams` plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
