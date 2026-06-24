# Plan: loom living-spec capstone G — PR-1 (make the index real)

Source brief: docs/loom/specs/2026-06-24-loom-living-spec-capstone-g.md (PR-1 section)
Design brief: docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md
Total tasks: 10   (width uncapped; many leaves)
Critical-path depth: 5 (≤5)   — longest chain: T1 → T4 → T5 → T6a → T6b (T9 is parallel to the T4→T5 branch, both feed T6a; T1→T2→T9→T6a→T6b = depth 5 too)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-24, round 2 — Check-4 split applied; 14/14)

## Amendment (2026-06-24, post-T5, mid-execution) — re-review skipped (additive + depth-invariant)

**Task 9 added** after a live-verify discovery: running the now-wired structural lane (Task 3) over loom's OWN repo exits 1 with 6 FALSE violations — `# @req:` markers that live INSIDE multi-line string-literal test fixtures (in test_living_spec_collect.py / test_living_spec_tags.py, which test the @req parser itself). The anchored line-regex cannot tell a fixture's string-literal `# @req:` from a real comment. Without a fix, T6b's every-push structural gate would red-CI loom itself and T6a's committed index would carry 6 fake orphans. User chose the root-cause fix (tokenize, only real comments). **Depth re-verified: Task 9 depends on T1+T2 only and is parallel to the T4→T5 branch — both feed T6a — so the longest chain stays T1→T4→T5→T6a→T6b = 5 (T1→T2→T9→T6a→T6b is also 5). No breach.** T6a's `Dependencies` updated to include Task 9. Amendment is additive (new task + one new dependency edge) and depth-invariant, so plan-document-reviewer re-review is skipped per writing-plans §Amending a PASS plan.

## Notes

- **Fixture-safety is load-bearing, not optional.** The repo's own living-spec test files
  carry `# @req:` markers *inside string literals* (test fixtures). The drift lane already
  solved this with the anchored `_REQ_TAG_RE` via `locate_bindings` (slice-2 hard-won fix:
  "6 fixture-string false WARNs → anchored regex"). The structural lane MUST collect through
  the SAME anchored path — naive `extract_tags`/`find_malformed_tags` (non-anchored `.search`)
  would flood the index with fixture false-positives and false-FAIL the gate. This is why
  Tasks 1–2 build new anchored collectors instead of calling `extract_tags` over the tree.
- **Namespace location on the real repo:** `load_namespace(root / "docs/loom/spec")`. That
  dir does not exist yet (the slice-3 intent layer ships authoring docs + a validator, not a
  populated tree here), so `glob("*/spec.md")` → `{}`. With no real `@req` bindings the index
  is legitimately near-empty (design B1 empty base case). This is correct, not a bug.
- **check-living-spec-index.py is NOT in CI today** (CI has 4 gates: pytest / verify-drift /
  codex-manifest / crossrefs; no living-spec gate). PR-1 adds both the structural-lane step
  (every push) and the verify-index step (Task 6).
- Prose-only tasks (T7 finishing SKILL.md, T8 implementer.md): a behavioral pytest is
  infeasible for Claude-prose policy text (known loom limit). Their RED/GREEN is a mechanical
  presence assertion (grep / a presence test), which is the honest acceptance for doc edits.
- All RED tests for the code tasks use `tmp_path` git/dir fixtures, mirroring the existing
  `test_check_living_spec_index.py` helpers (`_init_repo` / `_commit`).

## Task 1 — collect_structural_records(root)
- Description: Add a fixture-safe collector that walks test files under `root` and returns
  one `{"test", "reqs", "invariant_refs"}` record per tagged test (the `extract_tags` shape
  `find_structural_violations` / `generate_index` consume), built by regrouping the ANCHORED
  `collect_bindings` output by (file, test). Reusing the anchored `locate_bindings` path is
  what makes it skip `@req` markers inside fixture string literals.
- Module: loom-code/scripts/living_spec_collect.py
- Files touched: loom-code/scripts/living_spec_collect.py, loom-code/scripts/test_living_spec_collect.py
- Context paths:
  - loom-code/scripts/living_spec_collect.py (collect_bindings — anchored walk to reuse)
  - loom-code/scripts/living_spec_tags.py (locate_bindings record shape; _REQ_TAG_RE anchoring)
  - loom-code/scripts/test_check_living_spec_index.py (extract_tags record shape consumers expect)
- Acceptance:
  - RED: tests/test_living_spec_collect.py::test_collect_structural_records_is_fixture_safe fails
    (collect_structural_records undefined) — tmp tree with one real `def test_x` + `# @req: REQ-1`
    AND a second file whose only `@req` is inside a string literal (`x = "# @req: REQ-FIXTURE"`).
  - GREEN: result == `[{"test": "test_x", "reqs": ["REQ-1"], "invariant_refs": []}]` — the
    fixture-string `REQ-FIXTURE` is absent.
- Dependencies: none
- Independent: true
- Brief item covered: PR-1 item 1 — "structural FAIL lane reads the real repo" (collection half)

## Task 2 — collect_malformed(root)
- Description: Add a fixture-safe malformed-tag collector: walk test files under `root` and
  return raw malformed `@req`/`@invariant-ref` comment lines (marker present, no usable `: <id>`),
  detected ANCHORED (comment marker starts the line after optional indent) so a malformed marker
  inside a string literal is not reported. The structural lane feeds this to
  `find_structural_violations` as its `malformed` argument.
- Module: loom-code/scripts/living_spec_collect.py
- Files touched: loom-code/scripts/living_spec_collect.py, loom-code/scripts/test_living_spec_collect.py
- Context paths:
  - loom-code/scripts/living_spec_tags.py (find_malformed_tags + the _TAG_MARKER_RE / _TAG_RE pair; anchor it)
- Acceptance:
  - RED: tests/test_living_spec_collect.py::test_collect_malformed_is_fixture_safe fails
    (collect_malformed undefined) — tmp tree with a real column-0 `    # @req` (no colon/id) inside
    a test AND a fixture string `y = "# @req"`.
  - GREEN: result reports the real malformed line, NOT the fixture-string one.
- Dependencies: Task 1 completes first   # same file, sequential edit
- Independent: false
- Brief item covered: PR-1 item 1 — "structural FAIL lane reads the real repo" (malformed half; design #1 "malformed tag = structural FAIL")

## Task 3 — wire main() structural lane to the real repo
- Description: Replace the empty-inputs stub at `check-living-spec-index.py:128`
  (`find_structural_violations([], [], {})` + its slice-boundary comment) with real collection:
  `collect_structural_records(root)`, `collect_malformed(root)`, and
  `load_namespace(root / "docs/loom/spec")`, fed to `find_structural_violations`. Keep the WARN
  lane untouched and the exit-code contract (violations → print to stderr + return 1; clean → 0).
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/check-living-spec-index.py (main, find_structural_violations, run_drift_lane pattern)
  - loom-code/scripts/living_spec_index.py (load_namespace signature)
- Acceptance:
  - RED: test_check_living_spec_index.py::test_main_structural_lane_fails_on_real_dangling_req fails —
    tmp repo with a committed `def test_x` / `# @req: REQ-NOPE` test and a `docs/loom/spec/order/spec.md`
    declaring only `### Requirement: REQ-1`; `main([str(repo)])` currently returns 0 (stub).
  - GREEN: `main([str(repo)])` returns 1 and stderr names `REQ-NOPE`; a clean tmp repo (no `@req`,
    or every `@req` in namespace) returns 0; the existing WARN-lane tests stay green.
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: PR-1 item 1 — "structural FAIL lane reads the real repo"; design #3 "structural = hard FAIL on every push"

## Task 4 — build_index(root) composition function
- Description: Add `build_index(root) -> str` to check-living-spec-index.py composing
  `collect_structural_records(root)` + `load_namespace(root / "docs/loom/spec")` →
  `generate_index(records, namespace)`. This is the single regeneration entry point the CLI,
  finishing, and the CI verify step all call.
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_index.py (generate_index signature + output format)
- Acceptance:
  - RED: test_check_living_spec_index.py::test_build_index_renders_tree fails (build_index undefined) —
    tmp repo with a committed tagged test + matching `docs/loom/spec/<cap>/spec.md`.
  - GREEN: `build_index(repo)` returns the markdown tree containing `## <capability>`, `### <req>`,
    `- <test>` (byte-equal to `generate_index` over the same collected records).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: PR-1 item 2 — "docs/loom/INDEX.md is committed + regenerated"

## Task 5 — --write-index / --verify-index CLI modes
- Description: Add two CLI modes to check-living-spec-index.py `main()`:
  `--write-index <path>` regenerates via `build_index(root)` and writes `<path>`;
  `--verify-index <path>` regenerates and asserts byte-identity vs the committed `<path>`
  (reuse `index_is_current`), returning 1 on mismatch (the merge-boundary stale-index gate).
  Both default `<path>` to `docs/loom/INDEX.md`. Declare the new verbs in the command surface
  (loom-code AGENTS.md commands section / CI invocation) and verify they run.
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/check-living-spec-index.py (main argv handling, index_is_current)
- Acceptance:
  - RED: test_check_living_spec_index.py::test_verify_index_mode_fails_on_stale fails — tmp repo with
    a committed INDEX.md whose bytes differ from a fresh `build_index`; `main(["--verify-index", path, str(repo)])`
    currently doesn't recognize the flag.
  - GREEN: `--verify-index` returns 1 on a stale file, 0 on a current one; `--write-index` writes a
    file that `--verify-index` then passes. Command surface: the new `--write-index`/`--verify-index`
    verbs are declared in loom-code's command surface and verified to run.
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: PR-1 item 4 — "byte-identity CI gate reusing index_is_current"

## Task 6a — commit the docs/loom/INDEX.md artifact
- Description: Generate the repo's own `docs/loom/INDEX.md` via `--write-index` and commit it
  (near-empty: no real `@req` bindings yet — the valid B1 base case), then guard it with a currency
  test. This is the committed AUTHORED-vs-DERIVED anchor the CI verify step (Task 6b) checks against.
- Module: docs/loom/INDEX.md
- Files touched: docs/loom/INDEX.md, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/test_living_spec_e2e.py (committed-index currency assertion pattern)
  - loom-code/scripts/check-living-spec-index.py (build_index, index_is_current)
- Acceptance:
  - RED: test_check_living_spec_index.py::test_committed_index_is_current fails — `docs/loom/INDEX.md`
    absent (or not byte-equal to `build_index(repo_root)`).
  - GREEN: `docs/loom/INDEX.md` is committed and `index_is_current(committed, build_index(root))` is True.
- Dependencies: Tasks 3, 5, 9 complete first
- Independent: false
- Brief item covered: PR-1 item 2 — "docs/loom/INDEX.md is committed + regenerated"

## Task 6b — wire the structural-lane + verify-index CI steps
- Description: Add two steps to loom-code-ci.yml mirroring the existing gate structure: the
  structural-lane gate (`check-living-spec-index.py` over the repo root, runs every push — design #3
  RED-safe) and the byte-identity verify-index gate (`--verify-index docs/loom/INDEX.md`). Depends on
  6a so the committed artifact exists before the gate that verifies it is wired (a verify step with no
  committed file is instant-red).
- Module: .github/workflows/loom-code-ci.yml
- Files touched: .github/workflows/loom-code-ci.yml
- Context paths:
  - .github/workflows/loom-code-ci.yml (existing 4-gate job structure to mirror)
- Acceptance:
  - RED (presence): grep of loom-code-ci.yml finds neither the structural-lane step nor the
    `--verify-index` step.
  - GREEN: loom-code-ci.yml contains both steps; locally, running `check-living-spec-index.py` over the
    repo root exits 0 and `--verify-index docs/loom/INDEX.md` exits 0 against the Task-6a artifact.
- Dependencies: Task 6a completes first
- Independent: false
- Brief item covered: PR-1 item 4 — "byte-identity CI gate reusing index_is_current"; design #3 structural-every-push

## Task 7 — finishing-a-development-branch regen step
- Description: Add an orchestrator step to finishing-a-development-branch/SKILL.md: regenerate the
  living-spec index ONCE per branch (`--write-index docs/loom/INDEX.md`) and stage+commit it as part
  of the close-out commit — explicitly orchestrator-only, NOT per-implementer (design #5: a per-wave
  regen merge-conflicts the repo-wide generated file). Slot it into the close-out commit phase.
- Module: loom-code/skills/finishing-a-development-branch/SKILL.md
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md (the close-out commit phase)
- Acceptance:
  - RED (presence): grep for the index-regen instruction in finishing SKILL.md returns nothing.
  - GREEN: SKILL.md instructs the orchestrator to run `--write-index` once/branch in the close-out
    commit, with the explicit "NOT per-implementer" rationale.
- Dependencies: Task 5 completes first   # doc-mirrors-code: the --write-index verb must exist
- Independent: true   # disjoint file from T6/T8, no shared symbol
- Brief item covered: PR-1 item 3 — "finishing-a-development-branch orchestrator regen step (once/branch)"

## Task 8 — implementer @req DoD rule
- Description: Add a Definition-of-Done rule to loom-code/agents/implementer.md: every test written
  under the TDD iron law MUST carry a `# @req: <REQ-id>` tag binding it to its capability's
  requirement (the linkage the structural lane + index read). A test with no `@req` is incomplete.
  Place it alongside the existing test-discipline rules.
- Module: loom-code/agents/implementer.md
- Files touched: loom-code/agents/implementer.md
- Context paths:
  - loom-code/agents/implementer.md (Output contract / test-discipline rules)
- Acceptance:
  - RED (presence): grep for an `@req` tagging DoD in implementer.md returns nothing.
  - GREEN: implementer.md mandates a `# @req:` tag on every TDD test, framed as a DoD/incomplete-without rule.
- Dependencies: none
- Independent: true   # disjoint file, no shared symbol; parallel with T1
- Brief item covered: PR-1 item 5 — "implementer @req DoD rule"; design #6 "implementer DoD gains tag-the-test-with-its-@req"

## Task 9 — string-literal-aware structural collection (tokenize)
- Description: Make the structural collectors ignore `# @req:` / `# @invariant-ref` markers that live INSIDE Python string literals (multi-line test fixtures), so the structural lane over loom's own repo is clean (no false dangling/malformed from the parser's self-test fixtures). Add a stdlib `tokenize`-based helper that, for a `.py` file, returns the set of line numbers carrying a REAL `COMMENT` token, then filter `collect_structural_records` (drop bindings whose `binding_line` is not a real comment) and `collect_malformed` (only report real-comment lines). Apply ONLY to `.py` files; non-`.py` (e.g. `// @req`, `-- @req`) pass through the existing regex unchanged (their string-literal case stays the deferred 🟢). Do NOT touch `collect_bindings` / `locate_bindings` themselves — the drift WARN lane is advisory and out of scope here; layer the filter inside the structural collectors only.
- Module: loom-code/scripts/living_spec_collect.py
- Files touched: loom-code/scripts/living_spec_collect.py, loom-code/scripts/test_living_spec_collect.py
- Context paths:
  - loom-code/scripts/living_spec_collect.py (collect_structural_records + collect_malformed added in T1/T2)
  - loom-code/scripts/living_spec_tags.py (locate_bindings emits binding_line; the anchored regexes that currently over-match string-literal lines)
- Acceptance:
  - RED: test_living_spec_collect.py::test_structural_collectors_ignore_string_literal_reqs fails — tmp tree with a `.py` file whose ONLY `@req`/malformed markers are inside a triple-quoted string literal (a realistic parser-fixture, e.g. `_SRC = """\ndef test_x():\n    # @req: REQ-FAKE\n"""`), asserting `collect_structural_records` and `collect_malformed` both return empty (currently they pick REQ-FAKE up).
  - GREEN: both collectors return empty for the string-literal-only file; a sibling assertion confirms a REAL `# @req:` comment in actual code is STILL collected (no over-filtering); after this, `check-living-spec-index.py <repo-root>` exits 0 over loom itself (the 6 false violations are gone).
- Dependencies: Tasks 1, 2 complete first
- Independent: false   # same file as T1/T2 (both committed); parallel to the T4→T5 branch
- Brief item covered: PR-1 item 1 — "structural FAIL lane reads the real repo" (fixture-safety completion; design brief §Residual rot surface "AST string-literal awareness" pulled in for the structural lane so the gate is clean over the self-hosting repo)
