# Changelog

All notable changes to the `research-toolkit` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] — 2026-07-08

### Added — deep-deep-research: fact/opinion claim classification + attribution routing

- **`claimType`/`heldBy` claim classification** (Stage 3 extraction): each
  extracted claim is now tagged `claimType: "fact"` (a checkable, verifiable
  proposition) or `"opinion"` (a viewpoint, judgment, or interpretation).
  A source statement that mixes a factual component with an opinion
  component (e.g. "GDP grew 3%, which proves the policy failed") is
  decomposed into two separate claim objects at extraction — one
  `claimType: "fact"`, one `claimType: "opinion"` — rather than emitting one
  ambiguously-typed claim; an undecomposable statement defaults to `"fact"`
  (never `"opinion"` — uncertainty always resolves toward the stricter
  check). `heldBy` captures the attributable source (named person,
  organization, or institution) for either claimType.
- **Attribution-confirmation verification path** (Stage 5, opinion claims):
  `attribution_prompt()`, `ATTRIBUTION_VERDICT_SCHEMA`, and
  `rank.py attribution-check` / `attribution_survives()` — an opinion-tagged
  claim gets a single, non-adversarial attribution-confirmation check (does
  the cited source actually hold/express this view?) instead of the
  3-voter adversarial-refutation quorum. It survives whenever
  `attributionConfirmed=true`; a missing/false field fails closed.

### Changed

- Stage 5 now routes each ranked claim by its `claimType` tag: `fact`
  claims keep the unmodified `VOTES_PER_CLAIM = 3` adversarial-refutation
  quorum; `opinion` claims route to the new attribution-confirmation check.
  Both paths write into the same ordered `work/votes.json` `vote_results`
  array Stage 6 already consumes, so synthesis is unaffected. Because
  mixed statements are already decomposed at Stage 3, no claim reaching
  Stage 5 carries an unchecked factual assertion inside an opinion wrapper.
- The same `claimType`/`heldBy`/attribution primitives are synced (via
  `scripts/sync-primitives.sh`) into `fact-check`, `cite-check`, and
  `deep-read`, which share the SSOT `deep-deep-research/scripts/{schemas,rank,prompts}.py`.
