---
name: using-domain-teams
description: >-
  Route to the right domain team. Use when starting any domain task —
  coding, documentation, testing, deployment, research, design, or planning.
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
| `qa-team` | Ensure it's verified end-to-end (tested beyond unit) | TEST-PLAN.md, coverage reports |
| `devops-team` | Ensure it's shipped safely (deployable, observable) | DEPLOY-SPEC.md, CI/CD, IaC |
| `research-team` | Ensure we know enough (trustworthy sources, risks visible) | Research reports, analysis |
| `design-team` | Ensure it's used well (accessible, intuitive) | UI specs, wireframes |
| `planning-team` | Ensure the right thing gets built (scope, direction) | PRODUCT-SPEC.md |
| `skill-team` | Build/modify domain-team skills with convention discipline | New/refactored skill directories + 3-commit branches |

## Intent Routing

| You want to... | Invoke |
|----------------|--------|
| Write code, fix bugs, refactor, write tests | `code-team` |
| Write TECH-SPEC.md | `code-team` |
| Write README, API docs, architecture docs | `docs-team` |
| Assess codebase health or tech debt | `docs-team` |
| Create E2E / integration / performance test plans | `qa-team` |
| Analyze test coverage gaps | `qa-team` |
| Design CI/CD pipeline or deployment strategy | `devops-team` |
| Write Dockerfiles, IaC, or monitoring configs | `devops-team` |
| Research a topic, analyze market/competition | `research-team` |
| Investment analysis, valuation, asset allocation, macro regime call | `research-team` |
| Evaluate a tech stack or OSS | `research-team` |
| Design UI/UX, create wireframes | `design-team` |
| Audit accessibility | `design-team` |
| Define product scope, write PRODUCT-SPEC.md | `planning-team` |
| Start a new project (企画) | `planning-team` |
| Create a new domain-team skill | `skill-team` |
| Refactor a team with primary-source grounding | `skill-team` |

## Ambiguous Cases

| Situation | Recommendation |
|-----------|---------------|
| Need research to inform a spec | `research-team` first → then `planning-team` |
| Need spec before coding | `planning-team` (PRODUCT-SPEC) → `code-team` (TECH-SPEC) |
| Need design + code implementation | `design-team` (spec) → `code-team` (implement) |
| Need test plan + test code | `qa-team` (TEST-PLAN.md) → `code-team` (implement tests) |
| Need deployment after coding | `code-team` (code) → `devops-team` (deploy) |
| Full project lifecycle | `planning-team` → `code-team` → `qa-team` → `devops-team` |
| Task spans multiple domains | Decompose and invoke teams sequentially |

## Shared Agents

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Execute tasks with protocol guidance | sonnet |
| `evaluator` | Run quality gates | opus |
