# Changelog

All notable changes to the `domain-teams` plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed — Codex dispatch-portability (host-neutral reference files)

Following the same class of gap found and fixed in loom-code (#496) and
loom-interface-design/loom-spec (#497), the canonical Worker/Evaluator
launch contract (`skill-team/standards/agent-interface.md`, echoed in
all 9 team `SKILL.md` files) and the parallel-fan-out hooks
(`research-team/protocols/hook-parallel-fanout.md`,
`copywriting-team/protocols/copy-ideation-advanced.md`) were already
host-neutral prose but had zero per-host reference file explaining what
that prose resolves to concretely on Claude Code vs Codex. Added new
`using-domain-teams/references/{claude-code-tools.md,codex-tools.md}`
and pointed `agent-interface.md` + `using-domain-teams/SKILL.md` at
them. Also reworded `hook-parallel-fanout.md`'s degraded-mode
capability-detection check, which hardcoded Claude-Code tool names
("no `Agent` tool available") in its own detection logic, to
host-neutral phrasing with the per-host resolution pushed to the new
reference files.

**Follow-up (same session, behavioral dogfood)**: 3 of the new/edited
cross-skill pointers used skill-relative path syntax that didn't
resolve — repointed to repo-root-relative paths. A blind auditor also
found the reworded capability-detection check asymmetric (Claude Code
branch checked only tool presence; Codex branch checked both a feature
flag and profile permission) — tightened to document the gap and
default to degraded+disclosure when recursion-permission can't be
confirmed. `copy-ideation-{parallel,advanced}.md`'s appended pointer
sentences, flagged as "bolted on" by cold-readers, were also reworded
inline.

### Fixed — code-team quality-gate dead standards reference

`code-team/rubrics/quality-gate.md` §Rules referenced a nonexistent
`standards/code-conventions.md`; repointed to
`standards/naming-and-functions.md` (the standard that actually carries the
objective style rules). Propagates to the loom-code functional copy via
`loom-code/scripts/distribute.py`.

### Changed — research-team universal onboarding + selective tagging

`research-team` undergoes a structural refactor (planned v5.6.0)
to align skill behavior with its stated purpose — helping the
reader understand content, not performing fact-verification as an
end in itself. Three coordinated changes:

1. **Universal onboarding section, form bound to protocol** — every
   worker-dispatched protocol gains a MANDATORY Step / Phase 0.5
   that produces the artifact's opening section before
   investigation begins. Form is bound to the protocol, not
   user-selectable:
   - `stack-evaluation`, `competitive-analysis` → concept-first
     (Core Concepts: per-term definition + why it exists +
     distinction from neighbors)
   - `academic-research` → scope-first (research question +
     inclusion / exclusion criteria + search method; doubles as
     PRISMA 2020 protocol-registration disclosure)
   - `market-analysis` → context-first (market boundary + time
     range + primary drivers)
   - `research-summary` and `quick-lookup` exempt (source or
     single-question framing supplies its own onboarding)
2. **Selective tagging is now universal** — `citation-standards.md`
   replaces "every claim" with "every load-bearing claim".
   Load-bearing defined by three first-pass rules (specific
   entity / contested / direct conclusion support); a fourth
   "downstream-referenced" check is performed in the Self-Critique
   sweep instead of first-pass to avoid defensive over-tagging.
   Onboarding sections are explicitly exempt from F/A/S tagging
   per a new §Onboarding-Layer Exemption.
3. **Output frontmatter discipline** — workflow-produced artifacts
   record only reader-meaningful fields (`generated_by`, `date`,
   `protocol`, `mode`, `tags`). Skill internal state
   (`skill_version`, `pipeline_version`, `output_mode`) is
   forbidden in artifact frontmatter to prevent LLM hallucination
   of unreleased version numbers.
4. **Parallel fan-out graceful degradation** — `hook-parallel-fanout.md`
   gains a §Graceful Degradation clause for runtimes where the
   worker cannot spawn nested subagents. The hook degrades to
   single-agent parallel tool-call batches (wall-clock speedup
   preserved; context isolation approximated). Mandatory
   Self-Critique disclosure marks the degraded mode explicitly so
   readers can distinguish artifacts produced by N truly-independent
   sub-workers from artifacts produced by one agent parallelising
   calls. Degradation is rejected (BLOCKED) for adversarial-
   independence tasks (red-team / blue-team).

The `Reader Onboarding` dimension is added to
`rubrics/research-quality-gate.md` (fatal on missing or
form-mismatched onboarding; warning on skeletal or wrongly-tagged
onboarding). The `protocols/hook-self-critique.md` block gains a
3-line metadata record (Protocol applied / Onboarding form /
Onboarding tagging exemption applied) prepended to the existing
3-point disclosure.

#### Files

- `research-team/standards/citation-standards.md` — "every claim"
  → "every load-bearing claim"; new §Load-Bearing Definition; new
  §Onboarding-Layer Exemption; anti-patterns updated.
- `research-team/rubrics/research-quality-gate.md` — added 5th
  dimension §Reader Onboarding; updated mode-aware triggering
  list.
- `research-team/protocols/stack-evaluation.md` — added Step 0
  concept-first onboarding; Output Format updated.
- `research-team/protocols/competitive-analysis.md` — added
  Phase 0.5 concept-first onboarding.
- `research-team/protocols/academic-research.md` — added Phase 0.5
  scope-first onboarding (PRISMA Phase-1 protocol disclosure).
- `research-team/protocols/market-analysis.md` — added Phase 0.5
  context-first onboarding.
- `research-team/protocols/hook-self-critique.md` — 3-line
  metadata record; load-bearing-by-use sweep formalised.
- `research-team/protocols/hook-parallel-fanout.md` — §Graceful
  Degradation clause for runtimes lacking nested subagent dispatch.
- `research-team/SKILL.md` — new §Output Frontmatter Discipline
  section.

#### Why now

The 2026-05-12 produced artifact comparing Coding Agent platform
terminology (Agent / Subagent / Skill / Hooks) exhibited two
failure modes attributable to v5.5.1's design, not to LLM
laziness: (a) saturation tagging — every sentence carried
【事實】 / 【分析】 / 【推測】 + confidence label, drowning
load-bearing claims in routine descriptive noise; (b) absent
concept layer — the artifact jumped directly into per-platform
implementation without first defining what Agent / Subagent /
Skill / Hooks actually mean. The v5.5.1 root causes were
`citation-standards.md`'s literal-reading "every sentence in a
deliverable" requirement (an over-execution of Kovach 2021
Ch.4, which actually requires verification of load-bearing
facts) and the absence of any rubric dimension enforcing
reader-facing onboarding.

#### Migration note

Breaking change in artifact shape for users of
`stack-evaluation` / `competitive-analysis` /
`academic-research` / `market-analysis` workflows: the first
output section is now the protocol's onboarding section.
Existing artifacts under user vaults are not retroactively
invalid — they were produced under the v5.5.1 contract.

## [5.6.0] — 2026-05-04

### Added — CHK-SKL-014 (AskUserQuestion Pattern) gate in skill-team

New checklist item enforces the **hardened AskUserQuestion pattern** for any
domain-team skill that has user-input branching steps. Closes three documented
failure modes for Anthropic's `AskUserQuestion` tool:

1. **Inline fallback** — model treats question as text instead of tool call
2. **Silent default** — model assumes "(recommended default)" and skips asking
3. **Tool unavailable** — subagent / web client / sandbox contexts have no
   AskUserQuestion; without explicit fallback, model silently defaults

The gate verifies all four hardenings are present:

1. **MUST verb** — `MUST call AskUserQuestion` (not `Use AskUserQuestion`)
2. **Args-schema example** — fenced ` ```json ` block, not prose Q&A template
3. **Fallback contract** — explicit clause for tool-unavailable environments
4. **(Recommended) marker** — first option's `label` includes `(Recommended)`

**Exemption**: skills with NO user-input branching steps are exempt
(deterministic skills, single-shot generators, skills where input is
gathered upstream).

#### Files

- `skill-team/standards/asking-user-questions.md` (NEW) — full standard
  with rationale, the Thariq canonical phrase, copy-paste mandatory-gate
  template, anti-patterns table, and industry references
- `skill-team/standards/skill-md-structure.md` — new §AskUserQuestion
  Pattern (CHK-SKL-014) section pointing to the standard
- `skill-team/checklists/skill-completeness-checklist.md` — added
  CHK-SKL-014 (FIXABLE) between CHK-SKL-013 and §Verdict Rules

#### Why now

Empirical A/B test on 2026-05-04 confirmed the soft-verb pattern
(current `Use AskUserQuestion` wording across the obsidian wiki-* skill
family) fails in subagent context — subagent assumed the "(recommended
default)" silently. The hardened version (Variant B-v2 in /tmp/wiki-trigger-test)
"held the line", surfaced trade-offs, and explicitly marked default.

Companion to dev-workflow v2.2.0's `skill-creator-advance` reference
that codifies the same pattern for non-domain-team skill authoring.

## [5.5.1] — 2026-04-29

### Context

Patch-level clarification of the existing dual-file pattern in
`skill-team/standards/file-conventions.md` §README.md and
SKILL.md Coexistence (introduced v5.3.0).

The convention now explicitly documents that **skill-internal
READMEs do not require the `docs-team` workflow**. Audit revealed
that across recent dev-workflow PRs (#161 – #165), 21 skill-internal
README files (en/ja/zh-TW × 7 skills) were authored directly without
docs-team routing — and the resulting quality was fit-for-purpose.
This patch formalizes that as the intended convention rather than
treating it as a routing oversight.

### Added (skill-team)

- `standards/file-conventions.md` §Skill-Internal README Authoring
  Discipline (new sub-subsection under §README.md and SKILL.md
  Coexistence) covering:
  - Definition of skill-internal README (`skills/<name>/README.md`
    + i18n siblings; ~280–340 lines; technical reader; tightly
    coupled to sibling SKILL.md)
  - Why exempt from docs-team (table comparing docs-team scope vs
    skill-internal README scope: project-level vs single-skill,
    multi-author vs single-author, architecture-doc vs
    implementation-overview, Diátaxis-strict vs mixed-mode, ADR /
    API ref / runbook deliverables vs none)
  - Required discipline (lighter rules): language switcher,
    English-noun-preservation, link to SKILL.md, no contradiction
    with SKILL.md, upstream attribution if derivative
  - Recommended sections (Why / How / When / Worked example /
    Relates to / Limitations / Files / License / Bottom Line)
  - When `docs-team` IS required: plugin-level README, repo-level
    README, public release READMEs, ADR / API ref / runbook,
    architecture L0-L4 docs
  - Quick decision rule
  - 5 anti-patterns

### Bump rationale

Patch (5.5.0 → 5.5.1): documentation correction / clarification.
Existing convention (dual-file pattern) is unchanged; this patch
makes the implicit "skill-internal READMEs are exempt from
docs-team" rule explicit. No new behavior; no new gate.

## [5.5.0] — 2026-04-29

### Context

`code-team` gains 4 *philosophical mindset* standards alongside the
existing 7 *mechanical* standards (Clean Code naming, Pragmatic
principles, SOLID, TDD, Refactoring, OWASP ASVS, character-encoding
security). The mindsets are design-time anchors for non-mechanical
judgment calls — "should we add this at all", "is this complexity
essential", "what's the smallest result" — that the mechanical
standards do not directly speak to.

Curation lineage: selection range and philosophical position adapted
from `softaworks/agent-toolkit/skills/reducing-entropy` (MIT, fork of
`@joshuadavidthomas/agent-skills`), but mindset bodies rewritten to
cite primary sources directly (Hickey talks, Perlis 1982 epigram,
Moseley & Marks 2006 paper, Ousterhout 2018 book, Willison 2021 blog
post chain), per `skill-team/standards/grounding-principle.md` rules
on primary-source anchoring. Full lineage and citation verification
in `domain-teams/skills/code-team/research/grounding-v5.5.0.md`.

### Added (code-team)

- `standards/mindset-data-over-abstractions.md` — Perlis Epigram #9
  ("100 functions on 1 data structure > 10 functions on 10");
  Hickey *Value of Values*; Fabian *Data-Oriented Design*; Acton
  CppCon 2014. Anchors design-time decisions to "prefer generic
  data + free functions over custom types".
- `standards/mindset-design-is-taking-apart.md` — Hickey *Simple
  Made Easy* (the *complect* / *compose* distinction); Moseley &
  Marks *Out of the Tar Pit* (essential vs accidental complexity);
  Ousterhout *A Philosophy of Software Design* 2nd ed (deep modules
  vs shallow modules); Brooks *No Silver Bullet*. Anchors design as
  *separation* not *addition*.
- `standards/mindset-expensive-to-add-later.md` (PAGNI) — Willison
  2021 PAGNI post; Plant 2021 YAGNI Exceptions; Kaplan-Moss 2021
  AppSec PAGNIs; Fowler bliki Yagni. The named dual to YAGNI for
  the small set of cases where retrofit is dramatically more
  expensive (timestamps, audit, API versioning, security
  fundamentals).
- `standards/mindset-simplicity-vs-easy.md` — Hickey *Simple Made
  Easy* (etymology: *simple* = "one fold", *easy* = "near at hand");
  Hickey *Value of Values*; Moseley & Marks *Out of the Tar Pit*.
  Anchors the discipline of choosing simple over easy when they
  disagree.
- `research/grounding-v5.5.0.md` — citation verification
  per mindset, curation lineage from upstream MIT skill, and
  skill-team `grounding-principle.md` compliance check (4/5 rules
  green; PAGNI documented as practitioner-coined neologism exception
  parallel to Hickey's "complect").

### Changed (code-team)

- `SKILL.md` — new *On-demand mindsets* sub-section under Resource
  Manifest. Mindsets are explicitly NOT in worker/evaluator default
  standards list to keep token budget bounded; they are reference
  vocabulary loaded by `protocols/code-brainstorming.md` and
  `protocols/refactoring.md` when design judgment warrants.
- `standards/refactoring-standard.md` — new *Mindsets* sub-section
  under Cross-References naming when each mindset's question
  applies during a refactor decision. Explicit "not gates" framing
  — the standard remains authoritative for refactor mechanics
  (behavior preservation, Two Hats, Bad Smells); mindsets clarify
  *which* refactor is worth doing.

### Cross-plugin downstream

`dev-workflow:complexity-critique` (added in dev-workflow v1.5.0)
references the 4 mindsets as design-time philosophical anchors via
the Cross-Plugin Delegation Contract (paths only, no content
duplication). Mindsets remain a single source of truth in code-team.

### Bump rationale

Minor (5.4.0 → 5.5.0): new mindset standards within an existing
skill, no breaking change to existing standards / protocols / gates.

## [5.4.0] — 2026-04-29

### Context

`docs-team` adopts the full Trong-Tra/agent-skills `documentation-specialist`
content (readme + architecture sub-skills, ~100% coverage; Runbook L4
intentionally excluded → devops-team domain) and gains four foundational
features that were missing:

- **Quick mode** — opt-in cost-saving execution (~46K → ~11K tokens per
  task, 4× cheaper) with hard-block list (ADR / API reference / public
  release README / architecture docs always run full mode) and a
  `/docs verify` post-hoc upgrade path
- **Pre-writing checklist** — LLM-defensive reading rules (Read Before
  You Write + Never Assume Defaults) preventing common LLM failure
  modes (license invention, package-manager mismatch, file-naming
  drift, tone whiplash, frontmatter invention)
- **Architecture documentation module** — first-class L0–L4 hierarchy
  + Mermaid 5 rules + component spec template + Architecture Doc
  Completeness MUST gate. Previously authors had to squeeze
  architecture docs into write-explanation
- **Write API Reference protocol** — extracted from write-reference as
  an OpenAPI-shaped specialization with cross-cutting-concerns-first
  ordering and consistency-pass discipline

`skill-team` gains two reusable conventions, validated by docs-team
adoption:

- **Dual-file pattern** (README.md + SKILL.md coexistence) — `SKILL.md`
  remains the LLM-discovery SSOT; `README.md` is an optional
  human-facing GitHub-rendered overview. Files MUST NOT contradict
  each other; updates land in `SKILL.md` first
- **Companion file pattern** (`{protocol-name}-examples.md`) —
  protocols with 3+ worked examples extract them to a sibling
  companion file; worker loads via existing `additional:` field; quick
  mode hard-forbids loading. 1-2 examples stay inline as quick-mode
  pattern anchor. Documented threshold + naming + worker dispatch
  rules in `file-conventions.md`

i18n convention codified as **en / ja / zh-TW** for monkey-skills
plugin (per PR #150 i18n rollout, now reflected in
`pre-writing-checklist.md` and `write-readme.md` Phase 4 internal
references). All adopting skills (docs-team, skill-team) ship 3-language
READMEs.

Token cost impact (per task, cold cache):
- Full mode README: ~54.5K → ~58.5K (+7%)
- Full mode Architecture: new workflow ~46.7K
- Quick mode README: ~11K → ~16.7K (10 new rule sections; companion
  examples deferred so quick mode does NOT pay for them)
- Other artifact types (tutorial / how-to / reference / explanation /
  ADR): unchanged

All conventions are opt-in. Skills not yet adopting README.md or
companion files remain valid; existing docs-team workflows unaffected
unless protocols cross thresholds defined by the new conventions.

### Added

**docs-team — new functionality**

- `docs-team/protocols/quick-write.md` — cost-saving inline execution
  protocol (no worker/evaluator dispatch; SELF check only). Hard-block
  list, trigger signals, No Companion Load rule, `/docs verify` upgrade
  path
- `docs-team/standards/pre-writing-checklist.md` — LLM-defensive
  pre-writing rules (Read Before You Write + Never Assume Defaults
  table covering license, package manager, file naming, tone,
  frontmatter, tech stack, badge, i18n, Diátaxis directory layout)
- `docs-team/standards/architecture-doc-structure.md` — L0–L4 document
  hierarchy, Mermaid 5 rules, 7-required-section L1 overview template,
  10-field L2 component spec template, dependency / configuration /
  security boundary conventions
- `docs-team/protocols/write-architecture.md` — workflow for system
  overviews, component specs, data flow, deployment topology, security
  models. Failure modes mandatory in L2; aspiration-vs-reality
  discipline; runbook deliberately routed to devops-team
- `docs-team/protocols/write-api-reference.md` — OpenAPI-shaped HTTP /
  GraphQL / library API reference protocol; cross-cutting concerns
  documented once; per-operation template; realistic placeholder values
  (no `foo`/`bar`)
- `docs-team/rubrics/architecture-doc-completeness.md` — MUST gate for
  architecture documentation (required-sections by level, Mermaid
  discipline, failure-modes mandatory for L2, aspiration-vs-reality
  flag)
- `docs-team/protocols/write-readme-examples.md` — companion file with
  5 worked examples (Go library, full-stack app, CLI tool, Bad → Good
  rewrite, Monorepo) adapted from Trong-Tra `readme/examples.md`
- `docs-team/protocols/write-architecture-examples.md` — companion
  file with 5 worked examples (System Context, Component Spec, Data
  Flow + Error Path, Deployment Topology, Security Model) adapted from
  Trong-Tra `architecture/examples.md`
- `docs-team/README.md` + `README.ja.md` + `README.zh-TW.md` —
  human-facing 3-language overviews (first dual-file adopter)
- `skill-team/README.md` + `README.ja.md` + `README.zh-TW.md` —
  human-facing 3-language overviews (second dual-file adopter)

**docs-team — Trong-Tra rule sections (in `write-readme.md`)**

10 prescriptive sections adapted from Trong-Tra `readme/SKILL.md`:
30-Second Test, One-Liner Formula, Quickstart Patterns A–D
(library / app / CLI / infra), Feature Communication, Configuration
Documentation, Troubleshooting Section, Badge Strategy, README Length
Guide, Language-Specific Conventions, Common Pitfalls.

**docs-team — inline worked examples (1 per protocol)**

- `write-tutorial.md`: Taskflow first-board walk-through
- `write-how-to.md`: API key rotation
- `write-reference.md`: myapp-cli command reference
- `write-explanation.md`: token bucket rate limiter rationale
- `write-adr.md`: ADR-0017 rate limiter algorithm
- `write-readme.md`: 2 examples (Go library, full-stack app) — later
  extracted to companion when total reached 5
- `write-architecture.md`: Payment Service component spec — later
  extracted to companion
- `write-api-reference.md`: Notes API operation template

### Changed

**docs-team**

- `docs-team/SKILL.md`:
  - Added "Mode Selection (Full vs Quick)" section with trigger / hard-block tables
  - Added "Write Architecture Documentation" workflow phase table
  - Added "Write API Reference" workflow phase table (extracted from
    Write Reference)
  - Added "Quick Write" and "Verify" workflow phase tables
  - MUST gates: added Architecture Doc Completeness (4 MUST total)
  - Resource Manifest: added pre-writing-checklist, architecture-doc-
    structure (7 standards total); added architecture-doc-completeness
    rubric
  - Worker launch template: added `additional:` field with Companion
    Files table
  - Per-workflow phase notes: write-readme and write-architecture rows
    annotate companion file loading
  - When to Use bullet list: added architecture documentation
- `docs-team/protocols/doc-writing-router.md`:
  - Added Phase 0 Mode Selection (full vs quick triggers + hard-block list)
  - Added ambiguity fallback (2-3 bootstrap questions before classifying
    rather than silently defaulting to Explanation)
  - Routing table: added architecture and updated API reference target
- `docs-team/protocols/write-readme.md` — extracted Examples 1+2 to
  companion; gained 10 Trong-Tra rule sections; Phase 4
  Internationalization clarifies en / ja / zh-TW monkey-skills
  convention
- `docs-team/protocols/write-architecture.md` — extracted Payment
  Service example to companion; "Origin" attribution updated
- `docs-team/protocols/quick-write.md` — added "No Companion Load" rule
  forbidding any `protocols/*-examples.md` Read in quick mode
- `docs-team/protocols/write-{tutorial,how-to,reference,explanation,adr}.md`
  — each gained "Pre-writing reference" header pointing to the new
  pre-writing-checklist standard, plus 1 inline worked example
- `docs-team/standards/pre-writing-checklist.md` Internationalization
  row clarifies en / ja / zh-TW monkey-skills convention
- `docs-team/rubrics/`: renamed `style-convention.md` → `style.md` to
  disambiguate from `standards/style-conventions.md` (8 references
  updated across SKILL.md and standards/style-conventions.md)
- `docs-team/standards/architecture-doc-structure.md` and
  `docs-team/standards/pre-writing-checklist.md` — Trong-Tra
  attribution upgraded to clickable URLs; specifies which exact
  sub-sections (`AGENTS.md` §Read Before You Write, `architecture/SKILL.md`
  §Component Spec, etc.) were sourced
- `docs-team/protocols/write-readme.md` and
  `docs-team/protocols/write-architecture.md` — Trong-Tra attribution
  added (was missing in PR 2 / PR 3); Origin lines + Sources sections
  link to canonical Trong-Tra repo URL
- `docs-team/rubrics/architecture-doc-completeness.md` — Sources
  section credits Trong-Tra `architecture/SKILL.md` §Common Pitfalls
  as gate-criteria source

**skill-team**

- `skill-team/standards/file-conventions.md`:
  - New "Top-Level Files" section codifying SKILL.md (required) +
    optional README.md + optional README.{lang}.md BCP 47 translations
  - New "README.md and SKILL.md Coexistence" subsection — files MUST
    NOT contradict; updates land in SKILL.md first; README summarizes,
    SKILL specifies
  - New "Protocol Companion Files (`*-examples.md`)" section codifying
    the 3+-examples threshold, naming convention, worker launch via
    `additional:` field, and quick-mode exclusion rule
  - Anti-patterns: `README.md inside skill directory` removed (was the
    old prohibition); replaced by "README.md duplicating SKILL.md
    content verbatim"
- `skill-team/checklists/skill-completeness-checklist.md` —
  CHK-SKL-012 (directory structure) loosened to permit README.md and
  README.{lang}.md at the top level. Any OTHER top-level file remains
  FATAL

**plugin metadata**

- `domain-teams/.claude-plugin/plugin.json` — version `5.3.0` → `5.4.0`
- `domain-teams/README.md` + `README.ja.md` + `README.zh-TW.md` —
  Version field updated `5.2.0` → `5.4.0` (was lagging by one minor
  version since 5.3.0 release)

## [5.3.0] — 2026-04-24

### Context

`research-team` adopts three deep-mode pre-writing / synthesis hooks
to close gaps identified in an industry survey of research-agent
patterns (Anthropic Multi-Agent Research, Stanford STORM, LangGraph
`open_deep_research`, OpenAI Deep Research, GPT Researcher,
Perplexity). Hooks live in `protocols/hooks/` and are lazy-loaded
only when `mode=deep` — quick mode (default, ~80% of usage)
loads zero hook content.

Implementation deliberately picks the **smallest viable version**
of each pattern (not the full reference implementation):

- **multi-perspective**: STORM's perspective-mining step only;
  omits the simulated expert-writer dialogue
- **self-critique**: LangGraph `think_tool`'s disclosure pattern
  only; omits the iterative critique→revise loop (saves an LLM pass)
- **parallel-fanout**: Anthropic Multi-Agent Research lead/worker
  fan-out without a dedicated coordinator agent (main agent
  coordinates)

Token impact: quick mode 0; deep mode ±5% (hook content offset by
parallel-fanout's isolated context with subset-only standards).

### Added

- `research-team/protocols/hooks/multi-perspective.md` — Phase 0
  stakeholder/contrarian seeding (≥3 distinct perspectives) for
  deep-mode framing diversification
- `research-team/protocols/hooks/self-critique.md` — Phase 3 worker
  self-critique block (≤200 words: weakest evidence link, ignored
  opposing evidence, confidence-evidence match) appended to deep-mode
  artifacts before evaluator review
- `research-team/protocols/hooks/parallel-fanout.md` — Phase 1
  decision rule for spawning N≤4 parallel sub-workers with isolated
  context and subset-only standards loading; integration in Phase 3
- `research-team/research/grounding-v5.3.0.md` — industry survey
  audit trail (14 reference systems compared) + design-trade-off
  rationale for each minimum-disruption hook variant

### Changed

- `research-team/SKILL.md`:
  - Resource Manifest: added Deep-mode hooks lazy-load entry
  - Compressed prose to free headroom (485 → 460 lines): Investment
    Analysis Delegation 16L→6L, Note on Global Context 10L→6L,
    persona primary-sources block tightened, Behavioral Rules dedupe
- `research-team/protocols/research.md` — added §Deep-Mode Hooks
  trigger map (central; inherited by 4 specialized protocols)
- `research-team/protocols/{academic-research,market-analysis,competitive-analysis,stack-evaluation}.md`
  — each gains 1-line pointer to research.md §Deep-Mode Hooks
- `research-team/rubrics/research-quality-gate.md` — added
  Self-Critique Honesty dimension (Fatal if absent or vacuous in
  deep mode); SHOULD gate dimensions 4 → 5
- `.claude-plugin/plugin.json` — version `5.2.0` → `5.3.0`

## [5.1.0] — 2026-04-17

### Context

ISQ (Investment Signal Quality) added to `investing-team` as a SHOULD-level
gate. ISQ evaluates the credibility of analysis conclusions — orthogonal to
existing gates which check process compliance. Adapted from Dexter Kabu JP
(raditrejp/dexter-kabu-jp `src/tools/signal/isq.ts`); original formula
preserved with investing-team-specific dimension rubrics.

### Added

- `investing-team/standards/investment-signal-quality.md` — ISQ framework:
  4 dimensions (Confidence 35%, Intensity 30%, Expectation Gap 20%,
  Timeliness 15%), signal labels (Strong ≥0.8 / Medium / Weak / Noise <0.4),
  output format, gate interaction model
- `investing-team/rubrics/signal-quality-assessment-gate.md` — SHOULD gate:
  evaluator scores each dimension 🟢/🟡/🔴, computes ISQ, produces
  informational annotation (never FAIL — Noise conclusions still delivered)

### Changed

- `investing-team/SKILL.md`:
  - SHOULD gates table: added Signal Quality (ISQ)
  - All 5 workflow gate tables: added ISQ as SHOULD gate
  - Resource Manifest: added standard + rubric paths

## [5.0.0] — 2026-04-16

### Context

`investing-team` debuts as a new domain team purpose-built for personal
investment decisions. Simultaneously, `research-team`'s Investment Analysis
workflow is retired. The four foundational investment standards (L1 macro
regime, L2 sector/industry, L3 security valuation, portfolio construction)
are migrated from `research-team` to `investing-team`. Seven new standards
cover the decision/verdict/sizing/Taiwan/data layer that was absent. This
is a MAJOR bump: any session using `research-team` for investment
Buy/Hold/Sell verdicts must now route to `investing-team`.

### Added

**`investing-team`** — new domain team (investor perspective)

- `skills/investing-team/SKILL.md` — 5 workflows, 2 MUST + 3 SHOULD + 1 MAY gates
- `skills/investing-team/standards/` (11 files):
  - Migrated from research-team: `investment-macro-regime.md`,
    `investment-sector-industry.md`, `investment-security-valuation.md`,
    `investment-portfolio-construction.md`
  - New decision layer: `investment-thesis-structure.md`,
    `decision-framework-and-verdict.md`, `position-sizing-and-risk.md`,
    `backtesting-and-robustness-discipline.md`
  - New Taiwan + data: `taiwan-equity-frameworks.md`,
    `data-sources-and-fixtures.md`
  - New strategic (investor lens): `strategic-frameworks-investor-lens.md`
- `skills/investing-team/protocols/` (5 files):
  `quick-stock-screen.md`, `deep-equity-research-memo.md`,
  `portfolio-review.md`, `macro-regime-diagnosis.md`,
  `taiwan-market-diagnosis.md`
- `skills/investing-team/checklists/` (2 MUST gates):
  `primary-source-citation-compliance.md`,
  `investment-thesis-soundness-checklist.md`
- `skills/investing-team/rubrics/` (3 SHOULD + 1 MAY gates):
  `scenario-stress-test-gate.md`, `position-sizing-rationale-gate.md`,
  `market-regime-consistency-gate.md`, `taiwan-local-rigor-gate.md`
- `skills/investing-team/research/grounding-v5.0.0.md` — primary-source
  audit trail (42 attribution corrections across 11 standards)

### Removed (Breaking Changes)

**`research-team`** — Investment Analysis workflow retired

- `skills/research-team/standards/investment-macro-regime.md` — moved to investing-team
- `skills/research-team/standards/investment-sector-industry.md` — moved to investing-team
- `skills/research-team/standards/investment-security-valuation.md` — moved to investing-team
- `skills/research-team/standards/investment-portfolio-construction.md` — moved to investing-team
- `skills/research-team/protocols/investment.md` — superseded by investing-team protocols

### Changed

- `skills/research-team/SKILL.md` — removed Investment Analysis workflow;
  added Investment Analysis Delegation section pointing to investing-team;
  updated frontmatter description, system persona, Resource Manifest, and
  Gate Protocol to remove investment-* references; retained macro regime
  substrate as analytical background knowledge for competitive research
- `skills/using-domain-teams/SKILL.md` — added `investing-team` to Available
  Teams; added 5 routing rows for investment intents; added 2 Ambiguous Cases
  (regime-only vs. regime+verdict; business strategy vs. invest memo)
- `.claude-plugin/plugin.json` — version `4.21.1` → `5.0.0`

### Migration Guide

Sessions previously routing to `research-team` for investment decisions:
- `Investment Analysis` workflow → `investing-team` `Deep Equity Research Memo`
- `台股分析` → `investing-team` `Taiwan-Specific Diagnosis`
- `regime call with verdict` → `research-team` (regime substrate) →
  `investing-team` (verdict + sizing)

`research-team` retains macro regime knowledge as analytical background.
Use `research-team` for regime calls that are context for competitive
analysis (operator view), not investment verdicts.

### Rationale

The separation standard is user role: research-team = researcher / analyst /
operator perspective; investing-team = personal investor / fund manager
perspective. Investment frameworks (IC, DCF, Kelly) were always designed for
the investor question "should I buy this asset?" — not the analyst question
"what is the market doing?" Hosting them in research-team created conceptual
confusion. Clean extraction at v5.0.0 reflects this clarity principle.

## [4.21.1] — 2026-04-15

### Context

Two corrections to the v4.21.0 Empty Invocation Fallback spec. Review
with the user found that (1) "Introduce (≤5 lines)" was too thin for
user-facing onboarding — the original goal was "主動介紹該 skill 的
運作流程與建議的使用方式", which a 5-line essence doesn't satisfy; and
(2) the trigger condition checked only current-turn prompt length,
ignoring that Claude's context often carries rich brief signal from
prior conversation / IDE selection / plan files / upstream skill
handoffs.

### Changed (skill-team standards + checklist)
- `standards/skill-md-structure.md` §Empty Invocation Fallback Rules:
  - Element 1 upgraded: "Introduce (≤5 lines)" → **"Surface
    orientation"** (structured synthesis at runtime from existing
    sections — no static content duplication)
  - Element 3 upgraded: "Sharp-input skip" → **"Sufficient-context
    skip"** — agent MUST check 5 context sources before triggering:
    (a) current prompt ≥50 chars, (b) prior conversation, (c) IDE
    context, (d) plan/memory file, (e) upstream skill handoff
  - New §Surface Orientation Format sub-section specifying the
    markdown skeleton (team/mission → What I do / What I don't do /
    How we'll work together / Prerequisites / First intake question)
  - New §Hard-gate exception clarifying copywriting-team and
    planning-team explicitly replace element 3 with "Never skip"
    plus rationale (intake surfaces elements context cannot reliably
    provide — Schwartz awareness, voice, job story, risks)

- `checklists/skill-completeness-checklist.md` CHK-SKL-013:
  - Updated to check element 1 references Surface Orientation Format
    (static ≤5-line intro no longer acceptable)
  - Updated to check element 3 covers all 5 context sources
    (current-turn-only is FAIL_FIXABLE)
  - Added hard-gate variant PASS condition (Never skip + rationale)

### Changed (9 domain-team SKILL.md)
All 9 qualifying SKILL.md §Empty Invocation Fallback sections updated:
- Trigger wording: "empty OR < 50 chars" → "empty / very sparse AND
  no context source provides brief"
- Element 1: Surface orientation reference
- Element 3: Sufficient-context skip (or "Never skip" for hard gates)
- Added optional Prerequisites inline bullets to 8 teams
  (research-team intentionally omits — scopes vary too widely)

### Unchanged
- Router-skill exemption preserved (`using-domain-teams`,
  `using-philosophers-toolkit`)
- No SKILL.md section counts changed (still 15 required sections)
- Existing brainstorming protocols unchanged

### Rationale
Triggering on "empty current prompt" alone was a common pitfall that
would create friction for returning users. Real invocations often
have rich context from prior turns or IDE state. The sufficient-
context check ensures fallback fires only on genuine cold starts.

## [4.21.0] — 2026-04-15

### Context

Users invoking a domain-team skill with empty or very sparse input
got inconsistent onboarding: copywriting-team and planning-team
enforced hard intake gates, others asked lightly, docs-team used a
router, skill-team had only agent-internal Context Discovery. This
MINOR bump standardizes user-facing onboarding behavior as a new
required SKILL.md section.

### Added (skill-team — convention)
- `standards/skill-md-structure.md`: new Required Section §6 "Empty
  Invocation Fallback" + new §Empty Invocation Fallback Rules
  subsection specifying 3 required elements (Introduce ≤5 lines /
  Route to intake / Sharp-input skip). Documents router-skill
  exemption (using-domain-teams, using-philosophers-toolkit).
- `checklists/skill-completeness-checklist.md`: new
  **CHK-SKL-013 (Empty Invocation Fallback)** [FIXABLE] enforcing
  section presence + 3 required elements + router exemption
  recording.

### Added (9 domain-team SKILL.md files)
Each SKILL.md now has a `## Empty Invocation Fallback` section that
references its existing brainstorming/routing protocol:

- code-team, design-team, devops-team, qa-team, research-team,
  skill-team → reference `protocols/{team}-brainstorming.md` with
  sharp-input skip allowed (≥50 chars concrete brief bypasses intro)
- copywriting-team, planning-team → reference intake protocol as
  hard gate (never skip — intake surfaces elements that a
  seemingly-complete brief may still lack: Schwartz awareness /
  voice / job story / risks)
- docs-team → references `protocols/doc-writing-router.md` with
  router-then-route pattern; sharp-input skip allowed when doc type
  AND target audience are already specified

### Exempt
- `using-domain-teams/SKILL.md` — router skill; its entire SKILL.md
  body IS an empty-input routing mechanism. Exemption documented in
  skill-md-structure.md §Empty Invocation Fallback Rules.

### Unchanged
- Context Discovery sections (agent-internal state mapping) preserved
  in all skills — the new fallback section is a sibling, not a
  replacement
- All existing brainstorming protocols unchanged — the section just
  surfaces them at SKILL.md level
- Token budget: each SKILL.md remains well under ~6,000 token cap
  (+8 lines per file)

### Rationale
Context Discovery is agent-internal (what to read); Empty Invocation
Fallback is user-facing (what to show/ask). Keep them separate for
clarity. Eliminates the "user invokes `/team-name` and gets
inconsistent treatment across teams" friction.

## [4.20.1] — 2026-04-15

### Context

v4.20.0 added an Anti-Pattern forbidding 🔴 極限版 use inside
copywriting-team. On review, this contradicts the VS research note
(2026-03-30) §5.2, which explicitly applies extreme-tier-style
constraints (「至少兩個選項機率 <5%」/「低機率選項須極度反直覺、甚至
荒謬」) to guerrilla marketing campaigns — a legitimate copywriting
use case. The Anti-Pattern framing was too absolute and blocked
valid applications.

### Fixed (copywriting-team)
- `standards/verbalized-sampling.md`: move "Extreme-tier (極限版)
  usage" entry from Anti-Patterns to Limitations and caveats with
  softer framing and 3 opt-in conditions:
  (a) brief explicitly demands 反直覺 / 荒誕-acceptable output
  (viral-seed hunting, anti-competition provocation, etc.);
  (b) human QA pass on every output before ship;
  (c) reduced expectations on copy-quality floor.
  Still warns against using extreme tier as default — promote only
  when Pattern A+ tail coverage is insufficient AND the brief
  genuinely tolerates 荒唐無稽 output.

### Unchanged
- Pattern A (🟢 基礎版) and Pattern A+ (🟡 進階版) defaults unchanged
- Primary Sources list unchanged
- copy-ideation-advanced.md Decision Matrix unchanged

## [4.20.0] — 2026-04-15

### Context

Verbalized Sampling (VS) implementation audit against Obsidian
research note (2026-03-30 VS 與 AI 創意多樣性) found that the core
VS mechanism is faithfully reproduced at the 🟢 基礎版 level, but
the 🟡 進階版 tier (long-tail forced sampling with probability cap)
is not exposed. This MINOR bump adds the 進階版 tier as opt-in
Pattern A+, without changing default copy behavior.

### Added (copywriting-team)
- `standards/verbalized-sampling.md` §Pattern A+ — long-tail forced-
  sampling tier (進階版) with probability cap + explicit long-tail
  directive. Direct application of Zhang et al. 2025 §5 experimental
  tail-sampling protocol. Opt-in for guerrilla / viral / counter-
  intuitive briefs only.
- `standards/verbalized-sampling.md` §Forced probability allocation
  subsection — 60/25/<5 distribution shape for briefs that need
  explicit tail coverage beyond the soft "include both high and low"
  hint. Triggered by Pattern C evaluator detecting probability skew.
- `standards/verbalized-sampling.md` Anti-Pattern re: 🔴 極限版 —
  explicit guidance to stay at Pattern A / Pattern A+ for production
  copy. Extreme-creativity tiers (contrarian persona + absurd quota
  + temp=1.2) drop copy-usability floor below production threshold.
- `protocols/copy-ideation-advanced.md` Decision Matrix row for
  guerrilla / counter-intuitive briefs routing to Base protocol +
  Pattern A+. Clarifies Pattern A+ is orthogonal to divergence-axis
  overlays (曼陀羅 / 小霜 / ULSSAS / voice).

### Unchanged
- Default copy generation continues to use Pattern A (🟢 基礎版) —
  Pattern A+ is explicitly opt-in via Decision Matrix
- Primary Sources list unchanged at 3 citations — Pattern A+ derives
  from already-cited Zhang §5; root-cause theory papers (Kirk 2023,
  Yun 2025) intentionally NOT added (token cost > benefit;
  Zhang §2 Prior Work transitively covers)

### Rationale
- Research note prescribes 3 tiers (🟢 基礎 / 🟡 進階 / 🔴 極限);
  copywriting-team now exposes the first two, with 🔴 極限版
  explicitly marked as out-of-scope via Anti-Pattern. Campaign copy
  prizes production-ready quality floor; 極限版 targets creative-
  writing extremes.

## [4.19.1] — 2026-04-15

### Context

PR #73 was merged at commit bd344a4 (Mermaid guidelines, commits 1-4);
commits 5 and 6 were not included in the merge. This PATCH restores
both lost content fix sets.

### Fixed (copywriting-team)
- `copywriting-brainstorming.md` JP/EN scaffolding cleanup:
  - Q2 ja block: Chinese terms replaced with proper Japanese
    (ロングコピー / 中尺コピー / ショートコピー / コピーレビュー)
  - Q7 ja block: Chinese terms replaced with proper Japanese
    (ロングコピー / ショートコピー / ペインポイント / 常識破り /
    ターゲット呼びかけ / 問いかけ)
  - Q7 EN block: removed stale ZH-EN pair format; using canonical EN
    only (Benefit / Fear / Disruptive / Target call-out / Interactive
    question)
  - Primary Sources + Q6 Ogilvy系 + L222-225 Short-form: updated
    stale §references to post-v4.18.4 canonical EN section names

### Fixed (skill-team — line→token budget consistency)
Completing the line→token migration established in
`skill-md-structure.md` v4.11.0:
- `SKILL.md` Resource Manifest description: "line budget" →
  "token budget"
- `standards/file-conventions.md` §Standards Splitting Discipline:
  Tier thresholds converted from lines to tokens
  (Tier 1: ~90 lines → ~2,500 tokens;
   Tier 2: ~150 lines → ~4,000 tokens;
   Tier 3: ~250 lines → ~7,000 tokens)
- `protocols/new-skill-creation.md` Phase 6: SKILL.md target
  "Line budget: aim 300–380, hard cap 500" → "Token budget:
  aim ~3,000–4,500, hard cap ~6,000"
- `rubrics/skill-coherence.md`: output-format dimension
  "Line Budget" → "Token Budget" (matches §Flag Definitions
  already named "Token Budget"); prose references to
  "line budget overflow" / "line counts" / "700 lines"
  phrased in token terms

## [4.19.0] — 2026-04-15

### Added (skill-team)
- **New standard**: `standards/mermaid-usage-guidelines.md` (Tier 2).
  Codifies when and how to use Mermaid diagrams in domain-team skills,
  based on v4.18.5 empirical findings (3 demonstrations across
  copywriting-team + skill-team).
- Standards count: 6 → 7. Resource Manifest + agent launch templates
  (worker + evaluator) updated to include the new standard.

### Scope of guidelines
- **Core finding**: Mermaid adds clarity to branching logic but does
  NOT reduce token/line count when paired with explanatory prose.
  Value is eliminating prose ambiguity, not compression.
- **Decision criterion**: use Mermaid when prose would have ≥3 branch
  conditions OR ≥4 state transitions.
- **Strong candidates**: decision trees (framework/protocol selection),
  state machines with retry loops (gate verdict handling), multi-path
  routing with failure branches (retrieval paths), phase dependencies,
  cross-cutting flows touching 3+ agents/files.
- **Avoid**: Primary Sources, Anti-Patterns with why-explanation,
  content corpora, philosophy/tradition prose, clean tables,
  single-line conditionals.
- **Integration with 4-tier gate system**: references the shared
  Verdict State Machine in `gate-system.md`; explicitly directs gate
  files NOT to duplicate verdict logic.

## [4.18.5] — 2026-04-15

### Changed
- **Mermaid demonstrations (3 files)** — replacing complex decision
  logic / routing / state machine prose with Mermaid diagrams to
  reduce ambiguity for LLM readers:
  - `copywriting-team/protocols/write-long-form-copy.md` §Phase 1
    framework selection: word-count × Schwartz-level × tone-exclusion
    decision tree → Mermaid flowchart
  - `copywriting-team/protocols/copy-neta-injection.md` §Phase A:
    source-type routing (Path A-1 WebSearch-first / Path A-2
    parametric-first / merge) + failure handling → Mermaid flowchart
  - `skill-team/standards/gate-system.md` §Verdict Semantics:
    PASS / PASS_WITH_NOTES / NEEDS_REVISION / NEEDS_METADATA
    transitions → Mermaid state diagram (shared state machine for
    all domain-team gates)

### Rationale
Proof-of-concept for Mermaid adoption in domain-teams. Empirical
finding: Mermaid adds **clarity and reduces branching ambiguity**
for decision trees / routing logic / state machines, but **does
not uniformly reduce line count** when paired with explanatory prose
— token cost stays roughly neutral. Best suited for:
- Multi-condition decision trees (framework / protocol selection)
- State machines with auto-revise loops (gate verdict handling)
- Multi-path routing with failure branches (neta retrieval paths)

Guidelines documenting when to use / avoid Mermaid will be
established in a follow-up (Plan A).

## [4.18.4] — 2026-04-15

### Changed (copywriting-team)
- **voice-and-tone.md tradition sections brought to symmetric
  philosophy level**. After v4.18.0-v4.18.3 moved the copywriter
  deep-dive ownership to `jp-copy-craft-lineage.md` and the brand-
  level taxonomy to `voice-quadrant-positioning.md`, voice-and-tone.md
  was left with an asymmetric tradition section (Anglo 28 lines at
  philosophy level, JP 34 lines at deep-dive level, ZH 0 lines).
  All three traditions now occupy ~14-28 lines at philosophy level
  only, with deep-dive delegated.
- **§JP emotional-resonance tradition trimmed** (34 → 14 lines):
  retained philosophy contrast (state-proposal vs action-prompting,
  余韻/impermanence); delegated voice-signature deep-dive (grammar
  patterns, sentence endings, character ranges) to
  `jp-copy-craft-lineage.md §糸井 / §岩崎 / §眞木準`. Fixes prior
  dangling 眞木準 reference.

### Added (copywriting-team)
- **§ZH TW copywriting tradition** (new, ~18 lines) in voice-and-tone.md:
  four distinct TW philosophical contributions with representative line
  per contribution — 對仗式日常洞察 (龔大中 全聯), 意識形態式
  aphorism (許舜英 中興百貨), 跨文化文學改寫 (李欣頻 誠品 /
  寺山修司), 策略性敘事世界觀 (葉明桂 左岸咖啡館). Cross-references
  `voice-quadrant-positioning.md §ZH Copywriting Tradition` for full
  taxonomy + micro-indicators.
- Six new cross-references in voice-and-tone.md to
  `jp-copy-craft-lineage.md` (was zero) and
  `voice-quadrant-positioning.md`, resolving the discoverability gap
  introduced by v4.18.0 architecture.

### Removed (copywriting-team)
- Primary Sources entries for 糸井重里 voice reference and 岩崎俊一
  voice reference — these are now owned by `jp-copy-craft-lineage.md`.
  Ogilvy 1963 / Ogilvy 1983 / 18F / Mailchimp remain as
  voice-and-tone.md's direct dependencies.

## [4.18.3] — 2026-04-15

### Removed (copywriting-team)
- **voice-quadrant-positioning.md §Critical Attribution Corrections
  section removed entirely**. Redundancy audit found 3 of 4 retained
  items were already disclosed inline elsewhere in the file:
  - Drift #28 (ZH heuristics) — §ZH micro-indicators section header
    and prose already self-disclose as "HEURISTICS, NOT CANONICAL
    METRICS"
  - Archetype caveat — §Primary Sources Archetype framework block
    header already says "(contested — practitioner heuristic only)"
    with Neher/Xara-Brasil/Dias critique citations listed
  - Nike Q2/Q4 disambiguation — Nike brand entry in Q2 already
    contains the inline disambiguation note
  Only Drift #25 (FCB+SFL team synthesis) was both load-bearing and
  non-redundant; relocated inline to §The Framework as a Synthesis
  disclosure adjacent to the axis definitions.
- **§Primary Sources subsections trimmed**:
  - Removed §Canonical ad corpus bibliography roster (11 entries) —
    every entry is fully annotated in per-quadrant brand entries with
    more detail (agency, year, canonical lines, voice signature).
    Redundant with body.
  - Removed §Cross-reference anchors — actual cross-refs to
    voice-and-tone.md and jp-copy-craft-lineage.md already inline in
    per-quadrant Copywriter cross-reference sections.
  - §Primary Sources now focuses on framework grounding only:
    2-axis academic sources (Vaughn + Halliday) + Archetype contested-
    framework block (Mark & Pearson + Jung + Neher + Xara-Brasil).
- Stale breadcrumbs removed: "see drift #31 for prior attribution
  correction" in JR九州 brand entry; "see drift #28" in §ZH
  micro-indicators section.
- Historical attribution corrections (drifts #26, #27, #29, #30, #31)
  already applied inline in brand corpus — audit trail preserved in
  `research/grounding-v4.18.x.md` notes.

### Rationale
Per `skill-team/standards/grounding-principle.md §Critical Attribution
Corrections` convention, the section is OPTIONAL and should be OMITTED
entirely when no guardrails are needed. After trim, only Drift #25 was
a load-bearing non-duplicated guardrail — better placed inline where
the 2-axis is introduced than in a single-item section.

### No changes to
- Brand corpus attribution (already correct inline)
- Research notes (audit trail preserved unchanged for all drifts #25-31)
- Other standards files
- SKILL.md / other protocols / gates

## [4.18.2] — 2026-04-15

### Changed (copywriting-team)
- **voice-quadrant-positioning.md restructured to Brand × Copy primary
  axis**. Per-quadrant Canonical Copy Corpus (copywriter-centric)
  replaced with Canonical Brand Corpus (brand-centric). Per-brand
  entries follow the research-informed template: voice statement +
  paired "X, never Y" voice attributes (Slack pattern) + copywriter
  metadata + dated canonical corpus + optional era narration +
  optional voice-doc source.
- **Division of labor finalized**: voice-quadrant-positioning.md now
  owns brand-level market voice positioning; `jp-copy-craft-lineage.md`
  owns copywriter deep-dive (糸井/岩崎/眞木/谷山). The two standards
  become complementary instead of overlapping — cross-reference only.
- **Removed redundant tables**: Representative practitioners + Represen-
  tative brands tables absorbed into brand corpus.

### Added (copywriting-team)
- 19 brand entries across the four quadrants:
  - Q1 (3): The Economist, Rolls-Royce (Ogilvy 1958), 報導者
  - Q2 (7): Apple, Nike, MUJI, Patagonia, 誠品書店, 中興百貨,
    左岸咖啡館
  - Q3 (6): Dove, 西武百貨店 (糸井 era), ミツカン (岩崎 2004),
    JR九州, ほぼ日, 全聯福利中心
  - Q4 (3): Shopee, Amazon, UNIQLO
- Voice-doc primary-source citations for benchmark brands:
  MUJI (Kenya Hara *Designing Design*), Patagonia (Chouinard
  *Let My People Go Surfing*), 誠品 (李欣頻《廣告副作用》+
  《誠品副作用》), 左岸咖啡館 (葉明桂《品牌的技術和藝術》),
  ほぼ日 (1101.com daily corpus).
- Research: `research/grounding-v4.18.2.md` (2-cluster audit trail —
  industry brand-voice documentation structural patterns + 8 canonical
  sustained-voice brand case studies with stability rankings).

### Fixed (copywriting-team)
- **Drift #31**: JR九州 canonical line corrected to 仲畑貴志 1994
  「愛とか、勇気とか、見えないものも乗せている。」 (TCC年鑑
  verified). Prior-assumed 「夢とか、決意とか...」 is NOT in TCC
  archive — removed.
- Apple "1984" properly attributed to Steve Hayden (Chiat\Day).
- MUJI era disambiguation: "Compact Life" (post-2010 Kenya Hara
  product line) and 2003 "Horizon / 地平線" (Bolivia/Mongolia
  campaign) are distinct campaigns within the same stable voice —
  do not conflate.

### Research findings (cumulative honesty disclosures)
- TCC年鑑 dual-axis indexing (brand + copywriter) validates this
  refactor's Brand-primary + copywriter cross-ref approach.
- Industry convention: voice eras handled as dated tags within ONE
  brand entry, NOT separate sub-entries. Apply this to Apple era
  (pre-1997 / Think Different / post-Jobs) as inline narration.
- Bilingual gap: major brand-voice references are EN-only; for
  EN/JP/ZH trilingual corpus we keep canonical copy in original
  language, add market/era tag; do NOT auto-translate.

### Drift summary (cumulative)
- #25 (v4.18.0): FCB + SFL combination = team synthesis
- #26 (v4.18.0): 廣告樂血研究院 naming correction
- #27 (v4.18.0): 詹宏志 scope exclusion
- #28 (v4.18.0): ZH micro-indicators = team heuristics
- #29 (v4.18.1): 眞木準 sole attribution for 「恋を何年」
- #30 (v4.18.1): MUJI corpus = 小池一子
- **#31 (v4.18.2)**: JR九州 line = 仲畑貴志 1994 「愛とか、勇気とか」

## [4.18.1] — 2026-04-15

### Changed (copywriting-team)
- **voice-quadrant-positioning.md rebalanced to positive examples**:
  per-quadrant structure now leads with Positive Positioning Principle,
  expands Canonical Copy Corpus with verified EN/JP/TW samples, and
  closes with Positive Application Hints. Anti-Patterns section
  trimmed from ~10 items to 3 load-bearing rules (diagonal mixing /
  Schwartz × Quadrant mismatch / quadrant-as-hard-label).
- **Language compliance fix** (per v4.13.1 policy): framework labels
  Q1–Q4 refactored from 繁中 to EN only (Q1 Authority-Reason / Q2
  Authority-Emotion / Q3 Affinity-Emotion / Q4 Affinity-Reason). ZH
  labels retained only in §ZH Copywriting Tradition as Taiwan voice-
  family canonical terminology.
- Cross-file label alignment: `voice-consistency-gate.md` Dim 5 and
  `copywriting-brainstorming.md` Q6 updated to EN quadrant labels.

### Fixed (copywriting-team)
- **Drift #29**: 「恋を何年、休んでますか。」 attribution corrected to
  眞木準 伊勢丹 1989 alone (previous dual-attribution to 眞木/岩崎
  was incorrect).
- **Drift #30**: MUJI foundational corpus (わけあって、安い /
  愛は飾らない / 自然、当然、無印 / しゃけは全身しゃけなんだ) all
  attributed to 小池一子 (AD: 田中一光).
- Ogilvy Rolls-Royce 1958 wording fix: "this new Rolls-Royce" (not
  "the new").

### Added (canonical copy samples, all WebSearch-verified)
- **EN**: Ogilvy Rolls-Royce 1958, Apple Think Different full
  manifesto, Dove Real Beauty 2004.
- **JP**: MUJI x4 (小池一子), 糸井 西武 1980-1982 x3, 岩崎
  サントリー 1985 + ミツカン 2004 + プレナス, 眞木 伊勢丹 1989.
- **TW**: 葉明桂 左岸咖啡館 strategic brief (Q1), 左岸咖啡館 ad
  series x2 (Q2, with Altenberg borrowing note), 許舜英 銀行倒閉,
  李欣頻 拋開阿莫多瓦 (誠品敦南), 龔大中 全聯潮包 2016 + 經典篇 2017.

### Excluded (unverified)
- TW: 左岸「你在左岸咖啡館」 series, 許舜英「購物冷感症」
- JP: UNIQLO / 佐藤可士和 as copywriter (reframed as art direction)

### Research
- `research/grounding-v4.18.1.md` — 3-cluster verification audit trail
  (EN / JP / TW canonical ad corpus).

## [4.18.0] — 2026-04-14

### Added (copywriting-team)
- **Voice Quadrant Positioning** (`standards/voice-quadrant-positioning.md`,
  Tier 3): 2-axis macro typology (Authority↔Affinity × Reason↔Emotion)
  with 4 quadrants (Q1 知識權威 / Q2 意識形態 / Q3 情緒共鳴 /
  Q4 直覺行動). Per-quadrant EN/ZH/JP representative practitioners and
  brands with sample sentence patterns (One-shot anchors). Complements
  the existing 4-axis micro-tuning model in voice-and-tone.md.
- **ZH copywriting tradition**: 葉明桂, 林育聖 (Q1), 許舜英, 李欣頻
  (Q2), 龔大中, 盧建彰 (Q3), 織田紀香, 廣告樂血研究院 (Q4). Fills
  gap between existing JP and EN grounding.
- **Schwartz × Quadrant routing rule**: Level 5 Unaware readers must
  enter via Q3 (Affinity + Emotion) narrative, never Q4 (direct action).
- **Voice Consistency Gate Dim 5**: Voice Quadrant Coherence with
  mechanical per-quadrant distinguishability (particle density / emoji /
  abstract-noun ratio / imperative verbs / evidence style).
- Grounding research: `research/grounding-v4.18.0.md` (3 clusters:
  FCB+Halliday, Brand Archetypes contested, ZH tradition).

### Changed (copywriting-team)
- `voice-and-tone.md`: added "Voice positioning — strategic + tactical"
  section directing users to quadrant for macro first; added quadrant
  mapping for JP masters (糸井/岩崎 → Q3; 眞木 → Q2↔Q3).
- `voice-consistency-gate.md`: Dim 4 now 3-way (JP-emotional / Anglo-
  benefit-clear / ZH-copywriting); Dim 5 added.
- `copywriting-brainstorming.md` Q6: two-step (quadrant + maestro) with
  ZH maestro options.
- `write-long-form-copy.md`: added voice quadrant corollary to Schwartz
  awareness decision.
- Standards count: 18 → 19.

### Honesty disclosures (v4.18.0)
- Drift #25: FCB + SFL combination for brand voice is team synthesis.
- Drift #26: 廣告樂血研究院 (not 樂血幫).
- Drift #27: 詹宏志 excluded (editor, not ad copywriter).
- Drift #28: ZH micro-indicators are heuristics, not published metrics.
- Brand Archetypes: contested framework (Neher 1996, Xara-Brasil 2018,
  Dias & Dias 2022); cite as practitioner heuristic only.

## [4.17.0] — 2026-04-14

### Added (copywriting-team)
- **Neta Source Taxonomy** (`standards/neta-source-taxonomy.md`, Tier 3):
  5 source categories (SNS/Meme, Classical Literature, Modern Literature,
  Famous Quotes, Contemporary Culture) with 2-axis design separating
  source types (取材類型) from transformation techniques (轉化技法).
  Grounded on Kristeva 1969 intertextuality, Genette 1982 transtextuality,
  Ben-Porat 1976 literary allusion, 本歌取り (Brower & Miner 1961 /
  藤原定家 c.1209), Bourdieu 1984 cultural capital, Peterson & Kern 1996
  omnivore thesis.
- **Path A-2 parametric-first retrieval** for literary sources (Classical
  Lit, Modern Lit, Quotes) with 3-language verification allow-list
  (JP: 青空文庫, NDL, J-STAGE; EN: Project Gutenberg, Perseus, Internet
  Archive; ZH: ctext.org, 維基文庫, 成語典).
- **Source-type preference** intake field (`neta_source_type_preference:
  all | sns-meme | literary | mixed`) in Q7.5 brainstorming.
- Grounding research: `research/grounding-v4.17.0.md` (3 clusters:
  Intertextuality, 本歌取り, Cultural Capital).

### Changed (copywriting-team)
- `neta-injection-techniques.md`: added "Source Types vs Transformation
  Techniques" clarification section; broadened "What counts as neta" to
  include literary allusion and classical quotation.
- `neta-websearch-pipeline.md`: Phase A now routes by source type
  (Path A-1 WebSearch-first for SNS/Meme vs Path A-2 parametric-first
  for literary); source-type-aware Phase D self-check.
- `neta-safety-gate.md`: Dim 3 (Cringe) gains source-type-specific
  patterns; Dim 4 renamed to "Audience Capital Match" with dual-axis
  (Bourdieu + Thornton); Dim 5 (Timeliness) becomes source-type-aware.
- `copy-neta-injection.md`: source-type routing in Phase A; softened
  evergreen restriction for literary sources.
- `copywriting-brainstorming.md` Q7.5: expanded opt-in triggers for
  literary/classical allusion; added source-type preference sub-question.
- `intake-completeness-checklist.md` CHK-CTW-INTAKE-005: added
  source-type preference sub-check.
- Standards count: 17 → 18.

## [4.16.1] — 2026-04-14

Housekeeping: add missing `commands/copywriting.md` slash command
wrapper for copywriting-team. The team has shipped (v4.12.0 onward)
but the slash command entry point was never added — meaning users
could only invoke it via the using-domain-teams router or by name,
not via the `/copywriting` shortcut available for all 8 other teams.

This is a modify-only PATCH bump (no new runtime behavior; only
adds a discoverability wrapper). Parallels v4.5.1 precedent which
backfilled the missing skill-team slash command after a similar gap.

### Added

- `commands/copywriting.md` — 5-line stub matching the convention
  used by the 8 other team commands (code/design/devops/docs/planning/
  qa/research/skill). Description: "Persuasive marketing copy with
  framework grounding. Landing pages, キャッチコピー, email, voice
  guides, audits."

### Not a breaking change

No skill content modified. v4.16.0 consumers continue to work
unchanged; this PATCH only adds the `/copywriting` slash command
entry point.

## [4.16.0] — 2026-04-14

Neta Injection Capability: formal framework for injecting pop culture
/ subculture / meme references into copy via 4 techniques identified
by English academic anchors (**Reversal** / **Substitution** /
**Subcultural Capital** / **Cross-domain Mapping**) with EN industry
vernacular (subvertising / snowclone / tribal signal / conceptual
simplification) and JP practitioner terms (逆転 / 大喜利 / 界隈消費
/ 次元降下) documented as audience-facing aliases, a Phase A-D
WebSearch-only retrieval pipeline, and a safety gate with dual hard
legal vetoes (copyright + 景表法 ステマ).

### Motivation

v4.12.0-v4.15.0 established structured copy frameworks (PASONA-family,
QUEST/PASTOR, BEAF, キャッチコピー, PREP/CREMA), but had no formal
approach for advanced rhetoric leveraging cultural compression.
Neta (ネタ) injection is an advanced technique requiring:
1. Primary-source grounding on rhetoric + humor theory
2. Up-to-date cultural context (memes expire ≈4-6 months per
   Shifman 2014)
3. Strict safety discipline (copyright + JP ステマ告示 2023)

v4.16.0 closes this gap with 2 standards + 1 protocol + 1 gate.
Consistent with monkey-skills "file-based, no external infra" principle,
the pipeline uses WebSearch JIT retrieval — no RAG, no vector DB.

### Added

2 new standards:

- `standards/neta-injection-techniques.md` (Tier 3) — 4 operations
  grounded on McQuarrie & Mick (1996) *JCR* 22(4) rhetorical figures
  (reversal + substitution) + Ott & Walter (2000) *CSMC* 17(4)
  intertextuality (parodic allusion) + Lakoff & Johnson (1980)
  conceptual metaphor (cross-domain mapping) + Thornton (1995)
  subcultural capital + humor theory anchors (Suls 1972 + Raskin
  1985 + McGraw & Warren 2010). Explicit label-vs-mechanism
  disclaimer: 繁中 labels are team synthesis; underlying mechanisms
  are canonical rhetoric.

- `standards/neta-websearch-pipeline.md` (Tier 2) — Phase A-D
  lightweight retrieval pipeline. Phase B CoT grounded on Wei et al.
  (2022) arXiv:2201.11903; ReAct interleaving grounded on Yao et al.
  (2022) arXiv:2210.03629. Meme canon: Dawkins (1976) + Shifman
  (2014) MIT Press. Phase C "Strict Replacement Rule" flagged
  transparently as team synthesis (no primary source, parallel to
  v4.15.0 action-weight disclaimer pattern). WebSearch-only (no RAG)
  positioning grounded on Agentic RAG survey (arXiv:2501.09136) +
  meme half-life data (Cambridge *Humor 2.0* Ch. 16).

1 new protocol:

- `protocols/copy-neta-injection.md` — post-production layer
  executing Phase A-D pipeline. Invoked as optional overlay after
  base-framework draft (short-form / mid-form / long-form /
  light-action). Pre-Phase verifies intake neta opt-in; BLOCKED if
  opt-in = No or if brief is >6-month evergreen (except for
  evergreen-only techniques).

1 new rubric:

- `rubrics/neta-safety-gate.md` (SHOULD, with 2 hard legal vetoes)
  — 5-dimension traffic-light scoring:
  - Dim 1 Copyright/Trademark (**HARD VETO**): 17 USC § 107 +
    Campbell v. Acuff-Rose (1994) transformative-use + Louis Vuitton
    v. Haute Diggity Dog (2007) parody dual-message + JP 著作権法
    32条 judicial doctrine (主従関係 + 明瞭区別性 per モンタージュ
    写真事件 最高裁 昭和55年)
  - Dim 2 景表法 ステマ (**HARD VETO**, JP): 消費者庁 2023-10-01
    告示 two-prong test (brand-influence + identifiability); brand
    is liable party
  - Dim 3 Cringe index (soft): documented failure precedents
    (McDonald's McDStories 2012, DiGiorno #WhyIStayed 2014, Pepsi
    Kendall Jenner 2017, ペヤング 2014); Kucuk 2019 brand-hate taxonomy
  - Dim 4 In-group match (soft): Thornton 1995 + Spence 1973 signaling
    + Bourdieu 1984
  - Dim 5 Timeliness (soft): Shifman 2014 + Cambridge *Humor 2.0*
    Ch. 16 half-life
  - Verdict rule: hard veto Red → NEEDS_REVISION regardless of soft
    dimensions (legal risk non-fungible with taste risk)

Research note:

- `research/grounding-v4.16.0.md` — 3-cluster parallel audit trail
  (neta technique academic + WebSearch pipeline + cringe/legal).

### Changed

- `SKILL.md`: intro + persona + anchors list + Delivers + When to
  Use updated. Resource Manifest expanded 15 → 17 standards. MAY
  Gates section now includes Neta Safety gate. Worker + evaluator
  launch templates include 2 new standards. New workflow variant
  "Short-Form / Long-Form with Neta Injection" documented.

### Attribution corrections (drifts #20-#24)

- #20: "Hitchon 1991 Adaptation of Lakoff and Johnson..." is informal
  title; actual cite is ACR 18:752–753 "Effects of metaphorical vs
  literal headlines"
- #21: 「次元降下 (jigen kōka)」 is a JP vernacular borrowing from
  Liu Cixin 三体 (2008) SF — usable as audience-facing JP term for
  creative/technical communities but NOT rhetoric-canon terminology;
  formal contexts should use 概念の構造化・簡略化 or cite the
  academic anchor Cross-domain Mapping (Lakoff & Johnson 1980)
- #22: McQuarrie & Mick "operations" are rhetorical figures, not
  "neta injection" — team mapping is interpretive application
- #23: "Transformative use" was articulated by Leval (1990) *Harvard
  L. Rev.* 4 years before Campbell (1994) adopted the formulation
- #24: 主従関係 + 明瞭区別性 are judicial doctrine layers on 著作権法
  32条, NOT statutory text of the article

### Commit split

Canonical 3-commit split per skill-team convention:
1. Standards foundation (2 new standards + research note bundled)
2. Protocol + gate (new protocol + new rubric)
3. SKILL.md wiring + plugin bump + CHANGELOG

### Not a breaking change

All existing workflows, gates, and standards remain intact. The 4
new files are additive; the modified SKILL.md extends Resource
Manifest and adds workflow variant. v4.15.0 consumers continue to
work unchanged.

### Roadmap completion

v4.16.0 **completes the copywriting-team roadmap** (3-version plan
from eventual-gathering-canyon.md). Team now has 17 standards + 9
protocols + 3 checklists + 3 rubrics + 4 grounding research notes.

## [4.15.0] — 2026-04-14

Light-Action Frameworks: formally recognize PREP 法 and CREMA 法 as
industry-standard templates for micro-conversion copy (email opt-in,
newsletter subscribe, download, click-through), paired with
theoretical grounding on Kaushik 2007 micro/macro conversion +
Cialdini 1984 commitment-and-consistency + Freedman-Fraser 1966
foot-in-the-door.

### Motivation

v4.14.0 `long-form-extended-frameworks.md` dropped CREMA from the
long-form framework family because:
1. No canonical primary source exists for CREMA
2. CREMA's actual scope is short-to-mid form light-action copy, not
   long-form sales letters

v4.15.0 addresses the scope mismatch by creating a dedicated
light-action framework standard. CREMA and PREP are paired
(CREMA derives from PREP) and framed parallel to BEAF's industry-
standard framework treatment — no canonical author, but documented
across multiple independent JP industry sources.

The "light-action vs heavy-action" axis itself is this team's
analytical synthesis (not documented JP canon), explicitly flagged
as such and anchored on primary-source Anglo psychology research
(Kaushik / Cialdini / Freedman-Fraser).

### Added

1 new standard:

- `standards/light-action-frameworks.md` (Tier 2) — PREP 法
  (Anglo 1980s corporate training, Toastmasters canonical) + CREMA
  法 (JP web-marketing ~2021, earliest documentation 2021-10-25
  看板のサインシティ). Paired framing as "industry-standard
  framework" parallel to BEAF. Action-weight routing matrix across
  all 8 copywriting-team frameworks (PREP / CREMA / BEAF → light;
  PASONA-family / QUEST / PASTOR → heavy). Corrects drifts #15-#19.

Research note:

- `research/grounding-v4.15.0.md` — 3-cluster parallel grounding
  audit trail (PREP origin, CREMA documentation, light-action
  taxonomy).

### Changed

- `standards/long-form-extended-frameworks.md`: CREMA anti-pattern
  refined from "do not cite" to "do not cite as long-form framework;
  see light-action-frameworks.md for proper scope." Scope-correct
  framing replaces blanket prohibition.
- `SKILL.md`: intro updated to reference PREP/CREMA + Kaushik/FITD.
  Resource Manifest expanded 14 → 15 standards. Worker/evaluator
  launch templates include new standard. New "Light-Action Copy
  Writing (PREP / CREMA)" workflow added.

### Attribution corrections (drifts #15-#19)

- #15: PREP is NOT by Brian Tracy (no primary source)
- #16: PREP is NOT McKinsey-origin (conflation with Minto 1987)
- #17: PREP is NOT Toulmin model (structurally distinct)
- #18: CREMA name does NOT derive from espresso-foam (unverified)
- #19: David Kolb did NOT invent CREMA (comparison analogy misread)

### Commit split

Canonical 3-commit split per skill-team convention (new standards
file triggers 3-commit mode via `--diff-filter=A` detection rule):
1. Standards foundation (CREATE + MODIFY)
2. Research companion (grounding-v4.15.0.md audit trail)
3. SKILL.md wiring + plugin bump + CHANGELOG

### Not a breaking change

All existing workflows, gates, and standards remain intact. The 1
new standard is additive; the 1 modified standard (long-form-
extended-frameworks) only refines anti-pattern phrasing — no
structural changes. v4.14.0 consumers continue to work unchanged.

### Roadmap update

v4.15.0 slot originally planned for Neta Injection is now
Light-Action Frameworks. Neta Injection moved to v4.16.0.

## [4.14.0] — 2026-04-14

Depth & Craft expansion: 4 new standards + 1 new protocol deepening
copywriting-team's framework coverage, JP voice analysis, instinct-
driven ideation, and SNS-era consumer behavior modeling.

### Motivation

v4.12.0 shipped with 10 standards covering the PASONA/BEAF/AIDMA
core, but deferred several knowledge-deepening items: Anglo long-form
alternatives (QUEST/PASTOR), JP voice master deep dives, 小霜和也's
instinct-driven analytical lens, and SNS-era consumer behavior models
(AISAS/SIPS/ULSSAS). v4.14.0 closes these gaps.

### Added

4 new standards:

- `standards/long-form-extended-frameworks.md` (Tier 2) — QUEST
  (Michel Fortin 2005) + PASTOR (Ray Edwards 2016). Extends PASONA-
  family routing for EN/international long-form. Corrects drifts #6
  (QUEST attribution to Makepeace), #7 (PASTOR T = dual meaning),
  #14 (PASTOR authorship). CREMA dropped — no canonical source.
- `standards/jp-copy-craft-lineage.md` (Tier 3) — 糸井重里 / 岩崎俊一
  / 眞木準 voice deep dives with voice signatures, stylistic grammar
  patterns, generational context, and LLM reproduction gap analysis
  per master. Corrects drift #8 (リゲイン misattribution).
- `standards/kosimo-instinct-analysis.md` (Tier 3) — 小霜和也's
  instinct-driven (本能駆動) analytical lens. 無意識 vs 意識 model,
  90-10 rule, 一行で関係を作れるか test, structural comparison with
  PASONA family, 義 (righteousness) ethical foundation. Corrects
  drifts #9 (pub year 2010 not 2009), #10 (process lens not taxonomy).
- `standards/sns-evolution-aisas-ulssas.md` (Tier 2) — AIDMA →
  AISAS (秋山・杉山 2004) → SIPS (佐藤 2011) → ULSSAS (飯髙 2019).
  Per-model copywriting implications + ULSSAS UGC-triggering seed
  concept. Corrects drifts #11 (year), #12 (publisher), #13 (source).

1 new protocol:

- `protocols/copy-ideation-advanced.md` — multi-method overlay on
  copy-ideation-parallel.md. Adds 小霜 instinct-lens divergence,
  ULSSAS seed criteria, voice lineage calibration, and 谷山 31
  training fragments as warm-up / quality-development tools.

Research note:

- `research/grounding-v4.14.0.md` — 5-cluster parallel grounding
  audit trail (QUEST, PASTOR, 小霜, AISAS/ULSSAS, 糸井/岩崎/眞木).

### Changed

- `SKILL.md`: intro updated to reference new frameworks and sources.
  Resource Manifest expanded 10 → 14 standards. Protocol paths add
  copy-ideation-advanced. Worker/evaluator launch templates include
  all 14 standards. New "Long-Form Extended (QUEST / PASTOR)"
  workflow added. Copy Ideation Workshop updated with advanced
  variant opt-in.

### Not a breaking change

All existing workflows, gates, and standards remain intact. The 4
new standards are additive — no existing file was modified except
SKILL.md (wiring). Existing 10 standards retain their content and
tier levels. Gate files (checklists, rubrics) are unchanged.

## [4.13.1] — 2026-04-14

Language cleanup: migrate copywriting-team from 3-language mix
(繁中 + JP + EN) to 2-language clean (JP + EN only). Modify-only
PATCH bump — no new files, only prose language migration across
existing files.

### Motivation

copywriting-team was the only domain-team using 繁中 heavily in
its meta/scaffolding layer (protocols, gates, SKILL.md body). All
other domain-teams (including FULL JP teams like qa-team and
design-team) use EN for meta layer + JP for canon content. This
inconsistency created unnecessary cognitive load with 3 language
switches within single files and added "which language should I
use?" friction for future v4.14.0/v4.15.0 authoring.

### Changed

All 23 files under `skills/copywriting-team/` migrated:

- **10 standards**: 繁中 scaffolding (framing, anti-patterns,
  comparison tables, section intros) → EN. JP canonical prose
  (PASONA stages, キャッチコピー definitions, 谷山 / 今泉 / 川喜田
  quotes) preserved. Anglo citations (Ogilvy / Cialdini / Schwartz)
  already EN and untouched.
- **7 protocols**: 繁中 → EN for Phase descriptions, Rules,
  Anti-Patterns. `copywriting-brainstorming.md` gained a new
  `## Template Rendering Rule` section + triple-language (ja/en/zh-TW)
  rendered examples at Q2 and Q7 for intake templates.
- **5 gates**: checklist item descriptions and rubric flag criteria
  migrated 繁中 → EN. JP legal terms (景品表示法, ステマ告示) and
  technique names (PASONA, なんかいいよね禁止, etc.) preserved in JP.
- **SKILL.md** (390 → 391 lines): remaining 繁中 fragments in
  When to Use, Resource Manifest annotations, workflow table Notes
  column migrated to EN. Already-EN sections untouched.
- **research/grounding-v4.12.0.md**: NOT migrated (maintainer-facing
  audit trail, exempt from convention).

### Language rule established

> **Prose language follows canon language** — JP canon content
> uses JP prose, Anglo canon content uses EN prose, meta/scaffolding
> uses EN. No 繁中 in reference files going forward.

Intake brainstorming Q1-Q10 templates support trilingual rendering
via `output_language` parameter (ja / en / zh-TW), with EN baseline
and triple-rendered examples at Q2 and Q7.

### Not a breaking change

Agent contracts, gate schemas, verdict rules, and file paths are
all unchanged. Only prose language inside existing files was modified.

## [4.13.0] — 2026-04-14

First copywriting-team interaction layer refactor: formalize user
intake, clarification hierarchy, progress reporting, mid-pipeline
checkpoints, and candidate output format. MINOR bump per skill-team
conventions (new runtime files — 2 protocols + 1 checklist; additive).

Applies the 2-commit variant formalized in v4.12.1 (no new
`standards/` files added on this branch; `--diff-filter=A` detection
routes to 2-commit mode).

### Added

- `skills/copywriting-team/protocols/copywriting-brainstorming.md`
  (~300 lines) — Phase 0 intake protocol. 10-task sequential checklist
  + Socratic grill + Understanding Summary hard gate. Branches Level 1
  field collection by form type (long / mid / short / ideation / audit).
  Structural precedent: `planning-team/protocols/planning-brainstorming.md`.
- `skills/copywriting-team/protocols/copywriting-handoff-format.md`
  (~290 lines) — candidate output format standard + pipeline progress
  reporting templates + mid-pipeline checkpoint rules + audit report
  structure. Every candidate must attach voice/framework label + 3
  concrete "why good" reasons (enforcing 谷山「なんかいいよね禁止」).
- `skills/copywriting-team/checklists/intake-completeness-checklist.md`
  (~195 lines) — new MUST gate: verifies all Level 1 intake fields
  present in Understanding Summary before downstream protocols load.
  Branches verification by declared form type. FAIL_FATAL on any
  missing Level 1 field → returns BLOCKED to main.

### Changed

- `skills/copywriting-team/SKILL.md` (351 → 390 lines):
  - §Context Discovery rewritten to mandate Phase 0 via
    `copywriting-brainstorming.md` before any downstream work
  - §MUST Gates table adds Intake Completeness as first gate
  - §Resource Manifest evaluator block adds intake gate;
    worker block adds new protocols list section
  - All 5 workflows (Copy Ideation Workshop / Long-Form / Mid-Form /
    Short-Form / Copy Audit) prepend Phase 0 Intake + Phase 0.1 Intake
    Gate rows, gated on confirmed Summary before their respective
    Phase 1 loads
  - §Worker BLOCKED Handling adds "Intake-level BLOCKED" as the first
    common scenario (surfaced by brainstorming protocol or
    Intake Completeness gate)

### Design decisions

- **Full 5-dimension interaction layer in one version** — intake +
  clarification hierarchy + progress reporting + mid-pipeline
  checkpoints + output format convention all delivered together.
  Rationale: dimensions are mutually reinforcing; splitting would
  require temporary inconsistent UX.
- **Level 1 / 2 / 3 intake hierarchy** — Level 1 (Must, BLOCKED if
  missing), Level 2 (Strong recommend, ≤2 clarification rounds
  before fallback), Level 3 (default with disclosure in Summary).
- **Understanding Summary as hard gate** — user must explicitly
  confirm the structured spec before any downstream protocol loads.
  Mirrors `planning-team/protocols/planning-brainstorming.md` Task 4c
  and `code-team/protocols/code-brainstorming.md` Understanding
  Summary step.
- **Candidate output format standardization** — every candidate
  (from ideation workshop or direct drafting) carries voice
  reference + approach/framework label + 3 concrete "why good"
  reasons + ethics self-check result. Borrowed from
  `protocols/copy-ideation-parallel.md` §Phase 3 handoff and
  promoted to team-wide standard.

### Commit split

2-commit variant per v4.12.1 skill-team convention (this refactor adds
no new `standards/` files, so canonical 3-commit's "Commit 1/3 —
Standards Foundation" does not apply):

1. `refactor(copywriting-team): add intake protocol + handoff format + completeness checklist (v4.13.0 1/2)`
2. `refactor(copywriting-team): wire intake into workflows, bump 4.13.0 (v4.13.0 2/2)`

### Out of scope (deferred to v4.14.0 / v4.15.0)

- QUEST / PASTOR / CREMA extended long-form frameworks (v4.14.0 —
  addresses attribution drifts 6+7)
- 小霜和也 本能ドライバー analysis as structural alternative (v4.14.0)
- JP copy craft lineage depth — 糸井/岩崎/眞木 voice studies (v4.14.0)
- SNS evolution AIDMA → AISAS → ULSSAS coverage (v4.14.0)
- Neta injection techniques + WebSearch-only pipeline + safety gate
  (v4.15.0)

## [4.12.1] — 2026-04-14

Skill-team convention clarification: formally define a **2-commit
split variant** for refactors that introduce no new `standards/`
files. Modify-only PATCH bump per skill-team convention (existing
runtime files updated, no new files added).

### Motivation

copywriting-team v4.13.0 (forthcoming) is an interaction-layer
refactor (intake protocol + handoff format + intake-completeness
checklist) that adds no new `standards/` files. The canonical
3-commit split's "Commit 1/3 — Standards Foundation" has no content
to hold for such refactors. Forcing a placeholder or stub into
Commit 1 would be an anti-pattern per `grounding-principle.md`.
Before v4.12.1, the Commit Split Validity gate had no formal branch
for this case and flagged such refactors as NEEDS_REVISION — a
convention gap rather than an actual structural problem.

### Changed

- `skills/skill-team/standards/commit-convention.md`:
  - New §2-Commit Variant: Refactor Without New Standards section
    defining Commit 1/2 (protocols/gates + modify-only standards) +
    Commit 2/2 (wiring) layout
  - Detection rule: `git diff --name-only --diff-filter=A main..HEAD
    -- '**/standards/*.md'` empty → 2-commit variant applies;
    otherwise 3-commit canonical. The `--diff-filter=A` restricts to
    **added** files, so modify-only standards edits stay in 2-commit
    mode (rationale: 3-commit's value is isolating NEW grounding for
    review; text-only tweaks do not need that isolation)
  - §Commit Message Format clarifies `(v<X.Y.Z> <N>/<N>)` suffix with
    denominator matching detected split size (examples of both
    canonical 3-commit and 2-commit variant)
- `skills/skill-team/checklists/commit-split-checklist.md`:
  - §Scope adds mandatory split-mode detection first step with
    matching `--diff-filter=A` rule
  - CHK-CMT-001/002/003 gain mode-aware branches (3-commit canonical
    vs 2-commit variant) — each item specifies expected content per
    mode. 2-commit branch of CHK-CMT-001 explicitly permits modify-
    only standards edits (only NEW additions trip 3-commit mode)
  - CHK-CMT-003 returns NOT_APPLICABLE in 2-commit mode (content
    validated by CHK-CMT-002 in that mode)
  - CHK-CMT-004 updates suffix pattern to `N/<N>` with denominator
    matching the detected mode

### Self-dogfood

This very amendment is 2-commit mode — it modifies `commit-convention.md`
(in `standards/`) and `commit-split-checklist.md` (in `checklists/`).
Because no **new** standards files are added, the detection rule with
`--diff-filter=A` correctly routes to 2-commit mode. The initial draft
used plain `git diff --name-only` (no filter), which would have tripped
to 3-commit mode on this branch — the filter refinement was surfaced
by dogfood evaluation and applied before this commit.

### When to use which split

| Refactor touches `standards/`? | Split mode | Precedent |
|---|---|---|
| Yes (add / modify standards) | canonical 3-commit | qa-team v4.2.0, design-team v4.8.0 |
| No (protocols/gates/wiring only) | 2-commit variant | copywriting-team v4.13.0 (forthcoming) |

### Not a breaking change

Existing 3-commit branches continue to pass unchanged — mode detection
routes them to the canonical branch of each CHK-CMT item. The gate's
output JSON format and verdict rules are identical.

### Commit split

Since this amendment is itself a modify-only PATCH with no new files,
per the convention it codifies, the **2-commit variant** applies
self-dogfood style:

1. `refactor(skill-team): add 2-commit variant to commit-convention + checklist (v4.12.1 1/2)`
2. `refactor(skill-team): bump 4.12.1 with CHANGELOG (v4.12.1 2/2)`

## [4.12.0] — 2026-04-14

New domain team: **copywriting-team** — persuasive marketing copy
grounded in Japanese advertising tradition and Anglo direct-response
canon. MINOR bump per skill-team conventions (additive — new team
under `skills/copywriting-team/`, router update, no breaking changes).

### Added

- `skills/copywriting-team/` — complete skill directory
  - `SKILL.md` (351 lines) — persona grounded on 神田昌典 PASONA
    2016+2021, 谷山 散らかす→選ぶ→磨く, 今泉 曼陀羅 1987,
    川喜田 KJ法 1967, Cialdini 1984, Schwartz 1966, Zhang et al.
    2025 Verbalized Sampling
  - **10 standards** (1994 lines total):
    - 4 ideation: `ideation-mandalart.md` (Tier 3),
      `ideation-kj-convergence.md` (Tier 3),
      `ideation-taniyama-discipline.md` (Tier 3),
      `verbalized-sampling.md` (Tier 2)
    - 3 writing layers: `long-form-pasona-canon.md` (Tier 3),
      `mid-form-beaf-canon.md` (Tier 2),
      `short-form-catchcopy-canon.md` (Tier 3)
    - 3 common: `voice-and-tone.md` (Tier 2),
      `persuasion-ethics.md` (Tier 2),
      `persuasion-psychology-anchor.md` (Tier 2)
  - **5 protocols**: `copy-ideation-parallel.md`,
    `write-long-form-copy.md`, `write-mid-form-copy.md`,
    `write-short-form-copy.md`, `copy-audit.md`
  - **4 gates**: MUST `persuasion-framework-adherence-checklist.md`,
    MUST `ethics-checklist.md`, SHOULD `voice-consistency-gate.md`,
    SHOULD `form-appropriate-gate.md`
  - `research/grounding-v4.12.0.md` — consolidated audit trail from
    3 parallel research agents covering long-form / short-form /
    ideation framework clusters

### Changed

- `skills/using-domain-teams/SKILL.md` — router updated:
  - Available Teams table adds copywriting-team row
  - Intent Routing adds 7 copy-related intent rows (long-form LP,
    mid-form EC, short-form キャッチコピー, voice guide, ideation,
    audit) plus handoff patterns with planning / design
  - Ambiguous Cases adds 3 copywriting-involved chains

### Design decisions

- **Three-layer form split**: long (PASONA family) / mid (BEAF) /
  short (キャッチコピー) — each layer has its own structural
  framework because operating principles differ (conversion funnel
  vs functional persuasion vs 一撃型 insight).
- **Two-stage pipeline**: 發散 (曼陀羅 + Verbalized Sampling) →
  收斂 (KJ法 + 谷山「なんかいいよね禁止」) → 撰寫 (three-layer
  branching). Subagent parallelism via `copy-ideation-parallel.md`.
- **FULL JP integration** — 5 of 10 standards are Tier 3
  (神田 / 谷山 / 今泉 / 川喜田 / キャッチコピー 伝統) per
  grounding-principle decision tree; JP content is structural SSOT.
- **Secondary-source grounding discipline** — user confirmed no
  primary-source access; every load-bearing claim dual-verified
  against 2+ independent secondary sources per
  `skill-team/standards/grounding-principle.md`.

### Critical Attribution Corrections — 8 drifts校正

1. マンダラート 8-方向 standard classification is 後人衍生, not
   今泉 1987 原作
2. 大谷翔平 OW64 is 原田隆史 Method (松村寧雄 1979 マンダラチャート
   lineage), not 今泉 マンダラート
3. 谷山雅計 "What×How 四象限" is NOT in the original book; canonical
   is 散らかす→選ぶ→磨く +「なんかいいよね禁止」+ 31 訓練
4. PASONA 1999 年 is 通說; canonical documentation is 神田昌典 2016
   『稼ぐ言葉の法則』
5. PASBECONA was formally named in **2021**『コピーライティング
   技術大全』(神田 + 衣田共著), not 2016
6. QUEST belongs to **Michel** Fortin 2005 blog (NOT Michael
   Fortin, NOT Clayton Makepeace)
7. PASTOR's T = **Transformation + Testimony** (両義, per Ray
   Edwards 2016), not Testimony alone
8. リゲイン「24 時間戦えますか？」 belongs to 杉山恒太郎 + リゲイン
   PJ, not 岩崎俊一 (common misattribution)

### Out of scope (deferred to copywriting-team v1.1.0)

- Extended long-form frameworks (QUEST / PASTOR / CREMA)
- Neta (流行文化引用) injection with WebSearch-only pipeline
- 小霜和也 本能ドライバー analysis as structural alternative
- JP copy craft lineage (糸井 / 岩崎 / 眞木 deeper voice studies)
- SNS evolution AIDMA → AISAS → ULSSAS deep coverage

Commit split (per skill-team 3-commit convention):

1. `feat(copywriting-team): introduce standards + grounding research (v4.12.0 1/3)`
2. `feat(copywriting-team): add protocols + gates (v4.12.0 2/3)`
3. `feat(copywriting-team): wire SKILL.md, router, bump to 4.12.0 (v4.12.0 3/3)`

## [4.11.1] — 2026-04-12

Meta-refactor of **skill-team** (the plugin's meta-skill for building
domain-team skills) codifying 7 patterns surfaced during the
research-team v4.11.0 investment analysis L1/L2/L3/portfolio split
refactor (PR #45, merged earlier same day).

v4.11.0 was the first **post-grounding expansion refactor** in the
plugin's history — research-team was already grounded (v4.9.0
initial grounding, v4.10.x incremental PATCHes), and v4.11.0
expanded investment analysis by adding 5 new frameworks (Hedgeye
GIP / MMT / RAI / Taleb Barbell / Fama-French) AND splitting the
monolithic `investment-analysis-canon.md` (646 lines) into 4
scale-based standards files. The refactor surfaced **42 Critical
Attribution Corrections** and exposed several meta-conventions not
previously codified in skill-team: scale-hierarchy as a content
organization axis, contested-framework citation discipline,
cross-layer bridge preservation, extended JP integration decision
modes, per-phase resource narrowing, multi-cluster parallel
grounding, and post-grounding expansion as a distinct redesign
mode.

This v4.11.1 PATCH codifies all 7 patterns into skill-team's
existing standards and protocols so future refactors use them
consistently rather than re-inventing ad-hoc.

PATCH bump per `skill-team/standards/commit-convention.md`
CHK-CMT-005 distinguishing rule: all changes are **modify-only**
(no new files read at runtime by worker/evaluator). 3-commit PATCH
split allowance per v4.8.1.

### User's question that triggered the refactor

After merging research-team v4.11.0, the user asked:

> 請問這輪的修改是否有可供 skill-team 借鑑的地方？

("Are there any parts of this round's changes that skill-team
could borrow from?")

An audit of skill-team's current state against the 7 patterns
observed in v4.11.0 surfaced gaps in 5 of 7 patterns (MISSING or
PARTIAL coverage) and validated that all 7 are worth codifying.

### Self-bootstrap precedent (5th instance)

Previous self-bootstrap patches: v4.6.1 (CHK-SKL-001 80-word floor
drift), v4.7.1 (Compact+Admonitions citation policy), v4.7.2
(3-Tier Parametric Classification + Body Self-Containment), v4.8.1
(7-fix consolidation for v4.7.0 research-note convention
downstream drift). v4.11.1 is the 5th — skill-team codifying
conventions observed in research-team v4.11.0 and validating them
against its own newly-codified rules during dogfood. Each patch is
simultaneously codifying and validated against the codified rule.

### Added — 7 meta-conventions across 5 files (~460 lines total)

**Pattern 1: Scale-hierarchy split axis** (`file-conventions.md`)

- NEW §Standards Splitting Discipline with 3 split axes (topic /
  tier / scale-hierarchy). Scale-hierarchy is the new axis added
  by v4.11.0: split a single subject-matter domain by natural
  professional-practice taxonomy where each layer asks a
  qualitatively different question (macro → sector → security →
  portfolio for investment analysis; strategic → tactical →
  operational for planning; system → module → function for
  architecture).
- Includes a 4-condition decision rule, anti-conditions (do NOT
  use when layers are really topics or tiers, or when domain has
  no professional taxonomy), and cross-layer bridge requirement.

**Pattern 5: Contested/heterodox framework dual-canonical + critique rule** (`grounding-principle.md §What Counts as Primary Source`)

- NEW §Contested and heterodox frameworks subsection. For
  frameworks outside global consensus (MMT, heterodox macro
  schools, some JP 経営理論, Chinese regulatory frameworks),
  single-canonical citation manufactures false consensus.
- New rule: cite both **canonical lineage** (origin + academic
  canonical + popular canonical, 2-3 as applicable) AND **mainstream
  critique** (2-3 peer-reviewed responses) with equal prominence
  (not relegated to footnote).
- Precedent example: MMT with Mosler 1996 (origin) / Wray 2012
  (academic) / Kelton 2020 (popular) + Krugman / Summers / Rogoff /
  Blanchard 2019 *AER* 109(4) / Mankiw NBER WP 26650 critiques.
- Includes "contested decision test": can you find ≥2 peer-reviewed
  or authoritative-institution sources from outside the framework's
  originating school that explicitly reject it? → contested →
  dual/triple canonical required.

**Pattern 4: Cross-layer bridge preservation** (`grounding-principle.md §Body Self-Containment Rule`)

- NEW §Cross-Layer Bridge Preservation subsection. When splitting
  by scale hierarchy, some claims span two layers and cannot be
  cleanly assigned to a single file (CAPE is L1+L3; sector
  rotation is L1↔L2 bridge).
- Rule: each cross-layer claim has a single "home" file with the
  primary definition, plus an explicit cross-reference paragraph
  in the other affected file. Without this, the split loses
  content at the seam (claim either disappears from non-home file
  or duplicates and drifts).
- 4 research-team v4.11.0 precedent examples: CAPE, Damodaran
  implied ERP, sector rotation, factor × regime dependency.
- 4-item preservation test: single home file, explicit cross-
  reference, home-only worker can fully act, non-home-only worker
  knows to consult home.

**Pattern 6: Extended JP integration decision matrix** (`grounding-principle.md §Japanese Content Integration Strategy`)

- Extends the existing 3-row matrix (full integration / preamble /
  no overlay) with 2 new decision modes surfaced by v4.11.0:
  - **Terminology trap warning**: JP term superficially matches EN
    concept but means something different. Precedent: JP
    バーベル戦略 (bond duration barbell) ≠ Taleb's antifragility
    Barbell. Body MUST include §JP Terminology Traps section with
    explicit "NOT X" language.
  - **Closest analogue with caveat**: JP tool serves analogous-
    but-different purpose. Precedent: BoJ Financial System Report
    heat map is closest to RAI (same audience/scope) but differs
    in intent (macroprudential-not-sentiment). Body MUST include
    §JP Analogue section documenting both parallel and caveat.
- Extends decision process from 3 branches to 5 branches.
- Both new format templates included with concrete research-team
  v4.11.0 precedent wording (バーベル戦略 disambiguation + BoJ FSR
  heat map caveat).

**Pattern 2: Per-phase resource narrowing** (`agent-interface.md §Worker Input Contract`)

- NEW §Per-Phase Resource Narrowing as an **optional backward-
  compatible extension** to the Worker Input Contract. Workers
  that ignore any `phase_load_rule` hint continue to work
  correctly (they load every file in the `standards:` array).
- Two patterns documented:
  - **Pattern A (recommended default)**: protocol-driven loading.
    The protocol file itself documents which standards load in
    which phase (inside each Phase header). No launch-time
    contract change. Used by `research-team/protocols/investment.md`
    v4.11.0 Phase 0 "Layer loading by mode" table.
  - **Pattern B (explicit)**: launch-time `phase_load_rule` hint
    in the `### Input` block. More explicit but requires worker
    to parse.
- Use when: protocol has 3+ phases AND distinct standards needs
  per phase, full corpus exceeds ~100k tokens, quick/deep modes
  have qualitatively different resource requirements.

**Pattern 3: Multi-cluster parallel research** (`grounding-research.md §Phase 2b`)

- NEW §Phase 2b as an optional phase for multi-framework
  expansions. When grounding spans 3+ independent framework
  clusters, a single sequential research-team launch is both slow
  and loses focus across clusters.
- New pattern: launch one `general-purpose` worker per cluster in
  parallel (single main-agent response with N tool calls), each
  with narrow scope (one framework, 4-6 specific claims, ~40-60k
  token budget). Then synthesize N outputs into one consolidated
  research note.
- Precedent table from research-team v4.11.0: 5 parallel
  general-purpose agents (Hedgeye GIP 7 corrections / MMT 7 / RAI
  10 / Barbell 7 / Fama-French 11), total ~205k tokens, surfaced
  42 attribution corrections with 11 unique misattributions
  prevented.
- 3 anti-conditions: initial skill grounding, single-framework
  deep dive, tightly-coupled clusters.

**Pattern 7: Post-grounding expansion track** (`skill-redesign.md §Phase 1 Variant`)

- NEW §Phase 1 Variant: Post-Grounding Expansion Track as a
  distinct redesign mode for refactoring already-grounded teams.
- Trigger conditions: target already has `research/grounding-
  v{X.Y.Z}.md`, adding new frameworks (not re-grounding or fixing
  workflows), new frameworks fit existing scale/tier structure OR
  introduce new scale-hierarchy split.
- Streamlined Phase 1: skip full gap-assessment (no "load-bearing
  claims without citations" scan), scan for new-framework gap
  only, classify by layer / tier / topic, decide split vs extend,
  skip broken-workflow scan, skip JP re-decision unless new
  framework surfaces JP content.
- Jumps to `grounding-research.md §Phase 2b` (parallel) for 3+
  new frameworks; regular Phase 2 for 1-2.
- Comparison table distinguishing initial grounding from post-
  grounding expansion across 7 dimensions (target state, Phase 1
  focus, Phase 2 launch, file operations, version bump, dogfood
  gates, typical precedent).

### Changed

- `.claude-plugin/plugin.json` version bump `4.11.0` → `4.11.1`

### File changes summary

| File | Change | Δ Lines |
|---|---|---:|
| `skill-team/standards/file-conventions.md` | +§Standards Splitting Discipline | +55 |
| `skill-team/standards/grounding-principle.md` | +§Contested frameworks / +§Cross-Layer Bridge Preservation / extended §JP Integration matrix | +159 |
| `skill-team/standards/agent-interface.md` | +§Per-Phase Resource Narrowing | +62 |
| `skill-team/protocols/grounding-research.md` | +§Phase 2b Multi-Cluster Parallel Research | +84 |
| `skill-team/protocols/skill-redesign.md` | +§Phase 1 Variant: Post-Grounding Expansion Track | +88 |
| `.claude-plugin/plugin.json` | version bump | +0 (1 modify) |
| `CHANGELOG.md` | [4.11.1] entry | (this entry) |
| **TOTAL new content** | | **~448 lines** |

### Verification

- `git log --stat` shows clean 3-commit split:
  - 1/3 (0aeab23): standards — 3 files, +282 insertions
  - 2/3 (1a49865): protocols — 2 files, +174 insertions
  - 3/3: plugin.json + CHANGELOG (this commit)
- All changes modify-only; no new files read at runtime by worker
  or evaluator → PATCH classification per CHK-CMT-005
- SKILL.md unchanged for skill-team (v4.8.1 PATCH allowance: SKILL.md
  is optional for modify-only PATCHes that don't change SKILL.md
  structure or Resource Manifest)
- All 5 modified files retain their `## Primary Sources` sections
  intact; new content is additive to existing sections
- research-team v4.11.0 precedent references woven throughout for
  concrete grounding

### Dogfood gates (expected outcomes)

| Gate | Tier | Expected |
|---|---|---|
| Skill Completeness | MUST | PASS (SKILL.md unchanged) |
| Commit Split Validity | MUST | PASS (clean 3-commit PATCH, CHK-CMT-005 modify-only = PATCH) |
| Primary Source Grounding | SHOULD | PASS (meta-refactor grounds in research-team v4.11.0 as the precedent; new sections cite v4.11.0 instances concretely) |
| Skill Coherence | SHOULD | PASS (5 files modified, all cross-references preserved; new sections add cross-references between skill-team standards and protocols) |

### Future refactors that will benefit

Post-v4.11.1, future refactors can directly reference:

- `file-conventions.md §Standards Splitting Discipline` → split
  decision rules (topic vs tier vs scale-hierarchy)
- `grounding-principle.md §Contested and heterodox frameworks` →
  MMT-style dual-canonical citation discipline
- `grounding-principle.md §Body Self-Containment §Cross-Layer
  Bridge Preservation` → hierarchical split cross-reference rule
- `grounding-principle.md §Japanese Content Integration Strategy`
  (extended matrix) → terminology trap and closest-analogue modes
- `agent-interface.md §Per-Phase Resource Narrowing` → token-
  optimized workflow patterns
- `grounding-research.md §Phase 2b Multi-Cluster Parallel Research`
  → 3+ framework expansion grounding
- `skill-redesign.md §Phase 1 Variant: Post-Grounding Expansion
  Track` → already-grounded-team expansion workflow

Next expected beneficiary: any future research-team framework
expansion (e.g., v4.12+) AND any other grounded team that reaches
expansion phase (design-team, planning-team as candidates for
next post-grounding expansions).

## [4.11.0] — 2026-04-12

Investment analysis standards split by **analytical scale** (L1
macro / L2 sector / L3 security / portfolio meta-layer) matching
professional top-down investment process. The monolithic 646-line
`investment-analysis-canon.md` is replaced by 4 scale-specific
standards files, and 5 new frameworks are added with primary-
source grounding: Hedgeye GIP 4-quadrant, Modern Monetary Theory
(background theory for regime analysis), Risk Appetite Index,
Taleb Barbell Strategy, and Fama-French Factor Investing. The
investment protocol is restructured from 4 phases (Scope /
Security / Macro / Output) to 6 phases (Scope / L3 Security / L1
Macro / L2 Sector / Portfolio / Output) with context-cost-aware
per-layer standards loading.

MINOR bump per `skill-team/standards/commit-convention.md`
CHK-CMT-005 — 5 new files (4 standards + 1 research note) are
read at runtime by worker and evaluator agents.

### User's concern that triggered the refactor

The user wanted to add more investment analysis frameworks (Hedgeye
GIP / Economic Environments / RAI / Barbell / Risk Parity / Fama-
French / MMT) to research-team and flagged that the existing
`investment-analysis-canon.md` (646 lines after v4.10.1) was
becoming monolithic and would fail at scale. The initial proposal
was to split the canon by topic (valuation / regime / sentiment),
but the user's critical architectural insight redirected the plan:

> 我會覺得這些框架可能要區分是針對 總體經濟 產業 還是單一投資標的
> 這樣規模不同的分析情境由大到小做個分類？

Investment analysis has a **natural professional-practice taxonomy**
that matches the top-down / bottom-up investment process:

| Layer | Scale | Question | Output |
|---|---|---|---|
| **L1 Macro** | Global / country / currency-zone | "What regime are we in? Which asset class leads?" | Regime diagnosis + asset allocation |
| **L2 Sector / Industry** | Industry / sector / theme | "Which sectors benefit in this regime?" | Sector rotation + theme bets |
| **L3 Security** | Individual stocks / bonds / assets | "Is this specific asset cheap vs intrinsic value?" | Valuation + buy/sell + position sizing |
| **Portfolio** (meta) | Allocation construction | "How do we combine positions into a risk-coherent portfolio?" | Allocation philosophy + risk budgeting |

This maps 1:1 to how professional investment teams organize
research (Macro Strategist / Sector Analyst / Equity Analyst /
Portfolio Manager roles) and is the scalability-friendly structure
— new frameworks naturally slot into one of the 4 layers.

### Grounding research (Stage 1)

Before executing the file split, 5 parallel grounding research
agents verified primary sources and surfaced attribution
corrections for each of the 5 new frameworks. Outputs consolidated
into `research/grounding-v4.11.0.md` (1364 lines, audit trail).
**42 Critical Attribution Corrections surfaced, 11 misattributions
prevented before reaching standards files.**

Per-framework grounding outcomes:

**Hedgeye GIP (McCullough 2024)** — 7 corrections:
- GIP is **2-axis + derived policy overlay**, NOT a 3-axis framework
- Descendant of Dalio's 1996 4-box taxonomy, NOT a Greetham IC
  refinement
- Dual attribution: McCullough + Dale (Hedgeye Risk Management)
- Canonical text: McCullough 2024 *Master The Market* (Hedgeye
  self-published) + Hedgeye GIP white papers (grey literature)

**Modern Monetary Theory (Mosler 1996 / Wray 2012 / Kelton 2020)**
— 7 corrections:
- **Mosler 1996** *Soft Currency Economics* is origin (Italian bond
  trade context), NOT Kelton
- **Wray 2012** *Modern Money Theory: A Primer* Palgrave Macmillan
  is academic canonical
- **Kelton 2020** *The Deficit Myth* PublicAffairs is popular
  canonical — do NOT cite alone
- Intellectual ancestors: Knapp 1905 + Mitchell-Innes 1913/14 +
  Lerner 1943 + Minsky 1986 + Godley
- NOT "just print money" — inflation is the binding constraint,
  not debt level
- Neutral presentation required with mainstream critique
  (Krugman / Summers / Rogoff)
- Japanese context dual position: Kuroda rejection vs Fujii
  endorsement vs Ito / Fujimaki / Sakuragawa / Nersisyan-Wray 2021
  Levy WP 985

**Risk Appetite Index (Kumar & Persaud 2002)** — 10 corrections:
- **Kumar & Persaud 2002** "Pure Contagion and Investors' Shifting
  Risk Appetite" *International Finance* 5(3) is peer-reviewed
  origin, NOT Credit Suisse Wilmot
- **Illing & Aaron 2005** Bank of Canada *Financial System Review*
  is the survey anchor
- State Street ICI = **Froot & O'Connell NBER WP 10157** (corrected
  from common misattribution to WP 8226)
- Goldman Sachs publishes a **Risk-Aversion Index** (inverse
  semantics), NOT an RAI — disambiguate
- **"BofA Global Investor Confidence Index" does NOT exist** — the
  real product is the **Bull & Bear Indicator** by Michael Hartnett
- Use as contrarian indicator only

**Taleb Barbell Strategy (Taleb 2012 Antifragile)** — 7 corrections:
- **Taleb 2012** *Antifragile* Ch 11 is primary canonical, NOT
  *Black Swan* 2007 Ch 13 (which mentions the concept briefly)
- **Geman, Geman & Taleb 2015** "Tail Risk Constraints and Maximum
  Entropy" *Entropy* 17(6) DOI 10.3390/e17063724 is mathematical
  anchor
- Barbell is **extreme-extreme** allocation, NOT moderate middle-
  of-road — common misreading
- 85/15 proportion is illustrative, NOT prescriptive
- **Universa (Spitznagel) ≠ pure Barbell** — runs a 96.7% SPX +
  3.3% tail hedge overlay, technically separate instrument
  structure
- Japanese バーベル戦略 terminology trap = bond duration barbell
  (short + long, no middle), NOT Taleb's Barbell — disambiguate
  in JP context

**Fama-French Factor Investing (Fama & French 1993 / 2015)** —
11 corrections:
- **Fama & French 1993** "Common Risk Factors" *JFE* 33(1) is 3-
  factor operational model (Market + SMB + HML)
- **Fama & French 2015** "A Five-Factor Asset Pricing Model" *JFE*
  116(1) adds RMW profitability + CMA investment
- **Carhart 1997** "On Persistence in Mutual Fund Performance"
  *JoF* 52(1) is 4-factor with momentum — NOT Fama-French
- **FF5 EXPLICITLY excludes momentum** — specify which model when
  citing factor results
- **Quality factor = AQR QMJ** (Asness-Frazzini-Pedersen 2019
  *Review of Accounting Studies* 24), NOT FF RMW
- **Low-Vol / BAB = Frazzini-Pedersen 2014** *JFE* 111, NOT FF
- **Fama-French ≠ APT** (Ross 1976 is different mathematical
  foundation)
- **Japan exception is load-bearing**:
  - **Kubota & Takehara 2018** *International Review of Finance*
    18(1) — FF5 fails in Japan
  - **Fama & French 2012** *JFE* 105(3) — no momentum in Japan
  - **Asness et al. 2011** *JPM* 37(4) — momentum-as-value-hedge
    reinterpretation

### Added

- **`standards/investment-macro-regime.md`** (Tier 3, L1 Macro,
  ~768 lines) — Greetham & Hartnett 2004 Merrill Lynch Investment
  Clock + Dalio 2018 two-horizon debt cycle + Koo 2008 balance-
  sheet recession JP parallel + McCullough 2024 Hedgeye GIP
  4-quadrant refinement + Mosler 1996 / Wray 2012 / Kelton 2020
  MMT background theory (with mainstream critique) + Kumar &
  Persaud 2002 / Illing & Aaron 2005 RAI contrarian positioning
  signal + consolidated Critical Attribution Corrections section

- **`standards/investment-sector-industry.md`** (Tier 2, L2 Sector,
  ~541 lines) — Fama & French 1993 3-factor + Fama & French 2015
  5-factor + Carhart 1997 4-factor disambiguation + Asness 2011 /
  Kubota-Takehara 2018 JP exception + sector rotation by IC/Dalio
  regime mapping + factor × regime dependency tables + cross-ref
  to `strategic-frameworks.md` for stand-alone sector diagnosis

- **`standards/investment-security-valuation.md`** (Tier 3, L3
  Security, ~482 lines) — Damodaran 2012 three-framework valuation
  (DCF + Relative + Contingent-claim) + Graham & Dodd 1934 margin
  of safety + Mr. Market price-independent verdict discipline +
  Campbell & Shiller 1998 CAPE cycle-smoothing (cross-layer L1 +
  L3) + Cross-Layer Usage Notes (CAPE and Implied ERP as L1 sanity
  checks)

- **`standards/investment-portfolio-construction.md`** (Tier 2,
  Portfolio meta, ~390 lines) — Taleb 2012 *Antifragile* Ch 11
  Barbell Strategy + Geman-Geman-Taleb 2015 mathematical anchor
  + Dalio 2015 Bridgewater Risk Parity + allocation philosophy
  comparison table (60/40 / Risk Parity / Barbell / Concentrated
  value / Indexed passive) + integration with L1+L2+L3 layers

- **`research/grounding-v4.11.0.md`** (1364 lines) — Stage 1
  grounding research audit trail for the 5 new frameworks.
  Primary source verifications, 42 Critical Attribution Corrections,
  integration plan, open questions / deferred.

- **`protocols/investment.md` Phase 4 (L2 Sector/Industry
  Analysis)** — NEW phase for sector rotation by regime + factor
  × regime mapping + factor attribution discipline + cross-ref
  to `strategic-frameworks.md` for stand-alone sector diagnosis.
  Skipped in quick mode and when question is pure L1/L3.

- **`protocols/investment.md` Phase 5 (Portfolio Construction)**
  — NEW phase for allocation philosophy call + integration with
  L1+L2+L3 layers + critical attribution discipline. Skipped in
  quick mode and when question is not about portfolio-level
  allocation.

### Changed

- **`protocols/investment.md`** restructured from 4-phase (Scope /
  Security / Macro / Output) to 6-phase (Scope / L3 Security / L1
  Macro / L2 Sector / Portfolio / Output) structure. Phase 0 adds
  layer-loading-by-mode table for context-cost optimization —
  worker only loads standards files for the layers actually
  needed by the question (a single-security valuation loads only
  `investment-security-valuation.md`; a regime call loads only
  `investment-macro-regime.md`; a top-down thesis loads all 4
  progressively). Phase 1 adds analytical-scale classification
  step. Phase 2 renamed to "L3 Security Analysis". Phase 3
  renamed to "L1 Macro Regime Analysis" and split into required
  2-layer IC+Dalio read plus optional Hedgeye GIP / MMT / RAI
  refinements. Rules section expanded with all new attribution
  corrections from v4.11.0 grounding.

- **`SKILL.md` Resource Manifest** updated — 1 canon entry
  replaced by 4 scale-based entries (investment-macro-regime /
  investment-sector-industry / investment-security-valuation /
  investment-portfolio-construction) with per-layer tier
  classification (Tier 3 / 2 / 3 / 2) and load-on-demand
  semantics per layer. Worker launch template `additional`
  section lists the 4 files separately so per-workflow loading
  can target specific layers.

- **`SKILL.md` persona section** updated to reference the 4-layer
  investment analysis organization with expanded primary source
  list: L1 (IC + Dalio + Hedgeye + MMT + RAI), L2 (Fama-French +
  Carhart), L3 (Damodaran + Graham & Dodd + CAPE), Portfolio
  (Barbell + Risk Parity).

- **`SKILL.md` Investment Analysis workflow** row expanded with
  per-layer loading semantics: quick mode loads L1 and/or L3
  only; deep mode adds L2 + Portfolio progressively.

- **`plugin.json`** version bump `4.10.3` → `4.11.0`.

### Removed

- **`standards/investment-analysis-canon.md`** (646 lines) —
  content fully redistributed to the 4 new scale-specific
  standards files. No content lost; citation style, examples,
  and Critical Attribution Corrections all preserved with
  expanded grounding.

### Critical Attribution Corrections (consolidated, 42 total)

**L1 Macro Regime layer (11 corrections)**:
1. Investment Clock 4 regimes are **Reflation / Recovery /
   Overheat / Stagflation** — NEVER use business-cycle terminology
   (expansion / slowdown / contraction / recovery as GDP concepts)
2. Investment Clock describes asset-class relative performance,
   NOT GDP dynamics — conflating the two is a fatal attribution
   error
3. Dalio 6 phases must be named verbatim (Early / Bubble / Top /
   Depression / Beautiful deleveraging / Pushing on a string) —
   do NOT collapse to 4 or 5
4. Dalio framework is **diagnostic, NOT prescriptive** — asset-
   class calls come from IC, Dalio is structural risk overlay
5. Hedgeye GIP is **2-axis + derived policy overlay**, NOT a
   3-axis framework
6. Hedgeye GIP descended from Dalio 1996 4-box, NOT from Greetham
   2004 IC
7. Hedgeye dual attribution: McCullough + Dale
8. MMT canonical sequence: **Mosler 1996 → Wray 2012 → Kelton
   2020** — do NOT cite Kelton alone
9. MMT is NOT "just print money" — inflation is the binding
   constraint
10. RAI origin is **Kumar & Persaud 2002** *International Finance*
    5(3) — NOT Credit Suisse Wilmot
11. State Street ICI = Froot & O'Connell NBER WP **10157**, NOT
    WP 8226; GS publishes Risk-**Aversion** Index not RAI; "BofA
    Global Investor Confidence Index" does NOT exist (real =
    Bull & Bear Indicator by Hartnett)

**L2 Sector/Factor layer (11 corrections)**:
1. **FF3 (1993) ≠ FF5 (2015)** — specify which model when citing
   factor results
2. **FF5 EXPLICITLY excludes momentum** — momentum is Carhart
   1997 or Jegadeesh-Titman 1993
3. **Carhart 4-factor ≠ Fama-French** — Carhart is FF3 + momentum,
   NOT an FF model
4. **Quality factor = AQR QMJ** (Asness-Frazzini-Pedersen 2019),
   NOT FF RMW
5. **Low-Vol / BAB = Frazzini-Pedersen 2014**, NOT FF
6. **Fama-French ≠ APT** (Ross 1976)
7. **FF5 fails in Japan** per Kubota-Takehara 2018
8. **No momentum in Japan** per Fama-French 2012 JFE 105(3)
9. **Momentum-as-value-hedge** reinterpretation per Asness 2011
   JPM 37(4)
10. Sector rotation is **regime-dependent** — do not present
    sectors as absolute winners/losers
11. Factor regime dependency is **historical tendency, not
    deterministic** — always state confidence

**L3 Security Valuation layer (10 corrections)**:
1. DCF terminal growth must ≤ long-run nominal GDP growth
2. CAPE = **Campbell & Shiller 1998** both authors, NOT Shiller
   alone
3. CAPE operational formula = 10-year real-earnings window
4. Do NOT cite Shiller 2000 *Irrational Exuberance* as operational
   CAPE canonical
5. "Damodaran's macro framework" / "Damodaran regime model" do
   NOT exist — Damodaran is bottom-up valuation only
6. Margin of safety is antidote to false precision, NOT optional
   comfort
7. Mr. Market discipline: fundamentals FIRST, price comparison
   SECOND (reverse is guaranteed calibration failure)
8. Three-framework choice is a function of asset and question,
   NOT preference
9. Relative valuation comparable set must be matched rigorously
   (adjust for growth, risk, reinvestment differences)
10. CAPE is **cross-layer**: L3 P/E variant + L1 whole-market
    valuation signal; Damodaran implied ERP is L3 DCF input + L1
    pricing barometer

**Portfolio Construction layer (10 corrections)**:
1. Barbell primary canonical = Taleb 2012 *Antifragile* Ch 11,
   NOT *Black Swan* 2007 Ch 13
2. Barbell is **extreme-extreme** allocation (safe ballast +
   convex payoff), NOT moderate middle-of-road
3. 85/15 Barbell proportion is **illustrative, NOT prescriptive**
4. Geman-Geman-Taleb 2015 *Entropy* 17(6) is mathematical anchor
5. **Universa ≠ pure Barbell** — 96.7% SPX + 3.3% tail hedge
   overlay
6. Japanese バーベル戦略 = bond duration barbell (short + long),
   NOT Taleb's Barbell — disambiguate in JP context
7. **Risk Parity ≠ 60/40** — risk-contribution-balanced, NOT
   capital-weighted
8. Risk Parity canonical = Dalio 2015 Bridgewater "Engineering
   Targeted Returns" (grey-literature primary)
9. Risk Parity typical implementation = equal risk contribution
   across stocks / bonds / commodities / inflation-linked
10. Portfolio construction is meta-layer across L1+L2+L3 — takes
    regime call + sector tilt + security sizing as inputs

### Verification

- `git log --stat` shows clean 3-commit split (CHK-CMT rule):
  - 1/3 — standards + research note: 6 file operations (5 CREATE +
    1 DELETE), 3545 insertions / 646 deletions
  - 2/3 — protocol refactor: 1 file modified, 303 insertions / 79
    deletions
  - 3/3 — SKILL.md wiring + plugin + CHANGELOG: 3 files modified
- 4 new standards files each declare `tier:` + `layer:` in
  frontmatter + `## Primary Sources` section + body + dedicated
  `## Critical Attribution Corrections` section per
  `grounding-principle.md §Critical Attribution Corrections`
- `investment-analysis-canon.md` deleted; no stale references
  anywhere in `SKILL.md`, `protocols/`, `checklists/`, or
  `rubrics/`
- `research/grounding-v4.11.0.md` (1364 lines) captures full
  Stage 1 audit trail with 42 Critical Attribution Corrections
- MINOR bump per CHK-CMT-005: 5 new files (4 standards + 1
  research note) read at runtime by worker and evaluator — MINOR
  is correct bump, not PATCH

### Line budget status

| File | Lines | Budget | Status |
|---|---|---|---|
| `research-team/SKILL.md` | 489 | 500 hard cap | within cap with 11-line headroom |
| `investment-macro-regime.md` | 768 | Tier 3 heavyweight | expected — 6 frameworks in one file |
| `investment-sector-industry.md` | 541 | Tier 2 medium | expected — factor model + JP exception + rotation tables |
| `investment-security-valuation.md` | 482 | Tier 3 medium | within target |
| `investment-portfolio-construction.md` | 390 | Tier 2 compact | within target |
| `protocols/investment.md` | 480 | no hard cap | expanded from 256 for 6-phase structure |
| `research/grounding-v4.11.0.md` | 1364 | audit trail | not user-facing; expected size |

Carry-forward note from v4.10.2 / v4.10.3: research-team SKILL.md
green-band compression to ≤400 lines remains deferred. Current
489 is near the 500 hard cap; future Resource Manifest additions
may force another round of persona compression.

## [4.10.3] — 2026-04-11

Discoverability fix for investment analysis as a research-team
workflow, triggered by a user observation that "investment or macro
analysis" was buried mid-sentence in research-team's description and
not surfaced in the `using-domain-teams` router intent table. Pure
modify-only PATCH targeting two locations: (1) add a dedicated
Intent Routing row in the router skill; (2) minimal word-order
reorder of research-team's description to put investment analysis
first in the "Use when" clause. Zero new files, zero standards /
protocol / gate changes.

PATCH bump per `skill-team/standards/commit-convention.md`
CHK-CMT-005 — zero new files, matching the v4.10.2 pattern.

### User's original proposal and why it was not adopted as-is

The user initially proposed rewriting research-team's description
with an emoji prefix and `PRIMARY: / SECONDARY:` priority markers to
elevate investment analysis:

```yaml
description: >-
  🎯 PRIMARY: Investment analysis, valuation frameworks, asset
  allocation decisions, macro regime diagnosis (Investment Clock).
  ...
  SECONDARY: Market/competitive research, tech evaluation, OSS
  audits, academic reviews.
```

The proposal's underlying need was valid (investment analysis
discoverability from the top of the description) but the form had
**5 architectural problems**:

1. **Missing Delivers clause** — `skill-md-structure.md`
   §Frontmatter Schema requires a Delivers clause naming artifacts.
   CHK-SKL-001 would FAIL FATAL on any PR with this description.
2. **Missing mission statement** — `🎯 PRIMARY: Investment
   analysis...` is a topic label, not a mission sentence. CHK-SKL-001
   also fails on this.
3. **Emoji prefix breaks the 7-team description convention** — zero
   precedent across qa / docs / devops / code / design / planning /
   research for emojis in SKILL.md descriptions. Global
   `/Users/kouko/.claude/CLAUDE.md` says "avoid emojis unless
   explicitly asked".
4. **PRIMARY/SECONDARY priority markers bias routing for all
   users** — research-team has **5 equally-supported worker-dispatch
   workflows** (Market Analysis / Competitive Analysis / Academic
   Research / Investment Analysis / Tech Stack OSS Evaluation);
   calling Investment Analysis "PRIMARY" and the others
   "SECONDARY" over-weights one user's personal use pattern and
   misrepresents the actual implementation. The Tier 3 standards
   files are `investment-analysis-canon.md` AND
   `information-infrastructure.md` — both are load-bearing, neither
   is "primary".
5. **Architectural mislocation** — `skill-md-structure.md`
   §Frontmatter Schema Router-skill exemption explicitly designates
   `using-domain-teams/SKILL.md` as the canonical routing venue:
   "Router skills still MUST contain Use when / Do NOT use for
   clauses but may omit the mission sentence and Delivers list since
   they deliver routing decisions, not artifacts." Routing signals
   belong in the router, not in individual team descriptions.

### Added

- **`using-domain-teams/SKILL.md` Intent Routing table** — new row
  placed between the existing research-team rows:

  ```
  | Investment analysis, valuation, asset allocation, macro regime
  call | research-team |
  ```

  This is the architecturally correct fix for the discoverability
  gap: the router is the designated routing venue, and adding a
  specific investment-analysis intent row benefits **all users**
  scanning for investment work (not just kouko). Users scanning the
  router now see "Investment analysis, valuation, asset allocation,
  macro regime call → research-team" as a top-level entry.

### Changed

- **`research-team/SKILL.md` frontmatter description** — minimal
  word-order reorder of the "Use when" clause to move "investment
  or macro analysis" from mid-sentence to **first item**:

  ```diff
  -  Use when researching, analyzing, evaluating tech stacks, running
  -  OSS license audits, doing market or competitive research,
  -  investment or macro analysis, or academic literature review.
  +  Use when doing investment or macro analysis (valuation, asset
  +  allocation, Investment Clock regime diagnosis), researching and
  +  analyzing topics, evaluating tech stacks, running OSS license
  +  audits, doing market or competitive research, or academic
  +  literature review.
  ```

  All other description structure preserved: mission sentence,
  Delivers clause, "Do NOT use for" clause, CJK suffix, word count.
  No emoji, no PRIMARY/SECONDARY markers. This respects the
  7-team convention and passes CHK-SKL-001 unchanged.

  The parenthetical expansion adds specific framework names
  (valuation, asset allocation, Investment Clock) so a reader
  scanning the description sees investment-analysis detail at
  first-position weight without needing to adopt a priority-marker
  format.

### Notes

- **No persona or standards changes** — the Layer 1 / Layer 2 /
  Layer 3 architecture from v4.10.2 is preserved. The persona still
  lists 11 sources via 5 domain groupings (Booth / Cochrane / IPCC /
  Kent / Damodaran / Greetham-Hartnett / Dalio / Porter /
  Osterwalder / OpenSSF / 倉田 / NDL). The 8 `standards/*.md` files
  are byte-identical to v4.10.2. The investment-analysis grounding
  (Damodaran + Investment Clock + Dalio + CAPE + Koo) lives in
  `investment-analysis-canon.md` which this refactor does not touch.

- **SKILL.md line count impact** — the description reorder is a net
  zero line change (swaps word position, does not add or remove
  lines). research-team SKILL.md stays at 468 lines.

- **No dogfood gate regressions expected** — the description still
  passes CHK-SKL-001 (mission + Use when + Do NOT use for +
  Delivers clauses all present, word count within 40-200 range).
  The router change does not touch any standards file so Primary
  Source Grounding gate is unchanged. Skill Coherence's Line Budget
  flag stays 🟡 (at 468 lines, unchanged from v4.10.2) — this is
  the known line-budget condition the v4.10.2 CHANGELOG documented.

### Out of scope (deferred)

- **PRIMARY/SECONDARY markers or emoji in descriptions** — rejected
  as a 1-team convention break. If the user wants priority markers
  across all 7 teams for consistency, that would be a separate v4.11
  architecture decision affecting all team descriptions and would
  need agreement from downstream reviewers.
- **Propagating the "elevate most-used workflow to first position"
  pattern to other teams** — the specific reorder applied to
  research-team may or may not be appropriate for planning-team /
  code-team / etc. depending on each team's use distribution; out
  of scope for v4.10.3.
- **Research Modes tables consolidation** — still a valid future
  compression target, deferred.

## [4.10.2] — 2026-04-11

research-team SKILL.md persona compression — a pure text-level
refactor that brings the persona block from **75 lines** (v4.10.1
baseline, sitting at the 500-line hard cap with zero margin) back
into compliance with `skill-team/standards/skill-md-structure.md`
§Persona Block (target 15-30 lines, 2-5 anchor sources). Triggered
by a user observation that the SKILL.md opening source-citation
block was unusually long compared to the other 6 grounded teams.

PATCH bump per `skill-team/standards/commit-convention.md`
CHK-CMT-005 — zero new files, zero standards / protocol / gate
changes. The refactor touches only SKILL.md (compression),
plugin.json (version bump), and CHANGELOG.md (this entry).

### Architecture context — why Layer 1 citations are not redundant

User initially asked whether the extensive source citations in
SKILL.md were redundant with the `standards/*.md` §Primary Sources
sections. The architectural answer: **no**. skill-team uses a
3-layer primary-source record architecture with distinct loading
times:

| Layer | Location | Loading time | Role |
|---|---|---|---|
| **Layer 1** | SKILL.md persona "Anchored on…" clause | **Always loaded** | Behavioral priming + cross-skill routing + scope map |
| **Layer 2** | `standards/*.md` §Primary Sources | **On demand** | Full per-topic citations |
| **Layer 3** | `research/grounding-v{X.Y.Z}.md` | Never loaded | Audit trail |

Layer 1 performs 4 functions Layer 2 cannot:
1. **Agent behavioral priming** — the "Anchored on…" clause tells
   the worker that grounding discipline applies *before* any
   standard file is loaded. Without it, the worker may fall back
   to training-data recall for claims not covered by the specific
   standards invoked in a given workflow.
2. **Cross-skill routing** — `using-domain-teams/SKILL.md` and
   users scanning between skills see only frontmatter + persona.
   A persona with zero citations signals an ungrounded skill at a
   glance.
3. **Loading-cost asymmetry** — SKILL.md is always loaded; standards
   are selective. A quick-mode market scan may only load
   `source-quality-and-evidence.md` and never see
   `investment-analysis-canon.md`. The persona is the only
   universally-visible location showing grounding scope.
4. **Scope map** — domain groupings tell readers where to look in
   `standards/` for each topic. Without it, readers must scan 8
   standards files to find the right one.

`skill-md-structure.md` §Persona Block therefore REQUIRES (not
optional) 2-5 primary-source anchors in the persona. Zero citations
violates CHK-SKL-002. The compression target is not "remove Layer 1"
but "fit the full research-team scope into the 2-5 anchor window".

### Changed

- **`SKILL.md` persona §source-anchor paragraph** — rewritten from
  a 30-line run-on prose paragraph listing 11 primary sources into
  a compact 13-line paragraph grouped by **5 domains**:

  1. **Research methodology** — Booth 2024 *Craft of Research* 5th
     ed. + Cochrane Handbook v6.5
  2. **Confidence calibration** — IPCC AR5 Mastrandrea 2010 + Kent 1964
  3. **Investment analysis** — Damodaran 2012 *Investment Valuation*
     + Greetham & Hartnett 2004 Investment Clock + Dalio 2018
     *Big Debt Crises*
  4. **Strategic frameworks** — Porter 1980 *Competitive Strategy*
     + Osterwalder & Pigneur 2010 BMC
  5. **Information infrastructure** — OpenSSF Scorecard + 倉田敬子
     2007 + 国立国会図書館リサーチ・ナビ

  The outer anchor count is 5 (satisfying the `skill-md-structure.md`
  §Persona Block 2-5 rule by treating each domain grouping as one
  semantic anchor), and each grouping names 1-3 representative
  sources inside for a total of 11 sources visible at Layer 1 —
  the same count as the v4.10.1 baseline, but structurally grouped
  rather than run-on listed. Plus a one-sentence pointer to
  Layer 2 (standards/*.md §Primary Sources) naming the 6 sources
  **deferred from Layer 1**: PRISMA 2020, Tetlock 2015, Kovach &
  Rosenstiel 2021, Graham & Dodd 2008, Campbell & Shiller 1998, and
  SIST 02-2007.

- **`SKILL.md` §Note on Global Context** — compressed from 25 lines
  of full JP integration rationale (Japan's information-access
  apparatus + no-parallel-methodology argument + docs-team / code-team
  precedent comparison) to 8 lines of pointer prose. The full
  rationale stays in `research/grounding-v4.9.0.md` Phase 2, which
  is the maintainer-facing audit trail for the v4.9.0 grounding
  refactor. SKILL.md is the worker-facing skill body; it does not
  need to re-document the grounding archaeology log.

### Stats

- SKILL.md: **500 → 468 lines** (saved 32 lines)
- Persona source-anchor paragraph: 30 → 13 lines (saved 17)
- Note on Global Context: 25 → 8 lines (saved 17)
- Plus ~2 lines whitespace adjustments

- Headroom under the 500-line hard cap: **0 lines → 32 lines**
- Line count now back within the 400-500 "warning" zone on the
  skill-coherence rubric (was at hard cap, strict PASS but
  zero-margin)
- Compliance with `skill-md-structure.md` §Persona Block:
  - Persona lines: was 75 (target 15-30), now ~55 (closer to
    compliant; still over target because of the Mission + Default-
    cheap + Delivers + Done when + Note on Global Context which are
    distinct from the source-anchor paragraph the spec targets)
  - Primary-source anchors: was 11 (target 2-5), now 5 domain
    groupings (structurally compliant)

### Notes on what was NOT compressed

The v4.10.1 Gate 4 (Skill Coherence) yellow warning also suggested
two other compression targets that were deliberately left out of
scope for v4.10.2:

1. **Research Modes tables** (~90 lines) — the Quick / Deep mode
   tables + trigger phrase language table + escalation subsections
   could collapse to a single Mode-comparison table for ~40-50 lines
   savings. Deferred to a possible v4.10.3 if additional headroom
   is needed.
2. **Quick-first + escalation + BLOCKED subsections** (~60 lines,
   4 subsections) — could merge to 2 subsections for ~10-15 lines
   savings. Also deferred.

The user's v4.10.2 request was specifically about the persona
source-citation block, so this refactor stays focused and does not
bleed into unrelated compression work.

### Fixed

- **Zero-margin maintenance risk on SKILL.md line budget** — the
  v4.10.1 PR #42 Gate 4 review flagged SKILL.md at exactly 500
  lines (the hard cap) with zero margin. Any future v4.10.x
  addition to SKILL.md would have tripped CHK-SKL-010 (FATAL).
  v4.10.2 brings SKILL.md back to 468 lines with 32 lines of
  headroom, so subsequent patches can add to SKILL.md without
  requiring simultaneous compression work.

## [4.10.1] — 2026-04-11

research-team investment-analysis-canon.md extension adding two
additional frameworks — Dalio's two-horizon debt cycle (6 phases)
and Campbell & Shiller CAPE cycle-smoothing — plus a Critical
Attribution Correction that explicitly rejects a non-existent
"Damodaran macro regime framework". Also adds Richard Koo 2008
*The Holy Grail of Macroeconomics* as the Japanese parallel to
Dalio's depression → beautiful deleveraging phases.

PATCH bump per `skill-team/standards/commit-convention.md`
CHK-CMT-005 because **zero new files** are introduced. All changes
are additive content inside existing `investment-analysis-canon.md`
standards file + protocol wiring in `investment.md` + SKILL.md
persona touch + plugin.json bump + CHANGELOG entry. The PATCH scope
is intentionally narrow: no new standards file, no new protocol, no
new gate, no workflow-table changes.

### Added

- **`standards/investment-analysis-canon.md` §Dalio's Debt Cycle
  Framework** — new section (~135 lines) covering the two-horizon
  framework: short-term debt cycle (5-8 years, credit expansion /
  contraction) + long-term debt cycle (50-75 years, leverage
  accumulation). Both cycles use the same 6 canonical phases —
  **Early part of the cycle → Bubble → Top → Depression →
  Beautiful deleveraging → Pushing on a string**. Body spells out
  all 6 phases verbatim with definitions (LLM drift hotspot: cold
  query often collapses to 4 or 5 phases or drops "early part").
  Explicit 3-axis variable set (Growth + Inflation + Productivity)
  contrasted with Investment Clock's 2-axis (Growth × Inflation).
  Diagnostic-NOT-prescriptive discipline enforced: Dalio identifies
  phase; asset-class calls come from Investment Clock. Complementarity
  matrix showing IC and Dalio as orthogonal layers (tactical 1-3 yr
  vs structural 5-8 / 50-75 yr). Primary source: Ray Dalio 2018
  *Principles for Navigating Big Debt Crises*, Bridgewater Associates
  (free PDF via principles.com).

- **`standards/investment-analysis-canon.md` §Cyclically-Adjusted
  P/E (CAPE)** — new subsection (~80 lines) placed under existing
  §Damodaran's Valuation Taxonomy §2 Relative Valuation, NOT as a
  parallel regime model. CAPE is a single-variable equity valuation
  indicator (not cross-asset rotation), so it belongs alongside P/E
  / EV/EBITDA / P/B / P/S as a cycle-smoothed refinement of the P/E
  multiple. Full formula with explicit "real" (inflation-adjusted)
  qualifier, 10-year smoothing window anchored in Graham & Dodd
  1934 lineage, historical thresholds table (5 bands across ~150
  years), predictive power R² ~0.30-0.40 on 10-year-forward real
  returns per Campbell & Shiller 1998. Explicit "NOT a regime
  model" disclaimer with complementarity note to Investment Clock.
  JP application note on Nikkei CAPE availability via Shiller's
  Yale dataset since 1957 (no parallel JP methodology). Primary
  sources: Campbell & Shiller 1998 *JPM* 24(2) + Shiller 2015
  *Irrational Exuberance* 3rd ed.

- **`standards/investment-analysis-canon.md` §The Merrill Lynch
  Investment Clock §Complementarity with CAPE** — new subsection
  added after the existing §Anti-Drift Note making the IC ↔ CAPE
  reading explicit. Not a duplicate — the cross-reference lives in
  both directions (IC section points to CAPE, CAPE section points
  to IC) so readers arriving from either framework see the other.

- **`standards/investment-analysis-canon.md` §Balance-Sheet
  Recession — the Japanese Parallel (Koo 2008)** — new subsection
  inside the Dalio section documenting Richard C. Koo's 2008
  *The Holy Grail of Macroeconomics* balance-sheet recession
  concept. Koo's central finding: during Dalio's Depression →
  Beautiful Deleveraging phases, firms switch from
  profit-maximization to debt-minimization, producing prolonged
  demand collapse even at zero interest rates. Grounded in Japan's
  1990s Lost Decade with secondary 2008 US / Euro applications.
  Complementary to Dalio's 6-phase framework (Koo covers 2 phases
  in depth; Dalio covers the full cycle across 48 historical
  crises). Primary source: Koo 2008 Wiley Singapore.

### Changed

- **`standards/investment-analysis-canon.md` frontmatter description
  + Tier 3 rationale** — updated from "three load-bearing pillars"
  to "five load-bearing pillars", adding Dalio and CAPE. Tier 3
  rationale extended to document additional LLM hallucination
  hotspots the body must preempt: Dalio's 6 phases often collapsed
  to 4 or 5; CAPE miscredited to Shiller alone; fabricated
  "Damodaran macro regime framework".

- **`standards/investment-analysis-canon.md` §Critical Attribution
  Corrections** — extended from 1 correction (Investment Clock
  4-phase naming) to 4 corrections with 3 new subsections:
  1. **CAPE authorship is Campbell & Shiller 1998, NOT Shiller
     alone** — LLMs routinely credit CAPE to Shiller 2000
     *Irrational Exuberance* and omit Campbell. The operational
     10-year formulation is in the 1998 *JPM* paper.
  2. **10-year CAPE window is Graham & Dodd 1934, NOT Shiller's
     invention** — correct lineage is Graham & Dodd 1934 →
     Campbell & Shiller 1988 → operational CAPE 1998. Do NOT
     present the 10-year window as Shiller-derived or arbitrary.
  3. **Damodaran has NO canonical macro / regime framework** —
     explicit rejection of a recurring misconception. Damodaran's
     corpus is exclusively bottom-up valuation: DCF / Relative /
     Contingent-claim + ERP and Country Risk as DCF discount-rate
     inputs + 2024 *Corporate Life Cycle* (firm-stage taxonomy,
     NOT macro cycle). For regime frameworks, cite Greetham &
     Hartnett 2004 or Dalio 2018, NOT Damodaran.

- **`standards/investment-analysis-canon.md` §Primary Sources** —
  5 new bullets added (Campbell & Shiller 1998, Shiller 2015,
  Dalio 2018, Koo 2008, plus cross-reference to Campbell & Shiller
  1988 predecessor). Total Primary Sources now ~10 bullets covering
  the 5 load-bearing pillars.

- **`standards/investment-analysis-canon.md` §Damodaran's Valuation
  Taxonomy §Relative Valuation** — P/E bullet now explicitly
  references the CAPE subsection for cyclical-industry use cases.
  New CAPE bullet added to the multiples list.

- **`standards/investment-analysis-canon.md` §Anti-Patterns** —
  extended from 5 to 9 bullets with 4 new anti-patterns:
  1. Citing Dalio's framework as prescriptive asset allocation
  2. Collapsing Dalio's 6 phases into 4 or 5 or using business-cycle
     vocabulary (mirrors the existing IC anti-pattern)
  3. Citing "CAPE" without the "10-year" qualifier (LLMs drift to
     5 or 7)
  4. Citing "Damodaran's macro framework" — the framework does not
     exist; redirect to Greetham & Hartnett 2004 or Dalio 2018

- **`protocols/investment.md`** — Phase 2 Step 5 Valuation now
  lists CAPE as an option under Relative Valuation with explicit
  Campbell & Shiller 1998 dual-author citation requirement. Phase
  3 Step 11 Macro Regime Analysis now produces a **2-layer regime
  read**: Layer A (Investment Clock tactical call, existing) +
  Layer B (Dalio debt-cycle structural risk overlay, new). Step 12
  Implications extends from asset-class mapping alone to
  "tactical call + structural overlay" (e.g., IC says "Recovery →
  Stocks lead" AND Dalio says "Bubble phase → credit-overstretch
  risk → size down"). Quick-mode reductions extended to note one-
  line Dalio phase call only (no 6-phase enumeration) and
  rolling-P/E fallback for CAPE. Deep-mode rigor extended to
  require CAPE threshold check against Campbell & Shiller 1998
  historical bands plus full Dalio 6-phase identification for both
  short-term and long-term cycles. Rules section gains 4 new rules
  (Dalio diagnostic-only, CAPE dual-author, no fabricated Damodaran
  regime framework, Dalio 6 phases verbatim naming).

- **`SKILL.md` persona** — Investment canon anchor paragraph
  extended to name Campbell & Shiller 1998 CAPE and Dalio 2018 as
  additional load-bearing primary sources alongside Damodaran 2012
  and Greetham & Hartnett 2004.

- **`SKILL.md` Resource Manifest** — `investment-analysis-canon.md`
  description line extended to mention CAPE + Dalio + Koo
  coverage.

### Fixed

- **Non-existent "Damodaran macro regime framework" misconception**
  — documented as a Critical Attribution Correction so that future
  requests or deliverables citing Damodaran for macro regimes are
  explicitly redirected to the correct authors (Greetham & Hartnett
  2004 for asset rotation, Dalio 2018 for debt-cycle diagnosis,
  Howard Marks 2018 optional for narrative cycle). This preempts
  downstream LLM drift.

### Notes

SKILL.md line count: 496 → 500 (exactly at the hard cap, 0 lines
of margin). Any future v4.10.x patch that adds to SKILL.md will
need to compress the persona block first. Consider as a follow-up
the v4.10.2 candidate "SKILL.md persona compression pass to restore
~50 lines of budget margin".

investment-analysis-canon.md: 310 → 646 lines (+336 lines). Well
within Tier 3 budget (5 pillars × ~130 lines = proportional to
framework breadth). No new files added at runtime per CHK-CMT-005
→ PATCH bump is correct.

No new research note (`research/grounding-v4.10.1.md`) was created.
Per `grounding-principle.md` the research note is optional for
additive PATCH on frameworks that are already well-known,
canonical, and cold-query-verifiable — Dalio, Campbell & Shiller,
and Koo all meet this bar. The 3 parallel research agent outputs
from the planning session serve as the informal audit trail; the
v4.9.0 grounding-v4.9.0.md research note already covers the
Investment Clock cluster that sits upstream.

Howard Marks 2018 *Mastering the Market Cycle* (HarperBusiness)
was considered and **deferred to a potential v4.10.2** if a
contemporary narrative-cycle framework is desired alongside Dalio.
Marks's greed-fear pendulum and 4-cycle (economic / profit / credit
/ psychological) structure is qualitatively distinct from Dalio's
structured 6-phase diagnostic and from the Investment Clock's
quantitative 2×2 — adding all three in one PATCH would over-stuff
the file. Marks remains a valid future addition if usage shows the
gap.

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
