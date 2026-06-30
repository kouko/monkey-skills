# SSOT pointer — `loom-code/scripts/canonical/`

This directory does **not** contain canonical sources. It is a **pointer** that documents where the SSOT lives for files distributed across this plugin.

## Knowledge layer SSOT

| loom-code functional copy | Canonical SSOT |
|---|---|
| `skills/subagent-driven-development/standards/naming-and-functions.md` | `domain-teams/skills/code-team/standards/naming-and-functions.md` |
| `skills/subagent-driven-development/standards/pragmatic-principles.md` | `domain-teams/skills/code-team/standards/pragmatic-principles.md` |
| `skills/subagent-driven-development/standards/solid-principles.md` | `domain-teams/skills/code-team/standards/solid-principles.md` |
| `skills/subagent-driven-development/standards/tdd-standard.md` | `domain-teams/skills/code-team/standards/tdd-standard.md` |
| `skills/subagent-driven-development/standards/refactoring-standard.md` | `domain-teams/skills/code-team/standards/refactoring-standard.md` |
| `skills/subagent-driven-development/standards/app-security-standard.md` | `domain-teams/skills/code-team/standards/app-security-standard.md` |
| `skills/subagent-driven-development/standards/character-encoding-security.md` | `domain-teams/skills/code-team/standards/character-encoding-security.md` |
| `skills/subagent-driven-development/rubrics/quality-gate.md` | `domain-teams/skills/code-team/rubrics/quality-gate.md` |
| `skills/subagent-driven-development/rubrics/arch-gate.md` | `domain-teams/skills/code-team/rubrics/arch-gate.md` |
| `skills/subagent-driven-development/checklists/security-checklist.md` | `domain-teams/skills/code-team/checklists/security-checklist.md` |
| `skills/subagent-driven-development/checklists/spec-consistency.md` | `domain-teams/skills/code-team/checklists/spec-consistency.md` |
| `skills/tdd-iron-law/standards/tdd-standard.md` | `domain-teams/skills/code-team/standards/tdd-standard.md` |

## Drift management policy

1. Edits to standards / rubrics / checklists content MUST land first in `domain-teams/skills/code-team/` (canonical).
2. Same PR runs `loom-code/scripts/distribute.py` to sync functional copies.
3. CI runs `loom-code/scripts/verify-drift.py`; any byte diff fails the build.
4. Each functional copy carries an HTML comment header pointing back here:
   ```markdown
   <!--
   FUNCTIONAL COPY — DO NOT EDIT IN PLACE
   SSOT: domain-teams/skills/code-team/<subdir>/<filename>
   Sync via: loom-code/scripts/distribute.py
   -->
   ```

## Codex manifest sync

The Codex plugin manifest (`loom-code/.codex-plugin/plugin.json`) derives its **shared** fields from the Claude SSOT (`loom-code/.claude-plugin/plugin.json`) while keeping a Codex-only `interface` block.

| Script | Verb | Effect |
|---|---|---|
| `scripts/sync_codex_manifests.py loom-code` | (no flag) | Rewrite the Codex manifest's shared fields from the Claude SSOT; `interface` preserved verbatim. |
| `scripts/sync_codex_manifests.py loom-code --check` | `--check` | Pure read; exit non-zero on divergence (CI drift gate), zero when synced. |

Stdlib only (`json`). Mirrors the `distribute.py` (write) / `verify-drift.py` (`--check`) split used for the knowledge layer above.

## Why this pattern

Mirrors `legal-toolkit/scripts/canonical/` (Phase 1.10) and `dev-workflow:complexity-critique` mindset functional-copy arrangement (see `domain-teams:code-team/SKILL.md` §Resource Manifest cross-plugin paragraph). Keeps each plugin runtime self-contained while preserving a single editable source of truth.
