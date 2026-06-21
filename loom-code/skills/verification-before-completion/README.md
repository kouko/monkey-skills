# verification-before-completion

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> **HARD-GATE — NO "DONE" WITHOUT PACKAGE-LEVEL TEST INVOCATION.** Per P3-B. Runs the canonical package-level test command (`npm test` / `pytest` / `go test ./...` / `cargo test` / etc.) and refuses "done" claims without invocation evidence. Catches: test interaction bugs (A + B together fail), orphan tests (exist but not in default suite), lint-passes-but-tests-fail, manual-testing-isn't-verification.

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## Three failure modes only package-level catches

1. **Test interaction bugs** — Test A alone PASS, B alone PASS, A+B together FAIL (shared mutable state, fixture leakage, port conflicts).
2. **Orphan tests** — Test file exists, has assertions, never runs (missing from `tests/` glob, wrong extension, excluded by config). Author thinks coverage exists; reality has a hole.
3. **Lint ≠ tests** — TypeScript compiles + ESLint clean + runtime null-deref. Static analysis is orthogonal to test execution.

## When to use

- Before declaring any feature / task / branch "done"
- Auto-invoked by `subagent-driven-development` at end of each task (orchestrator choice for fast suites)
- Auto-invoked by `finishing-a-development-branch` as Step 2 (always)

## When NOT to use

Per [`SKILL.md`](SKILL.md) §When NOT to Use:
- No tests exist yet (brand-new repo, this commit adds the first test)
- Pure doc / config / generated regen (no runtime behavior change)
- Test infrastructure broken (runner crashes, not test failures)
- Explicit user override AND change matches exempt category

## What ships

- [`SKILL.md`](SKILL.md) — HARD-GATE measure, exemption list, 4-step process, 8 Red Flags refused.
- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — canonical command per language/build tool (20+ stacks: JS/TS/Python/Go/Rust/Ruby/Java/C#/Elixir/PHP/Swift/Dart/D/Bazel/Make/just); monorepo handling; "0 tests ran" detection per runner; slow-suite handling.

## Cross-skill contract

- **Invoked by** `subagent-driven-development` (optional, per-task end) + `finishing-a-development-branch` (mandatory Step 2).
- **Routes failures to** `tdd-iron-law` (for obvious-cause failures → write RED for the case) or `systematic-debugging` (for non-obvious failures → 4-phase REPRODUCE flow).
- **Does NOT replace CI** — CI runs after push; this skill runs before push so push carries clean diffs.

## What this skill does NOT do

- Does **not** write tests (`tdd-iron-law`'s job).
- Does **not** judge code quality (`requesting-code-review` / SDD's reviewers).
- Does **not** decide which tests should exist — the suite is what it is; this skill verifies it runs + passes.

## See also

- [`SKILL.md`](SKILL.md) — operational spec.
- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — command table.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — discipline that creates the tests.
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — sibling pre-merge gate (human review).
- [`../systematic-debugging/SKILL.md`](../systematic-debugging/SKILL.md) — when failure is non-obvious.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 7 (Verification).
