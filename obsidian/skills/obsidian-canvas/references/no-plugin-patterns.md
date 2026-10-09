# No-Plugin Advanced Canvas Patterns

Advanced application patterns for the Obsidian Canvas Creator skill, built on
Obsidian core features only — no community plugins. Where
`references/layout-patterns.md` documents four single-canvas visual layouts
(kanban, dashboard / home page, research map, moodboard), this file documents
multi-canvas and embedded-file workflows: nesting a canvas inside a canvas,
splitting a project across two canvases, documenting a data pipeline, using a
canvas as a finished artifact, running a class, building a world, embedding a
Bases view, and indexing a vault as a 2D MOC (canvas-only vault).

The mechanism behind every pattern is the JSON Canvas `file` node. Its `file`
field takes a vault path, and Obsidian renders that file in place — not only
notes and images but also `.canvas` files and `.base` files. An optional
`subpath` (`#Heading`) narrows a note embed to one section.

All rules from `references/canvas-spec.md` still apply: 16-character
lowercase-hex IDs unique across nodes and edges, integer coordinates, groups
listed first in the `nodes` array, and every edge referencing existing nodes.
Canvas JSON has no comments, so any guidance you want to keep in the file
belongs in node text.

Zero-plugin rule: every technique below works in a stock Obsidian install.
Where a feature is version-bound it is called out explicitly; the only such
case here is Bases, which **requires Obsidian 1.9+ (Bases core plugin)**.

## 1. Nested Canvas Workspace (Canvas-in-Canvas)

A file node whose `file` field points at a `.canvas` path embeds a child
canvas inside the parent. Obsidian renders the child's contents in the parent
and opens it as its own tab on double-click; the child remains a normal vault
file that you edit separately. This is the core nesting feature — no plugin
required.

### Parent / child layering

- The **parent** canvas holds orientation: the title, the legend, the
  navigation text, and the file nodes that embed each child. Keep it to
  navigation and overview nodes.
- A **child** canvas holds one self-contained topic each — a sub-project, a
  research theme, a meeting series. Everything in it is editable without
  touching the parent.
- The parent links to the embedding file node with an edge labeled
  `opens in its own tab` (or similar) so the hierarchy is legible; the child
  file itself need not know its parent.

### When to split a canvas into a hierarchy

- The canvas has grown past one screenful and its groups no longer fit
  together.
- Two or more sections are worked on at different times.
- A section has its own legend or color language that would clash with the
  parent's.
- Panning and zooming feel slow — large canvases degrade, and splitting
  restores responsiveness (see section 9 for the maintenance caveat).

### Example: a parent embedding a child canvas

```json
{
  "nodes": [
    { "id": "a1b2c3d4e5f60001", "type": "text", "x": 0, "y": 0, "width": 580, "height": 120, "text": "# Parent Workspace Canvas", "color": "4" },
    { "id": "a1b2c3d4e5f60005", "type": "file", "x": 0, "y": 200, "width": 760, "height": 560, "file": "Child/child-canvas.canvas", "color": "6" }
  ],
  "edges": []
}
```

Point `file` at the child's real vault path. The validator checks canvas
structure, not whether the referenced file exists, so keep the paths honest
yourself. Start from `assets/template-nested-workspace.canvas` — a parent
canvas with an embedded child canvas node, a linked note, and in-file
guidance for replacing the paths. To nest one level deeper, duplicate the
child canvas file and point the node at the copy.

## 2. Research Dual-Canvas

For a large, non-linear project — a thesis, a long investigation — a single
canvas conflates two jobs: deciding what to do next and showing what has been
produced. The Effortless Academic workflow splits them into two canvases.

- **Research canvas** — the working surface: open questions, next steps, open
  tasks, unresolved branches, candidate directions. It is allowed to be messy
  and changes often.
- **Results canvas** — the overview: one node per week or per milestone with
  the outcome, plus charts and figures that scripts generate and save into
  the vault as images. It is read, not edited, most of the time.

### How they link

- Each canvas embeds the other as a file node — the research canvas carries a
  file node to the results canvas and vice versa — so one hop moves between
  planning and outcomes.
- An open question on the research canvas becomes a results node once it
  resolves; connect the question to the results file node with a labeled
  `resolved by` edge.
- A to-do list cannot express non-linear research, so the research canvas
  positions questions spatially (nearby, linked) instead of ordering them.
- Charts stay out of the canvas JSON: a script writes `Results/week-12.png`
  and the results canvas embeds it with a file node, so regenerating the data
  updates the canvas without editing JSON.

Keep both canvases in one folder (`Research/`) so relative paths and search
stay simple.

## 3. Data-Pipeline Documentation Canvas

An ecology lab documents a data pipeline as a canvas, using color as a visual
language and file nodes for the moving parts.

### Color per stage

The lab assigns one preset color per element type and states the mapping in a
legend node:

- `"5"` cyan — raw inputs: CSV files, exports, dumps (file nodes).
- `"4"` green — scripts and transforms that produce the next stage.
- `"2"` orange — parameters, settings, and environment assumptions.
- `"3"` yellow — questions, caveats, and known gaps.

Keep the legend as a text node in a corner; it is the contract that makes the
colors readable.

### Layout

- Arrange stages left to right in pipeline order, each stage a group labeled
  with the step name; connect stages with labeled directional edges
  (`parse`, `join`, `fit`).
- Embed annotated screenshots as file nodes beside the script that produces
  them, so the pipeline reads without running the code.
- When a dataset is replaced, do not delete the old stage: move the superseded
  nodes to the canvas edge, under a `Deprecated` group with a dated note. The
  pipeline's history stays visible while the current path stays central.

This documents a fixed pipeline, not a monitor — see section 9 before turning
it into something that must stay current.

## 4. Output-as-Deliverable Method Canvases

Some canvases are the deliverable: you finish them, hand them over, and stop
editing. An independent consultant reports three that work as methods and two
that do not.

### Works: the canvas is the final artifact

- **System audit** — current architecture, dependencies, risks, and
  recommendations laid out spatially, delivered as a `.canvas` file.
- **Incident post-mortem** — a timeline along one axis, contributing factors
  grouped, root cause and follow-ups as linked nodes. The canvas is the
  report.
- **Onboarding map** — accounts, tools, people, and first-week tasks with file
  nodes into the real process notes; a new hire navigates it once.

For these, use file nodes to point at the authoritative notes and let the
canvas be the index, so the artifact stays small and the content stays
maintainable.

### Does not work as a maintained board

- A **project kickoff** canvas and a **content-ideation** canvas both failed
  as living documents: they needed updating faster than they were used.
- **Do not** keep any deliverable canvas as a continuously maintained
  dashboard. The drift trap (section 9) is exactly this mistake: an artifact
  canvas is allowed to freeze at delivery; a dashboard is not.

## 5. Teacher Class Canvas

A teacher opens one canvas per class and reuses it every session, which keeps
the whole class's context in one spatial place.

- Embed seating charts and class photos as file nodes (images), one per class
  or per arrangement.
- Keep a per-day log as text nodes or a small table group, newest at the top,
  so the term reads as a column of dated entries.
- Link the class's LMS pages (Moodle, Nextcloud, and similar) as link nodes,
  and the grade file and worksheets as file nodes; the canvas becomes the
  launch pad for the lesson.
- Save each class's own arrangement — one canvas per class, no shared board —
  so opening a class file restores that class's layout.

Because a canvas reopens where you left it, the per-class canvas doubles as
the lesson's bookmark wall. Move stale entries into a dated group rather than
deleting them.

## 6. Worldbuilding Basics

Writers and TTRPG game masters place world elements spatially so relations are
visible at a glance.

- **Character relations** — one text or file node per character, positioned
  close when they are allied and far when opposed; label edges with the
  relation (`mentor of`, `rival of`, `married to`) rather than drawing a
  complete graph.
- **Setting boards** — group locations, factions, and events by region or era;
  a timeline axis (x = time) is a common spine for events.
- **Visual material** — for reference imagery, use the moodboard pattern in
  `references/layout-patterns.md` rather than inventing a new layout: the same
  file-node imagery, theme groups, and no edges.

Keep character nodes short; put biography in the linked note and let the
canvas carry only the relation.

## 7. Bases-in-Canvas

> **requires Obsidian 1.9+ (Bases core plugin).**

Bases is a core plugin (shipped in Obsidian 1.9) that renders a note database
as a view — a table, a list, or a card layout. A canvas can embed a `.base`
file with a file node exactly as it embeds a note. Direct `.base` embeds in a
canvas card work from Obsidian 1.9 (Bases' release); 1.9.5 fixed an edge case
where an embedded base inside a moved canvas card failed to refresh. If a base
view does not render inside a canvas card, embed the base in a note first and
embed that note in the canvas (still core-only).

```json
{
  "nodes": [
    { "id": "b1c2d3e4f5060708", "type": "file", "x": 0, "y": 0, "width": 640, "height": 420, "file": "Views/projects.base" }
  ],
  "edges": []
}
```

### What Bases views give you spatially

- A live, query-backed view sits on the canvas: filtering, sorting, and
  grouping happen in Bases, while the canvas supplies the surrounding
  context — headings, annotations, and links to the notes behind the rows.
- Place several `.base` embeds side by side to compare views of one dataset
  (for example, "active" and "archived") in a single glance.
- Edges and annotations connect the view to related canvases or notes, which
  a plain Bases view cannot express.

The canvas is a spatial composition around the view; the data itself keeps
living in the notes and the `.base` query. Update the `.base` file, not the
canvas JSON, when the query changes. This is the "database view × spatial
document" workflow — useful for a working overview, never a substitute for the
query. The spatial composition around a view is still hand-maintained —
positions and annotations do not refresh — so treat it as a working overview,
not a live dashboard (see section 9).

## 8. Canvas-Only Vault / 2D MOC

Treat the vault's index as a 2D map: a canvas whose file nodes are MOCs and
hub notes, laid out spatially, replacing or supplementing a text MOC. The map
of contents becomes a place you navigate by position, grouping, and labeled
relations instead of by reading a list.

### How (core only)

- File nodes reference the MOC and hub notes; each stays a normal vault note.
- Groups mark the map's sections; edges carry the explicit relations between
  hubs (`feeds`, `part of`, `overlaps`).
- Embed a child canvas for a sub-map: a file node pointing at another
  `.canvas` file (see section 1), so one region of the index can grow its own
  canvas.

### Limits — stated plainly

- A canvas-only vault is an index — a finished artifact, not a self-updating
  map. Nothing in it refreshes itself.
- A canvas full of typed text cards stays out of backlinks and the graph —
  links only ever originate from file nodes — so the file nodes are the part
  that stays wired to the vault. (Text-card content is searchable, but a typed
  card is not a note.)
- Keep it small and about a structure that has stabilized, and re-derive the
  layout when the vault's structure changes.

### When it works, when it fails

It works for personal navigation over a slow-changing structure, or for
presenting a vault. It fails the moment the map is expected to stay
automatically current — that is canvas drift (see section 9).

## 9. When NOT to Use Canvas (Canvas Drift)

The most common canvas failure is **canvas drift**: a canvas kept as a
continuously maintained live dashboard. A consultant who ran a canvas as a
live dashboard reports it failed within about two weeks — the cards drifted
out of date faster than they were updated, and stale spatial information
turned out to be worse than no information at all.

Spatial documents do not refresh themselves. A note can be transcluded, a
query re-run, a Bases view re-rendered; a canvas node is a snapshot typed by
hand. Anything that changes on its own schedule will outpace the canvas.

**Never keep hand-maintained status content as a live dashboard on a canvas.**
Anything typed by hand on the canvas — status cards, checklists, summaries —
is a snapshot and will drift if it must stay current. For live data, embed a
Bases view or transclude a note instead: Bases views and file-node embeds
refresh from their source, and a note's links and backlinks stay truthful.
What refreshes is the embedded content; what does not is the spatial
composition around it — positions, grouping, and annotations are still
maintained by hand. Use canvas for the two jobs it does well:

- **Spatial reasoning** — thinking that benefits from position, grouping, and
  labeled relations while it is in flux (brainstorming, mapping, planning).
- **Finished artifacts** — delivered once and then frozen (section 4: audit,
  post-mortem, onboarding map).

A diagnosis to act on: if a canvas must be correct every time it is opened, it
is a dashboard, and it will drift. Move the changing part into notes and
Bases, and let the canvas hold only what has stabilized. Note also that a text
card is not a note — it does not appear in backlinks — so a canvas full of
typed text drifts out of the vault's link graph as well as out of date.
