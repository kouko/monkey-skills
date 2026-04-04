---
name: using-code-team
description: Develop code with quality gates and review. Use when implementing features, fixing bugs, refactoring, reviewing code/PRs, writing tests, writing documentation, assessing codebase health, or auditing tech debt. 實作・修 bug・重構・程式碼審查。コード実装・バグ修正。
---

# Using Code Team

Code development with checkpoint-based quality gates.

## When to Use

- New feature implementation
- Bug fixes
- Code refactoring
- Documentation (SPEC, README, API docs)
- Config / boilerplate creation
- Test writing
- Codebase assessment / tech debt audit
- Any task in a code project

## How It Works

`code-team` uses a **checkpoint model** with four quality levels:

| Level | Behavior |
|-------|----------|
| SELF | Agent self-checks every delivery (may reference any domain file) |
| MUST | Security + Architecture gates auto-trigger for code changes |
| SHOULD | Quality gate auto-triggers for significant changes |
| MAY | QA, tech debt gates available on request |

Agent decides how to approach the task. All domain knowledge (protocols,
checklists, rubrics, standards) is freely accessible as reference.

## Agents Used

| Agent | Role | Model |
|-------|------|-------|
| `evaluator` | Security checklist, architecture gate, quality gate | opus |
| `worker` | Execute large tasks with protocol guidance | sonnet |
| `context-compressor` | Compress context between phases | haiku |

## External Dependencies

- `feature-dev:code-architect` (Anthropic official plugin) — available for complex architecture planning

## Quick Start

Invoke `code-team` for any code-related task.
The agent will choose the appropriate approach and run quality gates based on output type.
