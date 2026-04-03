---
name: using-code-team
description: Entry point for the code-team plugin. Explains when to use it, what agents are available, and how to route tasks. Load this skill at session start for code-related tasks.
---

# Using Code Team

This plugin provides a complete feature development workflow with specialized agents.

## When to Use

- New feature implementation
- Bug fixes
- Code refactoring (with review)
- Any task that produces or modifies code

## Available Skills

| Skill | Purpose |
|-------|---------|
| `code-team` | Full workflow: Arch → Implement → Test → Review → Verify |

## Available Agents

| Agent | Role | Model |
|-------|------|-------|
| `code-arch-reviewer` | Architecture & design decision review | opus |
| `code-reviewer` | Code quality, bugs, security review | sonnet |
| `shared-qa-evaluator` | Final quality verification | opus |
| `code-test-writer` | Unit test generation | sonnet |
| `code-doc-writer` | Documentation generation | haiku |
| `code-refactor-agent` | Mechanical refactoring execution | sonnet |
| `code-summarizer` | Compress code-related text for other agents | haiku |

## External Dependencies

- `feature-dev:code-architect` (Anthropic official plugin) — used in Step 1 for architecture planning

## Quick Start

For a full feature development cycle, invoke `code-team`.
For standalone tasks (just review, just tests), dispatch individual agents directly.
