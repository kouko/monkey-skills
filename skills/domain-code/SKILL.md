---
name: domain-code
description: "Core knowledge base for code engineering — protocols, rubrics, checklists, and standards for implementation, testing, security, and tech debt. Internal: loaded by team skills, not invoked directly."
---

# Domain: Code Engineering

## Agent Role Routing

You MUST read files based ONLY on your current role:

### 1. worker (Executing/Generating)
- Read `protocols/*.md` for step-by-step implementation SOPs
- Read `standards/*.md` to ensure your output complies with baseline rules
- DO NOT read `rubrics/` or `checklists/`

### 2. evaluator (Reviewing/Grading)
- FIRST read `checklists/*.md` for binary pass/fail checks (objective gate)
- THEN read `rubrics/*.md` for qualitative flag evaluation (subjective gate)
- Read `standards/*.md` to cross-reference objective rules
- DO NOT read `protocols/`

## Available Files

| Directory | File | Used by | Purpose |
|-----------|------|---------|---------|
| `protocols/` | `brainstorming.md` | worker | Feature brainstorming & approach exploration SOP |
| `protocols/` | `test-writing.md` | worker | Unit test generation SOP |
| `protocols/` | `doc-writing.md` | worker | Documentation generation SOP |
| `protocols/` | `refactoring.md` | worker | Mechanical refactoring SOP |
| `protocols/` | `codebase-assessment.md` | worker | Codebase health assessment SOP |
| `checklists/` | `security-checklist.md` | evaluator | Binary security gate (first pass) |
| `checklists/` | `tech-debt-checklist.md` | evaluator | Binary technical debt gate |
| `rubrics/` | `arch-gate.md` | evaluator | Architecture fitness flags |
| `rubrics/` | `quality-gate.md` | evaluator | Code quality flags |
| `rubrics/` | `qa-gate.md` | evaluator | Final QA flags |
| `standards/` | `code-conventions.md` | both | Shared coding standards (SSOT) |
