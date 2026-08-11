---
name: 2026-07-10-ascii-graph-trigger-fix-post-ship-telemetry-a-b-re-run
description: ascii-graph trigger fix — post-ship telemetry A/B re-run
status: OPEN
origin: 2026-07-10 trigger-rate analysis session; brief `docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md`; dogfood `docs/loom/dogfood/2026-07-10-visual-trigger-weak-model-dogfood.md` (n=2/arm directional gate-check — the real A/B is this re-run).
start: ~2-4 weeks after PR #529 + PR #530 merge (needs organic session volume on the shipped trigger card + preload).
---

- Start: ~2-4 weeks after PR #529 + PR #530 merge (needs organic session
  volume on the shipped trigger card + preload).
- Origin: 2026-07-10 trigger-rate analysis session; brief
  `docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md`; dogfood
  `docs/loom/dogfood/2026-07-10-visual-trigger-weak-model-dogfood.md`
  (n=2/arm directional gate-check — the real A/B is this re-run).
- What: re-run the session-log telemetry (grep `~/.claude/projects/**/*.jsonl`:
  Skill invocations of `ascii-graph` vs assistant-drawn box-drawing lines
  containing CJK) against the 2026-07-10 baseline — 1/1042 organic firing,
  56 CJK hand-drawn sessions, family-relay.md Read 1/216, visual-companion.md
  0/56. Success = organic firing up, CJK hand-drawn share down. While there,
  triage the deferred debts recorded in both PR bodies (escape_for_json
  triplication, awk §(b.1) boundary, regex-vs-YAML description test).
- 2026-08-12 scope addition (feat/ascii-graph-generative-trigger, toolkit
  0.6.0): the card gained a GENERATIVE explain-a-flow sentence (branch A/B:
  candidate 2/2 skill-invoked, anti-decoration 0/1, baseline 1/2 — n=2
  directional; dogfood
  `docs/loom/dogfood/2026-08-12-generative-trigger-card-ab.md`). This
  re-run additionally measures: (a) organic generative firings
  (explain-shaped turns → skill invocation), (b) the carried instruction
  🟡 — "lead the explanation with the generated diagram" two-readings
  ambiguity: any reword ships only WITH a fresh A/B leg here (store:
  a-behavioral-ab-binds-the-exact-wording-it-tested), (c) a Codex-side
  injection probe for this plugin's SessionStart card (never separately
  probed; loom-code's hook shape verified, this card's assumed).
