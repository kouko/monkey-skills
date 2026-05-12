# gws-toolkit

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> ✅ **Phase 1 stable (2026-05-06).** Successor to [`slides-toolkit/`](../slides-toolkit/), seeded 2026-05-04 via strangler-fig fork. Phase 1 (vendor + α-trim + rename + scope upgrade + Drive safety wrappers + account switching) closed with all 4 validation criteria green: ≥ 1 deck generated end-to-end (108 sec; KR1 ≤ 180 sec), ≥ 1 ad-hoc Drive op via vendored `gws-drive`, ≥ 1 destructive op through three-tier `safe-delete.sh`, no KR1 regression. `slides-toolkit` is now Phase 3 deprecated and removed from the plugin marketplace; existing installations keep working but new users should land here. Not affiliated with Google.

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
`gws-toolkit` skills the repetitive layer (deck plumbing) so time and
attention land on content and design judgement. Beyond Slides, the
toolkit covers ad-hoc Drive / Docs / Sheets operations through 5
vendored upstream `gws-*` skills (Apache-2.0).

The toolkit follows the **Platform Pivot architecture** (PRODUCT-SPEC
v0.2): a backend-agnostic design knowledge layer (`slides-design`) is
decoupled from a pluggable execution layer. MVP ships the
`google-slides` backend only; `html` / `pptx` / `marp` backends are
Phase 2+, trigger-gated.

## Status

| Aspect | Value |
|---|---|
| Release | `0.5.0` (see [`CHANGELOG.md`](CHANGELOG.md)) |
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
/plugin install gws-toolkit@monkey-skills
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

## Account management

Day-to-day account operations after `/gws-setup` is done. The toolkit
stores one refresh token at a time; the OAuth client config
(`client_secret.json`, `env.sh`) is preserved across logins, so
re-auth and account switch never require redoing the GCP Console
steps.

### Re-auth on 7-day expiry (same account)

External + Testing-mode OAuth refresh tokens expire after 7 days.
When that hits:

```
bash scripts/gws/refresh-auth.sh
```

Re-runs `gws auth login` with the same scopes; the browser prompt is
brief (already-authorised app) and the new refresh token is good for
another ~7 days.

### Switch to a different Google account

```
bash scripts/gws/gws-login.sh --switch
```

Clears local credentials via `gws-logout.sh`, then re-runs OAuth.
Google's account picker appears in the browser (when multiple Google
accounts are signed in to the browser session); pick the new account
and the new refresh token is stored. Without `--switch`,
`gws-login.sh` is idempotent — exits 0 if already authed.

### Logout

```
bash scripts/gws/gws-logout.sh
```

Clears local credentials only (`credentials.enc` + `token_cache.json`
+ Keychain entry). Server-side, the refresh token remains valid until
its natural ~7-day Testing-mode expiry. For immediate server-side
revocation visit
[myaccount.google.com/permissions](https://myaccount.google.com/permissions).
The toolkit deliberately does not auto-revoke server-side because
that would require decrypting `credentials.enc` to extract the
refresh token, breaking the metadata-only access pattern in
`credential-check.sh` (ASVS V14 secrets-at-rest).

## Skills

The plugin ships **9 skills** in two provenance tiers — 4
toolkit-original + 5 vendored from upstream
[`googleworkspace/cli`](https://github.com/googleworkspace/cli) at
`v0.22.5` (Apache-2.0; provenance recorded in each vendored
SKILL.md's `metadata.vendored_from`).

**Toolkit-original (4)**

| Skill | Layer | Purpose |
|---|---|---|
| `using-gws-toolkit` | Router | Inspect intent, read `slide-plan.target`, route to the right skill |
| `gws-setup` | Setup (generic) | First-time GCP Console / OAuth (4 scopes: presentations + drive + documents + spreadsheets) / `gws` + `jq` bootstrap; state detection; 7-day re-auth |
| `slides-design` | Knowledge (Slides-specific) | Minto Pyramid + SCQA narrative, chart-type selection |
| `slides-builder` | Execution (Slides-specific) | `slide-plan.json` v1.2 → pre-flight → 4-recipe chain → deck URL; placeholder-map composition pattern lives here |

**Vendored upstream (5, Apache-2.0)**

| Skill | API surface | Helper |
|---|---|---|
| `gws-shared` | auth + global flags + security rules (other 4 reference this) | — |
| `gws-drive` | Drive API v3 (about / files / permissions / changes / etc.) | toolkit's `safe-delete.sh` + `tag-create.sh` complement Drive ops |
| `gws-docs` | Docs API v1 (`documents.{batchUpdate, create, get}`) | — |
| `gws-slides` | Slides API v1 (`presentations.{batchUpdate, create, get}` + pages) | — (slides-builder is a higher-layer orchestrator, not a helper) |
| `gws-sheets` | Sheets API v4 (`spreadsheets.*` + values + sheets + developerMetadata) | — |

`using-gws-toolkit` is deliberately backend-agnostic so future
`html-builder` / `pptx-builder` / `marp-builder` skills can reuse the
same routing entrypoint without changes.

For raw Drive / Docs / Sheets / Slides API method discovery, the
vendored per-API skills are first-line. For higher-level toolkit
opinions (slide-plan pipeline, three-tier delete safety, provenance
tagging), the toolkit-original layer is first-line.

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
│  Knowledge      │  │  Setup          │  │  Slides exec         │
│  (Slides)       │  │  (generic gws)  │  │  (build pipeline)    │
│                 │  │                 │  │                      │
│  slides-design  │  │  gws-setup      │  │  slides-builder      │
│                 │  │                 │  │  (placeholder-map +  │
│  Minto · SCQA · │  │  GCP / OAuth /  │  │   4 inline recipes)  │
│  chart pick     │  │  gws bootstrap  │  │                      │
└─────────────────┘  └────────┬────────┘  └──────────┬───────────┘
                              │                      │
                              └──────────┬───────────┘
                                         ▼
              scripts/gws/*.sh  ──┐
              (bootstrap, gws-wrap, env-guard,
               credential-check, refresh-auth,
               safe-delete, tag-create)
                                  ▼
              gws CLI · ~/.cache binaries
                                  ▼
                  Google Workspace APIs
              (Slides v1 / Drive v3 / Docs v1 / Sheets v4)
                                  ▼
                  Vendored upstream skills as
                  per-API method reference:
                  gws-shared / gws-drive / gws-docs /
                  gws-slides / gws-sheets
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
