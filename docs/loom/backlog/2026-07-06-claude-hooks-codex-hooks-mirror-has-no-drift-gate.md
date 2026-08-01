---
name: 2026-07-06-claude-hooks-codex-hooks-mirror-has-no-drift-gate
description: .claude/hooks ↔ .codex/hooks mirror has no drift gate
status: OPEN
origin: PR (this branch) Tasks 6+7 quality review, 2026-07-06 — remind-memory-mirror.sh became the SECOND byte-identical .claude/.codex hook pair (first: validate-skill-folder-structure.sh, since 2026-06-17); nothing enforces identity (check-codex-manifest-drift.sh gates only */plugin.json; loom-code CI pytests .claude/hooks/ only; CLAUDE.md documents the manifest mirror, not the hook-script mirror)
start: third mirrored hook-script pair, or next touch of check-codex-manifest-drift.sh — whichever comes first
---

- Start: third mirrored hook-script pair, or next touch of
  check-codex-manifest-drift.sh — whichever comes first
- Origin: PR (this branch) Tasks 6+7 quality review, 2026-07-06 —
  remind-memory-mirror.sh became the SECOND byte-identical
  .claude/.codex hook pair (first: validate-skill-folder-structure.sh,
  since 2026-06-17); nothing enforces identity
  (check-codex-manifest-drift.sh gates only */plugin.json; loom-code CI
  pytests .claude/hooks/ only; CLAUDE.md documents the manifest mirror,
  not the hook-script mirror)
- What: Rule of Three — at the third pair (or next drift-tooling
  touch), add a cmp-based identity test or extend the drift hook to
  cover .claude/hooks/*.sh ↔ .codex/hooks/*.sh.
