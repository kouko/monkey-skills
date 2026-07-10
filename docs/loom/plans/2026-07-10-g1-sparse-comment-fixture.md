# Plan: G1 sparse-comment fixture ablation

Source brief: docs/loom/specs/2026-07-10-g1-sparse-comment-fixture.md
Total tasks: 3
Critical-path depth: 3 (≤5)
Execution order: sequential (each task depends on the previous)
Plan-document-reviewer verdict: PASS (2026-07-10, 14/14)

## Task 1 — Literal-aware SQL comment stripper

- **Description**: Implement `strip_sql_comments(sql_text: str) -> str` that removes `--` line comments and `/* */` block comments from a SQL string while leaving string-literal contents (which may themselves contain `--` or `/*`-like substrings) untouched, and without reformatting/re-rendering the surrounding SQL (per the brief's caveat — do NOT use `sqlglot`'s `.sql(comments=False)` render path; implement a small dependency-free state-machine scanner that only recognizes and drops comment tokens, tracking whether the scanner is currently inside a single-quoted string literal).
- **Module**: `dbt-wiki/tests/strip_sql_comments.py`
- **Files touched**: `dbt-wiki/tests/strip_sql_comments.py`, `dbt-wiki/tests/test_strip_sql_comments.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/fixtures/l2-harness/models/marts/fct_avg_ratio_trap.sql` (a real committed model with both a header comment block and inline comments — realistic test input)
- **Acceptance**:
  - **RED**: `dbt-wiki/tests/test_strip_sql_comments.py::test_strips_comments_but_preserves_string_literals` fails (`strip_sql_comments` does not exist)
  - **GREEN**: given a SQL string containing a `--` line comment, a `/* */` block comment, AND a string literal containing a comment-like substring (e.g. `select '-- not a comment' as note`), `strip_sql_comments` removes only the two real comments and leaves the string literal's content and all other tokens/whitespace unchanged (byte-for-byte outside the removed comment spans — no reformatting)
- **External surfaces**: none (dependency-free stdlib string/regex logic, per the brief's rejection of `sqlglot`'s render path)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Decision — Build a comment-stripping step... Prefer a literal-aware comment-only stripper... that changes nothing but the comments."

## Task 2 — Sparse-comment fixture-variant builder

- **Description**: Implement `build_sparse_variant(source_dir: Path, dest_dir: Path) -> None` that materializes a copy of the W1 fixture project at `dest_dir`: every `.sql` file under `models/` has its comments stripped via Task 1's `strip_sql_comments`; every other file (`.yml` schema files, `seeds/*.csv`, `dbt_project.yml`, `profiles.yml`, `.gitignore`) is copied byte-identical (per the brief's Open Question resolution — strip inline SQL comments only, leave `.yml` `description:` fields intact). Verify the resulting variant still builds via `dbt build` against DuckDB.
- **Module**: `dbt-wiki/tests/build_sparse_variant.py`
- **Files touched**: `dbt-wiki/tests/build_sparse_variant.py`, `dbt-wiki/tests/test_build_sparse_variant.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/strip_sql_comments.py` (Task 1's output)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/fixtures/l2-harness/` (the committed source fixture — read-only input, do not modify)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/conftest.py` (reference only — this task's test builds its OWN temp dbt project and runs `dbt build` against it directly; it does NOT use the shared session-scoped `dbt_build` fixture, which points at the original fixture directory, not the sparse copy)
- **Acceptance**:
  - **RED**: `dbt-wiki/tests/test_build_sparse_variant.py::test_sparse_variant_builds_with_zero_sql_comments` fails (`build_sparse_variant` does not exist)
  - **GREEN**: calling `build_sparse_variant` against the committed fixture produces a temp directory where every `.sql` file under `models/` has zero `--`/`/* */` comments (scanned and asserted), every `.yml` / seed CSV / `dbt_project.yml` / `profiles.yml` is byte-identical to the source, and `dbt build` succeeds against the copy with the same model count as the original (10 models) and the same DuckDB queryability
- **External surfaces**: none new — reuses the already-grounded `dbt` CLI surface from Task 1 of the W1 plan (`dbt build`, `--project-dir`, `--profiles-dir`)
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: "Smallest End State — a comment-stripping step that derives a low/zero-comment variant of the SAME fixture project at test time (not a hand-maintained parallel copy)"

## Task 3 — Execute the real e2e validation run against the sparse-comment variant

- **Description**: Using Task 2's `build_sparse_variant` to materialize a sparse-comment copy of the fixture, drive an actual headless `claude -p` instance (real subprocess call, `skip_permissions=True`, same as the W1 plan's Task 11) through `/dbt-wiki:init` → `/dbt-wiki:pack` → answering all 5 gold questions blind against the SPARSE variant. Feed its answers through the UNCHANGED `grader.py` and the UNCHANGED `gold-questions.yml`. Write the result to a gitignored report file, and record the score alongside a note of W1's 5/5 baseline for direct comparison.
- **Module**: `dbt-wiki/tests/test_e2e_sparse_comment_validation.py`
- **Files touched**: `dbt-wiki/tests/test_e2e_sparse_comment_validation.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/build_sparse_variant.py` (Task 2's output)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/runner.py` (committed, unchanged — Task 10 of the W1 plan)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/grader.py` (committed, unchanged — Task 9 of the W1 plan)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/fixtures/l2-harness/gold-questions.yml` (committed, unchanged — Task 8 of the W1 plan)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/test_e2e_validation.py` (Task 11 of the W1 plan — style/containment/governance precedent: temporary git root for the sparse-variant temp dir, teardown, pack-bundle leak check; this task follows the same pattern against the sparse copy instead of the original fixture)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/tests/reports/.gitignore` (already ignores `*.json` — the new report file needs no new gitignore entry)
- **Acceptance**:
  - **RED**: no file exists yet at `dbt-wiki/tests/reports/g1-sparse-comment-run.json`
  - **GREEN**: `dbt-wiki/tests/reports/g1-sparse-comment-run.json` exists, produced by an actual (non-mocked) `claude -p` invocation against the sparse-comment variant, containing per-question grader results + overall accuracy + an explicit `baseline_comparison` field noting W1's 5/5 (100%) result for direct comparison; the captured transcript is confirmed to contain real model output (not canned); no pack bundle or `.dbt-wiki/` artifact from this run lands in version control; the task's DONE report to the orchestrator also states the score in plain text so the orchestrator can write it into `docs/dbt-wiki-quality-campaign.md`'s Journal after this task lands (the journal write itself is an orchestrator close-out step, not part of this task's own file changes — same division as the W1 plan's own campaign-doc close-out, done once after all tasks, not per-task)
- **External surfaces**: none new — reuses the already-grounded `claude -p` / `--output-format json` / `--dangerously-skip-permissions` / `--add-dir` surface from Task 10/11 of the W1 plan
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: "Decision — run a second real e2e validation against it... and record the resulting score in the campaign journal alongside W1's 5/5 baseline — whether it holds, degrades, or fails outright is itself the deliverable finding for this increment."

## Notes

- This is a real-LLM validation activity for Task 3, matching how the W1 plan treated its own Task 11 — RED/GREEN is artifact-existence + content-authenticity, not a pure function test.
- Task 3 spends real Claude subscription quota/time (the W1 precedent, Task 11, took ~7.5 minutes) — the user has already approved executing real e2e runs for this campaign (see the W1 plan's own precedent); no need to re-ask when Task 3 is reached, but confirm timing with the user before dispatch since it's the costly step.
- Dialect (Snowflake/BigQuery) and scale (100+ models) — the other two G1 dimensions — are explicitly out of scope per the brief and are NOT tasks in this plan.
- After Task 3 lands: update `docs/dbt-wiki-quality-campaign.md`'s G1 checklist item (currently unchecked, bundled with G1's other two dimensions — this plan only closes the comment-density slice) and log the score finding in the Journal, mirroring the W1 close-out pattern.
- **Re-review skip note**: plan-document-reviewer PASSed 14/14 (2026-07-10) on this plan before two amendments — (1) Task 3's `Module` field changed from the directory `dbt-wiki/tests/reports/` to the actual file it edits, `dbt-wiki/tests/test_e2e_sparse_comment_validation.py`; (2) Task 3's GREEN criterion gained one clause clarifying the campaign-journal write is an orchestrator close-out step, not part of Task 3's own file changes. Both are additive/schema-safe clarifications reflecting the reviewer's own advisory notes — no field was removed, no dependency/DAG structure changed, no new task added. Re-review skipped per this note.
