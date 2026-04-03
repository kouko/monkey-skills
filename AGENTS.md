# Monkey Skills

Personal agent skills for software development, design, research, and Obsidian team workflows.

## Architecture: Phase-Driven Agents + Domain Knowledge + Hybrid Evaluation

```
Team Skill (orchestrator)
  ├── worker (sonnet)    ← execute with protocols/ + standards/
  ├── evaluator (opus)   ← judge with checklists/ → rubrics/ + standards/
  └── summarizer (haiku) ← compress context between phases

Domain knowledge in domain-*/:
  protocols/   → Worker reads (how to do)
  checklists/  → Evaluator reads first (binary pass/fail)
  rubrics/     → Evaluator reads second (qualitative flags)
  standards/   → Both read (shared SSOT)
```

## Skills

### Code Team
- `using-code-team` — Entry point and routing guide
- `code-team` — Arch → Implement → Test → Checklist → Review → Verify
- `domain-code` — Domain knowledge: protocols, checklists, rubrics, standards

### Design Team
- `using-design-team` — Entry point and routing guide
- `design-team` — Generate → Checklist → Review (parallel) → Revise
- `domain-design` — Domain knowledge: checklists, rubrics, standards

### Research Team
- `using-research-team` — Entry point and routing guide
- `research-team` — Generate → Checklist → Quality Gate → Edit
- `domain-research` — Domain knowledge: protocols, checklists, rubrics, standards

### Obsidian Team
- `using-obsidian-team` — Entry point and routing guide
- `obsidian-daily` — Start the day with vault context
- `obsidian-vault-setup` — Interactive vault configurator
- `obsidian-tldr` — Save conversation summary to vault
- `obsidian-file-intel` — Extract content from files into Obsidian notes
- `obsidian-mermaid-visualizer` — Create Mermaid diagrams
- `obsidian-excalidraw-diagram` — Generate Excalidraw diagrams
- `obsidian-canvas-creator` — Create Canvas files

## Agents

| Agent | Role | Model |
|-------|------|-------|
| `orchestrator` | Task decomposition and routing | opus |
| `worker` | Generic task executor (protocols + standards) | sonnet |
| `evaluator` | Generic quality evaluator (checklists + rubrics + standards) | opus |
| `summarizer` | Context compressor for phase handoff | haiku |
| `obsidian-vault-organizer` | Vault maintenance (standalone) | haiku |

## Installation

See `.codex/INSTALL.md` for Codex, `gemini-extension.json` for Gemini CLI, `.cursor-plugin/plugin.json` for Cursor.
