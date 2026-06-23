"""Tests for living_spec_tags.extract_tags."""
from living_spec_tags import extract_tags, find_malformed_tags


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
