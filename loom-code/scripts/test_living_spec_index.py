"""Tests for the living-spec index generator.

`load_namespace(specs_dir)` walks `<specs_dir>/<capability>/spec.md`,
parses `### Requirement: <id>` headings, and returns a mapping
`{req_id: capability}` where `capability` is the immediate subdirectory
name under `specs_dir`.

These tests drive the function directly against HERMETIC `tmp_path`
fixtures (no on-disk fixture dir — mirrors `test_check_skill_crossrefs.py`).
Stdlib only (pathlib + tmp_path fixture).
"""

from living_spec_index import generate_index, load_namespace, load_req_status


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


def test_load_req_status_parses_suffix_default_active(tmp_path):
    # WHY: the `[deferred]` suffix on a `### Requirement:` heading marks
    # intent that is declared-but-not-yet-implemented; a bare heading is
    # `active` by default. load_req_status must surface that status so a
    # downstream consumer can distinguish "missing coverage on an active
    # req" (a real gap) from "missing coverage on a deferred req"
    # (expected). The status suffix MUST NOT leak into the req id —
    # load_namespace's REQ-1 capture has to stay "REQ-1", not
    # "REQ-1 [deferred]", or the two maps key on different ids and the
    # index can't join them.
    specs = tmp_path / "specs"
    _make_spec(
        specs,
        "orders",
        "### Requirement: REQ-1 [deferred]\n### Requirement: REQ-2\n",
    )

    assert load_req_status(specs) == {"REQ-1": "deferred", "REQ-2": "active"}
    assert load_namespace(specs) == {"REQ-1": "orders", "REQ-2": "orders"}


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


def test_orphans_section():
    # WHY: the index must surface BOTH coverage holes so a reader sees
    # what is untested and what is mistagged. Two distinct orphan kinds:
    # (a) a namespace req with zero linked tests (REQ-2) is a coverage
    # gap; (b) a test whose @req is absent from the namespace
    # (REQ-UNKNOWN) is a dangling tag — likely a typo or a deleted req.
    # Conflating them would hide the difference between "needs a test"
    # and "fix the tag", so the markdown lists them under distinct groups.
    tag_records = [
        {"test": "test_x", "reqs": ["REQ-1"], "invariant_refs": []},
        {"test": "test_y", "reqs": ["REQ-UNKNOWN"], "invariant_refs": []},
    ]
    namespace = {"REQ-1": "order", "REQ-2": "order"}

    md = generate_index(tag_records, namespace)

    assert "## Orphans" in md
    # (a) namespace req with no test
    assert "REQ-2" in md
    # (b) test's @req not in namespace (dangling)
    assert "REQ-UNKNOWN" in md
    # both appear after the Orphans heading, not in the tree above it
    orphans_at = md.index("## Orphans")
    assert md.index("REQ-2") > orphans_at
    assert md.index("REQ-UNKNOWN") > orphans_at
