# Changelog

All notable changes to the `loom-spec` plugin (formerly `spec-toolkit`) will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- `spec-expansion` §Consuming a `ui-flows.md` seed now names the seed's
  canonical per-change location (`docs/loom/<change-id>/ui-flows.md`, the same
  change folder this skill emits into) — following loom-interface-design's
  move of `ui-flows.md` off the fixed product-level path.

### Added

- `completeness-critic` now ends every run with a **machine-readable two-valued
  verdict** — `PASS_WITH_NOTES` / `NEEDS_REVISION` (aligned with loom-code's
  reviewer vocabulary; an unqualified PASS is deliberately absent — it would be
  a completeness claim, and Blind spots is non-empty by construction). Verdict
  semantics: `NEEDS_REVISION` when a severity-3 finding cannot be concretely
  re-seeded or the validator fails post-write-back. The **severity scale is now
  defined** (3 = load-bearing / 2 = should-add / 1 = polish, same scale as
  design-critic), and the write-back is documented as the sanctioned
  GENERATE-station exception to the evaluator-does-not-modify rule (repo
  CLAUDE.md). Guarded by `test_verdict_two_valued_enum` +
  `test_severity_scale_defined`.

- `spec-expansion` now reads `docs/loom/PRINCIPLES.md` as a **governing
  constraint** before expanding (new §Governing constraint — constitution→spec
  seam): the constitution bounds the fan-out scope, steers Phase ③ pruning
  priorities, and sets the NFR posture; absence is surfaced loudly (expansion
  proceeds only with an explicit "ungoverned" caveat). Closes the seam gap
  where product-principles claimed to govern spec-expansion but only the
  completeness-critic's post-hoc lens ever read the constitution. Guarded by
  `test_body_reads_principles_as_governing_constraint`.

## [0.3.1] — 2026-06-21

### Changed

`validate_spec_output.py` now accepts `## MODIFIED Requirements` and
`## REMOVED Requirements` as valid delta-block openers, not just
`## ADDED Requirements`. An OpenSpec change may add, modify, or remove
requirements; gating the delta on `ADDED` alone walled off legitimate
MODIFIED/REMOVED change-folders. Backward-compatible — every input the
validator previously accepted still passes; it only stops rejecting the
two previously-walled-off block kinds. More OpenSpec-faithful.

Known edge (out of scope, documented in the validator): a pure
`## REMOVED Requirements` delta with no scenarios still fails the
GIVEN/WHEN/THEN scenario check — a removal may legitimately carry no
scenario. That is a separate, deeper decision; this change only makes
the three block openers reachable.
