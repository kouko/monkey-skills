# Monkey Skills

Personal agent skills marketplace — two plugins: domain teams and Obsidian workflows.

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

## Plugins

```
monkey-skills (marketplace)
├── domain-teams            Planning / Code / Docs / QA / DevOps / Design / Research
├── obsidian                Daily notes, diagrams, vault management, dashboard design
└── philosophers-toolkit    Philosophical thinking frameworks (roadmap)
```

### Plugin: domain-teams

Domain team skills with checkpoint-based quality gates.

#### planning-team

| Type | Name | Role |
|------|------|------|
| Skill | `planning-team` | Checkpoint orchestrator for PRODUCT-SPEC.md |
| Agent | `evaluator` | Completeness checklist, cross-domain consistency gate (opus) |
| Agent | `worker` | Execute planning tasks with protocol guidance (sonnet) |

#### code-team

| Type | Name | Role |
|------|------|------|
| Skill | `code-team` | Checkpoint orchestrator for code development |
| Agent | `evaluator` | Security checklist, arch gate, quality gate (opus) |
| Agent | `worker` | Execute development tasks with protocol guidance (sonnet) |

External dependency: `feature-dev:code-architect` (Anthropic official plugin)

#### docs-team

| Type | Name | Role |
|------|------|------|
| Skill | `docs-team` | Documentation and codebase assessment |
| Agent | `worker` | Execute documentation and analysis tasks (sonnet) |
| Agent | `evaluator` | QA gate, tech debt checklist — MAY only (opus) |

#### qa-team

| Type | Name | Role |
|------|------|------|
| Skill | `qa-team` | Test strategy and planning (E2E, integration, performance) |
| Agent | `worker` | Execute test planning tasks (sonnet) |
| Agent | `evaluator` | Test plan completeness, strategy quality gates (opus) |

#### devops-team

| Type | Name | Role |
|------|------|------|
| Skill | `devops-team` | CI/CD, deployment, IaC, monitoring |
| Agent | `worker` | Execute infrastructure tasks (sonnet) |
| Agent | `evaluator` | Deployment safety, IaC quality gates (opus) |

#### design-team

| Type | Name | Role |
|------|------|------|
| Skill | `design-team` | Checkpoint orchestrator (discovery + execution) |
| Agent | `evaluator` | A11y checklist, UX/UI/visual gates (opus) |

#### research-team

| Type | Name | Role |
|------|------|------|
| Skill | `research-team` | Checkpoint orchestrator (discovery + execution) |
| Agent | `worker` | Research generation (sonnet) |
| Agent | `evaluator` | Citation checklist, quality gate (opus) |

### Plugin: obsidian

Obsidian vault daily workflows, visual tools, and dashboard design.

| Type | Name | Role |
|------|------|------|
| Skill | `using-obsidian` | Entry point and routing guide |
| Skill | `obsidian-daily` | Start the day — daily note, priorities |
| Skill | `obsidian-vault-setup` | Interactive vault configurator |
| Skill | `obsidian-tldr` | Save conversation summary to vault |
| Skill | `obsidian-file-intel` | Extract file content into Obsidian notes |
| Skill | `obsidian-mermaid-visualizer` | Create Mermaid diagrams \* |
| Skill | `obsidian-excalidraw-diagram` | Generate Excalidraw diagrams \* |
| Skill | `obsidian-canvas-creator` | Create Canvas files \* |
| Skill | `dashboard-design` | Dashboard design workflow |
| Agent | `obsidian-vault-organizer` | Vault cleanup and organization (haiku) |

\* Integrated from [axtonliu/axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills) (MIT License)

## Installation

### Claude Code

```bash
claude plugin marketplace add kouko/monkey-skills
# All plugins (domain-teams, obsidian, philosophers-toolkit) become available
```

### Gemini CLI

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md)

## Repository Structure

```
monkey-skills/
├── domain-teams/                    ← Plugin: domain-teams
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   │   ├── worker.md
│   │   └── evaluator.md
│   └── skills/
│       ├── using-domain-teams/      ← Router (entry point)
│       ├── planning-team/           ← Orchestrator + domain knowledge
│       │   ├── SKILL.md
│       │   ├── protocols/
│       │   ├── checklists/
│       │   ├── rubrics/
│       │   └── standards/
│       ├── code-team/
│       ├── docs-team/
│       ├── qa-team/
│       ├── devops-team/
│       ├── design-team/
│       └── research-team/
├── obsidian/                        ← Plugin: obsidian
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   │   └── obsidian-vault-organizer.md
│   └── skills/
│       ├── using-obsidian/
│       ├── obsidian-daily/
│       ├── obsidian-*/
│       └── dashboard-design/
├── philosophers-toolkit/             ← Plugin: philosophers-toolkit (roadmap)
│   ├── .claude-plugin/plugin.json
│   └── ROADMAP.md
├── .claude-plugin/
│   └── marketplace.json             ← Lists all plugins
├── gemini-extension.json             ← Gemini CLI (single extension)
├── GEMINI.md                         ← Gemini CLI context
└── AGENTS.md                         ← Codex / Copilot CLI
```

## License

MIT
