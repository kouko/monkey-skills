# Pie Chart

Proportion of a whole — market share, survey responses, time allocation.

## When to use

**Best for**:
- Proportion / percentage breakdown of a total (≤6 categories for readability)
- Market share, budget allocation, time spent, survey response distribution
- When the absolute values matter less than the relative ratios

**User query 關鍵字**: pie / pie chart / proportion / 比例 / 圓餅圖 / percentage / distribution / 分布

**Not for**: trends over time (use `data-viz/xychart.md`), >6 categories (legend becomes unreadable — use bar chart), cross-category comparisons (use `data-viz/xychart.md`).

## Canonical syntax

```mermaid
pie title "Market Share Q1 2026"
    "Product A" : 45
    "Product B" : 30
    "Product C" : 15
    "Others" : 10
```

**Minimum required**:
- `pie` directive on line 1
- At least one `"Label" : value` line

Values can be any numeric — Mermaid normalizes to percentages automatically. `45` is interpreted as 45% if the total is 100, or 45/n if the total is n.

## Configuration options

### With / without title

```mermaid
pie title "My Chart"
    "A" : 50
    "B" : 50
```

Or no title:

```mermaid
pie
    "A" : 50
    "B" : 50
```

### Show data on slices

```mermaid
pie showData
    "A" : 40
    "B" : 35
    "C" : 25
```

`showData` adds numeric values on each slice (in addition to the legend).

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — pie is one of Mermaid's oldest / most stable types
- **Known quirks**:
  - Label quoting: strings with spaces or special characters require `"..."` quotes
  - Too many slices (>6) makes the legend hard to read — not a technical limit but a design recommendation
- **Workaround**: none needed

## Quote rule for pie

Pie chart **requires** display labels to be wrapped in `"..."` — this is the canonical form. All examples in this file already follow that convention.

- **Slice labels**: `"Label" : value` (always quoted)
- **Title**: quote if it contains spaces: `pie title "Has Spaces"` — unquoted form `pie title Simple` also works for single-word titles, but quoting for consistency is safe

## Worked examples

### Example 1: Market share

```mermaid
pie title "Market Share 2026 Q1"
    "Acme Corp" : 42
    "BetaCo" : 28
    "Gamma Ltd" : 18
    "Delta Inc" : 8
    "Others" : 4
```

### Example 2: Time allocation (percentage)

```mermaid
pie showData title "Weekly Time Allocation"
    "Deep work" : 45
    "Meetings" : 25
    "Code review" : 15
    "Admin" : 10
    "Interruptions" : 5
```

### Example 3: Survey response distribution

```mermaid
pie title "NPS Response Distribution (n=200)"
    "Promoters (9-10)" : 112
    "Passives (7-8)" : 54
    "Detractors (0-6)" : 34
```

### Example 4: Budget breakdown (dollar amounts)

```mermaid
pie showData title "Q1 Marketing Budget (USD)"
    "Paid ads" : 15000
    "Content" : 8000
    "Events" : 5000
    "Tools" : 2000
```

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| `"Label" 50` (no colon) | `"Label" : 50` | Colon is required separator |
| Unquoted label with spaces | `"Label with spaces" : 50` | Quotes required for multi-word labels |
| Non-numeric value | Use integer or decimal `42` or `42.5` | Values must be numeric |
| >8 slices | Consider merging small categories into "Others" | Legend becomes cluttered |
| `pie title "Has Quotes" extra` | Either drop `extra` or separate | Title line ends at first non-quoted token |

### Pre-save validation

- [ ] `pie` declared on line 1
- [ ] Each data line uses `"Label" : value` format with colon
- [ ] Labels with spaces are quoted
- [ ] Values are numeric
- [ ] ≤6 slices for readability (merge small ones into "Others" if needed)
- [ ] `showData` added if exact values are important to show

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal rules.
