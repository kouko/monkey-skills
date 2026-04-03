---
name: domain-research
description: "Core knowledge base for research — analysis protocols, investment frameworks, tech stack evaluation, OSS due diligence, citation checklists, and standards. Internal: loaded by team skills, not invoked directly."
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
| `protocols/` | `stack-evaluation.md` | worker | Tech stack & OSS evaluation SOP |
| `checklists/` | `source-citation-checklist.md` | evaluator | Binary citation gate (first pass) |
| `checklists/` | `oss-due-diligence.md` | evaluator | Binary OSS compliance gate |
| `rubrics/` | `research-quality-gate.md` | evaluator | Research quality flags |
| `standards/` | `citation-standards.md` | both | Shared citation & output rules (SSOT) |
| `standards/` | `oss-safety.md` | both | OSS licensing & production-readiness rules (SSOT) |
