"""Verify fixture-coldread-8.json reproduces the #787 cold-read list verbatim.

Each item's `text` must equal, character for character, the quoted body of
the corresponding numbered line in the prior list file (the line number and
the surrounding double quotes stripped). The `expected` field for each item
must match the fixed owner map: {1,4,5,7} -> reviewer, {2,3,6} -> adversary,
{8} -> implementer.
"""

import json
import re
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    """Walk upward from `start` until a directory containing docs/loom is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "docs" / "loom").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root (docs/loom) above {start}")


REPO_ROOT = _find_repo_root(Path(__file__).parent)
FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "loom"
    / "2026-09-04-adversary-three-way-attribution-measured"
    / "evidence"
    / "fixture-coldread-8.json"
)
SOURCE_PATH = (
    REPO_ROOT
    / "docs"
    / "loom"
    / "2026-09-04-reviewer-and-adversary-positioning"
    / "evidence"
    / "coldread-findings-list.txt"
)

EXPECTED_OWNER_MAP = {
    1: "reviewer",
    2: "adversary",
    3: "adversary",
    4: "reviewer",
    5: "reviewer",
    6: "adversary",
    7: "reviewer",
    8: "implementer",
}

LINE_PATTERN = re.compile(r'^(\d+)\.\s"(.*)"\s*$')


def _parse_source_lines(source_path: Path) -> dict:
    """Parse the numbered, quoted lines of the source list file into {n: text}."""
    parsed = {}
    for raw_line in source_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        match = LINE_PATTERN.match(raw_line)
        assert match, f"unexpected line format in source file: {raw_line!r}"
        n = int(match.group(1))
        parsed[n] = match.group(2)
    return parsed


def test_fixture_items_verbatim_prior_list():
    """fixture item texts and expected owners match the #787 source list exactly."""
    source_items = _parse_source_lines(SOURCE_PATH)
    assert len(source_items) == 8, "source list must have exactly 8 items"

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture["source"] == (
        "docs/loom/2026-09-04-reviewer-and-adversary-positioning/"
        "evidence/coldread-findings-list.txt"
    )

    items = fixture["items"]
    assert len(items) == 8, "fixture must have exactly 8 items"

    fixture_by_n = {item["n"]: item for item in items}
    assert set(fixture_by_n.keys()) == set(range(1, 9))

    for n, source_text in source_items.items():
        item = fixture_by_n[n]
        assert item["text"] == source_text, (
            f"item {n} text does not match source verbatim: "
            f"{item['text']!r} != {source_text!r}"
        )
        assert item["expected"] == EXPECTED_OWNER_MAP[n], (
            f"item {n} expected owner mismatch: "
            f"{item['expected']!r} != {EXPECTED_OWNER_MAP[n]!r}"
        )

    actual_owner_map = {item["n"]: item["expected"] for item in items}
    assert actual_owner_map == EXPECTED_OWNER_MAP
