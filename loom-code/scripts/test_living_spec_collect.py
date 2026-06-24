"""Tests for living_spec_collect.collect_bindings."""
from __future__ import annotations

from pathlib import Path

from living_spec_collect import (
    collect_bindings,
    collect_malformed,
    collect_structural_records,
)

_TEST_A = """\
def test_alpha():
    # @req: REQ-A
    assert True
"""

_B_TEST = """\
def test_beta():
    # @req: REQ-B
    assert True
"""

# A non-test file carrying a @req-looking comment; must be ignored
# because its name matches none of the test-file patterns.
_HELPER = """\
def helper():
    # @req: REQ-HELPER
    return 1
"""


def _seed_tree(root: Path) -> None:
    (root / "test_a.py").write_text(_TEST_A, encoding="utf-8")
    (root / "b_test.py").write_text(_B_TEST, encoding="utf-8")
    (root / "helper.py").write_text(_HELPER, encoding="utf-8")


def test_collect_finds_tagged_tests_across_files(tmp_path: Path) -> None:
    _seed_tree(tmp_path)

    bindings = collect_bindings(tmp_path)

    # One binding per @req across BOTH test files; helper.py ignored.
    assert len(bindings) == 2
    reqs = {b["req"] for b in bindings}
    assert reqs == {"REQ-A", "REQ-B"}
    assert "REQ-HELPER" not in reqs

    by_req = {b["req"]: b for b in bindings}
    assert by_req["REQ-A"]["file"] == "test_a.py"
    assert by_req["REQ-B"]["file"] == "b_test.py"
    # Locator fields are preserved on each tagged binding.
    assert by_req["REQ-A"]["test"] == "test_alpha"
    assert by_req["REQ-B"]["test"] == "test_beta"


def test_collect_skips_vendored_and_dot_dirs(tmp_path: Path) -> None:
    # A real tagged test under a normal dir IS collected; an identically
    # tagged test file buried under a vendor / dot dir is NOT (no wasted
    # git log -L per vendored file).
    (tmp_path / "test_a.py").write_text(_TEST_A, encoding="utf-8")
    for vendor in (".venv", "node_modules"):
        vdir = tmp_path / vendor
        vdir.mkdir()
        (vdir / "test_vendored.py").write_text(_B_TEST, encoding="utf-8")

    bindings = collect_bindings(tmp_path)

    # Only the normal-dir test is collected; vendored ones are excluded.
    assert {b["file"] for b in bindings} == {"test_a.py"}
    assert {b["req"] for b in bindings} == {"REQ-A"}


def test_collect_is_deterministic_sorted_by_file(tmp_path: Path) -> None:
    _seed_tree(tmp_path)

    bindings = collect_bindings(tmp_path)

    # Files sorted before processing: b_test.py < test_a.py.
    assert [b["file"] for b in bindings] == ["b_test.py", "test_a.py"]


# A real test carrying a genuine `@req:` comment line (anchored binding).
_REAL = """\
def test_x():
    # @req: REQ-1
    pass
"""

# A test whose only `@req` lives INSIDE a string literal — a fixture
# string, NOT a binding. The anchored locator must skip it, so it must
# never reach the structural index.
_FIXTURE = """\
def test_y():
    src = "    # @req: REQ-FIXTURE"
    assert src
"""


def test_collect_structural_records_is_fixture_safe(tmp_path: Path) -> None:
    # A naive non-anchored `extract_tags` over the tree would treat the
    # fixture-string `@req` as a real binding and flood the index. The
    # structural collector reuses the ANCHORED locate_bindings path, so
    # only the genuine `# @req:` comment becomes a record.
    (tmp_path / "test_real.py").write_text(_REAL, encoding="utf-8")
    (tmp_path / "test_fixture.py").write_text(_FIXTURE, encoding="utf-8")

    records = collect_structural_records(tmp_path)

    assert records == [
        {"test": "test_x", "reqs": ["REQ-1"], "invariant_refs": []}
    ]


# A real malformed tag: an anchored `@req` marker with NO `: <id>`
# value, sitting on its own comment line inside a test.
_REAL_MALFORMED = """\
def test_x():
    # @req
    pass
"""

# A test whose only malformed-looking marker lives INSIDE a string
# literal — a fixture string, NOT a malformed comment line. The
# anchored collector must skip it.
_FIXTURE_MALFORMED = """\
def test_y():
    s = "# @req"
    assert s
"""


def test_collect_malformed_is_fixture_safe(tmp_path: Path) -> None:
    # A naive non-anchored `find_malformed_tags` over the tree would
    # flag the fixture-string `# @req` as malformed. The anchored
    # collector reports ONLY the real column-0 comment line.
    (tmp_path / "test_real.py").write_text(
        _REAL_MALFORMED, encoding="utf-8"
    )
    (tmp_path / "test_fixture.py").write_text(
        _FIXTURE_MALFORMED, encoding="utf-8"
    )

    malformed = collect_malformed(tmp_path)

    # The genuine malformed line is reported; the fixture string is not.
    assert any("@req" in line for line in malformed)
    assert all('"# @req"' not in line for line in malformed)
    assert malformed == ["# @req"]


# A `.py` file whose ONLY `@req` / malformed markers live inside a
# TRIPLE-QUOTED string literal — they sit at line-start on their own
# lines (so anchoring alone can't reject them), but they are part of a
# STRING token, not a real comment. A test file that exercises the
# `@req` parser carries exactly this shape (its fixtures embed fake
# tags). A `# @req: REQ-REAL` outside any string IS a real comment and
# must still be collected (guard against over-filtering).
_STRING_LITERAL_REQS = (
    "_SRC = '''\n"
    "def test_x():\n"
    "    # @req: REQ-FAKE\n"
    "    # @req\n"
    "    pass\n"
    "'''\n"
    "\n\n"
    "def test_real():\n"
    "    # @req: REQ-REAL\n"
    "    pass\n"
)


def test_structural_collectors_ignore_string_literal_reqs(
    tmp_path: Path,
) -> None:
    # The `# @req: REQ-FAKE` and bare `# @req` live at column-0 of their
    # own lines, but INSIDE a `'''...'''` literal — so the anchored
    # line-regex (which can't see token boundaries) would mistake them
    # for real comments. Tokenizing the source proves they are STRING
    # tokens, not COMMENT tokens, so neither collector reports them; the
    # genuine `# @req: REQ-REAL` comment outside the literal still is.
    (tmp_path / "test_litreq.py").write_text(
        _STRING_LITERAL_REQS, encoding="utf-8"
    )

    records = collect_structural_records(tmp_path)
    malformed = collect_malformed(tmp_path)

    # Only the real comment binds; the string-literal `@req`s vanish.
    assert records == [
        {"test": "test_real", "reqs": ["REQ-REAL"], "invariant_refs": []}
    ]
    # No malformed line: the bare `# @req` was inside the literal.
    assert malformed == []


# A `.py` file that does NOT tokenize — an unterminated triple-quoted
# string. `tokenize.generate_tokens` raises `tokenize.TokenError` on it.
# This is the exact shape the string-literal fix targets (a fixture
# embedding fake tags), so the collectors MUST survive it: the
# unparseable file contributes nothing, the walk continues.
_UNPARSEABLE_PY = "x = '''oops never closed\n"


def test_structural_collectors_survive_unparseable_py(
    tmp_path: Path,
) -> None:
    # An unterminated triple-quote makes `tokenize.generate_tokens`
    # raise `tokenize.TokenError`. `_real_comment_lines` must catch it
    # and treat the file as having no real comments — neither collector
    # may raise. A normal tagged test alongside it is still collected,
    # proving the walk continued past the bad file.
    (tmp_path / "test_bad.py").write_text(
        _UNPARSEABLE_PY, encoding="utf-8"
    )
    (tmp_path / "test_good.py").write_text(_REAL, encoding="utf-8")

    # Neither call may raise; the bad file contributes nothing.
    records = collect_structural_records(tmp_path)
    malformed = collect_malformed(tmp_path)

    assert records == [
        {"test": "test_x", "reqs": ["REQ-1"], "invariant_refs": []}
    ]
    assert malformed == []
