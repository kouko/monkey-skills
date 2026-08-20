---
name: 2026-07-06-codex-hook-events-apply-patch-handler-emits-none
description: Codex hook events — apply_patch handler emits none
status: open
blocked: waiting on openai/codex#17532
origin: 2026-07-06 live-fire test on Codex 0.139.0 — apply_patch wrote files but the rollout log carried zero hook events; official docs say apply_patch matches Edit/Write matchers, so wiring is dormant-correct
start: openai/codex#17532 closing, or the next Codex-side live re-probe in this environment, whichever first
---

- Start: openai/codex#17532 closing, or the next Codex-side live
  re-probe in this environment, whichever first
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

Upstream state re-researched 2026-08-06 (web, not a live re-probe):
the apply_patch handler gap this entry recorded was fixed upstream by
openai/codex PR #18289 (merged 2026-04-20); the symptom our live probe
hit is now more likely openai/codex#17532 (repo-local `.codex/`
config hooks silently not firing in interactive sessions — still open
as of 2026-08-06). Status stays UPSTREAM: the trigger is #17532
closing, or our next Codex-side live re-probe, whichever first.
