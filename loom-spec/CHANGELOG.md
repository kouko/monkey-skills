# Changelog

All notable changes to the `loom-spec` plugin (formerly `spec-toolkit`) will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

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
