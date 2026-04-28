# slides-toolkit

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 0.1.0-mvp
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

Google Slides generation toolkit — turn structured briefs (outline + tables +
local images) into finished Google Slides decks through Claude Code skills.
Single-command pipeline: `brief → deck URL ≤ 3 min`.

Backend-agnostic design knowledge layer (`slides-design`) plus pluggable
backend builders. MVP ships the Google Slides backend only; HTML / PPTX /
Marp backends are Phase 2+ and trigger-gated (see `PRODUCT-SPEC.md §3.5`).

## Status

- **Release**: MVP v0.1.0-mvp (pre-release; Platform-Pivot spec frozen 2026-04-23)
- **Backends**: `google-slides` only
- **Platform**: macOS 14+ (darwin-arm64 / darwin-x64)
- **Primary user**: kouko (個人生產力工具)
- **Runtime posture**: pure shell + `curl` + browser; `gws` / `jq` binaries
  self-fetched to `~/.cache/slides-toolkit/bin/` with SHA-256 verification

## Quick Start

Three steps from fresh machine to first deck.

### 1. Install

```bash
# Add the plugin through the monkey-skills Claude Code marketplace
# (plugin auto-activates once registered in marketplace.json)
```

### 2. Setup (first-time onboarding, ~20 min)

Inside Claude Code, invoke the setup skill:

```
/google-slides-setup
```

Walks you through:

- `gws` binary fetch + SHA-256 verify
- Google Cloud Console 4-step OAuth client setup (External + Testing mode)
- Keychain / file-backend credential storage detection
- Issue-119 workaround env var guard (`GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET`)
- First-login auth + token smoke test

Budget: **≤ 20 min** on a clean macOS box (KR2).

### 3. Generate your first deck

```
/using-slides-toolkit
```

Pick `slides-design` if you want narrative + chart-type guidance first,
then `google-slides-builder` to build the deck. Or go straight to the
builder if you already have a `slide-plan.json` and a template Drive ID
registered.

Budget: **≤ 3 min** from brief submission to Drive URL (KR1).

## Skills Inventory

| Skill | Layer | Purpose |
|-------|-------|---------|
| `using-slides-toolkit` | router (backend-agnostic) | Entry point — routes to setup / design / builder by `target` |
| `slides-design` | knowledge (backend-agnostic) | Minto Pyramid + SCQA + chart-selection reference; applies to any backend |
| `google-slides-setup` | google-slides backend | First-time onboarding (gws + GCP + auth); state-aware branching |
| `google-slides-builder` | google-slides backend | Execution layer — copy template / replaceAllText / insert-image via gws |

Phase 2+ (trigger-gated; not in MVP): `html-builder`, `pptx-builder`,
`marp-builder`.

## Prerequisites

All built into macOS 14+:

- `zsh` / `bash`
- `curl`
- Any modern browser (Google OAuth consent flow)

The toolkit self-fetches the rest:

- `gws` binary → `~/.cache/slides-toolkit/bin/gws` (SHA-256 pinned)
- `jq` binary → `~/.cache/slides-toolkit/bin/jq` (SHA-256 pinned)

**Not required**: Python, uv, gcloud, Homebrew, Node.js. Zero language
runtimes beyond the shell.

## Architecture

Three-layer design (see `PRODUCT-SPEC.md §6.3.1` + `TECH-SPEC.md §2.1-§2.2`
for the full picture):

```
┌──────────────────────────────────────────────────────┐
│ Layer 1 — Router (backend-agnostic)                  │
│   using-slides-toolkit                               │
│     → dispatches by slide-plan target field          │
└────────┬─────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────┐
│ Layer 2 — Design knowledge (backend-agnostic)        │
│   slides-design                                      │
│     → Minto / SCQA / chart-selection                 │
│     → applies to google-slides / html / pptx / marp  │
└────────┬─────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────┐
│ Layer 3 — Backend execution (backend-specific)       │
│   google-slides-setup     [MVP]                      │
│   google-slides-builder   [MVP]                      │
│   html-builder            [Phase 2+]                 │
│   pptx-builder            [Phase 2+]                 │
│   marp-builder            [Phase 2+]                 │
└──────────────────────────────────────────────────────┘
```

**Because** the design principles (narrative structure, chart selection)
are stable across output formats, while execution technology (gws / pandoc
/ python-pptx / marp-cli) evolves per backend. Decoupling keeps the
knowledge layer from churning whenever a new backend is added.

See `PRODUCT-SPEC.md` for the cross-domain product view (vision + MVP
scope + Job Story + 4 Big Risks) and `TECH-SPEC.md` for module design,
data flow, and interface contracts.

## Security Notes

Credentials never enter the repository. Two defence layers:

1. **`.claude/settings.json` deny rule** — blocks Claude tool-level Read /
   Bash / Write access to credential files (home-dir + repo-relative).
   Repo-relative `.gitignore` cannot protect `~/.config/gws/**` because
   git does not expand `~`; the deny rule closes that gap.
2. **`.gitignore`** — excludes repo-relative secret patterns:
   `.config/gws/`, `**/client_secret*.json`, `**/credentials.enc`,
   `**/.encryption_key`, `.env*`, `.cache/`, local test fixtures.

See `TECH-SPEC.md §8 Security & Credential Hygiene` for the full threat
model (OWASP ASVS v5.0.0 L1 — V1 / V2 / V5 / V13 / V14 / V16 mapping),
pre-commit hook recommendation, and credential-leak incident response
playbook.

Incident logs (if ever triggered) live in `incidents/` on demand — not
pre-created. See `incidents/README.md` for the playbook entry format.

## License

MIT — aligns with the parent `monkey-skills` repository. See `/LICENSE`
at the repo root.

## Links

- [PRODUCT-SPEC.md](./PRODUCT-SPEC.md) — planning-team spec (vision, users,
  goals, non-goals, Platform Pivot rationale)
- [TECH-SPEC.md](./TECH-SPEC.md) — code-team spec (architecture, modules,
  interfaces, testing, security, OPEN answers)
- [CHANGELOG.md](./CHANGELOG.md) — version history
- [parent repo](https://github.com/kouko/monkey-skills)
