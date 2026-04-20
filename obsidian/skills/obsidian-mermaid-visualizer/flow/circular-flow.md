# Circular Flow (graph TD with feedback)

Cyclic processes, continuous improvement loops, iteration-driven systems.

## When to use

**Best for**:
- Cyclic processes (continuous improvement, OODA loops, PDCA)
- Agent feedback systems — action → evaluation → refinement
- Central-hub systems with radiating elements and feedback
- Kaizen / iteration visualizations

**User query 關鍵字**: cyclic / feedback loop / iteration / PDCA / OODA / continuous improvement / 循環 / 反饋 / 迭代

**Not for**: one-way sequential flow (use `flow/flowchart.md`), state machines with discrete transitions (use `flow/state.md`).

## Canonical syntax

Circular flow is a **variant of flowchart** — uses `graph TD/TB` with explicit feedback arrows (`-.->`) that close the loop.

```mermaid
graph TD
    A[Plan] --> B[Do]
    B --> C[Check]
    C --> D[Act]
    D -.->|feedback| A
```

## Configuration options

Inherits all flowchart options (see [flowchart.md § Configuration options](flowchart.md)):
- Layout direction (TD recommended for circular)
- Node shapes
- Arrow types — **dashed feedback arrow `-.->` is the signature of circular flow**
- Styling

**Circular-specific tip**: use `-.->` (dashed) for feedback arrows to visually distinguish the loop-closing edge from forward flow.

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — built on flowchart which is the most stable type
- **Known quirks**: same as flowchart (see [flowchart.md § Obsidian compatibility](flowchart.md))
- **Workaround**: none needed

## Worked examples

### Example 1: PDCA (Plan-Do-Check-Act) cycle

```mermaid
graph TD
    P[Plan] --> D[Do]
    D --> C[Check]
    C --> A[Act]
    A -.->|next cycle| P

    style P fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px
    style D fill:#e5dbff,stroke:#5f3dc4,stroke-width:2px
    style C fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px
    style A fill:#fff4e6,stroke:#e67700,stroke-width:2px
```

### Example 2: Agent feedback loop

```mermaid
graph TB
    Input[User Query] --> Perceive[Perceive]
    Perceive --> Act[Act]
    Act --> Evaluate[Evaluate Outcome]
    Evaluate -.->|adjust strategy| Perceive
    Evaluate --> Response[Response]

    style Input fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px
    style Response fill:#c5f6fa,stroke:#0c8599,stroke-width:2px
    style Evaluate fill:#f3d9fa,stroke:#862e9c,stroke-width:2px
```

### Example 3: OODA loop (Observe-Orient-Decide-Act)

```mermaid
graph TD
    O1[Observe] --> O2[Orient]
    O2 --> D[Decide]
    D --> A[Act]
    A -.->|new information| O1

    style O1 fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px
    style O2 fill:#e5dbff,stroke:#5f3dc4,stroke-width:2px
    style D fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px
    style A fill:#fff4e6,stroke:#e67700,stroke-width:2px
```

## Error prevention

Circular flow inherits flowchart's error prevention. Specific additions:

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| Using `-->` for feedback edge | Use `-.->` for feedback | Distinguishes forward flow from loop-closing edge visually |
| Loop with >6 stages | Split into nested loops or sequential diagrams | Long circular loops become hard to read |
| Unclear which node is the cycle start | Add label text or annotation arrow showing entry point | Circular diagrams are ambiguous about "start" |
| Missing feedback arrow | Must have at least one arrow closing the loop | Otherwise it's a linear flowchart, not circular |

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal Obsidian Mermaid rules.
