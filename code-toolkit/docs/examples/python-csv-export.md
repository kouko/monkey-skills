# Worked example — Python: add CSV export to existing report endpoint

> **Stack**: Python 3.11 + FastAPI + SQLAlchemy + pytest
> **Persona**: data analyst maintaining an internal reporting service
> **Task complexity**: ~2 hours, touches 1-2 modules → SDD applies
> **Demonstrates**: full code-toolkit flow from brainstorming through finish-branch
> **Skills exercised**: `using-code-toolkit` → `brainstorming` → `writing-plans` → `subagent-driven-development` (with implementer + spec-reviewer + code-quality-reviewer triad) → `tdd-iron-law` → `requesting-code-review` → `verification-before-completion` → `finishing-a-development-branch`

## The user's initial prompt

```
We have a /reports/:id endpoint that returns JSON. Internal users
keep asking for the same data as CSV for Excel ingestion. Add CSV
export support.
```

---

## Stage 1 — `brainstorming` (Discovery)

Router auto-routes to `brainstorming` (Stage 1). Agent walks the 5-axis framework BEFORE jumping to implementation. The brief lands at `docs/code-toolkit/specs/2026-05-16-csv-export.md`:

```markdown
# Brief: CSV export for /reports/:id

## Problem (Axis 1 — JTBD)
When internal data analysts review report X, I want to load it into
Excel for pivot-tables / further analysis, so I can answer ad-hoc
questions without re-running SQL.

## Users (Axis 2)
Internal data analysts (~5 people). Current workaround: copy-paste
JSON output into Sheets and reshape manually (10-15 min per report).
They live in Excel; they will NOT install desktop tools or use a
data viz library.

## Smallest End State (Axis 3)
Add `?format=csv` query param to the existing `/reports/:id` GET.
When set, return same data as RFC 4180 CSV with `Content-Type:
text/csv; charset=utf-8`. No UI change. No new endpoint. No new
table. Existing JSON path unchanged.

## Decision
Build the query-param approach. Backend only; one file modified
(routes/reports.py) + one new file (renderers/csv.py).

## Out of Scope
- Streaming for large reports (current largest is 50K rows; CSV
  generation in-memory is fine; revisit if reports grow beyond 1M)
- CSV-specific column ordering / formatting (use JSON field order)
- XLSX support (CSV solves the Excel use case; XLSX adds complexity
  without proportional value)
- Authentication changes (existing JWT auth applies as-is)

## Alternatives Considered
1. New /reports/:id.csv endpoint — rejected: duplicates auth + ACL
   logic; query-param keeps single source of behavior.
2. Server-side Excel pivot (return XLSX with formulas) — rejected:
   spec is "load into Excel"; the analyst's pivots are interactive,
   not server-generated.
3. Do nothing; document JSON-to-CSV manual procedure — rejected:
   ~10 hours/month of analyst time wasted, recurring.

## What Becomes Obsolete
- The internal wiki page "Manually exporting report data to CSV"
  (delete in same PR).

## Open Questions
(none — brief is complete)
```

**Agent halts here**: brief written, asks user to approve before proceeding to plan-writing. *"Brief at `docs/code-toolkit/specs/2026-05-16-csv-export.md`. Confirm scope before I invoke writing-plans?"*

User confirms.

---

## Stage 2 — `writing-plans` (Planning)

Router routes to `writing-plans`. Reads the brief, produces atomic plan at `docs/code-toolkit/plans/2026-05-16-csv-export.md`:

```markdown
# Plan: CSV export query param

**Source brief**: docs/code-toolkit/specs/2026-05-16-csv-export.md
**Total tasks**: 3 (≤5 ✓)
**Execution order**: parallel-where-possible (Tasks 1 + 2 parallel; Task 3 joins)
**Plan-document-reviewer verdict**: PASS (2026-05-16, 12/12 checks)

## Task 1 — Add ?format= query param parsing to /reports handler

- **Description**: Accept `format=csv` query param in `GET /reports/:id`;
  default to `format=json` if absent. Pass parsed value to render dispatch.
- **Module**: `src/routes/reports.py`
- **Context paths**:
  - `/Users/analyst/proj/src/routes/reports.py`
  - `/Users/analyst/proj/tests/routes/test_reports.py`
- **Acceptance**:
  - **RED**: `test_reports.py::test_format_param_parsed` — fails because handler doesn't accept `format`
  - **GREEN**: param parsed; unknown values return 400; default `json` path unchanged
- **Dependencies**: none
- **Brief item covered**: Smallest End State — "Add `?format=csv` query param"

## Task 2 — Implement CSV renderer

- **Description**: New file `src/renderers/csv.py` exporting `render_csv(payload: dict) -> str`. RFC 4180 compliant: quote fields containing commas / quotes / newlines.
- **Module**: `src/renderers/csv.py`
- **Context paths**:
  - `/Users/analyst/proj/src/types/report_payload.py`
- **Acceptance**:
  - **RED**: `test_csv_renderer.py::test_quote_special_chars` — fails because renderer doesn't exist
  - **GREEN**: special chars quoted per RFC 4180; round-trip via csv.reader succeeds
- **Dependencies**: none (parallel with Task 1)
- **Brief item covered**: Smallest End State — "RFC 4180 CSV output"

## Task 3 — Wire renderer into handler + set Content-Type

- **Description**: When `format=csv`, call `render_csv(payload)`, set `Content-Type: text/csv; charset=utf-8`, return CSV body.
- **Module**: `src/routes/reports.py`
- **Context paths**:
  - `/Users/analyst/proj/src/routes/reports.py` (modified by Task 1)
  - `/Users/analyst/proj/src/renderers/csv.py` (produced by Task 2)
- **Acceptance**:
  - **RED**: `test_reports.py::test_csv_format_returns_csv` — fails (no CSV handling yet)
  - **GREEN**: end-to-end request returns valid CSV body; Content-Type header correct
- **Dependencies**: Tasks 1, 2 complete first
- **Brief item covered**: Smallest End State — "end-to-end CSV download path"

## Notes

SDD-friendly dispatch order: `[Task 1, Task 2 in parallel] → [Task 3]`.

**Out of Scope reminder** (per brief): streaming, XLSX, column reordering, auth — all deferred to future briefs if needed.
```

---

## Stage 3 — `subagent-driven-development` (Execution)

SDD dispatches 3 subagents per task (implementer + spec-reviewer + code-quality-reviewer). For brevity, this example shows **Task 2 (CSV renderer)** in detail.

### Task 2 implementer dispatch

Implementer subagent receives the prompt (see `skills/subagent-driven-development/agents/implementer-prompt.md` template) with:
- Task description (from plan)
- Context paths (existing files to read)
- Resource paths (7 standards + tdd-iron-law)

**Implementer's `tdd-iron-law` flow** (Stage 4 — Discipline, fires INSIDE implementer):

```python
# Step 1 — RED: write the failing test FIRST
# tests/renderers/test_csv_renderer.py
def test_quote_special_chars():
    from src.renderers.csv import render_csv
    payload = {"rows": [
        {"name": "Smith, Jr.", "comment": 'Said "hi"', "notes": "line1\nline2"},
    ]}
    result = render_csv(payload)
    # RFC 4180: comma → quote field; quote → double quote inside quoted field
    assert '"Smith, Jr."' in result
    assert '"Said ""hi"""' in result
    # Newline → must be inside quoted field
    assert '"line1\nline2"' in result

# Run: pytest tests/renderers/test_csv_renderer.py
# Output: ModuleNotFoundError: No module named 'src.renderers.csv'
# ✓ RED confirmed
```

```python
# Step 2 — GREEN: simplest code to make it pass
# src/renderers/csv.py
import csv
from io import StringIO

def render_csv(payload: dict) -> str:
    rows = payload.get("rows", [])
    if not rows:
        return ""
    fieldnames = list(rows[0].keys())
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()

# Run: pytest tests/renderers/test_csv_renderer.py
# Output: PASSED
# ✓ GREEN
```

```python
# Step 3 — REFACTOR: improve internal structure (no behavior change)
# Extract fieldnames derivation; handle empty rows edge case more explicitly
# (omitted for brevity — see Fowler 2018 §Extract Function)
# Tests stay GREEN throughout.
```

Implementer returns:
```
status: DONE
commits: [a3f8c12]
test_results:
  - tests/renderers/test_csv_renderer.py::test_quote_special_chars  PASS
self_review:
  - RFC 4180 §2.6 compliance verified (csv.QUOTE_MINIMAL covers
    the comma / quote / newline cases)
  - No allocation beyond StringIO + writer's internal buffers
    (memory linear in payload size; matches brief's 50K-row scope)
  - Empty payload returns empty string (not error) — matches
    "current behavior for empty reports" implicit in brief
```

### Task 2 reviewer dispatch (parallel)

**spec-reviewer** verdict: PASS (covers brief item "RFC 4180 CSV output")
**code-quality-reviewer** verdict: PASS (security ✓ no injection surface; architecture ✓ pure function; tests ✓ RED-then-GREEN evidence; naming ✓ `render_csv` matches snake_case + verb-noun convention; refactoring ✓ minimal; correctness ✓ test asserts spec)

---

## Stage 6 — `requesting-code-review` (Whole-branch review)

After all 3 tasks DONE, user invokes `finishing-a-development-branch` which dispatches `requesting-code-review` as Step 1.

```
verdict: PASS

dimension_scores:
  security: PASS
  architecture: PASS
  correctness: PASS
  naming: PASS
  tests: PASS
  refactoring: PASS
  cross-task-coherence: PASS

findings: []

summary:
  - Branch ships exactly the brief's Smallest End State (query-param
    only; no scope creep into streaming / XLSX / etc.)
  - Per-task tests cohere into a 3-test add (no test interactions);
    handler + renderer are independent; integration is the join point
  - Internal wiki page "Manually exporting report data to CSV" still
    needs deletion in same PR (per brief Axis 5) — not yet done
```

The cross-task-coherence note about the wiki page → user fixes (deletes wiki page), re-runs review → PASS clean.

---

## Stage 7 — `verification-before-completion`

```
$ pytest
============================= test session starts ==============================
collected 47 items

tests/routes/test_reports.py::test_format_param_parsed PASSED
tests/routes/test_reports.py::test_csv_format_returns_csv PASSED
tests/renderers/test_csv_renderer.py::test_quote_special_chars PASSED
... (44 pre-existing tests) ...

======================== 47 passed in 2.41s ========================
```

47 tests passed (3 new + 44 pre-existing); none of the new tests broke anything. PASS.

---

## Stage 8 — `finishing-a-development-branch`

Orchestrator runs 7-step flow:

1. ✅ `requesting-code-review` — PASS (verdict above)
2. ✅ `verification-before-completion` — PASS (pytest output above)
3. **`dev-workflow:git-memory`** — invoked; decides 1 Decision: trailer warranted (the choice not to support XLSX / streaming is non-obvious and worth recording for future maintainers)
4. **git commit** — user approves commit message:
   ```
   feat(reports): add ?format=csv export to /reports/:id

   Adds a CSV rendering path alongside the existing JSON response for the
   /reports/:id endpoint. CSV output is RFC 4180 compliant (csv module
   QUOTE_MINIMAL). Internal data analysts ingest into Excel via the
   ?format=csv query param; existing JSON callers are unaffected.

   Decision: query-param approach over new /reports/:id.csv endpoint —
    avoids duplicating auth + ACL logic; CSV is a render-time choice,
    not a separate resource. XLSX support deferred; CSV solves the
    Excel use case at lower complexity. Streaming deferred until
    reports grow beyond 1M rows (current largest is 50K).
   ```
5. **git push** — only after user explicit re-authorize
6. **gh pr create** — user opts in; PR body uses brief + plan + verdict as content
7. **git worktree cleanup** — N/A (branch not in a worktree)

---

## What this example demonstrates about code-toolkit

| Skill | What you saw |
|---|---|
| `using-code-toolkit` | Auto-injected at session start; routed to brainstorming on the user's open-ended prompt |
| `brainstorming` | Forced 5-axis exploration BEFORE the agent started typing code; surfaced obsolete wiki page in Axis 5 |
| `writing-plans` | Produced ≤5-task plan with explicit RED-GREEN per task; plan-document-reviewer PASS 12/12 |
| `subagent-driven-development` | 3 tasks × 3 subagents = 9 subagent dispatches; cross-task-coherence dimension caught the missing wiki deletion |
| `tdd-iron-law` | RED before GREEN every time; Beck 2002 Preface applied to the renderer |
| `requesting-code-review` | Branch-scope review caught the wiki-deletion gap that per-task review couldn't see |
| `verification-before-completion` | Forced `pytest` invocation; 47 tests pass evidence, not "tests pass" claim |
| `finishing-a-development-branch` | Orchestrated all 7 close-out steps; user re-authorized push explicitly |

**What you did NOT see (but the toolkit prevented)**:
- Random patching ("let me just try adding CSV and see") — brainstorming forced 5-axis first
- Tests-after ("I'll write tests once it works") — tdd-iron-law forced RED first
- Push without review — router rule #4 + requesting-code-review's Push-as-trigger
- "Tests pass" without invocation — verification-before-completion forced the pytest output
- Auto-merge — finishing-a-development-branch requires user re-authorize each visible action

## See also

- [`typescript-react-toast.md`](typescript-react-toast.md) — multi-module example with SDD child-test fallback
- [`swift-network-layer.md`](swift-network-layer.md) — refactoring example with Feathers 2004 legacy backfill
- [`../../README.md`](../../README.md) — top-level toolkit overview
- [`../../skills/using-code-toolkit/SKILL.md`](../../skills/using-code-toolkit/SKILL.md) — router charter the agent loads
