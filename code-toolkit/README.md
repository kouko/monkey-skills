# code-toolkit

> **Status**: Design-only (Phase 0 — PRODUCT/TECH/ROADMAP locked, no skill shipped yet)
> Languages: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Process-discipline + canon-grounded coding toolkit. Two-layer architecture:

- **Process layer** (Superpowers-style): 7-stage workflow with SessionStart hook auto-injection — brainstorm → plan → SDD (subagent-driven development) → TDD iron-law → systematic debugging → code-review → finish-branch.
- **Knowledge layer** (code-team grounding): byte-identical functional copy of `domain-teams:code-team` standards / rubrics / checklists. Each rule traceable to a primary source (Clean Code / Pragmatic Programmer / SOLID / Beck 2002 TDD / Fowler 2018 Refactoring / Feathers 2004 Legacy Code / OWASP ASVS v5.0.0 / 徳丸本 Ch.6).

## Status

| Phase | Version | Skills | Status |
|---|---|---|---|
| 0 | 0.1.0-draft | — | ⏳ Design lock (this PR) |
| 1 | 0.1.0 | 3 (using / tdd-iron-law / SDD) | pending |
| 1.5 | 0.1.5 | 3 (+soft-mode) | pending |
| 2 | 0.2.0 | 6 (+brainstorming / writing-plans / sys-debugging) | pending |
| 2.5 | 0.2.5 | 6 (+Codex CLI ship) | pending |
| 3 | 0.3.0 | 9 (Superpowers parity) | pending |
| 4 | 1.0.0 | 9 (GA) | pending |

See [ROADMAP.md](ROADMAP.md) for full plan.

## Design Documents

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — business / target user / goals / Q-lock
- [TECH-SPEC.md](TECH-SPEC.md) — architecture / SSOT / hooks / interface contracts
- [ROADMAP.md](ROADMAP.md) — phase plan / decision ledger

## Coexists with

- **`domain-teams:code-team`** — passive gate entry (审查既有產出). code-toolkit is the active-construction entry.
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — code-toolkit delegates to these at the right moments.

## Conflicts with

- **`obra/superpowers`** — both ship SessionStart hooks and overlapping skill names. Resolve by setting `export CODE_TOOLKIT_MODE=off` to disable this plugin's hook injection.

## License

MIT
