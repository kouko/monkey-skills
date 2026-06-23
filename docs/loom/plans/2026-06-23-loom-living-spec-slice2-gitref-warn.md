# Plan: loom living-spec slice 2 (D) — git-ref drift WARN (thick)

Source brief: docs/loom/specs/2026-06-23-loom-living-spec-slice2-gitref-warn.md
Total tasks: 5
Critical-path depth: 3 (≤5)   ← longest chain: Task 2 → Task 3 → Task 5
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-23; 14/14)

Slice = THICK: ships the git-ref WARN lane end-to-end (pure comparator + locator +
real-git adapter + runner wiring), so it emits WARN over a real tree at merge. The
structural FAIL lane's real-repo walk stays in the capstone slice (unchanged here).

Binding shape (the contract threaded through the tasks):
`{test, req, body_ref, binding_ref, body_ts, binding_ts}` — `*_ref` = commit SHAs
(for the human-readable WARN), `*_ts` = committer epoch ints (the orderable key the
comparator uses). Drift ⟺ `body_ts > binding_ts` (test body moved after its `@req`
binding line was last touched).

## Task 1 — pure drift comparator
- Description: add `find_gitref_drift(bindings) -> list[str]` returning one WARN
  string per binding whose `body_ts > binding_ts`; bindings with `body_ts <=
  binding_ts` produce nothing. WARN string names the test, the `@req`, and both SHAs.
- Module: loom-code/scripts/living_spec_drift.py
- Files touched: loom-code/scripts/living_spec_drift.py, loom-code/scripts/test_living_spec_drift.py
- Context paths:
  - loom-code/scripts/check-living-spec-index.py  (the FAIL-tier style to mirror, kept separate)
- Acceptance:
  - RED: test_living_spec_drift.py::test_flags_body_newer_than_binding fails (find_gitref_drift undefined)
  - GREEN: a binding with body_ts>binding_ts yields exactly one WARN string mentioning its test + req + both refs; a binding with body_ts<=binding_ts yields []; mixed list returns only the drifted ones (order preserved)
- Dependencies: none
- Independent: true
- Brief item covered: "Pure comparator — find_gitref_drift(bindings) -> list[str] … Hermetic unit tests"

## Task 2 — binding locator (line positions), extract_tags untouched
- Description: add `locate_bindings(text) -> list[dict]` to living_spec_tags.py
  returning per `@req` binding `{test, req, body_start, body_end, binding_line}`
  (1-based; body range = the `def test_…` line through the line before the next
  `def`/EOF). Do NOT modify `extract_tags` — add a sibling function only.
- Module: loom-code/scripts/living_spec_tags.py
- Files touched: loom-code/scripts/living_spec_tags.py, loom-code/scripts/test_living_spec_tags.py
- Context paths:
  - loom-code/scripts/living_spec_tags.py  (existing regexes _TEST_DEF_RE / _TAG_RE to reuse)
  - loom-code/scripts/test_living_spec_e2e.py  (the seam-test contract that must stay green)
- Acceptance:
  - RED: test_living_spec_tags.py::test_locate_bindings_returns_line_positions fails (locate_bindings undefined)
  - GREEN: for a 2-test source (one tagged, one with two `@req`), returns correct 1-based body_start/body_end + one entry per `@req` line; AND `extract_tags` output is byte-identical to before (run the existing seam test test_living_spec_e2e.py — stays green)
- Dependencies: none
- Independent: true
- Brief item covered: "Binding locator — a NEW function returning each binding's line positions … Kept separate from extract_tags so its {test,reqs,invariant_refs} output … stays byte-identical"

## Task 3 — git adapter (resolve refs via git log -L)
- Description: add `resolve_binding_refs(binding, repo_root) -> dict` to a new
  living_spec_gitref.py: given a binding's file + line positions, shell out to
  `git log -L` to fill `body_ref`/`body_ts` (last commit touching the body range)
  and `binding_ref`/`binding_ts` (last commit touching the `@req` line). Stdlib
  `subprocess` only.
- Module: loom-code/scripts/living_spec_gitref.py
- Files touched: loom-code/scripts/living_spec_gitref.py, loom-code/scripts/test_living_spec_gitref.py
- Context paths:
  - loom-code/scripts/living_spec_tags.py  (locate_bindings output shape consumed)
- Acceptance:
  - RED: test_living_spec_gitref.py::test_resolve_refs_body_touched_after_binding fails (resolve_binding_refs undefined)
  - GREEN: in a throwaway temp git repo (commit a tagged test, then a later commit touching only the body), resolve returns body_ts > binding_ts and the two distinct SHAs; a repo where only the binding line moved last returns binding_ts >= body_ts
- External surfaces: subprocess invocation of the `git` CLI (`git log -L`) — pin the
  invocation + parse `%H`/`%ct`; run with an explicit `cwd=repo_root`.
- Dependencies: Task 2 completes first (consumes locate_bindings line positions)
- Independent: true
- Brief item covered: "Git adapter — computes body_ref / binding_ref via git log -L over a real tree; tested against a throwaway temp git repo"

## Task 4 — collect bindings across the source tree
- Description: add `collect_bindings(root, patterns=("test_*.py","*_test.py")) ->
  list[dict]` to a new living_spec_collect.py: glob test files under `root`, read
  each, run `locate_bindings`, and tag each result with its file path. No git here
  (pure file I/O + locator).
- Module: loom-code/scripts/living_spec_collect.py
- Files touched: loom-code/scripts/living_spec_collect.py, loom-code/scripts/test_living_spec_collect.py
- Context paths:
  - loom-code/scripts/living_spec_tags.py  (locate_bindings reused)
- Acceptance:
  - RED: test_living_spec_collect.py::test_collect_finds_tagged_tests_across_files fails (collect_bindings undefined)
  - GREEN: given a tmp tree with two test files (each a tagged test) + one non-test file, returns one binding per `@req` across both test files, each carrying its file path; the non-test file is ignored
- Dependencies: Task 2 completes first (consumes locate_bindings)
- Independent: true
- Brief item covered: "Git adapter … __main__ wiring so the gate runs the WARN lane over the source tree" (the source-tree walk feeding the lane)

## Task 5 — wire the WARN lane into the runner (end-to-end)
- Description: extend check-living-spec-index.py with `run_drift_lane(root) ->
  list[str]` = collect_bindings → resolve_binding_refs per binding → find_gitref_drift;
  and have `main()` call it, print each WARN to **stderr**, and **exit 0** (WARN
  never fails the build, never touches the structural FAIL list). The structural
  lane stays as-is (empty inputs).
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_drift.py  (find_gitref_drift)
  - loom-code/scripts/living_spec_gitref.py  (resolve_binding_refs)
  - loom-code/scripts/living_spec_collect.py  (collect_bindings)
  - loom-code/scripts/test_living_spec_e2e.py  (importlib load pattern for the hyphenated file)
- Acceptance:
  - RED: test_check_living_spec_index.py::test_run_drift_lane_emits_warn_and_exits_zero fails (run_drift_lane undefined)
  - GREEN: against a temp git repo with one drifted tagged test, run_drift_lane returns the WARN list; main prints it to stderr and returns 0 even though a WARN exists; with no drift, stderr WARN-free and returns 0; structural FAIL path unchanged (existing tests stay green)
- External surfaces: invokes the `git` adapter (Task 3) over a real tree; no NEW
  command verb — extends the existing `check-living-spec-index.py` runner already
  used in loom-code-ci.yml (no command-surface accretion).
- Dependencies: Tasks 1, 3, 4 complete first (Task 3 transitively requires Task 2)
- Independent: false
- Brief item covered: "__main__ wiring so the gate runs the WARN lane over the source tree, prints WARN to stderr, exits 0 (never flips FAIL)"

## Notes
- Post-PASS amendment (2026-06-23, additive/schema-safe — re-review skipped): flipped
  Task 3 `Independent: false` → `true` per the reviewer's Check-15 advisory (T3 and T4
  are same-level, disjoint files, no mutual dep). All four `Independent: true` tasks
  (T1/T2/T3/T4) remain pairwise file-disjoint, so Check 14 still holds.
- Dependency levels: L0 = {Task 1, Task 2} (both Independent); L1 = {Task 3, Task 4}
  (both depend on Task 2, disjoint files + no mutual semantic dep → Independent pair);
  L2 = {Task 5}. Critical-path depth = 3.
- Seam-test guard: Task 2 is the only task near `extract_tags`; its GREEN explicitly
  requires the existing seam test (test_living_spec_e2e.py) to stay green.
- Out of scope (from brief): M2 intent-doc compare, M3 stored baseline/bless, the
  intent layer (E), index git-ref columns, and the capstone's other CI checks
  (index regen at finishing, required PR checks, active-coverage).
