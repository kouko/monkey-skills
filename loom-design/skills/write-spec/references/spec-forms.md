# Spec forms — when prose is not the right shape

Prose is the default. Reach for one of these when the content has a shape
prose has to spell out row by row; a form that carries one item is padding.

## Requirement identifiers

The grammar itself is declared once, in `loom-code`'s contract manifest
(`artifacts.spec.fields`, the `Requirements` entry). What that grammar
does not say, and what holds anyway:

- **Authored, never derived.** You type the number. It is never slugified
  or hashed from the name — a derived id desyncs from its requirement the
  moment the name is reworded.
- **Monotonic, never renumbered, never reused.** A new requirement takes
  the next unused number across this change's spec; inserting one above
  `REQ-3` does not renumber `REQ-3`. A deleted requirement's number is
  retired, so a stale citation fails loudly instead of silently pointing
  at something narrower.
- **Split and merge retire both sides.** One requirement split in two:
  the original number retires and both halves take new numbers. Two
  merged into one: both retire, the result takes a new number.
- **Near-misses are not the form.** `REQ1` (no hyphen), `req-1` (wrong
  case) and `R-1` (wrong prefix) are flagged, never silently accepted.

Each requirement ends by naming the intent Acceptance line it serves.
One-to-one is the default: do not fold two Acceptance lines into one
requirement, because the blind run walks the Acceptance list and has to
find each line answered somewhere.

## Table

Use a table when every row answers the same set of questions — the
columns are the questions. Two rows are enough if the comparison is the
point.

- **Options compared on shared axes** — one row per option, one column
  per axis (cost, coverage, what swapping it out later costs). This is
  the shape a one-way door is measured in before it is asked.
- **Joint states of co-active objects** — one row per combination,
  columns `Surface | Objects | Joint state | Reaction`. Only when a
  pair's joint reaction differs from the union of the individual ones;
  otherwise the enumeration manufactures volume.
- **Requirement → Acceptance coverage** — when there are more than about
  six requirements and the mapping is no longer readable inline.

Never pad a table to look substantial. When a section's table would be
empty, write one line — `N/A — <one-line reason>` — and the reason has to
fit the content.

## State list

Use a plain list, not a diagram, when one object moves through states in
one direction and nothing branches: `empty → loading → error | success`.
Per surface, name the variants that exist — for a screen, empty, loading,
error and populated; for a command, no-results output, progress, non-zero
exit text, success stdout. A specification that names only the happy,
populated state is incomplete, whatever else it covers.

## Diagram

Use a diagram when the content is a graph and the reader has to trace
paths through it — several states with transitions in both directions,
navigation between three or more surfaces, or a data flow that forks.

- **Mermaid** for state machines (`stateDiagram-v2`), relations
  (`erDiagram`) and navigation (`flowchart`). One diagram per object or
  per flow; a diagram carrying every object at once is read by nobody.
- **ASCII** for spatial layout — screen wireframes, pane splits, the
  column layout of command output. Mermaid has no native wireframe form
  (mermaid issue #1184), which is why layout stays ASCII.

Keep it narrow enough to survive a side pane, and when labels are CJK,
generate the box widths rather than eyeballing them.

## Completeness pass before hand-off

Ten questions, grounded in Nielsen's usability heuristics, that the review
station's design-conformance lens will ask. Answer them yourself first;
each unanswered one is a finding you could have closed for free.

1. Does every surface name its empty, loading, error and success variants?
2. Does every state have a path forward, back, or out?
3. Does every destructive action have confirmation or an undo?
4. Is every surface reachable — no orphan screen, no missing entry point?
5. Are cold start, resume and deep entry each accounted for?
6. Is there a designed error state, and a recovery path out of it?
7. Does the narrow case still work — narrow terminal, piped output, small
   screen — and are accessibility needs named?
8. Which objects and actors are named nowhere in the requirements?
9. Which non-functional bound (speed, size, privacy, offline) is assumed
   but unwritten?
10. Which requirement has no Acceptance line, and which Acceptance line
    has no requirement?

Where `PRINCIPLES.md` exists, add one: which surface does a
non-negotiable entail that the spec omits? Without that file, say
`principles lens: N/A — no PRINCIPLES.md` and invent nothing.
