# Plan: Command Surface v1 (野心 A — command resolution)

**Source brief**: code-toolkit/docs/code-toolkit/specs/2026-06-10-command-surface-v1-brief.md
**Total tasks**: 6
**Critical-path depth**: 3 (≤5 ✓ — longest chain: Task 1 → Task 4 → Task 5)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-10 12:43 CST) — 14/14; 2 advisory notes (Check 15 missed-parallel T5/T6 pre-justified; Task 6 Module is a dir w/ 2 files — scope reviewer to the dir)

> **TDD shape for prose edits**: Task 1 builds a deterministic grep-based assertion harness whose checks are RED against the current (unedited) files. Each edit task (2–6) flips exactly its own check from RED→GREEN. This makes "no production change without a failing test first" literal even for prose: the failing test already exists (Task 1) before each edit lands.
>
> **Canonical assertion phrases** (the harness greps these verbatim; edit tasks MUST produce them exactly so the contract is unambiguous):
> - CHECK-① (`test-invocation-by-stack.md`): contains `consult the project-declared surface first` AND `only if it runs and emits a test count`
> - CHECK-② (`verification-before-completion/SKILL.md`): contains `Resolve the test command` AND `declared-first`
> - CHECK-③a (`subagent-driven-development/SKILL.md`): contains `Resolved test command` AND `session-scoped`
> - CHECK-③b (`agents/implementer.md`): contains `Resolved test command`
> - CHECK-PRESSURE: file `tests/verification-before-completion-pressure/prompts/declared-surface-vs-detection.txt` exists AND that dir's `index.md` references `declared-surface-vs-detection`

## Task 1 — Build the grep assertion harness (the failing test)

- **Description**: Create `code-toolkit/tests/integration/test-command-surface-resolution.sh`, an executable bash test modeled on `test-rule-sheet-drift.sh` (`set -euo pipefail`, `REPO_ROOT` resolution, `die()` helper, clear per-check `FAIL —`/`ok` lines). Implement the five CHECK groups above as independent grep/`test -f` assertions, each printing `MISSING: <check-id>` and accumulating a nonzero exit when its phrase/file is absent. The script must exit 1 and list all five as MISSING when run against the current unedited tree, and exit 0 only when all five are satisfied. Do NOT edit any of the five target files in this task — only the harness.
- **Module**: `code-toolkit/tests/integration/test-command-surface-resolution.sh`
- **Files touched**: `code-toolkit/tests/integration/test-command-surface-resolution.sh`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/integration/test-rule-sheet-drift.sh`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/README.md`
- **Acceptance**:
  - **RED**: `bash code-toolkit/tests/integration/test-command-surface-resolution.sh` does not exist / is not executable yet (no harness).
  - **GREEN**: the harness exists, is valid bash, runs from repo root, and against the **current unedited** tree exits **nonzero** while printing `MISSING:` for all five CHECK ids (CHECK-①, ②, ③a, ③b, PRESSURE) — i.e. it correctly detects the absence the edit tasks will fill.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "a deterministic executable assertion (grep-based, in the style of tests/integration/test-rule-sheet-drift.sh) that asserts each required rule string is present in ①②③ — RED before edits, GREEN after"

## Task 2 — Priority-0 declared-surface step in the detection table (①)

- **Description**: In `test-invocation-by-stack.md`, add a "Priority 0 — consult the declared surface first" subsection **ahead of** the signal→command table. It must encode: (a) `consult the project-declared surface first` (AGENTS.md commands / `make`/`just` `test` recipes / README), preferring a granular `test` verb; (b) trust earned by execution — the declared verb outranks detection `only if it runs and emits a test count`, else fall back; (c) never hard-fail on a broken declaration — fall back to the table. Reframe the `:7` intro line from pure "Detect by signal files" to declared-first resolution (detection = fallback), and note Makefile/justfile may now be consulted as a declared surface rather than only the bottom-of-table Generic fallback. Do not delete the existing table or the "Detecting 0 tests ran" section.
- **Module**: `code-toolkit/skills/verification-before-completion/references/test-invocation-by-stack.md`
- **Files touched**: `code-toolkit/skills/verification-before-completion/references/test-invocation-by-stack.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/verification-before-completion/references/test-invocation-by-stack.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/docs/code-toolkit/specs/2026-06-10-command-surface-establishment.md` (§4.1)
- **Acceptance**:
  - **RED**: CHECK-① in `test-command-surface-resolution.sh` reports MISSING (phrases `consult the project-declared surface first` / `only if it runs and emits a test count` absent).
  - **GREEN**: both CHECK-① phrases present; the priority-0 step sits ahead of the table; detection retained as explicit fallback; harness CHECK-① passes.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "① detection table (test-invocation-by-stack.md) — add a priority-0 step ahead of the signal table: consult the project-declared surface first; a declared verb outranks detection ONLY if it runs and emits a test count, else fall back"

## Task 3 — "Detect" → "Resolve" in vbc Process step 1 (②)

- **Description**: In `verification-before-completion/SKILL.md` Process step 1 (currently L51, "**Detect** the package-level test command"), change to "**Resolve** the test command (`declared-first` consult; the declaration wins only if it runs and emits a test count; else fall back to detection)" and keep the existing reference link to `references/test-invocation-by-stack.md`. Surgical wording change to step 1 only; do not touch steps 2–5 or other sections.
- **Module**: `code-toolkit/skills/verification-before-completion/SKILL.md`
- **Files touched**: `code-toolkit/skills/verification-before-completion/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/verification-before-completion/SKILL.md` (L49-56)
- **Acceptance**:
  - **RED**: CHECK-② reports MISSING (`Resolve the test command` / `declared-first` absent from SKILL.md).
  - **GREEN**: step 1 contains `Resolve the test command` and `declared-first`; reference link to the stack table preserved; harness CHECK-② passes.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "② vbc gate (verification-before-completion/SKILL.md:51) — step 1 'Detect the package-level test command' → 'Resolve the test command (declared-first consult; ...; else fall back to detection)'"

## Task 4 — Pass resolved verb down + session cache in SDD dispatch (③a)

- **Description**: In `subagent-driven-development/SKILL.md` Process — per-task triad step 1 (currently L93), add that the orchestrator **resolves** the test command once via vbc's declared-first rule, **caches it `session-scoped`** (re-resolve across sessions because declarations rot; optionally invalidate if the declaring file's content-hash changes mid-session), and passes it into the implementer dispatch as a `Resolved test command` line in the dispatch prompt. Surgical addition to step 1; do not alter the verdict-resolution table or other sections.
- **Module**: `code-toolkit/skills/subagent-driven-development/SKILL.md`
- **Files touched**: `code-toolkit/skills/subagent-driven-development/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/subagent-driven-development/SKILL.md` (L89-100)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/implementer.md` (L218-239, input contract — the field name must match Task 5)
- **Acceptance**:
  - **RED**: CHECK-③a reports MISSING (`Resolved test command` / `session-scoped` absent from sdd SKILL.md).
  - **GREEN**: step 1 names the `Resolved test command` passed to the implementer and a `session-scoped` cache with re-resolve-across-sessions; harness CHECK-③a passes.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: "③a SDD dispatch (subagent-driven-development/SKILL.md:93) — pass the resolved verb down in the implementer dispatch; resolve once, cache session-scoped, re-resolve across sessions (Q6)"

## Task 5 — Receive + use resolved verb in implementer input contract (③b)

- **Description**: In `agents/implementer.md` Input contract (the `### Resource Paths` block, L218-239), add a `Resolved test command` field the orchestrator MAY supply, and instruct the implementer to USE it for package-level test runs instead of re-detecting — falling back to detection (`references/test-invocation-by-stack.md`) only when the field is absent. Field name MUST match Task 4's dispatch line exactly (`Resolved test command`). **Do NOT touch the `<!-- BEGIN/END baseline-v1 -->` (L65) or `<!-- BEGIN/END rule-sheet-v1 -->` (L175) managed blocks** — they are distribute.py-owned and guarded by verify-drift.py.
- **Module**: `code-toolkit/agents/implementer.md`
- **Files touched**: `code-toolkit/agents/implementer.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/agents/implementer.md` (L218-260, input/output contract)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/subagent-driven-development/SKILL.md` (the producer side from Task 4)
- **Acceptance**:
  - **RED**: CHECK-③b reports MISSING (`Resolved test command` absent from implementer.md).
  - **GREEN**: input contract documents the `Resolved test command` field + use-it-else-detect instruction; harness CHECK-③b passes; `python3 code-toolkit/scripts/verify-drift.py` still exits 0 (managed blocks untouched).
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: "③b implementer contract (agents/implementer.md Input contract) — receive the resolved test verb and use it for package-level test runs instead of re-detecting (closes the producer/consumer contract)"

## Task 6 — Behavioral pressure prompt for the declared-surface scenario

- **Description**: Add a new pressure prompt `tests/verification-before-completion-pressure/prompts/declared-surface-vs-detection.txt` (one user-message body: a project that declares `make test` in AGENTS.md AND is also pytest-detectable; the agent must consult the declaration first, but fall back to detection if the declared verb emits no parseable test count). Add a matching MUST/MUST NOT row to that directory's `index.md` (MUST consult declared surface first; MUST fall back — not hard-fail — when the declared verb runs but emits no `N passed`; MUST NOT blindly trust the declaration; MUST NOT use a bundled `check` as the gate). Keep the index's "3 of N prompts" acceptance line consistent.
- **Module**: `code-toolkit/tests/verification-before-completion-pressure/prompts`
- **Files touched**: `code-toolkit/tests/verification-before-completion-pressure/prompts/declared-surface-vs-detection.txt`, `code-toolkit/tests/verification-before-completion-pressure/prompts/index.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/verification-before-completion-pressure/prompts/index.md`
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/tests/verification-before-completion-pressure/prompts/tests-pass-no-invocation.txt`
- **Acceptance**:
  - **RED**: CHECK-PRESSURE reports MISSING (`declared-surface-vs-detection.txt` absent / not referenced in `index.md`).
  - **GREEN**: the new `.txt` exists with the declared-surface scenario; `index.md` has the MUST/MUST NOT row referencing `declared-surface-vs-detection`; harness CHECK-PRESSURE passes.
- **Dependencies**: Tasks 2, 3 complete first
- **Independent**: false
- **Brief item covered**: "a behavioral pressure prompt in tests/verification-before-completion-pressure/prompts/ (a declared-surface scenario ...) + its index.md MUST/MUST NOT row"

## Notes

- **Wave shape**: Task 1 (level 0) → Tasks 2, 3, 4 run as one **3-wide parallel wave** (all `Independent: true`, disjoint `Files touched`: detection table / vbc SKILL / sdd SKILL) → Task 5 (needs Task 4 for the field-name contract) and Task 6 (mirrors the Task 2/3 rule wording) at level 2. Critical-path depth = 3.
- **Tasks 5 and 6** touch disjoint files and have no edge between them; they *could* run parallel at level 2, but each carries a real semantic dependency to its producer (5→4 field-name match; 6→2,3 doc-mirrors-rule), so both are left `Independent: false`. (Expect a Check-15 advisory NOTE — benign.)
- **SSOT guard**: only Task 5 touches a file (`implementer.md`) that contains distribute-managed blocks; its GREEN explicitly re-asserts `verify-drift.py` exit 0. No task edits standards/rubrics/checklists.
- **Final verification**: after all tasks GREEN, `test-command-surface-resolution.sh` exits 0 (all five checks) — that is the package-level evidence for verification-before-completion.
