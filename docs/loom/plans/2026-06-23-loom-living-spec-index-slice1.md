# Plan: loom living-spec index — slice 1 (A+B+C core mechanism)

Source brief: docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md
Total tasks: 7
Critical-path depth: 4 (≤5)   ← T1 → T4 → T6 → T7 (and T1 → T4 → T5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (14/14, 2026-06-23)

Notes:
- Slice 1 = A (tag parser) + B (index generator) + C (CI gate script), pure `loom-code/scripts/`,
  TDD with **tmp_path hermetic fixtures** (no on-disk fixture dir — mirrors `check-skill-crossrefs.py`,
  avoids the skill-folder nested-subdir rule). All stdlib.
- **No CI-yaml change in slice 1**: the existing `loom-code-ci.yml` step `pytest loom-code/scripts/`
  auto-collects the new `test_*.py`. Wiring the gate against the REAL repo is deferred (no real
  `@req`-tagged tests / namespace exist until later slices) — see brief Out of scope.
- Same-file tasks serialize: T1/T3 share `living_spec_tags.py`; T2/T4/T5 share `living_spec_index.py`;
  T6/T7 share `check-living-spec-index.py`. T1 & T2 are disjoint files + independent → parallel wave 1.
- env: pytest with `PYTHONDONTWRITEBYTECODE=1`.

## Task 1 — A1: extract_tags core (parse @req/@invariant-ref per test-function)
- Description: Create `loom-code/scripts/living_spec_tags.py` with `extract_tags(text: str) -> list[dict]`: scan for tag-comment lines `@req: <id>` and `@invariant-ref: <id>` carried in a line comment (prefixes `#`, `//`, `--`), associate each with the nearest enclosing test-function above it (a line matching `def test_...`/`func Test...`/`test(...` — start with `def test_` for the fixture), and return `[{"test": <name>, "reqs": [...], "invariant_refs": [...]}]`.
- Module: loom-code/scripts/living_spec_tags.py
- Files touched: loom-code/scripts/living_spec_tags.py, loom-code/scripts/test_living_spec_tags.py
- Context paths:
  - loom-code/scripts/check-skill-crossrefs.py
  - docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md
- Acceptance:
  - RED: `PYTHONDONTWRITEBYTECODE=1 python -m pytest loom-code/scripts/test_living_spec_tags.py::test_extract_single_req` fails (module/function undefined)
  - GREEN: a fixture `def test_x():\n    # @req: REQ-1` → `extract_tags` returns `[{"test":"test_x","reqs":["REQ-1"],"invariant_refs":[]}]`
- Dependencies: none
- Independent: true
- Brief item covered: "A tag parser — structured comment tags `@req`/`@invariant-ref`, language-agnostic, stdlib, co-located"

## Task 2 — B1: load_namespace (req → capability from specs/<cap>/spec.md tree)
- Description: Create `loom-code/scripts/living_spec_index.py` with `load_namespace(specs_dir: Path) -> dict[str,str]`: walk `<specs_dir>/<capability>/spec.md`, parse `### Requirement: <id>` headings, return `{req_id: capability}` (capability = the dir name).
- Module: loom-code/scripts/living_spec_index.py
- Files touched: loom-code/scripts/living_spec_index.py, loom-code/scripts/test_living_spec_index.py
- Context paths:
  - loom-code/scripts/verify-drift.py
  - docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md
- Acceptance:
  - RED: `pytest loom-code/scripts/test_living_spec_index.py::test_load_namespace` fails (function undefined)
  - GREEN: a tmp_path `specs/order/spec.md` containing `### Requirement: REQ-1` → `load_namespace` returns `{"REQ-1": "order"}`
- Dependencies: none
- Independent: true
- Brief item covered: "capability is DERIVED via @req → loom-spec namespace lookup (specs/<capability>/)"

## Task 3 — A2: malformed-tag detection
- Description: Extend `living_spec_tags.py` so `extract_tags` also reports malformed tags — a `@req`/`@invariant-ref` marker missing its `: <id>` value (e.g. `@req:` empty, or `@req REQ-1` no colon). Expose them (e.g. a returned `malformed: list[str]` or a companion `find_malformed_tags(text)`).
- Module: loom-code/scripts/living_spec_tags.py
- Files touched: loom-code/scripts/living_spec_tags.py, loom-code/scripts/test_living_spec_tags.py
- Context paths:
  - loom-code/scripts/living_spec_tags.py
- Acceptance:
  - RED: `pytest loom-code/scripts/test_living_spec_tags.py::test_malformed_tag_reported` fails
  - GREEN: a fixture line `# @req:` (no id) and `# @req REQ-2` (no colon) are reported as malformed; well-formed `# @req: REQ-1` is NOT
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "structural = hard FAIL … malformed tag"

## Task 4 — B2: generate_index (capability → req → test markdown tree)
- Description: Add `generate_index(tag_records, namespace) -> str` to `living_spec_index.py`: resolve each test's `@req` → capability via namespace, build a markdown tree `# Living-spec index` → `## <capability>` → `### <req>` → `- <test>`. (Orphans handled in T5.)
- Module: loom-code/scripts/living_spec_index.py
- Files touched: loom-code/scripts/living_spec_index.py, loom-code/scripts/test_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_tags.py
  - loom-code/scripts/living_spec_index.py
- Acceptance:
  - RED: `pytest loom-code/scripts/test_living_spec_index.py::test_generate_index_tree` fails
  - GREEN: tags `[{"test":"test_x","reqs":["REQ-1"]}]` + namespace `{"REQ-1":"order"}` → markdown containing `## order`, `### REQ-1`, `- test_x` in tree order
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "DERIVED index = generated markdown tree: capability → req → test"

## Task 5 — B3: ## Orphans section
- Description: Extend `generate_index` (or a helper it calls) to append a `## Orphans` section listing (a) reqs in the namespace with 0 linked tests, and (b) tests whose `@req` is absent from the namespace (dangling).
- Module: loom-code/scripts/living_spec_index.py
- Files touched: loom-code/scripts/living_spec_index.py, loom-code/scripts/test_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_index.py
- Acceptance:
  - RED: `pytest loom-code/scripts/test_living_spec_index.py::test_orphans_section` fails
  - GREEN: namespace has `REQ-2` with no test, and a test tags `@req: REQ-UNKNOWN` → `## Orphans` lists `REQ-2` (no tests) and `REQ-UNKNOWN` (dangling)
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: "`## Orphans` section (0-test reqs, unknown-@req tests)"

## Task 6 — C1: structural violation check (dangling @req + malformed)
- Description: Create `loom-code/scripts/check-living-spec-index.py` with `find_structural_violations(tag_records, malformed, namespace) -> list[str]`: report dangling `@req` (a test's `@req` not in namespace) and malformed tags as violation strings (empty list = clean). Importable; the `__main__` runs it and `sys.exit(1)` if non-empty.
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_tags.py
  - loom-code/scripts/living_spec_index.py
  - loom-code/scripts/check-skill-crossrefs.py
- Acceptance:
  - RED: `pytest loom-code/scripts/test_check_living_spec_index.py::test_structural_violations` fails
  - GREEN: a dangling `@req: REQ-UNKNOWN` and a malformed `# @req:` each produce a violation entry; a clean fixture returns `[]`
- Dependencies: Tasks 2, 3 complete first
- Independent: false
- Brief item covered: "structural = hard FAIL: dangling @req, malformed tag"

## Task 7 — C2: index identity assertion (committed == fresh-regen)
- Description: Add `index_is_current(committed_md: str, regenerated_md: str) -> bool` to `check-living-spec-index.py` (byte-identity, verify-drift pattern) so CI can assert a committed `INDEX.md` matches a fresh `generate_index(...)`. Importable + exercised by `__main__`.
- Module: loom-code/scripts/check-living-spec-index.py
- Files touched: loom-code/scripts/check-living-spec-index.py, loom-code/scripts/test_check_living_spec_index.py
- Context paths:
  - loom-code/scripts/living_spec_index.py
  - loom-code/scripts/verify-drift.py
- Acceptance:
  - RED: `pytest loom-code/scripts/test_check_living_spec_index.py::test_index_is_current` fails
  - GREEN: `index_is_current(x, x)` is True; `index_is_current(x, x + "\n")` is False (byte-identity)
- Dependencies: Tasks 4, 6 complete first
- Independent: false
- Brief item covered: "the index `committed == fresh-regen` assertion (verify-drift byte-identity pattern)"
