# Obsidian Mermaid Compatibility Matrix

17-type compatibility status for Obsidian's native Mermaid viewer + fallback policies for types that don't render correctly.

## Obsidian Mermaid version context

- **Obsidian bundled Mermaid**: 11.4.1 (as of April 2026)
- **Mermaid latest official**: 11.14.0
- **Version gap**: ~10 minor versions
- **Impact**: Features added in v11.5+ are unavailable; some known bugs (e.g., xychart line rendering) remain unfixed in Obsidian's native viewer

If you need a newer Mermaid feature, options are (from least to most intrusive):
1. Use fallback syntax documented below (zero setup)
2. Export via [Mermaid Live Editor](https://mermaid.live/) as PNG, embed the image in your note
3. Install the [Mermaid View plugin](https://forum.obsidian.md/t/plugin-mermaid-view/110220) which bundles a newer Mermaid

This skill is designed for **option 1** (zero-setup Obsidian native rendering).

---

## 17-Type compatibility matrix

| Category | Type | Path | Mermaid req | Obsidian 11.4.1 | Known quirks | Recommendation |
|---|---|---|---|---|---|---|
| Flow | Flowchart | [flow/flowchart.md](flow/flowchart.md) | any | ✅ full | Undirected edges may render directed (11.5+ fix) | Use directly |
| Flow | Circular flow | [flow/circular-flow.md](flow/circular-flow.md) | any (graph) | ✅ full | — | Use directly |
| Flow | Comparison | [flow/comparison.md](flow/comparison.md) | any | ✅ full | — | Use directly |
| Flow | Mindmap | [flow/mindmap.md](flow/mindmap.md) | v9.3+ | ✅ full | FontAwesome icons unreliable | Avoid icons; otherwise use directly |
| Flow | Sequence | [flow/sequence.md](flow/sequence.md) | any | ✅ full | — | Use directly |
| Flow | State | [flow/state.md](flow/state.md) | any | ✅ full | Use v2 (`stateDiagram-v2`) not v1 | Use directly |
| Data viz | XY Chart (bar) | [data-viz/xychart.md](data-viz/xychart.md) | v11.1+ (`xychart-beta`) | ✅ full | — | Use directly |
| Data viz | **XY Chart (line)** | [data-viz/xychart.md](data-viz/xychart.md) | v11.1+ | 🔻 fallback-only | `stroke-width: 0` CSS bug — lines invisible | **Auto-fallback to bar + inline note** |
| Data viz | Pie | [data-viz/pie.md](data-viz/pie.md) | any | ✅ full | — | Use directly |
| Data viz | Quadrant | [data-viz/quadrant.md](data-viz/quadrant.md) | v10.6+ | ✅ full | Quadrant numbering counter-intuitive | Use directly |
| Structural | Architecture | [structural/architecture.md](structural/architecture.md) | v11.1+ (`architecture-beta`) | 🟡 partial | Iconify CDN offline fails | Built-in icons OK; fallback to graph TB if iconify blocked |
| Structural | Block | [structural/block.md](structural/block.md) | v10.10+ (`block-beta`) | 🟡 needs testing | 2024 forum reports rendering issues | Test in target Obsidian; fallback to graph TB if broken |
| Structural | Class | [structural/class.md](structural/class.md) | any | ✅ full | Relationship arrow direction confusing | Use directly |
| Structural | ER | [structural/er.md](structural/er.md) | any | ✅ full | Cardinality syntax strict | Use directly |
| Structural | C4 | [structural/c4.md](structural/c4.md) | v9+ | ✅ full | Don't mix Context / Container / Component in one diagram | Use directly (separate per level) |
| Structural | gitgraph | [structural/gitgraph.md](structural/gitgraph.md) | any | ✅ full | Orientation setting (`TB`) unreliable | Use directly (LR is default) |
| Time | Gantt | [time/gantt.md](time/gantt.md) | any | ✅ full | — | Use directly |
| Time | Timeline | [time/timeline.md](time/timeline.md) | v10.9+ | ✅ full | Colons in event text collide with separator | Escape or rephrase |

**Status legend**:
- ✅ **full**: renders correctly in Obsidian 11.4.1 native viewer
- 🟡 **partial**: syntax works but some features / styling degraded
- 🔻 **fallback-only**: known bugs make this type unreliable; skill auto-degrades to a different syntax

---

## Line chart fallback policy

**Trigger**: user query contains line-chart intent — `折線` / `line chart` / `trend` / `走勢` / `時間序列` / `time series` / `line graph` / similar.

**Behavior**:
1. Skill produces `xychart-beta` with **bar mode** (preserves numeric data + ordered x-axis for trend feel)
2. Skill includes an inline degrade note after the diagram:

> ⚠️ Obsidian 11.4.1 native viewer 無法正確渲染折線圖（已知 `stroke-width: 0` CSS bug），已自動降級為長條圖以保證可視化。需真折線請用 Mermaid Live Editor export PNG，或安裝 Mermaid View plugin。

**Why this policy**:

| Alternative | Why not |
|---|---|
| CSS snippet fix (`.obsidian/snippets/xychart-lines.css`) | ❌ Requires user setup; breaks "zero-setup" skill contract |
| `graph TB` approximation | ❌ Semantic mismatch — graph is structure, line is trend |
| Produce line syntax anyway + warn user | ❌ Diagram visibly fails; user has to re-run or manually fix |
| **Bar fallback with note** | ✅ Preserves numeric values + ordering + immediately usable + transparent about limitation |

**When Obsidian upgrades Mermaid to 11.5+**: verify the `stroke-width: 0` bug is resolved; if so, remove this policy and allow line mode. See § Migration path.

---

## Architecture icon fallback policy

**Trigger**: producing `architecture-beta` that uses `iconify` icons AND user reports (or environment indicates) icons are not loading.

**Causes**:
- Offline environment (iconify CDN unreachable)
- Corporate firewall blocking `cdn.jsdelivr.net`
- Obsidian running in restricted network

**Behavior**:
1. Detect icon-loading failure (user reports "icons missing" or environment known offline)
2. Re-generate as `graph TB` + subgraph, preserving the structural layout but dropping iconify icons
3. Keep the 5 built-in architecture icons when possible (`cloud`, `server`, `database`, `disk`, `internet`) — these don't need CDN
4. Inline note explaining the degrade:

> ⚠️ Iconify icons require network access to `cdn.jsdelivr.net`. Rendering as `graph TB` with subgraph layout instead. For full iconify-rendered architecture diagrams, enable network access or export via Mermaid Live Editor.

**Preferred path when online + unblocked**: use `architecture-beta` with full iconify icons.

---

## Version gap impact summary

Bugs known to exist in Mermaid 11.4.1 (and thus in Obsidian 11.4.1) that were fixed in 11.5+:

| Bug | Fixed in | Obsidian 11.4.1 behavior | Workaround |
|---|---|---|---|
| `xychart-beta` line `stroke-width: 0` | Possibly fixed v11.5+ (unverified) | Lines invisible, bars visible | Line-chart fallback policy above |
| Undirected graph rendering as directed | v11.5 | Undirected `---` shows arrow anyway | Use explicit directed `-->` arrows |
| Various minor arrow rendering issues | v11.5–11.8 | May see misaligned or mis-styled arrows | Prefer standard arrow types |

Features unavailable in Obsidian 11.4.1:

- `look: neo` theme (drop-shadows, soft padding) — added in v11.14.0
- `showDataLabelOutsideBar` xychart option — added in v11.14.0
- `wardley-beta` (Wardley Maps) — added v11.10+
- `packet-beta` (Packet diagrams) — not supported in Obsidian even if syntax works
- Hand-drawn sketch look — needs explicit init config, limited reliability

---

## Migration path

When Obsidian upgrades its bundled Mermaid to 11.5+ or newer:

1. **Check new version** — via Obsidian changelog or compare test diagram output with [Mermaid Live Editor](https://mermaid.live/)
2. **Re-verify 🟡 and 🔻 types** — follow the end-to-end test checklist from this skill's Commit 4 (test each type with its canonical example in the new Obsidian)
3. **Update the compatibility matrix above** — change the "Obsidian 11.4.1" column header to the new version and adjust status marks
4. **If `xychart-beta` line bug is fixed** — remove the Line chart fallback policy; allow direct `line [...]` syntax
5. **Update CHANGELOG and bump skill version** — document which fallbacks are obsoleted

---

## Quick reference: safe-by-default choices

When in doubt, prefer types marked ✅ full:

- **Process flow** → flowchart / sequence / state
- **Hierarchy** → mindmap
- **Data** → pie or quadrant (not xychart line)
- **Structure** → class / ER / C4
- **Time** → gantt / timeline

When user explicitly asks for types marked 🟡 or 🔻, apply the fallback policy and inform the user transparently.

See each type's individual file for syntax + examples, and [obsidian-common-quirks.md](obsidian-common-quirks.md) for cross-type rules.
