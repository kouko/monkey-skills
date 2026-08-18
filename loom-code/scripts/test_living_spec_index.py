"""Tests for the living-spec index generator.

`load_namespace(specs_dir)` walks `<specs_dir>/<capability>/spec.md`,
parses `### Requirement: <id>` headings, and returns a mapping
`{req_id: capability}` where `capability` is the immediate subdirectory
name under `specs_dir`.

These tests drive the function directly against HERMETIC `tmp_path`
fixtures (no on-disk fixture dir — mirrors `test_check_skill_crossrefs.py`).
Stdlib only (pathlib + tmp_path fixture).
"""

from pathlib import Path

from living_spec_index import (
    find_malformed_status,
    generate_index,
    load_namespace,
    load_req_paths,
    load_req_status,
)


def _make_spec(specs_dir, capability, body):
    cap_dir = specs_dir / capability
    cap_dir.mkdir(parents=True)
    (cap_dir / "spec.md").write_text(body, encoding="utf-8")


def test_load_namespace(tmp_path):
    # WHY: capability is DERIVED from the loom-design dir name, not declared
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


def test_namespace_parses_id_name_and_status_and_skips_prose(tmp_path):
    # No living-spec REQ-id: this test drives T6 itself, not a
    # requirement it implements.
    # WHY: the canonical grammar is `REQ-<n> — <name> [status]`; a
    # prose header (no `REQ-<n>` id) is legacy and must be invisible to
    # load_namespace/load_req_status/find_malformed_status alike — it
    # is neither a namespace entry nor a malformed-status offender.
    # EXCEPT: a prose header that DOES carry a bracket outside the
    # status vocabulary is still a find_malformed_status offender,
    # because the suffix grammar (the bracket rule) applies regardless
    # of whether the header is id-form or prose.
    specs = tmp_path / "specs"
    _make_spec(
        specs,
        "orders",
        "### Requirement: REQ-7 — Operational extraction [deferred]\n"
        "### Requirement: REQ-8 — Bare name\n"
        "### Requirement: Legacy prose name\n",
    )

    assert load_namespace(specs) == {"REQ-7": "orders", "REQ-8": "orders"}
    status = load_req_status(specs)
    assert status["REQ-7"] == "deferred"
    assert status["REQ-8"] == "active"
    assert find_malformed_status(specs) == []

    # Same grammar, but the prose header now carries an invalid bracket.
    specs2 = tmp_path / "specs2"
    _make_spec(
        specs2,
        "orders",
        "### Requirement: REQ-7 — Operational extraction [deferred]\n"
        "### Requirement: REQ-8 — Bare name\n"
        "### Requirement: Legacy [activ]\n",
    )

    malformed = find_malformed_status(specs2)
    assert len(malformed) == 1
    assert "activ" in malformed[0] and "Legacy" in malformed[0]

    # Lockstep property: the status vocabulary is declared in exactly
    # ONE literal place in the module source — both regexes are built
    # from that single `_STATUS_VOCAB` constant, so changing it can't
    # miss a second copy.
    source = Path(__file__).parent.joinpath("living_spec_index.py").read_text(
        encoding="utf-8"
    )
    assert source.count("active|deferred") == 1


def test_find_malformed_status(tmp_path):
    # WHY: load_req_status defaults any unrecognized suffix to "active"
    # by design, which silently swallows a typo'd status token like
    # `[activ]` — the author MEANT to declare intent but mistyped it, and
    # a silent default hides the mistake. find_malformed_status closes
    # that hole: a `[...]` whose content is neither "active" nor
    # "deferred" is a MALFORMED declaration that must be surfaced (a real
    # author error), while a valid `[deferred]` (REQ-2) or a bare heading
    # with no suffix (REQ-3) is intentional and must NOT be flagged. This
    # is the fail-loud counterpart to load_req_status's lenient default.
    specs = tmp_path / "specs"
    _make_spec(
        specs,
        "orders",
        "### Requirement: REQ-1 [activ]\n"
        "### Requirement: REQ-2 [deferred]\n"
        "### Requirement: REQ-3\n",
    )

    result = find_malformed_status(specs)

    joined = "\n".join(result)
    # the malformed one IS reported, naming both the req-id-portion and
    # the offending bracket content
    assert any("REQ-1" in line and "activ" in line for line in result)
    # the valid [deferred] and the bare heading are NOT flagged
    assert "REQ-2" not in joined
    assert "REQ-3" not in joined


def test_load_req_paths_maps_id_to_every_declaring_path(tmp_path):
    # WHY: the CI duplicate-declaration guard (BI-3) needs EVERY path that
    # declares a given req id, not just the last one (load_namespace's dict
    # merge silently drops earlier declarations). Two spec.md files each
    # declaring REQ-5 must both surface under the same key, sorted, so a
    # duplicate id across namespace files stays visible instead of being
    # overwritten.
    specs = tmp_path / "specs"
    _make_spec(specs, "order", "### Requirement: REQ-5\n")
    _make_spec(specs, "payment", "### Requirement: REQ-5\n")

    result = load_req_paths(specs)

    assert result == {
        "REQ-5": sorted([specs / "order" / "spec.md", specs / "payment" / "spec.md"])
    }


def test_load_req_paths_preserves_repeats_when_req_declared_twice_in_one_file(tmp_path):
    # WHY: find_duplicate_req_declarations (check-living-spec-index.py) must
    # be able to tell a SAME-FILE duplicate REQ-<n> (a same-file authoring
    # slip, e.g. a copy-paste heading duplicate) apart from a cross-file
    # collision — the two need distinct violation wording. That requires
    # the per-id path LIST to keep one entry per declaring line (repeats
    # included), not dedupe within a file — deduping here made a same-file
    # duplicate invisible to the CI structural lane entirely.
    specs = tmp_path / "specs"
    _make_spec(
        specs, "order",
        "### Requirement: REQ-5\nsome prose\n\n### Requirement: REQ-5\nmore prose\n",
    )

    result = load_req_paths(specs)

    assert result == {
        "REQ-5": [specs / "order" / "spec.md", specs / "order" / "spec.md"]
    }


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
