# Quadrant Chart (quadrantChart)

2×2 positioning analysis — Eisenhower matrix, risk/reward, impact/effort, BCG matrix.

## When to use

**Best for**:
- 2×2 strategic matrices (Eisenhower urgent/important, Ansoff matrix, BCG matrix)
- Impact / effort prioritization
- Risk / reward positioning
- Importance / urgency task classification
- Any two-axis continuous positioning with named quadrants

**User query 關鍵字**: quadrant / 2x2 matrix / Eisenhower / impact effort / risk reward / priority matrix / 象限 / 矩陣 / 優先度

**Not for**: single-axis ranking (use `data-viz/xychart.md`), >2 axes (use a table or multiple charts), discrete non-positional items (use `flow/mindmap.md`).

## Canonical syntax

```mermaid
quadrantChart
    title Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Quick Wins
    quadrant-2 Major Projects
    quadrant-3 Fill-ins
    quadrant-4 Thankless Tasks
    "Task A": [0.2, 0.8]
    "Task B": [0.7, 0.7]
    "Task C": [0.3, 0.3]
    "Task D": [0.8, 0.4]
```

**Minimum required**:
- `quadrantChart` directive
- `x-axis LEFT --> RIGHT` and `y-axis BOTTOM --> TOP` labels
- At least one data point `"Name": [x, y]`

**Coordinate system**: 0,0 = bottom-left corner; 1,1 = top-right corner. All values normalized 0–1.

**Quadrant numbering**: Mermaid's convention places `quadrant-1` in top-right (high-x, high-y), clockwise:
- `quadrant-1`: top-right (High x, High y)
- `quadrant-2`: top-left (Low x, High y)
- `quadrant-3`: bottom-left (Low x, Low y)
- `quadrant-4`: bottom-right (High x, Low y)

## Configuration options

### Without quadrant labels

```mermaid
quadrantChart
    title Simple Positioning
    x-axis Low --> High
    y-axis Low --> High
    "Item A": [0.3, 0.7]
    "Item B": [0.8, 0.5]
```

Quadrant labels are optional; if omitted the 4 regions are unlabeled (still visually divided).

### Custom styling (Mermaid init block)

```mermaid
%%{init: {'quadrantChart': {'chartWidth': 600, 'chartHeight': 600}}}%%
quadrantChart
    ...
```

Width / height customization. Not all init options work reliably in Obsidian 11.4.1; test before relying.

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — quadrantChart added in v10.6, stable
- **Known quirks**:
  - Point labels overlapping when points are close together — spread coordinates manually
  - Long quadrant labels may get truncated — use concise phrasing (2-3 words)
- **Workaround**: none needed for standard use

## Quote rule for quadrant

Mixed quoting convention — only **data points** take quoted labels; axis / title / quadrant labels are unquoted free-form text (quoting them causes the quotes to render literally):

- **Data points** (always quote): `"Name": [x, y]` ✅
- **Title** (unquoted, free-form): `title Priority Matrix` ✅ — do NOT quote
- **Axis labels** (unquoted, free-form): `x-axis Low Effort --> High Effort` ✅ — do NOT quote
- **Quadrant labels** (unquoted, free-form): `quadrant-1 Quick Wins` ✅ — do NOT quote

This is the opposite of `xychart-beta` where title and axis names ARE quoted. The divergence is intentional per each diagram type's parser. Quadrant data-point labels follow the unified quote rule because they are the user-visible items whose quoting is required for spaces and CJK.

## Worked examples

### Example 1: Eisenhower matrix (urgent × important)

```mermaid
quadrantChart
    title Eisenhower Matrix — Task Prioritization
    x-axis Not Urgent --> Urgent
    y-axis Not Important --> Important
    quadrant-1 Do First
    quadrant-2 Schedule
    quadrant-3 Delegate
    quadrant-4 Eliminate
    "Fix production bug": [0.9, 0.9]
    "Write quarterly plan": [0.2, 0.9]
    "Answer non-urgent email": [0.7, 0.2]
    "Organize old files": [0.1, 0.2]
```

### Example 2: Impact / effort prioritization

```mermaid
quadrantChart
    title Feature Prioritization
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Major Projects
    quadrant-2 Quick Wins
    quadrant-3 Fill-ins
    quadrant-4 Money Pits
    "Dark mode": [0.3, 0.6]
    "Real-time collab": [0.9, 0.9]
    "Update docs": [0.2, 0.3]
    "Blockchain integration": [0.8, 0.2]
    "Keyboard shortcuts": [0.2, 0.8]
```

### Example 3: Risk / reward assessment

```mermaid
quadrantChart
    title Investment Risk vs Reward
    x-axis Low Risk --> High Risk
    y-axis Low Reward --> High Reward
    quadrant-1 High Reward / High Risk
    quadrant-2 Sweet Spot
    quadrant-3 Avoid
    quadrant-4 Avoid
    "Blue-chip stocks": [0.3, 0.6]
    "Emerging markets": [0.7, 0.8]
    "Government bonds": [0.15, 0.3]
    "Crypto altcoins": [0.95, 0.75]
    "Real estate": [0.4, 0.55]
```

### Example 4: BCG matrix (market share × growth)

```mermaid
quadrantChart
    title BCG Matrix — Product Portfolio
    x-axis Low Market Share --> High Market Share
    y-axis Low Growth --> High Growth
    quadrant-1 Stars
    quadrant-2 Question Marks
    quadrant-3 Dogs
    quadrant-4 Cash Cows
    "Product A": [0.85, 0.85]
    "Product B": [0.25, 0.75]
    "Product C": [0.8, 0.2]
    "Product D": [0.15, 0.2]
```

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| `x-axis "Low" to "High"` | `x-axis Low --> High` | Must use `-->` arrow, not `to` |
| Point `"Name" (0.5, 0.5)` | `"Name": [0.5, 0.5]` | Colon + square brackets required |
| Coordinate outside `[0, 1]` range | Normalize to 0–1 scale | Values outside this range won't render |
| Mixing quadrant-N with skipping numbers | Define all 4 or none (for labeled quadrants) | Partial definitions may render inconsistently |
| Confusing quadrant numbering (thinking counter-clockwise from top-left) | Quadrant 1 is top-RIGHT; clockwise: top-right → top-left → bottom-left → bottom-right | Common mistake — verify against Mermaid docs |

### Pre-save validation

- [ ] `quadrantChart` declared on line 1
- [ ] x-axis and y-axis both defined with `-->` syntax
- [ ] All data points use `"Name": [x, y]` with coordinates in `[0, 1]` range
- [ ] Quadrant labels either all 4 defined or all 4 omitted (avoid partial)
- [ ] Quadrant labels ≤ 3 words to prevent truncation
- [ ] Point names quoted if contain spaces

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal rules.
