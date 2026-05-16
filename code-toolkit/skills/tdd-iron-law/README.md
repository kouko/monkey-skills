# tdd-iron-law

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.** Grounded in Beck (2002) *Test-Driven Development: By Example* Preface + Ch.1 + Part II, ISBN 978-0321146533; Martin (2008) *Clean Code* Ch.9 Three Laws of TDD, ISBN 978-0132350884; 和田卓人 訳 (2017) 『テスト駆動開発』 ISBN 978-4274217883.

Part of the [code-toolkit](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## What this skill enforces

A single rule, restated in three primary sources:

- **Beck (2002) Preface**: *"Write the test you wish you had. Make it fail. Make it pass. Make it clean."*
- **Martin (2008) Clean Code Ch.9, Three Laws of TDD §1**: *"You may not write production code until you have written a failing unit test."*
- **和田卓人 訳 (2017) 訳者解説**: 「テストは仕様の具体化であり、設計の feedback loop である」.

When the rule is violated, the only correct response is: **delete the code, write the test, start over.** Not "add tests later." The deletion restores the feedback loop that the violation disabled.

## When to use

Auto-invoked by `using-code-toolkit` whenever the user starts implementation work — feature, bug fix, refactor, migration. Also self-invoked by `subagent-driven-development` inside each implementer subagent.

## When NOT to use

Narrow, enumerated exemption list — see [`SKILL.md`](SKILL.md) §When NOT to Use:

- Throwaway / spike code (deleted within the same session, never committed)
- Pure code generation (regenerated output, e.g. protobuf stubs, ORM migrations)
- Trivial getter / setter / pure delegation
- Pure configuration files (no embedded executable logic)
- Explicit user override AND the task matches one of the above

If your work is not on this list, the Iron Law applies. Do not invent new exceptions.

## What this skill does NOT do

- Does not measure coverage. Coverage is a lagging indicator; TDD targets the feedback loop, not a percentage.
- Does not write tests for the user — it enforces that the user / agent writes the failing test before the production code.
- Does not replace `verification-before-completion` (Phase 3), which re-checks that every shipped behavior had a corresponding failing-then-passing test in commit history.

## Knowledge layer

[`standards/tdd-standard.md`](standards/tdd-standard.md) is a byte-identical functional copy of `domain-teams/skills/code-team/standards/tdd-standard.md` plus a 5-line SSOT header. Drift is policed by `code-toolkit/scripts/verify-drift.py`. To change the discipline, edit the canonical file in `domain-teams:code-team` and run `code-toolkit/scripts/distribute.py` in the same commit.

## See also

- [`SKILL.md`](SKILL.md) — operational spec the agent loads (iron law + cycle + exception list + red flags + false-green diagnostic).
- [`standards/tdd-standard.md`](standards/tdd-standard.md) — full canonical TDD discipline (F.I.R.S.T, Three Laws, anti-patterns, JP anchor).
- [`references/testing-anti-patterns.md`](references/testing-anti-patterns.md) — anti-pattern index with primary-source rebuttals.
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; explains where this skill fits in the flow.
- [`../../scripts/canonical/README.md`](../../scripts/canonical/README.md) — SSOT pointer + drift policy.
