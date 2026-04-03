# Monkey Skills

Personal agent skills marketplace — team-based development workflows and Obsidian vault management.

## Architecture: Phase-Driven + Domain Knowledge + Hybrid Evaluation

```
Team Skill (orchestrator)
  ├── worker (sonnet)    ← protocols/ + standards/
  ├── evaluator (opus)   ← checklists/ → rubrics/ + standards/
  └── context-compressor (haiku) ← context compression

Hybrid evaluation pipeline:
  1. Checklist gate (binary PASS/FAIL) — "有沒有做？"
  2. Qualitative gate (🔴🟡🟢 flags) — "做得好不好？"

Domain knowledge (domain-*/):
  protocols/   → Worker SOP (how to do)
  checklists/  → Evaluator binary gate (did you do it?)
  rubrics/     → Evaluator flag gate (did you do it well?)
  standards/   → Shared SSOT (both reference)
```

## Plugins

```
monkey-skills
├── code-team          Arch → Implement → Test → Checklist → Review → Verify
├── design-team        Generate → Checklist → Review (parallel) → Revise
├── research-team      Generate → Checklist → Quality Gate → Edit
├── obsidian-team       Daily notes, diagrams, vault management
└── youtube-skills      Search, download, transcribe, summarize
```

### code-team

Feature development workflow with hybrid evaluation gates.

| Type | Name | Role |
|------|------|------|
| Skill | `using-code-team` | Entry point — routing and documentation |
| Skill | `code-team` | Full workflow orchestration |
| Skill | `domain-code` | Domain knowledge (6 protocols, 1 checklist, 3 rubrics, 1 standard) |
| Agent | `evaluator` | Security checklist, arch gate, quality gate, QA gate (opus) |
| Agent | `worker` | Test writing, documentation, refactoring (sonnet) |

External dependency: `feature-dev:code-architect` (Anthropic official plugin)

### design-team

App design workflow with parallel evaluators and a11y checklist.

| Type | Name | Role |
|------|------|------|
| Skill | `using-design-team` | Entry point |
| Skill | `design-team` | Full workflow orchestration |
| Skill | `domain-design` | Domain knowledge (1 checklist, 3 rubrics, 1 standard) |
| Agent | `evaluator` | A11y checklist, UX/UI/visual gates in parallel (opus) |

### research-team

Deep research workflow with citation checklist and quality gate.

| Type | Name | Role |
|------|------|------|
| Skill | `using-research-team` | Entry point |
| Skill | `research-team` | Full workflow orchestration |
| Skill | `domain-research` | Domain knowledge (2 protocols, 1 checklist, 1 rubric, 1 standard) |
| Agent | `worker` | Research generation (sonnet) |
| Agent | `evaluator` | Citation checklist, quality gate (opus) |

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
├── agents/                          ← Phase-driven agents (5 total)
│   ├── orchestrator.md              ← Task decomposition (opus)
│   ├── worker.md                    ← Generic executor (sonnet)
│   ├── evaluator.md                 ← Generic evaluator (opus)
│   ├── context-compressor.md                ← Context compressor (haiku)
│   └── obsidian-vault-organizer.md  ← Standalone vault tool (haiku)
├── skills/
│   ├── domain-code/                 ← Code domain knowledge
│   │   ├── SKILL.md                 ← Role-based router
│   │   ├── protocols/               ← Worker SOPs
│   │   ├── checklists/              ← Evaluator binary gates
│   │   ├── rubrics/                 ← Evaluator flag gates
│   │   └── standards/               ← Shared SSOT
│   ├── domain-design/               ← Design domain knowledge
│   │   ├── SKILL.md
│   │   ├── checklists/
│   │   ├── rubrics/
│   │   └── standards/
│   ├── domain-research/             ← Research domain knowledge
│   │   ├── SKILL.md
│   │   ├── protocols/
│   │   ├── checklists/
│   │   ├── rubrics/
│   │   └── standards/
│   ├── code-team/                   ← Workflow orchestration
│   ├── design-team/
│   ├── research-team/
│   ├── obsidian-*/                  ← Vault tools
│   └── using-*/                     ← Entry point skills
├── .claude-plugin/                  ← Claude Code marketplace
├── .cursor-plugin/                  ← Cursor
├── gemini-extension.json            ← Gemini CLI
├── GEMINI.md                        ← Gemini CLI context
└── AGENTS.md                        ← Codex / Copilot CLI
```

## License

MIT
