# Monkey Skills

Personal agent skills marketplace — **4 plugins** covering domain-team quality
gates, Obsidian vault workflows, philosophical thinking frameworks, and
skill-authoring tools.

## Plugins at a glance

| Plugin | Skills | Slash commands | Description |
|--------|-------:|---------------:|-------------|
| `domain-teams` | 10 | 9 | Domain team skills with checkpoint-based quality gates (code, docs, qa, devops, design, research, planning, copywriting) + skill-team meta-skill + router |
| `obsidian` | 13 + 1 agent | 1 | Obsidian vault workflows — daily notes, diagrams, dashboards + imported kepano & axtonliu visual skills |
| `philosophers-toolkit` | 12 | 12 | Philosophical thinking frameworks for problem clarification and deeper reasoning |
| `dev-workflow` | 1 | 1 | Skill creation and eval workflows (adapted from upstream) |

**Total**: 36 skills, 23 slash commands across 4 plugins.

## Architecture: Checkpoint-Based Quality Gates + Open Domain Knowledge

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
```

Applies to `domain-teams` plugin; other plugins use lighter-weight patterns.

## Plugin: `domain-teams`

Domain team skills with primary-source grounding and checkpoint-based quality
gates. All 9 teams launch `worker` (sonnet) for execution + `evaluator` (opus)
for quality-gate verdicts.

### Router

| Type | Name | Role |
|------|------|------|
| Skill | `using-domain-teams` | Entry point — routes requests to the right team |

### Teams

| Team | Slash cmd | Role | Notable grounding |
|------|-----------|------|-------------------|
| `planning-team` | `/planning` | Cross-domain project planning (企画); produces PRODUCT-SPEC.md | Business thesis + JTBD |
| `code-team` | `/code` | Code development; implements features, fixes bugs, writes TECH-SPEC.md | External dep: `feature-dev:code-architect` |
| `docs-team` | `/docs` | Documentation + codebase assessment; README, API docs, tech debt audit | Diátaxis + Google Developer Style + JTAP |
| `qa-team` | `/qa` | Test strategy and planning; E2E, integration, performance | ISTQB + ISO/IEC/IEEE 29119 + VSTeP / HAYST / ゆもつよ |
| `devops-team` | `/devops` | Ship code safely; CI/CD, Dockerfiles, IaC, deployment, monitoring | Google SRE + DORA + 12-Factor + Continuous Delivery |
| `design-team` | `/design` | Design with accessibility + quality review; UI, wireframes, UX strategy | Norman / Nielsen / WCAG 2.2 + 原研哉 / 深澤 / 黒須 / 上野 |
| `research-team` | `/research` | Primary-source-grounded research; investment analysis, regime diagnosis | Systematic-review rigor + Investment Clock + Dalio + CAPE |
| `copywriting-team` | `/copywriting` | Persuasive marketing copy — landing pages, キャッチコピー, email, voice guides, audits | 神田 PASONA + 谷山 + 今泉 + 川喜田 + Cialdini + Schwartz + McQuarrie & Mick + Lakoff + Thornton |
| `skill-team` | `/skill` | Meta-skill: build or modify domain-team skills with convention discipline | Anthropic Agent Skills spec + Conventional Commits + Semver |

Each team skill directory is self-contained with `SKILL.md` + `protocols/` +
`checklists/` + `rubrics/` + `standards/` + optional `research/` (grounding
audit trails).

## Plugin: `obsidian`

Obsidian vault daily workflows, visual tools, file intelligence, and dashboard
design. Combines original skills with imports from the Obsidian community.

### Router + Agent

| Type | Name | Role |
|------|------|------|
| Skill | `using-obsidian` | Entry point — routes vault tasks to the right skill |
| Agent | `obsidian-vault-organizer` | Vault cleanup and organization (haiku) |

### Original skills (this project)

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `obsidian-daily` | `/obsidian` | Start the day — daily note, priorities |
| `obsidian-vault-setup` | — | Interactive vault configurator |
| `obsidian-tldr` | — | Save conversation summary to vault |
| `obsidian-file-intel` | — | Extract file content (PDF/PPTX/XLSX/DOCX/etc.) into Obsidian notes |
| `dashboard-design` | — | Dashboard design workflow |

### Imported from Steph Ango (kepano) — MIT

Upstream: [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)

| Skill | Role |
|-------|------|
| `defuddle` | Extract clean markdown from web pages (removes clutter) |
| `obsidian-bases` | Create and edit Obsidian Bases (.base files) |
| `obsidian-cli` | Interact with vaults via Obsidian CLI |
| `obsidian-markdown` | Obsidian-flavored Markdown (wikilinks, embeds, callouts, properties) |

### Imported from Axton Liu (axtonliu) — MIT

Upstream: [`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)

| Skill | Role |
|-------|------|
| `obsidian-canvas-creator` | Create Canvas files (MindMap / freeform layouts) — combines axtonliu base with kepano's json-canvas |
| `obsidian-excalidraw-diagram` | Generate Excalidraw diagrams (mind maps, animated flowcharts) |
| `obsidian-mermaid-visualizer` | Create Mermaid diagrams (flowcharts, architecture, mindmaps) |

## Plugin: `philosophers-toolkit`

Philosophical thinking frameworks for problem clarification and deeper
reasoning. Each framework is a self-contained skill with references, cases,
and guided questioning protocols.

### Router

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `using-philosophers-toolkit` | `/think` | Route to the best philosophical thinking method |

### Thinking methods (11)

| Skill | Slash cmd | Method |
|-------|-----------|--------|
| `aristotle-first-principles` | `/first-principles` | First-principles decomposition — rebuild from fundamental truths |
| `aristotle-four-causes` | `/four-causes` | Aristotle's Four Causes — material / formal / efficient / final |
| `descartes-methodical-doubt` | `/doubt` | Systematic doubt until only the indubitable remains |
| `hegelian-dialectics` | `/dialectics` | Thesis / antithesis / synthesis for trade-off analysis |
| `popper-falsifiability` | `/falsify` | Turn vague claims into testable hypotheses |
| `socratic-method` | `/socratic` | Socratic dialogue — guide through questioning, not answering |
| `hansei` (反省) | `/hansei` | Blame-free retrospective + inward reflection (JP) |
| `ikigai` (生き甲斐) | `/ikigai` | 4-axis purpose diagnosis (JP) |
| `kaizen` (改善) | `/kaizen` | Continuous small improvement cycles (JP) |
| `shu-ha-ri` (守破離) | `/shu-ha-ri` | Diagnose mastery stage; stage-appropriate guidance (JP) |
| `wabi-sabi` (侘寂) | `/wabi-sabi` | Find beauty in imperfection; cut the excess (JP) |

## Plugin: `dev-workflow`

Skill creation and eval workflows.

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `skill-creator-advance` | `/skill-creator-advance` | Create new skills and iteratively improve them via eval-driven loop (draft → test → review → improve) |

**Upstream chain** (MIT — see [ATTRIBUTION.md](ATTRIBUTION.md) for full detail):

```
Anthropic skill-creator (MIT)
  → AllanYiin (尹相志) skill-creator-advanced (MIT, github.com/AllanYiin/Amon)
    → kouko dev-workflow/skill-creator-advance (MIT)
```

## Installation

### Claude Code

```bash
claude plugin marketplace add kouko/monkey-skills
# All 4 plugins become available:
#   domain-teams, obsidian, philosophers-toolkit, dev-workflow
```

Install specific plugins only:

```bash
claude plugin install domain-teams@kouko/monkey-skills
claude plugin install obsidian@kouko/monkey-skills
# ...etc.
```

### Gemini CLI

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md).

## Repository Structure

```
monkey-skills/
├── .claude-plugin/
│   └── marketplace.json             ← Lists all 4 plugins
│
├── domain-teams/                    ← Plugin: domain-teams
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   │   ├── worker.md                ← sonnet
│   │   └── evaluator.md             ← opus
│   ├── commands/                    ← 9 slash commands
│   ├── skills/
│   │   ├── using-domain-teams/      ← Router
│   │   ├── planning-team/           ← SKILL.md + protocols/ + checklists/ + rubrics/ + standards/
│   │   ├── code-team/
│   │   ├── docs-team/
│   │   ├── qa-team/
│   │   ├── devops-team/
│   │   ├── design-team/
│   │   ├── research-team/
│   │   ├── copywriting-team/
│   │   └── skill-team/              ← Meta-skill for building domain-team skills
│   └── CHANGELOG.md
│
├── obsidian/                        ← Plugin: obsidian
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   │   └── obsidian-vault-organizer.md  ← haiku
│   ├── commands/                    ← /obsidian
│   └── skills/
│       ├── using-obsidian/          ← Router
│       ├── obsidian-daily/
│       ├── obsidian-vault-setup/
│       ├── obsidian-tldr/
│       ├── obsidian-file-intel/
│       ├── dashboard-design/
│       ├── defuddle/                ← 3rd-party (kepano, MIT)
│       ├── obsidian-bases/          ← 3rd-party (kepano, MIT)
│       ├── obsidian-cli/            ← 3rd-party (kepano, MIT)
│       ├── obsidian-markdown/       ← 3rd-party (kepano, MIT)
│       ├── obsidian-canvas-creator/ ← 3rd-party (axtonliu + kepano, MIT)
│       ├── obsidian-excalidraw-diagram/  ← 3rd-party (axtonliu, MIT)
│       └── obsidian-mermaid-visualizer/  ← 3rd-party (axtonliu, MIT)
│
├── philosophers-toolkit/            ← Plugin: philosophers-toolkit
│   ├── .claude-plugin/plugin.json
│   ├── commands/                    ← 12 slash commands
│   └── skills/
│       ├── using-philosophers-toolkit/
│       ├── aristotle-first-principles/
│       ├── aristotle-four-causes/
│       ├── descartes-methodical-doubt/
│       ├── hegelian-dialectics/
│       ├── popper-falsifiability/
│       ├── socratic-method/
│       ├── hansei/
│       ├── ikigai/
│       ├── kaizen/
│       ├── shu-ha-ri/
│       └── wabi-sabi/
│
├── dev-workflow/                    ← Plugin: dev-workflow
│   ├── .claude-plugin/plugin.json
│   ├── commands/                    ← /skill-creator-advance
│   ├── skills/
│   │   └── skill-creator-advance/   ← 3rd-party chain (Anthropic → AllanYiin → kouko, MIT)
│   │       ├── SKILL.md
│   │       ├── LICENSE              ← AllanYiin + kouko copyright
│   │       ├── NOTICE               ← Upstream chain detail
│   │       ├── agents/
│   │       ├── scripts/
│   │       └── references/
│   └── CHANGELOG.md
│
├── LICENSE                          ← Project MIT (kouko) + third-party pointer
├── ATTRIBUTION.md                   ← Summary of all 3rd-party imports
├── README.md                        ← This file
├── CLAUDE.md                        ← Claude Code context
├── GEMINI.md                        ← Gemini CLI context
├── AGENTS.md                        ← Codex / Copilot CLI context
├── gemini-extension.json            ← Gemini CLI extension manifest
└── .github/
    └── workflows/
        └── skill-structure.yml      ← CI: SKILL.md structure + Conventional Commits
```

## Slash Commands Reference

All 23 commands available after plugin installation:

**domain-teams (9)**: `/planning` `/code` `/docs` `/qa` `/devops` `/design` `/research` `/copywriting` `/skill`

**obsidian (1)**: `/obsidian`

**philosophers-toolkit (12)**: `/think` `/first-principles` `/four-causes` `/doubt` `/dialectics` `/falsify` `/socratic` `/hansei` `/ikigai` `/kaizen` `/shu-ha-ri` `/wabi-sabi`

**dev-workflow (1)**: `/skill-creator-advance`

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for the
project-level notice and pointers to per-component license files.

Third-party components retain their original copyright notices (Steph Ango,
Axton Liu, AllanYiin / 尹相志, Anthropic). Full attribution with upstream
URLs, licenses, and modification summaries: see
[ATTRIBUTION.md](ATTRIBUTION.md).

To report a license or attribution concern, open an issue at
https://github.com/kouko/monkey-skills/issues.
