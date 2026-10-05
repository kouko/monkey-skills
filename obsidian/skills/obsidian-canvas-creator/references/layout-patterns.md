# Layout Patterns for Obsidian Canvas

Community layout patterns for the Obsidian Canvas Creator skill. Each pattern
documents its node composition, grouping, connections, and color semantics,
and ships with a small valid template under `assets/`. These four patterns
complement the existing MindMap (radial hierarchy) and freeform (custom zones)
layouts; use them when the user asks for a kanban, a dashboard or home page, a
research map, or a moodboard.

All rules from `references/canvas-spec.md` still apply: 16-character
lowercase-hex IDs unique across nodes and edges, integer coordinates, groups
listed first in the `nodes` array, and every edge referencing existing nodes.

## Pattern Selection

| Pattern | Best for | When to choose it |
|---|---|---|
| Kanban | Task and project tracking | Content has workflow states (to do, in progress, done) |
| Dashboard / Home Page | Vault navigation and bookmark wall | User wants a pinned starting point with sections and links |
| Research Map | Literature and research projects | User is mapping papers, themes, and their relationships |
| Moodboard | Visual collection and collage | User wants images arranged by theme, not a graph |

## 1. Kanban

### Node Composition

- One group per workflow column: To Do, In Progress, Done (add Blocked only
  when the workflow needs it).
- One text node per task card, kept short (a title and at most one detail
  line). Use a sentence, not a paragraph.
- A file node when a card is backed by a real vault note.
- Keep columns to three to five and cards to eight or fewer per column so the
  board stays scannable.

### Grouping

- Columns are group nodes, labeled with the column name.
- Every card sits fully inside its column group; do not leave cards between
  columns.
- Place columns left to right in workflow order with a 40px gap. Give each
  column the full board height so later cards only grow downward.
- List the column groups first in the `nodes` array so they render behind the
  cards.

### Connections

- Kanban uses few or no edges. Add one labeled edge only for a dependency:
  from the blocked card to its blocker, labeled `blocked by`.
- Do not connect every card to every other card; the column already carries
  the state.

### Color Semantics

- Group color encodes the column state:
  - `"6"` purple: To Do (planned, not started)
  - `"2"` orange: In Progress (active work)
  - `"4"` green: Done (completed)
  - `"1"` red: Blocked (needs attention)
- Card color encodes urgency: `"1"` red for an urgent or blocked card, no color
  for a normal card.
- Edge color `"1"` red marks a blocking dependency.

### Example

```json
{
  "nodes": [
    { "id": "1a2b3c4d5e6f7081", "type": "group", "x": 0, "y": 0, "width": 300, "height": 400, "label": "To Do", "color": "6" },
    { "id": "2b3c4d5e6f708192", "type": "group", "x": 340, "y": 0, "width": 300, "height": 400, "label": "In Progress", "color": "2" },
    { "id": "3c4d5e6f708192a3", "type": "text", "x": 20, "y": 40, "width": 260, "height": 90, "text": "Task 1" },
    { "id": "4d5e6f708192a3b4", "type": "text", "x": 360, "y": 40, "width": 260, "height": 90, "text": "Task 2", "color": "1" }
  ],
  "edges": [
    { "id": "5e6f708192a3b4c5", "fromNode": "4d5e6f708192a3b4", "fromSide": "left", "toNode": "3c4d5e6f708192a3", "toSide": "right", "label": "blocked by", "color": "1" }
  ]
}
```

Full template: `assets/template-kanban.canvas`.

## 2. Dashboard / Home Page

### Node Composition

- One title node (large text, short heading) at the top.
- Sections as groups: Quick Capture, Active Projects, Bookmarks, Recent Notes.
- File nodes for vault notes (projects, recent notes); link nodes for external
  bookmarks; text nodes only for capture prompts and the title.
- Keep the dashboard to two to four sections; it is a bookmark wall, not a
  board.

### Grouping

- Each section is a group node with a descriptive label.
- A node belongs to exactly one section; do not fill the gaps between groups.
- Arrange sections in a grid below the title with a 40px gap. A three-section
  row at x = 0, 500, 1000 with the title centered above the middle section is
  a reliable default.
- List the title and groups first, then the section nodes.

### Connections

- A dashboard normally has no edges. The layout, not lines, carries the
  meaning.
- If an edge is needed, use at most one: from the title to the current focus
  node. Never connect the title to every section.

### Color Semantics

- Node color encodes attention level:
  - `"2"` orange: act today
  - `"3"` yellow: notes or waiting
  - `"4"` green: on track
  - `"5"` cyan: reference and reading material
  - `"6"` purple: title and brand accents
- Group color tints a whole section; keep one hue per section and leave
  neutral sections uncolored.

### Example

```json
{
  "nodes": [
    { "id": "6f708192a3b4c5d6", "type": "text", "x": 0, "y": 0, "width": 460, "height": 80, "text": "# Home", "color": "6" },
    { "id": "708192a3b4c5d6e7", "type": "group", "x": 0, "y": 120, "width": 460, "height": 320, "label": "Quick Capture", "color": "3" },
    { "id": "8192a3b4c5d6e7f8", "type": "text", "x": 20, "y": 160, "width": 420, "height": 70, "text": "Capture idea", "color": "3" },
    { "id": "92a3b4c5d6e7f809", "type": "text", "x": 20, "y": 250, "width": 420, "height": 70, "text": "Morning reflection", "color": "3" }
  ],
  "edges": []
}
```

Full template: `assets/template-dashboard.canvas`.

## 3. Research Map

### Node Composition

- One root text node holding the research question.
- Papers as file nodes, with `subpath` pointing at the relevant heading when it
  helps. Use text nodes for findings or open questions.
- Group papers by theme; keep each group to a handful of papers.

### Grouping

- One group node per theme, labeled `Theme X - <name>`.
- Papers of a theme sit inside that theme's group; the root question sits
  outside and above the groups.
- Lay the theme groups in a row with a 40px gap and the root centered above
  them. The map is non-linear, so groups may hold uneven paper counts.

### Connections

- Connect the root to each theme's anchor node (its first paper or overview
  text) with a labeled `explores` edge.
- Connect papers across themes to show relationships:
  - unlabeled edge: cites
  - `extends` or `supports`
  - `contradicts`
- Keep edges purposeful; do not draw a complete graph.

### Color Semantics

- Paper node color encodes reading status:
  - `"5"` cyan: to read
  - `"3"` yellow: reading
  - `"4"` green: read and incorporated
  - `"1"` red: key paper, unresolved contradiction, or open question
- Edge color encodes the relationship: `"2"` orange for extends or supports,
  `"1"` red for contradicts, no color for cites.
- Group color stays neutral (unset) so status colors on papers remain
  readable; the root uses `"6"` purple.

### Example

```json
{
  "nodes": [
    { "id": "a3b4c5d6e7f8091a", "type": "text", "x": 300, "y": 0, "width": 460, "height": 120, "text": "# Research question", "color": "6" },
    { "id": "b4c5d6e7f8091a2b", "type": "group", "x": 0, "y": 180, "width": 460, "height": 460, "label": "Theme A - Foundations" },
    { "id": "c5d6e7f8091a2b3c", "type": "file", "x": 20, "y": 220, "width": 420, "height": 90, "file": "Papers/Paper One.md", "subpath": "#Method", "color": "4" },
    { "id": "d6e7f8091a2b3c4d", "type": "file", "x": 20, "y": 330, "width": 420, "height": 90, "file": "Papers/Paper Two.md", "subpath": "#Findings", "color": "3" }
  ],
  "edges": [
    { "id": "e7f8091a2b3c4d5e", "fromNode": "a3b4c5d6e7f8091a", "fromSide": "bottom", "toNode": "c5d6e7f8091a2b3c", "toSide": "top", "label": "explores" }
  ]
}
```

Full template: `assets/template-research-map.canvas`.

## 4. Moodboard

### Node Composition

- File nodes for images are the content; use one per visual.
- One link node per external board or reference page.
- A text node only for a title or a short note. Do not describe the images in
  words.

### Grouping

- Each group is a mood theme: Palette, Textures, References. Label it with the
  theme name.
- Arrange images of a theme inside its group in a loose grid or column; leave
  breathing room between images.
- Place theme groups side by side with a 40px gap. Moodboards are flat, so
  keep the group count low.

### Connections

- A moodboard has no edges. It is a collage, not a graph.

### Color Semantics

- Keep preset colors off image nodes: the imagery carries the color. Use at
  most one accent (`"6"` purple) on the anchor image.
- Group backgrounds stay neutral (unset); the group label names the theme.
- Link nodes may use `"5"` cyan when they should read as reference material.

### Example

```json
{
  "nodes": [
    { "id": "f8091a2b3c4d5e6f", "type": "group", "x": 0, "y": 0, "width": 420, "height": 560, "label": "Palette" },
    { "id": "091a2b3c4d5e6f70", "type": "file", "x": 20, "y": 40, "width": 380, "height": 150, "file": "Moodboard/palette-sunset.png", "color": "6" },
    { "id": "102a3b4c5d6e7f80", "type": "file", "x": 20, "y": 210, "width": 380, "height": 150, "file": "Moodboard/palette-ocean.png" }
  ],
  "edges": []
}
```

Full template: `assets/template-moodboard.canvas`.

## Templates

Each template is a small, directly importable `.canvas` file that follows the
rules above. They double as conformance fixtures for the output validator.

| Template | Pattern |
|---|---|
| `assets/template-kanban.canvas` | Kanban board with three columns |
| `assets/template-dashboard.canvas` | Home page with title and three sections |
| `assets/template-research-map.canvas` | Research question, three themes, cross-links |
| `assets/template-moodboard.canvas` | Three theme groups of images and links |
