# Changelog

All notable changes to the dev-workflow plugin will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [1.0.4] — 2026-04-15

### Context

Paired with `domain-teams` v4.21.1 (same PR). Domain-teams made Empty
Invocation Fallback a hard-required SKILL.md section with surface-
orientation synthesis and 5-source sufficient-context check. This
release adds a companion **guidance** (not hard requirement) to
`skill-creator-advance` so authors of generic Claude skills can apply
the same pattern when building conversational or multi-workflow skills.

### Added (skill-creator-advance)

New §Empty-Prompt Onboarding subsection under §Skill Writing Guide
(between "Principle of Lack of Surprise" and "Writing Patterns").

The subsection covers:
- When to include the pattern (recommended for conversational /
  multi-workflow skills; unnecessary for single-shot utility skills)
- 3-element pattern: Surface orientation / Route to intake /
  Sufficient-context skip
- Sufficient-context check must cover 5 sources: current prompt,
  prior conversation, IDE context, plan/memory, upstream handoff
- Common pitfall: triggering orientation on empty-current-prompt
  alone creates friction for returning users
- Cross-reference to `domain-teams/skills/skill-team/standards/skill-md-structure.md`
  §Empty Invocation Fallback Rules as the rigorous domain-team
  version (with §Surface Orientation Format skeleton and CHK-SKL-013
  gate)

+23 lines. No breaking change.

## [1.0.3] — 2026-04-15

### Context

PR #73 was merged at commit bd344a4 (Mermaid guidelines only); the
line→token budget migration commit (d0b1b2c) was not included. This
PATCH restores the dev-workflow portion of that migration.

### Fixed (skill-creator-advance — line→token budget consistency)

Completing the line→token budget migration per `plugin-conventions.md`
§Lightweight SKILL.md canonical guidance ("Use word/token count rather
than line count — lines vary too much in density"):

- `SKILL.md` Key patterns: reference TOC threshold
  ">300 lines" → ">~8,000 tokens"
- `SKILL.md` Working-with-existing-plugin enum:
  "line budgets" → "token budgets"
- `references/plugin-conventions.md` §Lightweight Structure:
  "under 300 lines" → "under ~3,000 tokens"

### Kept as-is (correct current usage)

- `NOTICE:46` — historical migration record
- `references/mermaid-usage-guidelines.md` mentions of "token or line
  count" — accurate discussion of both metrics
- `references/plugin-conventions.md:85` "Use word/token count rather
  than line count" — canonical guidance

## [1.0.2] — 2026-04-15

### Added (skill-creator-advance)
- **New reference**: `references/mermaid-usage-guidelines.md`.
  Generic skill-authoring guidance for when to use Mermaid diagrams
  vs prose. Covers decision criterion (≥3 branch conditions OR ≥4
  state transitions), strong-candidate categories (decision trees,
  state machines with retry loops, routing with failure branches),
  avoid-categories (bibliographies, rationale, corpora, philosophy,
  clean tables, linear sequences), cost-benefit framework, Mermaid
  type selection, syntax conventions, and anti-patterns.
- SKILL.md references/ listing updated to include the new reference.

### Rationale

Complements `domain-teams/skill-team v4.19.0` which shipped the
domain-team-specific version. This version is generic (no gate-system
assumptions) and serves any Claude skill author, not just domain-team
skills.

Empirical finding from the precedent: Mermaid adds clarity to
branching logic but does NOT reduce token/line count when paired
with explanatory prose. The value is eliminating prose ambiguity,
not compression.

## [1.0.1] — 2026-04-14

License compliance: add missing `LICENSE` and `NOTICE` files to the
`skill-creator-advance` skill and correct the upstream attribution
previously misstated in the v1.0.0 CHANGELOG.

### Corrected upstream attribution

v1.0.0 stated "based on Anthropic's skill-creator with 7 enhancements"
and that bundled agents/scripts came "from Anthropic skill-creator."
The accurate upstream chain is:

1. **Anthropic `skill-creator`** (MIT) — the earliest upstream; provides
   the eval-loop concept and file naming for bundled agents (grader,
   comparator, analyzer) and scripts (aggregate_benchmark, run_eval,
   run_loop, improve_description, package_skill, quick_validate,
   generate_report, utils).
   https://github.com/anthropics/skills/tree/main/skills/skill-creator
2. **AllanYiin (尹相志) `skill-creator-advanced`** (MIT, Copyright (c)
   2026 AllanYiin) — **the direct upstream** this plugin adapted from.
   https://github.com/AllanYiin/Amon
   Path: `src/amon/resources/skills/skill-creator-advanced/`
3. **`dev-workflow/skills/skill-creator-advance/`** (MIT, Copyright (c)
   2026 kouko) — this distribution.

The v1.0.0 CHANGELOG incorrectly implied direct derivation from
Anthropic. The direct upstream is Allan's work, which in turn draws
from Anthropic (Allan's own reference files in the upstream
acknowledge "upstream skill-creator").

### Added

- `dev-workflow/skills/skill-creator-advance/LICENSE` — MIT license
  preserving AllanYiin's copyright + adding kouko's copyright for
  modifications, per MIT requirement that upstream notices be retained
  in all copies or substantial portions.
- `dev-workflow/skills/skill-creator-advance/NOTICE` — detailed
  upstream chain, per-version modifications, and link to Allan's
  Facebook announcement of the original skill-creator-advanced.

### Also (repo-root, in the same fix PR)

- Root `LICENSE` (MIT) — corresponding to the MIT declaration in the
  main `README.md` which previously had no license file backing it.
- Root `ATTRIBUTION.md` — summary table of all third-party components
  across all plugins (obsidian kepano skills, obsidian axtonliu visual
  skills, skill-creator-advance lineage).
- `obsidian/skills/README.md` — fixed 3 axtonliu upstream URLs that
  incorrectly pointed to `github.com/anthropics/claude-code-skills`;
  corrected to `github.com/axtonliu/axton-obsidian-visual-skills`.

### Not a breaking change

No skill content modified. Pure license-compliance housekeeping.
v1.0.0 consumers continue to work unchanged; this PATCH only adds
license / attribution files and corrects documentation text.

## [1.0.0] — 2026-04-13

Initial release of the dev-workflow plugin with `skill-creator-advance`.

### Added

- **skill-creator-advance** skill — general-purpose skill creation and
  iterative improvement tool. Adapted from AllanYiin's `skill-creator-
  advanced` (MIT; upstream at github.com/AllanYiin/Amon, path
  src/amon/resources/skills/skill-creator-advanced/), which itself
  draws on Anthropic's upstream `skill-creator`. See LICENSE and NOTICE
  in the skill directory for the full upstream chain. Added the
  following 7 enhancements in this distribution:
  1. monkey-skills ecosystem integration guidance
  2. Description best practices (negative triggers, multilingual keywords)
  3. Eval flow tiering (quick path vs full path)
  4. Existing skill improvement workflow
  5. Slash command creation guidance
  6. Self-assessment pass (auto-fix obvious defects before human review)
  7. Auto-regression detection across iterations

- **Bundled agents**: grader, comparator, analyzer (inherited via
  AllanYiin's skill-creator-advanced, which in turn took the file
  naming convention from Anthropic's upstream skill-creator)

- **Bundled scripts**: aggregate_benchmark, run_eval, run_loop,
  improve_description, package_skill, quick_validate, generate_report
  (same inheritance chain as agents)

- **Reference files**:
  - `plugin-conventions.md` — plugin ecosystem conventions and slash commands
  - `iteration-automation.md` — self-assessment and regression detection protocols
  - `platform-adaptations.md` — Claude.ai and Cowork adjustments
  - `eval-methodology.md` — eval principles with primary source citations
  - `schemas.md` — JSON structures for evals, grading, benchmarks

- **Slash command**: `/skill-creator-advance`

### Design decisions

- Eval results presented **inline + markdown report** instead of browser-based
  eval-viewer (removed dependency on Python web server and browser)
- Token-based budget (~6,000 tokens) instead of line-based (500 lines)
- Platform adaptations extracted to reference file (optional, loaded on demand)
- Eval methodology grounded with primary source citations (Fisher 1935,
  Beck 2002, Hastie et al. 2009, Myers et al. 2011, ISTQB v4.0, etc.)
