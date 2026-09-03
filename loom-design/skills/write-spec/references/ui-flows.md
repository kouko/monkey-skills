# UI flows — the grammar of the `## UI flows` section

This section is one of the two the user reads back at decision point ②,
so it is written in their words: what they do, and what they then see.
Mechanism names, module names and file paths do not appear here.

## The line

One line per operation:

```
<what the user does> → <what they see or what changes>
```

- **GUI** — `taps Add on the list screen → the create sheet opens, title
  focused`.
- **TUI** — `presses Tab in the tree pane → focus moves to the content
  pane, the status bar names the new binding`.
- **CLI** — `todo add "pay rent" --due 2026-09-10 → prints "added #4, due
  Sep 10" and exit 0`.

For a command, the reaction is its output text and its exit code; for a
screen, the region that changed. "It works" and "the item is saved" are
not reactions — the user cannot check either one by looking.

## What every surface owes

Group the lines by surface, and give each surface all four variants that
apply. Missing variants are where specs fail, not the happy path:

- **Empty** — nothing to show yet. `todo list` with no todos → what does
  it print, and does it say how to add one?
- **In progress** — anything the user waits for. Spinner, progress line,
  or a statement that it is instant.
- **Error** — one line per way it can fail, each with the exact message
  and, for a command, the exit code. Every error line names the way out:
  what the user does next to recover.
- **Success** — the populated, ordinary case.

## Paths, not just screens

After the per-surface lines, walk the graph once: for every legal move
between surfaces — forward, back, skip, abandon, resume, escape from an
error, retry in place — say where the user lands, what is preserved, and
what is revalidated. One pass over each edge is enough; edge pairs are
not this section's job.

A surface no line arrives at is orphaned, and a state no line leaves is a
dead end. Both are findings before the review station raises them.

## Irreversible steps get a sentence of their own

Where a flow rewrites, deletes or sends the user's existing data, the
line says so and names the safeguard: `todo migrate → rewrites
todos.json into the new format; the old program cannot read it; a copy
is kept at todos.json.bak`. That sentence is what decision point ② asks
about — it is asked even when there is no alternative design.

## When there is no interface

Write exactly `N/A — <one-line reason>`. An internal refactor with no
surface the user reads or types into has no UI flows, and inventing some
to fill the section makes the spec longer and less true.

## Layout, when the shape matters

A wireframe is worth its lines when position carries meaning — which
region is where, what the columns of a listing are, how a pane splits.
Draw it in ASCII: mermaid has no native wireframe form (mermaid issue
#1184). Keep it narrow, and keep it to the surfaces this change touches.

## Reading it back

At decision point ② these lines become one plain sentence per operation:
「你下 ___ 會看到 ___；___ 的情況會 ___。對嗎？」 — "you type ___ and you
see ___; when ___ happens it will ___. Is that right?" If a line cannot
be said that way without naming a mechanism, the line is written from the
inside out and needs rewriting before it is shown.
