---
name: research-team
description: Deep research workflow — Generate → Evaluate → Edit loop. Use for research, analysis, investigation, or any task requiring multi-source information gathering.
---

# Research Team

Generate → Evaluate → Edit loop.

## Step 1 — Generate

Launch `research-analyst` (or `research-investment-analyst` for investment/macro topics)
to produce research draft.

## Step 2 — Evaluate

Launch `shared-qa-evaluator` with the draft.

## Step 3 — Iterate based on verdict

- **PASS** → Done, deliver to user
- **PASS_WITH_NOTES** → Main conversation edits based on feedback
  (formatting, clarity, structure only) → re-run Step 2
- **NEEDS_REVISION** → Stop, present issues to user
  (user may choose to re-dispatch research-analyst with feedback)

## Guard Rails

- Max 2 auto-edit rounds before escalating to user
- Main conversation edits only what qa-evaluator flagged
- Factual accuracy or data freshness issues → always NEEDS_REVISION
  (main conversation cannot verify facts without web search)
