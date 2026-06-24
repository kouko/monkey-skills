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
    # Any `@invariant-ref` must be ignored here (drift lane is @req only).
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


def test_locate_bindings_body_includes_nested_helper_and_trailing_assert():
    # A nested helper `def` inside the test must NOT truncate the body
    # range. body_end must reach the assertion that follows the helper
    # (a dedent to the next sibling/top-level def or EOF ends the body),
    # else an edit to that assert line is invisible to `git log -L`.
    text = (
        "def test_x():\n"            # line 1  body_start
        "    # @req: REQ-1\n"        # line 2  binding
        "    def helper():\n"        # line 3  nested def -> must stay inside body
        "        return 1\n"         # line 4
        "    assert helper() == 1\n" # line 5  trailing assert -> must be in body
    )
    records = locate_bindings(text)
    assert len(records) == 1
    # The trailing assertion (line 5) must be within the body range.
    assert records[0]["body_end"] >= 5


def test_locate_bindings_ignores_at_req_inside_string_literal():
    # A fixture-style source where a `@req:` sits INSIDE a Python string
    # literal (a `"` precedes the `#`) must NOT be collected — that line
    # is code, not a dedicated comment. A sibling REAL comment line
    # (`# @req:` at line-start after indent) in the same source IS
    # collected, with a clean id (no garbled `\n",` suffix).
    text = (
        "def test_outer():\n"               # line 1
        '        "    # @req: REQ-1\\n",\n'  # line 2  @req inside a string literal -> IGNORE
        "    # @req: REQ-OK\n"              # line 3  real comment line -> COLLECT
        "    pass\n"                        # line 4
    )
    records = locate_bindings(text)
    # The string-literal occurrence is not a binding.
    assert all(r["binding_line"] != 2 for r in records)
    assert not any("REQ-1" in r["req"] for r in records)
    # The real comment line is collected with a clean id.
    assert records == [
        {
            "test": "test_outer",
            "req": "REQ-OK",
            "body_start": 1,
            "body_end": 4,
            "binding_line": 3,
        }
    ]
