# Comparison Diagram (graph TB with parallel paths)

Side-by-side A vs B comparison, traditional vs modern analysis, option analysis.

## When to use

**Best for**:
- Before/after comparisons
- A vs B analysis (two products, two approaches)
- Traditional vs modern system comparison
- Option evaluation with shared decision criteria

**User query 關鍵字**: comparison / compare / A vs B / 比較 / 對比 / 差異 / contrast

**Not for**: 2×2 positioning (use `data-viz/quadrant.md`), hierarchical concepts (use `flow/mindmap.md`), more than 3 items (use a table or separate diagrams).

## Canonical syntax

Comparison is a **flowchart pattern** — uses `graph TB` with parallel subgraphs and a shared title or comparison node.

```mermaid
graph TB
    Title["Comparison"]

    subgraph left["System A"]
        A1["Feature 1"]
        A2["Feature 2"]
    end

    subgraph right["System B"]
        B1["Feature 1"]
        B2["Feature 2"]
    end

    Title --> left
    Title --> right
```

## Configuration options

Inherits flowchart options. Key variations for comparison:

- **Layout**: TB with parallel subgraphs (default) OR LR for wide comparisons
- **Styling contrast**: differentiate the two sides with contrasting colors (e.g., gray = traditional, blue = modern)
- **Shared criteria**: use a "Key Differences" subgraph below to show summary

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — uses standard flowchart syntax
- **Known quirks**: same as flowchart
- **Workaround**: none needed

## Worked examples

### Example 1: Traditional vs modern system

```mermaid
graph TB
    Title["Architecture Comparison"]

    subgraph traditional["Traditional"]
        T1["Monolithic App"]
        T2["Single Database"]
        T3["Vertical Scaling"]
    end

    subgraph modern["Modern"]
        M1["Microservices"]
        M2["Distributed DB"]
        M3["Horizontal Scaling"]
    end

    Title --> traditional
    Title --> modern

    subgraph diff["Key Differences"]
        D1["Coupling / Deployment / Cost model"]
    end

    traditional --> diff
    modern --> diff

    style traditional fill:#f8f9fa,stroke:#868e96,stroke-width:2px
    style modern fill:#e7f5ff,stroke:#1971c2,stroke-width:2px
    style diff fill:#fff4e6,stroke:#e67700,stroke-width:2px
```

### Example 2: Before/after process

```mermaid
graph LR
    subgraph before["Before: Manual Review"]
        B1["Submit"] --> B2["Wait 3 days"] --> B3["Email feedback"]
    end

    subgraph after["After: Automated Pipeline"]
        A1["Submit"] --> A2["CI runs tests"] --> A3["Inline feedback"]
    end

    before --> Result["Comparison Outcome"]
    after --> Result

    style before fill:#f8f9fa,stroke:#868e96,stroke-width:2px
    style after fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px
```

### Example 3: A vs B with shared criteria

```mermaid
graph TB
    subgraph criteria["Evaluation Criteria"]
        C1["Speed"]
        C2["Cost"]
        C3["Maintainability"]
    end

    subgraph optionA["Option A: Library X"]
        A1["Fast"]
        A2["Free"]
        A3["Low maintenance"]
    end

    subgraph optionB["Option B: Library Y"]
        B1["Slow"]
        B2["Paid"]
        B3["High maintenance"]
    end

    criteria --> optionA
    criteria --> optionB

    style optionA fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px
    style optionB fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px
```

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| Mixing 3+ options into one diagram | Use tables or multiple comparison diagrams | Comparison layout gets cluttered >2-3 options |
| No visual distinction between sides | Use contrasting fill colors (e.g., gray vs blue) | Reader can't parse comparison without visual cue |
| Subgraphs at different depths on each side | Keep parallel structure identical (same node count, same nesting) | Asymmetry implies the comparison isn't fair |
| Using circular feedback arrows | Comparison is static, not cyclic — use flow arrows only | Feedback arrows confuse the comparison semantic |
| Unquoted display text: `A[Feature]` | `A["Feature"]` | Unified quote rule for display strings |

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal rules.
