---
name: domain-code
description: "Core knowledge base for code engineering — protocols, rubrics, checklists, and standards for implementation, testing, security, and tech debt. Internal: loaded by team skills, not invoked directly."
---

# Domain: Code Engineering

## Available Knowledge

All files are available to any agent as reference.

| Directory | Content | Typical Use |
|-----------|---------|-------------|
| `protocols/` | Step-by-step SOPs | Execution guidance |
| `checklists/` | Binary pass/fail criteria | Gate evaluation, preventive self-check |
| `rubrics/` | Qualitative flag criteria | Gate evaluation, preventive self-check |
| `standards/` | Baseline rules (SSOT) | Universal reference |

## Behavioral Rules

Knowledge access is open. Role boundaries are enforced by behavior, not by reading restrictions:

- **worker / main agent**: Produces artifacts. Does NOT produce gate verdicts (PASS/FAIL/flags).
- **evaluator**: Produces verdicts. Does NOT modify artifacts or produce revised output.

## Files

| Directory | File | Purpose |
|-----------|------|---------|
| `protocols/` | `brainstorming.md` | Feature brainstorming & approach exploration SOP |
| `protocols/` | `test-writing.md` | Unit test generation SOP |
| `protocols/` | `doc-writing.md` | Documentation generation SOP |
| `protocols/` | `refactoring.md` | Mechanical refactoring SOP |
| `protocols/` | `codebase-assessment.md` | Codebase health assessment SOP |
| `checklists/` | `security-checklist.md` | Binary security gate |
| `checklists/` | `tech-debt-checklist.md` | Binary technical debt gate |
| `rubrics/` | `arch-gate.md` | Architecture fitness flags |
| `rubrics/` | `quality-gate.md` | Code quality flags |
| `rubrics/` | `qa-gate.md` | Final QA flags |
| `standards/` | `code-conventions.md` | Shared coding standards (SSOT) |
