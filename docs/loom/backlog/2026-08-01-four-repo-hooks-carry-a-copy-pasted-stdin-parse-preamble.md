---
name: 2026-08-01-four-repo-hooks-carry-a-copy-pasted-stdin-parse-preamble
description: Four repo hooks carry a copy-pasted stdin-parse preamble
status: open
origin: PR #636 (`check-memory-store-integrity.sh`), which deliberately copied the sibling shape rather than extracting, because extraction touches all four and was out of that branch's scope.
start: the next time a fifth hook is added, or any change is needed to how a hook reads its stdin payload — that change is a four-file edit today.
---

- Start: the next time a fifth hook is added, or any change is needed to how a
  hook reads its stdin payload — that change is a four-file edit today.
- Origin: PR #636 (`check-memory-store-integrity.sh`), which deliberately copied
  the sibling shape rather than extracting, because extraction touches all four
  and was out of that branch's scope.
- What: `.claude/hooks/check-codex-manifest-drift.sh:25-27`,
  `.claude/hooks/check-memory-store-integrity.sh:44-46`, `.claude/hooks/remind-memory-mirror.sh:26-28` and
  `.claude/hooks/validate-skill-folder-structure.sh:26-28` each carry a byte-identical three
  lines (`FILE_PATH=""`, the `command -v jq` guard, and the same
  `jq -r '.tool_input.file_path // .tool_input.notebook_path // empty'`). Four
  copies is past Rule of Three.
- Constraint on the fix: the copies are what make each hook a **standalone**
  file that no-ops safely in a repo without the others. A shared helper must keep
  that property — a sourced file that is missing has to degrade to `exit 0`, not
  to a shell error, and each hook's `[ -f … ] || exit 0` portability exit must
  survive.
