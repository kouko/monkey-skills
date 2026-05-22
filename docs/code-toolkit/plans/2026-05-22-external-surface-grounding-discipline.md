# Plan: External Surface Grounding Discipline

Source brief: [docs/code-toolkit/specs/2026-05-22-external-surface-grounding-discipline.md](../specs/2026-05-22-external-surface-grounding-discipline.md)
Total tasks: 5
Execution order: T1 → T2 → (T3 ∥ T4) → T5
Plan-document-reviewer verdict: PASS (14/14 checks; 3 informational notes — T5 size acknowledged with pre-declared Beck Child Test fallback to T5a/T5b; T5 dependency line uses canonical `Tasks 3, 4 parallel` prefix; Approach 2 implementer baseline sentence explicitly deferred to v2)
Plugin under change: `code-toolkit` (with canonical SSOT edits in `domain-teams/skills/code-team/`)

## Brief-item coverage map

| Brief item (§Smallest End State) | Covered by |
|---|---|
| 1. New canonical standard at `domain-teams/skills/code-team/standards/external-surface-grounding.md` (≤120 lines) | T1 |
| 1b. Functional copy auto-materialized in `code-toolkit/skills/subagent-driven-development/standards/` via ROUTE | T2 |
| 2. D7 dimension added to `code-toolkit/agents/code-quality-reviewer.md` (per-task) | T3 |
| 2b. D7 dimension added to `code-toolkit/agents/code-reviewer.md` (whole-branch + cross-task surface consistency) | T4 |
| 3. `External surfaces:` field in `code-toolkit/skills/writing-plans/` (SKILL.md + plan-format.md) | T5 |
| 3b. spec-reviewer enforcement via new check row in canonical `domain-teams/skills/code-team/checklists/spec-consistency.md` + propagated copy | T5 |

implementer agent prompt baseline edit (§Alternatives Considered Approach 2): **deferred to v2** — the standard's presence in `code-toolkit/skills/subagent-driven-development/standards/` is auto-loaded by SDD's standards-routing; explicit dimension-row addition not needed for v1.

## Execution graph

```
T1 (canonical standard)
   ↓
T2 (ROUTE + distribute + verify-drift)
   ↓
   ├── T3 (code-quality-reviewer D7)   ← Independent: true with T4
   └── T4 (code-reviewer D7)            ← Independent: true with T3
   ↓
T5 (writing-plans field + spec-consistency check + final distribute)
```

T3 and T4 are dispatch-parallel-eligible (disjoint `Files touched`, both `Independent: true`). All other transitions are sequential.

---

## Task 1 — Write canonical SSOT standard `external-surface-grounding.md`

- **Description**: Author the canonical standard file in domain-teams at the SSOT location. Body covers: (a) the rule — any non-stdlib external surface invoked in production code MUST cite a grounding source; (b) the 5 surface categories (HTTP API / SDK package / MCP tool / CLI flag / internal sibling-team contract); (c) the 4 valid grounding sources in preference order (Live verification / MCP schema / Pinned reference with capture-date / In-repo evidence); (d) the explicit anti-pattern rationalizations to refuse (*"I know this API"* / *"the SDK probably has this"* / *"the CLI usually accepts --foo"* / *"the MCP tool I used last week"*); (e) primary-source citations (Amazon Science DAG paper / Trend Micro slopsquatting / Addy Osmani 2026 workflow / Zenn CLI 設計原則); (f) explicit note that per-task code-quality-reviewer is structurally blind to cross-task surface consistency — that dimension lives in whole-branch code-reviewer only.
- **Module**: domain-teams code-team standards (canonical SSOT)
- **Files touched**: `domain-teams/skills/code-team/standards/external-surface-grounding.md`
- **Context paths**:
  - `docs/code-toolkit/specs/2026-05-22-external-surface-grounding-discipline.md` (the brief — full design context)
  - `domain-teams/skills/code-team/standards/tdd-standard.md` (existing standard for tone + structural template)
  - `domain-teams/skills/code-team/standards/character-encoding-security.md` (closest analog — also "verify external input" discipline)
- **Acceptance**:
  - RED: `test -f domain-teams/skills/code-team/standards/external-surface-grounding.md` returns false (file does not exist before task starts).
  - GREEN: file exists; body ≤120 lines; contains required sections (Rule / 5 Surface Categories / 4 Grounding Sources / Anti-patterns / Citations / Per-task vs Whole-branch scope note); each surface category has at least one concrete example; each grounding source has at least one concrete example; citations include the 4 named sources with URLs.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: §Smallest End State item 1 (canonical SSOT standard `external-surface-grounding.md` ≤120 lines)

---

## Task 2 — Wire distribution for new standard (ROUTE + distribute + verify-drift)

- **Description**: Add a ROUTE dict entry in `code-toolkit/scripts/distribute.py` mapping `standards/external-surface-grounding.md` → `skills/subagent-driven-development/standards/external-surface-grounding.md`. Then run `python3 code-toolkit/scripts/distribute.py` to materialize the functional copy. Then run `python3 code-toolkit/scripts/verify-drift.py` to confirm CI gate passes.
- **Module**: code-toolkit SSOT distribution
- **Files touched**: `code-toolkit/scripts/distribute.py`, `code-toolkit/skills/subagent-driven-development/standards/external-surface-grounding.md` (auto-generated; do not hand-edit)
- **Context paths**:
  - `code-toolkit/scripts/distribute.py` lines containing existing ROUTE entries (`standards/tdd-standard.md` pattern)
  - `code-toolkit/scripts/verify-drift.py` (read-only — understand exit codes)
- **Acceptance**:
  - RED: `python3 code-toolkit/scripts/verify-drift.py; echo $?` returns non-zero (no ROUTE for new standard yet; or ROUTE added but functional copy not materialized).
  - GREEN: ROUTE entry present in `distribute.py` (visible in `grep external-surface-grounding code-toolkit/scripts/distribute.py`); `python3 code-toolkit/scripts/distribute.py` completes with no errors; functional copy exists at `code-toolkit/skills/subagent-driven-development/standards/external-surface-grounding.md` and is byte-identical to canonical-plus-SSOT-header; `python3 code-toolkit/scripts/verify-drift.py; echo $?` returns 0.
- **Dependencies**: Task 1 completes first (ROUTE entry is meaningless without canonical content to copy)
- **Independent**: false
- **Brief item covered**: §Smallest End State item 1b (functional copy auto-materialized via ROUTE) + §Reverse SSOT-chain requirement

---

## Task 3 — Add D7 dimension to `code-quality-reviewer.md` (per-task scope)

- **Description**: Add a new review dimension D7 "External Surface Grounding" to the per-task code-quality-reviewer agent prompt. Include: (a) the dimension's purpose (verify every external-surface call in this task's diff has a grounding cite); (b) the routing-table row mapping the dimension to `standards/external-surface-grounding.md` (analogous to the existing security/architecture/naming/tests/refactoring rows around lines 119-126 of the file); (c) the severity rubric — 🔴 fatal MUST: HTTP API / SDK package / MCP tool / CLI flag call without grounding cite; 🟡 should-fix SHOULD: internal sibling-team contract call without grounding cite; 🟢 nit: cite uses in-repo evidence when live verification was available in this session; (d) explicit scope statement: "per-task reviewer evaluates this task's artifact only — cross-task surface-consistency checks are out of scope here and live in whole-branch code-reviewer's D7."
- **Module**: code-toolkit code-quality-reviewer agent prompt
- **Files touched**: `code-toolkit/agents/code-quality-reviewer.md`
- **Context paths**:
  - `code-toolkit/agents/code-quality-reviewer.md` (existing 6-dimension structure for tone + template)
  - `code-toolkit/skills/subagent-driven-development/rubrics/quality-gate.md` (existing dimension rubric format)
  - `domain-teams/skills/code-team/standards/external-surface-grounding.md` (from T1 — to reference accurately)
- **Acceptance**:
  - RED: `grep -c "external-surface-grounding\|External Surface Grounding\|D7" code-toolkit/agents/code-quality-reviewer.md` returns 0.
  - GREEN: D7 dimension section exists with required severity rubric (3 levels named); routing-table row references `standards/external-surface-grounding.md`; explicit "per-task only, no cross-task" scope note present; total file LOC increase ≤60.
- **Dependencies**: Task 2 completes first (standard must exist canonically AND be materialized as functional copy at `code-toolkit/skills/subagent-driven-development/standards/external-surface-grounding.md` for the agent dimension-table reference to resolve at SDD dispatch time)
- **Independent**: true (parallel-eligible with Task 4 — disjoint `Files touched`)
- **Brief item covered**: §Smallest End State item 2 (D7 dimension in code-quality-reviewer, per-task scope)

---

## Task 4 — Add D7 dimension to `code-reviewer.md` (whole-branch + cross-task)

- **Description**: Add a new review dimension D7 "External Surface Grounding" to the whole-branch code-reviewer agent prompt. Mirrors Task 3's severity rubric but **adds the cross-task consistency check**: 🟡 should-fix when two or more tasks in the branch call the same external surface with conflicting parameter shapes / version pins / endpoints. Explicit statement: "this dimension's cross-task consistency check is whole-branch reviewer's responsibility because per-task reviewers are structurally blind to sibling tasks."
- **Module**: code-toolkit code-reviewer agent prompt
- **Files touched**: `code-toolkit/agents/code-reviewer.md`
- **Context paths**:
  - `code-toolkit/agents/code-reviewer.md` (existing 7-dimension structure including cross-task-coherence dimension for tone + template)
  - `domain-teams/skills/code-team/standards/external-surface-grounding.md` (from T1)
- **Acceptance**:
  - RED: `grep -c "external-surface-grounding\|External Surface Grounding\|D7" code-toolkit/agents/code-reviewer.md` returns 0.
  - GREEN: D7 dimension section exists with severity rubric (mirroring T3) plus explicit cross-task-consistency 🟡 rule; routing-table row references `standards/external-surface-grounding.md`; explicit "whole-branch owns cross-task surface consistency" statement present; total file LOC increase ≤70.
- **Dependencies**: Task 2 completes first (same reasoning as Task 3 — functional copy must be materialized for the agent reference to resolve)
- **Independent**: true (parallel-eligible with Task 3 — disjoint `Files touched`)
- **Brief item covered**: §Smallest End State item 2b (D7 dimension in code-reviewer, whole-branch + cross-task surface consistency)

---

## Task 5 — Plan-time declaration + spec-reviewer enforcement + final distribute

- **Description**: Three coordinated edits implementing the plan-time half of the discipline: (a) add `External surfaces:` as a new optional atomic-task field in `code-toolkit/skills/writing-plans/SKILL.md` task template documentation and in `code-toolkit/skills/writing-plans/references/plan-format.md` schema, with the format `- <surface category>: <name> — grounding: <method>` and 2-3 concrete examples; (b) add a new check row to the canonical `domain-teams/skills/code-team/checklists/spec-consistency.md` enforcing: when a task's `Files touched` or `Description` references any non-stdlib external surface, the task MUST also have an `External surfaces:` field populated; (c) run `python3 code-toolkit/scripts/distribute.py` and `python3 code-toolkit/scripts/verify-drift.py` to propagate the spec-consistency edit and confirm clean CI state.
- **Module**: plan-time declaration + spec-reviewer enforcement layer (justified scope stretch — three files but tightly coupled by "plan-time external-surface declaration" concern; the writing-plans field is meaningless without the spec-consistency check, and vice versa; distribute step propagates the SSOT edit and validates the whole chain)
- **Files touched**: `code-toolkit/skills/writing-plans/SKILL.md`, `code-toolkit/skills/writing-plans/references/plan-format.md`, `domain-teams/skills/code-team/checklists/spec-consistency.md`, `code-toolkit/skills/subagent-driven-development/checklists/spec-consistency.md` (auto-generated by distribute; do not hand-edit)
- **Context paths**:
  - `code-toolkit/skills/writing-plans/SKILL.md` (existing task template for tone + insertion point)
  - `code-toolkit/skills/writing-plans/references/plan-format.md` (existing schema definition; lines 42-65 are the task-field block — `External surfaces:` slots between `Acceptance` and `Independent`)
  - `domain-teams/skills/code-team/checklists/spec-consistency.md` (existing 11-row check table for tone)
  - `domain-teams/skills/code-team/standards/external-surface-grounding.md` (from T1 — referenced by the new check row)
- **Acceptance**:
  - RED: `grep -c "External surfaces" code-toolkit/skills/writing-plans/SKILL.md code-toolkit/skills/writing-plans/references/plan-format.md domain-teams/skills/code-team/checklists/spec-consistency.md` returns 0; `python3 code-toolkit/scripts/verify-drift.py; echo $?` returns 0 (clean before the canonical spec-consistency edit) or non-zero (after canonical edit, before distribute run).
  - GREEN: `External surfaces:` field documented in SKILL.md task-template prose AND in plan-format.md schema with 2-3 concrete examples covering ≥3 surface categories from §Resolved Decisions §5; canonical spec-consistency.md has a new check row enforcing the field when external surface is referenced; functional copy at `code-toolkit/skills/subagent-driven-development/checklists/spec-consistency.md` is byte-identical to canonical+header after distribute run; `python3 code-toolkit/scripts/verify-drift.py; echo $?` returns 0.
- **Dependencies**: Tasks 3, 4 parallel (both must finish; T1+T2 are transitive prerequisites via T3/T4's `Task 2 completes first` declaration, so T5 is also after T1+T2 by transitive closure)
- **Independent**: false
- **Brief item covered**: §Smallest End State item 3 (`External surfaces:` field in writing-plans SKILL.md + plan-format.md) + item 3b (spec-consistency canonical check + functional-copy propagation)

---

## Notes for SDD orchestrator

- **Implementer scope per task**: each task is sized for one focused 5-min implementer subagent. T5 is the heaviest — if implementer returns BLOCKED with decomposition signal, fall back to Beck Child Test pattern (§writing-plans BLOCKED fallback) and split T5 into T5a (writing-plans field) + T5b (spec-consistency canonical edit + distribute).
- **Parallel dispatch**: only T3 ∥ T4 are eligible. Do not parallel-dispatch other pairs — all other transitions have sequential dependencies (standards must exist before they can be referenced).
- **distribute.py runs**: appear in T2 (for the standard) and T5 (for the checklist). Both invocations are idempotent. If T2 ran clean, T5's run only changes the spec-consistency functional copy.
- **TDD ordering inside each task**: the RED → GREEN markers above ARE the failing-test acceptance, but several tasks have non-code RED tests (file-existence checks, grep counts, CI script exit codes). This is consistent with `tdd-iron-law/SKILL.md` §When NOT to Use exemption for "discipline-definition / config-shape tasks" — the RED condition is observably wrong before the task, observably right after.
- **No new tests under `code-toolkit/tests/`**: this v1 ships the discipline, not a pressure-test for it. Pressure-test deferred per brief §Out of Scope.

## Cross-references

- Brief: [`docs/code-toolkit/specs/2026-05-22-external-surface-grounding-discipline.md`](../specs/2026-05-22-external-surface-grounding-discipline.md)
- Related memory: `feedback_cross_skill_schema_rename_blind_spot`, `feedback_per_task_review_misses_pipe_semantics`, `feedback_lint_checks_md_second_drift_surface`
- SDD downstream consumer: [`code-toolkit/skills/subagent-driven-development/SKILL.md`](../../../code-toolkit/skills/subagent-driven-development/SKILL.md)
