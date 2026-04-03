---
name: using-design-team
description: Design with accessibility and quality review. Use when designing UI, creating wireframes, planning UX strategy, auditing accessibility, reviewing visual design, or implementing frontend. UI設計・UXレビュー・アクセシビリティ。介面設計・無障礙審查。
---

# Using Design Team

Design review workflow with hybrid evaluation: binary a11y checklist first, then qualitative flag gates in parallel.

## When to Use

- UI design and wireframes
- UX strategy and user journeys
- Frontend implementation review
- Accessibility audits
- Visual design feedback

## Available Skills

| Skill | Purpose |
|-------|---------|
| `design-team` | Full workflow: Generate → Checklist → Review (parallel) → Revise |
| `domain-design` | Domain knowledge index (internal, loaded by team skill) |

## Agents Used

| Agent | Role | Model |
|-------|------|-------|
| `evaluator` | A11y checklist, UX strategy gate, UI interaction gate, visual gate (parallel) | opus |
| `context-compressor` | Compress context between phases | haiku |

## Domain Files (in `skills/domain-design/`)

| Type | File | Purpose |
|------|------|---------|
| Checklist | `checklists/a11y-checklist.md` | Binary accessibility gate |
| Rubric | `rubrics/ux-strategy-gate.md` | UX strategy flags (Ando temporal model) |
| Rubric | `rubrics/ui-interaction-gate.md` | UI structure & interaction flags (OOUI) |
| Rubric | `rubrics/visual-gate.md` | Visual design flags (Kansei Engineering) |
| Standard | `standards/wcag-baseline.md` | Shared WCAG 2.2 AA rules (SSOT) |

## Routing

- Strategy / journey → evaluator + `ux-strategy-gate.md`
- Wireframe / UI spec / frontend code → evaluator + `ui-interaction-gate.md`
- Visual asset → evaluator + `visual-gate.md`
- Any UI output → evaluator + `a11y-checklist.md` (always runs first)

## Quick Start

For a full design review cycle, invoke `design-team`.
For standalone reviews, dispatch `evaluator` with the appropriate domain file.
