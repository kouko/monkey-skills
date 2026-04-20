# State Diagram

System states, status transitions, lifecycle stages — finite state machines.

## When to use

**Best for**:
- Finite state machines (FSM) with explicit states and transitions
- Lifecycle stages (order: created → paid → shipped → delivered)
- UI states (loading / error / success / idle)
- Protocol states (connecting / connected / disconnected / reconnecting)
- Workflow statuses (draft / review / approved / published)

**User query 關鍵字**: state diagram / FSM / state machine / lifecycle / status / 狀態圖 / 狀態機 / 狀態轉換 / transition

**Not for**: process flows without discrete states (use `flow/flowchart.md`), message timing between actors (use `flow/sequence.md`), hierarchy (use `flow/mindmap.md`).

## Canonical syntax

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Loading: fetch
    Loading --> Success: ok
    Loading --> Error: fail
    Success --> [*]
    Error --> Idle: retry
```

**Use `stateDiagram-v2`**, not the older `stateDiagram`. v2 has better styling and composite state support.

## Configuration options

### Basic transitions

```mermaid
stateDiagram-v2
    [*] --> A          # [*] = start state
    A --> B: event
    B --> [*]          # [*] = end state
```

### Composite (nested) states

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Idle
        Idle --> Processing: start
        Processing --> Idle: done
    }

    Active --> Terminated: shutdown
    Terminated --> [*]
```

### Choice (decision) points

```mermaid
stateDiagram-v2
    [*] --> Input
    Input --> Validate
    Validate --> choice_point <<choice>>
    choice_point --> Accepted: valid
    choice_point --> Rejected: invalid
```

### Fork / join (parallel states)

```mermaid
stateDiagram-v2
    [*] --> fork_state
    fork_state <<fork>>
    fork_state --> StateA
    fork_state --> StateB

    StateA --> join_state
    StateB --> join_state

    join_state <<join>>
    join_state --> [*]
```

### Notes

```mermaid
stateDiagram-v2
    State1 : This is a description
    State2

    note right of State1
        Additional details here
    end note

    State1 --> State2
```

### Direction

```mermaid
stateDiagram-v2
    direction LR       # or TB, BT, RL
    [*] --> A --> B --> [*]
```

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — state diagrams are stable
- **Known quirks**:
  - `stateDiagram` (v1) is deprecated — always use `stateDiagram-v2`
  - Choice / fork / join syntax must be precise; typos cause render failures
  - Composite states nested >2 levels deep can overflow preview pane
- **Workaround**: none needed

## Worked examples

### Example 1: Simple UI state

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Loading: user click
    Loading --> Success: data loaded
    Loading --> Error: network fail
    Success --> Idle: reset
    Error --> Idle: retry
```

### Example 2: Order lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted: submit
    Submitted --> Paid: payment received
    Paid --> Shipped: warehouse dispatch
    Shipped --> Delivered: arrived
    Delivered --> [*]

    Submitted --> Cancelled: user cancels
    Paid --> Refunded: user requests refund
    Cancelled --> [*]
    Refunded --> [*]

    note right of Paid
        Triggers fulfillment workflow
    end note
```

### Example 3: Composite state (nested — connection lifecycle)

```mermaid
stateDiagram-v2
    [*] --> Disconnected

    Disconnected --> Connecting: connect()

    state Connecting {
        [*] --> DNS
        DNS --> Handshake
        Handshake --> Authenticated
        Authenticated --> [*]
    }

    Connecting --> Connected: success
    Connecting --> Failed: error

    Connected --> Disconnected: close()
    Failed --> Disconnected: retry
```

### Example 4: Parallel states (document processing pipeline)

```mermaid
stateDiagram-v2
    [*] --> Upload
    Upload --> fork_state
    fork_state <<fork>>

    fork_state --> Virus_scan
    fork_state --> Extract_text
    fork_state --> Generate_thumbnail

    Virus_scan --> join_state
    Extract_text --> join_state
    Generate_thumbnail --> join_state

    join_state <<join>>
    join_state --> Ready
    Ready --> [*]
```

### Example 5: Choice point (validation branching)

```mermaid
stateDiagram-v2
    [*] --> Submitted
    Submitted --> Validate
    Validate --> decision <<choice>>

    decision --> Accepted: all fields valid
    decision --> NeedsRevision: missing required
    decision --> Rejected: policy violation

    NeedsRevision --> Submitted: user edits
    Accepted --> [*]
    Rejected --> [*]
```

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| `stateDiagram` (v1) | `stateDiagram-v2` | v1 deprecated; v2 has better features |
| `state1 --> state2 : label` (space around colon) | `state1 --> state2: label` (space after only) | Label syntax is strict |
| `[*]` inside nested state to escape | `[*]` only refers to the **containing scope's** start/end | Nested states have their own start/end |
| Choice without `<<choice>>` marker | `decision <<choice>>` required | Otherwise treated as regular state |
| Unbalanced fork/join | Every `<<fork>>` needs a matching `<<join>>` | Syntax error or orphan branches |
| Missing direction on complex diagram | Add `direction LR` or `direction TB` at top | Default TB may not fit lifecycle widths |

### State diagram vs flowchart — when to pick which

- **State diagram**: discrete states with named transitions triggered by events
- **Flowchart**: steps in a process, often sequential, not necessarily "states"

If your question is "what does the system look like at time T?" → state diagram. If "what happens next in the process?" → flowchart.

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal rules.
