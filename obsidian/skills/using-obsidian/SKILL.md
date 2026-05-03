---
name: using-obsidian
description: Manage Obsidian vault workflows. Use when managing daily notes, setting up vaults, saving conversation summaries, processing files, creating diagrams, or cleaning up vaults. 筆記・日記・整理。ノート・日記・整理。
---

# Using Obsidian

This plugin provides daily workflow skills and vault management for Obsidian.

## When to Use

- Starting your day (daily notes, priorities)
- Setting up a new Obsidian vault
- Saving conversation summaries to vault
- Processing files into Obsidian-ready notes
- Creating diagrams (Mermaid, Excalidraw, Canvas)
- Vault cleanup and organization
- **Building an LLM wiki layer** on top of source notes (entities/concepts/synthesis distillation, tiered retrieval, gap-filling)

## Available Skills

### Daily workflow

| Skill | Purpose |
|-------|---------|
| `obsidian-daily` | Start the day — read/create daily note, surface priorities |
| `obsidian-vault-setup` | Interactive vault configurator |
| `obsidian-tldr` | Save conversation summary to vault |
| `obsidian-file-intel` | Extract content from files into Obsidian notes |

### Authoring & visualization

| Skill | Purpose |
|-------|---------|
| `obsidian-markdown` | Create and edit Obsidian Flavored Markdown (wikilinks, embeds, callouts, properties) |
| `obsidian-bases` | Create and edit Bases (.base files) with views, filters, formulas |
| `obsidian-cli` | Interact with Obsidian vaults via CLI (read, create, search, plugin dev) |
| `obsidian-canvas-creator` | Create Canvas files (MindMap/freeform layouts) |
| `obsidian-mermaid-visualizer` | Create Mermaid diagrams in vault notes |
| `obsidian-excalidraw-diagram` | Generate Excalidraw diagrams (Obsidian/Standard/Animated) |
| `dashboard-design` | Design dashboards from requirements to prototyping |
| `defuddle` | Extract clean markdown from web pages using Defuddle CLI |

### Wiki layer (LLM knowledge distillation)

| Skill | Purpose |
|-------|---------|
| `wiki-setup` | One-time scaffold of `wiki/` structure, `.env`, manifest, hot cache |
| `wiki-ingest` | Ingest source notes (references/, research/) into wiki/ with delta tracking |
| `wiki-query` | Query wiki/ via tiered retrieval (hot → summary → full page) |
| `wiki-cross-linker` | Strengthen the knowledge graph by linking unlinked mentions |
| `wiki-lint` | 11-check health audit (structural, semantic, provenance) |
| `wiki-auto-research` | Scan Open Questions → web search → write reviewable notes to research/ |

## Available Agents

| Agent | Role | Model |
|-------|------|-------|
| `obsidian-vault-organizer` | Vault file organization, broken links, metadata cleanup | haiku |

## Quick Start

- Morning routine: invoke `obsidian-daily`
- End of session: invoke `obsidian-tldr`
- New vault: invoke `obsidian-vault-setup`
- New wiki layer: `wiki-setup` → `wiki-ingest` → `wiki-query`
