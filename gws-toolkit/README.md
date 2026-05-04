# gws-toolkit

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> 🚧 **Work in progress — not yet stable.** Successor to [`slides-toolkit/`](../slides-toolkit/), seeded by direct copy on 2026-05-04. Internal architecture is being generalized from "Slides-only" to "generic Google Workspace": vendored upstream `gws-shared` / `gws-drive` / `gws-docs` / `gws-slides` / `gws-sheets` skills, broader Drive operations with three-tier delete safety, OAuth scope expansion, and toolkit-original setup automation + Slides design knowledge layer. Until this banner is removed, **use `slides-toolkit/` for daily work.** This toolkit is not affiliated with Google.

> Brief → Google Workspace artifacts (Slides / Docs / Sheets / Drive) via Claude Code skills. Pure shell + `gws` CLI, no Python or gcloud required.

> ⚠️ **Cowork compatibility — Claude Code CLI / Code tab only.** Google
> Slides and Drive API calls are blocked by the Claude Desktop Cowork
> sandbox URL allowlist (same constraint as `investing-toolkit`; see
> [investing-toolkit MCP setup retrospective](../investing-toolkit/docs/mcp-setup.md)).
> If you are on Cowork, switch to Claude Code CLI or the Claude Desktop
> Code tab.

## Background

Producing Google Slides decks regularly involves a large mechanical
share — text replacement, image upload, placeholder alignment.
`slides-toolkit` skills the repetitive layer so time and attention
land on content and design judgement, not deck plumbing.

The toolkit follows the **Platform Pivot architecture** (PRODUCT-SPEC
v0.2): a backend-agnostic design knowledge layer (`slides-design`) is
decoupled from a pluggable execution layer. MVP ships the
`google-slides` backend only; `html` / `pptx` / `marp` backends are
Phase 2+, trigger-gated.

## Status

| Aspect | Value |
|---|---|
| Release | `0.1.0-mvp` (see [`CHANGELOG.md`](CHANGELOG.md)) |
| Backends | `google-slides` (MVP) · `html` / `pptx` / `marp` Phase 2+ trigger-gated |
| Platform | macOS (darwin-arm64 / darwin-x86_64) |
| Account scope | Personal Google account (`@gmail.com`); Workspace accounts Phase 2+ |
| Runtime posture | shell + curl + browser; toolkit self-fetches `gws` and `jq` binaries |
| License | MIT |

## Install

Add the plugin via the `monkey-skills` marketplace, then restart Claude
Code so it discovers the skills.

```bash
# from inside Claude Code
/plugin install slides-toolkit@monkey-skills
```

## Quick start

Two phases. The first-time setup is a one-shot. After that, every deck
goes through the second phase.

### 1. First-time setup (target: ≤ 20 minutes — KR2)

```
> /gws-setup
```

Routes to the `gws-setup` skill. It detects current state,
fetches `gws` + `jq` to `~/.cache/slides-toolkit/bin/`, walks you
through the manual GCP Console steps (OAuth Client + Test User), and
writes `~/.config/gws/env.sh` with the issue #119 workaround if your
account needs it.

This is bounded by Google's OAuth policy (External + Testing mode); see
[`docs/google-oauth-automation-limits.md`](docs/google-oauth-automation-limits.md)
for what can and cannot be automated.

### 2. Generate a deck (target: ≤ 3 minutes — KR1)

```
> /using-gws-toolkit
> "Turn this outline into a 6-slide product proposal"
```

The router (`using-gws-toolkit`) inspects intent, optionally
delegates to `slides-design` for narrative structure (Minto / SCQA /
chart selection), and hands a `slide-plan.json` v1.2 to
`slides-builder`. The builder runs the four-step pipeline —
create blank deck → create slides with predefined layouts → insert
text → insert local images — and returns the Drive URL.

Both `/using-gws-toolkit` and `/gws-setup` are skill
auto-routes (no `commands/` shims; the plugin ships zero slash
commands). Type the skill name and Claude Code dispatches.

## Skills

The plugin ships five skills across three layers.

| Skill | Layer | Purpose |
|---|---|---|
| `using-gws-toolkit` | Router (backend-agnostic) | Inspect user intent, read `slide-plan.target`, route to the right skill |
| `slides-design` | Knowledge (backend-agnostic) | Minto Pyramid + SCQA narrative, chart-type selection — applies to any backend |
| `gws-setup` | google-slides backend | First-time GCP Console / OAuth / `gws` bootstrap; state detection on subsequent runs |
| `google-slides-api` | google-slides backend | Low-level per-op recipe reference — `presentations.create`, `batchUpdate createSlide`, `insertText`, `createImage` |
| `slides-builder` | google-slides backend | High-level orchestration — `slide-plan.json` v1.2 → pre-flight → 4-recipe chain → deck URL |

`using-gws-toolkit` and `slides-design` are deliberately
backend-agnostic so future `html-builder` / `pptx-builder` /
`marp-builder` skills can reuse the same routing entrypoint and design
references without changes.

## Prerequisites

| Item | Requirement |
|---|---|
| OS | macOS 14+ (darwin-arm64 / darwin-x86_64). Linux / WSL are Phase 2+. |
| Shell | zsh or bash (default macOS zsh is fine) |
| Network tool | `curl` (preinstalled on macOS) |
| Browser | Chrome or Safari (needed once for the GCP Console steps) |
| Google account | Personal `@gmail.com`. Workspace accounts are Phase 2+. |

**Not required**: Python, uv, gcloud, brew, npm. The `gws` and `jq`
binaries are fetched into `~/.cache/slides-toolkit/bin/` by
`scripts/gws/bootstrap.sh` over HTTPS with `curl -f`.

## Architecture

Three layers. The router and the design knowledge layer are
backend-agnostic; only the execution layer binds to a concrete output
format.

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1 — Router (backend-agnostic)                        │
│  using-gws-toolkit                                       │
│  inspect intent · read slide-plan.target · dispatch         │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────────┐
        ▼                    ▼                        ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│  Layer 2 —      │  │  Layer 3 —      │  │  Layer 3 —           │
│  Design         │  │  Backend exec   │  │  Backend exec        │
│  knowledge      │  │  (onboarding)   │  │  (build pipeline)    │
│  (agnostic)     │  │                 │  │                      │
│  slides-design  │  │  google-slides- │  │  google-slides-      │
│                 │  │  setup          │  │  builder             │
│  Minto · SCQA · │  │                 │  │      ↓ uses          │
│  chart pick     │  │  GCP / OAuth /  │  │  google-slides-api   │
│                 │  │  gws bootstrap  │  │  (per-op recipes)    │
└─────────────────┘  └────────┬────────┘  └──────────┬───────────┘
                              │                      │
                              └──────────┬───────────┘
                                         ▼
                              scripts/gws/*.sh
                              gws CLI · ~/.cache binaries
                                         ▼
                              Google Slides + Drive API
                                         ▼
                                   Deck URL
```

Phase 2+ backends (`html-builder` / `pptx-builder` / `marp-builder`)
slot into Layer 3 alongside `slides-builder` without changing
Layer 1 or Layer 2. See PRODUCT-SPEC §2.1, §2.2 and TECH-SPEC §2.1,
§2.2.

## Security

Credentials never enter the repo. Two complementary mechanisms enforce
this (TECH-SPEC §8):

**Claude tool-layer block** — `.claude/settings.json` denies any
Read / Bash / Write that touches the gws credential store:

```json
{
  "permissions": {
    "deny": [
      "Read(~/.config/gws/**)",
      "Read(~/.cache/slides-toolkit/bin/.version)",
      "Bash(cat ~/.config/gws/*)",
      "Bash(cat ~/.config/gws/**)",
      "Bash(cp ~/.config/gws/* *)",
      "Bash(git add ~/.config/gws/*)",
      "Write(~/.config/gws/**)"
    ]
  }
}
```

**Repo-relative ignore** — `.gitignore` blocks credential files that
might land inside the repo tree:

```
.config/gws/
*/keyring-file.json
*/env.sh
.cache/slides-toolkit/
```

`.gitignore` cannot match `~/.config/gws/**` (git uses repo-relative
paths and does not expand `~`); the home-directory leg is owned by the
`settings.json` deny rule above. If credentials are ever leaked,
follow the incident playbook in TECH-SPEC §8.4.

## Links

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — product direction, Job Story, OKR / KR, Non-Goals, Phase 2+ triggers
- [TECH-SPEC.md](TECH-SPEC.md) — module design, `slide-plan.json` v1.2, shell script contracts, security
- [CHANGELOG.md](CHANGELOG.md) — version history (`0.1.0-spec` → `0.6.0-i18n`)
- [docs/console-ui-reference.md](docs/console-ui-reference.md) — current Google Cloud Console UI walkthrough
- [docs/google-oauth-automation-limits.md](docs/google-oauth-automation-limits.md) — what cannot be automated and why
- [docs/gws-cli-quirks.md](docs/gws-cli-quirks.md) — gws CLI gotchas discovered in live testing
- Parent repository: [`monkey-skills`](https://github.com/kouko/monkey-skills)

## Contributing

This plugin is part of the [`monkey-skills`](https://github.com/kouko/monkey-skills)
repository. Open issues or PRs against that repo. The skill structure
follows the conventions in the repo-root `CLAUDE.md` and the
`domain-teams:skill-team` skill.

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
