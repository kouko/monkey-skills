# Plan format — handoff from `writing-plans` to `subagent-driven-development`

> Companion to [`../SKILL.md`](../SKILL.md). Defines what writing-plans produces and what `subagent-driven-development` (SDD) consumes.

## Why this schema

SDD dispatches three subagents per task (implementer + spec-reviewer + code-quality-reviewer). To do that without re-extracting metadata from prose, SDD needs each task pre-decorated with:

- **Description** — the implementer's task text.
- **Module** — for code-quality-reviewer's per-task scoping.
- **Context paths** — what the implementer reads (paths-not-content delegation).
- **Acceptance** — for tdd-iron-law's RED-GREEN-REFACTOR cycle (failing test name + GREEN condition).
- **Dependencies** — for sequencing / parallelization.

Free-form plans force SDD to re-parse; this schema makes the parse trivial.

## Where the plan lives

| Repo convention | Path | When |
|---|---|---|
| monkey-skills-style | `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` | Default. Sibling to the brief at `docs/superpowers/specs/`. |
| Project-local | `docs/plans/<topic>.md` | If the project has its own `docs/plans/` convention. |
| Inline (no file) | Plan in chat context | Only for §When NOT to Use exempt cases — brief was its own plan; document inline; do not commit. |

## Schema

### Top-level header (required)

```markdown
# Plan: <topic>

**Source brief**: <path to brief, e.g. docs/superpowers/specs/2026-05-16-csv-export.md>
**Total tasks**: <N> (must be ≤5; if >5 route back to brainstorming)
**Execution order**: sequential | parallel-where-possible
**Plan-document-reviewer verdict**: PASS (timestamp) | PENDING
```

If `Plan-document-reviewer verdict` is `PENDING`, the plan has not been self-reviewed yet and SDD MUST NOT consume it.

### Per-task block (required, repeats N times)

```markdown
## Task <N> — <short imperative name>

- **Description**: <≤5 min unit of work, imperative voice>
- **Module**: <path or module name; ONE only>
- **Context paths**:
  - <absolute path to existing code the implementer reads>
  - <... additional context paths>
- **Acceptance**:
  - **RED**: <failing test name OR diagnostic the implementer writes first>
  - **GREEN**: <observable condition when the task is done>
- **Dependencies**: <one of: "none" | "Task N completes first" | "Tasks N, M parallel">
- **Brief item covered**: <quote or reference from the brief's Smallest End State / Decision section>
```

### Optional sections

```markdown
## Parent-child decomposition (only present if this plan is a BLOCKED fallback)

Parent task: <original task that returned BLOCKED>
Implementer's unblock_step: <quote>
Child tasks: 1, 2, 3 (listed above)
Parent declared DONE when all children DONE.

## Notes

(Free-form notes to SDD orchestrator — e.g. "Tasks 2+3 can run parallel after Task 1; Task 4 needs Task 2 only, not Task 3")
```

## Worked example

For a brief at `docs/superpowers/specs/2026-05-16-csv-export.md` whose Smallest End State is *"add `?format=csv` query param to the existing `/reports/<id>` endpoint":*

```markdown
# Plan: CSV export query param

**Source brief**: docs/superpowers/specs/2026-05-16-csv-export.md
**Total tasks**: 3 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-05-16 10:42)

## Task 1 — Add format query param parsing to /reports handler

- **Description**: Accept `format=csv` query param in `GET /reports/:id`; default to `format=json` if absent or unrecognized.
- **Module**: `src/routes/reports.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/routes/reports.ts`
  - `/Users/kouko/proj/tests/routes/reports.test.ts`
- **Acceptance**:
  - **RED**: `reports.test.ts > GET /reports/:id?format=csv returns 200`
  - **GREEN**: query param parsed; passed to renderer; existing JSON path unchanged
- **Dependencies**: none
- **Brief item covered**: "minimum shippable change: `?format=csv` query param to existing report URL (no UI work)"

## Task 2 — Implement CSV renderer for report payload

- **Description**: Convert the existing `ReportPayload` JSON shape to RFC 4180 CSV. Use `papaparse` (already in deps).
- **Module**: `src/renderers/csv.ts` (new file)
- **Context paths**:
  - `/Users/kouko/proj/src/types/ReportPayload.ts`
  - `/Users/kouko/proj/node_modules/papaparse/README.md` (API ref)
- **Acceptance**:
  - **RED**: `renderers/csv.test.ts > renderCSV produces RFC 4180-compliant output with quoted fields containing commas`
  - **GREEN**: CSV string matches RFC 4180 fixture; passes existing fuzz tests
- **Dependencies**: none (parallel with Task 1)
- **Brief item covered**: "minimum shippable change: CSV output that downstream pipeline can ingest"

## Task 3 — Wire renderer into handler + set Content-Type

- **Description**: When `format=csv`, call `renderCSV(payload)`, return with `Content-Type: text/csv; charset=utf-8`.
- **Module**: `src/routes/reports.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/routes/reports.ts` (modified by Task 1)
  - `/Users/kouko/proj/src/renderers/csv.ts` (produced by Task 2)
- **Acceptance**:
  - **RED**: `reports.test.ts > GET /reports/:id?format=csv returns text/csv body matching renderer output`
  - **GREEN**: end-to-end request returns valid CSV; Content-Type header correct
- **Dependencies**: Tasks 1, 2 complete first
- **Brief item covered**: "minimum shippable change: end-to-end CSV download path"

## Notes

Tasks 1 + 2 are independent and can run parallel in SDD dispatch. Task 3 joins them.
```

## Anti-patterns

- ❌ **Vague task descriptions.** *"Add CSV support"* is not actionable. *"Add `format=csv` query param parsing to `GET /reports/:id` handler"* is.
- ❌ **Multi-module task.** If `Module:` lists 2+ files, split. The implementer subagent's per-task scope is one module.
- ❌ **Missing acceptance.** A task with no RED test name has no done-condition. tdd-iron-law cannot fire on it. Always name the failing test.
- ❌ **Implicit dependencies.** If a task says *"also remember to update the OpenAPI spec,"* that update is a missing task. Declare it.
- ❌ **Tasks not traceable to brief.** Every task must quote / reference a brief item. Orphan tasks are scope creep.
- ❌ **>5 tasks with no fallback decision.** If the plan needs >5 atomic tasks, route back to brainstorming OR split into multiple briefs. Do not silently produce a 10-task plan.
- ❌ **Skipping plan-document-reviewer self-review.** `Plan-document-reviewer verdict: PENDING` means SDD blocks. Do not pass an unreviewed plan to SDD.

## See also

- [`../SKILL.md`](../SKILL.md) — the splitting framework + BLOCKED fallback flow.
- [`plan-document-reviewer-prompt.md`](plan-document-reviewer-prompt.md) — the evaluator subagent that PASSes / NEEDS_REVISIONs this schema.
- [`../../brainstorming/references/handoff-brief-format.md`](../../brainstorming/references/handoff-brief-format.md) — upstream brief schema.
- [`../../subagent-driven-development/SKILL.md`](../../subagent-driven-development/SKILL.md) — downstream consumer.
