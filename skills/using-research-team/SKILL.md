---
name: using-research-team
description: Conduct research with citation verification. Use when researching, analyzing, evaluating tech stacks, comparing libraries, checking OSS licenses, or doing investment/market analysis. 研究・分析・技術評估・開源調查。調査・技術評価。
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
| Protocol | `protocols/research.md` | General research methodology SOP (fallback) |
| Protocol | `protocols/market-analysis.md` | Market & industry analysis SOP |
| Protocol | `protocols/competitive-analysis.md` | Competitive & competitor analysis SOP |
| Protocol | `protocols/academic-research.md` | Academic & theoretical research SOP |
| Protocol | `protocols/investment.md` | Investment & macro analysis framework |
| Protocol | `protocols/stack-evaluation.md` | Tech stack & OSS evaluation SOP |
| Checklist | `checklists/source-citation-checklist.md` | Binary citation gate |
| Rubric | `rubrics/research-quality-gate.md` | Research quality flags |
| Standard | `standards/citation-standards.md` | Shared citation rules (SSOT) |

## Routing

### Worker (Generate)

- General research / analysis → worker + `protocols/research.md`
- Market / industry analysis → worker + `protocols/market-analysis.md`
- Competitive / competitor analysis → worker + `protocols/competitive-analysis.md`
- Academic / theoretical research → worker + `protocols/academic-research.md`
- Investment / stock / macro → worker + `protocols/investment.md`
- Tech stack / library / OSS evaluation → worker + `protocols/stack-evaluation.md`

### Evaluator (Review)

- Any research output → evaluator + `source-citation-checklist.md` (always runs first)
- Quality evaluation → evaluator + `research-quality-gate.md`

## Quick Start

For a full research cycle with quality evaluation, invoke `research-team`.
For standalone analysis, dispatch `worker` with the appropriate protocol.
