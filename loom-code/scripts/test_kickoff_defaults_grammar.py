"""W3-04 — grammar guard for docs/loom/KICKOFF-DEFAULTS.md.

The file's own header comment states the grammar:
`- <key>: <value> — <reason> (<date>)`, one line per key, keys declared
in `loom-code/contract/manifest.yaml`'s `kickoff_defaults`. This test
recomputes both halves of that claim against the real repo file —
every non-comment line matches the grammar, `<key>` is one of the
manifest's declared names, and `<date>` is a real calendar date — plus
a tmp fixture proving a malformed line fails.

Deliberately standalone (no import of loom_checker.py's lenient
`kickoff_defaults()`, which tolerates missing `—`/date for backward
compatibility): this test enforces the strict grammar, not what the
checker is willing to parse leniently.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
KICKOFF_DEFAULTS = REPO / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"

_LINE_RE = re.compile(
    r"^- (?P<key>[a-z][a-z0-9-]*): (?P<value>.+) — (?P<reason>.+) "
    r"\((?P<date>\d{4}-\d{2}-\d{2})\)$"
)


def manifest_kickoff_default_names() -> set[str]:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    return {entry["name"] for entry in manifest.get("kickoff_defaults", [])}


def _is_real_date(text: str) -> bool:
    try:
        year, month, day = (int(part) for part in text.split("-"))
        date(year, month, day)
        return True
    except ValueError:
        return False


def check_kickoff_defaults_grammar(
    doc_path: Path, valid_keys: set[str]
) -> list[str]:
    """Return one violation string per non-comment line that fails the
    grammar, an unknown key, or an unreal date. Empty = fully conformant."""
    violations: list[str] = []
    in_comment = False
    for lineno, raw_line in enumerate(
        doc_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if line.startswith("<!--"):
            in_comment = True
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if not line.startswith("- "):
            continue
        match = _LINE_RE.match(line)
        if match is None:
            violations.append(
                f"{doc_path}:{lineno} does not match "
                "`- <key>: <value> — <reason> (<YYYY-MM-DD>)`: {line!r}".format(
                    line=line
                )
            )
            continue
        key = match.group("key")
        if key not in valid_keys:
            violations.append(
                f"{doc_path}:{lineno} key {key!r} is not declared in "
                "loom-code/contract/manifest.yaml's kickoff_defaults"
            )
        if not _is_real_date(match.group("date")):
            violations.append(
                f"{doc_path}:{lineno} date {match.group('date')!r} is not "
                "a real calendar date"
            )
    return violations


def test_real_kickoff_defaults_file_is_fully_conformant() -> None:
    violations = check_kickoff_defaults_grammar(
        KICKOFF_DEFAULTS, manifest_kickoff_default_names()
    )
    assert violations == [], "\n".join(violations)


def test_every_key_is_manifest_declared() -> None:
    valid_keys = manifest_kickoff_default_names()
    assert valid_keys, "manifest declared no kickoff_defaults names"
    for line in KICKOFF_DEFAULTS.read_text(encoding="utf-8").splitlines():
        match = _LINE_RE.match(line.strip())
        if match is not None:
            assert match.group("key") in valid_keys


def test_malformed_line_missing_reason_fails(tmp_path: Path) -> None:
    doc = tmp_path / "KICKOFF-DEFAULTS.md"
    doc.write_text("- standing-docs: waived (2026-09-03)\n", encoding="utf-8")

    violations = check_kickoff_defaults_grammar(doc, {"standing-docs"})

    assert len(violations) == 1
    assert "does not match" in violations[0]


def test_malformed_line_bad_date_fails(tmp_path: Path) -> None:
    doc = tmp_path / "KICKOFF-DEFAULTS.md"
    doc.write_text(
        "- standing-docs: waived — some reason (2026-13-40)\n", encoding="utf-8"
    )

    violations = check_kickoff_defaults_grammar(doc, {"standing-docs"})

    assert len(violations) == 1
    assert "not a real calendar date" in violations[0]


def test_unknown_key_fails(tmp_path: Path) -> None:
    doc = tmp_path / "KICKOFF-DEFAULTS.md"
    doc.write_text(
        "- not-a-real-key: value — reason (2026-09-03)\n", encoding="utf-8"
    )

    violations = check_kickoff_defaults_grammar(doc, {"standing-docs"})

    assert len(violations) == 1
    assert "not declared" in violations[0]


def test_comment_block_lines_are_ignored(tmp_path: Path) -> None:
    doc = tmp_path / "KICKOFF-DEFAULTS.md"
    doc.write_text(
        "<!-- One line per key, grammar `- <key>: <value> — <reason> (<date>)`.\n"
        "not a real grammar line -->\n"
        "- standing-docs: waived — reason (2026-09-03)\n",
        encoding="utf-8",
    )

    violations = check_kickoff_defaults_grammar(doc, {"standing-docs"})

    assert violations == []


@pytest.mark.parametrize(
    "valid",
    [
        "2026-09-03",
        "2024-02-29",  # leap year
    ],
)
def test_real_dates_pass(valid: str) -> None:
    assert _is_real_date(valid)


@pytest.mark.parametrize(
    "invalid",
    [
        "2026-13-01",
        "2026-02-30",
        "2025-02-29",  # not a leap year
        "not-a-date",
    ],
)
def test_unreal_dates_fail(invalid: str) -> None:
    assert not _is_real_date(invalid)
