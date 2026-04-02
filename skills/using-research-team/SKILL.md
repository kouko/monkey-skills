---
name: using-research-team
description: Entry point for the research-team plugin. Explains when to use it, what agents are available, and how to route tasks. Load this skill at session start for research-related tasks.
---

# Using Research Team

This plugin provides a deep research workflow with specialized analysts.

## When to Use

- Research and analysis tasks
- Investment and macro analysis
- Multi-source investigation
- Technology evaluation
- Market research

## Available Skills

| Skill | Purpose |
|-------|---------|
| `research-team:research-team` | Full workflow: Generate → Evaluate → Edit |

## Available Agents

| Agent | Role | Model |
|-------|------|-------|
| `research-analyst` | Deep research, multi-source investigation | opus |
| `investment-analyst` | Investment, stock, macro, market analysis | opus |
| `research-summarizer` | Compress research data for other agents | haiku |

## Routing

- General research → `research-analyst`
- Investment / stock / macro / market → `investment-analyst`
- Quality evaluation of drafts → `qa-evaluator` (from code-team plugin)

## Quick Start

For a full research cycle with quality evaluation, invoke `research-team:research-team`.
For standalone analysis, dispatch `research-analyst` or `investment-analyst` directly.
