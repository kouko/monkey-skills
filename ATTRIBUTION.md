# Attribution

This document summarizes third-party components bundled or adapted in
`monkey-skills`. All components are MIT-licensed; their copyright notices
and license texts are preserved in the per-component `LICENSE` files
listed below.

See [`LICENSE`](LICENSE) for the overall project license (MIT,
Copyright (c) 2026 kouko).

## Third-Party Imports

### Obsidian skills from Steph Ango (kepano)

Upstream: [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)
License: MIT, Copyright (c) 2026 Steph Ango

| Component | License file |
|-----------|-------------|
| `obsidian/skills/defuddle/` | [LICENSE](obsidian/skills/defuddle/LICENSE) |
| `obsidian/skills/obsidian-markdown/` | [LICENSE](obsidian/skills/obsidian-markdown/LICENSE) |
| `obsidian/skills/obsidian-bases/` | [LICENSE](obsidian/skills/obsidian-bases/LICENSE) |
| `obsidian/skills/obsidian-cli/` | [LICENSE](obsidian/skills/obsidian-cli/LICENSE) |

### Obsidian visual skills from Axton Liu (axtonliu)

Upstream: [`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)
License: MIT, Copyright (c) 2025 Axton Liu

| Component | License file | Notes |
|-----------|-------------|-------|
| `obsidian/skills/obsidian-canvas-creator/` | [LICENSE](obsidian/skills/obsidian-canvas-creator/LICENSE) | Combines Axton Liu's canvas creator with kepano's json-canvas integration |
| `obsidian/skills/obsidian-excalidraw-diagram/` | [LICENSE](obsidian/skills/obsidian-excalidraw-diagram/LICENSE) | |
| `obsidian/skills/obsidian-mermaid-visualizer/` | [LICENSE](obsidian/skills/obsidian-mermaid-visualizer/LICENSE) | |

### skill-creator-advance (dev-workflow plugin)

Upstream chain:

1. [`anthropics/skills`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — earliest upstream, MIT, contributes eval-loop concept + bundled agent/script file naming
2. [`AllanYiin/Amon`](https://github.com/AllanYiin/Amon) (`src/amon/resources/skills/skill-creator-advanced/`) — direct upstream, MIT, Copyright (c) 2026 AllanYiin (尹相志); enhanced version with additional protocols and references. Announcement: [Facebook post (Chinese)](https://www.facebook.com/allanyiin/posts/26778210211773012/)
3. `dev-workflow/skills/skill-creator-advance/` — this distribution, MIT, Copyright (c) 2026 kouko

| Component | License file | NOTICE |
|-----------|-------------|--------|
| `dev-workflow/skills/skill-creator-advance/` | [LICENSE](dev-workflow/skills/skill-creator-advance/LICENSE) | [NOTICE](dev-workflow/skills/skill-creator-advance/NOTICE) |

### skill-judge (dev-workflow plugin)

Upstream: [`softaworks/agent-toolkit`](https://github.com/softaworks/agent-toolkit/tree/main/skills/skill-judge) — direct upstream, MIT, Copyright (c) 2026 Leonardo Flores; provides the 8-dimension rubric, E:A:R knowledge classification, evaluation protocol, and 9 common failure patterns.

Modifications by kouko: frontmatter rewritten to dev-workflow plugin convention; new "Adaptation for monkey-skills domain-team skills" section added (D7 rescaling, D4/D5 supplementary checks against `domain-teams:skill-team` gates, focus dimensions D1/D3/D6); cross-references inserted to `skill-dev-toolkit:skill-creator-advance` and `domain-teams:skill-team` for scope disambiguation.

| Component | License file | NOTICE |
|-----------|-------------|--------|
| `dev-workflow/skills/skill-judge/` | [LICENSE](dev-workflow/skills/skill-judge/LICENSE) | [NOTICE](dev-workflow/skills/skill-judge/NOTICE) |

### repo-wiki plugin (conceptual derivation, no code imported)

`repo-wiki/` adapts the conceptual pattern from these prior works. No source files are bundled; the implementation is original to this project. Credited here for transparency on intellectual lineage:

- [Andrej Karpathy — LLM Wiki Pattern (2024)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — conceptual root: synthesize at ingest time, not query time; AI-owned wiki layer separate from immutable raw layer
- [`SamurAIGPT/llm-wiki-agent`](https://github.com/SamurAIGPT/llm-wiki-agent) — `raw/ → wiki/` directory pattern, ingest/query SKILL.md split, page-type taxonomy reference
- [`llmrix/llm-wiki-skill`](https://github.com/llmrix/llm-wiki-skill) — SKILL.md frontmatter and step-numbered workflow style reference

`repo-wiki`'s additions over these prior works: git-aware seed (init), polymorphic ingest (git/context/doc-import), verification triggers T1-T7 with segmented output, entity name normalization rule, hidden `.repo-wiki/` directory convention, CLAUDE.md drop-in for AI-owned enforcement.

## Original Work (this project)

The following components are original to this project, authored under the
repository's overall MIT license:

- `domain-teams/` — entire plugin (planning / code / docs / qa / devops / design / research / copywriting / skill team skills)
- `obsidian/skills/using-obsidian/` — router
- `obsidian/skills/obsidian-daily/` — daily workflow
- `obsidian/skills/obsidian-vault-setup/` — vault configurator
- `obsidian/skills/obsidian-tldr/` — conversation summary saver
- `obsidian/skills/obsidian-file-intel/` — file content extractor
- `obsidian/skills/dashboard-design/` — dashboard design workflow
- `philosophers-toolkit/` — entire plugin
- `repo-wiki/` — entire plugin (init / ingest / query skills + templates; conceptual lineage credited above)

## External Runtime Dependencies (not bundled)

These are referenced at runtime but not bundled in this repository:

- `feature-dev:code-architect` — Anthropic official plugin, dependency of `domain-teams:code-team` (not embedded; users install the `feature-dev` plugin separately)

## Reporting License Issues

If you believe a component is incorrectly attributed or a license notice
is missing, please open an issue at
https://github.com/kouko/monkey-skills/issues.
