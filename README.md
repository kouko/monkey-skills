# Monkey Skills

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Personal agent skills marketplace — **6 plugins** covering domain-team quality
gates, Obsidian vault workflows, philosophical thinking frameworks,
skill-authoring tools, investing research, and pipeline-structured copywriting.

## Plugins

| Plugin | Version | Skills | Commands | Description |
|--------|--------:|-------:|---------:|-------------|
| [`domain-teams`](domain-teams/README.md) | 5.2.0 | 10 | 9 | 9-team skill suite with checkpoint-based quality gates (planning / code / docs / qa / devops / design / research / investing / copywriting) + skill-team meta-skill + router |
| [`obsidian`](obsidian/README.md) | 3.5.0 | 13 (+1 agent) | 1 | Obsidian vault workflows — daily notes, diagrams, dashboards + imported kepano & axtonliu visual skills |
| [`philosophers-toolkit`](philosophers-toolkit/README.md) | 1.0.4 | 12 | 12 | Philosophical thinking frameworks for problem clarification and deeper reasoning |
| [`dev-workflow`](dev-workflow/README.md) | 1.0.4 | 1 | 1 | Skill creation and eval workflows (adapted from Anthropic → AllanYiin chain) |
| [`investing-toolkit`](investing-toolkit/README.md) | 1.16.5 | 15 | 5 | Investing research — US/JP/TW/KR/CN macro regime diagnosis, DCF, screening, equity snapshots |
| [`copywriting-toolkit`](copywriting-toolkit/README.md) | 1.14.0 | 14 | 1 | Pipeline-structured copywriting — 9-phase pipeline, 90-anchor voice library, ethics + form gates. A/B coexistence with `domain-teams:copywriting-team` |

**Total**: 65 skills, 29 slash commands across 6 plugins.

Each plugin has its own `README.md` with full skill inventory, architecture,
and usage detail. This root README only indexes the plugins.

## Installation

### Claude Code

```bash
claude plugin marketplace add kouko/monkey-skills
# All 6 plugins become available:
#   domain-teams, obsidian, philosophers-toolkit, dev-workflow,
#   investing-toolkit, copywriting-toolkit
```

Install specific plugins only:

```bash
claude plugin install domain-teams@kouko/monkey-skills
claude plugin install obsidian@kouko/monkey-skills
# ...etc.
```

### Gemini CLI

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md).

## Repository Layout

```
monkey-skills/
├── .claude-plugin/marketplace.json   ← Lists all 6 plugins
├── domain-teams/                     ← Plugin (see domain-teams/README.md)
├── obsidian/                         ← Plugin (see obsidian/README.md)
├── philosophers-toolkit/             ← Plugin (see philosophers-toolkit/README.md)
├── dev-workflow/                     ← Plugin (see dev-workflow/README.md)
├── investing-toolkit/                ← Plugin (see investing-toolkit/README.md)
├── copywriting-toolkit/              ← Plugin (see copywriting-toolkit/README.md)
│
├── LICENSE                           ← Project MIT (kouko) + third-party pointer
├── ATTRIBUTION.md                    ← Summary of all 3rd-party imports
├── CLAUDE.md                         ← Claude Code context (skill conventions)
├── GEMINI.md                         ← Gemini CLI context
├── AGENTS.md                         ← Codex / Copilot CLI context
├── gemini-extension.json             ← Gemini CLI extension manifest
└── .github/workflows/
    └── skill-structure.yml           ← CI: SKILL.md structure + Conventional Commits
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for the
project-level notice and pointers to per-component license files.

Third-party components retain their original copyright notices (Steph Ango,
Axton Liu, AllanYiin / 尹相志, Anthropic). Full attribution with upstream
URLs, licenses, and modification summaries: see
[ATTRIBUTION.md](ATTRIBUTION.md).

To report a license or attribution concern, open an issue at
https://github.com/kouko/monkey-skills/issues.
