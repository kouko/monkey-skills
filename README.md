# Monkey Skills

Personal agent skills marketplace — team-based development workflows, Obsidian vault management, and YouTube processing.

## Plugins

```
monkey-skills
├── code-team          Arch → Implement → Test → Review → Verify
├── design-team        Generate → Review (parallel) → Revise
├── research-team      Generate → Evaluate → Edit
├── obsidian-workflow   Daily notes, diagrams, vault management
└── youtube-skills      Search, download, transcribe, summarize
```

### code-team

Feature development workflow with quality gates.

| Type | Name | Role |
|------|------|------|
| Skill | `using-code-team` | Entry point — routing and documentation |
| Skill | `code-team` | Full workflow orchestration |
| Agent | `arch-reviewer` | Architecture & design review (opus) |
| Agent | `code-reviewer` | Code quality, bugs, security (sonnet) |
| Agent | `qa-evaluator` | Final quality verification (opus) |
| Agent | `test-writer` | Unit test generation (sonnet) |
| Agent | `doc-writer` | Documentation generation (haiku) |
| Agent | `refactor-agent` | Mechanical refactoring (sonnet) |
| Agent | `code-summarizer` | Code-related text compression (haiku) |

External dependency: `feature-dev:code-architect` (Anthropic official plugin)

### design-team

App design workflow with parallel reviewers.

| Type | Name | Role |
|------|------|------|
| Skill | `using-design-team` | Entry point |
| Skill | `design-team` | Full workflow orchestration |
| Agent | `ux-strategist` | UX strategy, user journeys (opus) |
| Agent | `ui-reviewer` | UI structure, IA, interaction patterns (sonnet) |
| Agent | `visual-reviewer` | Visual design, typography, color (opus) |
| Agent | `a11y-reviewer` | Accessibility, WCAG compliance (sonnet) |
| Agent | `design-summarizer` | Design-related text compression (haiku) |

### research-team

Deep research workflow with evaluation loop.

| Type | Name | Role |
|------|------|------|
| Skill | `using-research-team` | Entry point |
| Skill | `research-team` | Full workflow orchestration |
| Agent | `research-analyst` | Multi-source investigation (opus) |
| Agent | `investment-analyst` | Investment & macro analysis (opus) |
| Agent | `qa-evaluator` | Draft quality evaluation (opus) — shared with code-team |
| Agent | `research-summarizer` | Research data compression (haiku) |

### obsidian-workflow

Obsidian vault daily workflows and visual tools.

| Type | Name | Role |
|------|------|------|
| Skill | `using-obsidian-workflow` | Entry point |
| Skill | `daily` | Start the day — daily note, priorities |
| Skill | `vault-setup` | Interactive vault configurator |
| Skill | `tldr` | Save conversation summary to vault |
| Skill | `file-intel` | Extract file content into Obsidian notes |
| Skill | `mermaid-visualizer` | Create Mermaid diagrams \* |
| Skill | `excalidraw-diagram` | Generate Excalidraw diagrams \* |
| Skill | `obsidian-canvas-creator` | Create Canvas files \* |
| Agent | `vault-organizer` | Vault cleanup and organization (haiku) |
| Agent | `note-summarizer` | Note content compression (haiku) |

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
claude plugin install code-team@monkey-skills
claude plugin install design-team@monkey-skills
claude plugin install research-team@monkey-skills
claude plugin install obsidian-workflow@monkey-skills
claude plugin install youtube-skills@monkey-skills
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
├── .claude-plugin/
│   └── marketplace.json           ← Claude Code marketplace (source: "./plugins/<name>")
├── .cursor-plugin/
│   └── plugin.json                ← Cursor
├── .codex/
│   └── INSTALL.md                 ← Codex install guide
├── gemini-extension.json          ← Gemini CLI
├── GEMINI.md                      ← Gemini CLI context
├── AGENTS.md                      ← Codex / Copilot CLI
└── plugins/                       ← Each plugin is isolated
    ├── code-team/
    │   ├── .claude-plugin/plugin.json
    │   ├── skills/                 ← Only code-team skills
    │   └── agents/                 ← Only code-team agents
    ├── design-team/
    ├── research-team/
    ├── obsidian-workflow/
    └── youtube-skills/
```

Uses **Pattern B** (isolated plugin directories). Each plugin has its own `skills/` and `agents/`, preventing namespace pollution. Shared agents (e.g., `qa-evaluator` used by both code-team and research-team) are copied to each plugin that needs them.

## License

MIT
