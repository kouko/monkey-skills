# Refactoring Rubric

## Protocol

1. **Receive instruction**: Get explicit refactoring task
   (what to change, not why)
2. **Analyze scope**: Which files, which symbols, what references
3. **Execute transformation**: Make the changes
4. **Verify**: Run existing tests, check for broken references
5. **Report**: List all files changed, what was done

## Rules

- NEVER change behavior — refactoring is structure-only
- NEVER make additional "while I'm here" changes
- If a transformation would require a design decision, STOP and
  report what decision is needed
- Always verify tests still pass after refactoring
- Preserve all existing formatting conventions

## Output Format

1. List of files modified
2. Transformation applied (what changed structurally)
3. Test results (pass/fail)
4. Broken references found (if any)
