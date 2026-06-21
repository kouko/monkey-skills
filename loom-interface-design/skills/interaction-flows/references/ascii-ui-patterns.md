# ASCII UI-Structure Patterns

Conventions for the ASCII wireframe / layout blocks used in
[ui-flows.md](../ui-flows.md). Mermaid has no native wireframe or
screen-layout primitive ([mermaid-js #1184](https://github.com/mermaid-js/mermaid/issues/1184)),
so per-screen *structure* (where elements sit on a page) is drawn with
ASCII skeletons. The *flow between screens* (transitions, decision
branches, state) stays in Mermaid — see the split below.

## When ASCII vs when Mermaid

| Concern | Tool |
| --- | --- |
| Per-screen layout — what is on the screen and roughly where (nav, sidebar, content regions, panels) | **ASCII skeleton** (this file) |
| Flow between screens — navigation graph, state transitions, decision branches, sequence of steps | **Mermaid** via `obsidian:obsidian-mermaid-visualizer` |

For the Mermaid flow half, invoke the `obsidian:obsidian-mermaid-visualizer`
skill — it owns canonical Mermaid syntax (flowchart / state / sequence),
renderer-compatibility quirks, and worked examples. Do **not** re-author
Mermaid rules here; this file is only for the ASCII layout half.

## Conventions

- Wrap every skeleton in a plain fenced code block (no language tag, so
  no renderer tries to parse it) to preserve monospace alignment.
- Use box-drawing characters (`┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼`) for region borders.
- Label each region with a short uppercase tag (`NAV`, `SIDEBAR`,
  `CONTENT`, `DETAIL`) so the wireframe reads structurally, not pixel-exact.
- Keep skeletons coarse — they show *arrangement*, not final visual design.
- One skeleton per distinct screen layout; name it above the block.

## Pattern 1 — Top-nav page

A header bar across the top, full-width content beneath. Common for
marketing pages, dashboards, and content-first apps.

```
┌──────────────────────────────────────────────┐
│ LOGO    Nav1   Nav2   Nav3            [ User ] │  ← TOP NAV
├──────────────────────────────────────────────┤
│                                                │
│   PAGE TITLE                                   │
│                                                │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│   │   CARD     │ │   CARD     │ │   CARD     │ │  ← CONTENT
│   └────────────┘ └────────────┘ └────────────┘ │
│                                                │
│   ───────────────  body text  ───────────────  │
│                                                │
├──────────────────────────────────────────────┤
│ FOOTER   links · legal · contact               │
└──────────────────────────────────────────────┘
```

## Pattern 2 — Sidebar page

A persistent left navigation rail beside a content area. Common for
admin consoles, settings, and docs.

```
┌────────────┬─────────────────────────────────┐
│  SIDEBAR   │  TOP BAR        search   [ User ] │
│            ├─────────────────────────────────┤
│  ▸ Home    │                                 │
│  ▸ Items   │   SECTION HEADING               │
│  ▸ Reports │                                 │
│  ▸ Settings│   ┌───────────────────────────┐ │
│            │   │  CONTENT PANEL            │ │
│            │   │                           │ │
│            │   │                           │ │
│            │   └───────────────────────────┘ │
│            │                                 │
└────────────┴─────────────────────────────────┘
```

## Pattern 3 — List / detail (master-detail)

A scrollable list on the left, the selected item's detail on the right.
Common for inbox, file browser, and record-management screens.

```
┌─────────────────┬──────────────────────────────┐
│  LIST           │  DETAIL                        │
├─────────────────┤                                │
│ ▸ Row A    ●    │   TITLE OF SELECTED ROW        │
│ ▸ Row B         │   ──────────────────────────   │
│ ▸ Row C    ●    │                                │
│ ▸ Row D         │   field:    value              │
│ ▸ Row E         │   field:    value              │
│ ▸ Row F         │   field:    value              │
│                 │                                │
│ [ + New ]       │   [ Edit ]   [ Delete ]        │
└─────────────────┴──────────────────────────────┘
```

## Pattern 4 — TUI panel layout (optional)

A terminal-style multi-pane layout: a tree / source pane, a main work
pane, and a status line. Common for terminal tools and IDE-like apps.

```
┌─ TREE ───────┬─ EDITOR ─────────────────────────┐
│ ▾ project    │ 1  line of content                │
│   ▾ src      │ 2  line of content                │
│     file_a   │ 3  line of content                │
│     file_b   │ 4  line of content                │
│   ▸ tests    │ 5  line of content                │
├──────────────┴───────────────────────────────────┤
│ STATUS: ready          row 4, col 12      [ NORMAL ]│
└───────────────────────────────────────────────────┘
```

## See also

- [ui-flows.md](../ui-flows.md) — consumes these skeletons for the
  per-screen structure half of an interaction flow.
- `obsidian:obsidian-mermaid-visualizer` — the Mermaid flow / state /
  sequence half (screen-to-screen transitions). Reference it for any
  diagram describing *movement between* screens rather than the layout
  *within* one screen.
