# Testing anti-patterns the Iron Law refuses

> Curated index of anti-patterns that have a primary-source rebuttal. For the full F.I.R.S.T properties + canonical TDD discipline, see [`../standards/tdd-standard.md`](../standards/tdd-standard.md) (functional copy of `domain-teams:code-team` SSOT).

Each entry: **name** → *what it looks like* → *why it fails* → *primary-source rebuttal*.

## 1. Tests-after / "I'll add tests last"

*Looks like*: production code lands; tests are written hours / days later to "match what we built." The PR description says *"adding test coverage."*

*Fails*: the design-feedback loop is gone. By the time you write the test, every painful-to-test signal in the production code has already been baked in. You will mock around the pain rather than refactor it.

*Rebuttal*: Beck (2002) Preface — *"Write the test you wish you had. Make it fail. Make it pass. Make it clean."* The Preface frames TDD as the loop by which design feedback is obtained at the cost of one minute per cycle. Skipping the failing test is opting out.

## 2. False-green / first-run-pass

*Looks like*: a new test is added; it passes on the first run; the developer marks the work done.

*Fails*: the test is not actually testing the change. The behavior already existed (no new test needed) OR the assertion is too weak to fail. Either way, the test is decorative — it will not catch a regression.

*Rebuttal*: Martin (2008) Clean Code Ch.9, Three Laws of TDD §1–2 — *"You may not write production code until you have written a failing unit test."* and *"You may not write more of a unit test than is sufficient to fail."* Both rules require an observed RED. See also [`SKILL.md`](../SKILL.md) §False-green diagnostic for the comment-out / re-run drill.

## 3. Mocking-the-pain-away

*Looks like*: a unit test requires 6 mocks, an in-memory DB stub, and an injected clock. Setup is 40 lines; the assertion is 1 line.

*Fails*: the test is now coupled to the production code's *structure*, not its *behavior*. Refactoring the production code breaks the test. The test costs more to maintain than it earns.

*Rebuttal*: Beck (2002) Preface — *"If it's hard to test, it's probably hard to use."* The pain is the production design speaking. Refactor the production code (likely an SRP / DIP violation — see [`../standards/tdd-standard.md`](../standards/tdd-standard.md) §"Tests as Design Feedback") until the test simplifies. Do not absorb the pain into the test.

## 4. One-giant-test

*Looks like*: a single test method exercises 12 behaviors with one `assert` per behavior; if one breaks, the rest never run.

*Fails*: violates F.I.R.S.T §Independent. Diagnosis time on failure is linear in the number of intermingled behaviors. The test is also a coverage liar — failing one early assertion silently skips the rest.

*Rebuttal*: Martin (2008) Clean Code Ch.9 §F.I.R.S.T — *"Independent — tests do not depend on execution order or shared mutable state."* One behavior per test; one logical assertion per behavior (multiple `assert` statements describing the same observation are fine; multiple distinct observations are not).

## 5. Skipping refactor

*Looks like*: RED → GREEN → next feature. The duplicate code introduced in GREEN survives unrefactored across many cycles. "All tests pass" is treated as done.

*Fails*: TDD without refactor is *tests-first*, not TDD. Beck (2002) Ch.1 ends each cycle with refactor; Part II contains an entire chapter on the refactoring patterns (*Reconcile Differences*, *Isolate Change*, *Migrate Data*, etc.).

*Rebuttal*: Beck (2002) Ch.1 and Part II — refactor is non-optional, but the discipline is *with the safety net*: if any test goes red during refactor, revert and take a smaller step. The safety net is what differentiates TDD-refactor from "refactor + pray."

## 6. Sleep-based / race-coupled tests

*Looks like*: `Thread.sleep(500)` after an async operation, hoping the work finishes before the assertion runs. Tests pass on the developer's laptop, fail intermittently in CI.

*Fails*: the test hides a race condition in production. The sleep is not waiting for *the operation* — it is waiting for the *typical* wall-clock time the operation takes on this machine on this day.

*Rebuttal*: Martin (2008) Clean Code Ch.9 §F.I.R.S.T — *"Fast"* and *"Repeatable."* Sleep-based tests fail both. The correct discipline is condition-based waiting (poll a state observable until the operation completes, with a generous timeout that fails the test on real hangs). See also `obra/superpowers:condition-based-waiting` (Phase 2 of this toolkit ships `systematic-debugging` which links to the same pattern).

## 7. 100%-coverage-as-the-goal

*Looks like*: coverage report is the success metric. Trivial getters / setters get unit tests; one-line delegations get unit tests; critical business logic and edge cases are 60% covered.

*Fails*: coverage is a lagging indicator. Pursuing 100% on cheap surface area while leaving the critical path under-tested optimizes the wrong number. Worse, *"100% coverage"* often emerges from test generators that exercise lines without asserting anything meaningful.

*Rebuttal*: TDD discipline does *not* target a coverage number — it targets a *feedback loop*. Beck (2002) is pragmatic about what counts as needing a test; the Preface rule is the limit case for code on the critical path. House rule: critical path → TDD mandatory; glue → test-after acceptable; generated / trivial → tests optional. See [`../standards/tdd-standard.md`](../standards/tdd-standard.md) §"Critical-Path Coverage."

## 8. "User said skip TDD"

*Looks like*: the user types "skip TDD" or "just write the code" and the agent immediately complies.

*Fails*: half the time the user is invoking the legitimate §When NOT to Use exception (throwaway / generated / pure config). The other half they are venting frustration mid-task and will regret the missing tests an hour later when something breaks.

*Rebuttal*: see [`SKILL.md`](../SKILL.md) §When NOT to Use. The override is valid only if (a) the user is explicit AND (b) the work matches one of the enumerated exempt categories. If only (a) holds, quote §When NOT to Use back and ask for explicit confirmation. Refusing the override is not insubordination — it is honoring the contract the user installed this skill for.

## See also

- [`../SKILL.md`](../SKILL.md) — the Iron Law + Red-Green-Refactor cycle + §When NOT to Use + §False-green diagnostic.
- [`../standards/tdd-standard.md`](../standards/tdd-standard.md) — full canonical discipline (functional copy of `domain-teams:code-team` SSOT).
- *Beck, K. (2002) Test-Driven Development: By Example*, Addison-Wesley, ISBN 978-0321146533.
- *Martin, R.C. (2008) Clean Code*, Prentice Hall, ISBN 978-0132350884, Ch.9 "Unit Tests."
- 和田卓人 訳 (2017) 『テスト駆動開発』, オーム社, ISBN 978-4274217883.
