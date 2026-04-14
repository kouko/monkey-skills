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

## External Runtime Dependencies (not bundled)

These are referenced at runtime but not bundled in this repository:

- `feature-dev:code-architect` — Anthropic official plugin, dependency of `domain-teams:code-team` (not embedded; users install the `feature-dev` plugin separately)

## Reporting License Issues

If you believe a component is incorrectly attributed or a license notice
is missing, please open an issue at
https://github.com/kouko/monkey-skills/issues.
