---
name: using-obsidian-workflow
description: Entry point for the obsidian-workflow plugin. Explains when to use it, what skills and agents are available. Load this skill for Obsidian vault operations.
---

# Using Obsidian Workflow

This plugin provides daily workflow skills and vault management for Obsidian.

## When to Use

- Starting your day (daily notes, priorities)
- Setting up a new Obsidian vault
- Saving conversation summaries to vault
- Processing files into Obsidian-ready notes
- Creating diagrams (Mermaid, Excalidraw, Canvas)
- Vault cleanup and organization

## Available Skills

| Skill | Purpose |
|-------|---------|
| `obsidian-workflow:daily` | Start the day — read/create daily note, surface priorities |
| `obsidian-workflow:vault-setup` | Interactive vault configurator |
| `obsidian-workflow:tldr` | Save conversation summary to vault |
| `obsidian-workflow:file-intel` | Extract content from files into Obsidian notes |
| `obsidian-workflow:mermaid-visualizer` | Create Mermaid diagrams in vault notes |
| `obsidian-workflow:excalidraw-diagram` | Generate Excalidraw diagrams (Obsidian/Standard/Animated) |
| `obsidian-workflow:obsidian-canvas-creator` | Create Canvas files (MindMap/freeform layouts) |

## Available Agents

| Agent | Role | Model |
|-------|------|-------|
| `vault-organizer` | Vault file organization, broken links, metadata cleanup | haiku |
| `note-summarizer` | Compress notes and vault content for other agents | haiku |

## Quick Start

- Morning routine: invoke `obsidian-workflow:daily`
- End of session: invoke `obsidian-workflow:tldr`
- New vault: invoke `obsidian-workflow:vault-setup`
