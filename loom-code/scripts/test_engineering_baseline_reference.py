"""W1-02 — the engineering baseline is one reference, cited not inlined.

tdd-iron-law and systematic-debugging stop being skills and become a single
advisory reference (concept-model §3, §10). Three consequences are checked
here: the reference exists and stays inside its word budget, the implementer
contract reaches it by a path that actually resolves, and neither the build
station nor the implementer contract carries vocabulary this redesign
deleted (§10) — a deleted word in a runtime contract is a mechanism that
still runs in an agent's head after it was removed from the repo.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REFERENCE = REPO / "loom-code" / "references" / "engineering-baseline.md"
IMPLEMENTER = REPO / "loom-code" / "agents" / "implementer.md"
SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"

WORD_CAP = 1500
IMPLEMENTER_WORD_CAP = 900

# concept-model §10's deletion list, as words that must not appear in a
# runtime prose contract. `status:` (the implementer's report field) is not a
# ledger, so only the ledger phrase is banned.
DELETED_VOCABULARY = (
    r"brief",
    r"seed",
    r"batch(es)?",
    r"packet",
    r"receipt",
    r"apply-result",
    r"waivers?",
    r"spec-reviewer",
    r"code-quality-reviewer",
    r"decision log",
    r"status ledger",
)

REQUIRED_COLUMNS = ("artifact", "who decides", "checker", "checkpoint")
STATION_ROWS = 7


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def test_reference_exists_and_fits_its_budget():
    assert REFERENCE.is_file(), f"{REFERENCE} has not landed."
    count = words(REFERENCE)
    assert count <= WORD_CAP, (
        f"engineering-baseline.md is {count} words; the merged reference is "
        f"capped at {WORD_CAP}."
    )


def test_reference_keeps_its_two_halves():
    text = REFERENCE.read_text(encoding="utf-8").lower()
    for anchor in ("iron law", "red", "green", "refactor", "reproduce",
                   "isolate", "root cause", "regression test", "beck"):
        assert anchor in text, (
            f"engineering-baseline.md drops {anchor!r}; the merge must keep "
            "both the TDD cycle and the four-phase debugging discipline, "
            "with the citation the source skill carried."
        )


def test_implementer_cites_the_reference_by_a_resolving_relative_path():
    text = IMPLEMENTER.read_text(encoding="utf-8")
    matches = re.findall(r"(\.\./[\w./-]*engineering-baseline\.md)", text)
    assert matches, (
        "implementer.md must point at the engineering baseline by relative "
        "path instead of inlining it."
    )
    for relative in set(matches):
        resolved = (IMPLEMENTER.parent / relative).resolve()
        assert resolved.is_file(), (
            f"implementer.md cites {relative!r}, which resolves to {resolved} "
            "— no such file."
        )
        assert resolved == REFERENCE.resolve()


def test_implementer_fits_its_budget():
    count = words(IMPLEMENTER)
    assert count <= IMPLEMENTER_WORD_CAP, (
        f"implementer.md is {count} words; the contract is capped at "
        f"{IMPLEMENTER_WORD_CAP} now that the baseline is a reference."
    )


def test_no_deleted_vocabulary_in_the_runtime_contracts():
    for path in (SKILL, IMPLEMENTER):
        text = path.read_text(encoding="utf-8")
        for pattern in DELETED_VOCABULARY:
            hit = re.search(rf"\b{pattern}\b", text, re.IGNORECASE)
            assert hit is None, (
                f"{path.name} still uses deleted vocabulary {hit.group(0)!r} "
                "(concept-model §10)."
            )


def test_build_station_carries_the_station_summary_table():
    rows = []
    for line in SKILL.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
    for index, row in enumerate(rows):
        header = " ".join(row).lower()
        if all(column in header for column in REQUIRED_COLUMNS):
            body = [
                r for r in rows[index + 1:]
                if len(r) == len(row) and not all(set(c) <= set("-: ") for c in r)
            ][:STATION_ROWS]
            assert len(row) == len(REQUIRED_COLUMNS) + 1, (
                "the summary table needs a station column plus the four "
                f"answer columns; got {row}."
            )
            assert len(body) == STATION_ROWS, (
                f"the summary table must carry all {STATION_ROWS} stations; "
                f"got {len(body)} rows."
            )
            return
    raise AssertionError(
        "the build station carries no summary table naming "
        f"{REQUIRED_COLUMNS}."
    )
