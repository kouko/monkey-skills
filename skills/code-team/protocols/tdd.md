# TDD Protocol

Write the test first. Watch it fail. Write minimal code to pass.

## Red-Green-Refactor Cycle

1. **RED**: Write one failing test for the next behavior
2. **Verify RED**: Run test — confirm it fails for the expected reason (missing feature, not typo)
3. **GREEN**: Write minimal code to make the test pass
4. **Verify GREEN**: Run test — confirm it passes, no other tests broken
5. **REFACTOR**: Clean up (remove duplication, improve names) — keep tests green
6. **Repeat**: Next failing test for next behavior

## Rules

- No production code without a failing test first
- One behavior per test, one cycle per behavior
- Test names describe the scenario, not the method
- Minimal code to pass — don't add features beyond the test
- Real code preferred over mocks (mock only when unavoidable)
- If stuck: hard to test = hard to use → simplify the design

## When to Skip (ask user first)

- Throwaway prototypes
- Generated / scaffolding code
- Configuration files
- User explicitly opts out

## Bug Fix with TDD

1. Write a failing test that reproduces the bug
2. Follow Red-Green-Refactor to fix
3. Test proves fix and prevents regression
