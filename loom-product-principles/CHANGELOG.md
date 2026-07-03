# Changelog

All notable changes to the `loom-product-principles` plugin (formerly `product-principles-toolkit`) are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

> This file was reconstructed on 2026-07-02 from the git history — the plugin
> shipped its first two versions without a CHANGELOG.

## [0.3.0] — 2026-07-03

### Changed

- **Three-jurisdiction sections**: the required section renamed
  `## Principles` → `## Product Principles` (legacy `## Principles` files
  are detected and migrated with a one-line message, not silently
  rejected). Two new optional sections, `## Design Principles` and
  `## Engineering Principles`, each 1–7 falsifiable principles and never
  emitted empty — jurisdiction-appropriate content is elicited only when
  the product warrants it. `references/principles-rules.md` gained the
  Jurisdictions table and the posture-elicitation steps (does this product
  need a Design jurisdiction? an Engineering jurisdiction?) that decide
  whether each optional section is generated.
- Unqualified "product-level" claims in `SKILL.md` / `principles-rules.md`
  / `README.md` widened to project-constitution framing; the `## Product
  Principles` jurisdiction itself is unchanged in scope (product design
  principles + target user, not business/market/strategy).

- §Downstream updated to reflect the wired reality: named per-station intake
  sections (design generators, `loom-spec:spec-expansion` §Governing
  constraint, both critics' principles lenses) and the **live** loom-code
  `code-reviewer` D8 principles-conformance gate — replacing the stale "a
  future conformance gate may check artifacts" forward-reference.

### Fixed

- Skill description restored to the proactive, trilingual-trigger form: fires
  BEFORE design/spec/build (not only when asked), carries 產品原則 / 產品憲章 /
  プロダクト指針 triggers and the "north star" phrasing the test suite encodes,
  and states a when-NOT boundary. #456's rewrite had dropped the CJK triggers
  and made the description reactive-only, silently breaking 2 tests (no CI ran
  them) and likely re-opening the pre-#456 under-firing this plugin was known
  for.

- `product-principles` SKILL.md now states the correct skill-dir-relative
  validator path (`../../scripts/validate_principles_output.py`); the
  previously claimed `scripts/…` form did not resolve from the skill directory
  in an installed plugin.
- Earlier unversioned post-0.2.0 changes: trigger-description rewrite (#456),
  reply-honesty prose fixes (#465).

## [0.2.0] — 2026-06-21

### Changed

- **BREAKING**: plugin renamed `product-principles-toolkit` →
  `loom-product-principles`; artifact path unified to
  `docs/loom/PRINCIPLES.md` (#440).

## [0.1.0] — 2026-06-14

### Added

- MVP: `product-principles` skill — turn a sparse product idea into a
  `PRINCIPLES.md` constitution (north-star + 3–7 falsifiable principles) —
  plus `validate_principles_output.py` structure validator (#398).
