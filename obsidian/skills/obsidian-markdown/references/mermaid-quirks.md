# Mermaid Quirks — Inline Authoring Safety Rules

Distilled from `obsidian-mermaid-visualizer/obsidian-common-quirks.md`.
Read this **before writing any Mermaid block inline** in an Obsidian note.

> **Obsidian bundled Mermaid**: 11.4.1 (as of 2026-04). Features added in v11.5+ will not render.

---

## Rule 1: Line breaks in node labels — `<br/>` not `\n`

`\n` is **not** a valid escape inside Mermaid node text. Use `<br/>`.

```
❌ A["first line\nsecond line"]
✅ A["first line<br/>second line"]
```

Applies to all quoted node labels in flowchart / graph diagrams.

---

## Rule 2: List syntax conflict

`number. space` inside node text triggers a Markdown list parser error.

```
❌ ["1. Perception"]   → Parse error: Unsupported markdown: list
✅ ["1.Perception"]    — no space after period
✅ ["① Perception"]    — circled number
✅ ["(1) Perception"]  — parentheses
✅ ["Step 1: Perception"]
```

---

## Rule 3: Subgraph names with spaces

```
❌ subgraph Core Process
✅ subgraph core["Core Process"]
✅ subgraph core_process
```

When referencing a subgraph elsewhere, always use the **ID** (`core`), never the display name.

---

## Rule 4: Node references — always use IDs

```
A["Display Text A"]
B["Display Text B"]

✅ A --> B               — IDs
❌ Display Text A --> Display Text B   — silent failure: creates unconnected orphan nodes
```

---

## Rule 5: Quote all user-visible display strings

Wrap node labels, arrow labels, and other display text in `"..."`.
CJK text without quotes fails unpredictably.

```
✅ A["処理ステップ"] -->|"条件一致"| B["完了"]
❌ A[処理ステップ] -->|条件一致| B[完了]
```

**Do not quote**: node IDs, keywords (`subgraph`, `end`, `class`), branch names.

---

## Rule 6: Special characters in text

| Character | Problem | Replacement |
|-----------|---------|-------------|
| `"` | Breaks node text | `『』` |
| `()` | Ambiguous with shape syntax | `「」` |
| `#` | Reserved | `&#35;` or spell out |

---

## Rule 7: Multi-node styling — use `classDef`, not comma `style`

```
❌ style A,B,C fill:#d3f9d8     — renders "A,B,C" as an orphan node

✅ classDef green fill:#d3f9d8,stroke:#2f9e44
   class A,B,C green
```

---

## Pre-flight checklist

Before finalising any inline Mermaid block:

- [ ] No `\n` in node labels — replaced with `<br/>`
- [ ] No `number. space` pattern in node text
- [ ] Subgraphs with spaces use `subgraph id["Name"]` format
- [ ] All connections use node IDs, not display text
- [ ] CJK / special-char display strings are quoted
- [ ] Multi-node styling uses `classDef` + `class`
- [ ] No v11.5+ features (`look: neo`, `showDataLabelOutsideBar`, `wardley-beta`)
