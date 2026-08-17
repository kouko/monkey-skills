# Changelog

All notable changes to the `loom-design` plugin will be documented in
this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

The five plugins this one absorbed keep their own histories alongside:
`CHANGELOG-pipeline.md`, `CHANGELOG-spec.md`, `CHANGELOG-discovery.md`,
`CHANGELOG-interface-design.md`, `CHANGELOG-product-principles.md`. Their
version numbers do not continue here — `loom-design` starts fresh at 0.1.0.

## [0.2.0] — 2026-08-17 — artifact-layer table routing (spec side)

### Changed

- **`spec-expansion`'s `## Path × edge matrix` and `## Cross-object
  combinations` sections now specify a markdown-table body** with pinned
  `N/A` lines for the genuinely-empty case, instead of free-form prose.
- **`validate_spec_output.py` rejects a body that carries neither a
  table nor its `N/A` line** for those two sections.

## [0.1.0] — 2026-08-17 — the design side becomes one plugin (6→2)

### Added

- **`loom-design` — one plugin for the whole design side.** Four station
  plugins (`loom-discovery`, `loom-product-principles`,
  `loom-interface-design`, `loom-spec`) and the conductor
  (`loom-pipeline`) merged into this one. Nine member skills ship here:
  `business-value`, `user-insights`, `product-principles`,
  `design-system`, `interaction-flows`, `design-critic`,
  `spec-expansion`, `completeness-critic`, plus the conductor
  `using-loom-pipeline`.
- **One entry router, `using-loom-design`.** The four `using-loom-*`
  design routers merged into it — they shared ~70% of their skeleton and
  four separate entry points made "where do I start" harder to answer,
  not easier. It routes to whichever of the four stations the ask needs.

### Changed

- **Member skill names are unchanged** — only the plugin prefix moved
  (`loom-spec:spec-expansion` → `loom-design:spec-expansion`). A caller
  who invokes a station by name is unaffected.
- **Scripts live under per-station subdirectories**
  (`scripts/{discovery,principles,interface,spec,pipeline}/`) because
  four of the absorbed plugins shipped same-named files. The station
  suites must still be run as separate pytest invocations — the
  duplicate basenames collide at collection without `__init__.py`.

### Moved out

- **The family hooks and `loom-memory` went to `loom-code`** (0.84.0):
  they are family infrastructure, and loom-code is the always-installed
  plugin. See that changelog for the receiving side.

### Note for installed hosts

The marketplace drops from 6 loom entries to 2. Run `plugin update` to
pick up `loom-design` and the 0.84.0 `loom-code` that now carries the
family hooks; without it the retired plugins simply disappear.
