---
name: skill-folder-structure-hook-reads-stdin-json-and-ignores-argv
description: A PostToolUse hook script that reads its target from the stdin JSON event ignores a path passed as argv — invoking it as `bash hook.sh <path>` from CI or a reviewer shell exits 0 without checking anything, so a "structure check" step built on the hook is a silent no-op; use the repo's CI checker (which takes the plugin as an argument) for any non-hook invocation
type: gotcha
origin: think-orbit Part 1 close-out (2026-08-18) — `.claude/hooks/validate-skill-folder-structure.sh <path>` was used as a CI step and as reviewer GREEN evidence for six tasks; a probe with a nested subfolder returned exit 0, revealing the hook reads `tool_input.file_path` from stdin (`INPUT=$(cat)`) and never looks at `$1`; `tsundoku-ci.yml` carries the same dead step
---

`.claude/hooks/validate-skill-folder-structure.sh` is wired as a
PostToolUse hook: it reads the tool event as JSON on stdin and extracts
`tool_input.file_path`. Called with a path argument and no stdin, it
finds no skill root and exits 0 — the invocation looks like a check but
checks nothing.

**Why:** the CI convention of "run the same hook the editor runs" is
attractive, but the hook's input contract is the harness event, not
argv. Every downstream reader (workflow YAML, reviewer instructions,
memory recipes) that says `bash hook.sh <path>` inherits a green light
that never turned red.

**How to apply:** for CI or manual verification of skill folder
structure, run `python3 scripts/check-skill-structure.py <plugin>`
(flat folders, frontmatter, word cap); reserve the hook for its
PostToolUse wiring. When a check step exits 0 suspiciously fast, feed it
a known-bad input once before trusting it — the same probe habit as
[[a-mechanical-check-can-go-green-by-skipping]].
