---
name: design-team
description: App design workflow — Generate → Review (parallel) → Revise loop. Use for UI design, wireframes, mockups, UX strategy, or frontend implementation.
---

# Design Team

Semi-automatic Generate → Review → Revise loop.

## Step 1 — Generate

Create design output in main conversation
(strategy doc, UI spec, Object Map, or frontend code).

## Step 2 — Review

Dispatch reviewers in parallel by output type:
- Strategy / journey / value proposition → `ux-strategist`
- Wireframe / UI spec / Object Map / IA / frontend code → `ui-reviewer`
- Visual design (user-provided asset) → `visual-reviewer`
- Any output with UI → `a11y-reviewer` (always runs alongside others)
- Full design → all four in parallel

## Step 3 — Iterate based on verdict

- **PASS** → Done, report to user
- **PASS_WITH_NOTES** → Auto-revise based on reviewer feedback → go to Step 2
- **NEEDS_REVISION** → Stop, present issues to user, await direction

## Guard Rails

- Max 3 auto-revision rounds before escalating to user
- Visual design cannot be auto-generated — always require human input
- Only auto-revise issues reviewers flagged; do not introduce new changes
