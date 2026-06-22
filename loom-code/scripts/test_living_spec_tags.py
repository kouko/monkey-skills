"""Tests for living_spec_tags.extract_tags."""
from living_spec_tags import extract_tags


def test_extract_single_req():
    text = (
        "def test_x():\n"
        "    # @req: REQ-1\n"
        "    assert True\n"
    )
    assert extract_tags(text) == [
        {"test": "test_x", "reqs": ["REQ-1"], "invariant_refs": []}
    ]
