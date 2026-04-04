# Documentation Writing Rubric

## Protocol

1. **Discover patterns**: Find existing doc style in the project —
   README structure, JSDoc/docstring style, doc directory layout
2. **Read source**: Understand the code and any existing docs
3. **Generate/update**: Follow discovered conventions exactly
4. **Cross-reference**: Ensure consistency with related docs

## Rules

- Language: Follow project convention. English for code docs.
  Non-code content uses the `output_language` from the launch prompt
- Never remove existing doc content without explicit instruction
- Keep docs DRY — link to source of truth rather than duplicating
- Include examples for non-obvious APIs
- Structure: What it does → How to use → API reference → Examples

## Output Format

1. List of files created/updated
2. Summary of changes made
