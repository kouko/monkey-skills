---
name: obsidian-canvas-creator
description: Create Obsidian Canvas files with MindMap or freeform layouts. Use when visualizing content spatially, creating mind maps, or organizing information on a canvas. Canvas・マインドマップ。心智圖・畫布。
---

# Obsidian Canvas Creator

Transform text content into structured Obsidian Canvas files with support for MindMap and freeform layouts.

## When to Use This Skill

- User requests to create a canvas, mind map, or visual diagram from text
- User wants to organize information spatially
- User mentions "Obsidian Canvas" or similar visualization tools
- Converting structured content (articles, notes, outlines) into visual format

## Core Workflow

### 1. Analyze Content

Read and understand the input content:
- Identify main topics and hierarchical relationships
- Extract key points, facts, and supporting details
- Note any existing structure (headings, lists, sections)

### 2. Determine Layout Type

Ask user to choose or infer from context:

**MindMap Layout:**
- Radial structure from center
- Parent-child relationships
- Clear hierarchy
- Good for: brainstorming, topic exploration, hierarchical content

**Freeform Layout:**
- Custom positioning
- Flexible relationships
- Multiple connection types
- Good for: complex networks, non-hierarchical content, custom arrangements

### 3. Plan Structure

**For MindMap:**
- Identify central concept (root node)
- Map primary branches (main topics)
- Organize secondary branches (subtopics)
- Position leaf nodes (details)

**For Freeform:**
- Group related concepts
- Identify connection patterns
- Plan spatial zones
- Consider visual flow

### 4. Generate Canvas

Create JSON following the Canvas specification:

**Node Creation:**
- Assign unique 16-character lowercase hex IDs
- Set appropriate dimensions based on content length
- Apply consistent color schemes
- Ensure no coordinate overlaps

**Edge Creation:**
- Connect parent-child relationships
- Use appropriate arrow styles
- Add labels for complex relationships
- Choose line styles (straight for hierarchy, curved for cross-references)

**Grouping (Optional):**
- Create visual containers for related nodes
- Use subtle background colors
- Add descriptive labels

### 5. Apply Layout Algorithm

**MindMap Layout Calculations:**

Refer to `references/layout-algorithms.md` for detailed algorithms. Key principles:

- Center root at (0, 0)
- Distribute primary nodes radially
- Space secondary nodes based on sibling count
- Maintain minimum spacing: 320px horizontal, 200px vertical

**Freeform Layout Principles:**

- Start with logical groupings
- Position groups with clear separation
- Connect across groups with curved edges
- Balance visual weight across canvas

### 6. Validate and Output

Before outputting:

**Validation Checklist:**
- All nodes have unique IDs
- No coordinate overlaps (check distance > node dimensions + spacing)
- All edges reference valid node IDs
- Groups (if any) have labels
- Colors use consistent format (hex or preset numbers)
- JSON is properly escaped (Chinese quotes: 『』 for double, 「」 for single)

**Output Format:**
- Complete, valid JSON Canvas file
- No additional explanation text
- Directly importable into Obsidian

## Editing Existing Canvases

### Add a Node to an Existing Canvas

1. Read and parse the existing `.canvas` file
2. Generate a unique 16-char hex ID that does not collide with existing node or edge IDs
3. Choose position (`x`, `y`) that avoids overlapping existing nodes (leave 50-100px spacing)
4. Append the new node object to the `nodes` array
5. Optionally add edges connecting the new node to existing nodes
6. **Validate**: Confirm all IDs are unique and all edge references resolve to existing nodes

### Connect Two Existing Nodes

1. Identify the source and target node IDs
2. Generate a unique 16-char hex edge ID
3. Set `fromNode` and `toNode` to the source and target IDs
4. Optionally set `fromSide`/`toSide` (`top`, `right`, `bottom`, `left`) for anchor points
5. Optionally set `label` for descriptive text on the edge
6. Append the edge to the `edges` array
7. **Validate**: Confirm both `fromNode` and `toNode` reference existing node IDs

### Edit Canvas Content

1. Read and parse the `.canvas` file as JSON
2. Locate the target node or edge by `id`
3. Modify the desired attributes (text, position, color, etc.)
4. Write the updated JSON back to the file
5. **Validate**: Re-check all ID uniqueness and edge reference integrity after editing

## Node Sizing Guidelines

**By Text Length:**
- Short text (<30 chars): 220 × 100 px
- Medium text (30-60 chars): 260 × 120 px  
- Long text (60-100 chars): 320 × 140 px
- Very long text (>100 chars): 320 × 180 px

**By Node Type:**

| Node Type | Suggested Width | Suggested Height |
|-----------|-----------------|------------------|
| Small text | 200-300 | 80-150 |
| Medium text | 300-450 | 150-300 |
| Large text | 400-600 | 300-500 |
| File preview | 300-500 | 200-400 |
| Link preview | 250-400 | 100-200 |

## Color Schemes

**Preset Colors (Recommended):**
- `"1"` - Red (warnings, important)
- `"2"` - Orange (action items)
- `"3"` - Yellow (questions, notes)
- `"4"` - Green (positive, completed)
- `"5"` - Cyan (information, details)
- `"6"` - Purple (concepts, abstract)

**Custom Hex Colors:**
Use for brand consistency or specific themes. Always use uppercase format: `"#4A90E2"`

## Critical Rules

1. **Quote Handling:**
   - Chinese double quotes → 『』
   - Chinese single quotes → 「」
   - English double quotes → `\"`

2. **Newline Handling:**
   - Use `\n` for line breaks in JSON strings
   - Do **not** use the literal `\\n` — Obsidian renders that as the characters `\` and `n`

3. **ID Generation:**
   - 16-character lowercase hexadecimal strings (e.g., `6f0ad84f44ce9c17`)
   - Must be unique across all nodes and edges

4. **Z-Index Order:**
   - Output groups first (bottom layer)
   - Then subgroups
   - Finally text/link nodes (top layer)

5. **Spacing Requirements:**
   - Minimum horizontal: 320px between node centers
   - Minimum vertical: 200px between node centers
   - Account for node dimensions when calculating

6. **JSON Structure:**
   - Top level contains only `nodes` and `edges` arrays
   - No extra wrapping objects
   - No comments in output

7. **No Emoji:**
   - Do not use any Emoji symbols in node text
   - Use color coding or text labels for visual distinction instead

## Examples

### Simple MindMap Request
User: "Create a mind map about solar system planets"

Process:
1. Identify center: "Solar System"
2. Primary branches: Inner Planets, Outer Planets, Dwarf Planets
3. Secondary nodes: Individual planets with key facts
4. Apply radial layout
5. Generate JSON with proper spacing

### Freeform Content Request
User: "Turn this article into a canvas" + [article text]

Process:
1. Extract article structure (intro, body sections, conclusion)
2. Identify key concepts and relationships
3. Group related sections spatially
4. Connect with labeled edges
5. Apply freeform layout with clear zones

## Reference Documents

- **Canvas Specification**: `references/canvas-spec.md` - Complete JSON Canvas format specification
- **Layout Algorithms**: `references/layout-algorithms.md` - Detailed positioning algorithms for both layout types
- **Complete Examples**: `references/EXAMPLES.md` - Full canvas examples (mind maps, project boards, research canvases, flowcharts)
- **JSON Canvas Spec 1.0**: https://jsoncanvas.org/spec/1.0/ — Official specification
- **JSON Canvas GitHub**: https://github.com/obsidianmd/jsoncanvas

Load these references when:
- Need specification details for edge cases
- Implementing complex layout calculations
- Troubleshooting validation errors

## Tips for Quality Canvases

1. **Keep text concise**: Each node should be scannable (<2 lines preferred)
2. **Use hierarchy**: Group by importance and relationship
3. **Balance the canvas**: Distribute nodes to avoid clustering
4. **Strategic colors**: Use colors to encode meaning, not just decoration
5. **Meaningful connections**: Only add edges that clarify relationships
6. **Test in Obsidian**: Verify the output opens correctly

## Common Pitfalls to Avoid

- Overlapping nodes (always check distances)
- Inconsistent quote escaping (breaks JSON parsing)
- Missing group labels (causes sidebar navigation issues)
- Too much text in nodes (use file nodes for long content)
- Duplicate IDs (each must be unique)
- Unconnected nodes (unless intentional islands)
