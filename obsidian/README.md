# obsidian

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 3.5.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Obsidian vault workflows — daily notes, visual tools, file intelligence,
dashboard design. Combines original skills with MIT-licensed imports from
the Obsidian community (kepano / axtonliu).

## Router + Agent

| Type | Name | Role |
|------|------|------|
| Skill | `using-obsidian` | Entry point — routes vault tasks to the right skill |
| Agent | `obsidian-vault-organizer` | Vault cleanup and organization (haiku) |

## Original skills (this project)

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `obsidian-daily` | `/obsidian` | Start the day — daily note, priorities |
| `obsidian-vault-setup` | — | Interactive vault configurator |
| `obsidian-tldr` | — | Save conversation summary to vault |
| `obsidian-file-intel` | — | Extract file content (PDF/PPTX/XLSX/DOCX/etc.) into Obsidian notes |
| `dashboard-design` | — | Dashboard design workflow |

## Imported from Steph Ango (kepano) — MIT

Upstream: [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)

| Skill | Role |
|-------|------|
| `defuddle` | Extract clean markdown from web pages (removes clutter) |
| `obsidian-bases` | Create and edit Obsidian Bases (.base files) |
| `obsidian-cli` | Interact with vaults via Obsidian CLI |
| `obsidian-markdown` | Obsidian-flavored Markdown (wikilinks, embeds, callouts, properties) |

## Imported from Axton Liu (axtonliu) — MIT

Upstream: [`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)

| Skill | Role |
|-------|------|
| `obsidian-canvas-creator` | Create Canvas files (MindMap / freeform layouts) — combines axtonliu base with kepano's json-canvas |
| `obsidian-excalidraw-diagram` | Generate Excalidraw diagrams (mind maps, animated flowcharts) |
| `obsidian-mermaid-visualizer` | Create Mermaid diagrams — 17 types covering flowcharts, sequence / state / class / ER / C4 / git-branch, charts, schedules, architecture / block diagrams |

13 skills total + 1 agent + 1 slash command.

## Repository Structure

```
obsidian/
├── .claude-plugin/plugin.json
├── agents/
│   └── obsidian-vault-organizer.md  ← haiku
├── commands/
│   └── obsidian.md                  ← /obsidian
└── skills/
    ├── README.md                    ← Skill attribution table
    ├── using-obsidian/              ← Router
    ├── obsidian-daily/
    ├── obsidian-vault-setup/
    ├── obsidian-tldr/
    ├── obsidian-file-intel/
    ├── dashboard-design/
    ├── defuddle/                    ← 3rd-party (kepano, MIT)
    ├── obsidian-bases/              ← 3rd-party (kepano, MIT)
    ├── obsidian-cli/                ← 3rd-party (kepano, MIT)
    ├── obsidian-markdown/           ← 3rd-party (kepano, MIT)
    ├── obsidian-canvas-creator/     ← 3rd-party (axtonliu + kepano, MIT)
    ├── obsidian-excalidraw-diagram/ ← 3rd-party (axtonliu, MIT)
    └── obsidian-mermaid-visualizer/ ← 3rd-party (axtonliu, MIT)
```

Per-skill attribution table: [`skills/README.md`](skills/README.md).
Repo-wide attribution with upstream URLs + modification summaries:
[`../ATTRIBUTION.md`](../ATTRIBUTION.md).

## License

MIT — see repository root [`LICENSE`](../LICENSE). Third-party components
retain their original copyright notices (Steph Ango, Axton Liu).
