# domain-teams

**Version**: 5.2.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Domain team skills with primary-source grounding and checkpoint-based quality
gates. 9 teams share a single `worker` (sonnet) + `evaluator` (opus) agent pair.

## Architecture

```
Team Skill (checkpoint orchestrator)
  ├── worker (sonnet)    ← protocols/ + standards/
  └── evaluator (opus)   ← checklists/ + rubrics/ + standards/

Four-level quality gates:
  SELF    → Agent self-checks every delivery
  MUST    → Auto-trigger, non-skippable (e.g., security, a11y, citation)
  SHOULD  → Auto-trigger, skippable with reason (e.g., quality, UX)
  MAY     → User-requested only (e.g., QA, tech debt, visual)

Domain knowledge (colocated in each team skill directory, open access):
  protocols/   → Step-by-step SOPs (execution guidance)
  checklists/  → Binary pass/fail criteria (gate evaluation)
  rubrics/     → Qualitative flag criteria (gate evaluation)
  standards/   → Baseline rules (shared SSOT)
  research/    → Grounding audit trails (optional)
```

## Router

| Type | Name | Role |
|------|------|------|
| Skill | `using-domain-teams` | Entry point — routes requests to the right team |

## Teams

| Team | Slash cmd | Role | Notable grounding |
|------|-----------|------|-------------------|
| `planning-team` | `/planning` | Cross-domain project planning (企画); produces PRODUCT-SPEC.md | Business thesis + JTBD |
| `code-team` | `/code` | Code development; implements features, fixes bugs, writes TECH-SPEC.md | Clean Code (Martin 2008) + Pragmatic Programmer + SOLID + Kent Beck; external dep: `feature-dev:code-architect` |
| `docs-team` | `/docs` | Documentation + codebase assessment; README, API docs, tech debt audit | Diátaxis + Google Developer Style + JTAP |
| `qa-team` | `/qa` | Test strategy and planning; E2E, integration, performance | ISTQB + ISO/IEC/IEEE 29119 + VSTeP / HAYST / ゆもつよ |
| `devops-team` | `/devops` | Ship code safely; CI/CD, Dockerfiles, IaC, deployment, monitoring | Google SRE + DORA + 12-Factor + Continuous Delivery |
| `design-team` | `/design` | Design with accessibility + quality review; UI, wireframes, UX strategy | Norman / Nielsen / WCAG 2.2 + 原研哉 / 深澤 / 黒須 / 上野 |
| `research-team` | `/research` | Primary-source-grounded research; market / competitive / literature review | Systematic-review rigor + citation verification |
| `investing-team` | — | Buy/Hold/Sell verdicts on individual securities, equity research memos, portfolio rebalancing, macro regime diagnosis | IC regime + Dalio + CAPE + ISQ (Investment Signal Quality) |
| `copywriting-team` | `/copywriting` | Persuasive marketing copy — landing pages, キャッチコピー, email, voice guides, audits | 神田 PASONA + 谷山 + 今泉 + 川喜田 + Cialdini + Schwartz + McQuarrie & Mick + Lakoff + Thornton |
| `skill-team` | `/skill` | Meta-skill: build or modify domain-team skills with convention discipline | Anthropic Agent Skills spec + Conventional Commits + Semver |

10 skills total (9 teams + router). 9 slash commands (`investing-team`
accessed via `investing-toolkit` plugin router).

## Repository Structure

```
domain-teams/
├── .claude-plugin/plugin.json
├── CHANGELOG.md
├── agents/
│   ├── worker.md                ← sonnet, produces artifacts (no verdicts)
│   └── evaluator.md             ← opus, produces verdicts (no artifacts)
├── commands/                    ← 9 slash commands
└── skills/
    ├── using-domain-teams/      ← Router
    ├── planning-team/
    ├── code-team/
    ├── docs-team/
    ├── qa-team/
    ├── devops-team/
    ├── design-team/
    ├── research-team/
    ├── investing-team/
    ├── copywriting-team/
    └── skill-team/
```

Each team skill directory is self-contained with `SKILL.md` + `protocols/` +
`checklists/` + `rubrics/` + `standards/` + optional `research/` (grounding
audit trails).

## Agent Behavioral Rules

- **worker** — produces artifacts, does NOT produce gate verdicts
- **evaluator** — produces verdicts, does NOT modify artifacts
- **Knowledge access is open** — skills read any protocol / standard / checklist
  they need; behavioral separation, not read-gating

## Cross-Plugin Delegation

`investing-team` is the target of `investing-toolkit:investment-memo-writer`.
Cross-plugin delegation passes paths + structured seed context; the delegated
team loads its own standards, runs its own gates, and returns verdicts.
See repo-root `CLAUDE.md §Cross-Plugin Delegation Contract` for rules.

## License

MIT — see repository root [`LICENSE`](../LICENSE).
