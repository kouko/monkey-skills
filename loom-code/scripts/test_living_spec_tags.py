"""Tests for living_spec_tags.extract_tags."""
from living_spec_tags import (
    extract_tags,
    find_malformed_tags,
    locate_bindings,
)


def test_extract_single_req():
    text = (
        "def test_x():\n"
        "    # @req: REQ-1\n"
        "    assert True\n"
    )
    assert extract_tags(text) == [
        {"test": "test_x", "reqs": ["REQ-1"], "invariant_refs": []}
    ]


def test_malformed_tag_reported():
    text = (
        "def test_x():\n"
        "    # @req:\n"          # colon but empty id  -> malformed
        "    # @req REQ-2\n"     # no colon            -> malformed
        "    # @req: REQ-1\n"    # well-formed         -> NOT reported
        "    assert True\n"
    )
    malformed = find_malformed_tags(text)
    assert "# @req:" in malformed
    assert "# @req REQ-2" in malformed
    assert "# @req: REQ-1" not in malformed


def test_locate_bindings_returns_line_positions():
    # test_a (lines 1-3) carries one @req; test_b (lines 4-7) carries two.
    # @invariant-ref must be ignored by this locator (drift lane is @req only).
    text = (
        "def test_a():\n"          # line 1  body_start for test_a
        "    # @req: REQ-1\n"      # line 2  binding for test_a
        "    pass\n"               # line 3  body_end for test_a
        "def test_b():\n"          # line 4  body_start for test_b
        "    # @req: REQ-2\n"      # line 5  first binding for test_b
        "    # @invariant-ref: INV-9\n"  # line 6  IGNORED
        "    # @req: REQ-3\n"      # line 7  second binding for test_b
    )
    assert locate_bindings(text) == [
        {
            "test": "test_a",
            "req": "REQ-1",
            "body_start": 1,
            "body_end": 3,
            "binding_line": 2,
        },
        {
            "test": "test_b",
            "req": "REQ-2",
            "body_start": 4,
            "body_end": 7,
            "binding_line": 5,
        },
        {
            "test": "test_b",
            "req": "REQ-3",
            "body_start": 4,
            "body_end": 7,
            "binding_line": 7,
        },
    ]
