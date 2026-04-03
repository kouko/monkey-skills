---
name: domain-design
description: "Core knowledge base for design — UX strategy, UI interaction, visual design, accessibility. Internal: loaded by team skills, not invoked directly."
---

# Domain: Design

## Agent Role Routing

You MUST read files based ONLY on your current role:

### 1. worker (Executing/Generating)
- Read `protocols/*.md` for step-by-step implementation SOPs (if available)
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
| `checklists/` | `a11y-checklist.md` | evaluator | Binary accessibility gate (first pass) |
| `rubrics/` | `ux-strategy-gate.md` | evaluator | UX strategy flags (Ando temporal model) |
| `rubrics/` | `ui-interaction-gate.md` | evaluator | UI structure & interaction flags |
| `rubrics/` | `visual-gate.md` | evaluator | Visual design flags (Kansei) |
| `standards/` | `wcag-baseline.md` | both | Shared WCAG 2.2 AA rules (SSOT) |
