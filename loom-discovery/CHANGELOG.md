# Changelog

All notable changes to the `loom-discovery` plugin will be documented in this
file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-07-18 — evidence source-type column

### Added

- **`user-insights` evidence template**: the evidence table gains a
  `Source type` column (`craft` / `domain-convention` / `project-local`) +
  a compact legend — evidence is typed at intake so downstream stations
  know which authority owns each claim.

## [0.1.2] — 2026-07-14

### Fixed

- **`user-insights` description reverted to the full pre-sweep 899-char
  version** (byte-identical to the 0.1.0 text). The post-merge A/B B-leg
  (plan Task 8) measured combined firing 100%→33%: two records were
  cross-family-attracted by loom-pipeline:loom-memory's pre-existing
  "check prior experience before loom work" clause once the slimmed
  170-char description lost its needs-research lexical thickness. A
  targeted 217-char restore was cache-experimented and ALSO failed
  (1/3 — the ja record newly flipped), demonstrating that mid-band
  lexical tuning near a sibling attractor is unstable — pin-literal
  revert per the plan's A/B bar. Evidence:
  `docs/skill-dogfood/2026-07-14-description-token-economy/ab-results.md`
  §remedy-experiment. Net sweep for this plugin stands at
  using-loom-discovery −566 / business-value −386 chars.

## [0.1.1] — 2026-07-14

### Changed

- Description token-economy sweep (two-tier standard,
  `skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md`
  Principle 5 + cutting rules): frontmatter descriptions rewritten —
  `using-loom-discovery` 1,065→499 rendered chars (router exception band
  ≤500, firing-evidence YAML comment added above `description:` citing the
  2026-07-14 baseline 3/3 EXACT), `user-insights` 899→170, `business-value`
  616→230 (normal band, 250 soft lint). Bodies untouched; multilingual belt
  triggers preserved (需求研究 / 值不值得做 / ユーザーインサイト /
  時間の使い方 / ビジネスバリュー).

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
