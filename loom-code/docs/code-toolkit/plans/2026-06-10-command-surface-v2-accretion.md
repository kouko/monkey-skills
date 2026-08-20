# Plan: Command Surface v2 (野心 B — accretion discipline)

**Source brief**: code-toolkit/docs/code-toolkit/specs/2026-06-10-command-surface-v2-accretion-brief.md
**Total tasks**: 5
**Critical-path depth**: 3 (≤5 ✓ — longest chain: Task 1 → Task 2 → Task 5)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-10 13:38 CST) — 14/14; no Check-15 advisory (T4/T5 precondition not met)

> **TDD shape for prose edits** (same as v1): Task 1 builds a deterministic grep-based assertion harness RED against the current tree; each edit task flips its own check RED→GREEN.
>
> **Canonical assertion phrases** (the harness greps these verbatim; edit tasks MUST produce them exactly):
> - CHECK-ACCRETE-SDD (`subagent-driven-development/SKILL.md`): contains `new runnable capability` AND `accretion`
> - CHECK-ACCRETE-IMPL (`agents/implementer.md`): contains `verify-before-declare` AND `BEGIN command-surface (managed)`
> - CHECK-ACCRETE-PLAN (`writing-plans/SKILL.md`): contains `runnable capability`
> - CHECK-ACCRETE-PRESSURE: file `tests/verification-before-completion-pressure/prompts/accretion-declare-new-verb.txt` exists AND that dir's `index.md` references `accretion-declare-new-verb`

## Task 1 — Build the accretion assertion harness (the failing test)

- **Description**: Create `code-toolkit/tests/integration/test-command-surface-accretion.sh`, a read-only executable bash test modeled on `test-command-surface-resolution.sh` (same `set -euo pipefail`, `REPO_ROOT` self-location, `die()` helper, per-check `MISSING:`/`ok` lines, failure counter, exit 1 if any MISSING). Implement the four CHECK groups above using `grep -F` / `test -f`. Against the current unedited tree it MUST exit nonzero and print MISSING for all four checks. Do NOT edit any target file — only the harness.
- **Module**: `code-toolkit/tests/integration/test-command-surface-accretion.sh`
- **Files touched**: `code-toolkit/tests/integration/test-command-surface-accretion.sh`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/test-command-surface-resolution.sh`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/docs/code-toolkit/plans/2026-06-10-command-surface-v2-accretion.md` (this plan's canonical-phrases block)
- **Acceptance**:
  - **RED**: the harness does not exist yet.
  - **GREEN**: harness exists, `bash -n` clean, executable, self-locating; run against the **current unedited** tree exits **nonzero** printing `MISSING:` for ALL FOUR check ids. Paste the run output (four MISSING lines + nonzero exit).
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "extend the v1 harness ... with accretion CHECK groups asserting the new clause/obligation/marker phrases" (realized as a sibling harness to keep v1/v2 concerns independent)

## Task 2 — SDD Definition-of-Done accretion clause (A)

- **Description**: In `subagent-driven-development/SKILL.md`, add a focused subsection (e.g. a new "## Definition of Done — command-surface accretion" section, or a subsection under the per-task triad) stating: a task that introduces a **new runnable capability** (new test suite / build step / lint / e2e / migrate / …) is not DONE until its verb is **declared in the command surface AND verified to run** — event-driven **accretion** bound into the task Definition of Done, exactly as TDD couples behaviour + test. No new capability → no surface change. NOT per-task polling; NOT a build-once bootstrap. Reuse v1's declared-first resolution to locate the surface. MUST contain literals `new runnable capability` AND `accretion`. Do not alter the verdict-resolution table, status taxonomy, or other sections.
- **Module**: `code-toolkit/skills/subagent-driven-development/SKILL.md`
- **Files touched**: `code-toolkit/skills/subagent-driven-development/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/subagent-driven-development/SKILL.md` (L89-97 per-task triad; L111-139 verdict/status)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/docs/code-toolkit/specs/2026-06-10-command-surface-establishment.md` (§4.2 beat ②)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/test-command-surface-accretion.sh` (CHECK-ACCRETE-SDD is yours)
- **Acceptance**:
  - **RED**: CHECK-ACCRETE-SDD reports MISSING.
  - **GREEN**: both literals present; the clause is event-driven (no-capability → no-op) and explicitly NOT polling/bootstrap; harness CHECK-ACCRETE-SDD passes. Other checks may stay MISSING (sibling tasks).
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "A) SDD Definition-of-Done accretion clause ... a task that introduces a new runnable capability is not DONE until its verb is declared in the command surface AND verified to run — event-driven, bound into the task DoD"

## Task 3 — implementer accretion obligation (B)

- **Description**: In `agents/implementer.md`, in the hand-authored role-contract region (NOT inside the `<!-- BEGIN/END baseline-v1 -->` L65 or `<!-- BEGIN/END rule-sheet-v1 -->` L175 managed blocks), add the accretion obligation: when the task adds a runnable capability, the implementer (1) **verify-before-declare** — run the new verb and confirm it works (Rule 12 fail-loud; never declare an unrun verb); (2) declare it in the project `AGENTS.md` inside a `<!-- BEGIN command-surface (managed) -->` / `<!-- END command-surface (managed) -->` block, extending an existing `## Commands` section rather than duplicating and never clobbering human-authored prose (Q4); (3) if the repo has no `CLAUDE.md`, create a thin one containing `@AGENTS.md` (Q7 shim); (4) reuse v1's declared-first resolution to locate/extend the surface — do NOT auto-scan or build a surface from zero (⑤ out of scope). MUST contain literals `verify-before-declare` AND `BEGIN command-surface (managed)`.
- **Module**: `code-toolkit/agents/implementer.md`
- **Files touched**: `code-toolkit/agents/implementer.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/implementer.md` (role contract L12-63; managed blocks L65+L175 OFF-LIMITS; I/O L218+)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/scripts/distribute.py` (L168/L209 — BEGIN/END marker style to mirror)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/test-command-surface-accretion.sh` (CHECK-ACCRETE-IMPL is yours)
- **Acceptance**:
  - **RED**: CHECK-ACCRETE-IMPL reports MISSING.
  - **GREEN**: both literals present; obligation lives OUTSIDE both managed blocks; `python3 code-toolkit/scripts/verify-drift.py` exits 0; harness CHECK-ACCRETE-IMPL passes. Paste the harness line + verify-drift exit.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "B) implementer accretion obligation ... verify-before-declare ... declare it in AGENTS.md inside a <!-- BEGIN command-surface (managed) --> block ... @AGENTS.md shim ... reuse v1 resolution; do NOT auto-scan"

## Task 4 — writing-plans capability-task marker (C)

- **Description**: In `writing-plans/SKILL.md`, add a short note (in the splitting framework or near the acceptance-criterion guidance) that a task which adds a **runnable capability** (new test suite / build / lint / e2e / migrate) should carry an acceptance line naming "the new verb is declared in the command surface and verified to run" — so accretion is visible at plan time, not only caught at SDD's Definition of Done. Additive note only; do not restructure the splitting framework, the depth ceiling, or the plan schema. MUST contain literal `runnable capability`.
- **Module**: `code-toolkit/skills/writing-plans/SKILL.md`
- **Files touched**: `code-toolkit/skills/writing-plans/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/writing-plans/SKILL.md` (L52-57 splitting framework / acceptance criterion)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/test-command-surface-accretion.sh` (CHECK-ACCRETE-PLAN is yours)
- **Acceptance**:
  - **RED**: CHECK-ACCRETE-PLAN reports MISSING.
  - **GREEN**: literal `runnable capability` present in an additive plan-time accretion-marker note; splitting framework otherwise unchanged; harness CHECK-ACCRETE-PLAN passes.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "C) writing-plans capability-task marker ... a task that adds a runnable capability gets an acceptance line naming 'the new verb is declared in the command surface and verified to run'"

## Task 5 — accretion behavioral pressure prompt

- **Description**: Add `code-toolkit/tests/verification-before-completion-pressure/prompts/accretion-declare-new-verb.txt` — a single realistic user message: a task just added an end-to-end (e2e) test suite to a project, and the user says it's done / asks to commit. Add a matching MUST/MUST NOT row to that dir's `index.md`. Acceptance rules to encode: MUST declare the new verb (e.g. `test-e2e`) in the command surface (AGENTS.md managed block) AND verify it runs before marking DONE (verify-before-declare); MUST extend, not clobber, any human-authored AGENTS.md section; MUST NOT pre-declare a capability that does not exist (no `deploy` verb before deploy); MUST NOT skip declaration ("I'll add it later"). The literal token `accretion-declare-new-verb` MUST appear in index.md. Update the cluster acceptance count line (4 → 5). Do not alter the other four prompt entries.
- **Module**: `code-toolkit/tests/verification-before-completion-pressure/prompts`
- **Files touched**: `code-toolkit/tests/verification-before-completion-pressure/prompts/accretion-declare-new-verb.txt`, `code-toolkit/tests/verification-before-completion-pressure/prompts/index.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/verification-before-completion-pressure/prompts/index.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/verification-before-completion-pressure/prompts/declared-surface-vs-detection.txt` (v1's prompt — match terseness/format)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/test-command-surface-accretion.sh` (CHECK-ACCRETE-PRESSURE is yours)
- **Acceptance**:
  - **RED**: CHECK-ACCRETE-PRESSURE reports MISSING.
  - **GREEN**: new `.txt` exists with the e2e-accretion scenario; `index.md` has the MUST/MUST NOT row referencing `accretion-declare-new-verb`; count line updated 4→5; harness CHECK-ACCRETE-PRESSURE passes.
- **Dependencies**: Tasks 2, 3 complete first
- **Independent**: false
- **Brief item covered**: "a behavioral accretion pressure prompt (a task adds an e2e suite → must declare test-e2e + verify it runs before DONE; must NOT pre-declare a non-existent capability; must NOT clobber human AGENTS.md sections)"

## Notes

- **Wave shape**: Task 1 (level 0) → Tasks 2, 3, 4 as a **3-wide parallel wave** (all `Independent: true`, disjoint `Files touched`: SDD SKILL / implementer / writing-plans SKILL) → Task 5 at level 2 (mirrors Task 2+3 rule wording, doc-mirrors-code → `Independent: false`). Critical-path depth = 3.
- **No producer/consumer field contract this time** (unlike v1's `Resolved test command`): A (SDD DoD) and B (implementer) share the *concept* but no literal field both must match, so T2/T3 are genuinely independent. The managed-block marker `BEGIN command-surface (managed)` is written by B and mirrored by the T5 pressure prompt's rules.
- **SSOT guard**: only Task 3 touches a file (`implementer.md`) with distribute-managed blocks; its GREEN re-asserts `verify-drift.py` exit 0. No task edits standards/rubrics/checklists or distribute-owned blocks.
- **Scope reminder**: this plan is the accretion DISCIPLINE only — no seed preflight (④ other half), no seed builder (⑤), no executable surface-writing tool. The implementer writes the AGENTS.md managed block by hand following the prose convention.
- **Check-15 advisory expected**: Task 4 and Task 5 are disjoint with no edge; T4 is `Independent: true` (level 1), T5 `Independent: false` (level 2, deps T2/T3) — no conflict.
- **Final verification**: after all tasks GREEN, `test-command-surface-accretion.sh` exits 0 — package-level evidence for verification-before-completion.
