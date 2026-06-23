"""End-to-end seam test for the living-spec index (slice 1).

The three slice-1 modules are unit-tested in isolation against
hand-authored fixtures, but the **contract between them** — the
``{"test", "reqs", "invariant_refs"}`` record shape and the
``{req_id: capability}`` namespace — lives only in those fixtures. This
test composes the REAL functions across all three modules so a future
change to one module's output shape that keeps the per-module tests
green still trips here. It is the committed regression guard for the
extract -> namespace -> generate -> check seam.

WHY a dedicated seam test: per-module TDD leaves the integration
contract unguarded; this is the one test that fails loud if the seam
drifts.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import living_spec_index as I
import living_spec_tags as T

# check-living-spec-index.py is hyphenated -> not importable by name;
# load it by file path (the house pattern from test_check_skill_crossrefs.py).
_CHECK_PATH = Path(__file__).parent / "check-living-spec-index.py"
_spec = importlib.util.spec_from_file_location("check_living_spec_index", _CHECK_PATH)
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def test_seam_extract_to_namespace_to_generate_to_check(tmp_path):
    # Namespace: one capability declaring two requirements; REQ-2 has no test.
    specs = tmp_path / "specs" / "order"
    specs.mkdir(parents=True)
    (specs / "spec.md").write_text(
        "### Requirement: REQ-1\n### Requirement: REQ-2\n", encoding="utf-8"
    )
    # Test source: one resolvable @req and one dangling @req.
    src = (
        "def test_happy():\n"
        "    # @req: REQ-1\n"
        "    pass\n"
        "def test_dangle():\n"
        "    # @req: REQ-NOPE\n"
        "    pass\n"
    )

    namespace = I.load_namespace(tmp_path / "specs")
    tags = T.extract_tags(src)
    malformed = T.find_malformed_tags(src)
    index = I.generate_index(tags, namespace)
    violations = C.find_structural_violations(tags, malformed, namespace)

    # Namespace + parser agree on the contract shape the consumers rely on.
    assert namespace == {"REQ-1": "order", "REQ-2": "order"}
    assert {"test": "test_happy", "reqs": ["REQ-1"], "invariant_refs": []} in tags

    # Tree places the resolvable req under its capability.
    assert "## order" in index
    assert "### REQ-1" in index
    assert "- test_happy" in index
    # Both orphan kinds surface: REQ-2 (no test) and REQ-NOPE (dangling).
    assert "## Orphans" in index
    assert "REQ-2" in index
    assert "REQ-NOPE" in index

    # The dangling @req is a structural violation; the resolvable one is not.
    assert any("REQ-NOPE" in v for v in violations)
    assert not any("REQ-1" in v for v in violations)

    # Identity check guards the committed index against drift.
    assert C.index_is_current(index, index) is True
    assert C.index_is_current(index, index + "x") is False
