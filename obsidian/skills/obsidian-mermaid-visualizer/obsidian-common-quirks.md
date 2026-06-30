# Obsidian Mermaid — Common Quirks Across All Diagram Types

Rules that apply to **every** Mermaid diagram type when rendered in Obsidian. If you are writing or reviewing any diagram, skim this first. Type-specific syntax lives in each type's own file under `flow/`, `data-viz/`, `structural/`, `time/`.

---

## Version notice

- **Obsidian bundled Mermaid**: 11.4.1 (as of April 2026)
- **Mermaid latest official**: 11.14.0
- **Gap**: ~10 minor versions behind — features added in 11.5+ are unavailable in Obsidian's native viewer

**Rule of thumb when writing diagrams for Obsidian notes**:
- Use only syntax documented in Mermaid docs as available in v11.4.1 or earlier
- Avoid features flagged as "11.5+" or newer in Mermaid changelog
- For full compatibility matrix per diagram type, see [obsidian-compatibility.md](obsidian-compatibility.md)

---

## Quirk 1: List syntax conflict (most common error)

**Root cause**: Mermaid parser interprets `number. space` inside node text as Markdown ordered list syntax.

**Error message**: `Parse error: Unsupported markdown: list`

**Wrong**:
```
❌ [1. Perception]
❌ [2. Planning]
❌ [3. Reasoning]
```

**Fix — 4 safe numbering options**:
```
✅ [1.Perception]           — remove space after period
✅ [① Perception]           — use circled numbers
✅ [(1) Perception]         — use parentheses
✅ [Step 1: Perception]     — use "Step" prefix
✅ [Step 1 - Perception]    — use dash separator
✅ [Perception]             — drop numbering entirely
```

**Circled-number reference**:
```
① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩ ⑪ ⑫ ⑬ ⑭ ⑮ ⑯ ⑰ ⑱ ⑲ ⑳
```

This quirk applies to **every** diagram type that has node text (flowchart, class, ER, sequence, state, etc.).

---

## Quirk 2: Subgraph naming rule

**Rule**: Subgraphs with spaces in their name must use `subgraph id["Display Name"]` format. Applies to flowchart / graph / state / sequence / architecture whenever subgraphs are used.

**Wrong**:
```mermaid
❌ subgraph Core Process
     A --> B
   end
```

**Right**:
```mermaid
✅ subgraph core["Core Process"]
     A --> B
   end

✅ subgraph core_process            — simple ID only, no spaces
     A --> B
   end
```

**Referencing subgraphs** (in any context — links, nesting, etc.): always use the **ID**, never the display name.

```mermaid
❌ Title --> Core Process      — cannot reference display name
✅ Title --> core              — must reference ID
```

---

## Quirk 3: Node reference rule

**Rule**: Always reference nodes by their **ID**, never by their display text. Applies universally.

```mermaid
# Define nodes
A[Display Text A]
B["Display Text B"]

# Reference nodes
A --> B                              ✅ use node IDs
Display Text A --> Display Text B    ❌ cannot use display text
```

This is the most common silent-failure pattern: diagram parses but layout is wrong because Mermaid treats display-text-as-reference as new unconnected nodes.

---

## Quirk 4: Special characters in node / label text

**Problematic characters and their safe replacements**:

| Character | Problem | Safe replacement |
|---|---|---|
| `"` (double quote) | Breaks node text parsing | `『』` (CJK quote) |
| `()` (parens in text) | Ambiguous with shape syntax | `「」` (CJK bracket) |
| `:` (colon) | Usually safe; avoid if parsing fails | Use dash or remove |
| `<br/>` (line break) | Works in quoted node labels: `["Text<br/>Line"]`, `(("Text<br/>Line"))`, etc. | Does **not** work unquoted; use `["..."]` quoting |
| `#` (hash) | Reserved; escape with `&#35;` | Replace with text "number" |

**Length guideline**: keep node text under 50 characters. Long labels should be broken into annotation nodes or use circle-node line breaks.

---

## Quirk 4.5: Always quote user-visible display strings (where the parser allows it)

**Rule**: Wrap user-visible display text in `"..."` wherever the diagram type's parser accepts it.

**Rationale**:
- CJK (Chinese / Japanese / Korean) text fails unpredictably without quotes across many Mermaid positions
- EN text often works unquoted but can fail silently on special characters (spaces, dashes, parentheses, reserved words)
- Unified rule eliminates per-case judgment and avoids the "works most of the time" trap

**Positions where quoting IS required or safe (apply consistently)**:
- Flowchart / graph / circular-flow / comparison node labels: `A["Label"]`, `B("Label")`, `C(("Label"))`, `D{"Decision?"}`, `E[/"Para"/]`, `F[("DB")]`, etc.
- Flowchart arrow labels: `A -->|"Label"| B`
- Subgraph display names with spaces: `subgraph id["Display Name"]`
- Pie slice labels: `"Label" : value` (the pie **title** must NOT be quoted — see unquoted list)
- Quadrant data points: `"Name": [x, y]`
- Quadrant x-axis / y-axis / quadrant-N labels: CJK MUST be quoted (`x-axis "單一規則" --> "完整框架"`); the quadrant **title** must NOT — see [data-viz/quadrant.md](data-viz/quadrant.md)
- xychart title, axis names, categorical x-axis labels, series names: all `"..."` per [data-viz/xychart.md](data-viz/xychart.md) Style rule
- Block-beta labels: `id["Display"]`
- Architecture-beta bracket labels containing CJK / special chars: `service x(server)["應用伺服器"]` — unquoted CJK in a bracket throws a syntax error
- C4 element / boundary / relationship labels: all quoted per C4 canonical syntax
- gitGraph commit IDs and tags: `id: "..."`, `tag: "..."`

**Positions where quoting is NOT supported — leave unquoted**:
- Identifiers / node IDs / branch names / class names / entity names (references, not display strings) — keep these **ASCII**: CJK in an identifier position (e.g. a gitGraph `branch 開發`) throws a syntax error and **cannot** be fixed by quoting; romanize it, or move the CJK into a quotable display field (tag / commit-id / label)
- Keywords: `subgraph`, `end`, `class`, `state`, `loop`, `alt`, `participant`, `actor`, `section`, `title`, `direction`
- Sequence message text / state transition labels / state descriptions (positions after `:` in sequence-v2 and state-v2)
- Gantt title / section / task name (all free-form after keyword; quoting renders literally — if CJK fails to parse, rephrase, there is no quoting escape)
- Timeline title / section / period / event text (same: quoting renders literally)
- Pie title and Quadrant title (free-form to end of line; quoting prints literal `"`). ⚠️ Quadrant **axis / quadrant-N labels are the exception** — those MUST be quoted for CJK (see quoted list above)
- Architecture-beta bracket content for **ASCII** labels (`[Label]`); CJK / special-char bracket labels MUST be quoted (`["..."]`) — see quoted list above
- Numeric values, arrow operators, cardinality symbols, shape syntax without text content

**When uncertain**: test in Mermaid Live Editor first; if quotes render literally in output, the position does not support quoting — leave unquoted and rely on rephrasing to avoid special characters.

Per-type quote rules are documented at the top of each type file under `## Quote rule for <type>`.

---

## Quirk 5: Inline styling syntax

**Rule**: Style declarations use the same syntax across all diagram types that support styling.

```mermaid
style NodeID fill:#color,stroke:#color,stroke-width:2px
```

**Color formats**:
- Hex: `#ff0000` or `#f00` (recommended)
- RGB: `rgb(255,0,0)` (works but verbose)
- Named: `red`, `blue`, etc. (limited support; stick to hex)

**Style multiple nodes at once** — do NOT use comma-separated `style` (Obsidian 11.4.1 parses it as one long node ID and creates an orphan node):

```
❌ style A,B,C fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px    ← renders as orphan node "A,B,C"
```

Use `classDef` + `class` instead (standard Mermaid multi-node styling):

```mermaid
classDef greenGroup fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px
class A,B,C greenGroup
```

This defines a named class once, then applies it to multiple node IDs. Supported universally in Mermaid including Obsidian 11.4.1.

**Font color for dark backgrounds**:
```mermaid
style Title fill:#1971c2,stroke:#1971c2,stroke-width:3px,color:#ffffff
```

---

## Quirk 6: Version-gap landmines (v11.4.1 vs v11.14.0)

Because Obsidian ships Mermaid 11.4.1, features added in 11.5+ will NOT render correctly in Obsidian's native viewer. Do not use:

| Feature | Added in | Obsidian 11.4.1 behavior |
|---|---|---|
| `look: neo` (drop-shadow sketch) | 11.14.0 | Ignored; falls back to default |
| `showDataLabelOutsideBar` (xychart) | 11.14.0 | Not recognized |
| `wardley-beta` | 11.10+ | Syntax error |
| Neo look styling | 11.14.0 | Ignored |
| Updated arrow rendering | 11.5+ | Older behavior in Obsidian |
| Fixed undirected-graph rendering | 11.5 | Obsidian still renders undirected as directed |

**If you encounter a bug in Obsidian that is known-fixed in Mermaid 11.5+**: either wait for Obsidian to upgrade, or degrade the diagram type (see [obsidian-compatibility.md](obsidian-compatibility.md) fallback policies).

**Specific beta types available in 11.4.1** (syntax works but may have styling quirks):
- `xychart-beta` (v11.1+) ✅ bar works / 🔻 line has CSS bug
- `architecture-beta` (v11.1+) 🟡 icon CDN dependency
- `block-beta` (v10.10+) 🟡 needs testing
- `packet-beta` (v11.0+) — not in scope

---

## Error message → root cause cheatsheet

| Error message | Root cause | Fix |
|---|---|---|
| `Unsupported markdown: list` | `number. space` pattern in node text | Quirk 1 |
| `Parse error on line X: Expecting 'SEMI', 'NEWLINE', 'EOF'` | Subgraph with spaces missing ID format, OR node reference by display text | Quirk 2 / Quirk 3 |
| `unexpected character` | Unescaped special character (`"`, `()`, etc.) | Quirk 4 |
| Diagram renders but layout is wrong | Likely display-text-used-as-reference silently creating unconnected nodes | Quirk 3 |
| Undirected graph looks directed | Known 11.4.1 bug — fixed in 11.5+ | Use explicit arrows |
| `xychart` lines invisible | `stroke-width: 0` CSS bug in 11.4.1 | Use bar mode (see [obsidian-compatibility.md § Line chart fallback policy](obsidian-compatibility.md)) |
| Architecture diagram icons missing | iconify CDN offline / blocked | See [obsidian-compatibility.md § Architecture icon fallback policy](obsidian-compatibility.md) |

---

## Cross-type validation checklist

Before finalizing ANY Mermaid diagram for an Obsidian note:

- [ ] No `number. space` pattern in any node / label text
- [ ] All subgraphs with spaces use `subgraph id["Display Name"]` format
- [ ] All node references use IDs, never display text
- [ ] **User-visible display strings quoted in positions that support it** (flowchart nodes, arrow labels, pie labels, quadrant data points, xychart title/axis/series, C4 labels, gitGraph tags) — see Quirk 4.5
- [ ] Special characters (`"`, `()`) replaced with safe equivalents (`『』`, `「」`)
- [ ] No features from Mermaid 11.5+ (Neo look, showDataLabelOutsideBar, wardley-beta)
- [ ] Style declarations use valid hex colors and syntax
- [ ] Emojis NOT used in node text (use color coding or text labels instead)
- [ ] Diagram tested in target renderer (Obsidian preferred; Mermaid Live Editor for pre-validation)

---

## Platform notes

**Obsidian** (primary target):
- Mermaid version 11.4.1 (bundled, may lag behind)
- Strictest parser — if it works here, it usually works elsewhere
- Known quirks for xychart lines, architecture icons, undirected graphs
- Test diagrams in target vault before publishing

**GitHub**:
- Mermaid version typically newer than Obsidian
- Most features supported including betas
- Good pre-validation platform

**Mermaid Live Editor** (<https://mermaid.live/>):
- Latest Mermaid version
- Best for testing new syntax before moving to Obsidian
- Features here may not work in Obsidian 11.4.1

**Migration consideration**: if Obsidian upgrades bundled Mermaid to 11.5+ or later, revisit [obsidian-compatibility.md § Migration path](obsidian-compatibility.md).

---

## Quick reference

### Safe numbering methods
- ✅ `1.Text` `①Text` `(1)Text` `Step 1:Text`
- ❌ `1. Text` (space after period)

### Safe subgraph syntax
- ✅ `subgraph id["Name"]` `subgraph simple_name`
- ❌ `subgraph Name With Spaces`

### Safe node references
- ✅ `NodeID --> AnotherID`
- ❌ `"Display Text" --> "Other Text"`

### Safe special characters in text
- ✅ `『』` for quotes, `「」` for parentheses
- ❌ `"` unescaped quotes, `()` in ambiguous contexts
