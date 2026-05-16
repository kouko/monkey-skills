<!--
FUNCTIONAL COPY — DO NOT EDIT IN PLACE
SSOT: domain-teams/skills/code-team/standards/tdd-standard.md
Sync via: code-toolkit/scripts/distribute.py
-->

# TDD Standard

Test-Driven Development as the default discipline for code-team: write
a failing test first, make it pass, then refactor. TDD は品質確保の
技法であると同時に、**設計の feedback loop** である — テストが書き
にくければ設計が悪い、というメッセージが核心。

## Primary Sources

- **Beck, K. (2002) *Test-Driven Development: By Example*, Addison-Wesley (Addison-Wesley Signature Series). ISBN 978-0321146533.** The canonical primary source for TDD and the Red/Green/Refactor cycle. Chapters cited: Ch.1 "Multi-Currency Money" (introductory walkthrough), Part II "Test-Driven Development Patterns" including Ch.25 "Test-Driven Development Patterns", Preface for the "never write production code without a failing test" rule.
- Martin, R.C. (2008) *Clean Code: A Handbook of Agile Software Craftsmanship*, Prentice Hall. ISBN 978-0132350884. Ch.9 "Unit Tests" — contains the "Three Laws of TDD" formulation and the F.I.R.S.T properties. Martin's Three Laws restate and sharpen Beck's Preface rule; Beck 2002 is the origin.
- 和田卓人 訳 (2017) 『テスト駆動開発』, オーム社. ISBN 978-4274217883 — Kent Beck *Test-Driven Development: By Example* の正規日本語訳。日本の TDD コミュニティの de facto primary。訳者 和田卓人 (t_wada) は JP の TDD 啓蒙活動の中心人物。
- Henney, K. (ed.) / 和田卓人 (監修) (2010) 『プログラマが知るべき 97 のこと』, オライリー・ジャパン. ISBN 978-4-87311-479-8. 和田卓人 執筆エッセイ「不具合にテストを書いて立ち向かう」— JP preamble echo.

## The Red-Green-Refactor Cycle

**Beck 2002, Ch.1 and Part II**: the canonical TDD cycle is three
strict steps.

### Red — write a failing test

Write the smallest test that expresses the next increment of
behavior you want. The test MUST fail when first run. If it passes
without any production code change, either the behavior already
exists (no new test needed) or the test is not actually testing
anything (false green).

Beck 2002 Part II pattern **Fake It ('Til You Make It)**: return a
literal value to make a test pass, then triangulate with a second
test that forces a real implementation.

### Green — make it pass

Write the simplest code that makes the failing test pass. "Simplest"
does not mean "sloppy" — it means *no speculative generality, no
premature abstraction*. Ugly duplication is acceptable at the Green
step; you will remove it in Refactor.

Beck 2002 Part II pattern **Obvious Implementation**: when you know
how to make the test pass with a trivial correct implementation,
just write it — don't force Fake It on every test.

### Refactor — improve the design

With all tests green, improve the internal structure without
changing behavior. The test suite is your safety net — if any test
goes red during refactor, revert and try a smaller step.

This step is load-bearing: skipping refactor accumulates technical
debt even when all tests pass. TDD without refactor is not TDD; it
is "tests first".

## The Three Laws of TDD

**Clean Code Ch.9 "Unit Tests"** — Martin's formulation (grounded in
Beck 2002's discipline):

1. *"You may not write production code until you have written a
   failing unit test."*
2. *"You may not write more of a unit test than is sufficient to
   fail — and not compiling is failing."*
3. *"You may not write more production code than is sufficient to
   pass the currently failing test."*

The three laws operationalize "write a failing test first" into a
minute-by-minute discipline. They rule out writing ten tests and
then one giant implementation, or writing one test and a
speculative implementation that covers five untested cases.

## F.I.R.S.T Test Properties

**Clean Code Ch.9 "Unit Tests", §"F.I.R.S.T"**: good unit tests are

- **F**ast — they run in milliseconds; slow tests get skipped
- **I**ndependent — tests do not depend on execution order or
  shared mutable state
- **R**epeatable — they produce the same result on any machine,
  any time
- **S**elf-Validating — the test has a boolean pass/fail output;
  no manual inspection
- **T**imely — tests are written just before the production code
  they test, not weeks later

## Tests as Design Feedback

**Beck 2002, Preface**:

> *"If it's hard to test, it's probably hard to use."*

This is the single most important meta-lesson of TDD: when a test
is painful to write, the pain is telling you the production design
is wrong. The correct response is **refactor the production code**,
not mock the pain away.

Typical "hard to test" signals and their usual root causes:

- Requires dozens of mocks → module has too many collaborators
  (SRP / DIP violation, see `solid-principles.md`)
- Requires elaborate setup → hidden dependencies (DIP violation)
- Requires `sleep()` to be reliable → race condition in production
- Requires reading private fields → the public interface is missing
  an observation point

## Critical-Path Coverage

TDD does not require 100% line coverage. code-team house rule:

- **Critical path** (business logic, input validation, security
  boundaries): TDD is mandatory. No production code without a
  failing test first.
- **Glue / framework integration**: test-after or integration test
  is acceptable if a fast unit test is impractical.
- **Generated code, trivial getters/setters, pure delegation**:
  tests are optional.

This is a house relaxation of the strict "100% TDD" stance. Beck
2002 itself is pragmatic about what "counts" as needing a test; the
Preface rule is the limit case, not the only case.

## Japanese Anchor

和田卓人 訳 2017 『テスト駆動開発』(オーム社) は Beck 2002 の日本語
正規訳であり、日本の TDD 実務の事実上の参照元。和田は TDD の中核
メッセージを「テストは仕様の具体化であり、設計の feedback loop で
ある」と定式化している (訳者解説 および 97 のこと 日本語版 エッセイ
「不具合にテストを書いて立ち向かう」)。

Worker や evaluator が日本語コードベースを扱う際は、和田訳 2017 を
JP 一次参照として扱うこと。日本人プログラマ向けの code review で
「TDD」と言う時、多くの現場は和田訳経由で Beck を読んでいる。

## Anti-Patterns

- ❌ **Writing tests after implementation is complete** — this is
  not TDD, it is "tests last". The feedback loop is lost.
- ❌ **Mocking everything** to avoid refactoring a painful design
  (Beck 2002: the pain is the message; listen to it)
- ❌ **One giant test** covering multiple behaviors (violates
  F.I.R.S.T "Independent")
- ❌ **Tests that always pass on first run** — if Red never happens,
  the test is not actually testing the change (Three Laws
  violation)
- ❌ **Skipping the Refactor step** — tests-first without refactor
  accumulates debt
- ❌ **100% coverage as the goal** — coverage is a lagging
  indicator; use it to find gaps, not as a target
- ❌ **Sleep-based tests** — `Thread.sleep(500)` to wait for async
  work; the test is hiding a race condition in production
