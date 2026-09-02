"""W1-01 — every landed station's SKILL.md carries the station summary table.

spec REQ-9: a cold reader who has never seen loom is handed exactly one
SKILL.md (the entry station for the task) and must answer four questions —
which files get produced, who decides what, which checker rule blocks and
when, when review runs — with zero guesses. The only way that is possible
from one file is if the file carries a table covering the WHOLE station
order, not just its own step.

The population is the contract manifest, not this directory listing: the
five loom-code stations land across W1-01..W1-05, so a station whose
directory does not exist yet skips by name rather than failing. When the
directory lands, the row it must satisfy is already written here.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"

# The four columns the cold reader's four questions map onto, one to one.
# Matched case-insensitively as substrings of the header row, so the prose
# of a header ("Checker rules that can block, and when") stays free.
REQUIRED_COLUMNS = ("artifact", "who decides", "checker", "checkpoint")


def load_manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


MANIFEST_DATA = load_manifest()
STATION_ORDER = [s["name"] for s in MANIFEST_DATA["stations"]]
LOOM_CODE_STATIONS = [
    s["name"] for s in MANIFEST_DATA["stations"] if s["owner"] == "loom-code"
]


def frontmatter_name(text: str) -> str | None:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    front = yaml.safe_load(match.group(1)) or {}
    value = front.get("name")
    return str(value).strip() if value else None


def table_rows(text: str) -> list[list[str]]:
    """Every markdown table row in the document, as stripped cell lists."""
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows


def summary_table(text: str) -> list[list[str]] | None:
    """The first table whose header row carries all four required columns,
    returned with its separator row dropped."""
    rows = table_rows(text)
    for index, row in enumerate(rows):
        header = " ".join(row).lower()
        if all(column in header for column in REQUIRED_COLUMNS):
            body = []
            for following in rows[index + 1 :]:
                if all(set(cell) <= set("-: ") for cell in following):
                    continue
                if len(following) != len(row):
                    break
                body.append(following)
            return [row] + body
    return None


@pytest.mark.parametrize("station", LOOM_CODE_STATIONS)
def test_station_skill_carries_the_summary_table(station):
    skill = REPO / "loom-code" / "skills" / station / "SKILL.md"
    if not skill.is_file():
        pytest.skip(f"station {station} has not landed yet ({skill.relative_to(REPO)})")
    text = skill.read_text(encoding="utf-8")

    assert frontmatter_name(text) == station, (
        f"{skill.relative_to(REPO)} frontmatter name must be the station name "
        f"declared in the contract manifest ({station})."
    )

    table = summary_table(text)
    assert table is not None, (
        f"{skill.relative_to(REPO)} carries no summary table whose header row "
        f"names all of {REQUIRED_COLUMNS} — REQ-9's cold reader answers those "
        "four questions from this one file or not at all."
    )

    header, *body = table
    assert body, f"{skill.relative_to(REPO)}: the summary table has no rows."

    first_cells = [row[0].lower() for row in body]
    for expected in STATION_ORDER:
        assert any(expected in cell for cell in first_cells), (
            f"{skill.relative_to(REPO)}: the summary table has no row for "
            f"station {expected!r}; REQ-9 requires the whole station order, "
            "upstream stations included."
        )

    # The rows must read in station order, so the reader can follow the flow.
    positions = []
    for expected in STATION_ORDER:
        positions.append(next(i for i, c in enumerate(first_cells) if expected in c))
    assert positions == sorted(positions), (
        f"{skill.relative_to(REPO)}: summary-table rows are out of station order "
        f"({STATION_ORDER})."
    )

    for row in body:
        assert all(cell for cell in row[1:]), (
            f"{skill.relative_to(REPO)}: row {row[0]!r} leaves a summary-table "
            "cell empty; a blank cell is a guess the cold reader has to make."
        )
    assert len(header) >= len(REQUIRED_COLUMNS) + 1, (
        "the summary table needs a station column plus the four answer columns."
    )
