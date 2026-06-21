# Brief — ascii-graph: multi-line node labels (換行)

> Consumed by `writing-plans`. Extends the shipped `ascii-graph` skill
> (`ascii-graph-toolkit/skills/ascii-graph/`, v0.3.0). Brownfield — touches the
> shared width primitive + the box/cell/tree generators.

## Problem

(Axis 1 — JTBD)

When the assistant explains something with a generated diagram, a node's label is
often **longer than one comfortable line** or has **naturally two-part content**
(e.g. a flowchart step "驗證使用者身份\n（OAuth）", a mindmap leaf with a term + its
gloss). Today a `\n` in any label **silently corrupts** the output — the box / cell /
tree branch splits mid-label and the diagram is broken, yet the command returns
**exit 0 with no warning** (verified: `flow`/`tree`/`table`/`arch` all break). The
user states multi-line node content (換行) is a **must**. The job: **"let a node's
label span multiple lines and still render a correctly-aligned CJK box,"** the same
deterministic-alignment promise the generators already keep for single-line labels.

## Users

(Axis 2)

The assistant, mid-conversation, drawing a 流程圖 / 心智圖 for a semi-technical
reader in a Mermaid-incapable channel. Job story: **When** a node's text doesn't fit
(or reads better) on one line, **in** a generated flowchart or mindmap, **I want** to
put a `\n` in the label and get a clean multi-line box, **so I can** communicate
denser content without the diagram breaking or me hand-drawing it.

## Smallest End State

(Axis 3)

A shared multi-line primitive + multi-line rendering in the box/cell/tree generators,
and a fail-loud guard everywhere else so **no generator silently corrupts on `\n`**:

- **Shared helper** (in `width.py`, the display-width SSOT): `split_lines(label)
  -> list[str]` = `label.split("\n")` (≥1 element). Generators size to
  `max(display_width(line) for line in split_lines(label))`.
- **Multi-line RENDER** in:
  - **flow** — a step with `\n` renders one body line per label line, each centered
    to the shared interior; box grows taller, trunk/arrow unchanged.
  - **tree** — a node label with `\n`: first line carries the `├─ `/`└─ ` connector;
    each continuation line carries the sibling continuation prefix (`│  ` if the node
    has a following sibling, else `   `) so it aligns under the label.
  - **table** — a cell with `\n` makes its row taller: row height = max line-count
    across the row's cells; each physical line shows each cell's i-th line
    (blank-padded when a cell has fewer lines); column width = max line width in
    that column.
  - **arch** — component cells and the layer-name line accept `\n`, same row-height
    logic as table (a band grows taller to fit its tallest cell).
- **Fail-loud REJECT** (multi-line deferred for these): **seq** and **bar** raise a
  clear `ValueError` if any label contains `\n` (instead of silently breaking).
- **Guarantee:** every generator's output stays rectangular (every line equal
  display width) — multi-line boxes included — verified by each generator's tests;
  hand-drawn diagrams still verified by `align.py`. Single-line behavior is
  byte-identical to today (a label with no `\n` is the 1-element case).

## Current State Evidence

(Brownfield.)

- **Forward (where labels become lines):** each generator turns a label into exactly
  ONE rendered line today — `gen_flow.py:66` (`"│"+_center(step,interior)+"│"`),
  `gen_table.py:53-56` (one `data_line` per row), `gen_tree.py:35`
  (`prefix+connector+child["label"]`), `gen_arch.py` (centered name line + one
  component-cell row), `gen_bar.py` (one `label  ████ value` line),
  `gen_seq.py` (participant box body + per-message label/arrow rows). The `\n` is
  never split — it passes through into the output string verbatim.
- **Reverse (SSOT ownership):** no sync/distribute script governs these scripts
  (standalone plugin). `width.py` is the in-skill display-width SSOT
  (`char_width`/`display_width`, `width.py:18-26`); `\n` → `wcwidth(-1)` → mapped to
  0 width, which is exactly why the broken line passes width checks today. The new
  `split_lines` belongs in `width.py` (layout-width concern, single-sourced) and is
  imported by every generator that already imports `display_width`.
- **Error:** generators currently raise `ValueError` only for unknown shape
  (`generate.py:48`) and seq self-message (`gen_seq.py`). A `\n` raises nothing →
  silent corruption. New: seq/bar gain an explicit `ValueError` on `\n`.
- **Data:** payloads unchanged — labels are still plain strings; a string may now
  contain `\n`. No schema change.
- **Boundary:** multi-line box output must stay rectangular. For the generators this
  is by construction (each line padded to the shared width). For hand-drawn diagrams,
  `align.py` already validates multi-line boxes (proven this session: a 2-line CJK box
  passed `✓ no drift`) — so no align.py change is needed.

Evidence paths: `…/scripts/width.py`, `…/gen_flow.py`, `…/gen_table.py`,
`…/gen_tree.py`, `…/gen_arch.py`, `…/gen_bar.py`, `…/gen_seq.py`, `…/generate.py`,
`…/align.py`, `…/SKILL.md`, `…/tests/`.

## Decision

Add `split_lines` to `width.py` and render multi-line labels in **flow, tree, table,
arch** (split on `\n`, size to the widest line, pad every line to the shared
width so output stays rectangular). For **seq** and **bar**, where multi-line is
deferred / not meaningful, **reject `\n` with a clear `ValueError`** rather than
silently corrupt. We will **NOT** auto-wrap long labels at a width limit (the author
controls breaks via explicit `\n` — auto-wrap is a separate, fuzzier feature). We
will **NOT** build multi-line for seq in this change (participant-box height + message
row-height + arrow repositioning is a larger layout problem). Net invariant after this
change: **no generator silently produces broken output for a `\n` label** — it either
renders it correctly or fails loud.

## Alternatives Considered

(Axis 4 — the split-on-`\n` + size-to-widest-line convention is universal.)

1. **Explicit `\n` in the label, split + size to widest line (chosen).** Source: the
   convention used by Graphviz record/HTML labels, PlantUML (`\n` in labels), and
   every monospace multi-line table renderer. Pros: author controls exactly where
   breaks fall; deterministic; trivial primitive (`str.split`); single-line is the
   1-element degenerate case (zero regression risk). Cons: author must insert breaks
   (no auto-wrap). **Chosen** — matches the skill's "deterministic, author-driven"
   ethos.
2. **Auto-wrap at a width limit (e.g. `max_width: 20`).** Pros: no manual breaks.
   Cons: wrapping CJK *well* is hard (no spaces between 漢字; line-break rules 禁則
   differ JA/ZH), it's a fuzzier feature, and it complects "where to break" into the
   generator. **Rejected** for v1 — layerable later on top of explicit `\n` if asked.
3. **Reject `\n` everywhere (fail-loud only, no multi-line).** The earlier-offered
   minimal option. Pros: smallest. Cons: the user explicitly said multi-line is a
   **must** — fail-loud alone doesn't deliver the job. **Rejected** (but kept as the
   seq/bar treatment where render is deferred).

## What Becomes Obsolete

(Axis 5)

- The current **silent-corruption-on-`\n`** behavior across all generators is the
  thing removed: every `\n` path now either renders correctly (flow/tree/table/arch)
  or raises (seq/bar). No code is deleted (additive), but the latent silent-failure
  class is closed. SKILL.md gains a short "multi-line labels" note + one worked
  example; the manifest description/version bumps (0.3.0 → 0.4.0, additive feature).

## Out of Scope

- Auto-wrapping long labels at a width limit (alternative 2 — explicit `\n` only).
- Multi-line for **seq** (participant boxes + message rows + arrow repositioning) —
  deferred; seq rejects `\n` loudly for now.
- Multi-line for **bar** (a bar row is inherently one line) — rejects `\n` loudly.
- Vertical alignment options (top/middle/bottom) for shorter cells in a tall table
  row — v1 top-aligns (blank-pad below); configurable alignment is a later nicety.
- Any `align.py` change (it already validates multi-line boxes).

## Open Questions

1. **Tall-table cell vertical alignment** — when one cell in a row has 3 lines and
   its neighbor has 1, the short cell's extra rows are blank below (top-aligned).
   Lean: top-align in v1 (simplest, predictable); note as a future option. Settle in plan.
2. **Empty line in a label** (`"a\n\nb"` → a blank middle line) — should render a blank
   interior line (height 3). Lean: yes, preserve author's blank line. Confirm in plan.
