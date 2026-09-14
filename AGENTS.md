<!-- Generated project guidance; source conventions live in CLAUDE.md. -->

# Monkey Skills

Personal agent skills organized into independent plugins. Domain-team skills
use checkpoint-based quality gates; each plugin owns its own runtime files and
tests.

## Common commands

- `python3 scripts/sync_codex_manifests.py <plugin>` synchronizes a plugin's
  Codex manifest from its Claude manifest.
- `python3 scripts/sync_codex_manifests.py --check <plugin>` checks manifest
  drift without writing.
- `python3 scripts/check-shared-conventions-drift.py` checks shared convention
  copies.
- `python3 -m pytest scripts/ -q` runs repository-level script tests.

Loom plugins have moved to the independent `kouko/loom-plugins` repository.
The `docs/loom/` tree in this repository is retained as historical material
only and is not part of the current plugin marketplace or runtime workflow.
