# using-code-toolkit

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Router + framework charter for code-toolkit. Loaded into every Claude Code / Codex CLI session by the plugin's SessionStart hook so the agent knows the rules before writing any code.

Part of the [code-toolkit](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans deciding whether and how to install.

## Why a router

`code-toolkit` ships a Superpowers-style process layer (brainstorm → plan → SDD → TDD iron-law → debugging → code-review → finish-branch) plus a knowledge layer that is a byte-identical functional copy of `domain-teams:code-team` standards. Without a router, the agent must remember which skill to load when and pick the right Beck / Martin / Fowler / OWASP section to cite. The router makes that decision and provides the agent's North Star.

The router is injected at SessionStart so the agent does **not** rely on the user remembering to call it. Phase 1.5 will add a `CODE_TOOLKIT_MODE=off` env var for users who already have `obra/superpowers` installed and want only one hook running.

## What it routes between

| Stage | Skill | v0.1.0 status |
|---|---|---|
| Discovery | [`brainstorming`](../brainstorming) | ✅ shipped |
| Planning | [`writing-plans`](../writing-plans) | ✅ shipped |
| Execution | [`subagent-driven-development`](../subagent-driven-development) | ✅ shipped |
| Discipline | [`tdd-iron-law`](../tdd-iron-law) | ✅ shipped |
| Repair | [`systematic-debugging`](../systematic-debugging) | ✅ shipped |
| Review | [`requesting-code-review`](../requesting-code-review) | ✅ shipped |
| Verification | [`verification-before-completion`](../verification-before-completion) | ✅ shipped |
| Branch close | [`finishing-a-development-branch`](../finishing-a-development-branch) | ✅ shipped |
| Auxiliary | [`using-git-worktrees`](../using-git-worktrees) | ✅ shipped (lateral utility, not in linear flow) |

## When to use

- Any coding task — feature, bug fix, refactor, migration, dependency bump, review.
- Trigger phrases (any locale): "add a feature / refactor / fix this bug / 機能を追加 / バグを直して / リファクタ / 加個功能 / 重構 / 修 bug".

## When NOT to use

- Pure read-only questions about code ("what does this function do?") — the router does not write or audit; answer directly.
- Auditing an already-shipped artifact for compliance scoring — use `domain-teams:code-team` (passive gate entry).
- Writing or refactoring a *skill* (not application code) — use `dev-workflow:skill-creator-advance` / `skill-refactor`.

## Coexistence

- **`domain-teams:code-team`** — passive gate entry, kept for auditing. Knowledge layer here is its functional copy; drift-checked by `scripts/verify-drift.py`.
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — code-toolkit delegates to these at the right moments.
- **`obra/superpowers`** — overlapping skill names + dual SessionStart hook. To disable code-toolkit's hook: `export CODE_TOOLKIT_MODE=off`.

## See also

- [`SKILL.md`](SKILL.md) — operational spec the agent loads.
- [`../../PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) — business / users / Q-lock.
- [`../../TECH-SPEC.md`](../../TECH-SPEC.md) — architecture / hooks / SSOT.
- [`../../ROADMAP.md`](../../ROADMAP.md) — phase plan / decision ledger.
