---
name: 2026-08-24-code-reviewer-sonnet-pin-two-week-telemetry
description: re-run the requested→resolved dispatch tally for loom-code:code-reviewer to verify the 0.98.0 model-sonnet frontmatter pin holds in organic sessions, and check the conditional-reversal clause against any post-merge defect a sonnet panel PASSed
status: open
origin: PR #734 (loom-code 0.98.0) — decision brief docs/loom/specs/2026-08-24-code-reviewer-sonnet-default.md schedules this telemetry; user confirmed "讓遙測說話" 2026-08-24
start: 2026-09-07 or later, once ~2 weeks of organic dispatches exist after the 0.98.0 device sync (2026-08-24)
---

Method (same scan as the 2026-08-24 tally): join Agent tool_use records in
`~/.claude/projects/*/*.jsonl` (requested `subagent_type` + `model` param)
to `subagents/agent-*.jsonl` resolved models; bucket by date >= 2026-08-24.

Pass condition: `loom-code:code-reviewer` dispatches with `model` omitted
resolve to sonnet (mirroring docs-reviewer's post-0.75.0 pattern:
inherit→sonnet, zero inherit→opus/fable). Baseline being replaced:
101/145 inherited opus/fable (2026-08-12 → 2026-08-23).

Reversal condition (from the brief, verbatim intent): a missed 🔴 that an
opus arm or post-merge evidence later catches on a branch a sonnet panel
PASSed → revert the pin and route via explicit per-dispatch model
selection instead.

Also check while in there: whether any frontier-shaped branch
(architecture / security-sensitive) was reviewed without an explicit
`model: opus` override — the silent-downgrade observation both 0.98.0
docs arms flagged.
