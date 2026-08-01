---
name: 2026-07-06-codex-hook-events-apply-patch-handler-emits-none
description: Codex hook events — apply_patch handler emits none
status: UPSTREAM
origin: 2026-07-06 live-fire test on Codex 0.139.0 — apply_patch wrote files but the rollout log carried zero hook events; official docs say apply_patch matches Edit/Write matchers, so wiring is dormant-correct
start: next Codex CLI version bump in this environment — re-run the live-fire ritual in docs/loom/codex-verification.md §remind-memory-mirror (codex exec writes a type:project note to a memory-pattern path; grep the session rollout log for the reminder fingerprint)
---

- Start: next Codex CLI version bump in this environment — re-run the
  live-fire ritual in docs/loom/codex-verification.md §remind-memory-mirror
  (codex exec writes a type:project note to a memory-pattern path; grep the
  session rollout log for the reminder fingerprint)
- Origin: 2026-07-06 live-fire test on Codex 0.139.0 — apply_patch wrote
  files but the rollout log carried zero hook events; official docs say
  apply_patch matches Edit/Write matchers, so wiring is dormant-correct
- What: BOTH mirrored repo hooks (.codex/hooks/remind-memory-mirror.sh and
  .codex/hooks/validate-skill-folder-structure.sh) are inert on Codex until
  upstream fixes ApplyPatchHandler hook emission. No local fix applies —
  matcher/payload changes cannot help when the handler never emits. On
  upstream fix: verify firing, then also confirm the payload carries
  tool_input.file_path (the script's silent-no-op tolerance would mask a
  key-name mismatch; probe with a catch-all debug hook if needed).
