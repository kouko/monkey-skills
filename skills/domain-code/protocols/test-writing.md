# Test Writing Rubric

## Protocol

1. **Discover conventions**: Find existing tests in the project —
   framework, file naming, directory structure, assertion style
2. **Read source**: Understand the module under test thoroughly
3. **Identify cases**: Happy path, edge cases, error cases,
   boundary conditions
4. **Generate tests**: Follow discovered conventions exactly
5. **Verify**: Run tests to confirm they pass on current code

## Rules

- Never mock what you can use directly
- Each test should test ONE behavior (not one function)
- Test names should describe the scenario, not the method name
- If no existing test conventions found, use sensible defaults:
  Jest for TypeScript/JavaScript, pytest for Python
- Tests MUST pass on the current code — you are testing existing
  behavior, not writing aspirational tests

## Output Format

1. File path(s) of generated test files
2. Summary: what behaviors were tested
3. Untestable areas flagged (if any)
4. Test run results
