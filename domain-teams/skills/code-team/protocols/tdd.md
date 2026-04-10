# TDD Protocol

Write the test first. Watch it fail. Write minimal code to pass.

## Primary Sources

- **Beck, K. (2002)** *Test-Driven Development: By Example*,
  Addison-Wesley (Addison-Wesley Signature Series).
  ISBN 978-0321146533. **The canonical primary source for TDD
  and the Red/Green/Refactor cycle.** Chapters grounding this
  protocol: Ch.1 "Multi-Currency Money" (the 6-step cycle
  walkthrough), Part II "Test-Driven Development Patterns"
  including Ch.25 "Test-Driven Development Patterns", and the
  Preface for the "never write production code without a failing
  test" rule.
- **Martin, R.C. (2008)** *Clean Code: A Handbook of Agile
  Software Craftsmanship*, Prentice Hall. ISBN 978-0132350884.
  Ch.9 "Unit Tests" contains the "Three Laws of TDD" formulation
  and the F.I.R.S.T properties. Martin's Three Laws **restate and
  sharpen Beck's Preface rule** — Beck 2002 is the origin, Martin
  is the operationalized minute-by-minute discipline.
- **和田卓人 訳 (2017)** 『テスト駆動開発』, オーム社.
  ISBN 978-4274217883 — Kent Beck *Test-Driven Development: By
  Example* の正規日本語訳。日本の TDD コミュニティの事実上の
  primary。訳者 和田卓人 (t_wada) は日本の TDD 啓蒙活動の中心
  人物であり、JP コードベース review で「TDD」と言う時の多くは
  和田訳経由で Beck を読んでいる。
- Team standard: `standards/tdd-standard.md` is the authoritative
  code-team reference for TDD discipline, including critical-path
  coverage rules and the "Tests as Design Feedback" meta-lesson.

## Red-Green-Refactor Cycle

**Beck 2002 Ch.1** walks the 6-step cycle through the
multi-currency money example. code-team follows Beck's original
steps:

1. **RED**: Write one failing test for the next behavior
   (Beck 2002, Preface: *"never write production code without a
   failing unit test"*)
2. **Verify RED**: Run test — confirm it fails for the expected
   reason (missing feature, not typo). A test that never fails is
   not testing anything (Beck 2002 Ch.1: the "false green" trap).
3. **GREEN**: Write minimal code to make the test pass. Beck 2002
   Part II offers two patterns: **Fake It ('Til You Make It)** —
   return a literal to pass, then triangulate — and **Obvious
   Implementation** — when the correct code is trivial, just
   write it.
4. **Verify GREEN**: Run test — confirm it passes, no other
   tests broken.
5. **REFACTOR**: Clean up (remove duplication, improve names) —
   keep tests green. Beck 2002 treats this step as load-bearing;
   skipping it is not TDD, it is "tests first".
6. **Repeat**: Next failing test for next behavior.

## Rules

**Three Laws of TDD** — Clean Code Ch.9 "Unit Tests" (Martin
formulation, grounded in Beck 2002 Preface):

1. *"You may not write production code until you have written a
   failing unit test."*
2. *"You may not write more of a unit test than is sufficient to
   fail — and not compiling is failing."*
3. *"You may not write more production code than is sufficient to
   pass the currently failing test."*

Operational rules (code-team discipline, grounded in Beck 2002
and Clean Code Ch.9):

- No production code without a failing test first (Three Laws #1)
- One behavior per test, one cycle per behavior
- Test names describe the scenario, not the method
- Minimal code to pass — don't add features beyond the test
  (Three Laws #3)
- Real code preferred over mocks (mock only when unavoidable)
- If stuck: hard to test = hard to use → simplify the design
  (Beck 2002 Preface: *"If it's hard to test, it's probably hard
  to use"*)

## When to Skip (ask user first)

- Throwaway prototypes
- Generated / scaffolding code
- Configuration files
- User explicitly opts out

## Bug Fix with TDD

1. Write a failing test that reproduces the bug
2. Follow Red-Green-Refactor to fix
3. Test proves fix and prevents regression
