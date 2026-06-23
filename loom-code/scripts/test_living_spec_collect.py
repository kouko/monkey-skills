"""Tests for living_spec_collect.collect_bindings."""
from __future__ import annotations

from pathlib import Path

from living_spec_collect import collect_bindings

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
