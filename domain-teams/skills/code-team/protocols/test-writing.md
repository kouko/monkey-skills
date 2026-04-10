# Test Writing Protocol

For test-first (TDD) workflow, use `tdd.md` instead.
This protocol is for adding tests to existing code without TDD.

## Primary Sources

- **Meszaros, G. (2007)** *xUnit Test Patterns: Refactoring Test
  Code*, Addison-Wesley (Addison-Wesley Signature Series).
  ISBN 978-0131495050. **Canonical source for the Test Double
  taxonomy** (Dummy / Stub / Spy / Mock / Fake) and for the
  discipline of refactoring test code as first-class code. The
  "never mock what you can use directly" rule below descends from
  Meszaros's taxonomy.
- **Fowler, M.** bliki "Mocks Aren't Stubs" (2007) —
  https://martinfowler.com/articles/mocksArentStubs.html —
  authoritative distinction between mock objects (behavior
  verification) and stubs (state verification). Fowler credits
  Meszaros's vocabulary and contrasts "classical" vs "mockist"
  TDD schools. Load-bearing for understanding when a mock
  genuinely adds signal vs when it hides a design problem.
- **Martin, R.C. (2008)** *Clean Code*, Prentice Hall.
  ISBN 978-0132350884. Ch.9 "Unit Tests" — the **F.I.R.S.T**
  properties (Fast, Independent, Repeatable, Self-Validating,
  Timely) are the acceptance criteria for every test written
  under this protocol.
- Team standard: `standards/tdd-standard.md` §"F.I.R.S.T Test
  Properties" and §"Tests as Design Feedback" are the
  authoritative code-team references for test quality.

## Protocol

1. **Discover conventions**: Find existing tests in the project —
   framework, file naming, directory structure, assertion style
2. **Read source**: Understand the module under test thoroughly
3. **Identify cases**: Happy path, edge cases, error cases,
   boundary conditions
4. **Generate tests**: Follow discovered conventions exactly
5. **Verify**: Run tests to confirm they pass on current code

## Rules

- **Never mock what you can use directly** — grounded in Fowler
  bliki "Mocks Aren't Stubs" (the classical vs mockist divide)
  and Beck 2002's test-as-design-feedback principle via
  `standards/tdd-standard.md` §"Tests as Design Feedback". A
  mock that replaces a pure function or a cheap value object is
  usually hiding a design problem.
- Each test should test ONE behavior (not one function) —
  F.I.R.S.T "Independent" (Clean Code Ch.9)
- Test names should describe the scenario, not the method name
- If no existing test conventions found, use sensible defaults
  (**house convention**, not a primary-source requirement):
  Jest for TypeScript/JavaScript, pytest for Python. These are
  ecosystem defaults at 2026-04; revisit if the host project has
  a different maintained convention.
- Tests MUST pass on the current code — you are testing existing
  behavior, not writing aspirational tests

## Output Format

1. File path(s) of generated test files
2. Summary: what behaviors were tested
3. Untestable areas flagged (if any)
4. Test run results
