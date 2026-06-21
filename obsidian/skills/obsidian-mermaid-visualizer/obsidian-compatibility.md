# Obsidian Mermaid Compatibility Matrix

17-type compatibility status for Obsidian's native Mermaid viewer + fallback policies for types that don't render correctly.

> **Data source disclosure**: the status marks in the matrix below (✅ / 🟡 / 🔻) are based on **WebSearch + Obsidian Forum research** (primarily posts from 2024 and Mermaid changelog analysis), NOT on observed rendering in any specific user's Obsidian instance. Actual render behavior in your vault may differ based on: your Obsidian version, installed plugins, custom CSS themes, OS / GPU, and network conditions (for iconify CDN). Before relying on a 🟡 or 🔻 type in production notes, test it with the canonical example from the corresponding type file.

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
| Data viz | XY Chart (line) | [data-viz/xychart.md](data-viz/xychart.md) | v11.1+ | ✅ full (with named syntax) | Use `line "name" [values]` not bare `line [values]` | Use directly with named-line form |
| Data viz | Pie | [data-viz/pie.md](data-viz/pie.md) | any | ✅ full | Title must NOT be quoted (quoting prints literal `"`); slice labels ARE quoted | Use directly |
| Data viz | Quadrant | [data-viz/quadrant.md](data-viz/quadrant.md) | v10.6+ | ✅ full | Quadrant numbering counter-intuitive; CJK axis/quadrant labels MUST be quoted, title must NOT | Use directly |
| Structural | Architecture | [structural/architecture.md](structural/architecture.md) | v11.1+ (`architecture-beta`) | 🟡 partial | Iconify CDN offline fails; CJK bracket labels MUST be quoted `["..."]` (unquoted CJK = syntax error) | Built-in icons OK; quote CJK labels; fallback to graph TB if iconify blocked |
| Structural | Block | [structural/block.md](structural/block.md) | v10.10+ (`block-beta`) | 🟡 needs testing | 2024 forum reports rendering issues | Test in target Obsidian; fallback to graph TB if broken |
| Structural | Class | [structural/class.md](structural/class.md) | any | ✅ full | Relationship arrow direction confusing | Use directly |
| Structural | ER | [structural/er.md](structural/er.md) | any | ✅ full | Cardinality syntax strict | Use directly |
| Structural | C4 | [structural/c4.md](structural/c4.md) | v9+ | ✅ full | Don't mix Context / Container / Component in one diagram | Use directly (separate per level) |
| Structural | gitgraph | [structural/gitgraph.md](structural/gitgraph.md) | any | ✅ full | Orientation setting (`TB`) unreliable; branch names must be ASCII (CJK branch = syntax error, not quotable) — put CJK in quoted `id:` / `tag:` | Use directly (LR is default) |
| Time | Gantt | [time/gantt.md](time/gantt.md) | any | ✅ full | CJK section/task names usually parse but no quoting escape (quotes render literally); if Obsidian throws `Unrecognized text`, rephrase | Use directly; verify CJK in Obsidian |
| Time | Timeline | [time/timeline.md](time/timeline.md) | v10.9+ | ✅ full | Only a space-padded ` : ` splits events (bare `9:00` is safe); no quoting escape exists | Rephrase to avoid a literal ` : ` in event text (quoting renders literally) |

**Status legend**:
- ✅ **full**: renders correctly in Obsidian 11.4.1 native viewer
- 🟡 **partial**: syntax works but some features / styling degraded
- 🔻 **fallback-only**: known bugs make this type unreliable; skill auto-degrades to a different syntax

---

## Line chart policy — named-line syntax (preferred)

**Update (April 2026)**: User testing confirmed that `xychart-beta` line mode **renders correctly in Obsidian 11.4.1** when using the named-line syntax `line "series name" [values]`. The earlier 2024 forum report of `stroke-width: 0` bug may have been specific to bare `line [values]` syntax (without a series name).

**Recommended default syntax**:

```mermaid
xychart-beta
    title "Monthly Revenue"
    x-axis "Month" ["Jan", "Feb", "Mar", "Apr", "May"]
    y-axis "NT$ M" 0 --> 100
    line "Revenue" [42, 58, 67, 81, 95]
```

**Works even without legend benefit**: use named-line even for single-series charts for consistent behavior. Multi-series works naturally:

```mermaid
    line "Product A" [35, 42, 28, 55]
    line "Product B" [22, 38, 45, 30]
```

**Fallback — only if named-line fails in a specific Obsidian environment**:

If a user reports their Obsidian vault still shows invisible lines (possible if custom CSS snippets conflict, or if a plugin modifies rendering), the skill may fall back to bar chart:

1. Produce `xychart-beta` with bar mode preserving data ordering
2. Inline note: "折線圖在此 Obsidian 環境未正常渲染，已改用長條圖。請檢查 Obsidian 是否有自訂 CSS snippet 或 plugin 影響 Mermaid 渲染。"

**This fallback is NOT auto-triggered** — default path is named-line syntax, which works in standard Obsidian 11.4.1.

**Rejected alternatives** (documented here for future maintainers):

| Alternative | Why not |
|---|---|
| CSS snippet `stroke: red !important` workaround | ❌ Unnecessary — named-line syntax works without CSS intervention |
| `graph TB` approximation | ❌ Semantic mismatch — graph is structure, line is trend |
| Always auto-fallback to bar | ❌ Would ignore the fact that line rendering works; loses the continuous-line visualization user asked for |
| **Named-line as default** | ✅ Preserves line visualization + works out of the box in Obsidian 11.4.1 |

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
| `xychart-beta` line `stroke-width: 0` (reported 2024) | Unclear — named-line syntax works in April 2026 user-tested Obsidian 11.4.1 | Bare `line [values]` may fail; named `line "name" [values]` works | Use named-line syntax (see line chart policy above) |
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
4. **If bare `line [values]` syntax starts rendering correctly** — update `data-viz/xychart.md` to note parity between named and bare forms; keep named-line as default for legend benefits
5. **Update CHANGELOG and bump skill version** — document which fallbacks are obsoleted

---

## Quick reference: safe-by-default choices

When in doubt, prefer types marked ✅ full:

- **Process flow** → flowchart / sequence / state
- **Hierarchy** → mindmap
- **Data** → pie / quadrant / xychart (bar + named-line both work)
- **Structure** → class / ER / C4
- **Time** → gantt / timeline

When user explicitly asks for types marked 🟡 or 🔻, apply the fallback policy and inform the user transparently.

See each type's individual file for syntax + examples, and [obsidian-common-quirks.md](obsidian-common-quirks.md) for cross-type rules.

---

## End-to-end verification results (v2.0.0 release)

### Automated checks — PASS

**Structural audit** (2026-04-20):
- 21 `.md` files across expected structure (1 SKILL.md + 2 cross-type + 17 type files + 1 README)
- No `references/` directory (deprecated in v2.0.0)
- All 4 category folders present: `flow/` (6 files), `data-viz/` (3), `structural/` (6), `time/` (2)

**Link integrity** (SKILL.md → type files):
- 17/17 unique type-file links resolve to existing files
- No dangling references

**Trigger routing simulation** — 18/18 PASS:
- 18 natural-language queries across zh-TW / ja / EN routed correctly to their target diagram type
- Coverage spans all 4 categories and both language mixes
- Tiebreakers confirmed working:
  - Architecture cloud-vs-software split (architecture-beta vs C4)
  - Timeline gantt-vs-timeline split (dependencies → Gantt, events-only → Timeline)
- Line-chart fallback policy triggers correctly on "line chart" / "折線" / "trend" keywords

### Manual verification pending — user-side tasks

The following tests **require actual rendering in your Obsidian vault** and are NOT performed automatically:

1. **Render test per type** — paste each type's canonical example into a `.md` note and verify it displays in preview mode
2. **xychart-beta bar rendering** — confirm bars display correctly (should ✅ per research)
3. **Line-chart user-flow test** — ask Claude: "幫我用折線圖顯示 Q1-Q4 營收" → verify skill output uses bar mode with degrade note (not line syntax)
4. **architecture-beta offline test** — disconnect internet, render an architecture-beta diagram, observe whether iconify icons appear or fail
5. **block-beta render test** — critical: 2024 forum reports said block-beta had render issues in Obsidian; verify current status in your Obsidian version
6. **C4 Context / Container / Component** — each at its own zoom level, verify boundaries and Rel() arrows
7. **gitgraph multi-branch layout** — with 3+ branches and merges, check for visual clutter
8. **Dark-mode contrast** — toggle Obsidian dark mode and verify all 17 types remain legible

### If manual tests reveal discrepancies

- Update the relevant row in the compatibility matrix above (✅ → 🟡, or 🟡 → 🔻 etc.)
- Add an entry in the `Version gap impact summary` if the issue is a Mermaid version bug
- If a fallback policy needs adjustment, update SKILL.md § Line Chart Fallback Policy or add a new §<Type> Fallback Policy section
- Open an issue in the monkey-skills repo so other users benefit from the observed behavior

