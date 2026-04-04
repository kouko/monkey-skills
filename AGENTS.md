# Monkey Skills

Personal agent skills for software development, design, research, and Obsidian team workflows.

## Architecture: Checkpoint-Based Quality Gates + Open Domain Knowledge

```
Team Skill (checkpoint orchestrator)
  ├── worker (sonnet)    ← execute with protocols/ + standards/
  ├── evaluator (opus)   ← judge with checklists/ + rubrics/ + standards/
  └── context-compressor (haiku) ← compress context between phases

Domain knowledge (open access, colocated in each team skill directory):
  protocols/   → Step-by-step SOPs (execution guidance)
  checklists/  → Binary pass/fail criteria (gate evaluation)
  rubrics/     → Qualitative flag criteria (gate evaluation)
  standards/   → Baseline rules (shared SSOT)

Role boundaries enforced by behavior, not reading restrictions:
  worker      → produces artifacts, does NOT produce gate verdicts
  evaluator   → produces verdicts, does NOT modify artifacts
```

### Four-Level Quality Gates

| Level | Behavior | Executor |
|-------|----------|----------|
| SELF | Agent self-generates check items | main agent |
| MUST | Auto-trigger, non-skippable | evaluator |
| SHOULD | Auto-trigger, skippable with reason | evaluator |
| MAY | User-requested only | evaluator |

## Skills

### Planning Team
- `planning-team` — Cross-domain project planning (企画) with Completeness + Consistency gates

### Code Team
- `code-team` — Agent-driven execution with Security + Architecture + Quality + Spec gates

### Design Team
- `design-team` — Agent-driven execution with Accessibility + UX/UI gates

### Research Team
- `research-team` — Agent-driven execution with Citation + Quality gates

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
| `worker` | Generic task executor (protocols + standards) | sonnet |
| `evaluator` | Generic quality evaluator (checklists + rubrics + standards) | opus |
| `context-compressor` | Context compressor for phase handoff | haiku |
| `obsidian-vault-organizer` | Vault maintenance (standalone) | haiku |

## Installation

See `.codex/INSTALL.md` for Codex, `gemini-extension.json` for Gemini CLI, `.cursor-plugin/plugin.json` for Cursor.
