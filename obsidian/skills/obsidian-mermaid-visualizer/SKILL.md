---
name: obsidian-mermaid-visualizer
description: Create Mermaid diagrams optimized for Obsidian notes — flowcharts, sequence / state / class / ER / C4 / git-branch diagrams, bar / pie / quadrant charts, Gantt / timeline schedules, architecture / block diagrams, mindmaps. Use when visualizing workflows, data trends, system architecture, project timelines, or hierarchical concepts in Obsidian notes. Handles Mermaid 11.4.1 syntax quirks + auto-downgrades line charts to bar (Obsidian native-viewer compat). Mermaid図・フローチャート・グラフ・データチャート・C4・ガントチャート。Mermaid 圖・流程圖・長條圖・架構圖・甘特圖・時間軸・類別圖・ER 圖。
---

# Obsidian Mermaid Visualizer

Produces clean, Obsidian-renderable Mermaid diagrams across 17 diagram types — flow / data-viz / structural / time categories. Handles Obsidian 11.4.1 syntax quirks, auto-downgrades line charts to bar (CSS bug in native viewer), and provides consistent per-type knowledge.

## Overview

When the user requests a diagram:

1. **Identify content intent** — what is the diagram trying to show? (flow / data / structure / time)
2. **Pick diagram type** via the § Diagram Type Selection Tree below
3. **Read the type file** for canonical syntax + Obsidian quirks + worked examples
4. **Apply cross-type rules** from [obsidian-common-quirks.md](obsidian-common-quirks.md) (list syntax, subgraph naming, node references, etc.)
5. **Check compatibility** via [obsidian-compatibility.md](obsidian-compatibility.md) if the type is 🟡 partial or 🔻 fallback-only
6. **Generate the Mermaid code** inside a ` ```mermaid ... ``` ` fence with brief context

## Quick start

```
User: "幫我畫一個 [content description]"
  ↓
Skill: identify category (flow / data-viz / structural / time)
  ↓
Skill: navigate § Selection Tree → specific type → read <category>/<type>.md
  ↓
Skill: generate Mermaid code + rendering notes
```

**Default assumptions** (unless user specifies otherwise):
- Vertical layout (TB) for flow / structural types
- Horizontal layout (LR) for time / gantt
- Medium detail level (balanced simplicity + information)
- Professional color palette (see § Color Scheme)
- Obsidian 11.4.1 syntax (no features requiring v11.5+)

---

## Diagram Type Selection Tree

Pick the diagram type by the content's intent. Each entry links to a type-specific file with canonical syntax, configuration options, worked examples, and error prevention.

### Flow & conceptual (流程 / 概念)

- Sequential / decision steps / workflow → [flow/flowchart.md](flow/flowchart.md)
- Cyclic / feedback loops / iteration (PDCA / OODA) → [flow/circular-flow.md](flow/circular-flow.md)
- A vs B side-by-side analysis → [flow/comparison.md](flow/comparison.md)
- Hierarchical concepts / topic breakdown → [flow/mindmap.md](flow/mindmap.md)
- Actor interactions over time / API calls → [flow/sequence.md](flow/sequence.md)
- System states + transitions (FSM / lifecycle) → [flow/state.md](flow/state.md)

### Data visualization (資料視覺化)

- Discrete bar chart (categorical data) → [data-viz/xychart.md](data-viz/xychart.md) bar mode
- **Line / trend chart** → [data-viz/xychart.md](data-viz/xychart.md) **auto-fallback to bar** (Obsidian 11.4.1 line CSS bug; see § Line Chart Fallback Policy below)
- Proportion of whole (%) → [data-viz/pie.md](data-viz/pie.md)
- 2×2 positioning (Eisenhower / impact-effort / BCG) → [data-viz/quadrant.md](data-viz/quadrant.md)

### Structural (結構 / 架構)

- Cloud / infrastructure with service icons → [structural/architecture.md](structural/architecture.md)
- Generic block / hardware layouts → [structural/block.md](structural/block.md)
- OOP class hierarchy + UML → [structural/class.md](structural/class.md)
- Database schema with cardinality → [structural/er.md](structural/er.md)
- Software architecture at 3 zoom levels (C4 model) → [structural/c4.md](structural/c4.md)
- Git branches / merges / commits → [structural/gitgraph.md](structural/gitgraph.md)

### Time / project (時程)

- Project schedule with dependencies (Gantt) → [time/gantt.md](time/gantt.md)
- Chronology without dependencies (history / release log) → [time/timeline.md](time/timeline.md)

**Decision tiebreakers** (when intent is ambiguous):

| If the user says... | Go with |
|---|---|
| "flowchart" / "workflow" (no specific type) | `flow/flowchart.md` |
| "timeline" (ambiguous — Gantt or Timeline?) | Has dependencies/durations → Gantt; just events → Timeline |
| "diagram" (generic) | Default to `flow/flowchart.md` and ask user if wrong |
| "chart" (generic) | Look for data — numeric = xychart/pie; positioning = quadrant |
| "architecture" (unclear — cloud or software?) | Cloud/infra → architecture-beta; software components → C4 |

---

## Line Chart Fallback Policy

**Trigger**: user query contains line-chart intent — words like `折線` / `line chart` / `trend` / `走勢` / `time series` / `時間序列`.

**Behavior**:
1. Produce `xychart-beta` with **bar** mode (preserves numeric data + ordered x-axis for trend feel)
2. Include an inline degrade note after the diagram:

> ⚠️ Obsidian 11.4.1 native viewer 無法正確渲染折線圖（已知 `stroke-width: 0` CSS bug），已自動降級為長條圖以保證可視化。需真折線請用 Mermaid Live Editor export PNG，或安裝 Mermaid View plugin。

**Rationale**: zero-setup principle — user shouldn't have to install CSS snippets to get a visible chart. Bar fallback preserves the numeric values and ordering; only continuous-line visualization is lost.

Full policy + why not CSS / graph TB alternatives: [obsidian-compatibility.md § Line chart fallback policy](obsidian-compatibility.md).

---

## Color Scheme Defaults

### Professional palette (use for flow / structural diagrams)

Each pair: light fill + stronger stroke. Use semantic assignments by role, not arbitrarily.

- **Green** (start / input / perception): `#d3f9d8` fill / `#2f9e44` stroke
- **Red** (decision / planning / problem): `#ffe3e3` fill / `#c92a2a` stroke
- **Purple** (processing / reasoning): `#e5dbff` fill / `#5f3dc4` stroke
- **Orange** (action / tool use / execution): `#ffe8cc` fill / `#d9480f` stroke
- **Cyan** (output / result / deliverable): `#c5f6fa` fill / `#0c8599` stroke
- **Yellow** (storage / memory / data): `#fff4e6` fill / `#e67700` stroke
- **Pink** (learning / optimization / feedback): `#f3d9fa` fill / `#862e9c` stroke
- **Blue** (metadata / title / context): `#e7f5ff` fill / `#1971c2` stroke
- **Gray** (neutral / traditional / background): `#f8f9fa` fill / `#868e96` stroke

Example:
```mermaid
style NodeA fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px
```

### Chart palette (use for data-viz diagrams — categorical data series)

For xychart (multiple bar series), pie slices, quadrant points — use a categorical palette to distinguish data series:

- Series 1: `#4c72b0` (blue)
- Series 2: `#dd8452` (orange)
- Series 3: `#55a868` (green)
- Series 4: `#c44e52` (red)
- Series 5: `#8172b3` (purple)

These are ColorBrewer-inspired, tested for colorblind-friendliness.

---

## Quality Checklist

Before outputting any diagram, verify:

### Universal checks (all 17 types)
- [ ] No `number. space` pattern in node / label text ([quirk 1](obsidian-common-quirks.md))
- [ ] Subgraphs with spaces use `subgraph id["Display"]` format ([quirk 2](obsidian-common-quirks.md))
- [ ] All node / entity references use IDs, not display text ([quirk 3](obsidian-common-quirks.md))
- [ ] Special characters replaced: `"` → `『』`, `()` → `「」` ([quirk 4](obsidian-common-quirks.md))
- [ ] No v11.5+ features used (Neo look, showDataLabelOutsideBar, wardley-beta) ([quirk 6](obsidian-common-quirks.md))
- [ ] Diagram wrapped in ` ```mermaid ... ``` ` fence
- [ ] No Emoji in node / label text (use color coding instead)

### Type-specific checks (follow the § Error prevention in the type file)
- Flow types → arrow syntax matches type (`-->` flowchart ≠ `->>` sequence)
- Data-viz → if line chart intent: bar fallback + degrade note applied
- Structural → relationship arrows match semantics (C4 uses `Rel()`, ER uses `||--o{`, class uses `<|--`)
- Time → dateFormat / duration suffix / milestone 0d rules honored

### Compatibility checks (when using 🟡 partial or 🔻 fallback types)
- [ ] Consulted [obsidian-compatibility.md](obsidian-compatibility.md) for quirks
- [ ] Applied fallback policy if applicable (line → bar, architecture icons → graph TB)
- [ ] Included inline degrade note if fallback was applied

---

## Output format

Standard output template when generating a diagram:

````
Here is the Mermaid diagram for <description>:

```mermaid
<diagram code>
```

<1-2 sentence context about diagram type choice>
<If fallback applied: inline degrade note>
<If non-trivial: rendering notes — e.g., "Renders in Obsidian 11.4.1 native viewer. For advanced features, consider Mermaid View plugin.">
````

---

## References

- [obsidian-common-quirks.md](obsidian-common-quirks.md) — cross-type rules every Mermaid diagram in Obsidian should follow (list syntax, subgraph naming, node refs, special chars, version-gap landmines)
- [obsidian-compatibility.md](obsidian-compatibility.md) — 17-type compatibility matrix for Obsidian 11.4.1, fallback policies for line charts and architecture icons, migration path for future Obsidian Mermaid upgrades
- Individual type files — see § Diagram Type Selection Tree above

---

## Design notes (non-normative)

**Directory structure** — this skill uses a non-standard layout: 4 category folders (`flow/`, `data-viz/`, `structural/`, `time/`) at the skill root instead of under a `references/` wrapper. Rationale: the 17 per-type files are primary routed content, not supplementary references. Other `obsidian/skills/*` use flat `references/` — this skill is an intentional deviation per user-approved plan.

**Single-layer router** — SKILL.md links directly to each type file, not through intermediate category routers. Rationale: Anthropic's skill authoring docs warn that nested references cause Claude partial-reads (`head -100` previews instead of full loads). Single-layer routing keeps every reference one level deep.

**Line-chart fallback as policy, not workaround** — the decision not to ship a CSS snippet is deliberate, preserving zero-setup skill contract. If Obsidian eventually upgrades Mermaid to 11.5+, see [obsidian-compatibility.md § Migration path](obsidian-compatibility.md) to remove the fallback.
