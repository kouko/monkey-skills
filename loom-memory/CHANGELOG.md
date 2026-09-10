# Changelog

## [0.1.0] — 2026-09-10 — first independent release

- Standalone, independently installable plugin (Claude Code + Codex):
  declares no mandatory dependency on `loom-code`, `loom-design`, or
  `loom-workflow`, and no `requires-contract`.
- OKF v0.2-compatible Loom memory profile: `loom-memory/scripts/loom_memory.py`
  validates a store's frontmatter, reserved `index.md`, and Loom-specific
  required fields, and regenerates `index.md` deterministically. Pure
  stdlib, ships inside the plugin.
- `loom-memory` skill: passively-triggered Recall, Record, Reconcile, and
  Retire operations, with no fixed-stage mandatory invocation and explicit
  user approval required before Retire deletes anything.
- The repository's own memory store at `docs/loom/memory/` migrated to this
  profile — 293 lesson concepts plus one guide concept, bodies and
  descriptions preserved byte-for-byte, origins carried forward as
  `sources[].resource`.
- `loom-code` and `loom-design` continue working identically whether or not
  this plugin is installed (proved end to end at
  `2026-09-10-okf-compatible-loom-memory` W4-01): `loom_checker.py`'s
  `intake write-plan` and loom-design's skill/executable surface both run
  clean from an isolated install with no `loom-memory` sibling present.
