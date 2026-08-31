"""Tests for map_store.py — the shared MAP.md/ticket parser + validate gate.

WHY: map_store.py is the ONLY sanctioned reader of decision-map store
bytes (map-format.md §Command surface). These tests pin the schema
conformance the parser must accept, the schema_version refusal, and
the validate CLI's 0/1/2 exit-code contract every sibling checker
relies on.

External CLI grounding: local Git 2.50.1 ``git help rev-parse`` documents
``git rev-parse --show-toplevel`` as returning the working tree's top-level
path, absolute by default, and reporting an error when no working tree exists.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import map_store  # noqa: E402
import map_transaction  # noqa: E402

SCRIPT = Path(__file__).parent / "map_store.py"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_store_writer_lock_dependency_is_one_way() -> None:
    # @req: REQ-87
    store_source = SCRIPT.read_text(encoding="utf-8")
    lifecycle_source = (SCRIPT.parent / "map_lifecycle.py").read_text(encoding="utf-8")
    tree = ast.parse(store_source)
    imported_modules = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert "import map_lock" in store_source
    assert {"map_lifecycle", "map_transaction"}.isdisjoint(imported_modules)
    assert "import map_transaction" not in lifecycle_source
    assert "def retire_active_map(" not in store_source
    assert "def archive_map(" not in store_source


def test_repo_root_cli_shape_has_exact_local_git_grounding() -> None:
    assert "git rev-parse --show-toplevel" in (__doc__ or "")
    assert "Git 2.50.1" in (__doc__ or "")


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
delivery-evidence: commit 0123456
"""


def _make_conformant_map(tmp_path: Path) -> Path:
    map_dir = tmp_path / "docs" / "loom" / "maps" / "wayfinder"
    _write(
        map_dir / "MAP.md",
        MAP_MD_CONFORMANT.replace("schema_version: 2", "schema_version: 3"),
    )
    _write(
        map_dir / "tickets" / "decision-a.md",
        TICKET_CLOSED.replace("type: task", "type: delivery"),
    )
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return map_dir


# --- RED acceptance test -------------------------------------------------


def test_validate_rejects_schema_v2_with_migration_guidance(tmp_path: Path) -> None:
    # @req: REQ-85
    """V2 is readable by migration tooling but not a valid live Map."""
    map_dir = _make_conformant_map(tmp_path)
    map_path = map_dir / "MAP.md"
    _write(
        map_path,
        map_path.read_text(encoding="utf-8").replace(
            "schema_version: 3", "schema_version: 2"
        ),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "migrat" in message.lower()
    assert "3" in message


@pytest.mark.parametrize(
    "text",
    [
        "---\nmap-id: wayfinder\nmap-id: replacement\nschema_version: 3\nstate: active\n---\n\nbody\n",
        "---\ntype: delivery\nstatus: open\nstatus: claimed\n---\n\nbody\n",
        "---\nmap-id: wayfinder\nthis is not a key\nschema_version: 3\nstate: active\n---\n\nbody\n",
        "---\ntype: delivery\nmalformed ticket metadata\nstatus: open\n---\n\nbody\n",
    ],
)
def test_frontmatter_rejects_duplicate_keys_and_malformed_lines(text: str) -> None:
    # @req: REQ-77
    with pytest.raises(map_store.SchemaViolation, match="frontmatter|duplicate|malformed"):
        map_store.parse_frontmatter(text)


def test_validate_requires_schema_v3_without_parts(tmp_path: Path) -> None:
    """Only v3 maps without a Parts section are accepted; v1 maps must
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
            "schema_version: 3", "schema_version: 1"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "migrate" in message.lower()


def test_v3_accepts_only_four_closure_exclusive_ticket_types(
    tmp_path: Path,
) -> None:
    # @req: REQ-76
    """Schema v3 replaces generic task work with closure-evidence types."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 2", "schema_version: 3"
        ),
        encoding="utf-8",
    )
    ticket_path = map_dir / "tickets" / "decision-a.md"

    evidence_by_type = {
        "grilling": "decision: adopt stdlib parsing\nuser-ratified: kouko, 2026-08-30",
        "research": "factual-answer: stdlib parsing is sufficient\ninspectable-evidence: docs/loom/results/probe.md",
        "prototype": "candidate-artifact: docs/loom/prototypes/parser.md\nevaluation: selected by the maintainer\nuser-ratified: kouko, 2026-08-30",
        "delivery": "delivery-evidence: commit 0123456",
    }
    for ticket_type, evidence in evidence_by_type.items():
        ticket = TICKET_CLOSED.replace("type: task", f"type: {ticket_type}")
        ticket = ticket.split("## Resolution", 1)[0] + "## Resolution\n\n" + evidence + "\n"
        _write(ticket_path, ticket)
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 0, message

    for ticket_type in ("task", "unblock", "future-type"):
        _write(
            ticket_path,
            TICKET_CLOSED.replace("type: task", f"type: {ticket_type}"),
        )
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 2
        assert "classif" in message.lower()
        assert "grilling" in message
        assert "research" in message
        assert "prototype" in message
        assert "delivery" in message


def test_v3_closed_ticket_requires_subtype_closure_evidence(
    tmp_path: Path,
) -> None:
    # @req: REQ-76
    """Every v3 closure type needs its own inspectable closure record."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 2", "schema_version: 3"
        ),
        encoding="utf-8",
    )
    ticket_path = map_dir / "tickets" / "decision-a.md"

    incomplete_evidence = {
        "grilling": "decision: adopt stdlib parsing",
        "research": "factual-answer: stdlib parsing is sufficient",
        "prototype": "candidate-artifact: docs/loom/prototypes/parser.md\nevaluation: selected by the maintainer",
        "delivery": "delivery-evidence: completed locally",
    }
    for ticket_type, evidence in incomplete_evidence.items():
        ticket = TICKET_CLOSED.replace("type: task", f"type: {ticket_type}")
        ticket = ticket.split("## Resolution", 1)[0] + "## Resolution\n\n" + evidence + "\n"
        _write(ticket_path, ticket)
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 2
        assert ticket_type in message


def test_v3_ticket_statuses_and_withdrawal_contract(tmp_path: Path) -> None:
    # @req: REQ-77
    """V3 persists only lifecycle states; withdrawal is ratified, terminal,
    and distinct from subtype closure."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 2", "schema_version: 3"
        ),
        encoding="utf-8",
    )
    ticket_path = map_dir / "tickets" / "decision-a.md"

    delivery = TICKET_CLOSED.replace("type: task", "type: delivery")
    for status in ("open", "claimed", "closed"):
        _write(ticket_path, delivery.replace("status: closed", f"status: {status}"))
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 0, message

    withdrawn = delivery.replace(
        "status: closed",
        "status: withdrawn\nwithdrawn-from: claimed",
    ).replace(
        "## Resolution\n\nstdlib only, no third-party imports.\ndelivery-evidence: commit 0123456",
        "## Withdrawal\n\nuser-ratified: kouko, 2026-08-30\nreason: replaced by narrower work\nreplacement-ticket: successor",
    )
    _write(ticket_path, withdrawn)
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message

    _write(
        ticket_path,
        withdrawn.replace("withdrawn-from: claimed", "withdrawn-from: open"),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message

    _write(
        ticket_path,
        withdrawn + "\n## Resolution\n\ndelivery-evidence: commit 0123456\n",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "resolution" in message.lower()
    assert "withdrawn" in message.lower()

    _write(
        ticket_path,
        withdrawn.replace(
            "graduated-from: null",
            "graduated-from: null\ndelivery-phase: review",
        ),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "delivery-phase" in message
    assert "derived" in message.lower()

    _write(
        ticket_path,
        withdrawn.replace(
            "graduated-from: null",
            "graduated-from: null\nphase: review",
        ),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "phase" in message
    assert "derived" in message.lower()

    _write(
        ticket_path,
        withdrawn.replace("reason: replaced by narrower work", "reason: "),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "reason" in message.lower()

    _write(ticket_path, withdrawn.replace("withdrawn-from: claimed", "withdrawn-from: closed"))
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "open" in message
    assert "claimed" in message

    _write(ticket_path, withdrawn)
    _write(
        map_dir / "tickets" / "dependent.md",
        TICKET_OPEN_B.replace(
            "type: task", "type: delivery"
        ).replace("graduated-from: null", "graduated-from: null\nblocked-by: decision-a"),
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "dependent.md" in message
    assert "withdrawn" in message

    _write(
        map_dir / "tickets" / "dependent.md",
        TICKET_OPEN_B.replace("type: task", "type: delivery"),
    )
    _write(ticket_path, withdrawn.replace("status: withdrawn", "status: reviewing"))
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "reviewing" in message

    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 3", "schema_version: 2"
        ),
        encoding="utf-8",
    )
    _write(ticket_path, withdrawn.replace("type: delivery", "type: task"))
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "migrat" in message.lower()


def test_clear_requires_terminal_tickets_empty_fog_and_satisfied_da(
    tmp_path: Path,
) -> None:
    # @req: REQ-78
    """A v3 Map clears only after each authored outcome criterion has
    both a satisfied state and an evidence pointer; terminal tickets and
    empty fog alone describe finished work, not the achieved outcome."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    clear_map = (
        map_md.read_text(encoding="utf-8")
        .replace("schema_version: 2", "schema_version: 3")
        .replace("state: charting", "state: clear")
        .replace(
            "Chart the decision-map layer.",
            "Chart the decision-map layer.\n\n"
            "user-ratified: kouko, 2026-08-30\n\n"
            "- DA-1: The parser remains stdlib-only | state: satisfied | "
            "kind: objective | evidence: docs/loom/results/probe.md",
        )
        .replace("- F-1: how does the fog id survive a rename?\n", "")
    )
    map_md.write_text(clear_map, encoding="utf-8")
    ticket_path = map_dir / "tickets" / "decision-a.md"
    _write(ticket_path, TICKET_CLOSED.replace("type: task", "type: delivery"))

    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message

    _write(
        ticket_path,
        """---
type: delivery
status: withdrawn
claim: null
graduated-from: null
withdrawn-from: claimed
---

## Withdrawal

user-ratified: kouko, 2026-08-30
reason: replaced by narrower work
""",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message

    map_md.write_text(
        clear_map.replace("state: satisfied", "state: open"), encoding="utf-8"
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "acceptance" in message.lower()
    assert "satisfied" in message.lower()

    map_md.write_text(
        clear_map.replace(" | evidence: docs/loom/results/probe.md", ""), encoding="utf-8"
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "acceptance" in message.lower()
    assert "evidence" in message.lower()

    map_md.write_text(
        clear_map.replace(
            "- DA-1: The parser remains stdlib-only | state: satisfied | "
            "kind: objective | evidence: docs/loom/results/probe.md",
            "",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "acceptance" in message.lower()

    map_md.write_text(
        clear_map.replace(
            "docs/loom/results/probe.md",
            "docs/loom/results/probe.md | trailing field",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "acceptance" in message.lower()

    map_md.write_text(
        clear_map.replace(
            "## Not-yet-specified (fog)\n\n",
            "## Not-yet-specified (fog)\n\nunfinished prose\n",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "fog" in message.lower()

    v2_map_dir = _make_conformant_map(tmp_path / "v2")
    v2_map_md = v2_map_dir / "MAP.md"
    v2_map_md.write_text(
        v2_map_md.read_text(encoding="utf-8")
        .replace("schema_version: 3", "schema_version: 2")
        .replace("state: charting", "state: clear")
        .replace(
            "Chart the decision-map layer.",
            "Chart the decision-map layer.\n\nuser-ratified: kouko, 2026-08-30",
        )
        .replace("- F-1: how does the fog id survive a rename?\n", ""),
        encoding="utf-8",
    )
    code, message = map_store.validate(v2_map_dir, repo_root=tmp_path)
    assert code == 2
    assert "migrat" in message.lower()


def _make_v3_active_map(tmp_path: Path) -> Path:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8")
        .replace("schema_version: 2", "schema_version: 3")
        .replace("state: charting", "state: active")
        .replace(
            "Chart the decision-map layer.",
            "Chart the decision-map layer.\n\n"
            "user-ratified: kouko, 2026-08-30\n"
            "- DA-1: Parser remains stdlib-only | state: open | kind: objective",
        ),
        encoding="utf-8",
    )
    _write(
        map_dir / "tickets" / "decision-a.md",
        TICKET_CLOSED.replace("type: task", "type: delivery"),
    )
    return map_dir


def test_clear_history_is_immutable_and_active_regression_is_followup(
    tmp_path: Path,
) -> None:
    # @req: REQ-86
    """Later regressions never rewrite historical closure evidence."""
    active = _make_v3_active_map(tmp_path)
    closed_ticket = active / "tickets" / "decision-a.md"
    closed_before = closed_ticket.read_bytes()

    created = map_store.record_active_regression(
        active,
        "decision-a",
        summary="The delivered parser now rejects a supported input.",
        followup_type="delivery",
        followup_slug="repair-parser-regression",
    )

    assert created == active / "tickets" / "repair-parser-regression.md"
    assert closed_ticket.read_bytes() == closed_before
    followup = map_store.read_ticket(created)
    assert followup.frontmatter.type == "delivery"
    assert followup.frontmatter.status == "open"
    assert "decision-a" in created.read_text(encoding="utf-8")

    map_md = active / "MAP.md"
    clear_text = (
        map_md.read_text(encoding="utf-8")
        .replace("state: active", "state: clear")
        .replace(
            "- DA-1: Parser remains stdlib-only | state: open | kind: objective",
            "- DA-1: Parser delivered | state: satisfied | kind: objective | "
            "evidence: docs/loom/results/parser.md",
        )
        .replace("- F-1: how does the fog id survive a rename?\n", "")
    )
    map_md.write_text(clear_text, encoding="utf-8")
    created.unlink()
    predecessor_before = {
        path.relative_to(active): path.read_bytes()
        for path in sorted(active.rglob("*"))
        if path.is_file()
    }

    successor = map_store.create_successor_map(
        active,
        "wayfinder-regression",
        reason="The delivered parser regressed on supported input.",
        repo_root=tmp_path,
    )

    assert {
        path.relative_to(active): path.read_bytes()
        for path in sorted(active.rglob("*"))
        if path.is_file()
    } == predecessor_before
    successor_text = (successor / "MAP.md").read_text(encoding="utf-8")
    assert "predecessor-map: docs/loom/maps/wayfinder/MAP.md" in successor_text
    assert "state: charting" in successor_text
    code, message = map_store.validate(successor, repo_root=tmp_path)
    assert code == 0, message


def test_active_regression_uses_shared_map_transaction_lock(tmp_path: Path) -> None:
    # @req: REQ-87
    map_dir = _make_v3_active_map(tmp_path)
    transactions = map_dir / ".transactions"
    transactions.mkdir()
    outside = tmp_path / "outside.lock"
    outside.write_text("outside\n", encoding="utf-8")
    (transactions / ".map.lock").symlink_to(outside)

    with pytest.raises(map_store.SchemaViolation, match="lock"):
        map_store.record_active_regression(
            map_dir,
            "decision-a",
            summary="The parser regressed.",
            followup_type="delivery",
            followup_slug="repair-regression",
        )
    assert not (map_dir / "tickets/repair-regression.md").exists()
    assert outside.read_text(encoding="utf-8") == "outside\n"


def test_active_retirement_requires_named_ratification_and_reason(
    tmp_path: Path,
) -> None:
    # @req: REQ-86
    map_dir = _make_v3_active_map(tmp_path)
    for ratified_by, reason in (("", "superseded"), ("kouko", "")):
        before = (map_dir / "MAP.md").read_bytes()
        try:
            map_transaction.retire_map(
                map_dir,
                ratified_by=ratified_by,
                ratified_on="2026-08-30",
                reason=reason,
                repo_root=tmp_path,
            )
        except map_transaction.CloseTransactionError:
            pass
        else:
            raise AssertionError("invalid retirement evidence was accepted")
        assert (map_dir / "MAP.md").read_bytes() == before

    map_transaction.retire_map(
        map_dir,
        ratified_by="kouko",
        ratified_on="2026-08-30",
        reason="The outcome is no longer worth pursuing.",
        repo_root=tmp_path,
    )
    text = (map_dir / "MAP.md").read_text(encoding="utf-8")
    assert "state: archived" in text
    assert "state: clear" not in text
    assert "retirement-ratified: kouko, 2026-08-30" in text
    assert "retirement-reason: The outcome is no longer worth pursuing." in text
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


def test_archived_map_rejects_every_work_mutation_without_writing(
    tmp_path: Path,
) -> None:
    # @req: REQ-86
    map_dir = _make_v3_active_map(tmp_path)
    map_transaction.retire_map(
        map_dir,
        ratified_by="kouko",
        ratified_on="2026-08-30",
        reason="The outcome is no longer worth pursuing.",
        repo_root=tmp_path,
    )
    before = {
        path.relative_to(map_dir): path.read_bytes()
        for path in sorted(map_dir.rglob("*"))
        if path.is_file()
    }

    for operation in ("add", "claim", "bind", "resolve", "graduate"):
        try:
            map_store.require_work_mutable(map_dir, operation)
        except map_store.SchemaViolation as exc:
            assert "archived" in str(exc)
            assert operation in str(exc)
        else:
            raise AssertionError(f"archived Map accepted {operation}")

    after = {
        path.relative_to(map_dir): path.read_bytes()
        for path in sorted(map_dir.rglob("*"))
        if path.is_file()
    }
    assert after == before


def test_charting_rejects_work_and_terminal_records_are_byte_immutable(
    tmp_path: Path,
) -> None:
    # @req: REQ-93
    map_dir = _make_v3_active_map(tmp_path)
    map_path = map_dir / "MAP.md"
    ticket_path = map_dir / "tickets" / "decision-a.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        .replace("state: active", "state: charting")
        .replace("- We chose stdlib-only parsing (tickets/decision-a.md)\n", ""),
        encoding="utf-8",
    )
    ticket_path.write_text(
        ticket_path.read_text(encoding="utf-8").replace("status: closed", "status: open"),
        encoding="utf-8",
    )
    before = (map_path.read_bytes(), ticket_path.read_bytes())

    for operation in ("claim", "bind", "resolve", "close", "clear"):
        try:
            map_store.require_ticket_mutable(map_dir, "decision-a", operation)
        except map_store.SchemaViolation as exc:
            assert "activate" in str(exc).lower()
        else:
            raise AssertionError(f"charting Map accepted {operation}")
        assert (map_path.read_bytes(), ticket_path.read_bytes()) == before

    map_transaction.retire_map(
        map_dir,
        ratified_by="kouko",
        ratified_on="2026-08-30",
        reason="The chart will not be activated.",
        repo_root=tmp_path,
    )
    assert "state: archived" in map_path.read_text(encoding="utf-8")
    assert "state: clear" not in map_path.read_text(encoding="utf-8")

    terminal_base = ticket_path.read_text(encoding="utf-8")
    for terminal_status in ("closed", "withdrawn"):
        terminal = terminal_base
        terminal = terminal.replace("status: open", f"status: {terminal_status}")
        ticket_path.write_text(terminal, encoding="utf-8")
        terminal_before = ticket_path.read_bytes()
        for operation in ("claim", "bind", "resolve", "close", "withdraw", "edit"):
            try:
                map_store.require_ticket_mutable(map_dir, "decision-a", operation)
            except map_store.SchemaViolation as exc:
                assert terminal_status in str(exc)
                assert "follow-up" in str(exc).lower() or "fog" in str(exc).lower()
            else:
                raise AssertionError(f"{terminal_status} ticket accepted {operation}")
            assert ticket_path.read_bytes() == terminal_before


def test_archive_transition_keeps_map_and_ticket_paths_stable(tmp_path: Path) -> None:
    # @req: REQ-95
    map_dir = _make_v3_active_map(tmp_path)
    map_path = map_dir / "MAP.md"
    ticket_path = map_dir / "tickets" / "decision-a.md"
    brief_path = tmp_path / "docs" / "loom" / "specs" / "deliver-parser.md"
    ticket_relative = ticket_path.relative_to(tmp_path).as_posix()
    brief_relative = brief_path.relative_to(tmp_path).as_posix()
    _write(
        brief_path,
                f"# Deliver parser\n\nOutcome Map ticket: {ticket_relative}\n\n## Delivery closure\n\npolicy: pr-ci\nreview-evidence: review.md\nverification-evidence: pytest -q\n",
    )
    ticket_path.write_text(
        ticket_path.read_text(encoding="utf-8").replace(
            "graduated-from: null", f"graduated-from: null\nbrief: {brief_relative}"
        ),
        encoding="utf-8",
    )
    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        .replace("state: active", "state: clear")
        .replace(
            "- DA-1: Parser remains stdlib-only | state: open | kind: objective",
            "- DA-1: Parser delivered | state: satisfied | kind: objective | "
            "evidence: docs/loom/results/parser.md",
        )
        .replace("- F-1: how does the fog id survive a rename?\n", ""),
        encoding="utf-8",
    )
    before_paths = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    ticket_before = ticket_path.read_bytes()

    map_transaction.archive_map_transition(map_dir, repo_root=tmp_path)

    assert map_dir.is_dir()
    assert ticket_path.read_bytes() == ticket_before
    assert {path.relative_to(tmp_path) for path in tmp_path.rglob("*")} == (
        before_paths
        | {
            (map_dir / ".transactions").relative_to(tmp_path),
            (map_dir / ".transactions/.map.lock").relative_to(tmp_path),
        }
    )
    assert "state: archived" in map_path.read_text(encoding="utf-8")
    import delivery_binding

    code, message = delivery_binding.validate(ticket_path, repo_root=tmp_path)
    assert code == 0, message


def test_archive_uses_stable_readiness_and_refuses_late_binding_break(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-95
    # @req: REQ-98
    map_dir = _make_v3_active_map(tmp_path)
    map_path = map_dir / "MAP.md"
    ticket_path = map_dir / "tickets" / "decision-a.md"
    brief_path = tmp_path / "docs" / "loom" / "specs" / "deliver-parser.md"
    ticket_relative = ticket_path.relative_to(tmp_path).as_posix()
    brief_relative = brief_path.relative_to(tmp_path).as_posix()
    _write(brief_path, f"# Deliver parser\n\nOutcome Map ticket: {ticket_relative}\n")
    ticket_path.write_text(
        ticket_path.read_text(encoding="utf-8").replace(
            "graduated-from: null", f"graduated-from: null\nbrief: {brief_relative}"
        ),
        encoding="utf-8",
    )
    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        .replace("state: active", "state: clear")
        .replace(
            "- DA-1: Parser remains stdlib-only | state: open | kind: objective",
            "- DA-1: Parser delivered | state: satisfied | kind: objective | "
            "evidence: docs/loom/results/parser.md",
        )
        .replace("- F-1: how does the fog id survive a rename?\n", ""),
        encoding="utf-8",
    )
    map_before = map_path.read_bytes()
    transaction = map_dir / ".transactions" / "broken.json"
    _write(transaction, "{\"prepared\": true}\n")

    try:
        map_transaction.archive_map_transition(map_dir, repo_root=tmp_path)
    except map_transaction.CloseTransactionError as exc:
        assert "incomplete" in str(exc)
    else:
        raise AssertionError("archive accepted an incomplete operation")
    assert map_path.read_bytes() == map_before

    transaction.unlink()
    import map_lifecycle

    def break_binding_before_replace() -> None:
        brief_path.write_text("# Broken reciprocal binding\n", encoding="utf-8")

    monkeypatch.setattr(
        map_lifecycle,
        "_before_state_replace",
        break_binding_before_replace,
    )
    try:
        map_transaction.archive_map_transition(map_dir, repo_root=tmp_path)
    except map_transaction.CloseTransactionError as exc:
        assert "stable snapshot" in str(exc) or "binding" in str(exc)
    else:
        raise AssertionError("archive committed after a late Brief-link break")
    assert map_path.read_bytes() == map_before
    assert "state: archived" not in map_path.read_text(encoding="utf-8")

    brief_path.write_text(
        f"# Deliver parser\n\nOutcome Map ticket: {ticket_relative}\n",
        encoding="utf-8",
    )

    def break_binding_after_replace() -> None:
        brief_path.write_text("# Broken after state replacement\n", encoding="utf-8")

    monkeypatch.setattr(
        map_lifecycle,
        "_before_state_replace",
        lambda: None,
    )
    monkeypatch.setattr(
        map_lifecycle,
        "_after_state_replace",
        break_binding_after_replace,
    )
    try:
        map_transaction.archive_map_transition(map_dir, repo_root=tmp_path)
    except map_transaction.CloseTransactionError as exc:
        assert "changed" in str(exc) or "binding" in str(exc)
    else:
        raise AssertionError("archive kept an invalid post-write binding")
    assert map_path.read_bytes() == map_before
    assert "state: archived" not in map_path.read_text(encoding="utf-8")


def test_atomic_exchange_cas_restores_immediate_concurrent_replacement(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-97
    # @req: REQ-98
    target = tmp_path / "ticket.md"
    target.write_bytes(b"audited\n")

    def replace_immediately_before_exchange(path: Path, temporary: Path) -> None:
        replacement = tmp_path / "concurrent.md"
        replacement.write_bytes(b"concurrent\n")
        replacement.replace(path)

    monkeypatch.setattr(
        map_store, "_before_atomic_exchange", replace_immediately_before_exchange
    )
    try:
        map_store._atomic_write(target, "candidate\n", expected=b"audited\n")
    except map_store.SchemaViolation as exc:
        assert "changed" in str(exc)
    else:
        raise AssertionError("CAS accepted a target replaced immediately before exchange")

    assert target.read_bytes() == b"concurrent\n"
    assert not list(tmp_path.glob(".ticket.md.*"))


def test_atomic_exchange_cas_refuses_unsupported_platform_without_replace(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-97
    # @req: REQ-98
    target = tmp_path / "MAP.md"
    target.write_bytes(b"original\n")

    def unsupported(first: Path, second: Path) -> None:
        raise map_store.AtomicExchangeUnsupported("simulated unsupported filesystem")

    monkeypatch.setattr(map_store, "_exchange_paths", unsupported)
    try:
        map_store._atomic_write(target, "candidate\n", expected=b"original\n")
    except map_store.SchemaViolation as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("CAS fell back after unsupported atomic exchange")

    assert target.read_bytes() == b"original\n"
    assert not list(tmp_path.glob(".MAP.md.*"))


def test_atomic_exchange_restore_preserves_newest_concurrent_replacement(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-97
    # @req: REQ-98
    target = tmp_path / "ticket.md"
    target.write_bytes(b"expected-E\n")

    def install_b_before_first_exchange(path: Path, temporary: Path) -> None:
        replacement = tmp_path / "B.md"
        replacement.write_bytes(b"concurrent-B\n")
        replacement.replace(path)

    def install_c_before_restore(path: Path, temporary: Path) -> None:
        replacement = tmp_path / "C.md"
        replacement.write_bytes(b"newest-C\n")
        replacement.replace(path)

    monkeypatch.setattr(
        map_store, "_before_atomic_exchange", install_b_before_first_exchange
    )
    monkeypatch.setattr(
        map_store, "_before_atomic_restore", install_c_before_restore
    )

    try:
        map_store._atomic_write(
            target, "candidate-A\n", expected=b"expected-E\n"
        )
    except map_store.AtomicExchangeBroken as exc:
        assert "BROKEN" in str(exc)
        assert "recovery-required" in str(exc)
    else:
        raise AssertionError("restore race was reported as an ordinary mismatch")

    assert target.read_bytes() == b"newest-C\n"
    evidence_path = tmp_path / ".ticket.md.cas-recovery.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    retained = Path(evidence["retained_path"])
    assert retained.read_bytes() == b"concurrent-B\n"
    assert evidence["retained_role"] == "concurrent version retained during restore"


def test_atomic_exchange_third_swap_failure_retains_newest_recovery_bytes(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-97
    # @req: REQ-98
    target = tmp_path / "ticket.md"
    target.write_bytes(b"expected-E\n")

    def install_b(path: Path, temporary: Path) -> None:
        replacement = tmp_path / "B.md"
        replacement.write_bytes(b"concurrent-B\n")
        replacement.replace(path)

    def install_c(path: Path, temporary: Path) -> None:
        replacement = tmp_path / "C.md"
        replacement.write_bytes(b"newest-C\n")
        replacement.replace(path)

    real_exchange = map_store._exchange_paths
    exchange_count = 0

    def fail_third(first: Path, second: Path) -> None:
        nonlocal exchange_count
        exchange_count += 1
        if exchange_count == 3:
            raise OSError("simulated third-exchange failure")
        real_exchange(first, second)

    monkeypatch.setattr(map_store, "_before_atomic_exchange", install_b)
    monkeypatch.setattr(map_store, "_before_atomic_restore", install_c)
    monkeypatch.setattr(map_store, "_exchange_paths", fail_third)
    try:
        map_store._atomic_write(
            target, "candidate-A\n", expected=b"expected-E\n"
        )
    except map_store.AtomicExchangeBroken as exc:
        assert "newest concurrent version" in str(exc)
    else:
        raise AssertionError("third-exchange failure was reported as success")

    assert target.read_bytes() == b"concurrent-B\n"
    evidence = json.loads(
        (tmp_path / ".ticket.md.cas-recovery.json").read_text(encoding="utf-8")
    )
    retained = Path(evidence["retained_path"])
    assert retained.read_bytes() == b"newest-C\n"
    assert evidence["retained_role"] == "newest concurrent version; restore incomplete"


def test_atomic_exchange_fsync_failure_restores_authority_with_truthful_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-97
    # @req: REQ-98
    target = tmp_path / "ticket.md"
    target.write_bytes(b"expected-authority\n")
    real_fsync_directory = map_store._fsync_directory
    fsync_calls = 0

    def fail_first_directory_fsync(directory: Path) -> None:
        nonlocal fsync_calls
        fsync_calls += 1
        if fsync_calls == 1:
            raise OSError("simulated exchange durability failure")
        real_fsync_directory(directory)

    monkeypatch.setattr(
        map_store, "_fsync_directory", fail_first_directory_fsync
    )
    try:
        map_store._atomic_write(
            target,
            "candidate-version\n",
            expected=b"expected-authority\n",
        )
    except map_store.AtomicExchangeBroken as exc:
        assert "BROKEN" in str(exc)
        assert "durability" in str(exc)
    except OSError as exc:
        raise AssertionError(f"raw OSError escaped: {exc}") from exc
    else:
        raise AssertionError("failed exchange durability was reported as success")

    assert target.read_bytes() == b"expected-authority\n"
    evidence = json.loads(
        (tmp_path / ".ticket.md.cas-recovery.json").read_text(encoding="utf-8")
    )
    retained = Path(evidence["retained_path"])
    assert retained.read_bytes() == b"candidate-version\n"
    assert evidence["retained_role"] == "candidate retained after durability failure"


def test_atomic_mismatch_restore_fsync_failure_retains_candidate_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-97
    # @req: REQ-98
    target = tmp_path / "ticket.md"
    target.write_bytes(b"expected-E\n")

    def install_b(path: Path, temporary: Path) -> None:
        replacement = tmp_path / "B.md"
        replacement.write_bytes(b"concurrent-B\n")
        replacement.replace(path)

    real_fsync_directory = map_store._fsync_directory
    fsync_calls = 0

    def fail_first_directory_fsync(directory: Path) -> None:
        nonlocal fsync_calls
        fsync_calls += 1
        if fsync_calls == 1:
            raise OSError("simulated restore durability failure")
        real_fsync_directory(directory)

    monkeypatch.setattr(map_store, "_before_atomic_exchange", install_b)
    monkeypatch.setattr(
        map_store, "_fsync_directory", fail_first_directory_fsync
    )
    try:
        map_store._atomic_write(
            target, "candidate-A\n", expected=b"expected-E\n"
        )
    except map_store.AtomicExchangeBroken as exc:
        assert "BROKEN" in str(exc)
        assert "restore durability" in str(exc)
    except OSError as exc:
        raise AssertionError(f"raw OSError escaped: {exc}") from exc
    else:
        raise AssertionError("restore durability failure was ordinary refusal")

    assert target.read_bytes() == b"concurrent-B\n"
    evidence = json.loads(
        (tmp_path / ".ticket.md.cas-recovery.json").read_text(encoding="utf-8")
    )
    retained = Path(evidence["retained_path"])
    assert retained.read_bytes() == b"candidate-A\n"
    assert evidence["retained_role"] == "candidate retained after mismatch restore"


def test_validate_refuses_future_schema_version(tmp_path: Path) -> None:
    """A schema_version above map_store's supported ceiling is exit 2,
    naming both versions — never a silent read-past."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace(
            "schema_version: 3", "schema_version: 999"
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


def test_closed_task_requires_resolution_and_delivery_evidence(
    tmp_path: Path,
) -> None:
    """A closed task names concrete delivery evidence, not merely a
    prose claim that work finished."""
    map_dir = _make_conformant_map(tmp_path)
    ticket_path = map_dir / "tickets" / "decision-a.md"

    def ticket_with_resolution(resolution: str | None) -> str:
        ticket_without_resolution = TICKET_CLOSED.replace(
            "type: task", "type: delivery"
        ).split("## Resolution", 1)[0]
        if resolution is None:
            return ticket_without_resolution
        return ticket_without_resolution + "## Resolution\n\n" + resolution + "\n"

    accepted = (
        "Implemented.\n\ndelivery-evidence: commit 0123456",
        "Implemented.\n\ndelivery-evidence: PR #123",
        "Implemented.\n\ndelivery-evidence: docs/loom/results/probe.md",
    )
    for resolution in accepted:
        _write(
            ticket_path,
            ticket_with_resolution(resolution),
        )
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 0, message

    rejected = (
        ticket_with_resolution(None),
        ticket_with_resolution("Implemented, but no evidence is named."),
        ticket_with_resolution("delivery-evidence: finished locally"),
    )
    for ticket_text in rejected:
        _write(ticket_path, ticket_text)
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 2
        assert "delivery-evidence" in message


# --- parser API ------------------------------------------------------------


def test_read_map_parses_frontmatter_and_sections(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    doc = map_store.read_map(map_dir)
    assert doc.frontmatter.map_id == "wayfinder"
    assert doc.frontmatter.schema_version == 3
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
    assert ticket.frontmatter.type == "delivery"
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
    assert version == 3


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


def test_live_map_result_distinguishes_broken_from_not_present(
    tmp_path: Path,
) -> None:
    absent = tmp_path / "no-map"
    assert (
        map_store.is_live_map(absent, repo_root=tmp_path)
        is map_store.LiveMapResult.NOT_PRESENT
    )

    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace("## Out-of-scope\n", ""),
        encoding="utf-8",
    )
    assert (
        map_store.is_live_map(map_dir, repo_root=tmp_path)
        is map_store.LiveMapResult.BROKEN
    )


def test_is_live_map_true_for_charting(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    assert (
        map_store.is_live_map(map_dir, repo_root=tmp_path)
        is map_store.LiveMapResult.LIVE
    )


def test_is_live_map_false_for_clear_state(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    map_md.write_text(
        map_md.read_text(encoding="utf-8").replace("state: charting", "state: clear"),
        encoding="utf-8",
    )
    assert (
        map_store.is_live_map(map_dir, repo_root=tmp_path)
        is map_store.LiveMapResult.BROKEN
    )


def test_is_live_map_false_when_not_checker_valid(tmp_path: Path) -> None:
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    text = map_md.read_text(encoding="utf-8").replace("## Out-of-scope\n", "")
    map_md.write_text(text, encoding="utf-8")
    assert (
        map_store.is_live_map(map_dir, repo_root=tmp_path)
        is map_store.LiveMapResult.BROKEN
    )


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
    _write(map_dir / "tickets" / "decision-b.md", TICKET_OPEN_B.replace("type: task", "type: delivery"))
    _write(map_dir / "tickets" / "blocked.md", TICKET_BLOCKED.replace("type: task", "type: delivery"))
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
            TICKET_BLOCKED.replace("type: task", "type: delivery").replace(
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
            TICKET_OPEN_B.replace("type: task", "type: delivery").replace(
            "graduated-from: null",
            "graduated-from: null\nblocked-by: ring-b",
        ),
    )
    _write(
        map_dir / "tickets" / "ring-b.md",
            TICKET_OPEN_B.replace("type: task", "type: delivery").replace(
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
            "candidate-artifact: docs/loom/prototypes/hooks.md\n"
            "evaluation: selected by kouko\n"
            "user-ratified: kouko, 2026-08-29",
        ),
    )
    map_path = map_dir / "MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8").replace(
            "- We chose stdlib-only parsing (tickets/decision-a.md)",
            "- We chose stdlib-only parsing (tickets/decision-a.md)\n"
            "- Prototype selected. (tickets/proto-probe.md)",
        ),
        encoding="utf-8",
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


def test_clear_rejects_non_closed_tickets_and_fog(tmp_path: Path) -> None:
    """Clear means every ticket is closed and fog is empty, not merely
    ratified."""
    map_dir = _make_conformant_map(tmp_path)
    map_md = map_dir / "MAP.md"
    clear_text = (
        map_md.read_text(encoding="utf-8")
        .replace("state: charting", "state: clear")
        .replace(
            "Chart the decision-map layer.",
            "Chart the decision-map layer.\n\nuser-ratified: kouko, 2026-08-29\n\n"
            "- DA-1: parser remains stdlib-only | state: satisfied | "
            "kind: objective | evidence: docs/loom/results/probe.md",
        )
    )

    map_md.write_text(clear_text, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "fog" in message.lower()

    empty_fog_text = clear_text.replace("- F-1: how does the fog id survive a rename?\n", "")
    map_md.write_text(empty_fog_text, encoding="utf-8")
    for status in ("open", "claimed"):
        _write(
            map_dir / "tickets" / f"{status}.md",
            TICKET_CLOSED.replace("type: task", "type: delivery").replace(
                "status: closed", f"status: {status}"
            ),
        )
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 2
        assert status in message
        (map_dir / "tickets" / f"{status}.md").unlink()

    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


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
            "Chart the decision-map layer.\n\n"
            "user-ratified: kouko, 2026-08-29\n"
            "- DA-1: Parser remains stdlib-only | state: open | kind: objective",
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
            "schema_version: 3", "schema_version: 999"
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


def test_da_ids_states_evidence_and_evaluative_ratification(tmp_path: Path) -> None:
    # @req: REQ-90
    map_dir = _make_v3_active_map(tmp_path)
    map_path = map_dir / "MAP.md"
    destination = (
        "- DA-1: Parser remains stdlib-only | state: open | kind: objective\n"
        "- DA-2: Maintainer accepts the workflow | state: satisfied | "
        "kind: evaluative | evidence: docs/loom/evidence.md | "
        "user-ratified: kouko, 2026-08-30"
    )
    map_path.write_text(
        map_path.read_text(encoding="utf-8").replace(
            "- DA-1: Parser remains stdlib-only | state: open | kind: objective",
            destination,
        ),
        encoding="utf-8",
    )
    doc = map_store.read_map(map_dir)
    assert [criterion.id for criterion in doc.destination_acceptance] == [
        "DA-1",
        "DA-2",
    ]
    assert doc.destination_acceptance[0].state == "open"
    assert doc.destination_acceptance[1].evidence == "docs/loom/evidence.md"
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message

    invalid = {
        "duplicate": destination + "\n- DA-2: Reused | state: open | kind: objective",
        "state": destination.replace("state: open", "state: pending", 1),
        "evidence": destination.replace(
            " | evidence: docs/loom/evidence.md", ""
        ),
        "ratification": destination.replace(
            " | user-ratified: kouko, 2026-08-30", ""
        ),
    }
    original = map_path.read_text(encoding="utf-8")
    for expected, replacement in invalid.items():
        map_path.write_text(original.replace(destination, replacement), encoding="utf-8")
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 2
        assert expected in message.lower()

    map_path.write_text(
        original.replace(
            destination,
            destination
            + "\n- DA1: Almost canonical | state: open | kind: objective",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "malformed destination acceptance" in message.lower()


def test_da_shaped_bullets_require_exact_numeric_canonical_ids(
    tmp_path: Path,
) -> None:
    # @req: REQ-90
    map_dir = _make_v3_active_map(tmp_path)
    map_path = map_dir / "MAP.md"
    original = map_path.read_text(encoding="utf-8")
    marker = "user-ratified: kouko, 2026-08-30"

    map_path.write_text(
        original.replace(
            marker,
            marker + "\n- DA-X: Not numeric | state: open | kind: objective",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2
    assert "malformed destination acceptance" in message.lower()

    map_path.write_text(
        original.replace(
            marker,
            marker + "\n- DATABASE compatibility remains an ordinary note.",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message


def test_v3_monotonic_ids_and_exactly_one_closed_ticket_gist(
    tmp_path: Path,
) -> None:
    # @req: REQ-92
    map_dir = _make_v3_active_map(tmp_path)
    map_path = map_dir / "MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        .replace(
            "- DA-1: Parser remains stdlib-only | state: open | kind: objective",
            "- DA-3: Parser remains reliable | state: open | kind: objective",
        )
        .replace(
            "Nothing special.",
            "Nothing special.\nretired-da: DA-2 | Old criterion",
        )
        .replace(
            "- F-1: how does the fog id survive a rename?",
            "- F-3: current question",
        )
        .replace(
            "- F-2: retrofitting the four legacy scripts",
            "- F-2: retrofitting the four legacy scripts",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message

    monotonic = map_path.read_text(encoding="utf-8")
    map_path.write_text(
        monotonic.replace(
            "- F-3: current question",
            "- F-4: later question\n- F-3: current question",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2 and "monotonic" in message.lower()
    map_path.write_text(monotonic, encoding="utf-8")

    duplicate_gist = map_path.read_text(encoding="utf-8").replace(
        "- We chose stdlib-only parsing (tickets/decision-a.md)",
        "- We chose stdlib-only parsing (tickets/decision-a.md)\n"
        "- Duplicate gist (tickets/decision-a.md)",
    )
    map_path.write_text(duplicate_gist, encoding="utf-8")
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2 and "exactly one" in message.lower()

    map_path.write_text(
        duplicate_gist.replace("\n- Duplicate gist (tickets/decision-a.md)", "")
        .replace("- F-3: current question", "- F-2: reused retired id"),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2 and "F-2" in message

    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        .replace("- F-2: reused retired id", "- F-3: current question")
        .replace("DA-3: Parser remains reliable", "DA-2: Reused criterion"),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2 and "DA-2" in message


def test_blockers_reject_cross_map_self_duplicate_cycle_and_early_claim(
    tmp_path: Path,
) -> None:
    # @req: REQ-94
    map_dir = _make_v3_active_map(tmp_path)
    closed = map_dir / "tickets/decision-a.md"
    first = map_dir / "tickets/first.md"
    second = map_dir / "tickets/second.md"
    _write(first, TICKET_OPEN_B.replace("type: task", "type: research"))
    _write(second, TICKET_OPEN_B.replace("type: task", "type: delivery"))

    cases = {
        "cross-map": "../other/tickets/work",
        "self": "first",
        "duplicate": "decision-a, decision-a",
        "missing": "not-here",
    }
    original = first.read_text(encoding="utf-8")
    for expected, blockers in cases.items():
        first.write_text(
            original.replace(
                "graduated-from: null",
                f"graduated-from: null\nblocked-by: {blockers}",
            ),
            encoding="utf-8",
        )
        code, message = map_store.validate(map_dir, repo_root=tmp_path)
        assert code == 2
        assert expected in message.lower()

    first.write_text(
        original.replace(
            "graduated-from: null", "graduated-from: null\nblocked-by: second"
        ),
        encoding="utf-8",
    )
    second.write_text(
        second.read_text(encoding="utf-8").replace(
            "graduated-from: null", "graduated-from: null\nblocked-by: first"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2 and "cycle" in message.lower()

    second.write_text(TICKET_OPEN_B.replace("type: task", "type: delivery"), encoding="utf-8")
    first.write_text(
        original.replace("status: open", "status: claimed")
        .replace("claim: null", "claim: alice, 2026-08-30")
        .replace(
            "graduated-from: null", "graduated-from: null\nblocked-by: second"
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 2 and "second" in message and "closed" in message.lower()

    second.write_text(
        TICKET_CLOSED.replace("type: task", "type: delivery"), encoding="utf-8"
    )
    map_path = map_dir / "MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8").replace(
            "- We chose stdlib-only parsing (tickets/decision-a.md)",
            "- We chose stdlib-only parsing (tickets/decision-a.md)\n"
            "- Second blocker closed. (tickets/second.md)",
        ),
        encoding="utf-8",
    )
    code, message = map_store.validate(map_dir, repo_root=tmp_path)
    assert code == 0, message
    assert closed.is_file()


def test_validate_rejects_active_map_without_destination_acceptance(
    tmp_path: Path,
) -> None:
    """map-format.md §Frontmatter and lifecycle: activation requires a
    ratified Destination — and since v3 that ratification must include
    at least one Destination acceptance entry. An active map with zero
    DA entries is exit 2, naming the map and the missing requirement."""
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
    assert code == 2
    assert "wayfinder" in message
    assert "Destination acceptance" in message
