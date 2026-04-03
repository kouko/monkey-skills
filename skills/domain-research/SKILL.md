---
name: domain-research
description: "Core knowledge base for research — analysis protocols, investment frameworks, citation checklists, and shared standards. Internal: loaded by team skills, not invoked directly."
---

# Domain: Research

## Agent Role Routing

You MUST read files based ONLY on your current role:

### 1. worker (Executing/Generating)
- Read `protocols/*.md` for research methodology SOPs
- Read `standards/*.md` for citation and output format rules
- DO NOT read `rubrics/` or `checklists/`

### 2. evaluator (Reviewing/Grading)
- FIRST read `checklists/*.md` for binary pass/fail checks (objective gate)
- THEN read `rubrics/*.md` for qualitative flag evaluation (subjective gate)
- Read `standards/*.md` to cross-reference objective rules
- DO NOT read `protocols/`

## Available Files

| Directory | File | Used by | Purpose |
|-----------|------|---------|---------|
| `protocols/` | `analysis.md` | worker | Deep research methodology SOP |
| `protocols/` | `investment.md` | worker | Investment & macro analysis framework |
| `checklists/` | `source-citation-checklist.md` | evaluator | Binary citation gate (first pass) |
| `rubrics/` | `research-quality-gate.md` | evaluator | Research quality flags |
| `standards/` | `citation-standards.md` | both | Shared citation & output rules (SSOT) |
