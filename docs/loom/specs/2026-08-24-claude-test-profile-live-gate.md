# Claude test profile for live-host gate — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-24
> **Author**: Codex with user approval

## Design-side on-ramp

not fired — this is an internal test-profile and release-gate correction, not a product-facing design change.

## Queue relation

unqueued — it unblocks the already-approved cross-host release gate rather than displacing a product bet.

## Problem

When a release gate must exercise Claude Code, it needs a persistent authenticated profile without changing the developer's daily Claude profile or requiring the developer to paste a command on every run.

## Users

- The repository maintainer — needs one-time authentication and then unattended live-host verification.
- The release-gate runner — must use a deliberately mutable test profile while proving the daily profile stays unchanged.

## Smallest End State

The dotfiles repository provides a `claude-test` profile following its existing named-profile convention. The live-host gate uses only that exact profile, treats changes inside it as expected runtime state, and continues to fail if daily settings, Codex authentication, or either host's plugin state changes. A missing test-profile login is a clear, fail-closed diagnostic rather than a request for a disposable sandbox.

- BI-1 — The managed `claude-test` profile can be installed, updated, and invoked through the established dotfiles profile pattern.
- BI-2 — The live-host gate accepts only the dedicated test profile and preserves daily settings, authentication, and plugin integrity.
- BI-3 — A missing dedicated-profile login fails with an actionable diagnostic without exposing credentials.

## Current State Evidence

- **Forward**: `/Users/kouko/dotfiles/claude/README.md` — heading `Profiles（多帳號）` defines named `CLAUDE_CONFIG_DIR` profiles and their aliases.
- **Reverse**: `/Users/kouko/dotfiles/_scripts/install-claude.sh` — function `install_profile()` installs marketplaces and plugins from each profile's `settings.json`.
- **Error**: `loom-code/scripts/live_host_review_gate.py` — message `claude config dir must be a caller-owned disposable temporary sandbox` rejects a durable named profile.
- **Data**: `loom-code/scripts/live_host_review_gate.py` — the former full-tree `_snapshot_user_state()` sees host-managed session and log writes unrelated to the release probe.
- **Boundary**: `[SECURITY] /Users/kouko/dotfiles/claude/README.md` — phrase `Claude Code-credentials-<config-dir-hash>` records per-profile Keychain credential separation.
- **Evidence paths**:
  - `/Users/kouko/dotfiles/claude/README.md` — `Profiles（多帳號）`
  - `/Users/kouko/dotfiles/zsh/.zshrc` — `# Claude`
  - `/Users/kouko/dotfiles/_scripts/stow-install.sh` — `mkdir -p`
  - `/Users/kouko/dotfiles/_scripts/install-claude.sh` — `install_profile()`
  - `loom-code/scripts/live_host_review_gate.py` — `create_workspace`, `_snapshot_user_state`, `check_claude_auth`

## Decision

Add a minimal `~/.claude-test` profile to dotfiles and make it the only accepted Claude credential root for this live gate. The gate will no longer rewrite `HOME` or require a caller-created `/private/tmp` sandbox; it will record the dedicated profile as intentionally mutable while retaining snapshots of daily settings, Codex authentication, and both hosts' plugins. We will not introduce a background macOS service or a separate paid API credential in this change.

Protected regular files are compared with an in-memory SHA-256 integrity digest plus filesystem identity metadata; neither file contents nor digests are written to a report. Plugin protection covers declared state files and plugin manifests, not cache payloads, logs, or session data.

- BI-4 — The release gate uses the named profile without `HOME` rewriting and without a per-run login command.
- BI-6 — The integrity snapshot excludes host-managed session, log, and cache files, which can change without a gate mutation.

## Out of Scope

- Creating the one-time Claude Max login interactively.
- Launchd, GitHub Actions, or remote CI execution.
- Copying daily plugins, hooks, MCP servers, or instructions into the test profile.
- Treating every host-managed session, log, or cache write as a release-gate mutation.

## Alternatives Considered

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| Per-run disposable config directory | Existing live gate | It still requires repeated manual login and was not a stable automation boundary. |
| Replace `HOME` with a temporary directory | Current WIP experiment | It made the dedicated profile's authentication unavailable. |
| Dedicated API credential in CI | [GitHub OIDC](https://docs.github.com/en/actions/concepts/security/openid-connect) | Sound long-term option, but adds credential and billing scope beyond this correction. |

## What Becomes Obsolete

- BI-5 — The caller-supplied disposable Claude sandbox and its exact mutable-sandbox authorization flag are removed from the live-gate interface.

## Open Questions

N/A — the user approved the named-profile approach and its intentionally minimal configuration.

## Diagrams

N/A — no flow/state/architecture-shaped content: the existing profile boundary is sufficiently described by the named configuration root.
