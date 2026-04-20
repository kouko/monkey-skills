# Gantt Chart

Project schedule — tasks, durations, dependencies, milestones, critical path.

## When to use

**Best for**:
- Project timelines with tasks and dependencies
- Sprint / release planning
- Multi-phase roadmaps with dates
- Team workload allocation over time
- Critical path analysis

**User query 關鍵字**: gantt / gantt chart / 甘特圖 / project schedule / timeline / project plan / roadmap / 專案時程 / 排程

**Not for**: chronology without dependencies (use `time/timeline.md`), sequential process steps (use `flow/flowchart.md`), simple task lists (use Markdown).

## Canonical syntax

```mermaid
gantt
    title Project Roadmap Q1 2026
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m-%d

    section Planning
    Research        :done, research, 2026-01-01, 5d
    Design          :done, design, after research, 10d

    section Development
    Backend API     :active, api, 2026-01-20, 14d
    Frontend UI     :ui, after api, 14d
    Integration     :integ, after ui, 5d

    section Launch
    Testing         :test, after integ, 7d
    Deploy          :milestone, deploy, after test, 0d
```

**Minimum required**:
- `gantt` directive
- `dateFormat` for parsing dates
- At least one task with start + duration

## Configuration options

### Date format

```mermaid
dateFormat YYYY-MM-DD                # Default ISO
dateFormat DD-MM-YYYY                # European
dateFormat HH:mm                     # Hour-based (short projects)
```

### Axis format (display format)

```mermaid
axisFormat %Y-%m-%d                  # ISO date
axisFormat %m/%d                     # Short
axisFormat %d %b                     # Day + month name (e.g., "15 Jan")
```

### Task declaration

```mermaid
TaskName :status, task_id, start_spec, duration_or_end
```

**Status options** (in order of declaration):
- `done` — completed
- `active` — in progress (highlighted)
- `crit` — critical path (red)
- `milestone` — point-in-time, duration 0

Multiple statuses: `:done, crit` (completed but was critical).

**Start spec**:
- Explicit date: `2026-01-15`
- After another task: `after task_id`
- After multiple: `after task_a task_b` (takes latest end)

**Duration**:
- Days: `7d`
- Weeks: `2w`
- Hours: `4h` (for hourly projects)
- Explicit end date: `until 2026-02-15`

### Sections (grouping)

```mermaid
section Group Name
    TaskA :task_a, 2026-01-01, 5d
    TaskB :task_b, after task_a, 3d

section Another Group
    TaskC :task_c, 2026-01-10, 7d
```

### Milestones (point events)

```mermaid
TaskName :milestone, id, date_or_after, 0d
```

Duration must be `0d` for milestones to render as diamond markers.

### Task dependencies via `after`

```mermaid
TaskA :a, 2026-01-01, 5d
TaskB :b, after a, 3d                # B starts when A ends
TaskC :c, after a b, 4d              # C starts when BOTH A and B end
```

### Today marker

```mermaid
gantt
    title Schedule
    dateFormat YYYY-MM-DD
    todayMarker on          # or "off" to hide
```

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — Gantt is one of Mermaid's oldest diagrams
- **Known quirks**:
  - Very long task names may truncate — keep to 20-30 chars
  - Too many tasks (>30) make the chart cramped — split by section or timeframe
  - Today marker position depends on user's system date when viewing
  - Sections with no tasks may render as empty rows
- **Workaround**: none needed

## Worked examples

### Example 1: Simple 2-month project

```mermaid
gantt
    title Website Launch Plan
    dateFormat YYYY-MM-DD

    section Planning
    Requirements     :done, req, 2026-01-01, 7d
    Design mockups   :done, design, after req, 10d

    section Development
    Backend API      :active, api, 2026-01-18, 20d
    Frontend build   :fe, after api, 15d

    section Launch
    QA testing       :qa, after fe, 7d
    Soft launch      :milestone, launch, after qa, 0d
```

### Example 2: With critical path

```mermaid
gantt
    title Sprint 3 — Feature Release
    dateFormat YYYY-MM-DD

    section Must-have
    Auth redesign        :crit, active, auth, 2026-02-01, 10d
    Payment integration  :crit, pay, after auth, 8d
    Final QA             :crit, qa, after pay, 5d

    section Nice-to-have
    Analytics upgrade    :ana, 2026-02-05, 12d
    Docs rewrite         :docs, 2026-02-10, 15d
```

### Example 3: Quarterly roadmap

```mermaid
gantt
    title 2026 Q1-Q2 Product Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section Q1
    Dark mode             :done, darkmode, 2026-01-01, 30d
    Mobile app v2         :active, mobile, 2026-01-15, 45d
    Search improvements   :search, 2026-02-01, 20d

    section Q2
    API v3                :api3, after search, 60d
    Team collab features  :collab, 2026-04-15, 45d
    Q2 launch             :milestone, q2launch, 2026-06-30, 0d
```

### Example 4: Dependencies and parallel tracks

```mermaid
gantt
    title Multi-team Delivery
    dateFormat YYYY-MM-DD

    section Backend Team
    DB migration     :db, 2026-01-01, 5d
    API rewrite      :api, after db, 15d
    API tests        :apitest, after api, 5d

    section Frontend Team
    Mockups          :mock, 2026-01-01, 7d
    UI build         :ui, after mock, 14d

    section Joint
    Integration      :integ, after apitest ui, 7d
    Release          :milestone, release, after integ, 0d
```

Note: `after apitest ui` — integration waits for BOTH.

### Example 5: Weekly sprint (hour granularity)

```mermaid
gantt
    title Sprint Week — Detailed View
    dateFormat YYYY-MM-DD HH:mm
    axisFormat %a %H:%M

    section Mon
    Stand-up          :monstand, 2026-01-05 09:00, 15m
    Design review     :monrev, after monstand, 1h

    section Tue
    Pair programming  :pair, 2026-01-06 10:00, 3h
    Code review       :review, after pair, 1h

    section Wed
    Sprint demo       :demo, 2026-01-07 14:00, 2h
    Retro             :retro, after demo, 1h
```

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| Missing `dateFormat` | `dateFormat YYYY-MM-DD` on line 2 | Without it, dates can't be parsed |
| Task ID with spaces | Use underscore or camelCase: `backend_api` / `backendApi` | IDs must be single tokens |
| Duration `7 days` (with word) | `7d` (letter code) | Use d/w/h/m suffix |
| `after task1, task2` (with comma) | `after task1 task2` (space-separated) | Multi-dependency uses space |
| Milestone with duration >0 | `:milestone, id, date, 0d` | Milestones must be 0 duration |
| Conflicting statuses | Status order matters: `done, crit` is valid; `crit, done` may parse differently | Put completion status first |

### Pre-save validation

- [ ] `gantt` declared on line 1
- [ ] `dateFormat` specified on line 2 (or near top)
- [ ] All tasks have format `Name :status, id, start, duration`
- [ ] Task IDs are single-token (no spaces)
- [ ] Durations use letter codes: `d`, `w`, `h`, `m`
- [ ] Milestones have `0d` duration
- [ ] `after taskA taskB` for multi-dependency (spaces, no commas)
- [ ] Task count ≤ 30 for readability

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal rules.
