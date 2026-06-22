"""Tests for the living-spec structural-violation gate.

`find_structural_violations(tag_records, malformed, namespace)` takes
the already-computed outputs of the slice-1 parser
(`extract_tags` -> `tag_records`, `find_malformed_tags` -> `malformed`)
plus the req-to-capability `namespace` (`load_namespace` output), and
returns one violation string per problem found:

- a DANGLING `@req` — a test's `@req` id absent from `namespace`;
- each MALFORMED tag line (passed through verbatim).

Clean input (every `@req` resolves, no malformed lines) returns `[]`.

The module is loaded by file path because its filename uses a hyphen
(not importable by name) — mirrors `test_check_skill_crossrefs.py`.
Stdlib only.
"""

import importlib.util
from pathlib import Path

_MODULE_PATH = Path(__file__).parent / "check-living-spec-index.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_living_spec_index", _MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_structural_violations():
    # WHY: the gate must FAIL LOUD on two distinct structural defects so
    # a mistagged or half-written tag cannot slip into the living-spec
    # index silently. (a) A test whose @req is not in the namespace is a
    # dangling tag (typo / deleted req); (b) a malformed `# @req:` line
    # never even produced a usable id. Both must surface as violations,
    # and each violation string must name the offending id / line so the
    # author can locate it.
    checker = _load_checker()

    tag_records = [
        {"test": "test_known", "reqs": ["REQ-1"], "invariant_refs": []},
        {"test": "test_dangle", "reqs": ["REQ-UNKNOWN"], "invariant_refs": []},
    ]
    malformed = ["# @req:"]
    namespace = {"REQ-1": "order"}

    violations = checker.find_structural_violations(
        tag_records, malformed, namespace
    )

    # (a) the dangling @req is reported, naming the offending id.
    assert any("REQ-UNKNOWN" in v for v in violations), (
        f"dangling @req must be reported, got: {violations!r}"
    )
    # (b) the malformed line is reported, carrying the raw line.
    assert any("# @req:" in v for v in violations), (
        f"malformed tag must be reported, got: {violations!r}"
    )
    # the resolvable @req (REQ-1) is NOT a violation.
    assert not any("REQ-1" in v for v in violations), (
        f"a resolvable @req must not be flagged, got: {violations!r}"
    )


def test_clean_input_returns_empty():
    # WHY: a clean run (every @req resolves, no malformed lines) must
    # return [] so the gate's __main__ exits 0 — no false positives.
    checker = _load_checker()

    tag_records = [
        {"test": "test_ok", "reqs": ["REQ-1", "REQ-2"], "invariant_refs": []},
    ]
    malformed: list[str] = []
    namespace = {"REQ-1": "order", "REQ-2": "billing"}

    violations = checker.find_structural_violations(
        tag_records, malformed, namespace
    )

    assert violations == [], f"clean input must yield no violations, got: {violations!r}"


def test_index_is_current():
    # WHY: the CI gate must be able to assert that a committed INDEX.md is
    # byte-identical to a fresh `generate_index(...)` (the verify-drift
    # pattern). Anything less than byte-identity — even a stray trailing
    # newline — means the committed file is stale and must fail loud, so
    # the index can never silently drift from its source of truth.
    checker = _load_checker()

    x = "# Living Spec Index\n\n- REQ-1: order\n"

    # identical strings are current.
    assert checker.index_is_current(x, x) is True, (
        "byte-identical strings must be current"
    )
    # a trailing-newline difference is NOT current (byte-identity).
    assert checker.index_is_current(x, x + "\n") is False, (
        "a trailing-newline difference must fail byte-identity"
    )
