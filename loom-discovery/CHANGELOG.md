# Changelog

All notable changes to the `loom-discovery` plugin will be documented in this
file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-07-10

### Added

- Initial plugin: dual manifest (`.claude-plugin/` + `.codex-plugin/`, Claude
  SSOT synced via `scripts/sync_codex_manifests.py`), `README.md`, this
  changelog; three skills — `using-loom-discovery` (family-entry router),
  `business-value` (adversarial worth-it check, GO / NO-GO /
  NEEDS-MORE-RESEARCH, skippable + re-entrant), `user-insights` (two-mode
  needs research with user-ratified value commitment) — plus
  `scripts/validate_discovery_artifacts.py` (assess-first intermediate state
  honored) and the behavioral-dogfood fix round
  (`docs/skill-dogfood/2026-07-10-loom-discovery/report.md`).
  Test count at close-out: 64 (loom-discovery suite; family suites green).
