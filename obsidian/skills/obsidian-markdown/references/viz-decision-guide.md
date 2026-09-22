# Visualization Decision Guide

> **Scope.** This guide decides one thing: which **presentation form** a piece of content gets — diagram, table, callout, list, or prose. It is advice, not a gate: when the user asks for a specific form, use that form.
>
> It does **not** decide, and must not restate:
> - whether to draw a diagram inline or delegate it, or which diagram type to use → [SKILL.md §Diagrams](../SKILL.md#diagrams-mermaid)
> - which callout type to use → [SKILL.md §Callouts](../SKILL.md#callouts)
> - list and table syntax — standard Markdown

## Pick the form

Ask these questions in order and take the first "yes".

1. **Diagram** — Does the content have steps, branches, states, dependencies, numeric trends or proportions, or positions on two axes — structure the reader would otherwise have to rebuild in their head? Then continue at [SKILL.md §Diagrams](../SKILL.md#diagrams-mermaid).
2. **Table** — Are there several items that share the same attributes, and will the reader compare them attribute by attribute?
3. **Callout** — Is it one short statement the reader must not miss (a summary, a caveat, a tip, an open question)? Pick the type per [SKILL.md §Callouts](../SKILL.md#callouts).
4. **List** — Is it a set of parallel points, or points nested under parent points, with no shared attributes to compare? Nest the list to show hierarchy.
5. **Prose** — None of the above: write paragraphs under headings.

## Tie-breakers

- **Diagram or table**: if the reader needs exact values or a cell-by-cell comparison, use a table; if the reader needs the shape (order, structure, trend), use a diagram. Add the second form only when it shows something the first does not.
- **Nested list or diagram**: a pure parent–child hierarchy read top-down is a nested list; use a diagram only when links across branches matter.
- **Callout or heading**: a callout marks an exception to the surrounding text. If most sections would open with a callout, they are not exceptions — use headings and plain paragraphs instead.

## Domain layouts

- Scenario × lever tables: follow the layout defined by the `systems-thinking-toolkit:strategy-lever-and-cascade` skill when it is available.
