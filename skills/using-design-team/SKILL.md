---
name: using-design-team
description: Entry point for the design-team plugin. Explains when to use it, what agents are available, and how to route tasks. Load this skill at session start for design-related tasks.
---

# Using Design Team

This plugin provides a design review workflow with parallel specialized reviewers.

## When to Use

- UI design and wireframes
- UX strategy and user journeys
- Frontend implementation review
- Accessibility audits
- Visual design feedback

## Available Skills

| Skill | Purpose |
|-------|---------|
| `design-team:design-team` | Full workflow: Generate → Review (parallel) → Revise |

## Available Agents

| Agent | Role | Model |
|-------|------|-------|
| `ux-strategist` | UX strategy, user journeys, value propositions | opus |
| `ui-reviewer` | UI structure, IA, interaction patterns, OOUI | sonnet |
| `visual-reviewer` | Visual design, typography, color, brand consistency | opus |
| `a11y-reviewer` | Accessibility, WCAG compliance, keyboard navigation | sonnet |
| `design-summarizer` | Compress design-related text for other agents | haiku |

## Routing

Reviewers are dispatched based on output type:
- Strategy / journey → `ux-strategist`
- Wireframe / UI spec / frontend code → `ui-reviewer`
- Visual asset → `visual-reviewer`
- Any UI output → `a11y-reviewer` (always runs alongside others)

## Quick Start

For a full design review cycle, invoke `design-team:design-team`.
For standalone reviews, dispatch individual agents directly.
