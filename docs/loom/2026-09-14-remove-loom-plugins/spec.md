# Remove Loom plugins from monkey-skills — spec
intent: 2026-09-14-remove-loom-plugins@ad0eb01d9
pre-build-review: not-required — the user already confirmed the removal scope
confirmed-behavior: 2026-09-14 @62d8036

## Requirements
REQ-1 — marketplace scope
  WHEN a user opens the monkey-skills marketplace, the marketplace shall list only the remaining plugins → Acceptance #1
REQ-2 — historical access
  WHEN a user needs prior Loom context, the repository shall retain its historical Loom records → Acceptance #4

## Design decision
Remove the three Loom plugin roots and all Loom-only operational surfaces from
monkey-skills. Keep `docs/loom/` as history and point users to the independent
repository. This is agent-decided within the user's confirmed full-cleanup scope.

## Alternatives considered
- Keep compatibility stubs: rejected because they would leave duplicate install surfaces.
- Delete historical records: rejected because provenance must remain available.

## Current state evidence
- Forward: `.claude-plugin/marketplace.json` publishes the plugin list.
- Reverse: `loom-code/`, `loom-design/`, and `loom-workflow/` are former plugin roots.
- Error: CI and hooks contain references to those roots.
- Data: `docs/loom/` contains historical intent, plans, and evidence.
- Boundary: the independent `kouko/loom-plugins` repository owns current Loom code.

## UI flows
1. Marketplace listing → Loom entries are absent; remaining entries remain installable.
2. Historical lookup → `docs/loom/` remains readable; current Loom link points to `kouko/loom-plugins`.
