---
name: using-code-team
description: Route code tasks — new features, bug fixes, refactoring, code review, PR review, test writing, documentation. Load BEFORE code-team to select the right workflow and agents.
---

# Using Code Team

Feature development workflow with hybrid evaluation: binary checklists first, then qualitative flag gates.

## When to Use

- New feature implementation
- Bug fixes
- Code refactoring (with review)
- Any task that produces or modifies code

## Available Skills

| Skill | Purpose |
|-------|---------|
| `code-team` | Full workflow: Arch → Implement → Test → Checklist → Review → Verify |
| `domain-code` | Domain knowledge index (internal, loaded by team skill) |

## Agents Used

| Agent | Role | Model |
|-------|------|-------|
| `evaluator` | Security checklist, architecture gate, quality gate, QA gate | opus |
| `worker` | Test writing, documentation, refactoring | sonnet |
| `context-compressor` | Compress context between phases | haiku |

## Domain Files (in `skills/domain-code/`)

| Type | File | Purpose |
|------|------|---------|
| Protocol | `protocols/test-writing.md` | Unit test generation SOP |
| Protocol | `protocols/doc-writing.md` | Documentation generation SOP |
| Protocol | `protocols/refactoring.md` | Mechanical refactoring SOP |
| Checklist | `checklists/security-checklist.md` | Binary security gate |
| Rubric | `rubrics/arch-gate.md` | Architecture fitness flags |
| Rubric | `rubrics/quality-gate.md` | Code quality flags |
| Rubric | `rubrics/qa-gate.md` | Final QA flags |
| Standard | `standards/code-conventions.md` | Shared coding rules (SSOT) |

## External Dependencies

- `feature-dev:code-architect` (Anthropic official plugin) — used in Step 1 for architecture planning

## Quick Start

For a full feature development cycle, invoke `code-team`.
For standalone tasks, dispatch `worker` or `evaluator` with the appropriate domain file.
