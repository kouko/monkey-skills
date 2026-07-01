# monkey-skills

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Personal Claude Code plugin marketplace — 11 plugins covering domain-team workflows, skill development, philosophical thinking, Obsidian, investing, copywriting, slides, book distillation, repo knowledge, artifact deconstruction, and Salesforce SOQL query.

## Plugins

| Plugin | Version | Skills | Commands | Description |
|--------|---------|-------:|---------:|-------------|
| [`domain-teams`](domain-teams/) | 5.5.1 | 11 | 9 | Domain team skills — planning, code, design, research, copywriting with checkpoint-based quality gates. |
| [`dev-workflow`](dev-workflow/) | 2.0.0 | 7 | 4 | Skill creation, skill quality scoring, git-backed project memory, proposal triage, complexity critique, skill refactor, and skill tuning. |
| [`philosophers-toolkit`](philosophers-toolkit/) | 1.0.4 | 12 | 12 | Philosophical thinking frameworks for problem clarification and deeper reasoning. |
| [`obsidian`](obsidian/) | 3.5.0 | 13 | 1 | Obsidian vault workflows — daily notes, markdown, bases, diagrams, canvas, file intel, vault management, dashboard design. |
| [`investing-toolkit`](investing-toolkit/) | 1.16.5 | 15 | 5 | Investing research toolkit — macro regime diagnosis (US/JP/TW/KR/CN), DCF, screener, equity snapshots via primary-source adapters. |
| [`copywriting-toolkit`](copywriting-toolkit/) | 1.14.0 | 14 | 1 | Pipeline-structured copywriting — intake, ideation, neta injection, 5 form-specific drafters, voice positioning, ethics + form gates, audit. |
| [`tsundoku`](tsundoku/) | 0.11.0 | 4 | 5 | Tsundoku 積読 — turn an owned-but-unread Kobo e-book pile into actionable agent skills via the RIA-TV++ distillation pipeline. |
| [`repo-wiki`](repo-wiki/) | 1.0.0 | 3 | 3 | LLM Wiki Pattern for code repos — seed `.repo-wiki/` from git history (init), grow from changes / context / external docs (ingest, polymorphic), query with verification against `src/` (Eager triggers + segmented output). |
| [`deconstruct-toolkit`](deconstruct-toolkit/) | 0.2.1 | 4 | 1 | Reverse-engineer polished artifacts (copy / docs / UI / arguments / products / organizations) — surface design blueprints, hidden frameworks, rhetorical mechanisms, intentional omissions. Grounded in Derrida / Barthes / Toulmin / Lakoff / Goffman / Cialdini / Bhatia / Nielsen-Norman, with EN/JA/ZH cultural-variant lenses (Hinds kishōtenketsu / 劉勰《文心雕龍》六觀 / Hu/Hwang face-and-favor). BCG「バリュー・チェーンの脱構築」系譜. |
| [`salesforce-toolkit`](salesforce-toolkit/) | 0.1.0 | 1 | 1 | Salesforce DX MCP server wrapped as Claude Code plugin — brew-first installer, read-only SOQL query (data toolset only). macOS only. ⚠️ Not supported in the Cowork sandbox (TTY-bound OAuth); installs on Codex CLI too (MCP auto-registers). |

**Totals:** 84 skills and 42 slash commands across 10 plugins listed (the marketplace ships 18 — table not yet fully synced; see [`marketplace.json`](.claude-plugin/marketplace.json) for the authoritative list).

> Plugins marked ⚠️ in their own description (`investing-toolkit`, `tsundoku`, `salesforce-toolkit`, plus the `defuddle` skill in `obsidian`) are not supported in the Cowork sandbox — it blocks their external network access or subprocess use. (`salesforce-toolkit` does install on Codex CLI; its ⚠️ is Cowork-specific, not "Claude Code only".)

## Install

### Claude Code (marketplace)

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install <plugin-name>@monkey-skills
```

Replace `<plugin-name>` with any name from the table above.

### Gemini CLI (extension)

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

The extension manifest lives at [`gemini-extension.json`](gemini-extension.json).

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md) for symlink and plugin installation modes.

## Repository layout

```
monkey-skills/
├── .claude-plugin/
│   └── marketplace.json          # plugin registry
├── .codex/
│   └── INSTALL.md                # Codex install instructions
├── .github/workflows/
│   ├── skill-structure.yml       # CI: enforce skill conventions
│   └── scraper-deps-monthly.yml  # CI: monthly dep refresh
├── domain-teams/                 # plugin
├── dev-workflow/                 # plugin
├── philosophers-toolkit/         # plugin
├── obsidian/                     # plugin
├── investing-toolkit/            # plugin
├── copywriting-toolkit/          # plugin
├── tsundoku/                     # plugin
├── repo-wiki/                    # plugin
├── deconstruct-toolkit/          # plugin
├── docs/                         # cross-cutting docs (i18n glossary, etc.)
├── scripts/                      # repo-level tooling
├── CLAUDE.md                     # project conventions for Claude Code
├── GEMINI.md                     # project conventions for Gemini CLI
├── AGENTS.md                     # generic agent conventions
├── ATTRIBUTION.md                # third-party imports & licenses
├── LICENSE                       # MIT
└── gemini-extension.json         # Gemini CLI extension manifest
```

## Contributing

This is a personal marketplace. Issues and PRs are welcome via the
[GitHub repository](https://github.com/kouko/monkey-skills). For
skill-development conventions (file paths, two-layer spec, quality
gates, agent roles, cross-plugin delegation), see [`CLAUDE.md`](CLAUDE.md).

## License

MIT — see [`LICENSE`](LICENSE).

Third-party components (Obsidian skills from kepano and axtonliu,
`skill-creator-advance` from AllanYiin, `skill-judge` from softaworks,
and others) are MIT-licensed and credited in [`ATTRIBUTION.md`](ATTRIBUTION.md).
