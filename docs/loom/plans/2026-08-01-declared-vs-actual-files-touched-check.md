# Plan: Measure the declared-vs-actual `Files touched` check

**Source brief**: docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md
**Total tasks**: 8
**Critical-path depth**: 4 (≤5 ✓ — longest chains T1→T3→T4→T5 and T2→T6→T7→T8, both 4)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-08-01, round 2, 15/15)

## Task 1 — Freeze the answer key in the audit document

- **Description**: Author `docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md` containing the frozen measurement design, BEFORE any comparator code exists: (1) a `## Frozen answer key` section with one row per fixture cell (cells 1–10 exactly as enumerated in the brief §Fixture cells), each row carrying the cell's construction spec, its ground-truth label (flag-worthy: yes/no, with the one-line reason), and the expected verdict under each rule variant R1 / R2 / R3 (variants as defined in the brief §Rule variants); (2) a `## Results` section that is explicitly a placeholder — it contains only the literal marker line `RESULTS-PENDING — frozen before implementation; results land in Task 5.`; (3) a `## Retro-fit` section with the same placeholder marker and the selection-bias label already in place. Ground-truth labels follow the brief's Boundary findings: regenerated functional copies and codex-mirror manifests are under-declaration targets, never excludes (source brief §Current State Evidence, Boundary bullet).
- **Module**: `docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`
- **Files touched**: NEW: `docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md
  - /Users/kouko/GitHub/monkey-skills/docs/loom/memory/files-touched-misses-machinery-coupled-files.md
  - /Users/kouko/GitHub/monkey-skills/docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md (the frozen-key discipline precedent)
- **Acceptance**:
  - **RED**: diagnostic — `test -f docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md` exits 1 (file absent)
  - **GREEN**: file exists; `## Frozen answer key` table has exactly 10 rows, every row filled in all three variant columns plus a ground-truth column; `## Results` and `## Retro-fit` contain the literal `RESULTS-PENDING` marker and no result numbers
- **Dependencies**: none
- **Independent**: false  # NEW path — disjointness oracle untrusted per plan-format.md:79
- **Review-weight**: prose
- **Brief item covered**: "Frozen answer key: every cell's expected verdict is written into the audit document and the test file BEFORE the comparator is implemented"
- **Status**: done(3566a164)

## Task 2 — Parse a plan's declared files and join keys

- **Description**: Create `scripts/check_files_touched.py` (top level, sibling to `scripts/check_loom_memory_integrity.py`) with the parse layer only: given a plan markdown path, return per-task structures `{task_no: (declared_paths, sha_or_None)}`. Must handle: bolded `**Files touched**:` and plain `Files touched:` field forms; comma-separated values; backticked or bare paths; the `NEW: <path>` token (normalize to the proposed path — plan-format.md:79); `Status: done(<sha>)` extraction (plan-format.md:106). Field lines that match the field name but fail to parse are collected into a `parse_errors` list — never silently dropped (the citation-checker empty-pass lesson, source brief §Decision). Write the failing test first in `scripts/test_check_files_touched.py`.
- **Module**: `scripts/check_files_touched.py`
- **Files touched**: NEW: `scripts/check_files_touched.py`, NEW: `scripts/test_check_files_touched.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/scripts/check_scenario_coverage.py (pattern reference — idiom copied, not imported)
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/plan-format.md (field grammar: lines 49, 68–71, 79, 106)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md
- **Acceptance**:
  - **RED**: `scripts/test_check_files_touched.py::test_parse_declared_files_bold_and_plain_forms` fails (module does not exist)
  - **GREEN**: parser returns declared sets + join keys for a corpus covering both field forms, backticked/bare, `NEW:` token, and a missing-`Status` task (returns `None` sha); malformed field lines land in `parse_errors`
- **Reuse-adequacy**:
  - **Observed**: `check_scenario_coverage.py` parses real plan markdown with two idioms — a bold-optional field-line regex (`^\s*-\s*(?:\*\*)?Brief item covered(?:\*\*)?\s*:\s*(.+)$`, accepting both the schema's bolded form and the plain form real plans use) and a section-boundary regex `^#{2,3}\s` whose documented limitation is that a fenced code block containing `## `-prefixed lines is still mistaken for a real heading — read loom-code/scripts/check_scenario_coverage.py:58-68
  - **Intended**: the new parser applies the same two idioms with the field name swapped to `Files touched` / `Status`, adding comma-splitting, backtick-stripping, and `NEW:` normalization on the captured value; the idiom is copied into the new module, not imported, and the fenced-heading limitation carries over unchanged — therefore the fixture plans Task 4 authors must not embed fenced blocks containing `## Task` lines
- **Dependencies**: none
- **Independent**: false  # NEW paths — plan-format.md:79
- **Brief item covered**: "parses a real plan's per-task `Files touched` + `Status: done(<sha>)`" (brief §Smallest End State item 1)
- **Status**: done(9b45b937)

## Task 3 — Verdict engine with the three rule variants

- **Description**: Add pure verdict functions to `scripts/check_files_touched.py`: given (declared_paths, actual_paths, plan_path) return a structured verdict per rule variant — R1 flags any symmetric difference (both directions); R2 flags only `actual − declared ≠ ∅` (UNDER, the dangerous direction); R3 is R2 computed after removing standing excludes from the actual set (exactly two exclude classes: the plan file itself, and any path containing `__pycache__/`). A task whose sha is `None` yields verdict `NO_JOIN` under every variant — never `OK`. Verdicts carry the offending paths (UNDER list / OVER list) for reporting. Variant semantics are the brief's §Rule variants table, verbatim.
- **Module**: `scripts/check_files_touched.py`
- **Files touched**: `scripts/check_files_touched.py`, `scripts/test_check_files_touched.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md (§Rule variants)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md (frozen key — produced by Task 1)
- **Acceptance**:
  - **RED**: `scripts/test_check_files_touched.py::test_rule_variants_diverge_on_over_declaration` fails — the test constructs an over-declaration input on which R1 MUST flag and R2/R3 MUST return OK, so the three variants are discriminated by construction (a cell where all variants agree cannot fail this test; input chosen per docs/loom/memory/a-test-can-be-correct-and-still-unable-to-fail.md)
  - **GREEN**: engine verdicts on synthetic sets match the brief's variant table, including `NO_JOIN` on missing sha and the two standing excludes applying to R3 only
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false
- **Brief item covered**: "Rule variants measured (all three run over the same cells)" (brief §Rule variants table)
- **Status**: done(88423c32)

## Task 4 — Git layer, CLI, and the ten-cell corpus end-to-end

- **Description**: Complete `scripts/check_files_touched.py`: (1) `actual_files(repo, sha)` running `git show --name-only --format= <sha>` via subprocess, with rename lines accounted per the frozen key's cell-8 convention; (2) a CLI `python3 scripts/check_files_touched.py <plan-path> [--repo <path>] [--variant R1|R2|R3|all]` printing per-task verdicts; (3) loud-empty behaviour: exit 2 with a message naming what was empty when the parse finds 0 tasks OR 0 join keys — a plan with no ledger must never produce an all-clear (source brief §Decision). In `scripts/test_check_files_touched.py`, build sandbox git repositories under pytest `tmp_path` (real `git init/add/commit` — real producer output, never hand-typed diffs, per docs/loom/memory/fixtures-mirror-producer-shape.md) reproducing cells 1–10 exactly as constructed in the frozen key, and assert each cell's frozen expected verdict for every variant in one parametrized test.
- **Module**: `scripts/check_files_touched.py`
- **Files touched**: `scripts/check_files_touched.py`, `scripts/test_check_files_touched.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md (frozen key — the cell corpus SSOT)
  - /Users/kouko/GitHub/monkey-skills/scripts/check_version_bump.py (subprocess-git harness pattern: `changed_paths()`, line 60)
- **Acceptance**:
  - **RED**: `scripts/test_check_files_touched.py::test_cells_match_frozen_answer_key` fails (git layer and CLI absent)
  - **GREEN**: all 10 cells produce their frozen verdicts under all three variants; the empty-parse CLI paths exit 2 with an explicit message; `python3 -m pytest scripts/ -q` green (the new suite is collected by loom-code CI's existing `pytest … scripts/ …` step — .github/workflows/loom-code-ci.yml:98 — so the runnable capability needs no new command-surface entry)
- **External surfaces**:
  - CLI flag: `git show --name-only --format=` — grounding: `git show --help` (captured 2026-08-01); sandbox uses `git init` / `git add` / `git commit` with `-c user.email/-c user.name` overrides, same grounding
- **Dependencies**: Tasks 1, 3 complete first
- **Independent**: false
- **Brief item covered**: "runs `git show --name-only --format= <sha>`, and emits a per-task verdict: `OK` / `UNDER` / `OVER` / `NO_JOIN`" + "the comparator fails LOUD on empty parses (0 tasks, 0 join keys)"
- **Status**: done(eedf33d3)

## Task 5 — Run the measurement, retro-fit the three real instances, complete the report

- **Description**: Replace the audit document's `RESULTS-PENDING` markers: (1) `## Results` — per-variant confusion tables (rule output vs frozen ground truth over cells 1–10) computed by running the Task-4 CLI/tests, plus the false-alarm/miss counts per variant; (2) `## Retro-fit` — run the CLI against the three real instances with their ORIGINAL declarations (recovered via `git show 293d446c:docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md`; task commits live only on the LOCAL branch `docs-reuse-adequacy-brief-and-backlog` — T3's is `c82c93cd`, T4's is `0c03c0e8`, T6's the implementer identifies from `git log` on that branch; the branch was squash-merged so these shas are machine-local); keep the section labeled selection-biased and outside the headline numbers; (3) `## Limitations` — one-sha-per-task; ledger optionality (how loud the inert NO_JOIN case reports); machine-local retro-fit provenance (not CI-reproducible); (4) `## Recommendation` — ship/no-ship per variant argued from the tables, placement options (SDD per-task step vs finishing-branch batch), and the ship-arc obligations restated (the ship arc must absorb or delete SDD SKILL.md:86's prose subset rule and the manual-diff advice in files-touched-misses-machinery-coupled-files.md §How-to-apply) — decision explicitly left to the user. Run `python3 loom-code/scripts/check_doc_citations.py` over the audit doc and resolve what it can check.
- **Module**: `docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`
- **Files touched**: `docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/scripts/check_files_touched.py (produced by Tasks 2–4)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md (the corrected declarations, for contrast with the originals)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/BACKLOG.md (§ "`Reuse-adequacy` got the gate it had been missing (SHIPPED)")
- **Acceptance**:
  - **RED**: diagnostic — `grep -c 'RESULTS-PENDING' docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md` returns ≥1 (placeholders still present)
  - **GREEN**: zero `RESULTS-PENDING` markers remain; confusion tables present for all three variants; retro-fit section reports all three instances with the selection-bias label; Limitations and Recommendation sections present; `check_doc_citations.py` reports no broken checkable citations for the audit doc
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Review-weight**: prose
- **Brief item covered**: "A measurement report … per-rule-variant confusion table on the independent cells, the retro-fit on the three known instances reported separately and labeled selection-biased, and a ship/no-ship recommendation"
- **Status**: done(712c9aed)

## Task 6 — Parse continuation-line (wrapped) `Files touched` values

- **Description**: Extend the parser in `scripts/check_files_touched.py` so a `Files touched` value that wraps across continuation lines parses to the FULL declared set. Real shapes to support, both live in this repo: (a) field line ends in a trailing comma, paths continue on indented following lines (`docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md:48-49`); (b) field line carries NO value at all and every path sits on indented continuation lines (`docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md`, Task 10 block). A continuation line is an indented line that is not a new `- ` bullet, not a heading, and not blank; the wrapped value is the concatenation, then comma-split as today. With continuation present, a trailing comma is list syntax, not an empty token — no parse_error; a genuinely empty final token with NO continuation stays a parse_error (current behavior preserved).
- **Module**: `scripts/check_files_touched.py`
- **Files touched**: `scripts/check_files_touched.py`, `scripts/test_check_files_touched.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md (real wrapped shape, lines 48-49)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md (Task 10: no-value + continuation shape)
- **Acceptance**:
  - **RED**: `scripts/test_check_files_touched.py::test_wrapped_files_touched_value_spans_continuation_lines` fails (continuation paths missing from declared set)
  - **GREEN**: both real shapes parse to their full declared sets with zero parse_errors; the no-continuation empty-token parse_error behavior is preserved by an existing-or-new pinning test; whole `scripts/` suite green
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: brief §Addendum — "continuation-line (wrapped) `Files touched` values … whose continuation paths are invisible to the parser and so produce false UNDER verdicts"
- **Status**: done(3b3970ac)

## Task 7 — Trailing parenthetical annotation is not a path token

- **Description**: A trailing parenthetical annotation after the FINAL path token of a `Files touched` value — real shape `docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md:24`, a post-PASS amendment note `(added in the review round … — see §Post-PASS amendment note)` — must not contaminate the token. Rule: after a backtick-closed token, a tail matching a parenthesized group at end of value is an annotation — stripped, no parse_error (legitimate plan practice). A non-parenthetical trailing tail after a backtick-closed token stays a parse_error. Bare (unbackticked) tokens keep current behavior.
- **Module**: `scripts/check_files_touched.py`
- **Files touched**: `scripts/check_files_touched.py`, `scripts/test_check_files_touched.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md (real annotation shape, line 24)
- **Acceptance**:
  - **RED**: `scripts/test_check_files_touched.py::test_trailing_parenthetical_annotation_not_a_token` fails (annotation text contaminates the final token)
  - **GREEN**: the real line-24 shape parses to exactly its four backticked paths, zero parse_errors; a non-parenthetical tail still errors (pinned); whole `scripts/` suite green
- **Dependencies**: Task 6 completes first
- **Independent**: false
- **Brief item covered**: brief §Addendum — "a trailing parenthetical annotation after the final path token … that contaminates the token"
- **Status**: done(dfa1002e)

## Task 8 — Re-sweep the repo and record the dogfood report

- **Description**: With the fixed parser, re-run the comparator over ALL plan documents (`docs/loom/plans/*.md`, `docs/plans/*.md`) and author `docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md`: methodology (command loop, machine-local sha caveat); exit-code distribution pre-fix vs post-fix; per-plan verdict table for the ledgered plans; a TRUE wild under-declaration list where each UNDER is verified against the plan's actual declared text INCLUDING continuation lines (artifact-vs-true separation is the whole point); the two parser gaps as findings (both failing toward false alarms, found only by wild data); the weak-model consumption probe deferred to the ship arc (explicit); selection caveats (sha resolvability is gc-dependent and machine-local; ledgered plans skew recent). Every number from an executed command. Run `python3 loom-code/scripts/check_doc_citations.py` on the new doc and record its output.
- **Module**: `docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md`
- **Files touched**: NEW: `docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md (the frozen-corpus measurement this sweep complements)
  - /Users/kouko/GitHub/monkey-skills/scripts/check_files_touched.py
- **Acceptance**:
  - **RED**: diagnostic — `test -f docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md` exits 1
  - **GREEN**: file exists with the sweep table, the verified true-UNDER list, both parser-gap findings, the deferred-probe statement, and the citation-checker output recorded; zero unverified numbers
- **Dependencies**: Task 7 completes first
- **Independent**: false
- **Review-weight**: prose
- **Brief item covered**: brief §Addendum — "re-run the sweep, and record the results — the true wild under-declaration rate is the load-bearing evidence for the next arc's wire-in decision"
- **Status**: done(0b4bdb31)

## Notes

- **Amendment (2026-08-01, round 2)**: Tasks 6-8 added after the user approved the dogfood extension recorded in brief §Addendum; the five original tasks are done (see their `Status` lines) and are not re-opened. This is a substantive amendment → re-reviewed by plan-document-reviewer (round 2, PASS 15/15).
- Annotation-shape referent corrected `:11` → `:24` in Task 7 and brief §Addendum after the round-2 reviewer's own note flagged the drift and directed the correction ("writing-plans should correct both referents on next touch; the RED test should target the line-24 shape") — reviewer-adjudicated fix, no further round.
- Verdict stamped PASS (2026-08-01, round 1) — stamping the verdict, no re-review (amendment kind 1).
- Kickoff decision: rename accounting in `actual_files()` → use `git show --name-only --no-renames --format= <sha>` so a rename contributes BOTH the old and the new path (probed 2026-08-01 in a sandbox repo: with default rename detection `--name-only` prints only the new path; the old path's deletion still collides with a sibling task touching it, so the disjointness oracle needs both). Cell 8's frozen expectation follows this convention; Task 4's Description's `--format=` invocation gains `--no-renames`.
- Kickoff sweep 2026-08-01: zero one-way-door decisions collected (the genuine one-way door — institutional wiring — is explicitly next-arc per the brief §Decision); no briefing fired per kickoff-briefing.md §c. No PRINCIPLES.md in this repo → default appetite applied.
- **Change-folder binding**: layer (i) no branch-slug match; layer (ii) found 2 non-archived change-folders (`docs/loom/2026-07-12-us-sec-primary-source-layer/`, `docs/loom/2026-07-19-8k-prose-kpi-intake/`). Per the documented decision in `.claude/handoffs/HANDOFF-2026-08-01-013000-reuse-adequacy-shipped-declared-vs-actual-next.md` §Do Not Touch ("The user declined to bind either; do not bind, do not archive without asking"), this plan binds to neither and consumes the brainstorming brief.
- **Placement deviation from the brief's working name**: the brief names `loom-code/scripts/check_files_touched.py` as a *working name*; this plan places the prototype at top-level `scripts/` instead — it is unshipped measurement machinery, and placing it inside the plugin would ship it to marketplace users and force a plugin version bump before the ship decision is even taken. Top-level `scripts/` tests are still CI-collected (.github/workflows/loom-code-ci.yml:98 runs `pytest loom-code/scripts/ scripts/ .claude/hooks/`). The ship arc relocates it if the user decides to wire it in.
- **Freeze discipline**: Task 1 (the answer key) has no code dependencies and MUST be committed before Tasks 3–4 encode any expected verdict; Tasks 3 and 4 declare `Dependencies` on Task 1 to make the ordering mechanical, not conventional.
- **Retro-fit shas are machine-local**: the reuse-adequacy branch was squash-merged (`f22e9aa1`) and its remote branch deleted; `c82c93cd` / `0c03c0e8` resolve only while the local branch `docs-reuse-adequacy-brief-and-backlog` exists. Task 5 records results in the audit doc; no test may pin these shas (CI would fail).
- Tasks 1 and 2 have disjoint files and no dependency edge but are NOT marked `Independent: true` because both create `NEW:` paths, and plan-format.md:79 defaults PROPOSED-new tasks to `Independent: false` (the disjointness oracle cannot be trusted on paths that do not exist yet).
