"""Tests for the living-spec index generator.

`load_namespace(specs_dir)` walks `<specs_dir>/<capability>/spec.md`,
parses `### Requirement: <id>` headings, and returns a mapping
`{req_id: capability}` where `capability` is the immediate subdirectory
name under `specs_dir`.

These tests drive the function directly against HERMETIC `tmp_path`
fixtures (no on-disk fixture dir — mirrors `test_check_skill_crossrefs.py`).
Stdlib only (pathlib + tmp_path fixture).
"""

from living_spec_index import generate_index, load_namespace


def _make_spec(specs_dir, capability, body):
    cap_dir = specs_dir / capability
    cap_dir.mkdir(parents=True)
    (cap_dir / "spec.md").write_text(body, encoding="utf-8")


def test_load_namespace(tmp_path):
    # WHY: capability is DERIVED from the loom-spec dir name, not declared
    # per-req. A single `### Requirement: REQ-1` under `specs/order/`
    # must resolve to capability "order" so downstream index links a
    # test's @req to the right capability.
    specs = tmp_path / "specs"
    _make_spec(specs, "order", "### Requirement: REQ-1\nsome prose\n")

    assert load_namespace(specs) == {"REQ-1": "order"}


def test_generate_index_tree():
    # WHY: the index is a 3-level tree (capability > req > test). Each
    # test's @req must resolve through the namespace to its capability
    # and nest under both headings in tree order, so a reader scanning
    # the index sees which tests pin which requirement under which
    # capability.
    tag_records = [{"test": "test_x", "reqs": ["REQ-1"], "invariant_refs": []}]
    namespace = {"REQ-1": "order"}

    md = generate_index(tag_records, namespace)

    assert "## order" in md
    assert "### REQ-1" in md
    assert "- test_x" in md
    assert md.index("## order") < md.index("### REQ-1") < md.index("- test_x")
