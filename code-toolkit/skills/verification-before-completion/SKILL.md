---
name: verification-before-completion
description: 'Use BEFORE declaring "done" — claiming a task / branch / feature complete without running the package-level test suite is the failure mode this skill exists to prevent. Examples: "I''m done with feature X", "this is ready to ship", "branch is finished", "tests pass" (without showing the invocation), "merge this", any "complete" / "ready" / "finished" framing. HARD-GATE: tests MUST run at package level (npm test / pytest / go test / cargo test / bundle exec rspec / mvn test / etc.), not single-file lint or one-test-spotcheck. Per P3-B. Catches: tests passing in isolation but breaking together (test interaction bugs); orphan tests not in default suite; lint missing runtime regressions; "it works on my machine" before actual suite invocation. Refuses "tests pass" claims without invocation evidence. 完了前検証・パッケージレベルテスト強制・ "tests pass" 主張検証。完成前驗證・套件層級測試強制・"測試過了" 主張驗證。'
version: 0.5.2
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, your dispatcher already decided whether verification applies. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## The HARD-GATE

> **NO "DONE" WITHOUT PACKAGE-LEVEL TEST INVOCATION.**

"Done" without running the actual test suite at package level (`npm test` / `pytest` / `go test ./...` / `cargo test` / etc.) is the failure mode this skill exists to prevent. Single-file lint passes, individual test files passing, "the code looks right" — none of these are verification. The package-level invocation is the verification.

Three failure modes only the package-level run catches:

1. **Test interaction bugs**: Test A passes alone; Test B passes alone; A + B together fail (shared mutable state, database fixtures, port conflicts, env leakage).
2. **Orphan tests**: A test file exists but isn't included in the default suite (missing from `tests/` glob, excluded by config, wrong file extension). The author thinks coverage exists; CI thinks coverage exists; reality has a hole.
3. **Lint passes ≠ tests pass**: TypeScript compiles + ESLint clean + still has a runtime null dereference covered by no test. Lint is not verification.

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **No tests exist yet** | Brand-new repo, no test infrastructure set up, this is the commit that adds the first test | "Tests exist but I didn't write any for this change" — that's Iron Law violation; not exempt |
| **Pure doc / config / generated regen** | Markdown change, version bump, regenerated protobuf stubs, `.gitignore` edit | Config that affects runtime behavior (retries: 3 → 5; feature flag flipped) — not exempt |
| **Test infrastructure broken** | The test runner itself crashes (not a test failure — the runner doesn't run); a dependency-install failure prevents even starting tests | "Tests are slow so I skipped them" — that's the Red Flag below |
| **Explicit user override + scoped** | User says "skip verification for this PR because it's only doc" AND the change matches exempt category 2 | "Just merge, I checked manually" — that's the rationalization |

When uncertain, ask: *"If this shipped and broke production, would I be able to point to the test run that should have caught it?"* If no, verification applies.

## Process

1. **Detect the package-level test command** for this project. See [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — table of canonical invocations per language / build tool. Detection signals:
   - `package.json` → `npm test` / `pnpm test` / `yarn test` (check `scripts.test`)
   - `pyproject.toml` / `setup.py` / `tox.ini` → `pytest` or `tox`
   - `go.mod` → `go test ./...`
   - `Cargo.toml` → `cargo test`
   - `Gemfile` → `bundle exec rspec` or `bundle exec rake test`
   - `pom.xml` → `mvn test`
   - `build.gradle` → `gradle test`
   - `*.csproj` / `*.sln` → `dotnet test`
   - `mix.exs` → `mix test`
   - `composer.json` → `vendor/bin/phpunit` or `composer test`

2. **Run the command from project root.** Not from a subdirectory; not on a single file; not in IDE-watch-mode. The canonical CI-equivalent invocation.

3. **Read the exit code AND the output.** Exit 0 alone is not verification — *what was actually run*? Look for: total test count > 0, all-pass summary line, no `[skipped]` covering the touched modules. If exit 0 but 0 tests ran, that's a configuration bug, not a pass.

4. **If failures**, surface them. Do NOT mark "done." User decides remediation (route back to `tdd-iron-law` for the failing case; or `systematic-debugging` if the failure is non-obvious).

5. **If pass**, return verdict with evidence: the command run, the test count, the summary line.

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream invocation** | `subagent-driven-development` | Optionally invokes this skill at end of each task triad (orchestrator choice — for fast suites, run per-task; for slow suites, defer to end of plan) |
| **Upstream invocation** | `finishing-a-development-branch` | Invokes this skill as Step 2 of close-branch flow (after `requesting-code-review`) |
| **Downstream (PASS)** | `finishing-a-development-branch` proceeds to git-memory + commit | |
| **Downstream (FAIL)** | Surface to user; user decides whether to route to `tdd-iron-law` (failing case → write RED → fix → GREEN) or `systematic-debugging` (failure non-obvious) | |
| **Loads** | `references/test-invocation-by-stack.md` | Canonical command table |

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Tests pass."* (without showing invocation) | Unverified claim. The user's mental model of "passing" may not match what `npm test` actually says. | Refuse to accept. Run `npm test` (or equivalent); paste output; THEN you have evidence. |
| *"I ran the test file directly, it passed."* | Single-file run misses test interaction + orphan-test failure modes. | Run package-level. The single-file run is necessary but not sufficient. |
| *"Lint passes / TypeScript compiles."* | Static analysis ≠ tests. Runtime null-deref / off-by-one / wrong-string-format passes lint, fails tests. | Run tests. Lint is orthogonal. |
| *"Tests are slow, I'll let CI catch it."* | CI catches it AFTER you push. The verification-before-push gate exists so you push only clean diffs. | Run locally first. If suite is genuinely too slow (>10 min), see `systematic-debugging` references for slow-suite isolation. |
| *"It worked when I tested manually."* | Manual testing is exploration, not verification. Manual test doesn't ratchet — next regression won't be caught. | Run the suite. Add a test for what you tested manually if it isn't covered. |
| *"I just made a 1-line tweak after the tests passed."* | The tweak might be the bug. Re-run. | Re-run. 30 seconds to verify; weeks to recover from a 1-line regression in prod. |
| *"The suite has known-failing tests, just ignore."* | Known-fail tests are tech debt; ignoring them means "well, one more failure won't matter" — which is how 1 known-fail becomes 30. | Distinguish known-fail (documented xfail / skip with ticket) from new-fail. If your change is the new-fail, that's the bug; if your change leaves known-fail alone, the suite is still all-pass for what your change touched. |
| 「テストはパスしてる / 測試 OK / 跑過了」 | Same rationalization, localized. | Same refusal — show the invocation. |

## What this skill does NOT do

- Does **not** write tests. That's `tdd-iron-law`'s job.
- Does **not** judge code quality. That's `requesting-code-review` / SDD's per-task reviewer.
- Does **not** replace CI. CI runs on push to remote; this skill runs before push so push only carries clean diffs.
- Does **not** decide which tests should exist. The suite is what it is; this skill verifies the existing suite runs and passes.

## See also

- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — canonical test commands per language / build tool, plus detection signals.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — discipline that creates the tests this skill runs.
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — sibling pre-merge gate (human-judgment quality review).
- [`../systematic-debugging/SKILL.md`](../systematic-debugging/SKILL.md) — when the suite has a failure you don't understand, route here from a verification fail.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator that invokes this skill as Step 2.
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; this skill is Stage 7 (Verification).
