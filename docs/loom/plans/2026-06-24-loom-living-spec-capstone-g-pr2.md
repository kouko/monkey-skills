# Plan: loom living-spec capstone G — PR-2 (enforce intent)

Source brief: docs/loom/specs/2026-06-24-loom-living-spec-capstone-g-pr2.md (4 pieces, post-RESHAPE)
Design brief: docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md
Total tasks: 7
Critical-path depth: 4 (≤5)   — longest chain: T1 → T4 → T5 → T6
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-24, 14/14) — post-PASS amendment: T2 flipped Independent:false→true to form the T2‖T4 parallel pair the reviewer verified disjoint (living_spec_index.py vs check-living-spec-index.py, both dep T1 only, no shared symbol — T4 reads load_req_status, not find_malformed_status). Additive + schema-safe (enables a parallel dispatch already validated as disjoint); re-review skipped per writing-plans §Amending a PASS plan.

## Notes

- **"0 passing tests" = "0 linked tests" by CI ordering.** The active-coverage gate (T5/T6) runs in the
  post-pytest band; a green suite means every linked test passed, so the gate needs only the req→test
  linkage from `collect_structural_records` (PR-1) — NO junit/per-test-result parsing.
- **Status syntax lives on the requirement heading** (`### Requirement: REQ-X [deferred]`, active = default).
  The parser must keep `load_namespace`'s `{req_id: capability}` `req_id` capture UNCHANGED (the index
  depends on it) — the `[status]` is a separate optional capture, and an id must NOT swallow the bracket.
- **Malformed-status is RED-safe (every-push), coverage is RED-unsafe (merge-boundary).** A bad status
  token (`[activ]`) is a syntax error surfaced by the every-push structural lane (T2/T3); the active-0-test
  coverage check is merge-boundary only (T5/T6). Two lanes, matching the design's separation.
- The intent layer `docs/loom/spec/` (singular) does not exist on this repo yet → both new checks are
  correct-but-near-noop until a real requirement is declared; RED tests use `tmp_path` trees with a seeded
  `### Requirement:` + spec.md, mirroring PR-1's test style (`test_living_spec_e2e.py`, `_load_checker`).
- All tasks are stdlib-only (re, pathlib); no external surfaces.

## Task 1 — load_req_status() parses the [active|deferred] suffix
- Description: Add `load_req_status(specs_dir) -> dict[str, str]` to living_spec_index.py: walk the same
  `<specs_dir>/<capability>/spec.md` files as `load_namespace`, parse each `### Requirement: <id>` heading,
  and map `req_id -> "active"|"deferred"` (default `"active"` when no `[...]` suffix). Extend `_REQUIREMENT_RE`
  (or add a sibling regex) to optionally capture `[active|deferred]` WITHOUT changing what `load_namespace`'s
  `req_id` captures — verify `load_namespace` still returns clean ids for a heading carrying a status suffix.
- Module: loom-code/scripts/living_spec_index.py
- Files touched: loom-code/scripts/living_spec_index.py, loom-code/scripts/test_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_index.py (_REQUIREMENT_RE line 15, load_namespace 18-31)
- Acceptance:
  - RED: test_living_spec_index.py::test_load_req_status_parses_suffix_default_active fails
    (load_req_status undefined) — tmp specs/orders/spec.md with `### Requirement: REQ-1 [deferred]` and
    `### Requirement: REQ-2` (no suffix).
  - GREEN: `load_req_status(tmp)` == `{"REQ-1": "deferred", "REQ-2": "active"}` AND
    `load_namespace(tmp)` == `{"REQ-1": "orders", "REQ-2": "orders"}` (req_id capture unchanged — REQ-1 is
    NOT "REQ-1 [deferred]").
- Dependencies: none
- Independent: false
- Brief item covered: Decision piece 1 — "extend _REQUIREMENT_RE to optionally capture [active|deferred] (default active) WITHOUT changing load_namespace's {req_id:capability} contract; add load_req_status loader"

## Task 2 — find_malformed_status() flags a bad status token
- Description: Add `find_malformed_status(specs_dir) -> list[str]` to living_spec_index.py: a
  `### Requirement: <id>` heading whose trailing `[...]` bracket content is neither `active` nor `deferred`
  (e.g. `[activ]`, `[todo]`) is a malformed declaration → return one descriptive string per offender
  (e.g. `"MALFORMED status '[activ]' on requirement REQ-1"`). A heading with no bracket, or a valid
  `[active]`/`[deferred]`, yields nothing.
- Module: loom-code/scripts/living_spec_index.py
- Files touched: loom-code/scripts/living_spec_index.py, loom-code/scripts/test_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_index.py (the requirement-heading parse + load_req_status from Task 1)
- Acceptance:
  - RED: test_living_spec_index.py::test_find_malformed_status fails (find_malformed_status undefined) —
    tmp spec.md with `### Requirement: REQ-1 [activ]` + `### Requirement: REQ-2 [deferred]`.
  - GREEN: result names `REQ-1`/`activ` and does NOT name `REQ-2` (a valid `[deferred]` is clean).
- Dependencies: Task 1 completes first   # same file as T1, sequential after it
- Independent: true   # disjoint file from T4 (living_spec_index.py vs check-living-spec-index.py); both dep T1 only, no shared symbol
- Brief item covered: Decision piece 1 — "A status token that is neither active nor deferred ... is rejected fail-loud as a malformed declaration"

## Task 3 — wire malformed-status into the every-push structural lane
- Description: In check-living-spec-index.py `main()`, fold `find_malformed_status(root/"docs/loom/spec")`
  into the structural FAIL lane's violation list (alongside the existing `find_structural_violations`
  output) so a bad status token fails the build (rc=1) on every push — RED-safe (it's a syntax error, not
  a coverage check). Keep the WARN lane + the CLI modes untouched.
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/check-living-spec-index.py (main structural lane, lines 219-236)
  - loom-code/scripts/living_spec_index.py (find_malformed_status from Task 2)
- Acceptance:
  - RED: test_check_living_spec_index.py::test_main_fails_on_malformed_status fails — tmp repo with a
    `docs/loom/spec/orders/spec.md` carrying `### Requirement: REQ-1 [activ]`; `main([str(repo)])` currently
    returns 0 (status not checked).
  - GREEN: `main([str(repo)])` returns 1 and stderr names the malformed status; a clean tree returns 0;
    existing structural/WARN-lane tests stay green.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: Decision piece 1 — "surfaced by the EXISTING every-push structural lane (find_structural_violations malformed path), RED-safe"

## Task 4 — active_coverage() hermetic check
- Description: Add `active_coverage(tag_records, namespace, statuses) -> tuple[list[str], list[str]]` to
  check-living-spec-index.py (hermetic, in-memory inputs like `find_structural_violations`): invert
  `tag_records` (test→reqs) to req→tests; for each req in `namespace`: status = `statuses.get(req, "active")`;
  `active` + 0 linked tests → append to violations (e.g. `"UNCOVERED active req 'REQ-1' (0 passing tests)"`);
  `deferred` + 0 linked → append to a separate `surfaced` list (`"deferred req 'REQ-2' (inspirational, 0 tests)"`);
  a req WITH ≥1 linked test → neither list. Returns `(violations, surfaced)`.
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/check-living-spec-index.py (find_structural_violations as the hermetic-shape model)
  - loom-code/scripts/living_spec_collect.py (collect_structural_records record shape {test, reqs})
- Acceptance:
  - RED: test_check_living_spec_index.py::test_active_coverage fails (active_coverage undefined) — inputs:
    tag_records linking REQ-1 to a test, REQ-2 unlinked; namespace {REQ-1, REQ-2, REQ-3}; statuses
    {REQ-2: "deferred", REQ-3: "active"} (REQ-1 defaults active).
  - GREEN: violations name REQ-3 (active, 0 tests) and NOT REQ-1 (active, linked); surfaced names REQ-2
    (deferred, 0 tests). Exact strings asserted.
- Dependencies: Task 1 completes first   # needs the status concept; uses load_req_status output shape
- Independent: true   # disjoint file from Task 2 (living_spec_index.py); both feed later tasks
- Brief item covered: Decision piece 2 — "active+0 linked tests → violation; deferred+0 linked → surfaced never fails"

## Task 5 — --check-coverage CLI mode (merge-boundary gate)
- Description: Add a `--check-coverage [root]` mode to check-living-spec-index.py `main()` (mirroring the
  `--write-index`/`--verify-index` argv handling at lines 187-212): compose `collect_structural_records(root)`
  + `load_namespace(root/"docs/loom/spec")` + `load_req_status(root/"docs/loom/spec")` → `active_coverage(...)`;
  print each surfaced (deferred) line to stdout, print each violation to stderr; return 1 if any active
  violation, else 0. Declare the new `--check-coverage` verb in the command surface (AGENTS.md managed block,
  next to --write-index/--verify-index) and verify it runs.
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py, AGENTS.md
- Context paths:
  - loom-code/scripts/check-living-spec-index.py (main argv modes 187-212; active_coverage from Task 4)
  - AGENTS.md (the command-surface managed block from PR-1)
- Acceptance:
  - RED: test_check_living_spec_index.py::test_check_coverage_mode_fails_on_uncovered_active fails — tmp repo
    with `docs/loom/spec/orders/spec.md` declaring `### Requirement: REQ-1` (active default) and NO test
    carrying `# @req: REQ-1`; `main(["--check-coverage", str(repo)])` is unrecognized pre-impl.
  - GREEN: `--check-coverage` returns 1 on the uncovered active req (stderr names REQ-1); returns 0 when a
    test carries `# @req: REQ-1`; a `[deferred]` req with 0 tests prints to stdout and returns 0. Command
    surface: `--check-coverage` declared in AGENTS.md and verified to run.
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: Decision piece 2 — "a --check-coverage CLI mode ... Runs at merge-boundary (post-green-suite)"

## Task 6 — CI active-coverage gate step
- Description: Add a step to loom-code-ci.yml in the post-pytest band (after the structural + verify-index
  gates), mirroring their shape: `python3 loom-code/scripts/check-living-spec-index.py --check-coverage .`
  with `PYTHONDONTWRITEBYTECODE: "1"`. This is the merge-boundary gate that blocks an active req with no
  passing test (sound because it runs after the green pytest gate).
- Module: .github/workflows/loom-code-ci.yml
- Files touched: .github/workflows/loom-code-ci.yml
- Context paths:
  - .github/workflows/loom-code-ci.yml (the structural + verify-index gate steps from PR-1)
- Acceptance:
  - RED (presence): grep of loom-code-ci.yml finds no `--check-coverage` step.
  - GREEN: loom-code-ci.yml contains the `--check-coverage .` step in the post-pytest band; locally
    `check-living-spec-index.py --check-coverage .` exits 0 over the (empty-layer) repo.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: Decision piece 3 — "add the active-coverage step in the post-pytest band, after the existing living-spec gates"

## Task 7 — spec-expansion authoring docs for status
- Description: Add to loom-spec/skills/spec-expansion/SKILL.md (after the "Authoring the persistent intent
  layer" section, ~line 417): document the `### Requirement: REQ-X [deferred]` status syntax (active =
  default, may be omitted), the canonical-vs-inspirational mapping (verified active = canonical; deferred /
  unverified = inspirational), and the merge-boundary gate behavior (active + 0 passing tests = FAIL;
  deferred + 0 = surfaced, not failed). Update any slice-3 text that flagged status as "deferred to capstone G".
- Module: loom-spec/skills/spec-expansion/SKILL.md
- Files touched: loom-spec/skills/spec-expansion/SKILL.md
- Context paths:
  - loom-spec/skills/spec-expansion/SKILL.md (Authoring section ~388-417)
- Acceptance:
  - RED (presence): grep of spec-expansion SKILL.md finds no `[deferred]` status-syntax / active-coverage
    documentation.
  - GREEN: SKILL.md documents the `[active|deferred]` suffix, the canonical/inspirational mapping, and the
    gate behavior; the stale "status deferred to capstone G" note is updated.
- Dependencies: Task 1 completes first   # doc-mirrors-code: the syntax the parser implements
- Independent: false
- Brief item covered: Decision piece 4 — "document the [deferred] suffix (active = default), the canonical-vs-inspirational mapping, and the gate behavior"
