---
name: using-design-team
description: Design with accessibility and quality review. Use when designing UI, creating wireframes, planning UX strategy, auditing accessibility, reviewing visual design, implementing frontend, or writing design documentation. UI設計・UXレビュー・アクセシビリティ。介面設計・無障礙審查。
---

# Using Design Team

Design with checkpoint-based quality gates.

## When to Use

- Design brainstorming and concept development
- UI design and wireframes
- UX strategy and user journeys
- Visual design creation and specification
- Frontend implementation review
- Accessibility audits and reports
- Design documentation (style guides, pattern libraries)
- Design review and feedback

## How It Works

`design-team` uses a **checkpoint model** with four quality levels:

| Level | Behavior |
|-------|----------|
| SELF | Agent self-checks every delivery (may reference any domain file) |
| MUST | Accessibility gate auto-triggers for UI output |
| SHOULD | UX strategy + UI interaction gates auto-trigger by output type |
| MAY | Visual design gate available on request |

Agent decides how to approach the task. All domain knowledge (protocols,
checklists, rubrics, standards) is freely accessible as reference.

## Agents Used

| Agent | Role | Model |
|-------|------|-------|
| `evaluator` | A11y checklist, UX strategy gate, UI interaction gate, visual gate | opus |
| `context-compressor` | Compress context between phases | haiku |

## Quick Start

Invoke `design-team` for any design-related task.
The agent will choose the appropriate approach and run quality gates based on output type.
