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
schema_version: 2
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


def test_validate_requires_schema_v2_without_parts(tmp_path: Path) -> None:
    """Only v2 maps without a Parts section are accepted; v1 maps must
    fail loudly with migration guidance, and the parser exposes no Parts
    state to consumers."""
    map_dir = _make_conformant_map(tmp_path)
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message
    assert "Parts" not in map_store.REQUIRED_SECTIONS
    assert not hasattr(map_store.read_map(map_dir), "parts")

    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 2", "schema_version: 1"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "migrate" in message.lower()


def test_validate_refuses_future_schema_version(tmp_path: Path) -> None:
    """A schema_version above map_store's supported ceiling is exit 2,
    naming both versions — never a silent read-past."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 2", "schema_version: 999"
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
    assert doc.frontmatter.schema_version == 2
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
    assert version == 2


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
    text = map_md.read_text(encoding="utf-8").replace("## Out-of-scope\n", "")
    map_md.write_text(text, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "Out-of-scope" in message


def test_validate_operational_error_on_missing_map_dir(tmp_path: Path) -> None:
    code, message = map_store.validate(tmp_path / "does-not-exist", repo_root=tmp_path)
    assert code == 1


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
    text = map_md.read_text(encoding="utf-8").replace("## Out-of-scope\n", "")
    map_md.write_text(text, encoding="utf-8")
    assert map_store.is_live_map(map_dir, repo_root=tmp_path) is False


# --- review round 2 findings ------------------------------------------------


def test_validate_rejects_out_of_order_sections(tmp_path: Path) -> None:
    """The required sections are order-sensitive — Out-of-scope moved
    to the front of the body must not still validate clean."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8")
    out_of_scope_block = "## Out-of-scope\n\n- F-2: retrofitting the four legacy scripts\n"
    destination_block = "## Destination\n\nChart the decision-map layer.\n"
    assert out_of_scope_block in text
    assert destination_block in text
    reordered = text.replace(out_of_scope_block, "\0").replace(
        destination_block, out_of_scope_block
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


# --- blocked-by / ratification grammar (map-format.md §Ticket schema) -------


TICKET_BLOCKED = """---
type: task
status: open
claim: null
graduated-from: null
blocked-by: decision-a, decision-b
ratification: pending
---

Waits on both siblings.
"""

TICKET_OPEN_B = """---
type: task
status: open
claim: null
graduated-from: null
---

A second sibling ticket.
"""


def test_blocked_by_documented_grammar(tmp_path: Path) -> None:
    """map-format.md §Ticket schema: `blocked-by: a, b` is one line of
    comma-separated sibling slugs and `ratification: pending` marks a
    deferred ratification — both optional, both parsed; absent fields
    behave exactly as today (no blockers / no pending ratification)."""
    map_dir = _make_conformant_map(tmp_path)
    _write(map_dir / "tickets" / "decision-b.md", TICKET_OPEN_B)
    _write(map_dir / "tickets" / "blocked.md", TICKET_BLOCKED)
    ticket = map_store.read_ticket(map_dir / "tickets" / "blocked.md")
    assert ticket.frontmatter.blocked_by == ["decision-a", "decision-b"]
    assert ticket.frontmatter.ratification == "pending"
    # absent fields keep today's meaning
    plain = map_store.read_ticket(map_dir / "tickets" / "decision-a.md")
    assert plain.frontmatter.blocked_by == []
    assert plain.frontmatter.ratification is None
    # a store using the new grammar correctly still validates clean
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


def test_validate_rejects_dangling_blocked_by_slug(tmp_path: Path) -> None:
    """A blocked-by slug naming no ticket file in the same map's
    tickets/ dir is exit 2, naming the ticket and the missing slug."""
    map_dir = _make_conformant_map(tmp_path)
    _write(
        map_dir / "tickets" / "blocked.md",
        TICKET_BLOCKED.replace(
            "blocked-by: decision-a, decision-b",
            "blocked-by: decision-a, no-such-ticket",
        ),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "blocked.md" in message
    assert "no-such-ticket" in message


def test_validate_rejects_blocked_by_cycle(tmp_path: Path) -> None:
    """The blocked-by graph must be acyclic — a cycle is exit 2 with a
    message naming the cycle."""
    map_dir = _make_conformant_map(tmp_path)
    _write(
        map_dir / "tickets" / "ring-a.md",
        TICKET_OPEN_B.replace(
            "graduated-from: null",
            "graduated-from: null\nblocked-by: ring-b",
        ),
    )
    _write(
        map_dir / "tickets" / "ring-b.md",
        TICKET_OPEN_B.replace(
            "graduated-from: null",
            "graduated-from: null\nblocked-by: ring-a",
        ),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "cycle" in message.lower()
    assert "ring-a" in message
    assert "ring-b" in message


def test_validate_unchanged_without_blocked_by_anywhere(tmp_path: Path) -> None:
    """Regression guard: a store carrying no blocked-by / ratification
    field anywhere validates exactly as before the grammar landed."""
    map_dir = _make_conformant_map(tmp_path)
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


# --- HITL user-ratified presence (map-format.md §Ticket schema / §Sections) --


TICKET_GRILLING_CLOSED_UNRATIFIED = """---
type: grilling
status: closed
claim: null
graduated-from: null
---

Which cut goes first?

## Resolution

Decided: hooks first.
"""


def test_validate_rejects_closed_hitl_ticket_without_user_ratified(
    tmp_path: Path,
) -> None:
    """map-format.md §Ticket schema: every `grilling`/`prototype`
    ticket is HITL unconditionally — closed with no `user-ratified:`
    line in its Resolution is exit 2, naming the ticket file and the
    missing line."""
    map_dir = _make_conformant_map(tmp_path)
    _write(
        map_dir / "tickets" / "grilling-cut.md",
        TICKET_GRILLING_CLOSED_UNRATIFIED,
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "grilling-cut.md" in message
    assert "user-ratified:" in message


def test_validate_accepts_closed_hitl_ticket_with_user_ratified(
    tmp_path: Path,
) -> None:
    map_dir = _make_conformant_map(tmp_path)
    _write(
        map_dir / "tickets" / "proto-probe.md",
        TICKET_GRILLING_CLOSED_UNRATIFIED.replace(
            "type: grilling", "type: prototype"
        ).replace(
            "Decided: hooks first.",
            "Decided: hooks first.\n\nuser-ratified: kouko, 2026-08-29",
        ),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


def test_validate_hitl_presence_ignores_open_hitl_ticket(tmp_path: Path) -> None:
    """The duty fires on CLOSE — an open grilling ticket with no
    Resolution at all still validates clean."""
    map_dir = _make_conformant_map(tmp_path)
    _write(
        map_dir / "tickets" / "grilling-open.md",
        TICKET_OPEN_B.replace("type: task", "type: grilling"),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


def test_validate_rejects_active_map_without_destination_ratification(
    tmp_path: Path,
) -> None:
    """map-format.md §Sections: an `active` map's Destination must
    carry a `user-ratified:` line — missing is exit 2, unconditional
    (no legacy branch), pointing the reader at §Sections."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "state: charting", "state: active"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "user-ratified:" in message
    assert "Sections" in message


def test_validate_rejects_clear_map_without_destination_ratification(
    tmp_path: Path,
) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "state: charting", "state: clear"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "user-ratified:" in message


def test_validate_accepts_active_map_with_destination_ratification(
    tmp_path: Path,
) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8")
        .replace("state: charting", "state: active")
        .replace(
            "Chart the decision-map layer.",
            "Chart the decision-map layer.\n\nuser-ratified: kouko, 2026-08-29",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


def test_validate_charting_map_needs_no_destination_ratification(
    tmp_path: Path,
) -> None:
    """A `charting` map (the scaffold state) carries no ratification
    yet — that is the designed pre-close window, exit 0."""
    map_dir = _make_conformant_map(tmp_path)
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


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
            "schema_version: 2", "schema_version: 999"
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
