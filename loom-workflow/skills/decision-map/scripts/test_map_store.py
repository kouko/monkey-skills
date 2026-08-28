"""Tests for map_store.py — the shared MAP.md/ticket parser + validate gate.

WHY: map_store.py is the ONLY sanctioned reader of decision-map store
bytes (map-format.md §Command surface). These tests pin the schema
conformance the parser must accept, the schema_version refusal, and
the validate CLI's 0/1/2 exit-code contract every sibling checker
relies on.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import map_store  # noqa: E402

SCRIPT = Path(__file__).parent / "map_store.py"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


MAP_MD_CONFORMANT = """---
map-id: wayfinder
schema_version: 1
state: charting
---

## Destination

Chart the decision-map layer.

## Notes

Nothing special.

## Decisions-so-far

- We chose stdlib-only parsing (tickets/decision-a.md)

## Not-yet-specified (fog)

- F-1: how does the fog id survive a rename?

## Out-of-scope

- F-2: retrofitting the four legacy scripts

## Parts

| Part | Join key | Status |
|---|---|---|
| Engine | `wayfinder / Part: Engine` | in-progress |
"""

TICKET_CLOSED = """---
type: task
status: closed
claim: null
graduated-from: null
---

Decide the parser's stdlib-only constraint.

## Resolution

stdlib only, no third-party imports.
"""


def _make_conformant_map(tmp_path: Path) -> Path:
    map_dir = tmp_path / "docs" / "loom" / "maps" / "wayfinder"
    _write(map_dir / "MAP.md", MAP_MD_CONFORMANT)
    _write(map_dir / "tickets" / "decision-a.md", TICKET_CLOSED)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return map_dir


# --- RED acceptance test -------------------------------------------------


def test_validate_refuses_future_schema_version(tmp_path: Path) -> None:
    """A schema_version above map_store's supported ceiling is exit 2,
    naming both versions — never a silent read-past."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 1", "schema_version: 999"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "999" in message
    assert str(map_store.SUPPORTED_SCHEMA_VERSION) in message


# --- GREEN acceptance test ------------------------------------------------


def test_validate_accepts_schema_conformant_fixture(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


# --- parser API ------------------------------------------------------------


def test_read_map_parses_frontmatter_and_sections(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    doc = map_store.read_map(map_dir)
    assert doc.frontmatter.map_id == "wayfinder"
    assert doc.frontmatter.schema_version == 1
    assert doc.frontmatter.state == "charting"
    assert "Chart the decision-map layer." in doc.sections["Destination"]


def test_read_map_parses_fog_entries_with_ids(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    doc = map_store.read_map(map_dir)
    assert [f.number for f in doc.fog_entries] == [1]
    assert doc.fog_entries[0].id == "F-1"


def test_read_map_parses_decisions_last_parenthesized_token(
    tmp_path: Path,
) -> None:
    """The gist sentence may itself contain parentheses; the ticket
    link is read from the line's FINAL `(...)` group."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8").replace(
        "- We chose stdlib-only parsing (tickets/decision-a.md)",
        "- We chose stdlib-only parsing (see also PEP 8) (tickets/decision-a.md)",
    )
    map_md.write_text(text, encoding="utf-8")
    doc = map_store.read_map(map_dir)
    assert doc.decisions[0].ticket_link == "tickets/decision-a.md"
    assert "(see also PEP 8)" in doc.decisions[0].gist


def test_read_map_parses_parts_join_keys(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    doc = map_store.read_map(map_dir)
    assert doc.parts[0].name == "Engine"
    assert doc.parts[0].join_key == "wayfinder / Part: Engine"
    assert doc.parts[0].status == "in-progress"


def test_read_ticket_parses_frontmatter_and_resolution(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    ticket = map_store.read_ticket(map_dir / "tickets" / "decision-a.md")
    assert ticket.frontmatter.type == "task"
    assert ticket.frontmatter.status == "closed"
    assert ticket.frontmatter.claim is None
    assert ticket.frontmatter.graduated_from is None
    assert "stdlib only" in ticket.resolution


def test_resolve_schema_version_walks_up_from_ticket_path(
    tmp_path: Path,
) -> None:
    map_dir = _make_conformant_map(tmp_path)
    version = map_store.resolve_schema_version(
        map_dir / "tickets" / "decision-a.md"
    )
    assert version == 1


# --- validate: structural violations --------------------------------------


def test_validate_rejects_bad_state_enum(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "state: charting", "state: nonexistent"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "state" in message.lower()


def test_validate_rejects_missing_section(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8").replace("## Parts\n", "")
    map_md.write_text(text, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "Parts" in message


def test_validate_operational_error_on_missing_map_dir(tmp_path: Path) -> None:
    code, message = map_store.validate(tmp_path / "does-not-exist", repo_root=tmp_path)
    assert code == 1


def test_validate_accepts_done_sha_status_cell(tmp_path: Path) -> None:
    """map-format.md §Parts pins `done(<sha>)` as the third Status
    value (map_parts.py's write-back form) — validate must accept a
    Parts row already carrying it, not just the bare `in-progress`
    fixture value (map_parts.py Task 10 revision round 2)."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "| Engine | `wayfinder / Part: Engine` | in-progress |",
            "| Engine | `wayfinder / Part: Engine` | done(096c3167) |",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message
    doc = map_store.read_map(map_dir)
    assert doc.parts[0].status == "done(096c3167)"


# --- is_live_map helper ----------------------------------------------------


def test_is_live_map_true_for_charting(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    assert map_store.is_live_map(map_dir, repo_root=tmp_path) is True


def test_is_live_map_false_for_clear_state(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace("state: charting", "state: clear"),
        encoding="utf-8",
    )
    assert map_store.is_live_map(map_dir, repo_root=tmp_path) is False


def test_is_live_map_false_when_not_checker_valid(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8").replace("## Parts\n", "")
    map_md.write_text(text, encoding="utf-8")
    assert map_store.is_live_map(map_dir, repo_root=tmp_path) is False


# --- review round 2 findings ------------------------------------------------


def test_validate_rejects_out_of_order_sections(tmp_path: Path) -> None:
    """map-format.md pins the six sections 'in this order' — Parts
    moved to the front of the body must not still validate clean."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8")
    parts_block = (
        "## Parts\n\n"
        "| Part | Join key | Status |\n"
        "|---|---|---|\n"
        "| Engine | `wayfinder / Part: Engine` | in-progress |\n"
    )
    destination_block = "## Destination\n\nChart the decision-map layer.\n"
    assert parts_block in text
    assert destination_block in text
    reordered = text.replace(parts_block, "\0").replace(
        destination_block, parts_block
    ).replace("\0", destination_block)
    map_md.write_text(reordered, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "order" in message.lower()


def test_split_sections_rejects_duplicate_heading(tmp_path: Path) -> None:
    """Two `## Destination` headings must not silently last-win."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8").replace(
        "## Notes",
        "## Destination\n\nDuplicate.\n\n## Notes",
    )
    map_md.write_text(text, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "duplicate" in message.lower()
    assert "Destination" in message


def test_validate_rejects_duplicate_fog_id(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8").replace(
        "- F-1: how does the fog id survive a rename?",
        "- F-1: how does the fog id survive a rename?\n"
        "- F-1: a second entry reusing the same id",
    )
    map_md.write_text(text, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "F-1" in message


def test_validate_rejects_non_ascii_digit_fog_id(tmp_path: Path) -> None:
    """`re.fullmatch(r"F-\\d+")` accepts unicode digits (e.g. Arabic-indic
    ٥) since `\\d` is unicode-aware by default — the id grammar is
    ASCII-digit only."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8").replace(
        "- F-1: how does the fog id survive a rename?",
        "- F-٥: unicode-digit id must be rejected",
    )
    map_md.write_text(text, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "malformed fog id" in message.lower()


# --- CLI --------------------------------------------------------------------


def test_cli_validate_exits_0_on_conformant_fixture(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "validate", str(map_dir), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_cli_validate_exits_2_on_future_schema_version(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 1", "schema_version: 999"
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "validate", str(map_dir), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "999" in result.stderr
