# Monkey Skills

Personal agent skills organized into two plugins: domain teams and Obsidian workflows.

## Architecture: Checkpoint-Based Quality Gates + Open Domain Knowledge

```
Team Skill (checkpoint orchestrator)
  ├── worker (sonnet)    ← execute with protocols/ + standards/
  └── evaluator (opus)   ← judge with checklists/ + rubrics/ + standards/

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

## Commands

<!-- BEGIN command-surface (managed) -->
- **Living-spec structural gate** (every push):
  `python3 loom-code/scripts/check-living-spec-index.py [<repo-root>]` —
  fails rc=1 on any dangling `@req` / malformed tag; runs the advisory
  drift WARN lane alongside.
- **Regenerate the living-spec index**:
  `python3 loom-code/scripts/check-living-spec-index.py --write-index docs/loom/INDEX.md`
  — regenerates `docs/loom/INDEX.md` from the source tree (the
  finishing-step / once-per-branch regen path).
- **Verify the committed index is current** (merge-boundary gate):
  `python3 loom-code/scripts/check-living-spec-index.py --verify-index docs/loom/INDEX.md`
  — byte-identity check vs a fresh regeneration; rc=1 if stale.
<!-- END command-surface (managed) -->

## Plugin: domain-teams

### Entry Point
- `using-domain-teams` — Route to the right domain team

### Teams
- `planning-team` — Cross-domain project planning (企画) with Completeness + Consistency gates
- `code-team` — Code development with Security + Architecture + Quality + Spec gates
- `docs-team` — Documentation and codebase assessment (MAY gates only)
- `qa-team` — Test strategy and planning with Test Plan Completeness + Strategy Quality gates
- `devops-team` — Deployment and infrastructure with Deployment Safety + IaC Quality gates
- `design-team` — Design with Accessibility + UX/UI gates
- `research-team` — Research with Citation + Quality gates

### Agents (shared across domain teams)

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Generic task executor (protocols + standards) | sonnet |
| `evaluator` | Generic quality evaluator (checklists + rubrics + standards) | opus |

## Plugin: obsidian

### Skills
- `using-obsidian` — Entry point and routing guide
- `obsidian-daily` — Start the day with vault context
- `obsidian-vault-setup` — Interactive vault configurator
- `obsidian-tldr` — Save conversation summary to vault
- `obsidian-file-intel` — Extract content from files into Obsidian notes
- `obsidian-mermaid-visualizer` — Create Mermaid diagrams
- `obsidian-excalidraw-diagram` — Generate Excalidraw diagrams
- `obsidian-canvas-creator` — Create Canvas files
- `dashboard-design` — Dashboard design workflow

### Agents

| Agent | Role | Model |
|-------|------|-------|
| `obsidian-vault-organizer` | Vault maintenance (standalone) | haiku |

## Plugin: philosophers-toolkit (v0.1.0 — roadmap only)

Philosophical thinking frameworks for problem clarification and deeper reasoning.
See `philosophers-toolkit/ROADMAP.md` for planned skills.

## Installation

See `.codex/INSTALL.md` for Codex, `gemini-extension.json` for Gemini CLI.
