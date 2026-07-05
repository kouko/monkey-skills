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
| `copywriting-team` | Ensure copy persuades (framework-grounded, ethics-safe, voice-consistent) | Landing pages, emails, キャッチコピー, voice guides, copy audits |
| `skill-team` | Build/modify domain-team skills with convention discipline | New/refactored skill directories + 3-commit branches |
| `investing-team` | Make defensible investment decisions — thesis, verdict, sizing, Taiwan-aware | Buy/Hold/Sell memos, portfolio reviews, regime calls, Taiwan equity diagnoses |

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
| Recommend Buy/Hold/Sell on a ticker | `investing-team` |
| Write a full equity research memo | `investing-team` |
| Review allocation / rebalance portfolio | `investing-team` |
| Size a position (Kelly / risk-budget) | `investing-team` |
| 台股分析 — 三大法人, 月營收, 董監持股, 融資融券 | `investing-team` |
| Macro regime call WITHOUT an investment verdict (regime substrate only) | `research-team` |
| Evaluate a tech stack or OSS | `research-team` |
| Design UI/UX, create wireframes | `design-team` |
| Audit accessibility | `design-team` |
| Define product scope, write PRODUCT-SPEC.md | `planning-team` |
| Start a new project (企画) | `planning-team` |
| Write landing page / email / sales letter (long-form copy) | `copywriting-team` |
| Write 樂天 / Amazon JP product description / POP (mid-form copy) | `copywriting-team` |
| Write キャッチコピー / tagline / headline / SNS post (short-form, 7-15 字) | `copywriting-team` |
| Draft voice-and-tone guide for a brand | `copywriting-team` |
| Generate multiple copy candidates via 曼陀羅 + Verbalized Sampling | `copywriting-team` |
| Audit existing copy for framework / ethics / voice issues | `copywriting-team` |
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
| Value proposition + marketing copy | `planning-team` (PRODUCT-SPEC value prop) → `copywriting-team` (expressions) |
| Marketing launch campaign | `planning-team` (positioning) → `copywriting-team` (copy) → `design-team` (visual pairing) |
| Brand voice + UX microcopy consistency | `copywriting-team` (voice & tone guide) → `design-team` (microcopy) |
| Task spans multiple domains | Decompose and invoke teams sequentially |
| Macro regime call + investment verdict needed | `research-team` (regime substrate) → `investing-team` (verdict + sizing) |
| Business strategy analysis vs. investment memo on same company | `research-team` (operator perspective) vs. `investing-team` (investor perspective) |

## Shared Agents

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Execute tasks with protocol guidance | sonnet |
| `evaluator` | Run quality gates | opus |

Launch instructions (`domain-teams/skills/skill-team/standards/agent-interface.md`,
echoed in every team's `SKILL.md`) are host-neutral prose. For the
concrete per-host dispatch call, see `references/claude-code-tools.md` /
`references/codex-tools.md`.
