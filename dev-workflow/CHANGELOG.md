# Changelog

All notable changes to the dev-workflow plugin will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-04-13

Initial release of the dev-workflow plugin with `skill-creator-advance`.

### Added

- **skill-creator-advance** skill — general-purpose skill creation and
  iterative improvement tool, based on Anthropic's skill-creator with
  7 enhancements:
  1. monkey-skills ecosystem integration guidance
  2. Description best practices (negative triggers, multilingual keywords)
  3. Eval flow tiering (quick path vs full path)
  4. Existing skill improvement workflow
  5. Slash command creation guidance
  6. Self-assessment pass (auto-fix obvious defects before human review)
  7. Auto-regression detection across iterations

- **Bundled agents**: grader, comparator, analyzer (from Anthropic skill-creator)

- **Bundled scripts**: aggregate_benchmark, run_eval, run_loop,
  improve_description, package_skill, quick_validate, generate_report

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
