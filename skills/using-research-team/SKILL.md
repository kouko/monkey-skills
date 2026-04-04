---
name: using-research-team
description: Conduct research with citation verification. Use when researching, analyzing, evaluating tech stacks, comparing libraries, checking OSS licenses, doing investment/market analysis, writing research summaries, or quick fact-checking. 研究・分析・技術評估・開源調查。調査・技術評価。
---

# Using Research Team

Research with checkpoint-based quality gates.

## When to Use

- Deep research and analysis
- Investment and macro analysis
- Market / competitive research
- Technology evaluation
- Research summaries from existing sources
- Quick fact-check / single-question lookup
- OSS license and compliance checks

## How It Works

`research-team` uses a **checkpoint model** with four quality levels:

| Level | Behavior |
|-------|----------|
| SELF | Agent self-checks every delivery (may reference any domain file) |
| MUST | Citation gate auto-triggers when output cites sources |
| SHOULD | Research quality gate auto-triggers for deep analysis |
| MAY | OSS due diligence gate available on request |

Agent decides how to approach the task. All domain knowledge (protocols,
checklists, rubrics, standards) is freely accessible as reference.

## Agents Used

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Research generation with protocol guidance | sonnet |
| `evaluator` | Citation checklist, research quality gate | opus |
| `context-compressor` | Compress context between phases | haiku |

## Quick Start

Invoke `research-team` for any research-related task.
The agent will choose the appropriate approach and run quality gates based on output type.
