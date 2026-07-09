# Changelog

All notable changes to the `loom-discovery` plugin will be documented in this
file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-07-10

### Added

- Initial plugin scaffold: `.claude-plugin/plugin.json` +
  `.codex-plugin/plugin.json` (dual manifest, Claude SSOT synced into Codex
  via `scripts/sync_codex_manifests.py`), `README.md`, this changelog, and
  `scripts/test_plugin_manifest.py`. No skills or hooks yet — those land in
  subsequent tasks per `docs/loom/plans/2026-07-10-loom-discovery-station.md`.
  Test count: stamped at branch close-out per repo memory
  `stamp-changelog-test-counts-at-closeout`.
