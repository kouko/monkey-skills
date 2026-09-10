# loom-memory

> **An optional, passively-triggered repository-memory capability with an
> OKF v0.2-compatible store profile.** It installs and works standalone —
> no dependency on `loom-code`, `loom-design`, or `loom-workflow` — and any
> of them, or a user working without any of them, can invoke the same
> public memory skill.

**Status**: v0.1.0 — the first release ships the public memory skill with
its four operations, the OKF-profile validator and index generator, and the
one-shot legacy-store migration. See [CHANGELOG.md](CHANGELOG.md).
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: part of [`monkey-skills`](https://github.com/kouko/monkey-skills)

---

## What this is

Repository knowledge — lessons, gotchas, decisions worth not re-learning —
outlives any single change. loom-memory is where that knowledge lives: a
store of Markdown documents conforming to the Open Knowledge Format (OKF)
v0.2 profile, plus one public skill that recalls, records, reconciles, and
retires entries in it.

The capability is passive: it acts only when the user explicitly asks to
remember, recall, reconcile, or retire repository knowledge, or when an
agent independently identifies a concrete need for prior repository
experience. No Loom station invokes it merely because that station was
reached, and its absence never blocks `loom-code`, `loom-design`, or any
other consumer — an absent store or an empty recall result is a normal
no-memory result, not a failure.

## Independently installable

loom-memory ships as its own plugin. Its skill, store template, and
validator live entirely inside this plugin directory, and its manifests
declare no mandatory dependency on `loom-code`, `loom-design`, or
`loom-workflow` — unlike `loom-design`, it does not read a contract
package from any sibling plugin. `loom-code` and `loom-design` likewise
declare no dependency on it: composition happens only through
plugin-qualified skill names and the project's own repository files, never
through another plugin's private `hooks/`, `skills/`, or `scripts/` paths.

## OKF v0.2-compatible store

The store this plugin manages conforms to OKF v0.2: every non-reserved
Markdown document carries parseable YAML frontmatter with a non-empty
`type`, and the reserved `index.md` and `log.md` files (where present)
follow their reserved structure. That conformance is what lets the store
be read and validated by any tool that understands the OKF profile, not
only by this plugin.

## Install

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-memory@monkey-skills
claude plugin list | grep loom-memory     # expect: enabled
```

loom-memory installs and runs alone. `loom-code` and `loom-design` are
never required — they compose with it only through plugin-qualified skill
names and the project's own `docs/loom/` (or equivalent) artifacts.

### Codex CLI

Install the Codex plugin the same way; it ships its own `.codex-plugin/plugin.json`.

## Licence

MIT, as part of `monkey-skills`.
