---
name: using-design-team
description: Design with accessibility and quality review. Use when designing UI, creating wireframes, planning UX strategy, auditing accessibility, reviewing visual design, or implementing frontend. UI設計・UXレビュー・アクセシビリティ。介面設計・無障礙審查。
---

# Using Design Team

Design review workflow with hybrid evaluation: binary a11y checklist first, then qualitative flag gates in parallel.

## When to Use

- Design brainstorming and concept development
- UI design and wireframes
- UX strategy and user journeys
- Visual design creation and specification
- Frontend implementation review
- Accessibility audits
- Design review and feedback

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

| Type | File | Used by | Purpose |
|------|------|---------|---------|
| Protocol | `protocols/design-brainstorming.md` | worker | 統合設計発想（感性工学 × 意味のイノベーション × 無意識の設計） |
| Protocol | `protocols/ux-strategy.md` | worker | UX戦略策定（安藤昌也 期間モデル × Garrett） |
| Protocol | `protocols/visual-design.md` | worker | ビジュアル設計（感性工学 × 引き算のデザイン） |
| Protocol | `protocols/ui-interaction.md` | worker | UI・インタラクション設計（無意識の設計 × OOUI） |
| Checklist | `checklists/a11y-checklist.md` | evaluator | Binary accessibility gate |
| Rubric | `rubrics/ux-strategy-gate.md` | evaluator | UX strategy flags (Ando temporal model) |
| Rubric | `rubrics/ui-interaction-gate.md` | evaluator | UI structure & interaction flags (OOUI) |
| Rubric | `rubrics/visual-gate.md` | evaluator | Visual design flags (Kansei Engineering) |
| Standard | `standards/wcag-baseline.md` | both | Shared WCAG 2.2 AA rules (SSOT) |

## Routing

### Worker (Generate)

- Design brainstorming / concept → worker + `protocols/design-brainstorming.md`
- UX strategy / user journey → worker + `protocols/ux-strategy.md`
- Visual design / color / typography → worker + `protocols/visual-design.md`
- UI spec / wireframe / frontend code → worker + `protocols/ui-interaction.md`
- Full design → worker + `protocols/design-brainstorming.md` first, then task-specific protocol

### Evaluator (Review)

- Any UI output → evaluator + `a11y-checklist.md` (always runs first)
- Strategy / journey → evaluator + `ux-strategy-gate.md`
- Wireframe / UI spec / frontend code → evaluator + `ui-interaction-gate.md`
- Visual asset → evaluator + `visual-gate.md`

## Quick Start

For a full design review cycle, invoke `design-team`.
For standalone reviews, dispatch `evaluator` with the appropriate domain file.
