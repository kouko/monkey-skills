# Plan: principles replay loop — L1 matrix workflow + L2 traceability checker

**Source brief**: docs/loom/specs/2026-07-10-principles-replay-loop.md
**Total tasks**: 5
**Critical-path depth**: 3 (≤5 ✓) — longest chain: Task 1 → Task 2 → Task 3 (Task 4 joins at the same level as Task 3; Task 5 is a leaf)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-10, 14/14 checks; fresh-context evaluator)

## Task 1 — Oracle parser in check_seed_traceability.py

- **Description**: Create `loom-product-principles/scripts/check_seed_traceability.py` with a public `parse_oracle(text: str) -> dict` that extracts the three checker-scope keys from an oracle document: `named_anchors`, `deferred_items`, `negative`. Contract (this parser DEFINES the oracle format contract, per brief): each key is a flat `key: value` line; a value is a `;`-separated list of exact match tokens; `none in this seed` (or an absent key) parses to an empty list; a document carrying none of the three keys raises a `ValueError` naming what is missing. Other oracle keys (`stances:`, `out_of_jurisdiction_bait:`) are ignored by design — out of checker scope (brief §Level 2). Document the contract in the module docstring.
- **Module**: `loom-product-principles/scripts/check_seed_traceability.py`
- **Files touched**: `loom-product-principles/scripts/check_seed_traceability.py`, `loom-product-principles/scripts/test_check_seed_traceability.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-10-principles-replay-loop.md (brief §Level 2)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/seed4-oracle.md (current key shape)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/seed1-oracle.md (`none in this seed` case)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/test_validate_principles_output.py (test conventions: same-dir bare import, tmp_path inline fixtures, no conftest)
- **Acceptance**:
  - **RED**: `test_check_seed_traceability.py::test_parse_oracle_extracts_three_token_lists` fails (module does not exist)
  - **GREEN**: `parse_oracle` returns the expected token lists for an inline fixture covering all three keys, `;`-separated multi-token values, and `none in this seed` → `[]`
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: §Level 2 — "parses the oracle's `named_anchors:` / `deferred_items:` / `negative:` lists"; "The script's parser defines the oracle format contract"

## Task 2 — Artifact checks + CLI exit codes

- **Description**: In the same module, add the three check functions and `main(argv)` so `python3 check_seed_traceability.py <artifact> <oracle>` verifies: (a) every `named_anchors` token appears in an `## Anchors` table data row whose version cell (second `|` cell) is non-empty; (b) every `deferred_items` token appears in an `## Open Questions` entry that carries `— re-trigger:` on the same line; (c) every `negative` token is absent from the artifact. Exit 0 when all pass; exit 1 with one line per miss in the form `<class>: <token>` (stderr). Do NOT duplicate any of `validate_principles_output.py`'s 8 structural checks (the checker composes with it; the workflow runs both).
- **Module**: `loom-product-principles/scripts/check_seed_traceability.py`
- **Files touched**: `loom-product-principles/scripts/check_seed_traceability.py`, `loom-product-principles/scripts/test_check_seed_traceability.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/validate_principles_output.py (exit-code convention `:375-383`; the 8 checks NOT to duplicate `:340-349`)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/references/principles-rules.md (Anchors table row shape `:185-197`; Open Questions entry shape `:284-294`)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/SKILL.md (§seed-traceability invariant, `(agent-decided)` end-of-line marker)
- **Acceptance**:
  - **RED**: `test_check_seed_traceability.py::test_missing_named_anchor_exits_1_naming_the_miss` fails (subprocess CLI run on tmp_path fixtures; `main` not implemented)
  - **GREEN**: conformant artifact+oracle pair → exit 0; an artifact missing an anchor row / an OQ re-trigger entry / containing a negative token → exit 1 with each miss named `<class>: <token>`
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: §Level 2 — "verifies against the artifact: every named anchor has a non-empty-version `## Anchors` data row; every deferred item has an `## Open Questions` entry carrying `— re-trigger:`; every negative string is absent. Exit 0 / exit 1 naming every miss"

## Task 3 — Normalize the 6 committed oracles to the parser contract

- **Description**: Normalize the values of `named_anchors:` / `deferred_items:` / `negative:` in `seed1..5-oracle.md` to exact greppable tokens per the Task 1 contract (tokens must be strings the Task 2 checks can match literally in an artifact); leave `stances:` and `out_of_jurisdiction_bait:` untouched (out of checker scope, stays prose for LLM/human graders). ADD a machine-readable key block (the three keys) to `docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md` §Oracle — that Oracle is a living doc (calibrated in #532); append the block without deleting its existing prose assertions. Add regression test `test_committed_oracles_conform_to_parser_contract` (parses all 6 committed oracle sources; asserts non-empty `named_anchors` everywhere and expected empty/non-empty `deferred_items`/`negative` per seed).
- **Module**: `docs/loom/dogfood/` (oracle data files)
- **Files touched**: `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/seed1-oracle.md`, `seed2-oracle.md`, `seed3-oracle.md`, `seed4-oracle.md`, `seed5-oracle.md`, `docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md`, `loom-product-principles/scripts/test_check_seed_traceability.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/README.md (grader contract; canonical key set)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md (§Oracle current prose format `:49-69`)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/check_seed_traceability.py (the contract, produced by Tasks 1-2)
- **Acceptance**:
  - **RED**: `test_check_seed_traceability.py::test_committed_oracles_conform_to_parser_contract` fails on today's committed oracles (prose-qualified values in seed1..5; no machine keys in seed.md §Oracle)
  - **GREEN**: `parse_oracle` extracts the expected token lists from all 6 committed oracle sources; frozen dogfood files (`report.md`, `transcript.md`, `instrument*.md`, `matrix-results.md`) untouched
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: true
- **Brief item covered**: §Level 2 — "the 5 corpus oracles are normalized to greppable tokens in the same change" (seed.md's living Oracle joins the same contract so the L1 workflow can grade all 6 seeds)

## Task 4 — L1 replay-matrix Workflow script

- **Description**: Write `.claude/workflows/principles-replay-matrix.js`: `export const meta = { name: 'principles-replay-matrix', description, phases: [{title: 'Replay'}, {title: 'Grade'}] }`; `args = { runLabel, sandboxDir, seeds? }` (timestamps/labels come in via args — Workflow scripts cannot call `Date.now()`); pipeline over the 6 committed seed pairs (5 corpus `seedN-input.md`/`seedN-oracle.md` + cold-operator `seed.md` as both input §Seed and oracle §Oracle) → **Replay stage**: `agent(…, {model: 'haiku', phase: 'Replay'})` instructed to execute the product-principles SKILL.md §Headless/seeded mode on the seed input and Write the artifact to `<sandboxDir>/<runLabel>/<seed>/PRINCIPLES.md` → **Grade stage**: agent runs ONLY `python3 loom-product-principles/scripts/validate_principles_output.py <artifact>` and `python3 loom-product-principles/scripts/check_seed_traceability.py <artifact> <oracle>` via Bash, saves raw stdout/stderr+exit codes to `<sandboxDir>/<runLabel>/<seed>/grade.txt`, and returns them schema-forced; the script computes each verdict from the two exit codes alone — no LLM self-report anywhere in the verdict path (grade agents are couriers; their claims are re-checkable because artifact + grade.txt paths are returned for on-disk re-verification). Return a per-seed pass table + overall pass-rate (eval semantics, never per-push CI). Add `loom-product-principles/scripts/test_replay_matrix_workflow.py` with static assertions on the committed .js text.
- **Module**: `.claude/workflows/principles-replay-matrix.js`
- **Files touched**: `.claude/workflows/principles-replay-matrix.js`, `loom-product-principles/scripts/test_replay_matrix_workflow.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.claude/workflows/code-toolkit-sweep.js (meta block + pipeline/agent invocation conventions; read-only — another arc's file)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-10-principles-replay-loop.md (brief §Level 1 + §Acceptance)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/README.md (seed list)
- **External surfaces**:
  - Internal host contract: Claude Code Workflow script runtime (`export const meta`, `agent()`/`pipeline()`/`phase()`/`log()`, no `Date.now()`/`Math.random()`) — grounding: in-repo evidence `.claude/workflows/code-toolkit-sweep.js` + in-context Workflow tool schema (captured 2026-07-10)
- **Acceptance**:
  - **RED**: `test_replay_matrix_workflow.py::test_meta_block_and_deterministic_grade_stage` fails (workflow file does not exist)
  - **GREEN**: static assertions pass — meta block parses with expected name and both phase titles; all 6 seed pair paths present; grade-stage text names ONLY the two scripts as verdict inputs (no other verdict source); no `Date.now(`/`Math.random(` anywhere in the file
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: §Level 1 — "fans out one haiku headless replay per seed to a sandbox, then grades each artifact MECHANICALLY (validator + the Level-2 checker; no LLM self-report anywhere in the verdict path) and returns a pass-rate table"

## Task 5 — BACKLOG harness entry points at brief §Level 3

- **Description**: Update the existing `## Dogfood replay/eval harness for the principles construction flow (OPEN)` entry in `docs/loom/BACKLOG.md`: record that L1 (replay-matrix workflow) + L2 (traceability checker) ship in this arc, and make the remaining open item the L3 autonomous loop pointing at `docs/loom/specs/2026-07-10-principles-replay-loop.md` §Level 3 for the design + four guardrails INSTEAD of restating them (point-don't-copy). Keep the entry's required fields (Status / Start / Origin / What) per the BACKLOG header convention; re-trigger stays "several rounds of real L1/L2 data".
- **Module**: `docs/loom/BACKLOG.md`
- **Files touched**: `docs/loom/BACKLOG.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/BACKLOG.md (header format `:2-12`; existing entry `:46-89`)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-10-principles-replay-loop.md (§Level 3)
- **Acceptance**:
  - **RED**: diagnostic — `grep -c '2026-07-10-principles-replay-loop' docs/loom/BACKLOG.md` returns 0 today
  - **GREEN**: the entry cites the brief §Level 3 as SSOT for the L3 design; no guardrail list duplicated into BACKLOG; Status/Start/Origin/What fields intact
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Acceptance — "BACKLOG harness entry points at this brief's §Level 3 instead of restating"; §Level 3 — "autonomous improvement loop (DESIGN ONLY, BACKLOG)"

## Notes

- **Matrix-artifact caveat (from handoff)**: the 6 graded matrix artifacts lived in a session scratchpad that no longer exists. The checker's acceptance therefore runs against synthetic tmp_path fixtures (Tasks 1-2) + the committed oracles (Task 3); spot-reproduction of the committed matrix verdicts is possible later via 1-2 fresh replays of the Task 4 workflow — do not block on the old scratchpad.
- **Retry-on-miss deliberately out of scope**: the brief names a "future conductor retry-on-miss loop" as a checker CONSUMER, not as part of L1. The workflow returns verdicts; it does not retry.
- **Checker scope exclusions are by design** (brief §Level 2): `stances:` and `out_of_jurisdiction_bait:` need semantic judgment and stay with LLM graders/humans. Do not "improve" the checker to cover them.
- **Do Not Touch (from handoff)**: frozen dogfood records (`instrument*.md`, `report.md`, `transcript.md`, `matrix-results.md`); the other sessions' untracked files (never `git add -A`); SKILL.md prose (word budget 2,266/4,500 — this plan adds no SKILL.md text, and no 4th round of anchor-drop prose).
- Tasks 3 and 4 sit at the same dependency level after Task 2 with disjoint `Files touched` → parallel-eligible. Task 5 is a free leaf, dispatchable any time.
- **Post-review amendments (additive; schema/DAG unchanged — re-review skipped per writing-plans amendment rule)**: (1) T2's new CLI is deliberately NOT declared in AGENTS.md's command-surface block — spec-reviewer verified the precedent (block covers repo-wide/CI gates; the sibling validator CLI is likewise absent). (2) Round-2 fix commits beyond the 5 task commits: T4 🔴 courier null-guard + runLabel allow-list (4ba5eef3); debt bundle from PASS_WITH_NOTES findings — T2 file-existence guard (exit 2) + T3 exemplar-token pins (f79dff65), T5 BACKLOG content restore (85a2044b).
