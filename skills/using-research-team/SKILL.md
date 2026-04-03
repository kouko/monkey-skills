---
name: using-research-team
description: Route research tasks — analysis, investigation, investment analysis, stock/macro/market research, technology evaluation. Load BEFORE research-team to select the right protocol.
---

# Using Research Team

Deep research workflow with hybrid evaluation: binary citation checklist first, then qualitative flag gate.

## When to Use

- Research and analysis tasks
- Investment and macro analysis
- Multi-source investigation
- Technology evaluation
- Market research

## Available Skills

| Skill | Purpose |
|-------|---------|
| `research-team` | Full workflow: Generate → Checklist → Quality Gate → Edit |
| `domain-research` | Domain knowledge index (internal, loaded by team skill) |

## Agents Used

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Research generation (with analysis or investment protocol) | sonnet |
| `evaluator` | Citation checklist, research quality gate | opus |
| `context-compressor` | Compress context between phases | haiku |

## Domain Files (in `skills/domain-research/`)

| Type | File | Purpose |
|------|------|---------|
| Protocol | `protocols/analysis.md` | Deep research methodology SOP |
| Protocol | `protocols/investment.md` | Investment & macro analysis framework |
| Checklist | `checklists/source-citation-checklist.md` | Binary citation gate |
| Rubric | `rubrics/research-quality-gate.md` | Research quality flags |
| Standard | `standards/citation-standards.md` | Shared citation rules (SSOT) |

## Routing

- General research → worker + `analysis.md` protocol
- Investment / stock / macro / market → worker + `investment.md` protocol
- Quality evaluation → evaluator: checklist first, then quality gate

## Quick Start

For a full research cycle with quality evaluation, invoke `research-team`.
For standalone analysis, dispatch `worker` with the appropriate protocol.
