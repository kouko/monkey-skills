---
name: using-domain-teams
description: >-
  Route to the right domain team. Use when starting any domain task —
  coding, documentation, research, design, or planning.
  Do NOT use when you already know which team to invoke.
  ドメインチーム案内。領域團隊導引。
---

# Using Domain Teams

This plugin provides domain-specialized teams with quality gates.
Each team has its own protocols, standards, and evaluation criteria.

## Available Teams

| Team | Mission | Delivers |
|------|---------|----------|
| `code-team` | Ensure it's built well (secure, sound, tested) | Code, TECH-SPEC.md, tests |
| `docs-team` | Ensure it's understood (clear docs, honest assessment) | Documentation, codebase reports |
| `research-team` | Ensure we know enough (trustworthy sources, risks visible) | Research reports, analysis |
| `design-team` | Ensure it's used well (accessible, intuitive) | UI specs, wireframes |
| `planning-team` | Ensure the right thing gets built (scope, direction) | PRODUCT-SPEC.md |

## Intent Routing

| You want to... | Invoke |
|----------------|--------|
| Write code, fix bugs, refactor, write tests | `code-team` |
| Write TECH-SPEC.md | `code-team` |
| Write README, API docs, architecture docs | `docs-team` |
| Assess codebase health or tech debt | `docs-team` |
| Research a topic, analyze market/competition | `research-team` |
| Evaluate a tech stack or OSS | `research-team` |
| Design UI/UX, create wireframes | `design-team` |
| Audit accessibility | `design-team` |
| Define product scope, write PRODUCT-SPEC.md | `planning-team` |
| Start a new project (企画) | `planning-team` |

## Ambiguous Cases

| Situation | Recommendation |
|-----------|---------------|
| Need research to inform a spec | `research-team` first → then `planning-team` |
| Need spec before coding | `planning-team` (PRODUCT-SPEC) → `code-team` (TECH-SPEC) |
| Need design + code implementation | `design-team` (spec) → `code-team` (implement) |
| Task spans multiple domains | Decompose and invoke teams sequentially |

## Shared Agents

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Execute tasks with protocol guidance | sonnet |
| `evaluator` | Run quality gates | opus |
