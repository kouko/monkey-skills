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

| Mode | Path | When |
|---|---|---|
| File | `docs/loom/plans/YYYY-MM-DD-<topic>.md` | **Default.** Sibling to the brief at `docs/loom/specs/`. |
| Inline (no file) | Plan in chat context | Only for §When NOT to Use exempt cases — brief was its own plan; document inline; do not commit. |

## Schema

### Top-level header (required)

```markdown
# Plan: <topic>

**Source brief**: <path to brief, e.g. docs/loom/specs/2026-05-16-csv-export.md>
**Total tasks**: <N>
**Critical-path depth**: <D> (must be ≤5; if >5 route back to brainstorming)
**Execution order**: sequential | parallel-where-possible
**Plan-document-reviewer verdict**: PASS (timestamp) | PENDING
```

If `Plan-document-reviewer verdict` is `PENDING`, the plan has not been self-reviewed yet and SDD MUST NOT consume it.

**Critical-path depth** is the **longest chain of tasks linked by `Dependencies`** (the longest sequential path through the dependency DAG). N independent tasks at the **same dependency level** (disjoint `Files touched`, no semantic dependency) count as **one level**, not N. The ceiling is on this depth, NOT on `Total tasks` — `Total tasks` is uncapped.

### Per-task block (required, repeats N times)

```markdown
## Task <N> — <short imperative name>

- **Description**: <one-assertion unit of work, imperative voice>
- **Module**: <path or module name; ONE only>
- **Files touched**: <comma-separated paths the implementer will Write / Edit>
- **Context paths**:
  - <absolute path to existing code the implementer reads>
  - <... additional context paths>
- **Acceptance**:
  - **RED**: <failing test name OR diagnostic the implementer writes first>
  - **GREEN**: <observable condition when the task is done>
- **External surfaces**: <v0.9.0+ — required when task touches non-stdlib external surface. See §External surfaces below. Omit field entirely if task is pure internal logic.>
- **Dependencies**: <one of: "none" | "Task N completes first" | "Tasks N, M complete first" (multi-prerequisite — N and M must both finish before this task starts) | "Tasks N, M parallel" (both are prerequisites, may run in parallel). Cross-part ordering: use "none" at task level + a plan-level `Notes` entry; the field is within-plan only and cannot reference a sibling part's tasks.>
- **Independent**: <true | false>  # v0.8.0+ — opt-in marker for `dispatching-parallel-agents`. Default false.
- **Review-weight**: <mechanical | OMIT>  # v0.11.0+ — opt-in, default absent = full triad (implementer + spec-reviewer + code-quality-reviewer). May ONLY be set when this task is an identical or near-identical edit reproducible from an exact spec — never for logic, heuristic, hook, or security-surface changes. See §`Review-weight` below.
- **Brief item covered**: <traceability referent — ONE field, two accepted referent kinds:
    (a) a quote or reference from the brief's Smallest End State / Decision section, OR
    (b) when the plan consumes a loom-spec change-folder, a **stable join key** of the form
    `<change-id> / Requirement: <name> / Scenario: <name>` (R5 — a checkable provenance referent,
    à la Kiro `_Requirements:` / Spec-Kit `FR-###`). This is the SAME field with a broadened
    referent — do NOT add a second field; point at the source `### Requirement:` / `#### Scenario:`
    names rather than copying their prose.>
- **Status**: <OPTIONAL runtime ledger field — see §Progress ledger. One of:
    "pending" | "claimed(@<agent>)" | "done(<sha>)" | "blocked". Default OMITTED (a plan with no
    Status fields behaves exactly as before — fully backward compatible). NOT authoring content;
    SDD writes it, the plan-document-reviewer ignores it.>
```

#### `Files touched` and `Independent` (v0.8.0+)

- **`Files touched`** is the **disjointness oracle** for cross-task parallel dispatch. List every file the implementer will Write or Edit (not files it merely Reads — those go in `Context paths`).
- **`Independent: true`** is the plan author's claim that this task has no shared symbol / no sequential data dependency with other `Independent: true` tasks. Default `false`.
- [`../../dispatching-parallel-agents/SKILL.md`](../../dispatching-parallel-agents/SKILL.md) MAY dispatch tasks concurrently only when **both** declare `Independent: true` AND their `Files touched` sets are disjoint. Otherwise SDD's sequential dispatch is the floor.
- **Empty-recon sentinel.** When target-repo reconnaissance finds **no existing target** (greenfield target / wrong repo), the contract forbids fabricating an existing path — so `Files touched` / `Module` may be written as a **PROPOSED-new** form clearly marked NEW (`NEW: <proposed-path>`, or `greenfield — no existing target found`), **never a guessed existing path**. A task whose `Files touched` is a PROPOSED-new path defaults to **`Independent: false`**: the disjointness oracle cannot be trusted on a path that does not exist yet, so such tasks must not be marked parallel-eligible.

#### `Review-weight` (v0.11.0+, optional)

`Review-weight: mechanical` is an **opt-in exemption marker**, not a default. Default (field absent) is the full triad — implementer + spec-reviewer + code-quality-reviewer — unchanged.

It may ONLY be set when this task is an identical or near-identical edit reproducible from an exact spec — never for logic, heuristic, hook, or security-surface changes. If the task involves any conditional branching, a heuristic threshold, a hook, or touches a security-relevant surface, do NOT set this field; leave it absent so the full triad runs.

#### Progress ledger — the `Status` field (v0.10.0+, optional)

The optional per-task `Status` field turns the plan into a **run-scoped, durable, shared progress
ledger**. It is **runtime state**, not plan-authoring content: `writing-plans` never sets it (a fresh
plan has no `Status` fields), `subagent-driven-development` **maintains** it as it executes, and
`plan-document-reviewer` **ignores** it.

Vocabulary (exactly these four):

| Value | Meaning | Set by SDD when |
|---|---|---|
| `pending` | not started (or simply omitted) | — (default / omitted) |
| `claimed(@<agent>)` | an agent is working it; `<agent>` is the worktree branch name (unique per agent) | the implementer is dispatched |
| `done(<sha>)` | resolved + committed; `<sha>` is the task's commit | reviewers PASS and the task is committed |
| `blocked` | stuck (NEEDS_CONTEXT / BLOCKED / 3-round cap) | the task cannot proceed |

Why it earns its place:
- **Interruption (crash / session death):** the committed ledger + per-task commits let a resumed run
  skip `done(<sha>)` tasks and redo only the in-flight `claimed` one — no full-plan re-derivation.
- **Scale:** explicit status beats reconstructing progress from `git log` on a large plan.
- **Multi-agent (b):** the ledger is the **shared task-claim doc** that coordinates several concurrent
  agents (see `dispatching-parallel-agents` §Multiple concurrent sessions) — worktrees isolate files,
  the ledger coordinates *who does what*.

**Backward compatibility is total:** omit `Status` and nothing changes. The field is opt-in by presence,
exactly like `External surfaces`.

#### `External surfaces` (v0.9.0+)

When an atomic task touches a **non-stdlib external surface** the agent does not author, the plan MUST declare it. This is the plan-time half of the external-surface-grounding discipline (see `loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md`); the review-time half is D7 in `code-quality-reviewer.md` + `code-reviewer.md`. The two halves form one defense-in-depth gate.

Five surface categories trigger the field (per the standard's §Five Surface Categories): **HTTP API**, **SDK package**, **MCP tool**, **CLI flag**, **internal sibling-team contract**. A third-party library reached for to do version / date / format work (e.g. `packaging`) is an **SDK package** surface — declare it or replace it with stdlib. Stdlib parsing (`json`, `datetime`, version-tuple split) is authored-internal and needs no declaration.

Format — one bullet per surface:

```markdown
- **External surfaces**:
  - SDK package: @anthropic-ai/sdk@0.40 client.messages.create — grounding: WebFetch https://docs.anthropic.com/en/api/messages (captured 2026-05-22)
  - MCP tool: claude_ai_Asana__create_tasks — grounding: in-context tool schema
  - CLI flag: gh pr create --base — grounding: gh pr create --help (captured 2026-05-22)
```

Each bullet declares **category** + **specific name / identifier** + **grounding source** (one of the four valid types: Live verification / MCP schema / Pinned reference / In-repo evidence — see the standard for details).

**Omit the field entirely** when the task is pure internal logic (renames a local symbol, edits a markdown doc with no external references, refactors an existing function with no new external calls, etc.). The field is opt-in by surface presence, not by every task.

Per-task `code-quality-reviewer.md` D7 enforces that any external call in the task's diff carries a grounding cite. Whole-branch `code-reviewer.md` D7 additionally checks for cross-task surface-consistency conflicts. The `spec-consistency.md` checklist (`CHK-SPEC-008`) requires this field's presence when the task description / `Files touched` reference any of the five surface categories.

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

For a brief at `docs/loom/specs/2026-05-16-csv-export.md` whose Smallest End State is *"add `?format=csv` query param to the existing `/reports/<id>` endpoint":*

```markdown
# Plan: CSV export query param

**Source brief**: docs/loom/specs/2026-05-16-csv-export.md
**Total tasks**: 3
**Critical-path depth**: 2 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-05-16 10:42)

## Task 1 — Add format query param parsing to /reports handler

- **Description**: Accept `format=csv` query param in `GET /reports/:id`; default to `format=json` if absent or unrecognized.
- **Module**: `src/routes/reports.ts`
- **Files touched**: `src/routes/reports.ts`, `tests/routes/reports.test.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/routes/reports.ts`
  - `/Users/kouko/proj/tests/routes/reports.test.ts`
- **Acceptance**:
  - **RED**: `reports.test.ts > GET /reports/:id?format=csv returns 200`
  - **GREEN**: query param parsed; passed to renderer; existing JSON path unchanged
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "minimum shippable change: `?format=csv` query param to existing report URL (no UI work)"

## Task 2 — Implement CSV renderer for report payload

- **Description**: Convert the existing `ReportPayload` JSON shape to RFC 4180 CSV. Use `papaparse` (already in deps).
- **Module**: `src/renderers/csv.ts` (new file)
- **Files touched**: `src/renderers/csv.ts`, `src/renderers/csv.test.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/types/ReportPayload.ts`
  - `/Users/kouko/proj/node_modules/papaparse/README.md` (API ref)
- **Acceptance**:
  - **RED**: `renderers/csv.test.ts > renderCSV produces RFC 4180-compliant output with quoted fields containing commas`
  - **GREEN**: CSV string matches RFC 4180 fixture; passes existing fuzz tests
- **Dependencies**: none (parallel with Task 1)
- **Independent**: true
- **Brief item covered**: "minimum shippable change: CSV output that downstream pipeline can ingest"

## Task 3 — Wire renderer into handler + set Content-Type

- **Description**: When `format=csv`, call `renderCSV(payload)`, return with `Content-Type: text/csv; charset=utf-8`.
- **Module**: `src/routes/reports.ts`
- **Files touched**: `src/routes/reports.ts`, `tests/routes/reports.test.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/routes/reports.ts` (modified by Task 1)
  - `/Users/kouko/proj/src/renderers/csv.ts` (produced by Task 2)
- **Acceptance**:
  - **RED**: `reports.test.ts > GET /reports/:id?format=csv returns text/csv body matching renderer output`
  - **GREEN**: end-to-end request returns valid CSV; Content-Type header correct
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false  # touches files Task 1 also touches; must run after Task 1
- **Brief item covered**: "minimum shippable change: end-to-end CSV download path"

## Notes

Tasks 1 + 2 are independent (disjoint `Files touched`) and can run parallel in `dispatching-parallel-agents`. Task 3 joins them sequentially because its `Files touched` overlaps Task 1's.
```

### Wide-but-shallow example — 8 tasks, critical-path depth 2

A high `Total tasks` count is **not** a discovery failure when the tasks fan out wide instead of chaining deep. Consider a brief whose Smallest End State is *"add a one-line module docstring to each of the 6 renderer files, then run the lint gate, then update the index":*

```markdown
# Plan: backfill renderer module docstrings

**Source brief**: docs/loom/specs/2026-05-20-renderer-docstrings.md
**Total tasks**: 8
**Critical-path depth**: 2 (≤5 ✓)
**Execution order**: parallel-where-possible

## Task 1 — Docstring for csv renderer   (Independent: true, Dependencies: none)
## Task 2 — Docstring for json renderer  (Independent: true, Dependencies: none)
## Task 3 — Docstring for xml renderer   (Independent: true, Dependencies: none)
## Task 4 — Docstring for yaml renderer  (Independent: true, Dependencies: none)
## Task 5 — Docstring for toml renderer  (Independent: true, Dependencies: none)
## Task 6 — Docstring for html renderer  (Independent: true, Dependencies: none)
## Task 7 — Run lint gate over all renderers (Dependencies: Tasks 1-6 complete first)
## Task 8 — Regenerate renderer index doc   (Dependencies: Task 7 completes first)
```

Tasks 1-6 are **6 disjoint `Independent: true` leaves at one dependency level** — they count as **one level**, not six. The longest chain of tasks linked by `Dependencies` is `(any of 1-6) → 7 → 8`, so the **critical-path depth is 2**. Eight tasks, depth 2: a wide-but-shallow plan that validates cleanly and is **NOT** a discovery failure. It parallelizes the 6 leaves and joins them at Task 7. (Each per-task block above is abbreviated to one line for the depth illustration; a real plan expands every task to the full per-task schema.)

### `Review-weight: mechanical` example — 3 sibling tasks, identical one-line edit

Consider a brief whose Smallest End State is *"bump the copyright year string in each of 3 module headers from `2025` to `2026`, verbatim, no other changes":*

```markdown
## Task 1 — Bump copyright year in csv.ts header
- **Description**: In `src/renderers/csv.ts` line 1, replace the exact literal `// Copyright 2025` with the exact literal `// Copyright 2026`. No other changes.
- **Module**: `src/renderers/csv.ts`
- **Files touched**: `src/renderers/csv.ts`
- **Acceptance**:
  - **RED**: `csv.test.ts > header contains Copyright 2026` fails
  - **GREEN**: header line reads `// Copyright 2026`
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical

## Task 2 — Bump copyright year in json.ts header
- **Description**: In `src/renderers/json.ts` line 1, replace the exact literal `// Copyright 2025` with the exact literal `// Copyright 2026`. No other changes.
- **Module**: `src/renderers/json.ts`
- **Files touched**: `src/renderers/json.ts`
- **Acceptance**:
  - **RED**: `json.test.ts > header contains Copyright 2026` fails
  - **GREEN**: header line reads `// Copyright 2026`
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical

## Task 3 — Bump copyright year in xml.ts header
- **Description**: In `src/renderers/xml.ts` line 1, replace the exact literal `// Copyright 2025` with the exact literal `// Copyright 2026`. No other changes.
- **Module**: `src/renderers/xml.ts`
- **Files touched**: `src/renderers/xml.ts`
- **Acceptance**:
  - **RED**: `xml.test.ts > header contains Copyright 2026` fails
  - **GREEN**: header line reads `// Copyright 2026`
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical
```

Each task is an identical one-line edit (same exact-spec literal-string replacement, different file) — the reproducible-from-exact-spec bar `Review-weight: mechanical` requires. Contrast with Task 3 in the CSV-export example above (`Wire renderer into handler + set Content-Type`): that task branches on `format=csv` and touches request-handling logic, so it must NOT declare `Review-weight: mechanical` even though it is a small task — logic changes always take the full triad.

**"Near-identical" — one bounded per-file substitution, not free-form variation.** The marker also covers tasks that are the *same template with one literal swapped per file from a fixed, plan-declared list* — e.g. three sibling tasks each inserting the identical pointer sentence `"See \`family-relay.md §Family relay discipline\`."` into a different skill's `SKILL.md`, where only the surrounding one-line anchor phrase differs per file (still a verbatim literal named IN the task, not left to the implementer's judgment). This is *not* license to mark a task mechanical because it merely "feels similar" to a sibling — "add error handling similar to how Task 2 does it" is NOT reproducible-from-exact-spec (the implementer must judge what "similar" means) and must NOT declare `Review-weight: mechanical`, even though it superficially resembles a batch edit.

## Anti-patterns

- ❌ **Vague task descriptions.** *"Add CSV support"* is not actionable. *"Add `format=csv` query param parsing to `GET /reports/:id` handler"* is.
- ❌ **Multi-module task.** If `Module:` lists 2+ files, split. The implementer subagent's per-task scope is one module.
- ❌ **Missing acceptance.** A task with no RED test name has no done-condition. tdd-iron-law cannot fire on it. Always name the failing test.
- ❌ **Implicit dependencies.** If a task says *"also remember to update the OpenAPI spec,"* that update is a missing task. Declare it.
- ❌ **Tasks not traceable to brief.** Every task must quote / reference a brief item. Orphan tasks are scope creep.
- ❌ **Critical-path depth >5 with no fallback decision.** If the longest chain of tasks linked by `Dependencies` exceeds depth 5, route back to brainstorming OR split into multiple briefs. A deep chain is a discovery failure. Do not silently produce a deep sequential chain. (A wide-but-shallow plan — many `Independent: true` leaves, shallow depth — is fine; the ceiling counts depth, NOT total task count.)
- ❌ **Skipping plan-document-reviewer self-review.** `Plan-document-reviewer verdict: PENDING` means SDD blocks. Do not pass an unreviewed plan to SDD.
- ❌ **Claiming `Independent: true` with overlapping `Files touched`.** Independence requires disjoint write sets. If two tasks both declare `Independent: true` AND share any file in `Files touched`, the claim is wrong — fix the plan, not the dispatch. `dispatching-parallel-agents` will refuse to dispatch overlapping tasks regardless of the marker.

## See also

- [`../SKILL.md`](../SKILL.md) — the splitting framework + BLOCKED fallback flow.
- [`plan-document-reviewer-prompt.md`](plan-document-reviewer-prompt.md) — the evaluator subagent that PASSes / NEEDS_REVISIONs this schema.
- [`../../brainstorming/references/handoff-brief-format.md`](../../brainstorming/references/handoff-brief-format.md) — upstream brief schema.
- [`../../subagent-driven-development/SKILL.md`](../../subagent-driven-development/SKILL.md) — downstream consumer.
