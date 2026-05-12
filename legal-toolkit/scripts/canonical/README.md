# Canonical sources (SoT)

This directory is the **single source of truth** for cross-skill data files
in `legal-toolkit`. Editing rules:

- **Only edit files here.** Never edit `skills/<skill>/assets/<file>` directly —
  those are byte-identical functional copies materialized by `distribute.py`.
- **After editing**, run from the repo root:
  ```
  python3 legal-toolkit/scripts/distribute.py
  ```
  This deploys the byte-identical copy to every skill listed in `distribute.py`'s
  `ROUTE` table.
- **Commit canonical edit + functional-copy updates in the same commit.**
  CI runs `verify-drift.py` and will fail the PR if any functional copy
  drifts from canonical.

## Current consumers

See `legal-toolkit/scripts/distribute.py:ROUTE` for the authoritative list.
As of v0.3.6, `legal-sources.json` deploys to:

- `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json`

Phase 2 (v0.4.0) extends the ROUTE with `legal-document-draft` and
`legal-incident-response`.

## Why this pattern

Anthropic skill convention: each skill is self-contained — its SKILL.md and
runtime-loaded protocols may not reach into another skill's directory tree.
But Phase 2 sibling skills need the same statute / case / 函釋 URL registry.
We resolve this by **storing the SoT outside `skills/`** and **deploying
byte-identical copies INTO each consuming skill**, with CI enforcing that
the copies never drift. Mirrors `translation-toolkit/scripts/canonical/`
precedent.

Background: `docs/superpowers/specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md`.
