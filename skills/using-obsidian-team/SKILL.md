---
name: using-obsidian-team
description: Entry point for the obsidian-team plugin. Explains when to use it, what skills and agents are available. Load this skill for Obsidian vault operations.
---

# Using Obsidian Team

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
| `obsidian-daily` | Start the day — read/create daily note, surface priorities |
| `obsidian-vault-setup` | Interactive vault configurator |
| `obsidian-tldr` | Save conversation summary to vault |
| `obsidian-file-intel` | Extract content from files into Obsidian notes |
| `obsidian-mermaid-visualizer` | Create Mermaid diagrams in vault notes |
| `obsidian-excalidraw-diagram` | Generate Excalidraw diagrams (Obsidian/Standard/Animated) |
| `obsidian-canvas-creator` | Create Canvas files (MindMap/freeform layouts) |

## Available Agents

| Agent | Role | Model |
|-------|------|-------|
| `obsidian-vault-organizer` | Vault file organization, broken links, metadata cleanup | haiku |
| `obsidian-note-summarizer` | Compress notes and vault content for other agents | haiku |

## Quick Start

- Morning routine: invoke `obsidian-daily`
- End of session: invoke `obsidian-tldr`
- New vault: invoke `obsidian-vault-setup`
