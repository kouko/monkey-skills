# Mindmap

Hierarchical concepts, knowledge organization, topic breakdowns, brainstorming.

## When to use

**Best for**:
- Hierarchical concepts with clear parent-child relationships
- Knowledge organization (book outlines, research topics)
- Topic / skill breakdowns
- Brainstorming branches from a central concept

**User query 關鍵字**: mindmap / mind map / 心智圖 / 腦圖 / hierarchy / outline / concept tree / breakdown

**Not for**: cyclic relationships (use `flow/circular-flow.md`), time sequences (use `time/timeline.md`), decision trees with branches-and-merges (use `flow/flowchart.md`).

## Canonical syntax

Mermaid `mindmap` uses indentation-based hierarchy (not arrows). For reliability (especially with CJK text or special characters), wrap node display text in shape markers with quotes: `id(("Text"))`, `id["Text"]`, `id("Text")`.

```mermaid
mindmap
  root(("Central Topic"))
    Branch1["Branch1"]
      Sub1a["Sub1a"]
      Sub1b["Sub1b"]
    Branch2["Branch2"]
      Sub2a["Sub2a"]
        Leaf2a1["Leaf2a1"]
    Branch3["Branch3"]
```

**Note on bare text nodes**: Mermaid mindmap also accepts unquoted bare text as the default rounded shape. However, for CJK content and content with special characters, wrapping in a quoted shape (e.g., `["..."]`) is more reliable and follows the unified quote rule.

## Configuration options

### Node shapes

```mermaid
mindmap
  root(("Circle"))            # Double parens = circle
    Rectangle["Square"]       # Square brackets = rectangle
    Rounded("Rounded")        # Single parens = rounded
    Bang))"Bang"((            # Double parens reversed = bang shape
    Cloud)"Cloud"(            # Single paren reversed = cloud
    Hexagon{{"Hex"}}          # Double braces = hexagon
    Default                   # No brackets = default rounded (unquoted)
```

### Indentation

**Rule**: use consistent spacing (2 or 4 spaces) for each level. Mixing levels of indentation confuses the parser.

```mermaid
mindmap
  root(("Root"))
    Level1a["Level1a"]        # 4 spaces from root
      Level2a["Level2a"]      # 4 spaces deeper
        Level3a["Level3a"]    # 4 more
    Level1b["Level1b"]
```

### Icons (optional, v10.3+)

```mermaid
mindmap
  root(("Research"))
    ::icon(fa fa-book)
    Topic_A["Topic A"]
      ::icon(fa fa-lightbulb)
```

Note: icon rendering depends on FontAwesome availability in Obsidian. May not render in 11.4.1 without additional setup.

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — mindmap is stable since Mermaid 9.3
- **Known quirks**:
  - FontAwesome icons may not render without additional CSS / plugin setup — avoid icons for portable notes
  - Deep nesting (>4 levels) may overflow Obsidian preview pane; keep to 3 levels for readability
  - `<br/>` in node text has inconsistent behavior across shapes
  - Bare (unquoted) text works for simple ASCII but may fail with CJK / special chars — prefer quoted shape wrappers
- **Workaround**: wrap display text in `["..."]` or `(("..."))` for reliability

## Worked examples

### Example 1: Book outline

```mermaid
mindmap
  root(("Book: System Design"))
    Part1["Part 1 Foundations"]
      Scalability["Scalability"]
      Reliability["Reliability"]
      Maintainability["Maintainability"]
    Part2["Part 2 Patterns"]
      Microservices["Microservices"]
      EventSourcing["Event Sourcing"]
      CQRS["CQRS"]
    Part3["Part 3 Case Studies"]
      Uber["Uber"]
      Netflix["Netflix"]
      Discord["Discord"]
```

### Example 2: Research topic breakdown

```mermaid
mindmap
  root(("AI Safety"))
    Alignment["Alignment"]
      ValueLearning["Value learning"]
      RewardHacking["Reward hacking"]
      MesaOpt["Mesa-optimization"]
    Interpretability["Interpretability"]
      Mechanistic["Mechanistic"]
      Probing["Probing"]
      FeatureAttr["Feature attribution"]
    Robustness["Robustness"]
      Adversarial["Adversarial examples"]
      DistShift["Distribution shift"]
      OOD["OOD detection"]
```

### Example 3: Project skill tree

```mermaid
mindmap
  root(("Full-stack Skills"))
    Frontend["Frontend"]
      React["React"]
        Hooks["Hooks"]
        Context["Context"]
      CSS["CSS"]
        Flexbox["Flexbox"]
        Grid["Grid"]
    Backend["Backend"]
      NodeJS["Node.js"]
      Python["Python"]
        FastAPI["FastAPI"]
        Django["Django"]
    DevOps["DevOps"]
      Docker["Docker"]
      CICD["CI/CD"]
```

### Example 4: CJK content (讀書筆記 — 系統設計書)

```mermaid
mindmap
  root(("系統設計入門筆記"))
    Part1["第一部 基礎"]
      Scale["可擴展性"]
      Reliability["可靠性"]
      Maintain["可維護性"]
    Part2["第二部 模式"]
      Micro["微服務"]
      ES["事件溯源"]
      CQRS["CQRS 模式"]
    Part3["第三部 案例"]
      Uber["Uber 架構"]
      Netflix["Netflix 架構"]
      Discord["Discord 架構"]
    Takeaway["關鍵收穫"]
      Trade["權衡取捨"]
      Boundary["邊界設計"]
      Evolution["漸進演化"]
```

Using the quoted shape form `id["..."]` is especially important for CJK content — bare text like `可擴展性` without a shape wrapper may fail to parse reliably. Node IDs stay as ASCII identifiers (`Part1`, `Scale`, etc.) since they are references, not display strings.

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| Mixed indentation (tabs + spaces) | Use only spaces, consistent width | Mermaid parser is strict about indentation levels |
| Unquoted node text with spaces or special chars | Wrap in quoted shape: `id["Text with spaces"]` | Unified quote rule for reliability |
| >5 nesting levels | Keep to ≤3 levels; split into multiple mindmaps if needed | Preview overflow + reader cognitive load |
| Using arrows `-->` inside mindmap | Mindmap uses indentation, not arrows | Wrong diagram type — use flowchart if you need arrows |
| Forgetting `mindmap` keyword | First line must be `mindmap` | Otherwise Mermaid tries to parse as flowchart |

### Mindmap vs flowchart — when to pick which

- **Mindmap**: pure parent-child hierarchy, no cross-links between branches, no specific flow direction
- **Flowchart**: need arrows between items, cross-branch connections, labeled relationships, decision points

If you need both hierarchy AND cross-links, use flowchart with subgraphs — not mindmap.

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal Obsidian Mermaid rules.
