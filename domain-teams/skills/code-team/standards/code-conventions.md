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

## Style

- Do not add comments/docstrings to code you did not change
- Only add comments where logic is not self-evident
- Do not add error handling for scenarios that cannot happen
- Do not create abstractions for one-time operations
- Keep functions focused; prefer explicit over clever

## DRY

- Link to source of truth rather than duplicating
- Three similar lines are better than a premature abstraction
- Extract only when the pattern repeats 3+ times with identical structure

## Dependencies

- Follow existing dependency patterns in the project
- Do not introduce new dependencies without explicit justification
- Prefer standard library over third-party when capability is equivalent
