# Brief — ascii-graph v2-A: layered-architecture generator

> Consumed by `writing-plans`. Extends the shipped `ascii-graph` skill
> (`ascii-graph-toolkit/skills/ascii-graph/`). Brownfield — adds one new
> generator alongside table / flow / tree / bar.

## Problem

(Axis 1 — JTBD)

When the assistant explains a system to a **semi-technical** reader in a
plain-text channel (CC terminal / Slack / PR), the most-requested shape — a
**layered / n-tier architecture diagram** (Presentation → Business → Data,
each layer holding several components) — currently has **no generator**. It
falls to the hand-drawn `align.py` verify-loop, where the tedium is real:
nested boxes (an outer layer band containing a row of component boxes) must be
hand-aligned cell-by-cell, and CJK component labels (中/英/日, 2 cells each)
make eyeballed padding silently drift. The job: **"turn a structured
description of layers-and-their-components into a guaranteed-aligned stacked
architecture diagram in one shot,"** the same deterministic-generation promise
the other four shapes already keep.

## Users

(Axis 2)

The assistant itself, mid-conversation, rendering an architecture explanation
for a reader who *懂一點技術但不是非常精通* — in a Mermaid-incapable channel.
Job story: **When** I need to show a non-expert how a system's layers stack and
what lives in each, **in** a plain-text channel, **I want** to hand a
`{layers:[...]}` structure to a generator, **so I can** get a high-density,
CJK-aligned diagram without hand-counting display columns.

## Smallest End State

(Axis 3 — minimum shippable)

A fifth generator, **`arch`**, wired into the existing `generate.py` dispatch:

- **Input:** `{"layers": [{"name": str, "components": [str, ...]}, ...]}` —
  flat 2-level (layer → list of component label strings). Matches the canonical
  layered model (a set of layers, each a set of components; dependency is
  top-down by vertical order).
- **Output:** a vertical stack of **independent, equal-outer-width boxes**, one
  per layer. Each box = `[top border]` / `[centered layer-name line]` /
  `[separator]` / `[one component row of cells]` / `[bottom border]`. All layers
  share ONE outer interior width so the stack's left/right edges line up; within
  a layer, component cells are sized by `display_width` so CJK labels align;
  the row's cells sum to the shared interior width (slack distributed
  deterministically). Top-down layering is conveyed by **vertical containment +
  order** — no connector arrows in v1.
- **Guarantee:** output is **aligned by construction** and passes
  `align.py` (`✓ no drift`, exit 0) with no hand-fixing — identical contract to
  the other four generators.
- **Surfaces touched:** `generate.py` (`_SHAPES` + `render()` + usage),
  new `gen_arch.py`, `tests/test_gen_arch.py`, and `SKILL.md` (routing table
  row + one worked example + honest-ceiling/ Bundled-files update).

Example shape (illustrative — exact glyphs settled in the plan):

```
┌────────────────────────────────────┐
│            Presentation            │
├──────────┬────────────┬────────────┤
│ Web App  │ モバイル    │ 桌面端     │
└──────────┴────────────┴────────────┘
┌────────────────────────────────────┐
│           Business Logic           │
├─────────────────┬──────────────────┤
│ 訂單サービス     │ 在庫サービス      │
└─────────────────┴──────────────────┘
┌────────────────────────────────────┐
│                Data                │
├────────────────────────────────────┤
│ PostgreSQL / Redis                 │
└────────────────────────────────────┘
```

## Current State Evidence

(Brownfield — extending the shipped skill.)

- **Forward (how a generator is invoked):** stdin JSON → `generate.py:64`
  `json.load` → `render(shape, payload)` dispatch
  (`generate.py:29-48`) → per-shape `render_X` → stdout. Shape allow-list is the
  `_SHAPES` tuple (`generate.py:26`). User-facing routing is the SKILL.md table
  (`SKILL.md:22-30`) + a worked `echo … | generate.py <shape>` block per shape.
- **Reverse (SSOT ownership):** **no sync/distribute script governs the
  `ascii-graph` scripts** — this is a standalone plugin, not the code-team
  byte-synced copy. In-skill SSOT is **`width.py`** (display-width primitive,
  wraps `wcwidth`) and **`glyphs.py`** (box-drawing taxonomy, imported by the
  checks — `checks_kink.py:24`). A new generator imports `width.display_width`
  directly (same as `gen_table.py:14`, `gen_flow.py:27`); it uses only default
  light box-drawing glyphs, so it needs no `glyphs.py` import.
- **Error:** unknown shape → `ValueError` (`generate.py:48`) / `return 2` with a
  stderr message (`generate.py:59-62`). Adding `arch` means extending `_SHAPES`,
  `render()`, and the usage string together (single touch point each).
- **Data:** payload is one shape's JSON on stdin; new payload is
  `{"layers":[{"name","components":[...]}]}`. Cells/labels are plain strings
  (same as table cells, `gen_table.py:36-47`).
- **Boundary:** generated output MUST be `align.py`-clean. The nested
  outer-band-plus-component-row structure is exactly what `checks_kink`
  (nested-box false-positive fixed in v1 T5b) and `checks_table` (equal-width
  cells) inspect — so a per-output `align.py` assertion belongs in the tests
  (the e2e suite already round-trips generators through `align.py`,
  `tests/test_e2e.py`).

Evidence paths: `ascii-graph-toolkit/skills/ascii-graph/scripts/generate.py`,
`…/gen_table.py`, `…/gen_flow.py`, `…/gen_tree.py`, `…/glyphs.py`, `…/width.py`,
`…/align.py`, `…/checks_kink.py`, `…/SKILL.md`, `…/tests/`.

## Decision

Build a deterministic **`arch`** generator that renders a flat 2-level
`{layers:[{name,components}]}` structure as a vertical stack of equal-width,
independent boxes (layer-name line + one component-cell row each), CJK-aligned
by `display_width` and aligned-by-construction (passes `align.py`). We will
**NOT** draw any connector arrows between layers or between components in v1:
top-down layering is shown by vertical order and containment. We will **NOT**
support recursive/nested sub-components (components are flat strings) — depth
belongs to the existing `tree` generator. This keeps the work strictly inside
the deterministic-layout envelope and away from the free-topology graph-layout
wall that v1 deliberately avoided.

## Alternatives Considered

(Axis 4 — researched, EN + JA)

1. **Status quo: hand-draw + `align.py` verify-loop.** Source: the shipped
   SKILL.md routing (`SKILL.md:28`). Pros: zero new code; already supported.
   Cons: the exact tedium the user flagged — nested-box alignment is the most
   error-prone hand-draw case, and the verify-loop catches drift but doesn't
   *remove* the hand-labour. **Rejected as the primary path** for this common
   shape (keep it as the fallback for irregular topologies).
2. **Recursive nested-box generator (arbitrary depth + cross-arrows).** Pros:
   one generator for all box diagrams. Cons: arbitrary cross-component arrows =
   graph layout = reinvents graphviz; the canonical layered model
   ([A Model of Layered Architectures, arXiv:1503.04916] / Lucidchart JA
   アーキテクチャ図) defines inter-layer links as **strictly top-down**, which
   vertical order already encodes — general arrows are unneeded for this shape.
   **Rejected** (over-general; breaks the in-envelope promise).
3. **External diagrams-as-code engine** (Mermaid/Structurizr export to ASCII).
   Source: JA DevelopersIO ARC308 diagram-as-code review; Lucidchart JA. Cons:
   v1's hand-tested survey found **no engine renders CJK-correct ASCII** — the
   same finding that deferred all external engines to v2-D. **Deferred**, not
   chosen here.

**My take (given the brief):** Recommend **#1's structure, productised** — a
flat 2-level deterministic generator (the chosen Decision). It removes the
hand-labour for the single most-tedious shape while staying fully inside the
deterministic, `align.py`-verifiable envelope. **Conditional reversal:** if real
use shows readers need explicit cross-layer dependency arrows (not just
containment), revisit a *single centered inter-layer ▼ trunk* (deterministic,
like `flow`) — but cross-*component* arrows stay out (that is the graph wall).

EN ↔ JA agreement: both frame layered architecture as horizontal layers with
top-down dependency and recommend diagram-as-code text definitions; neither
surfaced a CJK-correct ASCII layered renderer — consistent, no disagreement.

## What Becomes Obsolete

(Axis 5)

- The SKILL.md routing currently sends layered architecture down the **hand-drawn
  verify-loop** path (`SKILL.md:28`, "Any other box-and-arrow flowchart you
  compose by hand"). Once `arch` ships, that guidance is stale for this shape —
  **move layered architecture from the verify-loop row to a `generate.py arch`
  row in the same PR**, and trim the honest-ceiling/Bundled-files sections to
  list the new generator. Nothing else is removed (purely additive generator).

## Out of Scope

- Connector arrows between layers or components (graph-wall-adjacent; vertical
  containment conveys top-down layering in v1).
- Recursive / nested sub-components (flat string components only; depth = `tree`).
- `align.py --fix` auto-fix (that is v2-B).
- External-engine rendering / fallback (that is v2-D).
- The two 🟢 SSOT next-touch nits (that is v2-E) — untouched here.

## Open Questions

1. **Component-row slack distribution** — when a layer's components are
   narrower than the shared outer width, where does the extra width go
   (pad the last cell / distribute evenly / center each cell)? Lean: distribute
   evenly across cells, remainder to the last — deterministic, settle in plan.
2. **Single-component / single-layer degenerate cases** — a layer with one
   component, or a one-layer diagram, must still render a clean box. Covered as
   explicit test cases in the plan.
