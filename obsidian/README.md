# obsidian

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Obsidian vault workflows — daily notes, markdown, Bases, diagrams, Canvas, file intel, vault management, and dashboard design, packaged as a Claude Code plugin.

## ⚠️ Cowork compatibility

Most skills in this plugin are Cowork-compatible. The `defuddle` skill is the
exception — it shells out to the [Defuddle CLI](https://github.com/kepano/defuddle)
to fetch and clean external URLs, which Cowork's sandbox URL allowlist blocks.
Use Claude Code CLI for `defuddle`. The same pattern is documented in
[`investing-toolkit/docs/mcp-setup.md`](../investing-toolkit/docs/mcp-setup.md):
plugin-installed subprocesses run inside the same sandbox as plugin MCPs, so
both paths get blocked equally on Cowork.

| Skill | Cowork | Claude Code CLI |
|---|---|---|
| `defuddle` | Blocked (URL fetch) | Works |
| All other obsidian skills | Works | Works |

## Version

3.8.1 — see [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

## Part of

This plugin is part of [`monkey-skills`](https://github.com/kouko/monkey-skills),
a marketplace of Claude Code plugins for daily knowledge work, investing,
copywriting, and skill development.

## Background

Obsidian is a local-first markdown knowledge base. Day-to-day vault work
involves many small, repetitive tasks: opening today's daily note, sweeping the
inbox, writing valid Bases YAML, drawing a Mermaid diagram inside a note,
importing a folder of PDFs as summarized notes, and saving a conversation
summary at the end of the session.

This plugin packages those tasks as skills that Claude Code can dispatch on
intent. Original skills cover the daily workflow, file intel, dashboard
design, vault setup, and conversation summary. Imported skills cover
Obsidian-specific markdown, Bases, the Obsidian CLI, Defuddle web extraction,
Canvas authoring, Excalidraw diagrams, and Mermaid diagrams.

## Router and agent

### Router

`using-obsidian` is the entry skill. It routes intent to the right skill based
on what the user asks for — daily notes, vault setup, file processing,
diagrams, or cleanup.

The slash command `/obsidian` invokes `using-obsidian`.

### Agent

`obsidian-vault-organizer` is a vault-maintenance agent for periodic hygiene:
sorting `inbox/`, fixing broken wikilinks, normalizing frontmatter, flagging
duplicates, and standardizing tags. It never deletes files — only moves or
edits — and asks before reorganizing when the destination is ambiguous.

## Skills

### Original skills (this project)

| Skill | Purpose |
|---|---|
| `using-obsidian` | Router — routes vault-workflow intent to the right skill. |
| `obsidian-daily` | Read or create today's daily note, sweep `inbox/`, surface the top 3 priorities. |
| `obsidian-vault-setup` | Interactive first-time vault configurator — infers role and scope from free-text answers. |
| `obsidian-tldr` | Save a conversation summary to the vault and update `memory.md`. |
| `obsidian-file-intel` | Extract content from PDF / PPTX / XLSX / DOCX / CSV / JSON via Gemini and produce Obsidian-ready summaries. |
| `dashboard-design` | Guide dashboard design from requirements to layout, grounded in Japan Digital Agency dashboard guidelines. |

### Wiki layer (LLM knowledge distillation, original)

Inspired by [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and [`Ar9av/obsidian-wiki`](https://github.com/Ar9av/obsidian-wiki), reimagined with a 6-category type axis (entities / concepts / synthesis / skills / journal / references), tiered retrieval, content-hash delta tracking, and bounded auto-research. Each skill is fully self-contained — no cross-skill or plugin-level shared references.

| Skill | Purpose |
|---|---|
| `wiki-setup` | One-time scaffold of `wiki/` structure, `.env`, manifest, hot cache. |
| `wiki-ingest` | Ingest source notes (references/, research/, etc.) into wiki/ with SHA-256 delta tracking. Owns the page format spec. |
| `wiki-query` | Query wiki/ via tiered retrieval (hot.md → frontmatter summary → full page). |
| `wiki-cross-linker` | Strengthen the knowledge graph by converting plain-text mentions into `[[wikilinks]]`. |
| `wiki-lint` | 11-check health audit — structural, semantic, provenance. Read-only. |
| `wiki-auto-research` | Manual one-shot — scan Open Questions and ambiguous claims, web-search, write reviewable notes to `research/`. |

### Imported from kepano (Steph Ango)

Upstream: [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)
— MIT, Copyright (c) 2026 Steph Ango.

| Skill | Purpose |
|---|---|
| `obsidian-markdown` | Author Obsidian Flavored Markdown — wikilinks, embeds, callouts, properties, comments. |
| `obsidian-bases` | Create and edit `.base` files with views, filters, formulas, and summaries. |
| `obsidian-cli` | Drive a running Obsidian instance via the official CLI — read, create, search, plugin and theme dev. |
| `defuddle` | Extract clean markdown from web pages via Defuddle CLI (token-saving alternative to WebFetch). |

### Imported from axtonliu (Axton Liu)

Upstream: [`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)
— MIT, Copyright (c) 2025 Axton Liu.

| Skill | Purpose |
|---|---|
| `obsidian-canvas-creator` | Create Obsidian Canvas files with MindMap or freeform layouts. (Combined with json-canvas integration from kepano.) |
| `obsidian-excalidraw-diagram` | Generate Excalidraw diagrams in Obsidian / Standard / Animated formats. |
| `obsidian-mermaid-visualizer` | 17 Mermaid diagram types — flow, data-viz, structural, time — optimized for Obsidian 11.4.1, portable to GitHub / Notion / HackMD. |

## Install

```bash
# Inside Claude Code (CLI)
/plugin marketplace add kouko/monkey-skills
/plugin install obsidian
```

The `defuddle` skill needs the Defuddle CLI:

```bash
npm install -g defuddle
```

The `obsidian-cli` skill needs the official Obsidian CLI and a running
Obsidian instance — see [help.obsidian.md/cli](https://help.obsidian.md/cli).

The `obsidian-file-intel` skill needs the bundled
`scripts/process_files_with_gemini.py` and a Gemini API key configured in your
vault.

## Usage

Start the day:

```
/obsidian
> Start my day
```

`using-obsidian` routes to `obsidian-daily`, which reads or creates
`daily/YYYY-MM-DD.md`, lists `inbox/` items, and surfaces the top 3
priorities.

Save a conversation summary at the end of the session:

```
> Save a TLDR of this conversation
```

`using-obsidian` routes to `obsidian-tldr`, which writes a markdown summary
into the relevant folder and updates `memory.md`.

Draw a diagram inside a note:

```
> Make a Mermaid sequence diagram of the OAuth device flow
```

`using-obsidian` routes to `obsidian-mermaid-visualizer`, which picks the
sequence diagram type, applies Obsidian 11.4.1 quirks, and emits a
` ```mermaid ` block.

## Repository structure

```
obsidian/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata, version 3.8.1
├── agents/
│   └── obsidian-vault-organizer.md  # vault hygiene agent
├── commands/
│   └── obsidian.md              # /obsidian → using-obsidian
├── skills/
│   ├── README.md                # per-skill attribution table
│   ├── using-obsidian/          # router (original)
│   ├── obsidian-daily/          # daily workflow (original)
│   ├── obsidian-vault-setup/    # vault configurator (original)
│   ├── obsidian-tldr/           # conversation summary (original)
│   ├── obsidian-file-intel/     # file → Obsidian summaries (original)
│   ├── dashboard-design/        # dashboard design (original)
│   ├── obsidian-markdown/       # imported from kepano
│   ├── obsidian-bases/          # imported from kepano
│   ├── obsidian-cli/            # imported from kepano
│   ├── defuddle/                # imported from kepano
│   ├── obsidian-canvas-creator/ # imported from axtonliu
│   ├── obsidian-excalidraw-diagram/ # imported from axtonliu
│   ├── obsidian-mermaid-visualizer/ # imported from axtonliu
│   ├── wiki-setup/                # wiki layer init (original)
│   ├── wiki-ingest/               # source → wiki distillation (original)
│   ├── wiki-query/                # tiered retrieval (original)
│   ├── wiki-cross-linker/         # knowledge graph strengthening (original)
│   ├── wiki-lint/                 # health audit (original)
│   └── wiki-auto-research/        # gap-filling via web search (original)
├── README.md
├── README.ja.md
└── README.zh-TW.md
```

Per-skill attribution lives in [`skills/README.md`](skills/README.md).
Repo-wide attribution lives in [`../ATTRIBUTION.md`](../ATTRIBUTION.md).

## Contributing

- Bug reports and feature requests: open an issue at
  [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues).
- Pull requests welcome. Match the existing skill structure (frontmatter +
  workflow + reference files) and use Conventional Commits.
- For imported skills, upstream changes flow from kepano and axtonliu; please
  also consider opening upstream PRs when fixes apply there.

## License

MIT — see [LICENSE](../LICENSE) at the repository root.

Imported skills retain their original copyright notices in each skill's
`LICENSE` file:

- `defuddle`, `obsidian-bases`, `obsidian-cli`, `obsidian-markdown` — MIT,
  Copyright (c) 2026 Steph Ango. See the per-skill `LICENSE`.
- `obsidian-canvas-creator`, `obsidian-excalidraw-diagram`,
  `obsidian-mermaid-visualizer` — MIT, Copyright (c) 2025 Axton Liu. See the
  per-skill `LICENSE`. (`obsidian-canvas-creator` also bundles json-canvas
  integration from kepano.)

See [LICENSE](../LICENSE) for the overall project license, and
[ATTRIBUTION.md](../ATTRIBUTION.md) for the full third-party component map.
