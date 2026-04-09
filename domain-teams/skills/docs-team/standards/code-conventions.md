# Code Conventions (Shared Standard)

This file is the single source of truth for coding standards.
Both worker (when writing) and evaluator (when reviewing) reference this file.

## Naming

- Follow existing project conventions (discover before creating new patterns)
- Variable and function names must be semantically meaningful
- Constants: UPPER_SNAKE_CASE
- Respect language idioms (camelCase for JS/TS, snake_case for Python/Rust)

## Language

- Code documentation: English (unless project convention differs)
- Non-code content (vault notes, reports): Use the `output_language` from the launch prompt

## Comments

Code comments are a last resort. First try: rename, extract function, replace magic numbers
with constants. Refactor unclear code rather than explaining it with comments.
Only write what code alone cannot express.

### What to write

- **Docstring (功能)**: one-line summary of calling contract — write for the caller,
  not the implementer. Omit if the function name already says it all.
- **Intent (意圖)**: why this code exists in the system — what calls it,
  what problem it solves, what breaks if removed
- **Why (理由)**: why this approach was chosen when alternatives exist
- **Why Not (却下理由)**: why the obvious/simpler approach was intentionally rejected —
  prevents future "improvements" that reintroduce known issues

### What NOT to write

- What the code does line-by-line — the code already says this
- Block-end markers (`// end if`, `// end for`) — the IDE shows structure
- Revision history — git manages this
- Commented-out code — delete it; git preserves history

### Staleness rule

A stale comment is worse than no comment.
When changing code, update or delete adjacent comments. Treat outdated comments
as tech debt equivalent to dead code.

## KISS (Keep It Simple, Stupid)

- Keep functions focused; prefer explicit over clever

## YAGNI (You Ain't Gonna Need It)

- Do not create abstractions for one-time operations
- Do not add error handling for scenarios that cannot happen
- Do not design for hypothetical future requirements

## DRY (Don't Repeat Yourself)

- Link to source of truth rather than duplicating
- Three similar lines are better than a premature abstraction
- Extract only when the pattern repeats 3+ times with identical structure

## Dependencies

- Follow existing dependency patterns in the project
- Do not introduce new dependencies without explicit justification
- Prefer standard library over third-party when capability is equivalent
