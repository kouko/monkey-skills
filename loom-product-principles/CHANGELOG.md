# Changelog

All notable changes to the `loom-product-principles` plugin (formerly `product-principles-toolkit`) are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

> This file was reconstructed on 2026-07-02 from the git history — the plugin
> shipped its first two versions without a CHANGELOG.

## [Unreleased]

### Fixed

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
