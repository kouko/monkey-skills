---
name: 2026-07-02-468-reviewer-next-touch-nits-loom-code-tech-spec-ci
description: #468 reviewer next-touch nits (loom-code TECH-SPEC + CI)
status: OPEN
origin: PR #468 whole-branch reviewer 🟢 next-touch nits (2026-07-02)
start: next loom-code/TECH-SPEC.md touch
---

- Start: next loom-code/TECH-SPEC.md touch
- Origin: PR #468 whole-branch reviewer 🟢 next-touch nits (2026-07-02)
- What: freshness-checked 2026-07-06 — (a) dimension-count drift STILL
  PRESENT: TECH-SPEC.md:420 `dimension_scores` lists 6 keys and :261
  says "7-dimension scores" for code-reviewer, whose actual contract is
  10 dimensions (agents/code-reviewer.md description); the same drift
  exists INSIDE agents/code-reviewer.md itself (verified 2026-07-06:
  its line 10 says "7-dimension scores" while its own frontmatter
  description and findings `dimension` enum say 10), so the fix touch
  should sweep the agent file too; (b) dual
  path-presentation styles (mixed backtick/plain paths) STILL PRESENT
  in TECH-SPEC.md; (c) loom CI steps sharing one `run:` block appears
  ALREADY FIXED — all four loom-*-ci.yml workflows now run one command
  per step; confirm and drop sub-item (c) at next touch.
