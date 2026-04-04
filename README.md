# Monkey Skills

Personal agent skills marketplace — team-based development workflows and Obsidian vault management.

## Architecture: Checkpoint-Based Quality Gates + Open Domain Knowledge

```
Team Skill (checkpoint orchestrator)
  ├── worker (sonnet)    ← protocols/ + standards/
  ├── evaluator (opus)   ← checklists/ + rubrics/ + standards/
  └── context-compressor (haiku) ← context compression

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
monkey-skills
├── planning-team      Cross-domain project planning (企画) + Completeness / Consistency gates
├── code-team          Agent-driven + Security / Architecture / Quality / Spec gates
├── design-team        Agent-driven + Accessibility / UX / UI gates
├── research-team      Agent-driven + Citation / Quality gates
├── obsidian-team       Daily notes, diagrams, vault management
└── youtube-skills      Search, download, transcribe, summarize
```

### planning-team

Cross-domain project planning (企画) with quality gates.

| Type | Name | Role |
|------|------|------|
| Skill | `planning-team` | Checkpoint orchestrator for PRODUCT-SPEC.md |
| Agent | `evaluator` | Completeness checklist, cross-domain consistency gate (opus) |
| Agent | `worker` | Execute planning tasks with protocol guidance (sonnet) |

Domain knowledge: 1 protocol, 1 checklist, 1 rubric (colocated in `skills/planning-team/`)

### code-team

Code development with checkpoint-based quality gates.

| Type | Name | Role |
|------|------|------|
| Skill | `code-team` | Checkpoint orchestrator (discovery + execution) |
| Agent | `evaluator` | Security checklist, arch gate, quality gate (opus) |
| Agent | `worker` | Execute large tasks with protocol guidance (sonnet) |

Domain knowledge: 6 protocols, 3 checklists, 3 rubrics, 1 standard (colocated in `skills/code-team/`)

External dependency: `feature-dev:code-architect` (Anthropic official plugin)

### design-team

Design with checkpoint-based quality gates.

| Type | Name | Role |
|------|------|------|
| Skill | `design-team` | Checkpoint orchestrator (discovery + execution) |
| Agent | `evaluator` | A11y checklist, UX/UI/visual gates (opus) |

Domain knowledge: 4 protocols, 1 checklist, 3 rubrics, 1 standard (colocated in `skills/design-team/`)

### research-team

Research with checkpoint-based quality gates.

| Type | Name | Role |
|------|------|------|
| Skill | `research-team` | Checkpoint orchestrator (discovery + execution) |
| Agent | `worker` | Research generation (sonnet) |
| Agent | `evaluator` | Citation checklist, quality gate (opus) |

Domain knowledge: 6 protocols, 2 checklists, 1 rubric, 2 standards (colocated in `skills/research-team/`)

### obsidian-workflow

Obsidian vault daily workflows and visual tools.

| Type | Name | Role |
|------|------|------|
| Skill | `using-obsidian-workflow` | Entry point |
| Skill | `obsidian-daily` | Start the day — daily note, priorities |
| Skill | `obsidian-vault-setup` | Interactive vault configurator |
| Skill | `obsidian-tldr` | Save conversation summary to vault |
| Skill | `obsidian-file-intel` | Extract file content into Obsidian notes |
| Skill | `obsidian-mermaid-visualizer` | Create Mermaid diagrams \* |
| Skill | `obsidian-excalidraw-diagram` | Generate Excalidraw diagrams \* |
| Skill | `obsidian-canvas-creator` | Create Canvas files \* |
| Agent | `obsidian-vault-organizer` | Vault cleanup and organization (haiku) |

\* Integrated from [axtonliu/axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills) (MIT License)

### youtube-skills

YouTube video processing toolkit.

| Type | Name | Role |
|------|------|------|
| Skill | `using-youtube-skills` | Entry point |
| Skill | `mk-youtube-search` | Search videos by keyword |
| Skill | `mk-youtube-get-info` | Get video metadata |
| Skill | `mk-youtube-get-caption` | Download subtitles |
| Skill | `mk-youtube-get-audio` | Download audio |
| Skill | `mk-youtube-audio-transcribe` | Transcribe via whisper.cpp |
| Skill | `mk-youtube-summarize` | Summarize video content |
| Skill | `mk-youtube-transcript-summarize` | Summarize from transcript file |
| Skill | `mk-youtube-get-channel-latest` | Get latest from channel |

## Installation

### Claude Code

```bash
claude plugin marketplace add kouko/monkey-skills
claude plugin install monkey-skills
```

### Gemini CLI

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md)

### Cursor

Install via marketplace or import `https://github.com/kouko/monkey-skills` in Settings > Plugins.

## Repository Structure

```
monkey-skills/
├── agents/                          ← Reusable agents (4 total)
│   ├── worker.md                    ← Generic executor (sonnet)
│   ├── evaluator.md                 ← Generic evaluator (opus)
│   ├── context-compressor.md        ← Context compressor (haiku)
│   └── obsidian-vault-organizer.md  ← Standalone vault tool (haiku)
├── skills/
│   ├── planning-team/               ← Planning: orchestrator + domain knowledge
│   ├── code-team/                   ← Code: orchestrator + domain knowledge
│   │   ├── SKILL.md                 ← Checkpoint orchestrator
│   │   ├── protocols/               ← Execution SOPs
│   │   ├── checklists/              ← Binary gate criteria
│   │   ├── rubrics/                 ← Qualitative gate criteria
│   │   └── standards/               ← Shared SSOT
│   ├── design-team/                 ← Design: orchestrator + domain knowledge
│   ├── research-team/               ← Research: orchestrator + domain knowledge
│   ├── obsidian-*/                  ← Vault tools
│   └── using-obsidian-team/         ← Obsidian entry point
├── .claude-plugin/                  ← Claude Code marketplace
├── .cursor-plugin/                  ← Cursor
├── gemini-extension.json            ← Gemini CLI
├── GEMINI.md                        ← Gemini CLI context
└── AGENTS.md                        ← Codex / Copilot CLI
```

## License

MIT
